"""
app/routes/scam.py
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import ScamSessionRequest, ScamSessionResponse
from app.services import scam_service

router = APIRouter(prefix="/scam", tags=["scam"])


@router.post("/detect", response_model=ScamSessionResponse)
def detect(request: ScamSessionRequest):
    try:
        return scam_service.classify_session(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))