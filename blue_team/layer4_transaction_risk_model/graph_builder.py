"""
Layer 4 — Transaction-Entity Graph Builder
Converts flat IEEE-CIS transaction rows into a graph structure:
  - Card nodes (card1)
  - Merchant-proxy nodes (addr1, since IEEE-CIS has no real merchant ID)
  - Edges = transactions, carrying transaction features + fraud label
"""

import pandas as pd
import numpy as np

DATA_PATH = "data/raw/ieee-cis/train_transaction.csv"


def load_and_clean(frac=1.0, random_state=42):
    df = pd.read_csv(DATA_PATH)
    if frac < 1.0:
        df = df.sample(frac=frac, random_state=random_state).reset_index(drop=True)

    # Drop rows with missing card1 or addr1 — can't build graph nodes without them
    df = df.dropna(subset=["card1", "addr1"])
    return df


def build_node_mappings(df: pd.DataFrame):
    """
    Assign each unique card1 and addr1 value a node index.
    Returns two dicts: card_id -> node_idx, addr_id -> node_idx
    (kept in separate index spaces here; combine later when building
    the actual PyG graph tensor)
    """
    unique_cards = df["card1"].unique()
    unique_addrs = df["addr1"].unique()

    card_to_idx = {card: idx for idx, card in enumerate(unique_cards)}
    addr_to_idx = {addr: idx for idx, addr in enumerate(unique_addrs)}

    return card_to_idx, addr_to_idx


def build_edge_list(df: pd.DataFrame, card_to_idx: dict, addr_to_idx: dict):
    """
    Build the edge list: each transaction is an edge between a card node
    and a merchant-proxy (addr) node.
    Returns: edge_index (list of [card_node, addr_node] pairs),
             edge_labels (isFraud per edge),
             edge_features (TransactionAmt, etc.)
    """
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


if __name__ == "__main__":
    print("Loading data for graph construction (10% sample for fast dev iteration)...")
    df = load_and_clean(frac=0.1)
    print(f"Loaded {len(df)} rows after cleaning")

    card_to_idx, addr_to_idx = build_node_mappings(df)
    edges, labels, amounts = build_edge_list(df, card_to_idx, addr_to_idx)

    summarize_graph(df, card_to_idx, addr_to_idx, edges)

import torch
from torch_geometric.data import Data


def build_pyg_graph(df: pd.DataFrame, card_to_idx: dict, addr_to_idx: dict):
    """
    Converts the transaction data into a PyTorch Geometric Data object.

    Graph design:
    - Card nodes and addr nodes share one combined node index space
      (cards: 0 to N-1, addrs: N to N+M-1)
    - Each transaction becomes an edge between its card node and addr node
    - Edge features: TransactionAmt (normalized)
    - Node labels: for cards, we propagate whether ANY of their transactions
      was fraud (simplification for a first working version)
    """
    num_cards = len(card_to_idx)
    num_addrs = len(addr_to_idx)
    total_nodes = num_cards + num_addrs

    edge_index = []
    edge_attr = []

    # Track per-card fraud signal (any fraud transaction -> flag card as fraud-adjacent)
    card_fraud_flag = np.zeros(num_cards)

    for _, row in df.iterrows():
        card_node = card_to_idx[row["card1"]]
        addr_node = num_cards + addr_to_idx[row["addr1"]]  # offset into addr space

        # add edges in both directions (undirected graph)
        edge_index.append([card_node, addr_node])
        edge_index.append([addr_node, card_node])

        amt = row["TransactionAmt"] if not pd.isna(row["TransactionAmt"]) else 0.0
        edge_attr.append([amt])
        edge_attr.append([amt])

        if row["isFraud"] == 1:
            card_fraud_flag[card_node] = 1

    # Simple node features: just a placeholder for now (node degree could
    # be added later). Using a constant feature + fraud flag for cards,
    # zeros for addr nodes (no direct fraud label at merchant-proxy level)
    node_features = np.zeros((total_nodes, 2))
    node_features[:num_cards, 0] = 1.0  # marks "is a card node"
    node_features[num_cards:, 1] = 1.0  # marks "is an addr node"

    # Labels: only cards have a meaningful fraud label for this first version
    node_labels = np.concatenate([card_fraud_flag, np.full(num_addrs, -1)])  # -1 = no label

    data = Data(
        x=torch.tensor(node_features, dtype=torch.float),
        edge_index=torch.tensor(edge_index, dtype=torch.long).t().contiguous(),
        edge_attr=torch.tensor(edge_attr, dtype=torch.float),
        y=torch.tensor(node_labels, dtype=torch.float),
    )

    return data, num_cards, num_addrs