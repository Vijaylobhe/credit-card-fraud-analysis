"""Simple, explainable features built from Time and Amount."""

import numpy as np
import pandas as pd

# Euro amount bands used throughout the analysis and the dashboard.
AMOUNT_BINS = [-0.01, 1, 10, 50, 100, 250, 500, 1000, np.inf]
AMOUNT_LABELS = ["€0-1", "€1-10", "€10-50", "€50-100",
                 "€100-250", "€250-500", "€500-1000", "€1000+"]

PCA_COLUMNS = [f"V{i}" for i in range(1, 29)]
MODEL_FEATURES = PCA_COLUMNS + ["log_amount", "hour"]


def add_features(df):
    """Add hour of day, day number, log amount and amount band.

    `Time` is seconds since the first transaction in the dataset, which
    covers two days. Hour of day assumes the data starts at midnight -
    a common assumption, but it is not stated by the data provider.
    """
    df = df.copy()
    df["day"] = (df["Time"] // 86400).astype(int) + 1
    df["hour"] = ((df["Time"] // 3600) % 24).astype(int)
    df["log_amount"] = np.log1p(df["Amount"])
    df["amount_band"] = pd.cut(df["Amount"], bins=AMOUNT_BINS, labels=AMOUNT_LABELS)
    return df
