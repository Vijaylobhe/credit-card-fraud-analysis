"""Load the analysis tables into SQLite and run every query in fraud_analysis.sql.

Usage (from the project root):  python sql/run_sql.py
Run the notebooks first - this reads the CSVs they export to dashboard/data/.
"""

import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "fraud.db"
SQL_PATH = ROOT / "sql" / "fraud_analysis.sql"
TABLES = {
    "transactions": ROOT / "dashboard" / "data" / "transactions.csv",
    "predictions": ROOT / "dashboard" / "data" / "model_predictions.csv",
}


def load_tables(conn):
    for table, csv_path in TABLES.items():
        if not csv_path.exists():
            sys.exit(f"Missing {csv_path}. Run the notebooks first (see README).")
        pd.read_csv(csv_path).to_sql(table, conn, if_exists="replace", index=False)
        print(f"Loaded {table} from {csv_path.relative_to(ROOT)}")


def run_queries(conn):
    pd.set_option("display.width", 160)
    pd.set_option("display.max_columns", 20)
    for block in SQL_PATH.read_text().split(";"):
        lines = [line for line in block.strip().splitlines() if line.strip()]
        title = next((l for l in lines if l.startswith("-- Q")), None)
        if title is None:
            continue
        print(f"\n{title[3:]}")
        print(pd.read_sql_query(block, conn).to_string(index=False))


if __name__ == "__main__":
    with sqlite3.connect(DB_PATH) as conn:
        load_tables(conn)
        run_queries(conn)
