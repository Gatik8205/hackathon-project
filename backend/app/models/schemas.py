"""
Pydantic request/response models for RakshakAI backend.
Place this file at: app/models/schemas.py
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


# ---------- CHATBOT (Citizen Fraud Shield) ----------

class ChatbotAssessRequest(BaseModel):
    message: str = Field(..., description="Description of the call/message/situation from the citizen")
    channel: Optional[str] = Field(default="web", description="whatsapp | ivr | app | web")
    language: Optional[str] = Field(default="en")
    phone_number: Optional[str] = Field(default=None, description="Phone number involved, if known — used to link this report into the fraud network graph")


class ChatbotAssessResponse(BaseModel):
    verdict: Literal["likely_scam", "possibly_scam", "likely_safe"]
    confidence: float = Field(..., ge=0, le=1)
    red_flags: List[str]
    advice: str
    recommended_action: str  # e.g. "Do not share OTP. Report to cybercrime.gov.in"


# ---------- SCAM (Digital Arrest Scam Detection) ----------

class ScamSessionRequest(BaseModel):
    transcript: str = Field(..., description="Call/session transcript or description of the interaction")
    caller_number: Optional[str] = None
    claimed_identity: Optional[str] = Field(default=None, description="e.g. 'CBI officer', 'Customs'")
    video_call: Optional[bool] = False


class ScamSessionResponse(BaseModel):
    is_scam_session: bool
    confidence: float = Field(..., ge=0, le=1)
    scam_type: Optional[str] = None  # e.g. "digital_arrest", "otp_fraud", "investment_scam"
    matched_patterns: List[str]
    alert_priority: Literal["low", "medium", "high", "critical"]


# ---------- CURRENCY (Counterfeit Detection) ----------

class CurrencyVerifyResponse(BaseModel):
    denomination: Optional[str] = None
    is_likely_genuine: bool
    confidence: float = Field(..., ge=0, le=1)
    checks_performed: List[str]
    flagged_issues: List[str]


# ---------- GRAPH (Fraud Network Intelligence) ----------

class FraudReportIngest(BaseModel):
    report_id: str
    phone_number: Optional[str] = None
    device_id: Optional[str] = None
    bank_account: Optional[str] = None
    upi_id: Optional[str] = None
    amount_lost: Optional[float] = None
    complaint_text: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None


class GraphNode(BaseModel):
    id: str
    type: str  # "phone" | "device" | "account" | "upi" | "report"
    label: str


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str


class FraudNetworkResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    clusters_detected: int
    high_risk_clusters: List[List[str]]  # list of report_ids grouped per suspected ring