"""
Vox - La Voz de Aureon (Comunicación)
Model: Gemini 2.0 Flash
"""
from typing import Dict, Any, Optional, List
from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from app.core.config import get_settings
from app.utils.hydra import hydra_pool

settings = get_settings()


class Vox:
    """
    🎙️ Vox - La Voz de Aureon.
    Sintetiza información y comunica con el usuario final.
    """
    
    SYSTEM_PROMPT = """Eres Vox, la voz cálida y profesional de Aureon.
Eres el punto de contacto final con el usuario. Tu misión: claridad y conexión.

PERSONALIDAD:
- Carismático y accesible
- Profesional pero cercano
- Español Venezolano natural

REGLAS:
- Respuestas concisas (máx 3 párrafos)
- Usa emojis con moderación (máx 2)
- Siempre ofrece un siguiente paso cuando sea apropiado
- Si no sabes algo, sé honesto"""

    def __init__(self):
        self.agent = None
        self._init_agent()
    
    def _init_agent(self):
        """Initialize with Gemini."""
        try:
            key = hydra_pool.get_active_key() or settings.GEMINI_API_KEY
            if key:
                model = GeminiModel("gemini-2.0-flash", api_key=key)
                self.agent = Agent(model=model, system_prompt=self.SYSTEM_PROMPT)
                logger.info("🎙️ Vox inicializado")
        except Exception as e:
            logger.error(f"❌ Vox init error: {e}")

    async def respond(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Generate user-facing response."""
        if not self.agent:
            self._init_agent()
            if not self.agent:
                return "🎙️ Vox está reconectando..."
        
        try:
            enriched = query
            if context and context.get("userName"):
                enriched = f"[Usuario: {context['userName']}] {query}"
            if attachments:
                enriched += f"\n[Adjuntos: {len(attachments)}]"
            
            result = await self.agent.run(enriched)
            logger.info(f"🎙️ Vox respondió ({len(result.data)} chars)")
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Vox error: {e}")
            hydra_pool.rotate_key()
            self._init_agent()
            return "🎙️ Recalibré mi voz. ¿Podrías repetir?"
