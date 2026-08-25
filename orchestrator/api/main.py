from fastapi import FastAPI

from orchestrator.campaign_manager import CampaignManager
from shared.schemas.attack_event import AttackEvent
from shared.schemas.verdict import Verdict


app = FastAPI(
    title="SENTINEL Orchestrator",
    description="Adversarial payment-security orchestration API",
    version="0.1.0",
)


def mock_defense(event: AttackEvent) -> Verdict:
    """Temporary defense adapter for orchestrator integration testing."""

    return Verdict(
        event_id=event.event_id,
        timestamp=event.timestamp,
        layer_scores=[],
        fusion_score=0.95 if event.attack_succeeded_against_agent else 0.05,
        decision="decline" if event.attack_succeeded_against_agent else "approve",
        attack_caught=event.attack_succeeded_against_agent,
        explanation="Temporary mock defense used for orchestrator integration testing.",
        latency_ms=1.0,
    )


campaign_manager = CampaignManager(
    defense_pipeline=mock_defense
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "sentinel-orchestrator",
    }


@app.post("/run_campaign", response_model=list[Verdict])
def run_campaign(events: list[AttackEvent]):
    return campaign_manager.run_campaign(events)