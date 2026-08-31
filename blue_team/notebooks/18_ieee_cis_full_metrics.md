\# IEEE-CIS Full Metrics (XGBoost + GNN v4)



| Metric | XGBoost | GNN v4 |

|---|---|---|

| AUROC | 0.9394 | 0.8548 |

| Accuracy | 0.9797 | 0.7927 |

| Precision | 0.9205 | 0.0843 |

| Recall | 0.4595 | 0.7522 |

| F1 | 0.6130 | 0.1516 |

| Confusion Matrix | \[\[113811,164],\[2234,1899]] | \[\[162527,42238],\[1281,3888]] |

| Test size | 118,108 | 209,934 |

| Test fraud rate | 3.50% | 2.46% |



\## Key Finding

At the default 0.5 threshold, the two models sit at very different points

on the precision/recall trade-off: XGBoost is precision-heavy (92%

precision, 46% recall - conservative, rarely wrong when it flags fraud),

while GNN is recall-heavy (75% recall, but only 8.4% precision - catches

far more actual fraud but with many more false alarms). AUROC alone

understates this difference. In a production system, GNN's high recall

could be valuable as a first-pass filter (catch more, let downstream

layers like Layer 3 reduce false positives), while XGBoost's precision

suits it better as a final-decision layer. Worth noting GNN's threshold

was not separately calibrated/tuned - 0.5 is a naive default, not

necessarily optimal for this model's score distribution.

