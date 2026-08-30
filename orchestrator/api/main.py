from fastapi import FastAPI

from orchestrator.real_defense_pipeline import RealDefensePipeline
from orchestrator.campaign_manager import CampaignManager
from shared.schemas.attack_event import AttackEvent
from shared.schemas.verdict import Verdict


app = FastAPI(
    title="SENTINEL Orchestrator",
    description="Adversarial payment-security orchestration API",
    version="0.1.0",
)


campaign_manager = CampaignManager(
    defense_pipeline=RealDefensePipeline()
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