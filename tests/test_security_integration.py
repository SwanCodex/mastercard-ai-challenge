from datetime import datetime, timezone

from orchestrator.campaign_manager import CampaignManager
from orchestrator.defense_interface import DefensePipeline
from orchestrator.event_log.store import EventStore
from orchestrator.enforcement_policy import EnforcementPolicy
from orchestrator.security_agent import SecurityAgent

from shared.schemas.attack_event import AttackEvent
from shared.schemas.security_decision import SecurityDecision
from shared.schemas.verdict import Verdict


class FakeDefense(DefensePipeline):
    def __init__(self, decision="approve", score=0.1):
        self.decision = decision
        self.score = score

    def evaluate(self, event):
        return Verdict(
            event_id=event.event_id,
            timestamp=datetime.now(timezone.utc),
            layer_scores=[],
            fusion_score=self.score,
            decision=self.decision,
            attack_caught=self.decision != "approve",
            explanation="Test verdict",
            latency_ms=5.0,
        )


class FakeSecurityAgent:
    def __init__(self, action):
        self.action = action

    def investigate(self, event, verdict):
        return SecurityDecision(
            event_id=event.event_id,
            timestamp=verdict.timestamp,
            action=self.action,
            confidence=0.95,
            reason="Test agent recommendation",
            evidence=["Test evidence"],
            requires_human_review=self.action == "review",
            source_verdict_decision=verdict.decision,
            fusion_score=verdict.fusion_score,
        )


def make_event():
    return AttackEvent(
        event_id="integration-001",
        timestamp=datetime.now(timezone.utc),
        track="track_a_agentic",
        user_instruction="Buy the requested item.",
        campaign_id="integration-test",
        round_number=1,
        attack_variant_id="test-001",
        attack_succeeded_against_agent=False,
    )


def test_agent_can_escalate_an_approve_verdict_to_review(tmp_path):
    manager = CampaignManager(
        FakeDefense("approve", 0.1),
        EventStore(tmp_path / "events.jsonl"),
        security_agent=FakeSecurityAgent("review"),
        enforcement_policy=EnforcementPolicy(),
    )

    verdict = manager.process_attack(make_event())

    assert verdict.decision == "approve"
    assert manager.last_security_decision.action == "review"
    assert manager.last_security_decision.requires_human_review is True


def test_agent_can_escalate_an_approve_verdict_to_block(tmp_path):
    manager = CampaignManager(
        FakeDefense("approve", 0.1),
        EventStore(tmp_path / "events.jsonl"),
        security_agent=FakeSecurityAgent("block"),
        enforcement_policy=EnforcementPolicy(),
    )

    manager.process_attack(make_event())

    assert manager.last_security_decision.action == "block"


def test_agent_cannot_downgrade_deterministic_block(tmp_path):
    manager = CampaignManager(
        FakeDefense("decline", 0.9),
        EventStore(tmp_path / "events.jsonl"),
        security_agent=FakeSecurityAgent("allow"),
        enforcement_policy=EnforcementPolicy(),
    )

    manager.process_attack(make_event())

    assert manager.last_security_decision.action == "block"


def test_security_decision_is_logged(tmp_path):
    store = EventStore(tmp_path / "events.jsonl")

    manager = CampaignManager(
        FakeDefense("review", 0.6),
        store,
        security_agent=FakeSecurityAgent("review"),
        enforcement_policy=EnforcementPolicy(),
    )

    manager.process_attack(make_event())

    decisions = store.get_security_decisions()

    assert len(decisions) == 1
    assert decisions[0].event_id == "integration-001"
    assert decisions[0].action == "review"
