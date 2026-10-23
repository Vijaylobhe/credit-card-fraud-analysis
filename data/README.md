# Data

The raw dataset is **not committed** to this repository: at about 150 MB it is over GitHub's file-size limit.

## Source

**Credit Card Fraud Detection**, from the ULB Machine Learning Group (Université Libre de Bruxelles), hosted on Kaggle:
https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

- 284,807 transactions made by European cardholders over two days in September 2013
- 492 frauds (0.172%)
- `Time`: seconds since the first transaction in the dataset
- `Amount`: transaction amount in euros
- `V1` to `V28`: anonymised PCA components (their real meaning is confidential)
- `Class`: 1 = fraud, 0 = legitimate

## Download

**Option A: Kaggle (the official source).** Download `creditcard.csv` from the link above and put it in this folder.

**Option B: the public mirror (no login).** TensorFlow hosts an identical copy:

```bash
curl -L -o data/creditcard.csv https://storage.googleapis.com/download.tensorflow.org/data/creditcard.csv
```

## Files created by the notebooks (also not committed)

| File | Created by | Contents |
|---|---|---|
| `creditcard_clean.csv` | notebook 01 | Raw data with duplicates removed and a `transaction_id` column added |
| `test_scores.csv` | notebook 03 | Fraud scores from each model on the test set |
| `fraud.db` | `sql/run_sql.py` | SQLite database used by the SQL queries |
