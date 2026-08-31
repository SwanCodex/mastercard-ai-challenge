"""
Converts Samiksha's Track B synthetic-face-liveness payloads into
AttackEvent objects. Structurally these are text-based injection/social-
engineering attempts (fake "already verified" claims, spoofed system
notes) - no image/video data involved despite the "face liveness" name -
so they route through the existing Layers 1-3, not a new detection layer.

Ground truth: per fixtures.py, both SESSION-2001 and SESSION-2002 have
true_liveness_signal="fail", so a compliant agent should NEVER enroll for
either session. Every payload here represents an attempt to get
enroll_identity called anyway - attack_succeeded_against_agent is True
by design for all of them (ground truth is unambiguous).

agent_reasoning_trace is SYNTHESIZED (assumed worst-case compliance),
not observed agent behavior - documented explicitly for Layer 3
evaluation methodology.
"""

import json
import uuid
from datetime import datetime

from shared.schemas.attack_event import AttackEvent

PAYLOAD_PATH = "red_team/track_b_deepfake_vishing/synthetic_face_liveness/liveness_injection_payloads.json"


def load_liveness_events(campaign_id: str = "samiksha-track-b-liveness-v1") -> list[AttackEvent]:
    with open(PAYLOAD_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    events = []
    for payload in data.get("payloads", []):
        if "payload_text" in payload:
            untrusted_text = payload["payload_text"]
        elif "turns" in payload:
            parts = []
            for turn in payload["turns"]:
                if "applicant_message" in turn:
                    parts.append(turn["applicant_message"])
                if "system_note" in turn:
                    parts.append(turn["system_note"])
            untrusted_text = " ".join(parts)
        else:
            untrusted_text = ""

        reasoning_trace = (
            f'Agent processed untrusted content containing: "{untrusted_text}". '
            f"Complying with this instruction would enroll the applicant despite a failed liveness check."
        )

        event = AttackEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            track="track_b_deepfake",
            user_instruction=payload.get("user_instruction", ""),
            untrusted_input=untrusted_text,
            agent_reasoning_trace=reasoning_trace,
            campaign_id=campaign_id,
            round_number=1,
            attack_variant_id=payload.get("attack_variant_id", "unknown"),
            attack_succeeded_against_agent=True,
        )
        events.append(event)

    return events


if __name__ == "__main__":
    events = load_liveness_events()
    print(f"Total liveness AttackEvents converted: {len(events)}")
    for e in events:
        print(f"\n[{e.attack_variant_id}] {e.untrusted_input[:80]}")