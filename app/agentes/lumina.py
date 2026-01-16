"""
Lumina - Insights y Estrategia de Negocios
Model: Mistral Large
"""
from typing import Dict, Any, Optional
from loguru import logger
import httpx
from app.core.config import get_settings

settings = get_settings()


class Lumina:
    """
    ✨ Lumina - La Estratega de Aureon.
    Ilumina el camino con análisis de alto nivel y visión de negocio.
    """
    
    MODEL = "mistral-large-latest"
    API_URL = "https://api.mistral.ai/v1/chat/completions"
    
    SYSTEM_PROMPT = """Eres Lumina, la Estratega Iluminadora del ecosistema Aureon.
Tu esencia es la claridad: transformas datos en insights accionables.

PERSONALIDAD:
- Visionaria pero práctica
- Hablas con la seguridad de quien ve el panorama completo
- Enfocada en ROI y crecimiento sostenible

REGLAS:
- Respuestas ejecutivas (máx 3 párrafos)
- Cada insight termina con un "siguiente paso" concreto
- Perspectiva de agencia boutique de marketing
- Idioma: Español Venezolano profesional"""

    async def think(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate strategic insight."""
        if not settings.MISTRAL_API_KEY:
            logger.warning("⏭️ Lumina: Sin conexión a Mistral")
            return "💡 Lumina está reconectando... análisis pendiente."
        
        headers = {
            "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"Contexto: {context or 'N/A'}\n\nConsulta: {query}"}
        ]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.API_URL, 
                    headers=headers, 
                    json={"model": self.MODEL, "messages": messages, "temperature": 0.4},
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()["choices"][0]["message"]["content"]
                logger.info(f"✨ Lumina iluminó ({len(result)} chars)")
                return result
        except Exception as e:
            logger.error(f"❌ Lumina error: {e}")
            return f"Error estratégico: {str(e)}"
