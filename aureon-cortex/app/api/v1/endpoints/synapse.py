from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from loguru import logger
from app.services.brain import brain_service

router = APIRouter()

class SynapseRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class SynapseResponse(BaseModel):
    answer: str
    thought_trace: List[str]
    actions: List[Dict[str, Any]]

@router.post("/process", response_model=SynapseResponse)
async def process_synapse(request: SynapseRequest):
    """
    🧠 Neuro-Link Endpoint
    
    Processes the request through the Aureon Brain service.
    """
    logger.info(f"SYNAPSE: Stimulus received: {request.message[:50]}...")
    
    # Process through Brain service
    answer = await brain_service.process_query(
        request.message,
        organization_id=request.context.get("organizationId") if request.context else None,
        context=request.context
    )
    
    thought_trace = [
        "Estímulo recibido y decodificado",
        "Consulta a memoria de largo plazo (RAG) completada",
        "Pensamiento sintetizado para el aliado comercial"
    ]
    
    return SynapseResponse(
        answer=answer,
        thought_trace=thought_trace,
        actions=[]
    )
