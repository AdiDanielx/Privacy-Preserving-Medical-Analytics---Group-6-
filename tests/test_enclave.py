import pandas as pd
import pytest

from ppma.enclave import Enclave
from ppma.secure_channel import seal_for_transport


@pytest.fixture
def sample_df():
    return pd.DataFrame({"patient_token": ["abc", "def"], "Age": [40, 55]})


def test_ingest_decrypts_and_seals(sample_df):
    enclave = Enclave()
    payload = seal_for_transport(sample_df, enclave.public_key)
    sealed = enclave.ingest(payload)
    pd.testing.assert_frame_equal(sealed, sample_df)
    pd.testing.assert_frame_equal(enclave.sealed_dataframe, sample_df)


def test_sealed_dataframe_raises_before_ingest():
    enclave = Enclave()
    with pytest.raises(RuntimeError):
        _ = enclave.sealed_dataframe


def test_ingest_requires_valid_payload_for_this_enclave(sample_df):
    enclave_a = Enclave()
    enclave_b = Enclave()
    payload = seal_for_transport(sample_df, enclave_a.public_key)
    with pytest.raises(Exception):
        enclave_b.ingest(payload)
