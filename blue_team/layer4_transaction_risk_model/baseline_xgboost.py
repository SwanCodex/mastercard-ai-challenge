"""
Layer 4 — Transaction Risk Model, XGBoost Baseline
This is the REQUIRED comparison baseline for the GNN. We need this
number before claiming any "GNN beats XGBoost by X%" result.
"""
import pickle
import os
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import LabelEncoder

DATA_PATH = "data/raw/ieee-cis/train_transaction.csv"

def load_data(nrows=None, frac=None):
    """
    Load IEEE-CIS transaction data.
    nrows: limit rows for fast dev iteration (sequential, from file start).
    frac: random sample fraction of the FULL dataset (e.g. 1.0 = all rows, randomly ordered).
    """
    if frac is not None:
        df = pd.read_csv(DATA_PATH)
        df = df.sample(frac=frac, random_state=42).reset_index(drop=True)
    else:
        df = pd.read_csv(DATA_PATH, nrows=nrows)
    return df

def preprocess(df: pd.DataFrame, save_encoders=False, encoders_path="blue_team/layer4_transaction_risk_model/checkpoints/label_encoders.pkl"):
    df = df.copy()
    y = df["isFraud"]
    X = df.drop(columns=["isFraud", "TransactionID"])

    categorical_cols = X.select_dtypes(include=["object"]).columns
    encoders = {}

    for col in categorical_cols:
        X[col] = X[col].astype(str).fillna("missing")
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        encoders[col] = le

    if save_encoders:
        os.makedirs(os.path.dirname(encoders_path), exist_ok=True)
        with open(encoders_path, "wb") as f:
            pickle.dump(encoders, f)
        print(f"Encoders saved to {encoders_path}")

    return X, y

def train_and_evaluate(X, y, test_size=0.2, random_state=42):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    print(f"Train fraud rate: {y_train.mean():.4f}, Test fraud rate: {y_test.mean():.4f}")

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        eval_metric="auc",
        random_state=random_state,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auroc = roc_auc_score(y_test, y_pred_proba)

    print(f"\nXGBoost Baseline AUROC: {auroc:.4f}")

    return model, auroc


def save_model(model, path="blue_team/layer4_transaction_risk_model/checkpoints/xgboost_model.json"):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    model.save_model(path)
    print(f"Model saved to {path}")

if __name__ == "__main__":
    print("Loading FULL dataset (randomly sampled)...")
    df = load_data(frac=1.0)
    print(f"Loaded {len(df)} rows, {df.shape[1]} columns")

    X, y = preprocess(df, save_encoders=True)
    print(f"Features: {X.shape[1]}, Fraud rate: {y.mean():.4f}")

    model, auroc = train_and_evaluate(X, y)
    save_model(model)

    print(f"\n=== FINAL BASELINE RESULT ===")
    print(f"XGBoost AUROC on full IEEE-CIS dataset: {auroc:.4f}")
