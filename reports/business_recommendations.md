# Fraud Monitoring: Findings and Recommendations

**Prepared by:** Fraud Data Analyst
**Data:** ULB credit card transactions, 2 days, September 2013 (283,726 transactions after cleaning)
**Audience:** Fraud Operations and Risk Management

---

## Summary

- Fraud is rare: **473 of 283,726 transactions (0.167%)**, worth **€58,591**.
- Fraud is concentrated in **two places**: tiny "test" charges under €1 and the **early-morning hours (2-4 am)**, where the fraud rate is 6-9 times the average.
- Most fraud *money* is in a small number of large transactions: **€250+ transactions hold 15% of fraud cases but 74% of fraud value**.
- A Random Forest risk score, alerting at a threshold of 0.25, **caught 80% of fraud (114 of 142) and 80% of fraud value** on held-out data. It raised only **24 false alerts** among 85,118 transactions.

---

## 1. Transaction patterns

| Metric | Legitimate | Fraud |
|---|---|---|
| Transactions | 283,253 | 473 |
| Median amount | €22.00 | €9.82 |
| Mean amount | €88.41 | €123.87 |
| 95th percentile | €365.00 | €655.82 |

The *typical* fraud (the median) is **smaller** than a typical legitimate payment. The *average* fraud is larger, because a few big frauds pull the mean up. Report the median as "typical", not the mean.

**Timing.** The fraud *rate* peaks at **2 am (1.45%)** and **4 am (1.04%)**, against 0.17% overall. Fraud *counts* are not highest at night. The rate is high because few genuine customers shop overnight.
*Assumption: the data's clock starts at midnight. The provider does not confirm this.*

## 2. Financial impact

| Amount band | Fraud cases | Fraud rate | Share of fraud cases | Share of fraud value |
|---|---|---|---|---|
| €0-1 | 171 | 0.56% | 36.2% | 0.2% |
| €1-10 | 67 | 0.10% | 14.2% | 0.5% |
| €10-50 | 55 | 0.06% | 11.6% | 2.6% |
| €50-100 | 55 | 0.15% | 11.6% | 8.3% |
| €100-250 | 54 | 0.16% | 11.4% | 14.3% |
| €250-500 | 37 | 0.27% | 7.8% | 21.6% |
| €500-1000 | 25 | 0.40% | 5.3% | 29.8% |
| €1000+ | 9 | 0.31% | 1.9% | 22.6% |

Count, rate and value each tell a different story:
- **By count**, fraud is dominated by **€0-1** charges.
- **By value**, fraud is dominated by **€250+** charges.
- **By rate**, both ends are risky. The middle (€1-50) is the safest.

## 3. Risk monitoring: model results

Evaluated on a 30% held-out test set (85,118 transactions, 142 frauds).

| Model | Precision | Recall | PR-AUC | False alerts (at 0.5) |
|---|---|---|---|---|
| Logistic Regression (baseline) | 86% | 56% | 0.71 | 13 |
| Logistic Regression (class-weighted) | 5% | 89% | 0.69 | 2,349 |
| Logistic Regression (SMOTE) | 5% | 89% | 0.70 | 2,498 |
| **Random Forest (class-weighted)** | **91%** | **77%** | **0.81** | **11** |

The class-weighted and SMOTE models catch the most fraud, but **19 out of 20 of their alerts are false**. That would bury investigators. High recall alone is not a good outcome.

### Chosen operating point: Random Forest, threshold 0.25

| Question | Answer (test set) |
|---|---|
| How many transactions must investigators review? | **138 alerts** (0.16% of transactions) |
| How many fraud cases are detected? | **114 of 142 (80.3%)** |
| How many legitimate transactions are wrongly flagged? | **24** (precision 82.6%) |
| Fraud value caught | **€16,000.52 of €19,877.88 (80.5%)** |
| Fraud value missed | **€3,877.36** (28 cases; median €2.50) |
| Review cost (€5 per alert) | €690 |
| **Net benefit** | **€15,310.52** |

**Assumptions:** reviewing one alert costs €5, and a missed fraud loses its full transaction amount. The threshold was chosen to maximise net benefit (value caught minus review cost).

Scaled to the full two days (the test set is 30% of the data), this is roughly **230 alerts per day**. A small team can handle that volume.

---

## Recommendations

1. **Adopt a risk score with a threshold, not yes/no rules.** Use the Random Forest score at 0.25 as the starting threshold. Recalculate the threshold whenever review costs or fraud losses change, using `src/evaluate.py`.
2. **Sort the alert queue by amount.** Work alerts of €250 and over first. They hold three-quarters of fraud value.
3. **Add overnight scrutiny.** For transactions between 1 and 5 am, consider step-up authentication (for example, an SMS code) instead of a manual review.
4. **Treat micro-charges as an early warning.** 36% of fraud cases are €0-1 "test" charges. They lose almost no money themselves, but in industry practice they often come before larger fraud. Flag the card for closer watching rather than spending investigator time on the €1 itself. *This dataset has no card IDs, so we cannot prove that link here. Confirm it with card-level data.*
5. **Do not judge the system on accuracy.** A system that flags nothing is 99.83% accurate. Report **recall (fraud caught), precision (alert quality) and value caught vs missed** every month.
6. **Review missed fraud monthly.** Most missed cases are small (median €2.50), but six of them, worth €300-€1,100 each, make up 94% of the missed value. Feed confirmed misses back into model retraining.

## Limitations

- Only 2 days of data from 2013. Patterns may not hold for other periods or other banks.
- `V1` to `V28` are anonymised PCA components. We do not claim they represent merchants, locations or cardholder behaviour.
- There is no customer, merchant or location data, so hotspot or customer-level analysis is not possible.
- The €5 review cost is an illustrative assumption. Replace it with the bank's real figure.
- Results come from a single 30% test split (142 frauds). With this few frauds, a different split could move precision and recall by a few percentage points.
