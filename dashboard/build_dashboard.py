"""Build an interactive HTML dashboard from the CSVs in dashboard/data/.

Usage (from the project root):  python dashboard/build_dashboard.py
Then open dashboard/fraud_dashboard.html in any web browser.
Run the notebooks first - they create the CSV files this script reads.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
TEMPLATE = HERE / "dashboard_template.html"
OUTPUT = HERE / "fraud_dashboard.html"

BAND_ORDER = ["€0-1", "€1-10", "€10-50", "€50-100",
              "€100-250", "€250-500", "€500-1000", "€1000+"]


def read(name):
    path = DATA / name
    if not path.exists():
        sys.exit(f"Missing {path}. Run the notebooks first (see README).")
    return pd.read_csv(path)


def pattern_data(tx):
    """Aggregate transactions by day, hour and amount band (small enough to embed)."""
    tx["fraud_amount"] = tx["amount"] * tx["is_fraud"]
    cube = (tx.groupby(["day", "hour", "amount_band"])
              .agg(n=("is_fraud", "size"), fraud=("is_fraud", "sum"),
                   value=("amount", "sum"), fraud_value=("fraud_amount", "sum"))
              .reset_index())
    cube["band"] = cube["amount_band"].map(BAND_ORDER.index)
    cube = cube.drop(columns="amount_band").round(2)

    # Amount distribution: % of each class per log-scale bin, by day.
    edges = np.logspace(-1, np.log10(tx["amount"].max() + 1), 41)
    tx["bin"] = np.clip(np.digitize(tx["amount"] + 0.1, edges) - 1, 0, len(edges) - 2)
    hist = (tx.groupby(["day", "is_fraud", "bin"]).size()
              .rename("n").reset_index())

    frauds = tx[tx["is_fraud"] == 1][["transaction_id", "day", "hour", "amount"]]
    return {
        "cube": cube.to_dict(orient="list"),
        "hist": hist.to_dict(orient="list"),
        "hist_edges": edges.round(2).tolist(),
        "frauds": frauds.to_dict(orient="list"),
    }


def model_data():
    kpis = read("model_kpis.csv").iloc[0]
    preds = read("model_predictions.csv")
    return {
        "best_model": kpis["model"],
        "best_threshold": float(kpis["threshold"]),
        "review_cost": float(kpis["review_cost_per_alert_eur"]),
        "test_rows": int(len(preds)),
        "test_frauds": int(preds["is_fraud"].sum()),
        "thresholds": read("threshold_tradeoff.csv").round(4).to_dict(orient="records"),
        "models": read("model_comparison.csv").round(4).to_dict(orient="records"),
    }


if __name__ == "__main__":
    data = {"bands": BAND_ORDER, **pattern_data(read("transactions.csv")), **model_data()}
    html = TEMPLATE.read_text().replace("__DASHBOARD_DATA__", json.dumps(data, default=int))
    OUTPUT.write_text(html)
    print(f"Dashboard written to {OUTPUT.relative_to(HERE.parent)} - open it in a browser.")
