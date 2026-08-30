"""
schemas_compat.py (Track C)

Local mirror of the shared `shared/schemas/attack_event.py` contract -
same pattern used by Track A and Track B so Track C can run standalone
even if the shared schema module isn't committed yet.

Field set matches Track A's Section 16 AttackEvent Mapping, with
`track = "track_c_synthetic_identity"` and `audio_file_path = None`
(no audio in this track).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class ToolCall:
    tool_name: str
    arguments: Dict[str, Any]


def new_tool_call(tool_name: str, arguments: Dict[str, Any]) -> ToolCall:
    return ToolCall(tool_name=tool_name, arguments=arguments)


@dataclass
class AttackEvent:
    user_instruction: str
    untrusted_input: str
    agent_reasoning_trace: str
    tool_calls_made: List[ToolCall]
    transaction_fields: Dict[str, Any]
    campaign_id: str
    round_number: int
    attack_variant_id: str
    attack_succeeded_against_agent: bool

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    track: str = "track_c_synthetic_identity"
    audio_file_path: Optional[str] = None


def event_to_dict(event: AttackEvent) -> Dict[str, Any]:

    return {
        "event_id": event.event_id,
        "timestamp": event.timestamp,
        "track": event.track,
        "user_instruction": event.user_instruction,
        "untrusted_input": event.untrusted_input,
        "agent_reasoning_trace": event.agent_reasoning_trace,
        "tool_calls_made": [
            {"tool_name": tc.tool_name, "arguments": tc.arguments}
            for tc in event.tool_calls_made
        ],
        "audio_file_path": event.audio_file_path,
        "transaction_fields": event.transaction_fields,
        "campaign_id": event.campaign_id,
        "round_number": event.round_number,
        "attack_variant_id": event.attack_variant_id,
        "attack_succeeded_against_agent": event.attack_succeeded_against_agent,
    }
