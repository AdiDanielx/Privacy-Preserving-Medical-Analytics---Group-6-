"""Identity Layer: local tokenization of direct identifiers at the source site.

Direct identifiers (Name, patient ID) are replaced with deterministic HMAC
pseudonyms before the data leaves the source site. The key never leaves this
module's caller — it is generated and stored locally only, so a cloud host,
even if fully compromised, never has the material needed to reverse a token
back to the original value.
"""

import hashlib
import hmac
import secrets
from pathlib import Path

import pandas as pd

from ppma.config import IDENTIFIER_COLUMNS, TOKENIZATION_KEY_PATH


def load_or_create_key(path: Path = TOKENIZATION_KEY_PATH) -> bytes:
    """Load the local tokenization key, generating one on first use."""
    if path.exists():
        return path.read_bytes()
    path.parent.mkdir(parents=True, exist_ok=True)
    key = secrets.token_bytes(32)
    path.write_bytes(key)
    return key


def _tokenize_value(value: object, key: bytes) -> str:
    return hmac.new(key, str(value).encode("utf-8"), hashlib.sha256).hexdigest()


def tokenize_identifiers(df: pd.DataFrame, key: bytes) -> pd.DataFrame:
    """Return a copy of df with direct identifier columns replaced by tokens.

    The "id" identifier falls back to the DataFrame's row index when
    IDENTIFIER_COLUMNS["id"] is not set to an actual column name.
    """
    tokenized = df.copy()

    name_col = IDENTIFIER_COLUMNS.get("name")
    if name_col and name_col in tokenized.columns:
        tokenized[name_col] = tokenized[name_col].map(lambda v: _tokenize_value(v, key))
        tokenized = tokenized.rename(columns={name_col: "patient_token"})

    id_col = IDENTIFIER_COLUMNS.get("id")
    if id_col and id_col in tokenized.columns:
        tokenized[id_col] = tokenized[id_col].map(lambda v: _tokenize_value(v, key))
        tokenized = tokenized.rename(columns={id_col: "id_token"})
    else:
        tokenized["id_token"] = [
            _tokenize_value(idx, key) for idx in tokenized.index
        ]

    return tokenized.reset_index(drop=True)
