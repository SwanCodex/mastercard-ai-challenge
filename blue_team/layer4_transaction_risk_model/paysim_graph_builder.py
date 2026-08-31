"""
PaySim Graph Builder — genuine account-to-account transaction graph.
Unlike IEEE-CIS (card <-> region proxy), PaySim's nameOrig/nameDest are
real sender/receiver accounts, so this is a natural payment network graph.
Building with rich features from the start (skipping the naive-features
iteration, since IEEE-CIS already established that lesson).
"""

import pandas as pd
import numpy as np
import torch
from torch_geometric.data import Data

DATA_PATH = "data/raw/paysim/PS_20174392719_1491204439457_log.csv"


def load_and_clean(frac=0.05, random_state=42):
    df = pd.read_csv(DATA_PATH)
    if frac < 1.0:
        df = df.sample(frac=frac, random_state=random_state).reset_index(drop=True)
    return df


def build_node_mappings(df: pd.DataFrame):
    # Single shared node space: both orig and dest are accounts of the
    # same type (unlike IEEE-CIS's separate card/addr spaces)
    all_accounts = pd.concat([df["nameOrig"], df["nameDest"]]).unique()
    account_to_idx = {acc: idx for idx, acc in enumerate(all_accounts)}
    return account_to_idx


def build_pyg_graph(df: pd.DataFrame, account_to_idx: dict):
    num_nodes = len(account_to_idx)

    # Edge features: amount, balances, step (time), type one-hot
    numeric_cols = ["amount", "oldbalanceOrg", "newbalanceOrig",
                     "oldbalanceDest", "newbalanceDest", "step"]
    df_features = df[numeric_cols].fillna(0).reset_index(drop=True)

    type_dummies = pd.get_dummies(df["type"], prefix="type").astype(float).reset_index(drop=True)
    df_features = pd.concat([df_features, type_dummies], axis=1)

    df_features[numeric_cols] = (
        (df_features[numeric_cols] - df_features[numeric_cols].mean())
        / (df_features[numeric_cols].std() + 1e-6)
    )

    edge_feature_dim = df_features.shape[1]
    print(f"Edge feature dimension: {edge_feature_dim}")

    # Node features: per-account aggregated stats (as origin sender)
    acc_stats = df.groupby("nameOrig").agg(
        avg_amt=("amount", "mean"),
        std_amt=("amount", "std"),
        txn_count=("amount", "count"),
    ).fillna(0).to_dict("index")

    node_features = np.zeros((num_nodes, 3))
    for acc, idx in account_to_idx.items():
        stats = acc_stats.get(acc, {"avg_amt": 0, "std_amt": 0, "txn_count": 0})
        node_features[idx, 0] = stats["avg_amt"]
        node_features[idx, 1] = stats["std_amt"]
        node_features[idx, 2] = stats["txn_count"]

    for c in range(3):
        col = node_features[:, c]
        std = col.std()
        if std > 1e-6:
            node_features[:, c] = (col - col.mean()) / std

    # Edges: directed orig -> dest, undirected for message passing
    edge_index = []
    edge_attr_list = []
    edge_labels = []

    feature_matrix = df_features.values
    orig_idx = df["nameOrig"].map(account_to_idx).values
    dest_idx = df["nameDest"].map(account_to_idx).values
    labels = df["isFraud"].values

    for i in range(len(df)):
        src, dst = orig_idx[i], dest_idx[i]
        edge_index.append([src, dst])
        edge_index.append([dst, src])
        feat = feature_matrix[i].tolist()
        edge_attr_list.append(feat)
        edge_attr_list.append(feat)
        edge_labels.append(labels[i])
        edge_labels.append(labels[i])

    data = Data(
        x=torch.tensor(node_features, dtype=torch.float),
        edge_index=torch.tensor(edge_index, dtype=torch.long).t().contiguous(),
        edge_attr=torch.tensor(edge_attr_list, dtype=torch.float),
    )
    edge_labels = torch.tensor(edge_labels, dtype=torch.float)

    return data, edge_labels, num_nodes, edge_feature_dim