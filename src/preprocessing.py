"""Load and clean the ULB credit card fraud dataset."""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "creditcard.csv"
CLEAN_PATH = PROJECT_ROOT / "data" / "creditcard_clean.csv"


def load_raw(path=RAW_PATH):
    """Read the raw CSV downloaded from Kaggle / the TensorFlow mirror."""
    if not Path(path).exists():
        raise FileNotFoundError(
            f"{path} not found. See data/README.md for download instructions."
        )
    return pd.read_csv(path)


def data_quality_report(df):
    """Return simple data-quality checks as a dictionary."""
    return {
        "rows": len(df),
        "columns": df.shape[1],
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "negative_amounts": int((df["Amount"] < 0).sum()),
        "zero_amounts": int((df["Amount"] == 0).sum()),
        "class_values": sorted(df["Class"].unique().tolist()),
    }


def clean(df):
    """Fix types, drop exact duplicates and add a transaction id.

    Zero-amount transactions are kept: they are valid card checks
    (e.g. card verification), not data errors.
    """
    df = df.copy()
    df["Class"] = df["Class"].astype(int)
    df = df.drop_duplicates().reset_index(drop=True)
    df = df[df["Amount"] >= 0]
    df.insert(0, "transaction_id", range(1, len(df) + 1))
    return df


def load_clean(path=CLEAN_PATH):
    """Read the cleaned dataset saved by notebook 01."""
    return pd.read_csv(path)
