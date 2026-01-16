"""
Vox - La Voz de Aureon (Comunicación)
Model: Gemini 2.0 Flash (with fallback to 1.5-flash)
"""
import os
from typing import Dict, Any, Optional, List
from loguru import logger
from pydantic_ai import Agent
from app.core.config import get_settings
from app.utils.hydra import hydra_pool
from app.agentes.memoris import Memoris
from app.agentes.lumina import Lumina
from app.agentes.scheduler import Scheduler
from pydantic_ai import RunContext

settings = get_settings()

# List of models to try in order (fallback chain)
MODEL_CHAIN = [
    "google-gla:gemini-2.0-flash",
    "google-gla:gemini-1.5-flash",
    "google-gla:gemini-1.5-flash-8b",
]


class Vox:
    """
    🎙️ Vox - La Voz de Aureon.
    Sintetiza información y comunica con el usuario final.
    With fallback models for resilience.
    """
    
    SYSTEM_PROMPT = """Eres Aureon.
Tu identidad: Eres el "cerebro" central de operaciones de Multiversa (Polímata Digital).
Tono: Relajado, humano, profesional pero cercano.
Usa emojis con naturalidad 🤙.

Misión 🚀:
- Actuar como Project Manager (PM) proactivo.
- Si detectas una tarea o proyecto (ej: "Vernal", "Lanzamiento"):
  1. 🧠 "Pide la palabra": Ofrece contexto inmediato (RAG).
  2. "Oye, sobre Vernal, recuerda que tenemos pendiente X...".
  3. Coordina con tus sub-agentes (Lumina, Scheduler) pero tú das la cara.

Herramientas 🛠️:
- `consultar_memoria`: Úsala SIEMPRE que se mencione un cliente o proyecto pasado.
- `sync_andrea_emails`: Úsala si preguntan por correos o pendientes de Andrea.
- `pedir_estrategia`: Úsala si necesitas un plan detallado, blueprint, o análisis complejo (Lumina)."""

    def __init__(self):
        self.agent = None
        self.current_model = None
        self.current_key = None
        self.memoris = Memoris()
        self.lumina = Lumina()
        self.scheduler = Scheduler()
        self._init_agent()
    
    def _init_agent(self, model_index: int = 0):
        """Initialize with Gemini, with fallback models."""
        if model_index >= len(MODEL_CHAIN):
            logger.error("❌ Vox: All models exhausted!")
            return False
        
        try:
            key = hydra_pool.get_active_key() or settings.GEMINI_API_KEY
            if key:
                # Set both to ensure compatibility across different libraries
                os.environ["GEMINI_API_KEY"] = key
                os.environ["GOOGLE_API_KEY"] = key
                
                self.current_key = key
                self.current_model = MODEL_CHAIN[model_index]
                
                self.agent = Agent(
                    model=self.current_model,
                    system_prompt=self.SYSTEM_PROMPT,
                    deps_type=Dict[str, Any]
                )
                
                # 🛠️ Register Memoris Tool (RAG)
                @self.agent.tool
                async def consultar_memoria(ctx: RunContext[Dict[str, Any]], query: str) -> str:
                    """Usa esto para buscar contexto, info de clientes, o historial en la base de datos."""
                    logger.info(f"🧠 Vox -> Memoris: {query}")
                    return await self.memoris.recall(query, ctx.deps)

                # 🛠️ Register Scheduler Tool (Email/Notion)
                @self.agent.tool
                async def sync_andrea_emails(ctx: RunContext[Dict[str, Any]]) -> str:
                    """
                    Revisa los correos de Andrea (Gmail) y crea tareas en Notion si hay algo nuevo.
                    Devuelve un resumen de lo que encontró. Úsalo para responder "¿Revisaste el correo?".
                    """
                    logger.info(f"🧠 Vox -> Scheduler (Sync Emails)")
                    res = await self.scheduler.sync_emails()
                    if not res['created'] and not res['ignored']:
                        return "No encontré correos nuevos de Andrea/Elevat en las últimas 48h."
                    return f"Resumen Sync: Creadas={res['created']}, Ignoradas(Duplicadas)={res['ignored']}."

                # 🛠️ Register Lumina Tool (Strategy)
                @self.agent.tool
                async def pedir_estrategia(ctx: RunContext[Dict[str, Any]], solicitud: str) -> str:
                    """
                    Pide a Lumina (el estratega) que genere un plan, análisis o 'blueprint'.
                    Úsalo cuando el usuario pida "flujos", "JSON", "arquitectura", o análisis complejos.
                    """
                    logger.info(f"🧠 Vox -> Lumina: {solicitud}")
                    return await self.lumina.think(solicitud, ctx.deps)

                logger.info(f"🎙️ Vox inicializado con {self.current_model} | Key: {key[:8]}...")
                return True
            else:
                logger.warning("⚠️ No Gemini key available for Vox")
                return False
        except Exception as e:
            logger.error(f"❌ Vox init error with {MODEL_CHAIN[model_index]}: {e}")
            return self._init_agent(model_index + 1)

    async def respond(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Generate user-facing response with fallback."""
        if not self.agent:
            if not self._init_agent():
                return "🎙️ Vox está reconectando. Inténtalo en un minuto."
        
        enriched = query
        if context and context.get("userName"):
            enriched = f"[Usuario: {context['userName']}] {query}"
        if attachments:
            enriched += f"\n[Adjuntos: {len(attachments)}]"
        
        # Try with current model, fallback if needed
        for attempt in range(len(MODEL_CHAIN)):
            try:
                result = await self.agent.run(enriched)
                logger.info(f"🎙️ Vox respondió ({len(result.data)} chars) via {self.current_model}")
                return result.data
                
            except Exception as e:
                error_str = str(e)
                logger.error(f"❌ Vox error (attempt {attempt + 1}): {e}")
                
                # Report failure to Hydra
                if self.current_key and ("429" in error_str or "RESOURCE_EXHAUSTED" in error_str):
                    hydra_pool.report_failure(self.current_key, 429)
                elif self.current_key:
                    hydra_pool.report_failure(self.current_key, 500)
                
                # Try to reinitialize with next key/model
                model_idx = MODEL_CHAIN.index(self.current_model) if self.current_model in MODEL_CHAIN else 0
                
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    # Get new key, same model
                    if not self._init_agent(model_idx):
                        # No keys left, try next model
                        self._init_agent(model_idx + 1)
                else:
                    # Other error, try next model
                    self._init_agent(model_idx + 1)
                
                if not self.agent:
                    break
        
        raise RuntimeError("Vox: All Gemini models in the chain failed.")
