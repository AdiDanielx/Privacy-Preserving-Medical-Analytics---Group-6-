"""Builds the non-identifying mock DataFrame handed to the PySyft Asset.

Each column is independently shuffled, which preserves the marginal
distribution the analyst needs to write sensible queries against, while
destroying every row's real combination of attributes -- no mock row
corresponds to any real patient.
"""

import numpy as np
import pandas as pd


def build_mock(df: pd.DataFrame, seed: int | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    mock = pd.DataFrame(index=df.index)
    for column in df.columns:
        mock[column] = rng.permutation(df[column].to_numpy())
    return mock
