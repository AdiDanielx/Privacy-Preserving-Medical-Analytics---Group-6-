import numpy as np
import pandas as pd
import pytest

from ppma.dp_queries import (
    QUERY_REGISTRY,
    dp_gender_counts,
    dp_mean_age,
    query_epsilon,
    true_category_counts,
    true_mean_age,
)


@pytest.fixture
def sample_df():
    rng = np.random.default_rng(0)
    return pd.DataFrame(
        {
            "Age": rng.integers(18, 90, size=200),
            "Gender": rng.choice(["Male", "Female"], size=200),
        }
    )


def test_dp_mean_age_noised_but_close(sample_df):
    results = [dp_mean_age(sample_df, epsilon=5.0) for _ in range(20)]
    assert len(set(results)) > 1  # noise present
    true_value = true_mean_age(sample_df)
    assert all(abs(r - true_value) < 20 for r in results)


def test_dp_gender_counts_shape_matches_true(sample_df):
    dp_counts = dp_gender_counts(sample_df, epsilon=5.0)
    true_counts = true_category_counts(sample_df, "Gender")
    assert set(dp_counts.keys()) == set(true_counts.keys())


def test_query_epsilon_reads_literal_default():
    assert query_epsilon(dp_mean_age) == 1.0


def test_registry_is_open_ended():
    assert len(QUERY_REGISTRY) >= 1
    for entry in QUERY_REGISTRY:
        assert "name" in entry and "fn" in entry and "true_fn" in entry
