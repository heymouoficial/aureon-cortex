"""
Aureon Cortex - Polímata Enrutador
El sistema de orquestación multi-agente de ElevatOS.
Con auto-recuperación: si Vox falla, Lumina toma el control.
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
    - Lumina: Estrategia e Insights (Mistral - Alta Cuota)
    - Nux: Prospección y Ventas
    - Memorís: RAG y Conocimiento
    - Vox: Comunicación con el Usuario (Gemini 2.0 Flash)
    
    Protocolo de Emergencia: Si Vox (2.0) falla por 429,
    Lumina (1.5/Mistral) toma el control automáticamente.
    """
    
    INTENT_KEYWORDS = {
        "lumina": ["estrategia", "analiza", "plan", "riesgo", "evalúa", "piensa", "insight", "roi"],
        "nux": ["vende", "prospecta", "lead", "cliente", "contacta", "seguimiento", "outreach", "cierra"],
        "memoris": ["recuerda", "busca", "encuentra", "qué dijimos", "historial", "contexto", "conocimiento"],
        "scheduler": ["reunión", "calendario", "agenda", "cita", "programe", "agendar", "clase"],
    }

    def __init__(self):
        from app.agentes.scheduler import Scheduler
        self.lumina = Lumina()
        self.nux = Nux()
        self.memoris = Memoris()
        self.scheduler = Scheduler()
        self.vox = Vox()
        logger.info("🧠 Aureon Cortex inicializado | Lumina ✨ | Nux ⚡ | Memorís 📚 | Scheduler 📅 | Vox 🎙️")

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
        """
        Main routing method - the heart of Aureon Cortex.
        Con auto-recuperación: si Vox falla, Lumina entra al rescate.
        """
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
                case "scheduler":
                    return await self.scheduler.act(query, context)
                case _:
                    # Vox es el default, pero tiene fallback a Lumina
                    return await self._vox_with_fallback(query, context, attachments)
                    
        except Exception as e:
            error_str = str(e)
            logger.error(f"❌ Cortex error en {decision.agent}: {e}")
            
            # Si cualquier agente falla, intentar con Lumina
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                logger.warning("🚨 Activando protocolo de emergencia: LUMINA")
                try:
                    return await self.lumina.think(query, context)
                except Exception as lumina_error:
                    logger.error(f"❌ Lumina también falló: {lumina_error}")
            
            return "🔧 Mis sistemas principales están en mantenimiento preventivo. Dame 30 segundos para recalibrar."

    async def _vox_with_fallback(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Vox con auto-recuperación: si falla por 429, Lumina toma el control.
        El usuario no debe notar el fallo.
        """
        try:
            logger.info("🎙️ Intentando con VOX (Gemini 2.0)...")
            return await self.vox.respond(query, context, attachments)
            
        except Exception as e:
            error_str = str(e)
            
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                logger.warning("🚨 VOX agotado (429). Activando LUMINA (1.5/Mistral)...")
                try:
                    # Lumina responde en lugar de Vox - el usuario no nota la diferencia
                    return await self.lumina.think(query, context)
                except Exception as lumina_error:
                    logger.error(f"❌ Lumina también agotada: {lumina_error}")
                    return "🚀 ¡Demasiada energía! Mis llaves de IA necesitan un respiro. Reintenta en 30s."
            
            logger.error(f"❌ VOX fallo no-429: {e}")
            return "🎙️ Estoy recalibrando mi voz. ¿Podrías repetir en un momento?"


# Singleton
aureon_cortex = AureonCortex()
