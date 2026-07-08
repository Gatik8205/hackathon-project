"""
app/routes/currency.py
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import CurrencyVerifyResponse
from app.services import currency_service

router = APIRouter(prefix="/currency", tags=["currency"])


@router.post("/verify", response_model=CurrencyVerifyResponse)
async def verify(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        return currency_service.verify_note(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))