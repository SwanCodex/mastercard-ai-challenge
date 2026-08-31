\# Layer 2 Full Metrics: Zero-shot vs Fine-tuned



Both evaluated on the identical held-out 12-example set (8 new attacks +

4 new benign, none seen during fine-tuning) - a fair, apples-to-apples

comparison, not different test sets.



| Metric | Zero-shot | Fine-tuned |

|---|---|---|

| Accuracy | 0.750 | 0.833 |

| Precision | 1.000 | 1.000 |

| Recall | 0.625 | 0.750 |

| F1 | 0.769 | 0.857 |

| Confusion Matrix | \[\[4,0],\[3,5]] | \[\[4,0],\[2,6]] |

| Test size | 12 | 12 |



\## Key Finding

Fine-tuning improved recall (+0.125) while holding precision perfect

(1.0 in both cases, zero false positives on this set) - a clean

improvement with no precision trade-off on the held-out test. This

reproduces the earlier result from notebooks/16 exactly (post class-

balance-fix: 6/8 attacks caught, 0/4 false positives), now formalized

with standard classification metrics.



The 2 remaining fine-tuned misses are independently confirmed (notebooks/12)

to be caught by Layer 3's alignment check, closing the gap to 100% at the

full fusion-pipeline level - the multi-layer architecture compensates for

Layer 2's residual recall gap.

