"""
Layer 4 - XGBoost on PaySim (second-dataset generalization check).
Note: PaySim is SYNTHETIC data (simulator-generated, not real transactions)
- reported honestly as a large-scale sanity check, not equal-weight
evidence to IEEE-CIS / Credit Card Fraud.
"""

import pandas as pd
import xgboost as xgb
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    roc_auc_score, accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix,
)

DATA_PATH = "data/raw/paysim/PS_20174392719_1491204439457_log.csv"
MODEL_DIR = "blue_team/layer4_transaction_risk_model/checkpoints"

DROP_COLS = ["nameOrig", "nameDest", "isFlaggedFraud"]
TARGET = "isFraud"


def load_and_preprocess():
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows, fraud rate: {df[TARGET].mean():.4%}")

    y = df[TARGET]
    X = df.drop(columns=DROP_COLS + [TARGET])

    le = LabelEncoder()
    X["type"] = le.fit_transform(X["type"])

    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(f"{MODEL_DIR}/paysim_type_encoder.pkl", "wb") as f:
        pickle.dump(le, f)

    return X, y


def train_and_eval():
    X, y = load_and_preprocess()
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
        "dataset": "PaySim (synthetic)",
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

    model.save_model(f"{MODEL_DIR}/paysim_xgboost_model.json")

    # Bonus: compare against PaySim's own built-in naive rule
    df_full = pd.read_csv(DATA_PATH)
    _, test_idx = train_test_split(range(len(df_full)), test_size=0.2, random_state=42, stratify=df_full[TARGET])
    naive_flag = df_full.iloc[test_idx]["isFlaggedFraud"]
    naive_recall = recall_score(y_test, naive_flag)
    print(f"\nPaySim's own naive rule recall (comparison baseline): {naive_recall:.4f}")

    return metrics


if __name__ == "__main__":
    metrics = train_and_eval()
    import json
    with open("blue_team/notebooks/report_generation_scripts/paysim_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)