"""
schemas_compat.py

Compatibility shim for the shared AttackEvent / Verdict schemas.

Track A code imports AttackEvent / Verdict / new_tool_call from THIS
module rather than importing `shared.schemas.attack_event` directly.

Why this exists
----------------
- Person C owns `shared/schemas/attack_event.py` and
  `shared/schemas/verdict.py` (per Solution_And_Team_Plan.md, Part 5/6).
- Those files may not be committed yet, or may live on a branch that
  hasn't been merged when you're running Track A standalone.
- This module tries the real shared schema first. If it can't be
  imported, it falls back to a LOCAL definition that mirrors, field for
  field, the contract documented in:
      Track_A_Attack_Taxonomy_Variants_Success_Criteria_AttackEvent_Mapping.md
      section 16 "AttackEvent Mapping"

Once `shared/schemas/attack_event.py` is committed and importable, no
other Track A file needs to change - only this shim's import path
starts resolving to the real thing. This is the only file that should
ever need editing if/when the shared schema changes shape.
"""

from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Make sure the repo root is importable regardless of the working
# directory the script is launched from, so `shared.schemas...` can be
# found once it exists.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

USING_SHARED_SCHEMA = False

try:
    from shared.schemas.attack_event import AttackEvent  # type: ignore
    from shared.schemas.verdict import Verdict  # type: ignore

    USING_SHARED_SCHEMA = True

except Exception:
    try:
        from pydantic import BaseModel, Field
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "pydantic is required for the local AttackEvent fallback. "
            "Install with: pip install pydantic"
        ) from exc

    class ToolCallRecord(BaseModel):
        tool_name: str
        arguments: Dict[str, Any] = Field(default_factory=dict)

    class AttackEvent(BaseModel):  # type: ignore[no-redef]
        """Local fallback - mirrors shared/schemas/attack_event.py (§16)."""

        event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
        timestamp: str = Field(
            default_factory=lambda: datetime.now(timezone.utc).isoformat()
        )
        track: str = "track_a_agentic"
        user_instruction: str
        untrusted_input: str
        agent_reasoning_trace: str
        tool_calls_made: List[ToolCallRecord] = Field(default_factory=list)
        audio_file_path: Optional[str] = None
        transaction_fields: Dict[str, Any] = Field(default_factory=dict)
        campaign_id: str
        round_number: int = 1
        attack_variant_id: str
        attack_succeeded_against_agent: bool

    class Verdict(BaseModel):  # type: ignore[no-redef]
        """Local fallback - mirrors shared/schemas/verdict.py (Blue Team output)."""

        event_id: str
        decision: str = "unknown"
        risk_score: Optional[float] = None
        rationale: Optional[str] = None


def new_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Uniform tool-call record shape, independent of which AttackEvent impl is active."""
    return {"tool_name": tool_name, "arguments": arguments}


def event_to_dict(event: Any) -> Dict[str, Any]:
    """Serialize an AttackEvent (shared pydantic v1/v2, or local fallback) to a plain dict."""
    if hasattr(event, "model_dump"):
        return event.model_dump()
    if hasattr(event, "dict"):
        return event.dict()
    return dict(event)
