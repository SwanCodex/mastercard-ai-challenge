"""
schemas_compat.py (Track B)

Local compatibility layer mirroring shared/schemas/attack_event.py.

Track B (owned by Person A, same as Track A) can run standalone even if
shared/schemas/attack_event.py has not been committed by Person C yet.
If/when the real shared schema lands, this module's fields are designed
to line up with it field-for-field so switching the import is a
one-line change in run_track_b.py.

Do NOT let this module drift from Track A's schemas_compat.py in terms
of field names — the orchestrator/dashboard consume both tracks through
the same AttackEvent shape.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
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

    track: str = "track_b_deepfake"
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Populated for vishing attacks when a synthesized call-audio artifact
    # exists. None for liveness-only attacks or when audio synthesis was
    # skipped/unavailable.
    audio_file_path: Optional[str] = None


def event_to_dict(event: AttackEvent) -> Dict[str, Any]:
    return asdict(event)
