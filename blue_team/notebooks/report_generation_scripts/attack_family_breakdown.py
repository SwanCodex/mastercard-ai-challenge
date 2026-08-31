"""
Task #8: Attack-family breakdown - per-category catch rates across
Track A (4 sub-families) and Track B liveness, for the report's
attack-family coverage table/chart.
"""

import json
from collections import defaultdict

from blue_team.layer2_injection_classifier.payload_converter import load_track_a_events_with_categories
from blue_team.layer2_injection_classifier.liveness_payload_converter import load_liveness_events
from blue_team.fusion.risk_fusion import run_pipeline


def run_breakdown():
    results_by_family = defaultdict(lambda: {"total": 0, "caught": 0})

    # Track A: 4 sub-families
    print("Running Track A events by category...")
    tagged_events = load_track_a_events_with_categories()
    for event, category in tagged_events:
        verdict = run_pipeline(event)
        results_by_family[category]["total"] += 1
        if verdict.attack_caught:
            results_by_family[category]["caught"] += 1

    # Track B liveness (one family)
    print("Running Track B liveness events...")
    liveness_events = load_liveness_events()
    for event in liveness_events:
        verdict = run_pipeline(event)
        results_by_family["liveness"]["total"] += 1
        if verdict.attack_caught:
            results_by_family["liveness"]["caught"] += 1

    # Print + save results
    print("\n=== ATTACK FAMILY BREAKDOWN ===")
    output = {}
    for family, stats in results_by_family.items():
        rate = stats["caught"] / stats["total"] if stats["total"] else 0
        print(f"{family:20s} {stats['caught']}/{stats['total']} ({rate:.1%})")
        output[family] = {"caught": stats["caught"], "total": stats["total"], "rate": rate}

    with open("blue_team/notebooks/report_generation_scripts/attack_family_breakdown.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print("\nSaved: attack_family_breakdown.json")


if __name__ == "__main__":
    run_breakdown()