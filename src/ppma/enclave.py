"""Phase 1: the simulated Secure Enclave (cloud side).

An Enclave instance owns an RSA keypair, standing in for the key an
attested hardware enclave would hold. Only its public key is ever handed
out; the private key never leaves the instance. The only way plaintext
data comes to exist inside an Enclave is through ingest(), which decrypts
an EncryptedPayload and keeps the result solely as an in-memory
pandas.DataFrame -- no method on this class ever writes that DataFrame to
disk.

This is a course-project simplification of real remote attestation: no
attestation protocol is implemented, the enclave "just" has a keypair. The
encryption itself (RSA-OAEP + AES-256-GCM in secure_channel.py) is real.
"""

import pandas as pd
from cryptography.hazmat.primitives.asymmetric import rsa

from ppma.secure_channel import EncryptedPayload, open_payload


class Enclave:
    def __init__(self) -> None:
        self._private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self._sealed_dataframe: pd.DataFrame | None = None

    @property
    def public_key(self) -> rsa.RSAPublicKey:
        return self._private_key.public_key()

    def ingest(self, payload: EncryptedPayload) -> pd.DataFrame:
        """Decrypt payload in memory and hold it as the sealed dataset.

        Never writes the decrypted DataFrame to disk.
        """
        self._sealed_dataframe = open_payload(payload, self._private_key)
        return self._sealed_dataframe

    @property
    def sealed_dataframe(self) -> pd.DataFrame:
        if self._sealed_dataframe is None:
            raise RuntimeError("Enclave has not ingested any data yet")
        return self._sealed_dataframe
