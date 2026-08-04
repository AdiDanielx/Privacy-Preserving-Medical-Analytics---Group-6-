# Privacy-Preserving Medical Analytics — PoC

A proof of concept for a Confidential Computing course: a Third-Party
Analyst researches sensitive medical data without ever seeing raw
plaintext, protected by two independent, defense-in-depth layers — a
simulated hardware enclave (data-in-use protection) and Differential
Privacy (output protection). See `CLAUDE.md` for the full project brief
and threat model.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
pip install -e .
```

Then place the Kaggle healthcare CSV at `data/raw/healthcare_dataset.csv`
— see `data/README.md` for the expected columns.

## Running

```bash
pytest                 # unit tests, no dataset required
python demo.py          # full end-to-end demo, requires the CSV in place
```

## Architecture

### Phase 1 — Enclave / Ingestion
- **Identity Layer** (`src/ppma/tokenization.py`): at the source site, direct
  identifiers (Name, and row-index-derived ID) are replaced with deterministic
  HMAC pseudonyms using a key that is generated and stored locally only. Raw
  identifiers never leave this step.
- **Encryption in transit** (`src/ppma/secure_channel.py`): the tokenized data
  is hybrid-encrypted (AES-256-GCM payload, RSA-OAEP-wrapped session key) using
  the public key of the destination `Enclave`. Only ciphertext crosses the
  network boundary; `demo.py` even stages it on disk as ciphertext, in
  `data/_transit/`, to make "encryption at rest" tangible too.
- **Enclave** (`src/ppma/enclave.py`): represents the cloud-side simulated
  hardware enclave. It owns an RSA keypair — only its public key is ever
  exposed. `Enclave.ingest()` is the *only* place plaintext comes to exist: it
  decrypts the payload and holds the result solely as an in-memory
  `pandas.DataFrame`. No method writes that DataFrame to disk. A memory or
  disk dump of the cloud host outside the `Enclave` object, at any point
  before `ingest()`, yields only ciphertext.

  *Honest scope note*: this simplifies real remote attestation — there's no
  attestation protocol, the "enclave" is just a keypair-holding Python object.
  The encryption itself is real, not simulated. Separately, PySyft's own
  datasite server (below) persists its own metadata/job state to a local
  SQLite file; that's PySyft's implementation detail, not something this
  project controls — the plaintext-in-memory-only guarantee is enforced by
  `Enclave`, upstream of PySyft.

### Phase 2 — Data Pointer
- **`src/ppma/datasite.py`** launches a real local PySyft (0.9.x) datasite
  server and uploads the enclave's sealed DataFrame as the dataset's real
  asset, alongside a **mock** DataFrame (`src/ppma/mock_data.py` — every
  column independently shuffled, so no mock row corresponds to any real
  patient). The mock is what the Analyst can freely explore; the real data is
  reachable only through the request/approve/execute workflow below.

### Phase 3 — Execution
- **`src/ppma/dp_queries.py`** — differentially private aggregate query
  functions (mean age, category counts) built on `diffprivlib`. Each function
  is self-contained (own imports, literal epsilon default) because PySyft
  ships a submitted function's own source text for isolated remote execution.
  `QUERY_REGISTRY` is an open-ended list — add an entry to expose a new query.
- **`src/ppma/roles.py`** — `Analyst` submits a query via
  `@sy.syft_function_single_use` + `request_code_execution`, spending from a
  `PrivacyBudget` (`src/ppma/budget.py`) up front; `DataOwner` reviews and
  approves pending requests. The DP noise is added *inside* the submitted
  function, so the value that crosses back out via `.get()` is already
  sanitized — the Analyst never receives an un-noised statistic.

`demo.py` wires all three phases into one end-to-end script and prints the
DP result next to the true (non-private) value at each step, so the privacy
effect is visible.
