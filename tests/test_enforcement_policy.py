from datetime import datetime, timezone

import pytest

from orchestrator.enforcement_policy import EnforcementPolicy
from shared.schemas.verdict import LayerScore, Verdict


def make_verdict(decision: str, fusion_score: float) -> Verdict:
    return Verdict(
        event_id=f"policy-{decision}",
        timestamp=datetime.now(timezone.utc),
        layer_scores=[
            LayerScore(
                layer_name="layer2_injection_classifier",
                score=fusion_score,
                flagged=decision != "approve",
                reason="Test security signal.",
            )
        ],
        fusion_score=fusion_score,
        decision=decision,
        attack_caught=decision != "approve",
        explanation="Test verdict.",
        latency_ms=10.0,
    )


@pytest.mark.parametrize(
    "verdict_decision,expected_action",
    [
        ("approve", "allow"),
        ("step_up", "review"),
        ("review", "review"),
        ("decline", "block"),
    ],
)
def test_verdict_maps_to_enforcement_action(
    verdict_decision,
    expected_action,
):
    policy = EnforcementPolicy()

    verdict = make_verdict(
        verdict_decision,
        {
            "approve": 0.10,
            "step_up": 0.35,
            "review": 0.60,
            "decline": 0.90,
        }[verdict_decision],
    )

    decision = policy.evaluate(verdict)

    assert decision.action == expected_action
    assert decision.event_id == verdict.event_id
    assert decision.source_verdict_decision == verdict.decision


def test_decline_is_blocked():
    policy = EnforcementPolicy()

    verdict = make_verdict("decline", 0.90)
    decision = policy.evaluate(verdict)

    assert decision.action == "block"
    assert decision.requires_human_review is False
    assert decision.confidence >= 0.90


def test_review_requires_human_review():
    policy = EnforcementPolicy()

    verdict = make_verdict("review", 0.60)
    decision = policy.evaluate(verdict)

    assert decision.action == "review"
    assert decision.requires_human_review is True


def test_step_up_becomes_review():
    policy = EnforcementPolicy()

    verdict = make_verdict("step_up", 0.35)
    decision = policy.evaluate(verdict)

    assert decision.action == "review"
    assert decision.requires_human_review is True


def test_approve_allows_action():
    policy = EnforcementPolicy()

    verdict = make_verdict("approve", 0.05)
    decision = policy.evaluate(verdict)

    assert decision.action == "allow"
    assert decision.requires_human_review is False


def test_flagged_layer_is_preserved_as_evidence():
    policy = EnforcementPolicy()

    verdict = make_verdict("review", 0.60)
    decision = policy.evaluate(verdict)

    assert len(decision.evidence) == 1
    assert "layer2_injection_classifier" in decision.evidence[0]
