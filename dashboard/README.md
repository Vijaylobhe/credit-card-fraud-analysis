# Dashboards

## HTML dashboard (ready to use)

Open **`fraud_dashboard.html`** in any browser. It needs an internet connection to load the Chart.js library. To rebuild it after rerunning the notebooks, run `python dashboard/build_dashboard.py`.

It has three sections:
- **Executive overview:** KPI cards
- **Fraud patterns:** hourly volume and fraud rate, a fraud-by-amount-band chart with a cases/rate/value toggle, the amount distribution, the top 10 fraud transactions, and the riskiest hours
- **Model performance:** a threshold slider that updates the KPIs, the confusion matrix, the share of fraud value caught, and the precision/recall chart; plus a model comparison table

## Tableau dashboard

Tableau workbooks (`.twbx`) can only be built inside Tableau, so this folder provides
**ready-to-use data** and a **step-by-step build guide**. Once you have built the workbook,
save it here as `tableau_dashboard.twbx` and publish it to Tableau Public.

Tableau Public is free: https://public.tableau.com/app/discover

## Data files (`dashboard/data/`, created by the notebooks)

| File | Rows | Use it for |
|---|---|---|
| `transactions.csv` | every cleaned transaction | Dashboards 1 and 2 |
| `model_predictions.csv` | test-set transactions with model score and outcome | Dashboard 3 |
| `threshold_tradeoff.csv` | one row per alert threshold | Dashboard 3 trade-off chart |
| `model_kpis.csv` | one row: chosen threshold results | Dashboard 3 KPI cards |
| `model_comparison.csv` | one row per model | Dashboard 3 model table |

Key columns: `is_fraud` (1 = fraud), `amount` (EUR), `hour` (0-23), `day` (1-2),
`amount_band`, `outcome` (Fraud caught / False alert / Fraud missed / Correctly cleared).

## Calculated fields to create in Tableau

```
Fraud Rate        = SUM([is_fraud]) / COUNT([transaction_id])
Fraud Value       = SUM(IF [is_fraud] = 1 THEN [amount] END)
Fraud Label       = IF [is_fraud] = 1 THEN "Fraud" ELSE "Legitimate" END
```

Use the same colours as the Python charts: **blue `#2a78d6` = Legitimate** and **orange `#eb6834` = Fraud**.

---

## Dashboard 1: Executive Fraud Overview (`transactions.csv`)

KPI cards. Build each one as a sheet that shows a single big number:
- Total transactions: `COUNT([transaction_id])`
- Confirmed frauds: `SUM([is_fraud])`
- Fraud rate: `[Fraud Rate]`, formatted as a percentage with 3 decimals
- Total fraud value: `[Fraud Value]`, formatted as currency (EUR)

Add one small chart: fraud cases by `day`.

## Dashboard 2: Fraud Pattern Analysis (`transactions.csv`)

1. **Amount distribution.** Columns: `amount` (create bins of size 50, or use `amount_band`). Rows: `COUNT`. Colour: `Fraud Label`. Use percent of total within each class.
2. **Fraud rate by amount band.** Columns: `amount_band`. Rows: `[Fraud Rate]`. Sort the bands in their natural order, not by value.
3. **Time-of-day trend.** Columns: `hour`. Build two separate line charts, not a dual axis: (a) `COUNT` of transactions, (b) `[Fraud Rate]`.
4. **Fraud count and value by band.** Bars of `SUM([is_fraud])`, with `[Fraud Value]` shown in the tooltip.
5. **Filters.** Add `day` and `amount_band` as filters, applied to all sheets on the dashboard.

## Dashboard 3: Model Performance (`model_kpis.csv`, `threshold_tradeoff.csv`, `model_predictions.csv`)

1. **KPI cards** from `model_kpis.csv`: `threshold`, `precision`, `recall`, `alerts`, `false_alerts`, `fraud_value_caught_eur`, `fraud_value_missed_eur`, `net_benefit_eur`.
2. **Fraud detected vs missed.** From `model_predictions.csv`, filter to `is_fraud = 1`. Show bars of `COUNT` and `SUM(amount)` by `outcome`.
3. **Confusion matrix.** Rows: `is_fraud`. Columns: `flagged`. Text: `COUNT`. Colour: `COUNT` (single blue scale).
4. **Threshold trade-off.** From `threshold_tradeoff.csv`, plot `threshold` against `precision` and `recall` on one axis (both are 0-1). Put `alerts` in a second chart below.
5. **Model comparison table** from `model_comparison.csv`: precision, recall, F1, PR-AUC.
6. State the assumptions on the dashboard as text: *"Review cost €5 per alert; a missed fraud loses the full transaction amount; results are on a 30% held-out test set."*

Save the workbook as `dashboard/tableau_dashboard.twbx`, publish it to Tableau Public, and put the link in the main README.
