from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SecurityDecision(BaseModel):
    """Final enforcement decision produced after security analysis."""

    event_id: str
    timestamp: datetime

    action: Literal["allow", "review", "block"]

    confidence: float = Field(ge=0.0, le=1.0)

    reason: str

    evidence: list[str] = Field(default_factory=list)

    requires_human_review: bool = False

    source_verdict_decision: Literal[
        "approve",
        "step_up",
        "decline",
        "review",
    ]

    fusion_score: float = Field(ge=0.0, le=1.0)
