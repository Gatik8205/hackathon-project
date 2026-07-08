"""
app/routes/graph.py
"""

from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import FraudReportIngest, FraudNetworkResponse
from app.services import graph_service

router = APIRouter(prefix="/graph", tags=["graph"])


@router.post("/ingest")
def ingest(reports: List[FraudReportIngest]):
    try:
        graph_service.ingest_batch(reports)
        return {"status": "ok", "ingested": len(reports)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network", response_model=FraudNetworkResponse)
def network():
    try:
        return graph_service.get_network()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
def reset():
    graph_service.reset_graph()
    return {"status": "reset"}