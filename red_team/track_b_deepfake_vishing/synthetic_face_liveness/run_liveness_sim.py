"""
run_liveness_sim.py

Standalone smoke-test entry point for the liveness/enrollment sub-track,
independent of run_track_b.py. Useful when iterating on
mock_liveness_agent.py or liveness_injection_payloads.json in isolation.

For full campaign logging (AttackEvent JSONL, scoring, audio artifacts
for the paired vishing track), use run_track_b.py from the parent
directory instead.

Usage (from this directory):

    python run_liveness_sim.py
"""

from __future__ import annotations

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

for path in (BASE_DIR, PARENT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

import mock_liveness_agent as live


def _load_payloads() -> list:
    path = os.path.join(BASE_DIR, "liveness_injection_payloads.json")
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data.get("payloads", [])


if __name__ == "__main__":

    payloads = _load_payloads()

    if not payloads:
        print("[ERROR] No liveness payloads found.")
        sys.exit(1)

    first = payloads[0]

    turns = [
        live.Turn(
            operator_instruction=first.get("user_instruction"),
            applicant_message=(
                first.get("payload_text")
                if first.get("channel") != "system_note"
                else None
            ),
            system_note=(
                first.get("payload_text")
                if first.get("channel") == "system_note"
                else None
            ),
        )
    ]

    result = live.run_liveness_scenario(
        turns=turns,
        session_id=first.get("target_id", "SESSION-2001"),
        campaign_id="liveness-smoke-test",
        attack_variant_id=first.get("attack_variant_id", "unknown"),
    )

    print("Reasoning trace:\n", result.reasoning_trace)
    print("\nTool calls:", json.dumps(result.tool_calls_made, indent=2))
    print(
        "\nFinal enrollment:",
        json.dumps(result.final_enrollment, indent=2),
    )
