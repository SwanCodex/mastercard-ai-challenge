"""
Trains GraphSAGE on the PaySim account-transaction graph, reusing the
same architecture as IEEE-CIS v3/v4.
"""

from blue_team.layer4_transaction_risk_model.paysim_graph_builder import (
    load_and_clean, build_node_mappings, build_pyg_graph,
)
from blue_team.layer4_transaction_risk_model.gnn_model import train_gnn_v3

if __name__ == "__main__":
    print("Loading PaySim data (5% sample for graph construction speed)...")
    df = load_and_clean(frac=0.05)
    print(f"Loaded {len(df)} rows, fraud rate: {df['isFraud'].mean():.4%}")

    account_to_idx = build_node_mappings(df)
    print(f"Unique accounts (nodes): {len(account_to_idx)}")

    print("Building PyG graph...")
    data, edge_labels, num_nodes, edge_feat_dim = build_pyg_graph(df, account_to_idx)
    print(f"Graph: {data.x.shape[0]} nodes, {data.edge_index.shape[1]} edges, edge_feat_dim={edge_feat_dim}")

    print("\nTraining GraphSAGE on PaySim...")
    model, auroc = train_gnn_v3(data, edge_labels, edge_feat_dim, epochs=200, lr=0.001)

    print(f"\n=== PaySim GNN Final AUROC: {auroc:.4f} ===")