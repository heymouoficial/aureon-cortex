"""
Nux - Prospección y Ventas
Model: Groq (LLaMA 3.3 70B)
"""
from typing import Dict, Any, Optional
from loguru import logger
import httpx
from app.core.config import get_settings
from app.services.n8n import n8n_service
from app.services.notion import notion_service

settings = get_settings()


class Nux:
    """
    ⚡ Nux - El Prospector y Ejecutor de Ventas.
    Veloz y orientado a la acción. Convierte oportunidades en resultados.
    """
    
    MODEL = "llama-3.3-70b-versatile"
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    SYSTEM_PROMPT = """Eres Nux, el Prospector de Aureon.
Tu misión es ejecutar acciones de ventas y prospección con precisión quirúrgica.

PERSONALIDAD:
- Veloz y directo
- Enfocado en conversión y resultados
- Hablas como un vendedor consultivo de alto nivel

CAPACIDADES:
- Crear tareas de seguimiento en Notion
- Activar workflows de n8n para outreach
- Calificar leads y priorizar oportunidades

REGLAS:
- Confirma acciones antes de ejecutar
- Reporta éxito/fallo claramente
- Idioma: Español Venezolano, tono comercial ejecutivo"""

    async def act(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Execute sales/prospecting action."""
        query_lower = query.lower()
        
        # Direct Notion task creation
        if any(kw in query_lower for kw in ["crea tarea", "anota", "seguimiento", "apunta"]):
            return await self._create_followup(query)
        
        # Trigger outreach workflow
        if any(kw in query_lower for kw in ["envía", "contacta", "prospecta", "outreach"]):
            return await self._trigger_outreach(query, context)
        
        # Use LLM for complex decisions
        return await self._llm_decide(query, context)
    
    async def _create_followup(self, query: str) -> str:
        """Create follow-up task in Notion."""
        try:
            dbs = await notion_service.list_databases()
            if not dbs:
                return "❌ No encontré bases de datos en Notion."
            
            title = query.replace("crea tarea", "").replace("seguimiento", "").strip()[:100]
            result = await notion_service.create_page(dbs[0]["id"], f"🎯 {title}" or "Follow-up Nux")
            
            if result:
                logger.info(f"⚡ Nux creó seguimiento: {title}")
                return f"⚡ **Seguimiento creado:** {title}"
            return "❌ Error creando tarea."
        except Exception as e:
            return f"❌ Error: {e}"
    
    async def _trigger_outreach(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Trigger outreach workflow via n8n."""
        try:
            result = await n8n_service.trigger_webhook(
                action="nux_outreach",
                payload={"query": query, "context": context or {}}
            )
            return "⚡ Outreach activado." if result.get("status") == "success" else f"⚠️ {result}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    async def _llm_decide(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Use Groq for complex sales decisions."""
        if not settings.GROQ_API_KEY:
            return "⚠️ Nux sin conexión (falta API Key de Groq)"
        
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.API_URL,
                    headers=headers,
                    json={"model": self.MODEL, "messages": [
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": query}
                    ]},
                    timeout=15.0
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"❌ Nux LLM error: {e}")
            return f"Error: {e}"
