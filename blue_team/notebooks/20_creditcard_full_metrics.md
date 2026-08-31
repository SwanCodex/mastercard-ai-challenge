\# Credit Card Fraud Full Metrics (XGBoost)



Dataset: real European cardholder transactions, PCA-anonymized features

(V1-V28), extreme class imbalance (0.17% fraud - among the most

imbalanced fraud datasets commonly used in research).



| Metric | Value |

|---|---|

| AUROC | 0.9616 |

| Accuracy | 0.9995 |

| Precision | 0.9277 |

| Recall | 0.7857 |

| F1 | 0.8508 |

| Confusion Matrix | \[\[56858, 6], \[21, 77]] |

| Test size | 56,962 |

| Test fraud rate | 0.172% |



\## Cross-Dataset Summary

| Dataset | Nature | AUROC | Recall |

|---|---|---|---|

| PaySim | Synthetic | 0.9992 | 0.8332 |

| Credit Card Fraud | Real, extreme imbalance | 0.9616 | 0.7857 |

| IEEE-CIS | Real, richest features | 0.9394 | 0.4595 |



\## Key Finding

A coherent difficulty gradient across the three datasets: PaySim

(synthetic, rule-based fraud generation) is easiest; Credit Card Fraud

(real transactions, extreme 0.17% imbalance) is moderately difficult;

IEEE-CIS (real transactions, 392 raw features, most diverse fraud

patterns) is hardest. This gradient is itself evidence the model isn't

just overfitting to one dataset's quirks - performance degrades sensibly

with genuine task difficulty rather than randomly.

