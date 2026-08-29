content = """# Fusion Layer - Dilution Bug Fix

## Bug Found (Day 3)

Initial fusion implementation used a flat weighted average across ALL layers
regardless of whether an event had meaningful input for each layer. This
caused a real problem: a pure transaction event (no text/agent trace) with
a legitimate 55.46% fraud signal from Layer 4 got diluted down to an 11.1%
final fusion score, because Layers 1-3 all contributed their (meaningless,
since there was no text to judge) near-zero scores at full weight.

Result before fix: fraud transaction (55% Layer 4 risk) -> fusion 0.111 ->
decision "approve" (WRONG - this was a real fraud sample from IEEE-CIS)

## Fix

compute_fusion_score() now checks has_text_signal = bool(untrusted_input or
agent_reasoning_trace). If an event has no real text content for Layers 1-3
to evaluate, those layers are excluded entirely from the weighted average
rather than counted as legitimate "safe" signal. Weights are re-normalized
over only the layers that actually ran.

## Result After Fix

Fraud transaction event (Layer 4 alone, no text):
- fusion_score: 0.5546 (exactly matches Layer 4's raw score, no dilution)
- decision: review
- attack_caught: true (CORRECT)

Safe transaction event (Layer 4 alone, no text):
- fusion_score: 0.2310
- decision: approve (correct)

Clean/attack text events (Layers 1-3, no transaction data): unaffected,
still working correctly as before.

## Key Learning

Naive weighted averaging across heterogeneous layers is dangerous when
inputs are sparse/event-type-dependent. Event-aware weighting (only
combining layers that have meaningful input for a given event) is
necessary for a fusion layer handling multiple attack tracks with
different data shapes (text-based Track A vs transaction-based Track C).

This is a good story for the deck: caught and fixed during dev testing,
not during integration or live demo - shows rigorous internal testing.
"""

with open("blue_team/notebooks/09_fusion_dilution_bug_fix.md", "w", encoding="utf-8") as f:
    f.write(content)

print("File written successfully.")