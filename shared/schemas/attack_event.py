from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class ToolCall(BaseModel):
    tool_name: str 
    arguments: dict  


class AttackEvent(BaseModel):
    event_id: str                    
    timestamp: datetime
    track: Literal["track_a_agentic", "track_b_deepfake", "track_c_synthetic_id"]

    user_instruction: str
    untrusted_input: Optional[str] = None
    agent_reasoning_trace: Optional[str] = None
    tool_calls_made: list[ToolCall] = Field(default_factory=list)
    audio_file_path: Optional[str] = None
    transaction_fields: Optional[dict] = None
    campaign_id: str
    round_number: int
    attack_variant_id: str          
    attack_succeeded_against_agent: bool