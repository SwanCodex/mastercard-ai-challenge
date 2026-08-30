# Fusion Layer - First End-to-End Pipeline Test

## Result (Day 3)

First successful end-to-end run: Layers 1, 2, 3 combined via weighted fusion.

### Clean Event
All layers correctly identified no threat.
Fusion score: ~0.00001 -> decision: approve (correct)

### Attack Event (indirect injection via product page)
All 3 layers independently flagged the attack:
- Layer 1 (regex): caught "ignore instructions" phrasing, score 0.9
- Layer 2 (classifier): 0.9999996 injection probability
- Layer 3 (LLM judge): caught the intent mismatch specifically, correctly
  explained the shipping address manipulation in natural language

Fusion score: 0.959 -> decision: decline (correct, well above 0.75 threshold)

### Key Finding
This is the first working end-to-end defense pipeline. Three structurally
different detection methods (regex, fine-tuned classifier, LLM reasoning)
independently converged on the correct verdict for both clean and attack
cases - validates the layered-defense architecture decision.

### Important Metric: Latency
- Clean event: 12,554ms
- Attack event: 17,751ms
Layer 3 (Gemini API call) is the dominant latency cost - expected, since
it is a real network round-trip to an LLM, unlike Layers 1/2 which run
locally in milliseconds.

Production implication (future work): Layer 3 could run conditionally
(only when Layer 1/2 scores are ambiguous) rather than always, to reduce
average latency significantly.

### Not Yet Integrated
- Layer 4 (GNN/XGBoost) - needs full transaction row input, not AttackEvent
- Layer 5 (deepfake detector) - needs audio input, pending Samiksha Track B payloads

### Next Steps
- Integrate Layer 4 once transaction-shaped fields are available in AttackEvent
- Integrate Layer 5 once audio clips are available
- Tune LAYER_WEIGHTS and thresholds using a larger evaluation set
