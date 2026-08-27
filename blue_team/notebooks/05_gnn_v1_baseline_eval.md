# Layer 4 - GNN Evaluation

## v1 - Naive GraphSAGE Baseline (Day 3)

Dataset: IEEE-CIS, 10% random sample (~52K transactions, 5546 card nodes, 138 addr nodes)

### Design (v1)
- Node features: placeholder only (constant [1,0] for card nodes, [0,1] for addr nodes)
- Task: card-level fraud classification (card flagged as fraud-adjacent if ANY of its transactions were fraud)
- Model: 2-layer GraphSAGE, hidden_channels=32, 50 epochs

### Result
- Test AUROC: 0.5523 (barely above random)
- Loss decreased normally (0.60 -> 0.30), confirming the model trains correctly,
  it just does not have enough signal to learn from

### Why This Result Makes Sense
- Node features carry almost no information (just node-type indicator)
- Card-level fraud labeling is a much coarser task than XGBoost transaction-level prediction
- NOT a fair comparison to XGBoost baseline (0.9394) - different prediction tasks entirely

### Key Learning
Graph structure alone, without informative node/edge features, is not enough
signal for fraud detection. This validates that feature engineering matters
as much as graph structure - an honest, useful finding for the report.

### Next Steps (v2)
- Add real node features: aggregate per-card stats (avg TransactionAmt,
  transaction count, most common ProductCD, card4/card6 type)
- Switch to EDGE-level fraud prediction (matching XGBoost transaction-level task)
  for a fair, direct AUROC comparison
