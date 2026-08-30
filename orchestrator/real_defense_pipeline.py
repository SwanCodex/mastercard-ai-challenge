from shared.schemas.attack_event import AttackEvent
from shared.schemas.verdict import Verdict

from blue_team.fusion.risk_fusion import run_pipeline

from orchestrator.defense_interface import DefensePipeline


class RealDefensePipeline(DefensePipeline):
    """Adapter between the orchestrator and the Blue Team fusion pipeline."""

    def evaluate(self, event: AttackEvent) -> Verdict:
        return run_pipeline(event)