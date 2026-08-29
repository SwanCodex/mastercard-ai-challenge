content = """# Layer 2 - Zero-Shot Evaluation on Real Track A Payloads

## Result (Day 3)

Dataset: 58 real attack payloads from Samiksha's Track A taxonomy
(direct: 12, indirect: 22, multi_turn_drip: 12, agent_to_agent: 12)

Model: protectai/deberta-v3-base-prompt-injection-v2 (zero-shot, no fine-tuning)

### Result
- Catch rate: 84.48% (49/58)
- 9 attacks missed

### Missed Attack Pattern Analysis
The misses are NOT random - they cluster into specific, identifiable
categories:

1. Polite/contextually-plausible phrasing (A05, A06, A07): attacks
   phrased as normal e-commerce copy ("apply promotional code", "add
   the complementary item as part of the bundle") rather than an
   obvious command override. No urgency or authority-framing keywords
   for the classifier to key on.

2. Multi-turn drip attacks (A12, A13, A25): attacks split across
   conversational turns or fragments, evaluated here as a single
   concatenated string. The classifier likely was not trained on this
   attack pattern (delayed activation, split payload reconstruction).

3. Agent-to-agent impersonation (A16): messages framed as legitimate
   inter-agent system communication ("Merchant checkout confirmation",
   "operations notice") - sounds like infrastructure, not an attack.

### Why This Matters
This is a precise, actionable fine-tuning target: rather than generic
improvement, we know exactly which 3 attack patterns need targeted
training examples. This is a stronger, more specific finding than a
flat catch-rate number alone.

### Next Steps
- Fine-tune Layer 2 specifically weighting these 3 miss categories
- Consider whether multi-turn attacks need a structurally different
  detection approach (e.g. evaluating conversation state over time,
  not just single-string classification) - possible v2 architecture
  note for Layer 2, or a job for Layer 3's alignment check instead
- Re-run this exact 58-case eval after fine-tuning for a clean before/after
"""

with open("blue_team/notebooks/10_layer2_real_payload_baseline.md", "w", encoding="utf-8") as f:
    f.write(content)

print("File written successfully.")