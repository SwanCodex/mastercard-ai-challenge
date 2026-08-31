\# PaySim Full Metrics (XGBoost)



Dataset note: PaySim is SYNTHETIC (simulator-generated from real mobile

money transaction patterns), not real transactions. Reported as a

large-scale generalization sanity check, not equal-weight evidence to

IEEE-CIS or Credit Card Fraud (both real transactions).



| Metric | Value |

|---|---|

| AUROC | 0.9992 |

| Accuracy | 0.9997 |

| Precision | 0.9654 |

| Recall | 0.8332 |

| F1 | 0.8945 |

| Confusion Matrix | \[\[1270832, 49], \[274, 1369]] |

| Test size | 1,272,524 |

| Test fraud rate | 0.129% |



\## Key Finding

Near-perfect AUROC, consistent with PaySim's known rule-based, relatively

simple fraud-generation logic (fraud concentrated in TRANSFER/CASH\_OUT

transaction types) - this is expected and should not be oversold as

model superiority; it reflects the dataset's characteristics, not a

harder achievement than the IEEE-CIS result (0.9394 AUROC on real,

subtler fraud patterns).



\## Bonus Comparison

PaySim's own built-in `isFlaggedFraud` naive rule (transfers > 200,000)

caught 0/1,369 fraud cases in the test set (0% recall) - the simulator's

naive baseline is essentially non-functional in practice. Our trained

XGBoost model achieves 83.3% recall on the same test set, a concrete,

striking before/after comparison point for the report.

