from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from shared.schemas.security_decision import SecurityDecision


def make_decision(**overrides):
    data = {
        "event_id": "test-event-001",
        "timestamp": datetime.now(timezone.utc),
        "action": "block",
        "confidence": 0.95,
        "reason": "High-risk transaction detected.",
        "evidence": [
            "Layer 2 flagged prompt injection.",
            "Fusion risk exceeded the blocking threshold.",
        ],
        "requires_human_review": False,
        "source_verdict_decision": "decline",
        "fusion_score": 0.92,
    }

    data.update(overrides)
    return SecurityDecision(**data)


def test_security_decision_accepts_valid_block():
    decision = make_decision()

    assert decision.action == "block"
    assert decision.confidence == 0.95
    assert decision.fusion_score == 0.92
    assert decision.requires_human_review is False


def test_security_decision_accepts_review():
    decision = make_decision(
        action="review",
        confidence=0.75,
        requires_human_review=True,
        source_verdict_decision="review",
    )

    assert decision.action == "review"
    assert decision.requires_human_review is True


def test_security_decision_accepts_allow():
    decision = make_decision(
        action="allow",
        confidence=0.99,
        source_verdict_decision="approve",
        fusion_score=0.01,
    )

    assert decision.action == "allow"


@pytest.mark.parametrize("field,value", [
    ("confidence", -0.1),
    ("confidence", 1.1),
    ("fusion_score", -0.1),
    ("fusion_score", 1.1),
])
def test_scores_must_be_between_zero_and_one(field, value):
    with pytest.raises(ValidationError):
        make_decision(**{field: value})


def test_invalid_action_is_rejected():
    with pytest.raises(ValidationError):
        make_decision(action="maybe")


def test_invalid_source_verdict_decision_is_rejected():
    with pytest.raises(ValidationError):
        make_decision(source_verdict_decision="block")