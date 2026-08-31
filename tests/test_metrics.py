from datetime import datetime, timezone

from orchestrator.metrics.compute_metrics import compute_metrics
from shared.schemas.attack_event import AttackEvent
from shared.schemas.verdict import Verdict


def make_event(event_id: str, attack: bool) -> AttackEvent:
    return AttackEvent(
        event_id=event_id,
        timestamp=datetime.now(timezone.utc),
        track="track_a_agentic",
        user_instruction="Test instruction",
        campaign_id="metrics-test",
        round_number=1,
        attack_variant_id=event_id,
        attack_succeeded_against_agent=attack,
    )


def make_verdict(event_id: str, caught: bool) -> Verdict:
    return Verdict(
        event_id=event_id,
        timestamp=datetime.now(timezone.utc),
        layer_scores=[],
        fusion_score=0.9 if caught else 0.1,
        decision="decline" if caught else "approve",
        attack_caught=caught,
        explanation="Test verdict",
        latency_ms=100.0,
    )


def test_compute_metrics():
    events = [
        make_event("attack-caught", True),
        make_event("attack-missed", True),
        make_event("benign-approved", False),
        make_event("benign-false-positive", False),
    ]

    verdicts = [
        make_verdict("attack-caught", True),
        make_verdict("attack-missed", False),
        make_verdict("benign-approved", False),
        make_verdict("benign-false-positive", True),
    ]

    metrics = compute_metrics(events, verdicts)

    assert metrics.total_events == 4
    assert metrics.attacks == 2
    assert metrics.benign_events == 2

    assert metrics.caught_attacks == 1
    assert metrics.missed_attacks == 1

    assert metrics.false_positives == 1
    assert metrics.true_negatives == 1

    assert metrics.attack_catch_rate == 0.5
    assert metrics.precision == 0.5
    assert metrics.recall == 0.5
    assert metrics.false_positive_rate == 0.5

    assert metrics.average_latency_ms == 100.0