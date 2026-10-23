#!/usr/bin/env bash
# Run the whole analysis end to end: notebooks 01-04, then the SQL queries.
# Usage:  source .venv/bin/activate && ./run_all.sh
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f data/creditcard.csv ]; then
  echo "data/creditcard.csv not found - see data/README.md"; exit 1
fi

cd notebooks
for nb in 01_data_cleaning 02_exploratory_analysis 03_imbalance_experiments 04_model_evaluation; do
  echo "Running $nb ..."
  jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 "$nb.ipynb"
done
cd ..

echo "Running SQL queries ..."
python sql/run_sql.py

echo "Building HTML dashboard ..."
python dashboard/build_dashboard.py

echo "Done. Open dashboard/fraud_dashboard.html in a browser. Charts are in visuals/, Tableau data in dashboard/data/."
