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
            if "wording" in variant:
                untrusted_text = variant["wording"]
            elif "message" in variant:
                untrusted_text = variant["message"]
            elif "turns" in variant:
                turn_texts = []

                for turn in variant["turns"]:
                    if isinstance(turn, str):
                        turn_texts.append(turn)

                    elif isinstance(turn, dict):
                        # Common multi-turn schema:
                        # {"role": "...", "content": "..."}
                        content = (
                            turn.get("content")
                            or turn.get("message")
                            or turn.get("text")
                            or ""
                        )

                        if isinstance(content, str):
                            turn_texts.append(content)
                        else:
                            turn_texts.append(str(content))

                    else:
                        turn_texts.append(str(turn))

                untrusted_text = " ".join(
                    text for text in turn_texts if text
                )
            elif "fragments" in variant:
                untrusted_text = " ".join(variant["fragments"])
            elif "message_chain" in variant:
                untrusted_text = " ".join(variant["message_chain"])
            else:
                untrusted_text = ""

            # SYNTHESIZED reasoning trace: assumes worst-case (agent complied
            # with the injected instruction), for evaluating Layer 3 on
            # realistic attack content rather than a content-free scenario.
            # This is an assumed/synthesized trace, NOT observed agent
            # behavior - documented explicitly in the report methodology.
            reasoning_trace = (
                f'Agent processed untrusted content containing: "{untrusted_text}". '
                f"Complying with this instruction would result in: {objective}"
            )

            event = AttackEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                track=track,
                user_instruction=user_instruction,
                untrusted_input=untrusted_text,
                agent_reasoning_trace=reasoning_trace,
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

def load_track_a_events_with_categories(campaign_id: str = "samiksha-track-a-v1") -> list[tuple[AttackEvent, str]]:
    """
    Same as load_all_track_a_events(), but tags each event with its
    source category (direct/indirect/multi_turn_drip/agent_to_agent)
    for per-family breakdown reporting. Does not modify the AttackEvent
    schema - category is tracked alongside, not on the event itself.
    """
    file_category_map = {
        f"{PAYLOAD_DIR}/direct/direct_payloads.json": "direct",
        f"{PAYLOAD_DIR}/indirect/indirect_payloads.json": "indirect",
        f"{PAYLOAD_DIR}/multi_turn_drip/multi_turn_drip_payloads.json": "multi_turn_drip",
        f"{PAYLOAD_DIR}/agent_to_agent/agent_to_agent_payloads.json": "agent_to_agent",
    }

    tagged_events = []
    for filepath, category in file_category_map.items():
        try:
            data = load_payload_file(filepath)
            events = payload_to_attack_events(data, campaign_id)
            for e in events:
                tagged_events.append((e, category))
        except FileNotFoundError:
            print(f"WARNING: {filepath} not found, skipping")

    return tagged_events

if __name__ == "__main__":
    events = load_all_track_a_events()
    print(f"\nTotal AttackEvents converted: {len(events)}")

    if events:
        print("\nSample converted event:")
        print(events[0].model_dump_json(indent=2))