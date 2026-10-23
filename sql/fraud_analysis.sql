-- Credit Card Fraud Analysis - SQL (SQLite)
-- Tables (created by sql/run_sql.py):
--   transactions(transaction_id, time_seconds, day, hour, amount, amount_band, is_fraud)
--   predictions(transaction_id, amount, is_fraud, fraud_score, flagged, outcome)  -- test set only
-- Each query starts with a "-- Q<n>:" line so run_sql.py can print a title.


-- Q1: Overall fraud rate and value (conditional aggregation)
SELECT
    COUNT(*)                                             AS total_transactions,
    SUM(is_fraud)                                        AS fraud_transactions,
    ROUND(100.0 * SUM(is_fraud) / COUNT(*), 3)           AS fraud_rate_pct,
    ROUND(SUM(amount), 2)                                AS total_value_eur,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount END), 2) AS fraud_value_eur
FROM transactions;


-- Q2: Typical amount - fraud vs legitimate (median via window function)
WITH ranked AS (
    SELECT
        is_fraud,
        amount,
        ROW_NUMBER() OVER (PARTITION BY is_fraud ORDER BY amount) AS rn,
        COUNT(*)     OVER (PARTITION BY is_fraud)                 AS n
    FROM transactions
)
SELECT
    CASE WHEN is_fraud = 1 THEN 'Fraud' ELSE 'Legitimate' END AS class,
    MAX(n)                                    AS transactions,
    ROUND(AVG(amount), 2)                     AS avg_amount_eur,
    ROUND(AVG(CASE WHEN rn IN ((n + 1) / 2, (n + 2) / 2) THEN amount END), 2)
                                              AS median_amount_eur,
    ROUND(MAX(amount), 2)                     AS max_amount_eur
FROM ranked
GROUP BY is_fraud;


-- Q3: Fraud count AND fraud rate by amount band, with share of total fraud value
WITH bands AS (
    SELECT
        amount_band,
        MIN(amount)                                           AS band_min,
        COUNT(*)                                              AS transactions,
        SUM(is_fraud)                                         AS fraud_cases,
        SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END)    AS fraud_value
    FROM transactions
    GROUP BY amount_band
)
SELECT
    amount_band,
    transactions,
    fraud_cases,
    ROUND(100.0 * fraud_cases / transactions, 3)              AS fraud_rate_pct,
    ROUND(fraud_value, 2)                                     AS fraud_value_eur,
    ROUND(100.0 * fraud_value / SUM(fraud_value) OVER (), 1)  AS share_of_fraud_value_pct
FROM bands
ORDER BY band_min;


-- Q4: Fraud by hour of day, ranked by fraud rate (CTE + RANK)
WITH hourly AS (
    SELECT
        hour,
        COUNT(*)       AS transactions,
        SUM(is_fraud)  AS fraud_cases,
        100.0 * SUM(is_fraud) / COUNT(*) AS fraud_rate_pct
    FROM transactions
    GROUP BY hour
)
SELECT
    hour,
    transactions,
    fraud_cases,
    ROUND(fraud_rate_pct, 3)                       AS fraud_rate_pct,
    RANK() OVER (ORDER BY fraud_rate_pct DESC)     AS risk_rank
FROM hourly
ORDER BY risk_rank
LIMIT 10;


-- Q5: Top 10 highest-value fraud transactions
SELECT
    RANK() OVER (ORDER BY amount DESC) AS case_rank,
    transaction_id,
    day,
    hour,
    ROUND(amount, 2)                   AS amount_eur
FROM transactions
WHERE is_fraud = 1
ORDER BY amount DESC
LIMIT 10;


-- Q6: Running total of fraud value across the two days (window running sum)
SELECT
    day,
    hour,
    SUM(is_fraud)                                                   AS fraud_cases,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END), 2)    AS fraud_value_eur,
    ROUND(SUM(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END))
          OVER (ORDER BY day, hour), 2)                             AS cumulative_fraud_value_eur
FROM transactions
GROUP BY day, hour
ORDER BY day, hour;


-- Q7: Alert review workload at the chosen model threshold (test set)
SELECT
    outcome,
    COUNT(*)                 AS transactions,
    ROUND(SUM(amount), 2)    AS value_eur
FROM predictions
GROUP BY outcome
ORDER BY transactions DESC;


-- Q8: Monitoring summary - alerts, precision, recall, value caught vs missed
SELECT
    SUM(flagged)                                                     AS alerts_to_review,
    SUM(CASE WHEN flagged = 1 AND is_fraud = 1 THEN 1 ELSE 0 END)    AS fraud_caught,
    SUM(CASE WHEN flagged = 1 AND is_fraud = 0 THEN 1 ELSE 0 END)    AS false_alerts,
    SUM(CASE WHEN flagged = 0 AND is_fraud = 1 THEN 1 ELSE 0 END)    AS fraud_missed,
    ROUND(100.0 * SUM(CASE WHEN flagged = 1 AND is_fraud = 1 THEN 1 ELSE 0 END)
          / SUM(flagged), 1)                                         AS precision_pct,
    ROUND(100.0 * SUM(CASE WHEN flagged = 1 AND is_fraud = 1 THEN 1 ELSE 0 END)
          / SUM(is_fraud), 1)                                        AS recall_pct,
    ROUND(SUM(CASE WHEN flagged = 1 AND is_fraud = 1 THEN amount ELSE 0 END), 2)
                                                                     AS fraud_value_caught_eur,
    ROUND(SUM(CASE WHEN flagged = 0 AND is_fraud = 1 THEN amount ELSE 0 END), 2)
                                                                     AS fraud_value_missed_eur
FROM predictions;
