"""Privacy Layer: diffprivlib-backed differentially private aggregate queries.

Each function below is submitted to PySyft via
@sy.syft_function_single_use and runs *inside* the request/approve
boundary, against the real sealed data -- so DP noise is added before a
result ever crosses back out to the Analyst.

PySyft ships each submitted function by its own source text and executes
it in an isolated context, so every function here is intentionally
self-contained: its own imports, no calls to helpers defined elsewhere in
this module, and a literal epsilon default (not a reference to
config.DEFAULT_EPSILON) so the source text stands alone. QUERY_REGISTRY is
an open-ended list -- add an entry to expose a new query; nothing else in
the codebase needs to change. To change a query's privacy budget, edit its
literal epsilon default directly.

Category labels for the count queries are hardcoded literals (fixed domain
knowledge for the well-known Kaggle "Healthcare Dataset"), not derived from
the data via e.g. df[col].unique(). Deriving the label set from the data
itself would leak which categories are present -- diffprivlib's own
PrivacyLeakWarning flags exactly this if you pass an unspecified histogram
range. If your actual CSV uses different category values, edit the literal
lists below to match.
"""

import inspect


def dp_mean_age(df, epsilon: float = 1.0) -> float:
    from diffprivlib.tools import mean

    ages = df["Age"].to_numpy(dtype=float)
    return float(mean(ages, epsilon=epsilon, bounds=(0, 120)))


def dp_gender_counts(df, epsilon: float = 1.0) -> dict:
    import numpy as np
    from diffprivlib.tools import histogram

    labels = ["Female", "Male"]  # fixed domain knowledge, not derived from data
    label_to_code = {label: i for i, label in enumerate(labels)}
    codes = df["Gender"].map(label_to_code).to_numpy()
    bin_edges = np.arange(len(labels) + 1)
    counts, _ = histogram(codes, epsilon=epsilon, bins=bin_edges, range=(0, len(labels)))
    return {label: int(round(count)) for label, count in zip(labels, counts)}


def dp_condition_counts(df, epsilon: float = 1.0) -> dict:
    import numpy as np
    from diffprivlib.tools import histogram

    # fixed domain knowledge, not derived from data
    labels = ["Arthritis", "Asthma", "Cancer", "Diabetes", "Hypertension", "Obesity"]
    label_to_code = {label: i for i, label in enumerate(labels)}
    codes = df["Medical Condition"].map(label_to_code).to_numpy()
    bin_edges = np.arange(len(labels) + 1)
    counts, _ = histogram(codes, epsilon=epsilon, bins=bin_edges, range=(0, len(labels)))
    return {label: int(round(count)) for label, count in zip(labels, counts)}


def dp_test_result_counts(df, epsilon: float = 1.0) -> dict:
    import numpy as np
    from diffprivlib.tools import histogram

    labels = ["Abnormal", "Inconclusive", "Normal"]  # fixed domain knowledge
    label_to_code = {label: i for i, label in enumerate(labels)}
    codes = df["Test Results"].map(label_to_code).to_numpy()
    bin_edges = np.arange(len(labels) + 1)
    counts, _ = histogram(codes, epsilon=epsilon, bins=bin_edges, range=(0, len(labels)))
    return {label: int(round(count)) for label, count in zip(labels, counts)}


def query_epsilon(fn) -> float:
    """Read the epsilon a query function will run with from its own default."""
    return inspect.signature(fn).parameters["epsilon"].default


def true_mean_age(df) -> float:
    return float(df["Age"].astype(float).mean())


def true_category_counts(df, column: str) -> dict:
    return df[column].value_counts().to_dict()


QUERY_REGISTRY = [
    {
        "name": "dp_mean_age",
        "fn": dp_mean_age,
        "true_fn": lambda df: true_mean_age(df),
    },
    {
        "name": "dp_gender_counts",
        "fn": dp_gender_counts,
        "true_fn": lambda df: true_category_counts(df, "Gender"),
    },
    {
        "name": "dp_condition_counts",
        "fn": dp_condition_counts,
        "true_fn": lambda df: true_category_counts(df, "Medical Condition"),
    },
    {
        "name": "dp_test_result_counts",
        "fn": dp_test_result_counts,
        "true_fn": lambda df: true_category_counts(df, "Test Results"),
    },
]
