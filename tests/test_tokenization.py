import pandas as pd
import pytest

from ppma.tokenization import tokenize_identifiers


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "Name": ["Alice Smith", "Bob Jones"],
            "Age": [40, 55],
        }
    )


def test_tokenize_is_deterministic(sample_df):
    key = b"0" * 32
    result_a = tokenize_identifiers(sample_df, key)
    result_b = tokenize_identifiers(sample_df, key)
    assert result_a["patient_token"].tolist() == result_b["patient_token"].tolist()


def test_tokenize_differs_with_different_keys(sample_df):
    result_a = tokenize_identifiers(sample_df, b"0" * 32)
    result_b = tokenize_identifiers(sample_df, b"1" * 32)
    assert result_a["patient_token"].tolist() != result_b["patient_token"].tolist()


def test_original_names_do_not_survive(sample_df):
    result = tokenize_identifiers(sample_df, b"0" * 32)
    assert "Name" not in result.columns
    assert "Alice Smith" not in result["patient_token"].tolist()
    assert "Bob Jones" not in result["patient_token"].tolist()


def test_id_falls_back_to_row_index(sample_df):
    result = tokenize_identifiers(sample_df, b"0" * 32)
    assert "id_token" in result.columns
    assert result["id_token"].nunique() == len(sample_df)
