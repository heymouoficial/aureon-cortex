"""
Memorís - Guardián del Conocimiento (RAG)
Model: Gemini (embeddings) + Supabase Vector Search
"""
from typing import Dict, Any, Optional
from loguru import logger
from app.services.vector_search import vector_search_service
from app.core.config import get_settings

settings = get_settings()


class Memoris:
    """
    📚 Memorís - El Archivista de Aureon.
    Guardián del conocimiento. Recupera contexto y memoria de la agencia.
    """
    
    DEFAULT_ORG_ID = "392ecec2-e769-4db2-810f-ccd5bd09d92a"

    async def recall(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Search the knowledge base."""
        org_id = context.get("organization_id", self.DEFAULT_ORG_ID) if context else self.DEFAULT_ORG_ID
        
        logger.info(f"📚 Memorís buscando: '{query[:50]}...'")
        
        try:
            results = await vector_search_service.search(query, org_id, limit=5)
            
            if not results:
                return "🔍 Memorís no encontró información relevante en la base de conocimiento."
            
            formatted = "📚 **Memorís encontró:**\n\n"
            for i, r in enumerate(results, 1):
                content = r.get("content", "")[:300]
                source = r.get("metadata", {}).get("file_name", "Neural DB")
                formatted += f"**{i}.** _{source}_\n{content}...\n\n"
            
            logger.info(f"📚 Memorís recuperó {len(results)} fragmentos")
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Memorís error: {e}")
            return f"Error consultando memoria: {str(e)}"
    
    async def store(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store new information. (Future implementation)"""
        logger.warning("⚠️ Memorís.store() pendiente de implementación")
        return False
