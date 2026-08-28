"""
Layer 4 — GraphSAGE GNN, v3: rich features, edge-level fraud prediction.
Matches XGBoost's transaction-level task with comparable feature richness.
"""

import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from blue_team.layer4_transaction_risk_model.graph_builder import (
    load_and_clean,
    build_node_mappings,
    build_pyg_graph_v3,
)


class EdgeFraudGraphSAGE_v3(torch.nn.Module):
    def __init__(self, node_in_channels, edge_feat_dim, hidden_channels=32):
        super().__init__()
        self.conv1 = SAGEConv(node_in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, hidden_channels)
        self.edge_predictor = torch.nn.Sequential(
            torch.nn.Linear(hidden_channels * 2 + edge_feat_dim, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, 1),
        )

    def encode(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.conv2(x, edge_index)
        return x

    def predict_edges(self, node_embeddings, edge_index, edge_attr):
        src, dst = edge_index
        edge_feat = torch.cat([node_embeddings[src], node_embeddings[dst], edge_attr], dim=1)
        return self.edge_predictor(edge_feat).squeeze(-1)


def train_gnn_v3(data, edge_labels, edge_feat_dim, epochs=100, lr=0.001):
    model = EdgeFraudGraphSAGE_v3(node_in_channels=data.x.shape[1], edge_feat_dim=edge_feat_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    num_edges = data.edge_index.shape[1]
    train_idx, test_idx = train_test_split(
        range(num_edges), test_size=0.2, random_state=42, stratify=edge_labels.numpy()
    )
    train_idx = torch.tensor(train_idx)
    test_idx = torch.tensor(test_idx)

    pos_weight = torch.tensor([(edge_labels[train_idx] == 0).sum() / (edge_labels[train_idx] == 1).sum()])

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()

        node_embeddings = model.encode(data.x, data.edge_index)
        edge_scores = model.predict_edges(node_embeddings, data.edge_index, data.edge_attr)

        loss = F.binary_cross_entropy_with_logits(
            edge_scores[train_idx], edge_labels[train_idx], pos_weight=pos_weight
        )
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.4f}")

    model.eval()
    with torch.no_grad():
        node_embeddings = model.encode(data.x, data.edge_index)
        edge_scores = model.predict_edges(node_embeddings, data.edge_index, data.edge_attr)
        probs = torch.sigmoid(edge_scores[test_idx]).numpy()
        true_labels = edge_labels[test_idx].numpy()
        auroc = roc_auc_score(true_labels, probs)

    print(f"\nGNN v3 Test AUROC (rich features, edge-level prediction): {auroc:.4f}")
    return model, auroc


if __name__ == "__main__":
    print("Loading data (10% sample)...")
    df = load_and_clean(frac=0.1)
    card_to_idx, addr_to_idx = build_node_mappings(df)

    print("Building PyG graph v3 (rich features)...")
    data, edge_labels, num_cards, num_addrs, edge_feat_dim = build_pyg_graph_v3(df, card_to_idx, addr_to_idx)
    print(f"Graph: {data.x.shape[0]} nodes, {data.edge_index.shape[1]} edges, edge_feat_dim={edge_feat_dim}")

    print("\nTraining GraphSAGE v3...")
    model, auroc = train_gnn_v3(data, edge_labels, edge_feat_dim)