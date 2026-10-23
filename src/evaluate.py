"""Model metrics and the business view of an alert threshold."""

import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, confusion_matrix,
                             f1_score, precision_score, recall_score)

# Business assumptions - change these to match your bank.
REVIEW_COST_EUR = 5.0   # cost for an investigator to review one alert
# A missed fraud is assumed to cost the full transaction amount.


def model_metrics(name, y_true, scores, threshold=0.5):
    """Precision, recall, F1, PR-AUC and confusion-matrix counts."""
    y_pred = (scores >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    return {
        "model": name,
        "threshold": threshold,
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred),
        "pr_auc": average_precision_score(y_true, scores),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
    }


def business_impact(y_true, scores, amounts, threshold):
    """Money view of one threshold: fraud caught, fraud missed, review cost."""
    y_true = np.asarray(y_true)
    amounts = np.asarray(amounts)
    flagged = np.asarray(scores) >= threshold
    is_fraud = y_true == 1

    caught_value = amounts[flagged & is_fraud].sum()
    missed_value = amounts[~flagged & is_fraud].sum()
    alerts = int(flagged.sum())
    review_cost = alerts * REVIEW_COST_EUR
    return {
        "threshold": threshold,
        "alerts": alerts,
        "fraud_caught": int((flagged & is_fraud).sum()),
        "fraud_missed": int((~flagged & is_fraud).sum()),
        "false_alerts": int((flagged & ~is_fraud).sum()),
        "precision": (flagged & is_fraud).sum() / alerts if alerts else 0.0,
        "recall": (flagged & is_fraud).sum() / is_fraud.sum(),
        "fraud_value_caught_eur": round(caught_value, 2),
        "fraud_value_missed_eur": round(missed_value, 2),
        "review_cost_eur": review_cost,
        "net_benefit_eur": round(caught_value - review_cost, 2),
    }


def threshold_table(y_true, scores, amounts, thresholds=None):
    """Business impact across a range of thresholds (for the trade-off chart)."""
    if thresholds is None:
        thresholds = np.round(np.arange(0.05, 1.0, 0.05), 2)
    rows = [business_impact(y_true, scores, amounts, t) for t in thresholds]
    return pd.DataFrame(rows)


def outcome_labels(y_true, scores, threshold):
    """Label each transaction TP / FP / FN / TN for the dashboard."""
    y_true = np.asarray(y_true)
    flagged = np.asarray(scores) >= threshold
    return np.select(
        [flagged & (y_true == 1), flagged & (y_true == 0), ~flagged & (y_true == 1)],
        ["Fraud caught", "False alert", "Fraud missed"],
        default="Correctly cleared",
    )
