# Layer 4 - Transaction Risk Model Evaluation

## XGBoost Baseline (Day 2)

Dataset: IEEE-CIS Fraud Detection, full dataset (590,540 rows, 392 features)
Split: 80/20 train/test, stratified, random_state=42

### Result

- AUROC: 0.9394
- Fraud rate: 3.50% (matches documented IEEE-CIS rate)
- Train fraud rate: 3.50%, Test fraud rate: 3.50% (stratified split confirmed working)

### Next Steps

- Build GNN (GraphSAGE/GAT) on transaction-entity graph
- Compare GNN AUROC against this 0.9394 baseline
- Report the real delta, whatever it is - do not force it to match literature claims
