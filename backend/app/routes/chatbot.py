"""
app/routes/chatbot.py
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatbotAssessRequest, ChatbotAssessResponse
from app.services import chatbot_service

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post("/assess", response_model=ChatbotAssessResponse)
def assess(request: ChatbotAssessRequest):
    try:
        return chatbot_service.assess_message(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))