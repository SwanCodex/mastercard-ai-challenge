from orchestrator.defense_interface import DefensePipeline
from orchestrator.event_log.store import EventStore
from shared.schemas.attack_event import AttackEvent
from shared.schemas.verdict import Verdict


class CampaignManager:
    """Coordinates attack events, defense evaluation, and verdict logging."""

    def __init__(
        self,
        defense_pipeline: DefensePipeline,
        event_store: EventStore | None = None,
    ):
        self.defense_pipeline = defense_pipeline
        self.event_store = event_store or EventStore()

    def process_attack(self, attack_event: AttackEvent) -> Verdict:
        """Run one attack event through the defense pipeline."""

        self.event_store.append_attack_event(attack_event)

        verdict = self.defense_pipeline.evaluate(attack_event)

        if verdict.event_id != attack_event.event_id:
            raise ValueError(
                "Defense pipeline returned a verdict for a different event."
            )

        self.event_store.append_verdict(verdict)

        return verdict

    def run_campaign(
        self,
        attack_events: list[AttackEvent],
    ) -> list[Verdict]:
        """Run all attack events in a campaign."""

        return [
            self.process_attack(attack_event)
            for attack_event in attack_events
        ]