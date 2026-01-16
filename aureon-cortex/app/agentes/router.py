"""
Aureon Cortex - Polímata Enrutador
El sistema de orquestación multi-agente de ElevatOS.
"""
from typing import Dict, Any, List, Optional
from loguru import logger
from pydantic import BaseModel, Field

from app.agentes.lumina import Lumina
from app.agentes.nux import Nux
from app.agentes.memoris import Memoris
from app.agentes.vox import Vox
from app.core.config import get_settings

settings = get_settings()


class RoutingDecision(BaseModel):
    """Structured routing decision."""
    agent: str = Field(description="Target agent: lumina, nux, memoris, vox")
    confidence: float = Field(default=0.8)
    reasoning: str = Field(default="")


class AureonCortex:
    """
    🧠 Aureon Cortex - El Polímata Enrutador
    
    La mano derecha del Humano. Recibe consultas y las dirige
    al agente especializado más apropiado.
    
    Agentes:
    - Lumina: Estrategia e Insights
    - Nux: Prospección y Ventas
    - Memorís: RAG y Conocimiento
    - Vox: Comunicación con el Usuario
    """
    
    INTENT_KEYWORDS = {
        "lumina": ["estrategia", "analiza", "plan", "riesgo", "evalúa", "piensa", "insight", "roi"],
        "nux": ["vende", "prospecta", "lead", "cliente", "contacta", "seguimiento", "outreach", "cierra"],
        "memoris": ["recuerda", "busca", "encuentra", "qué dijimos", "historial", "contexto", "conocimiento"],
    }

    def __init__(self):
        self.lumina = Lumina()
        self.nux = Nux()
        self.memoris = Memoris()
        self.vox = Vox()
        logger.info("🧠 Aureon Cortex inicializado | Lumina ✨ | Nux ⚡ | Memorís 📚 | Vox 🎙️")

    def classify_intent(self, query: str) -> RoutingDecision:
        """Classify and route to the appropriate agent."""
        query_lower = query.lower()
        
        for agent, keywords in self.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in query_lower:
                    logger.info(f"🎯 Enrutando a: {agent.upper()} (keyword: {kw})")
                    return RoutingDecision(agent=agent, confidence=0.9, reasoning=f"Keyword: '{kw}'")
        
        # Default: Vox handles general conversation
        return RoutingDecision(agent="vox", confidence=0.7, reasoning="Conversación general")

    async def route(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Main routing method - the heart of Aureon Cortex."""
        decision = self.classify_intent(query)
        logger.info(f"🔀 Cortex → {decision.agent.upper()} | Confianza: {decision.confidence}")
        
        try:
            match decision.agent:
                case "lumina":
                    return await self.lumina.think(query, context)
                case "nux":
                    return await self.nux.act(query, context)
                case "memoris":
                    return await self.memoris.recall(query, context)
                case _:
                    return await self.vox.respond(query, context, attachments)
        except Exception as e:
            logger.error(f"❌ Cortex error en {decision.agent}: {e}")
            return await self.vox.respond(f"[Fallback] {query}", context, attachments)


# Singleton
aureon_cortex = AureonCortex()
