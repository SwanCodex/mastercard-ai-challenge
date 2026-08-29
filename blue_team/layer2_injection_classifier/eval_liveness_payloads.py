"""
Runs Samiksha's Track B liveness/enrollment payloads through the full
fusion pipeline (Layers 1-3, since these are text-based social-engineering/
injection attacks, no audio or transaction data involved).
"""

from blue_team.layer2_injection_classifier.liveness_payload_converter import load_liveness_events
from blue_team.fusion.risk_fusion import run_pipeline


def run_eval():
    events = load_liveness_events()
    print(f"Evaluating {len(events)} liveness attack payloads through full fusion pipeline...\n")

    caught = 0
    for event in events:
        verdict = run_pipeline(event)
        status = "CAUGHT" if verdict.attack_caught else "MISSED"
        if verdict.attack_caught:
            caught += 1

        print(f"[{status}] {event.attack_variant_id} -> {verdict.decision} (fusion={verdict.fusion_score:.3f})")
        for ls in verdict.layer_scores:
            flag = "FLAGGED" if ls.flagged else "clear"
            print(f"    [{ls.layer_name}] {flag} ({ls.score:.3f}) - {ls.reason[:90]}")
        print()

    print(f"=== RESULT: {caught}/{len(events)} caught ({caught/len(events):.1%}) ===")


if __name__ == "__main__":
    run_eval()