"""
Converts Samiksha's Track A payload JSON format into AttackEvent objects,
so we can run them through Layer 2 (and the full fusion pipeline) for
real evaluation and fine-tuning data.
"""

import json
import uuid
from datetime import datetime

from shared.schemas.attack_event import AttackEvent

PAYLOAD_DIR = "red_team/track_a_agentic_payments/injection_payloads"


def load_payload_file(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def payload_to_attack_events(payload_data: dict, campaign_id: str = "samiksha-track-a-v1") -> list[AttackEvent]:
    events = []
    track = payload_data.get("track", "track_a_agentic")

    for payload in payload_data.get("payloads", []):
        objective = payload.get("objective", "")
        ground_truth = payload.get("ground_truth_authorized", {})
        user_instruction = f"Process this {payload.get('target', 'transaction')} according to the authorized parameters: {ground_truth}"

        for variant in payload.get("variants", []):
            # Samiksha's payloads use 5 different field names across categories:
            # - "wording": single string (direct, indirect)
            # - "turns": list of sequential conversation turns (multi_turn_drip)
            # - "message": single string (agent_to_agent)
            # - "fragments": list of pieces meant to be combined (multi_turn_drip)
            # - "message_chain": list of fabricated agent messages (agent_to_agent)
            if "wording" in variant:
                untrusted_text = variant["wording"]
            elif "message" in variant:
                untrusted_text = variant["message"]
            elif "turns" in variant:
                untrusted_text = " ".join(variant["turns"])
            elif "fragments" in variant:
                untrusted_text = " ".join(variant["fragments"])
            elif "message_chain" in variant:
                untrusted_text = " ".join(variant["message_chain"])
            else:
                untrusted_text = ""

            event = AttackEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                track=track,
                user_instruction=user_instruction,
                untrusted_input=untrusted_text,
                agent_reasoning_trace=None,
                campaign_id=campaign_id,
                round_number=1,
                attack_variant_id=variant.get("id", payload.get("id", "unknown")),
                attack_succeeded_against_agent=False,
            )
            events.append(event)

    return events

def load_all_track_a_events(campaign_id: str = "samiksha-track-a-v1") -> list[AttackEvent]:
    """
    Loads and converts all 4 payload categories (direct, indirect,
    multi_turn_drip, agent_to_agent) into one combined list of AttackEvents.
    """
    files = [
        f"{PAYLOAD_DIR}/direct/direct_payloads.json",
        f"{PAYLOAD_DIR}/indirect/indirect_payloads.json",
        f"{PAYLOAD_DIR}/multi_turn_drip/multi_turn_drip_payloads.json",
        f"{PAYLOAD_DIR}/agent_to_agent/agent_to_agent_payloads.json",
    ]

    all_events = []
    for filepath in files:
        try:
            data = load_payload_file(filepath)
            events = payload_to_attack_events(data, campaign_id)
            all_events.extend(events)
            print(f"Loaded {len(events)} events from {filepath}")
        except FileNotFoundError:
            print(f"WARNING: {filepath} not found, skipping")

    return all_events


if __name__ == "__main__":
    events = load_all_track_a_events()
    print(f"\nTotal AttackEvents converted: {len(events)}")

    if events:
        print("\nSample converted event:")
        print(events[0].model_dump_json(indent=2))