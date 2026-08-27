"""
Layer 4 — Transaction-Entity Graph Builder
Converts flat IEEE-CIS transaction rows into a graph structure:
  - Card nodes (card1)
  - Merchant-proxy nodes (addr1, since IEEE-CIS has no real merchant ID)
  - Edges = transactions, carrying transaction features + fraud label
"""

import pandas as pd
import numpy as np
import torch
from torch_geometric.data import Data

DATA_PATH = "data/raw/ieee-cis/train_transaction.csv"


def load_and_clean(frac=1.0, random_state=42):
    df = pd.read_csv(DATA_PATH)
    if frac < 1.0:
        df = df.sample(frac=frac, random_state=random_state).reset_index(drop=True)
    df = df.dropna(subset=["card1", "addr1"])
    return df


def build_node_mappings(df: pd.DataFrame):
    unique_cards = df["card1"].unique()
    unique_addrs = df["addr1"].unique()
    card_to_idx = {card: idx for idx, card in enumerate(unique_cards)}
    addr_to_idx = {addr: idx for idx, addr in enumerate(unique_addrs)}
    return card_to_idx, addr_to_idx


def build_edge_list(df: pd.DataFrame, card_to_idx: dict, addr_to_idx: dict):
    edges = []
    labels = []
    amounts = []
    for _, row in df.iterrows():
        card_node = card_to_idx[row["card1"]]
        addr_node = addr_to_idx[row["addr1"]]
        edges.append((card_node, addr_node))
        labels.append(row["isFraud"])
        amounts.append(row["TransactionAmt"])
    return edges, labels, amounts


def summarize_graph(df, card_to_idx, addr_to_idx, edges):
    print(f"Total transactions (edges): {len(edges)}")
    print(f"Unique card nodes: {len(card_to_idx)}")
    print(f"Unique addr (merchant-proxy) nodes: {len(addr_to_idx)}")
    print(f"Fraud rate: {df['isFraud'].mean():.4f}")
    avg_txns_per_card = len(edges) / len(card_to_idx)
    print(f"Avg transactions per card: {avg_txns_per_card:.2f}")


def build_pyg_graph_v3(df: pd.DataFrame, card_to_idx: dict, addr_to_idx: dict):
    """
    v3: Richer node features (per-card aggregates) + richer edge features
    (ProductCD, card metadata, C1-C10, D1-D5) for a fair comparison against
    XGBoost's full feature set.
    """
    num_cards = len(card_to_idx)
    num_addrs = len(addr_to_idx)
    total_nodes = num_cards + num_addrs

    numeric_edge_cols = [
        "TransactionAmt", "card2", "card3", "card5",
        "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10",
        "D1", "D2", "D3", "D4", "D5",
    ]
    df_features = df[numeric_edge_cols].fillna(0).reset_index(drop=True)

    product_dummies = pd.get_dummies(df["ProductCD"], prefix="product").astype(float).reset_index(drop=True)
    df_features = pd.concat([df_features, product_dummies], axis=1)

    df_features[numeric_edge_cols] = (
        (df_features[numeric_edge_cols] - df_features[numeric_edge_cols].mean())
        / (df_features[numeric_edge_cols].std() + 1e-6)
    )

    edge_feature_dim = df_features.shape[1]
    print(f"Edge feature dimension: {edge_feature_dim}")

    card_stats = df.groupby("card1").agg(
        avg_amt=("TransactionAmt", "mean"),
        std_amt=("TransactionAmt", "std"),
        txn_count=("TransactionAmt", "count"),
        avg_c1=("C1", "mean"),
        avg_c2=("C2", "mean"),
    ).fillna(0).to_dict("index")

    node_feat_dim = 6
    node_features = np.zeros((total_nodes, node_feat_dim))
    for card_val, idx in card_to_idx.items():
        stats = card_stats.get(card_val, {})
        node_features[idx, 0] = stats.get("avg_amt", 0)
        node_features[idx, 1] = stats.get("std_amt", 0)
        node_features[idx, 2] = stats.get("txn_count", 0)
        node_features[idx, 3] = stats.get("avg_c1", 0)
        node_features[idx, 4] = stats.get("avg_c2", 0)
        node_features[idx, 5] = 1.0

    addr_counts = df["addr1"].value_counts().to_dict()
    for addr_val, idx in addr_to_idx.items():
        node_features[num_cards + idx, 2] = addr_counts.get(addr_val, 0)

    for c in [0, 1, 2, 3, 4]:
        col = node_features[:, c]
        std = col.std()
        if std > 1e-6:
            node_features[:, c] = (col - col.mean()) / std

    edge_index = []
    edge_attr_list = []
    edge_labels = []

    feature_matrix = df_features.values

    for i, (_, row) in enumerate(df.iterrows()):
        card_node = card_to_idx[row["card1"]]
        addr_node = num_cards + addr_to_idx[row["addr1"]]

        edge_index.append([card_node, addr_node])
        edge_index.append([addr_node, card_node])

        feat = feature_matrix[i].tolist()
        edge_attr_list.append(feat)
        edge_attr_list.append(feat)

        edge_labels.append(row["isFraud"])
        edge_labels.append(row["isFraud"])

    data = Data(
        x=torch.tensor(node_features, dtype=torch.float),
        edge_index=torch.tensor(edge_index, dtype=torch.long).t().contiguous(),
        edge_attr=torch.tensor(edge_attr_list, dtype=torch.float),
    )
    edge_labels = torch.tensor(edge_labels, dtype=torch.float)

    return data, edge_labels, num_cards, num_addrs, edge_feature_dim


if __name__ == "__main__":
    print("Loading data for graph construction (10% sample)...")
    df = load_and_clean(frac=0.1)
    print(f"Loaded {len(df)} rows after cleaning")

    card_to_idx, addr_to_idx = build_node_mappings(df)
    edges, labels, amounts = build_edge_list(df, card_to_idx, addr_to_idx)

    summarize_graph(df, card_to_idx, addr_to_idx, edges)