from fastapi import FastAPI, HTTPException


from orchestrator.real_defense_pipeline import RealDefensePipeline
from orchestrator.campaign_manager import CampaignManager
from shared.schemas.attack_event import AttackEvent
from shared.schemas.verdict import Verdict
from orchestrator.metrics.compute_metrics import compute_metrics


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

@app.get("/get_verdict/{event_id}", response_model=Verdict)
def get_verdict(event_id: str):
    verdicts = campaign_manager.event_store.get_verdicts()

    for verdict in reversed(verdicts):
        if verdict.event_id == event_id:
            return verdict

    raise HTTPException(
        status_code=404,
        detail=f"Verdict not found for event_id: {event_id}",
    )

@app.get("/get_metrics/{campaign_id}")
def get_metrics(campaign_id: str):
    records = campaign_manager.event_store.get_campaign_records(campaign_id)

    metrics = compute_metrics(
        records["attack_events"],
        records["verdicts"],
    )

    return metrics

@app.post("/run_campaign", response_model=list[Verdict])
def run_campaign(events: list[AttackEvent]):
    return campaign_manager.run_campaign(events)