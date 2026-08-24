from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class LayerScore(BaseModel):
    layer_name: Literal[
        "layer1_fast_filters",
        "layer2_injection_classifier",
        "layer3_alignment_check",
        "layer4_transaction_risk",
        "layer5_deepfake_detector",
    ]
    score: float                 
    flagged: bool
    reason: Optional[str] = None  


class Verdict(BaseModel):
    event_id: str                      
    timestamp: datetime

    layer_scores: list[LayerScore]    

    fusion_score: float               
    decision: Literal["approve", "step_up", "decline", "review"]
    attack_caught: bool

    explanation: str              
    latency_ms: float                 