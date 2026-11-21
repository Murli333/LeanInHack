"""
Pydantic Schemas for ScamLens Backend API
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    message_text: Optional[str] = Field(None, description="Suspicious SMS or WhatsApp message text")
    url: Optional[str] = Field(None, description="Suspicious URL to analyze")
    audio_transcript: Optional[str] = Field(None, description="Transcript of suspicious audio recording")


class AnalyzeResponse(BaseModel):
    verdict: str = Field(..., description="Verdict: Safe, Suspicious, Scam, or Unknown")
    risk_score: int = Field(..., description="Calibrated risk percentage (0 to 100)")
    status_color: str = Field(..., description="UI theme color: green, amber, red, or gray")
    icon: str = Field(..., description="Status emoji icon: ✅, ⚠️, 🚨, or ❓")
    reasons: List[str] = Field(..., description="Plain-language explanations of why the input is risky")
    safety_tips: List[str] = Field(..., description="Actionable recommendations for the user")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed sub-scores and debug indicators")


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: bool
