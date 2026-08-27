"""
Layer 4 — GraphSAGE GNN for transaction fraud risk scoring.
First working version — trains node-level fraud classification
on card nodes only (addr nodes have no direct label).
"""

import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv
from sklearn.metrics import roc_auc_score

from blue_team.layer4_transaction_risk_model.graph_builder import (
    load_and_clean,
    build_node_mappings,
    build_pyg_graph,
)


class FraudGraphSAGE(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels=32):
        super().__init__()
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, hidden_channels)
        self.out = torch.nn.Linear(hidden_channels, 1)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = self.out(x)
        return x.squeeze(-1)


def train_gnn(data, num_cards, epochs=50, lr=0.01):
    model = FraudGraphSAGE(in_channels=data.x.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # Only train/evaluate on card nodes (they have real labels; addr nodes are -1)
    card_mask = torch.zeros(data.x.shape[0], dtype=torch.bool)
    card_mask[:num_cards] = True

    labels = data.y[card_mask]

    # simple 80/20 split on card nodes
    perm = torch.randperm(num_cards)
    split = int(0.8 * num_cards)
    train_idx = perm[:split]
    test_idx = perm[split:]

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        out = model(data.x, data.edge_index)
        card_out = out[:num_cards]

        loss = F.binary_cross_entropy_with_logits(card_out[train_idx], labels[train_idx])
        loss.backward()
        optimizer.step()

        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.4f}")

    # Evaluate
    model.eval()
    with torch.no_grad():
        out = model(data.x, data.edge_index)
        card_out = out[:num_cards]
        probs = torch.sigmoid(card_out[test_idx]).numpy()
        true_labels = labels[test_idx].numpy()

        auroc = roc_auc_score(true_labels, probs)

    print(f"\nGNN Test AUROC (card-node fraud classification): {auroc:.4f}")
    return model, auroc


if __name__ == "__main__":
    print("Loading data (10% sample, matching graph_builder dev settings)...")
    df = load_and_clean(frac=0.1)
    card_to_idx, addr_to_idx = build_node_mappings(df)

    print("Building PyG graph...")
    data, num_cards, num_addrs = build_pyg_graph(df, card_to_idx, addr_to_idx)
    print(f"Graph: {data.x.shape[0]} nodes, {data.edge_index.shape[1]} edges")

    print("\nTraining GraphSAGE...")
    model, auroc = train_gnn(data, num_cards)