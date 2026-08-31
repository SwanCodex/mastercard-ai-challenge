"""
PaySim GNN at 100% data - final data point for the AUROC-vs-data-size
curve. Based on 5% (0.9508) and 20% (0.9480) results, expected to land
close to those numbers - this run is for narrative/visual completeness
(a 3-point saturation curve), not because we expect a different result.
"""

from blue_team.layer4_transaction_risk_model.paysim_graph_builder import (
    load_and_clean, build_node_mappings, build_pyg_graph,
)
from blue_team.layer4_transaction_risk_model.gnn_model import train_gnn_v3

if __name__ == "__main__":
    print("Loading PaySim data (100% - full dataset)...")
    df = load_and_clean(frac=1.0)
    print(f"Loaded {len(df)} rows, fraud rate: {df['isFraud'].mean():.4%}")

    account_to_idx = build_node_mappings(df)
    print(f"Unique accounts (nodes): {len(account_to_idx)}")

    print("Building PyG graph...")
    data, edge_labels, num_nodes, edge_feat_dim = build_pyg_graph(df, account_to_idx)
    print(f"Graph: {data.x.shape[0]} nodes, {data.edge_index.shape[1]} edges, edge_feat_dim={edge_feat_dim}")

    print("\nTraining GraphSAGE on PaySim (100%)...")
    model, auroc = train_gnn_v3(data, edge_labels, edge_feat_dim, epochs=200, lr=0.001)

    print(f"\n=== 100% PaySim GNN Final AUROC: {auroc:.4f} ===")