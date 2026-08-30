"""
Layer 4 — Transaction Risk Model, Inference Wrapper
"""

import pandas as pd
import xgboost as xgb
import pickle
import numpy as np

from shared.schemas.verdict import LayerScore
from shared.schemas.attack_event import AttackEvent

MODEL_PATH = "blue_team/layer4_transaction_risk_model/layer4_checkpoints/xgboost_model.json"
ENCODERS_PATH = "blue_team/layer4_transaction_risk_model/layer4_checkpoints/label_encoders.pkl"

_model = None
_encoders = None


def load_model():
    global _model
    if _model is None:
        _model = xgb.XGBClassifier()
        _model.load_model(MODEL_PATH)
    return _model


def load_encoders():
    global _encoders
    if _encoders is None:
        with open(ENCODERS_PATH, "rb") as f:
            _encoders = pickle.load(f)
    return _encoders


def score_transaction(transaction_fields: dict) -> float:
    if not transaction_fields:
        return 0.0

    model = load_model()
    encoders = load_encoders()
    expected_cols = model.get_booster().feature_names

    row = {col: transaction_fields.get(col, 0) for col in expected_cols}
    df_row = pd.DataFrame([row])

    # Apply the same label encoding used during training
    for col, le in encoders.items():
        if col in df_row.columns:
            raw_val = str(df_row[col].iloc[0])
            if raw_val in le.classes_:
                df_row[col] = le.transform([raw_val])[0]
            else:
                # unseen category at inference time - fall back to 0
                df_row[col] = 0

    prob = model.predict_proba(df_row)[0, 1]
    return float(prob)


def score_event(event: AttackEvent) -> LayerScore:
    if not event.transaction_fields:
        return LayerScore(
            layer_name="layer4_transaction_risk",
            score=0.0,
            flagged=False,
            reason="no transaction data provided",
        )

    score = score_transaction(event.transaction_fields)
    flagged = score >= 0.5

    return LayerScore(
        layer_name="layer4_transaction_risk",
        score=score,
        flagged=flagged,
        reason=f"XGBoost transaction risk model predicted {score:.2%} fraud probability",
    )