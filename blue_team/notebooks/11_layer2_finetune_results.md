# Layer 2 - Fine-Tuning Results

## Training (Day 4)

Base model: protectai/deberta-v3-base-prompt-injection-v2
Training data: 82 examples (58 real Track A payloads, 24 hand-written benign)
Split: 66 train / 17 validation (stratified)
5 epochs, CPU training (~7.5 minutes)

### Training Metrics (validation set, in-sample)
Final epoch: accuracy=1.0, precision=1.0, recall=1.0, f1=1.0

WARNING: Perfect validation scores on a 17-example set are a strong
overfitting signal, not proof of real performance. Did NOT trust this
number - proceeded to genuine generalization testing instead.

## Real Generalization Test (Day 4)

Tested against 8 BRAND NEW attack examples and 4 BRAND NEW benign examples,
none of which were in the training data, written in the same "subtle,
polite phrasing" style that was the base model's identified weakness
(patterns from A05-A07, A16).

### Results
- New attack catch rate: 8/8 = 100%
- False positive rate on new benign text: 1/4 = 25%

### Key Finding
The fine-tuned model shows genuine generalization - it correctly caught
100% of held-out attacks using phrasing patterns never seen during
training, confirming it learned the underlying manipulation pattern
rather than memorizing training strings.

However, it also shows a real, traceable trade-off: one false positive
on an ordinary "estimated delivery date" question, at a low-confidence
edge (0.554). Likely caused by class imbalance in training data (58
attack vs 24 benign examples, ~70:30 ratio), which may bias the model
toward flagging shipping/delivery-related language more aggressively.

## Honest Before/After Summary

| Metric | Zero-shot (base) | Fine-tuned |
|---|---|---|
| Catch rate on 58 known Track A payloads | 84.48% | N/A (used for training, not a fair re-test) |
| Catch rate on new, unseen attacks | not tested | 100% (8/8) |
| False positive rate on new benign text | not tested | 25% (1/4, small sample) |

## Next Steps
- Add more benign training examples to fix the class imbalance (target
  closer to 50:50 or 60:40 attack:benign) and reduce false positives
- Test against a larger held-out set for more statistically confident
  numbers (n=12 total is small)
- Consider this v1 fine-tune "good enough for demo", with class-balance
  fix as a stretch improvement if time permits
