from fastapi import APIRouter
from app.api.v1.endpoints import synapse, whatsapp

api_router = APIRouter()

api_router.include_router(synapse.router, prefix="/synapse", tags=["synapse"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])
# api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
