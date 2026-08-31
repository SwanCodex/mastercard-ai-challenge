from datetime import datetime, timezone

from blue_team.fusion import risk_fusion
from shared.schemas.attack_event import AttackEvent


def make_transaction_event() -> AttackEvent:
    return AttackEvent(
        event_id="fusion-layer4-missing-001",
        timestamp=datetime.now(timezone.utc),
        track="track_c_synthetic_id",
        user_instruction="Process this transaction.",
        transaction_fields={
            "TransactionAmt": 100.0,
            "card1": 12345,
            "card4": "visa",
            "card6": "credit",
            "ProductCD": "W",
            "C1": 1.0,
            "C2": 1.0,
        },
        campaign_id="fusion-test",
        round_number=1,
        attack_variant_id="layer4-missing",
        attack_succeeded_against_agent=False,
    )


def test_missing_layer4_does_not_crash(monkeypatch):
    event = make_transaction_event()

    def failing_layer4(_event):
        raise RuntimeError("checkpoint unavailable")

    monkeypatch.setattr(
        risk_fusion,
        "layer4_score",
        failing_layer4,
    )

    verdict = risk_fusion.run_pipeline(event)

    assert verdict.event_id == event.event_id
    assert verdict.decision in {
        "approve",
        "step_up",
        "review",
        "decline",
    }

    layer_names = {
        layer.layer_name
        for layer in verdict.layer_scores
    }

    assert "layer4_transaction_risk" not in layer_names