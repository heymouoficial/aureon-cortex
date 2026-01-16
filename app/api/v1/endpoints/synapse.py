from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from loguru import logger
from app.services.agent_pydantic import pydantic_brain, AureonDependencies

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
    
    Processes the request through the Aureon Brain service (Agnostic/Multi-model).
    """
    logger.info(f"SYNAPSE: Stimulus received: {request.message[:50]}...")
    
    # dependencies
    deps = AureonDependencies(
        organization_id=request.context.get("organizationId") if request.context else None
    )

    # Process through Brain service
    answer = await pydantic_brain.process_query(
        request.message,
        dependencies=deps,
        attachments=None # Synapse currently text only via this endpoint
    )
    
    thought_trace = [
        "Estímulo recibido y decodificado",
        "Procesamiento Agnóstico (Gemini/Mistral/Groq) completado",
        "Respuesta sintetizada para el aliado comercial"
    ]
    
    return SynapseResponse(
        answer=answer,
        thought_trace=thought_trace,
        actions=[]
    )
