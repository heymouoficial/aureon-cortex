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
                    return await self._universal_fallback(query, context, attachments)
                    
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

    async def _universal_fallback(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        🛡️ Protocolo Universal de Resiliencia
        Cadena de mando: Vox (Gemini) -> Lumina (Mistral) -> Nux (Groq) -> DeepSeek/OpenAI
        """
        # 1. Intentar con Vox (Gemini 2.0 / 1.5)
        try:
            logger.info("🎙️ Aureon: Intentando Vox (Gemini)...")
            return await self.vox.respond(query, context, attachments)
        except Exception as e:
            logger.warning(f"⚠️ Vox falló: {e}. Activando Lumina...")

        # 2. Fallback a Lumina (Mistral Large) via Mistral API
        try:
            logger.info("✨ Aureon: Vox caído. Lumina tomando el control (Mistral)...")
            return await self.lumina.think(query, context)
        except Exception as e:
            logger.warning(f"⚠️ Lumina falló: {e}. Activando Nux...")

        # 3. Fallback a Nux (Groq LLaMA 3)
        try:
            logger.info("⚡ Aureon: Lumina caída. Nux tomando el control (Groq)...")
            # Force Nux to act as chat executioner
            nux_response = await self.nux.act(query, context)
            return f"⚡ [Respaldo Nux] {nux_response}"
        except Exception as e:
            logger.warning(f"⚠️ Nux falló: {e}. Activando Núcleo de Último Recurso...")

        # 4. Último Recurso: DeepSeek / OpenAI (Direct API)
        try:
            import httpx
            logger.info("🥥 Aureon: Activando DeepSeek/OpenAI...")
            api_key = settings.DEEPSEEK_API_KEY or settings.OPENAI_API_KEY
            if not api_key:
                raise ValueError("No DeepSeek/OpenAI key available")
            
            base_url = "https://api.deepseek.com/v1/chat/completions" if settings.DEEPSEEK_API_KEY else "https://api.openai.com/v1/chat/completions"
            model = "deepseek-chat" if settings.DEEPSEEK_API_KEY else "gpt-3.5-turbo"
            
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    base_url,
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": query}]
                    },
                    timeout=10.0
                )
                resp.raise_for_status()
                return f"🥥 [Respaldo DeepSeek] {resp.json()['choices'][0]['message']['content']}"
        except Exception as e:
            logger.error(f"❌ FALLO TOTAL DEL SISTEMA: {e}")
            return "🔥 Error Crítico: Todos los núcleos de IA están fuera de línea. Por favor contacta a soporte."


# Singleton
aureon_cortex = AureonCortex()
