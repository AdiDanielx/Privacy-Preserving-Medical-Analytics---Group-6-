import pandas as pd
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from ppma.secure_channel import EncryptedPayload, open_payload, seal_for_transport


@pytest.fixture
def keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


@pytest.fixture
def sample_df():
    return pd.DataFrame({"patient_token": ["abc", "def"], "Age": [40, 55]})


def test_round_trip(keypair, sample_df):
    private_key, public_key = keypair
    payload = seal_for_transport(sample_df, public_key)
    recovered = open_payload(payload, private_key)
    pd.testing.assert_frame_equal(recovered, sample_df)


def test_wrong_private_key_fails(keypair, sample_df):
    _private_key, public_key = keypair
    other_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    payload = seal_for_transport(sample_df, public_key)
    with pytest.raises(Exception):
        open_payload(payload, other_private_key)


def test_ciphertext_has_no_plaintext_values(keypair, sample_df):
    _private_key, public_key = keypair
    payload = seal_for_transport(sample_df, public_key)
    raw_bytes = payload.to_bytes()
    assert b"abc" not in raw_bytes
    assert b"def" not in raw_bytes


def test_payload_bytes_round_trip(keypair, sample_df):
    private_key, public_key = keypair
    payload = seal_for_transport(sample_df, public_key)
    reconstructed = EncryptedPayload.from_bytes(payload.to_bytes())
    recovered = open_payload(reconstructed, private_key)
    pd.testing.assert_frame_equal(recovered, sample_df)
