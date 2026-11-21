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
    status: Optional[str] = Field("OK", description="Execution status: OK, PARTIAL, OCR_FAILED, NO_INPUT")
    risk_score: Optional[int] = Field(0, description="Calibrated risk percentage (0 to 100)")
    status_color: str = Field("gray", description="UI theme color: green, amber, red, or gray")
    icon: str = Field("❓", description="Status emoji icon: ✅, ⚠️, 🚨, or ❓")
    user_message: Optional[str] = Field(None, description="Direct plain-language summary for the user")
    reasons: List[str] = Field(default_factory=list, description="Plain-language explanations of why the input is risky")
    safety_tips: List[str] = Field(default_factory=list, description="Actionable recommendations for the user")
    signals: List[Dict[str, Any]] = Field(default_factory=list, description="Structured triggered signals")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed sub-scores and debug indicators")


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: bool
