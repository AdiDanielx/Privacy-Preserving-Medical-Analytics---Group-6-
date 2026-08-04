# Data Setup

Place the Kaggle healthcare CSV at:

```
data/raw/healthcare_dataset.csv
```

This file is gitignored and must never be committed.

## Expected columns

`src/ppma/config.py` maps the columns the pipeline expects:

- **Direct identifiers** (`IDENTIFIER_COLUMNS`): `Name`. There's no separate
  patient-ID column mapped by default — `tokenize_identifiers()` falls back
  to the DataFrame's row index for the "ID" token. If your CSV has an
  explicit ID column, set `IDENTIFIER_COLUMNS["id"]` to its name.
- **Quasi-identifiers** (`QUASI_IDENTIFIER_COLUMNS`): `Age`, `Gender`, `Blood Type`.
- **Sensitive medical data** (`SENSITIVE_COLUMNS`): `Medical Condition`, `Medication`, `Test Results`.
- **Operational data** (`OPERATIONAL_COLUMNS`): `Doctor`, `Hospital`, `Admission Type`,
  `Date of Admission`, `Discharge Date`, `Room Number`, `Insurance Provider`, `Billing Amount`.

If your CSV's column names differ, update the mappings in `config.py` rather
than renaming columns in code.
