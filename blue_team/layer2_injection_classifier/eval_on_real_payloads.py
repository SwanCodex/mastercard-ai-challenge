"""
Runs Samiksha's real Track A payloads through Layer 2 (zero-shot),
producing a proper evaluation report before fine-tuning.
"""

from blue_team.layer2_injection_classifier.payload_converter import load_all_track_a_events
from blue_team.layer2_injection_classifier.inference import classify


def run_eval():
    events = load_all_track_a_events()
    print(f"Evaluating {len(events)} real attack payloads (zero-shot Layer 2)...\n")

    results = []
    caught = 0

    for event in events:
        result = classify(event.untrusted_input)
        is_caught = result["label"] == "INJECTION"
        caught += int(is_caught)

        results.append({
            "attack_variant_id": event.attack_variant_id,
            "text": event.untrusted_input[:60],
            "predicted_label": result["label"],
            "confidence": result["score"],
            "caught": is_caught,
        })

    catch_rate = caught / len(events) if events else 0

    print(f"=== RESULTS ===")
    print(f"Total attacks: {len(events)}")
    print(f"Caught (zero-shot): {caught}")
    print(f"Catch rate: {catch_rate:.2%}\n")

    print("=== MISSED ATTACKS (highest priority for fine-tuning) ===")
    for r in results:
        if not r["caught"]:
            print(f"[{r['attack_variant_id']}] {r['text']}...")

    return results, catch_rate


if __name__ == "__main__":
    run_eval()