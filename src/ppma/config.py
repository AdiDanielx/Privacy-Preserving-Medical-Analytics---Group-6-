"""Central configuration: paths, column mapping, and privacy defaults.

Column names are configurable because the exact Kaggle CSV variant a user
drops into data/raw/ may not match the brief's schema exactly (e.g. some
variants have no explicit patient-ID column). Adjust the mappings below to
match your actual CSV instead of renaming columns in code.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
RAW_CSV_PATH = DATA_DIR / "raw" / "healthcare_dataset.csv"
TOKENIZATION_KEY_PATH = DATA_DIR / "tokenization.key"
TRANSIT_DIR = DATA_DIR / "_transit"

# Direct identifiers: tokenized locally at the source site, never reach the
# cloud in their original form. "id" has no configured column by default —
# tokenize_identifiers() falls back to the DataFrame's row index when absent.
IDENTIFIER_COLUMNS = {
    "name": "Name",
    "id": None,
}

QUASI_IDENTIFIER_COLUMNS = ["Age", "Gender", "Blood Type"]

SENSITIVE_COLUMNS = ["Medical Condition", "Medication", "Test Results"]

OPERATIONAL_COLUMNS = [
    "Doctor",
    "Hospital",
    "Admission Type",
    "Date of Admission",
    "Discharge Date",
    "Room Number",
    "Insurance Provider",
    "Billing Amount",
]

# Note: dp_queries.py bakes each query's own epsilon as a literal default
# in its function signature (required so PySyft can ship the function's
# source text standalone) rather than referencing this constant. Edit a
# query's default directly to change its budget. This value only sets the
# Analyst's total session budget.
SESSION_EPSILON_BUDGET = 10.0

DATASITE_NAME = "medical-analytics-datasite"
DATASITE_PORT = 9081
ROOT_EMAIL = "info@openmined.org"
ROOT_PASSWORD = "changethis"
ANALYST_NAME = "Third-Party Analyst"
ANALYST_EMAIL = "analyst@research-org.example"
ANALYST_PASSWORD = "analyst-pass-123"
ANALYST_INSTITUTION = "External Research Org"
ANALYST_WEBSITE = "https://research-org.example"
