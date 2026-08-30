from shared.schemas.security_decision import SecurityDecision
from shared.schemas.attack_event import AttackEvent
from shared.schemas.verdict import Verdict

from orchestrator.adaptive_learning import AdaptiveThreatLearner
from orchestrator.defense_interface import DefensePipeline
from orchestrator.enforcement_policy import EnforcementPolicy
from orchestrator.event_log.store import EventStore
from orchestrator.security_agent import SecurityAgent


class CampaignManager:
    """Coordinates attacks, defense, investigation, enforcement, and learning."""

    def __init__(
        self,
        defense_pipeline: DefensePipeline,
        event_store: EventStore | None = None,
        security_agent: SecurityAgent | None = None,
        enforcement_policy: EnforcementPolicy | None = None,
        threat_learner: AdaptiveThreatLearner | None = None,
    ):
        self.defense_pipeline = defense_pipeline
        self.event_store = event_store or EventStore()
        self.security_agent = security_agent or SecurityAgent()
        self.enforcement_policy = enforcement_policy or EnforcementPolicy()
        self.threat_learner = threat_learner or AdaptiveThreatLearner()

        self.last_security_decision: SecurityDecision | None = None
        self.last_learning_result: dict | None = None

    def process_attack(self, attack_event: AttackEvent) -> Verdict:
        """Evaluate, investigate, and enforce one attack event."""

        self.event_store.append_attack_event(attack_event)

        verdict = self.defense_pipeline.evaluate(attack_event)

        if verdict.event_id != attack_event.event_id:
            raise ValueError(
                "Defense pipeline returned a verdict for a different event."
            )

        self.event_store.append_verdict(verdict)

        security_decision = self.security_agent.investigate(
            attack_event,
            verdict,
        )

        security_decision = self.enforcement_policy.apply(
            verdict,
            security_decision,
        )

        self.last_security_decision = security_decision
        self.event_store.append_security_decision(security_decision)

        return verdict

    def run_campaign_from_file(
        self,
        event_log_path: str,
    ) -> list[Verdict]:
        """Load Red Team AttackEvents and evaluate the campaign."""

        from orchestrator.red_team_adapter import load_attack_events

        attack_events = load_attack_events(event_log_path)

        return self.run_campaign(attack_events)

    def run_campaign(
        self,
        attack_events: list[AttackEvent],
    ) -> list[Verdict]:
        """Run a campaign and update adaptive threat knowledge."""

        verdicts = [
            self.process_attack(attack_event)
            for attack_event in attack_events
        ]

        self.last_learning_result = self.threat_learner.learn(
            attack_events,
            verdicts,
        )

        return verdicts
