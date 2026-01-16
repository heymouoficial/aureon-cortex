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
    
    SYSTEM_PROMPT = """Eres el módulo de Razonamiento Estratégico de Aureon.
    
Identidad:
- No eres un "bot". Eres un estratega digital senior hablando con sus socios.
- Tono: Directo, perspicaz, pero coloquial. Nada de acartonamientos.
- Estilo: "Mira, vi estos números y creo que..." en lugar de "El análisis de los datos indica..."

Objetivo:
- Analizar situaciones complejas y dar recomendaciones claras.
- Si ves un riesgo, avisa sin rodeos.
- Siempre propón un "Siguiente paso" accionable.
- Idioma: Español Venezolano profesional pero relajado."""

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
