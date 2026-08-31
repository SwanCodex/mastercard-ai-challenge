"""
Layer 4 - XGBoost on Credit Card Fraud (European cardholders, real
transactions, PCA-anonymized features). Third dataset for cross-dataset
generalization evidence - genuinely difficult due to extreme class
imbalance (0.17% fraud) and real (not synthetic) transaction patterns.
"""

import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix,
)

DATA_PATH = "data/raw/creditcard/creditcard.csv"
MODEL_DIR = "blue_team/layer4_transaction_risk_model/checkpoints"
TARGET = "Class"


def train_and_eval():
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows, fraud rate: {df[TARGET].mean():.4%}")

    y = df[TARGET]
    X = df.drop(columns=[TARGET])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = xgb.XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        eval_metric="auc", random_state=42, n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)

    metrics = {
        "dataset": "Credit Card Fraud (European cardholders)",
        "model": "XGBoost",
        "auroc": roc_auc_score(y_test, y_proba),
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "test_size": len(y_test),
        "test_fraud_rate": float(y_test.mean()),
    }
    print(metrics)

    model.save_model(f"{MODEL_DIR}/creditcard_xgboost_model.json")
    return metrics


if __name__ == "__main__":
    metrics = train_and_eval()
    import json
    with open("blue_team/notebooks/report_generation_scripts/creditcard_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)