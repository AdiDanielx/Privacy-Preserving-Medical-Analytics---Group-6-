"""End-to-end PoC demo.

Walks through all three phases of the brief:
  1. Enclave / Ingestion  -- source-site tokenization, encrypted transport,
     in-memory-only decryption inside the simulated enclave.
  2. Data Pointer         -- a PySyft datasite exposes the sealed dataset to
     an analyst as mock data + a real-data pointer behind an
     approval boundary.
  3. Execution            -- the analyst submits differentially private
     aggregate queries; the data owner approves them; the analyst
     receives only DP-noised results, never raw plaintext.

Run with the real Kaggle CSV in place at data/raw/healthcare_dataset.csv
(see data/README.md).
"""

import sys

import pandas as pd

from ppma.budget import PrivacyBudget, PrivacyBudgetExceeded
from ppma.config import RAW_CSV_PATH, SESSION_EPSILON_BUDGET, TRANSIT_DIR
from ppma.datasite import launch_datasite, register_analyst, upload_sealed_dataset
from ppma.dp_queries import QUERY_REGISTRY, query_epsilon
from ppma.enclave import Enclave
from ppma.mock_data import build_mock
from ppma.roles import Analyst, DataOwner
from ppma.secure_channel import EncryptedPayload, seal_for_transport
from ppma.tokenization import load_or_create_key, tokenize_identifiers

DATASET_NAME = "patients"
ASSET_NAME = "patients"


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> None:
    if not RAW_CSV_PATH.exists():
        print(f"Raw CSV not found at {RAW_CSV_PATH}. See data/README.md.", file=sys.stderr)
        sys.exit(1)

    # --- Phase 1a: Identity Layer (source site, local) ---
    section("Source site: local tokenization")
    raw_df = pd.read_csv(RAW_CSV_PATH)
    key = load_or_create_key()
    tokenized_df = tokenize_identifiers(raw_df, key)
    print("Direct identifiers (Name/ID) tokenized locally; raw values never leave this step.")
    print(tokenized_df[["patient_token", "id_token"]].head(3).to_string(index=False))

    # --- Phase 1b: Encryption in transit, source site -> cloud enclave ---
    section("Source site -> cloud enclave: encrypted transport")
    enclave = Enclave()
    payload = seal_for_transport(tokenized_df, enclave.public_key)
    TRANSIT_DIR.mkdir(parents=True, exist_ok=True)
    transit_path = TRANSIT_DIR / "payload.bin"
    transit_path.write_bytes(payload.to_bytes())
    print(f"Ciphertext staged at {transit_path} ({transit_path.stat().st_size} bytes).")
    print("Anything read from this file or from cloud host memory right now is ciphertext only.")

    # --- Phase 1c: Enclave ingestion (in-memory only) ---
    section("Cloud enclave: decrypt in memory, seal dataset")
    received_payload = EncryptedPayload.from_bytes(transit_path.read_bytes())
    sealed_df = enclave.ingest(received_payload)
    transit_path.unlink()
    print("Plaintext now exists only inside the Enclave instance, in memory. Transit file deleted.")
    print(f"Sealed dataset: {len(sealed_df)} rows, columns: {list(sealed_df.columns)}")

    # --- Phase 2: Data Pointer (PySyft datasite) ---
    section("Launching PySyft datasite and uploading sealed dataset")
    mock_df = build_mock(sealed_df, seed=42)
    server, root_client = launch_datasite()
    try:
        upload_sealed_dataset(
            root_client,
            sealed_df,
            mock_df,
            name=DATASET_NAME,
            description="Tokenized medical records, sealed by a simulated hardware enclave.",
        )
        analyst_client = register_analyst(server, root_client)

        data_owner = DataOwner(root_client)
        budget = PrivacyBudget(SESSION_EPSILON_BUDGET)
        analyst = Analyst(analyst_client, budget)

        section("Analyst: exploring mock data only")
        mock_view = analyst.explore_mock(ASSET_NAME)
        print("This is ALL the analyst can see directly -- shuffled, non-identifying mock rows:")
        print(mock_view.head(3).to_string(index=False))

        # --- Phase 3: Execution, DP queries under approval ---
        section("Analyst: submitting DP query requests")
        asset = analyst.get_asset(ASSET_NAME)
        submitted = []
        for query_spec in QUERY_REGISTRY:
            epsilon = query_epsilon(query_spec["fn"])
            try:
                analyst.request_query(asset, query_spec, epsilon)
                submitted.append(query_spec)
                print(f"  requested {query_spec['name']} (epsilon={epsilon}, "
                      f"budget remaining={budget.remaining:.2f})")
            except PrivacyBudgetExceeded as exc:
                print(f"  skipped {query_spec['name']}: {exc}")

        section("Data owner: reviewing and approving requests")
        for request in data_owner.pending_requests():
            data_owner.review_and_approve(request)
        print(f"Approved {len(submitted)} request(s).")

        section("Analyst: collecting DP-noised results")
        for query_spec in submitted:
            dp_result = analyst.collect_result(asset, query_spec)
            true_result = query_spec["true_fn"](sealed_df)
            print(f"  {query_spec['name']}:")
            print(f"    DP result   -> {dp_result}")
            print(f"    true result -> {true_result}")

        section("Summary")
        print("The analyst never received: raw Name/ID, the sealed DataFrame, "
              "the enclave's private key, or any un-noised sensitive statistic.")
        print(f"Total privacy budget spent: {budget.spent:.2f} / {budget.total_epsilon:.2f}")
    finally:
        server.land()


if __name__ == "__main__":
    main()
