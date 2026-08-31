"""
Computes full classification metrics (Accuracy, Precision, Recall, F1,
confusion matrix) for XGBoost and GNN v4 on IEEE-CIS - reuses already-
trained artifacts, no retraining.
"""

import pandas as pd
import xgboost as xgb
import pickle
import torch
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score,
)
from sklearn.model_selection import train_test_split

from blue_team.layer4_transaction_risk_model.baseline_xgboost import (
    load_data, preprocess,
)
from blue_team.layer4_transaction_risk_model.graph_builder import (
    load_and_clean, build_node_mappings, build_pyg_graph_v4,
)
from blue_team.layer4_transaction_risk_model.gnn_model import (
    EdgeFraudGraphSAGE_v3, train_gnn_v3,
)

THRESHOLD = 0.5


def eval_xgboost():
    print("=== XGBoost on IEEE-CIS (full dataset) ===")
    df = load_data(frac=1.0)
    X, y = preprocess(df, save_encoders=False)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = xgb.XGBClassifier()
    model.load_model("blue_team/layer4_transaction_risk_model/checkpoints/xgboost_model.json")

    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= THRESHOLD).astype(int)

    metrics = {
        "dataset": "IEEE-CIS",
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
    return metrics


def eval_gnn():
    print("\n=== GNN v4 on IEEE-CIS (retraining for eval - no saved checkpoint) ===")
    df = load_and_clean(frac=1.0)
    card_to_idx, addr_to_idx = build_node_mappings(df)
    data, edge_labels, num_cards, num_addrs, edge_feat_dim = build_pyg_graph_v4(df, card_to_idx, addr_to_idx)

    model, auroc = train_gnn_v3(data, edge_labels, edge_feat_dim, epochs=300, lr=0.001)

    # Reproduce the same test split used inside train_gnn_v3 for consistent metrics
    from sklearn.model_selection import train_test_split as tts
    num_edges = data.edge_index.shape[1]
    _, test_idx = tts(range(num_edges), test_size=0.2, random_state=42, stratify=edge_labels.numpy())
    test_idx = torch.tensor(test_idx)

    model.eval()
    with torch.no_grad():
        node_embeddings = model.encode(data.x, data.edge_index)
        edge_scores = model.predict_edges(node_embeddings, data.edge_index, data.edge_attr)
        probs = torch.sigmoid(edge_scores[test_idx]).numpy()
        true_labels = edge_labels[test_idx].numpy()

    y_pred = (probs >= THRESHOLD).astype(int)

    metrics = {
        "dataset": "IEEE-CIS",
        "model": "GNN v4",
        "auroc": roc_auc_score(true_labels, probs),
        "accuracy": accuracy_score(true_labels, y_pred),
        "precision": precision_score(true_labels, y_pred),
        "recall": recall_score(true_labels, y_pred),
        "f1": f1_score(true_labels, y_pred),
        "confusion_matrix": confusion_matrix(true_labels, y_pred).tolist(),
        "test_size": len(true_labels),
        "test_fraud_rate": float(true_labels.mean()),
    }
    print(metrics)
    return metrics


if __name__ == "__main__":
    xgb_metrics = eval_xgboost()
    gnn_metrics = eval_gnn()

    import json
    with open("blue_team/notebooks/report_generation_scripts/ieee_cis_full_metrics.json", "w", encoding="utf-8") as f:
        json.dump({"xgboost": xgb_metrics, "gnn": gnn_metrics}, f, indent=2)
    print("\nSaved to ieee_cis_full_metrics.json")