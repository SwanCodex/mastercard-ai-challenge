\# Layer 4 - GNN v4: Feature Engineering to Close XGBoost Gap



\## Motivation

v3 (24 edge features) reached AUROC 0.72, far below XGBoost's 0.9394 (392

features). Investigated whether feature richness genuinely was the

bottleneck, as hypothesized in v3's notes.



\## Missingness Analysis

Checked missingness on IEEE-CIS's 339 V-columns (anonymized Vesta engineered

features) and remaining D-columns before including them - many V/D blocks

are 70-96% missing and would inject noise, not signal, if naively filled

with 0.



Found 131 V-columns with <15% missingness (V12-V34, V53-V74, V95-V137,

V279-V321) plus D10 (11.7% missing) that were genuinely usable.



\## v4 Design

Same architecture as v3 (2-layer GraphSAGE, edge-level prediction, node

features = per-card aggregates). Edge feature set expanded from 24 -> 156

by adding the 131 low-missingness V-columns + D10.



\## Results



| Version | AUROC | Edge Features | Data Sample |

|---|---|---|---|

| v1 | 0.5523 | placeholder | 10% |

| v2 | 0.598 | 1 | 10% |

| v3 | 0.72 | 24 | 10% |

| v4 | 0.8427 | 156 | 50% |

| v4 (full) | 0.8495 | 156 | 100% |

| XGBoost baseline | 0.9394 | 392 | 100% |



\## Key Finding

Feature richness closed most of the gap: 0.72 -> 0.85 (a 13-point AUROC

gain) purely from adding V-columns, with no architecture change. Confirms

v3's hypothesis directly.



Data volume alone gave diminishing returns AGAIN at this larger scale:

50% -> 100% of data only moved AUROC by +0.007 (0.8427 -> 0.8495), nearly

identical in shape to the earlier 10% -> 50% result in v3 (+0.01). This is

now a two-point-confirmed pattern: for this GNN architecture on IEEE-CIS,

the ceiling is feature-driven, not data-volume-driven.



Minor training instability observed at epoch 240 (loss briefly increased

from 0.9519 to 0.9816 before recovering and continuing to decrease) - did

not derail final convergence, worth noting but not treated as a blocker.



\## Remaining Gap to XGBoost (0.85 vs 0.94)

Not pursued further given time constraints. Would require: full 339

V-column set with a real imputation strategy (rather than excluding

high-missingness blocks), categorical card4/card6 encoding, and possibly

architecture changes (attention-based aggregation, deeper GNN). Diminishing

returns expected relative to remaining project time - this is documented

here as a legitimate "future work" item rather than pursued now.



\## Honest Conclusion for Report

The GNN's underperformance relative to XGBoost on this dataset is

substantially, though not entirely, a feature-availability problem rather

than a fundamental limitation of graph-based fraud detection. This nuances

the earlier v3 conclusion: graph structure combined with rich features

narrows the gap considerably (0.72 -> 0.85), even though IEEE-CIS's lack of

true merchant IDs still caps the achievable relational signal.

