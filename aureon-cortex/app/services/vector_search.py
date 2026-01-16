from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from app.core.config import get_settings
from app.utils.hydra import hydra_pool
from google import genai
from google.genai import types
from loguru import logger
import asyncio

settings = get_settings()

class VectorSearchService:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        self._client: Optional[genai.Client] = None
        self._current_key: Optional[str] = None

    def _get_client(self) -> genai.Client:
        """Get or create genai Client from hydra pool."""
        active_key = hydra_pool.get_active_key() or settings.GEMINI_API_KEY
        if not active_key:
            raise ValueError("No GEMINI_API_KEY available for embeddings.")
            
        if self._client is None or self._current_key != active_key:
            self._client = genai.Client(api_key=active_key)
            self._current_key = active_key
        return self._client

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for the query string using Gemini 2.0 (text-embedding-004)."""
        try:
            client = self._get_client()
            # Run in thread pool as google-genai is sync
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: client.models.embed_content(
                    model="text-embedding-004",
                    contents=text,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
                )
            )
            return result.embeddings[0].values
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            # Try rotating key on failure
            hydra_pool.rotate_key()
            raise

    async def search(self, query: str, organization_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Perform vector search in Supabase document_chunks."""
        try:
            embedding = await self.get_embedding(query)
            
            # Call the match_documents RPC in Supabase
            response = self.supabase.rpc(
                'match_documents',
                {
                    'query_embedding': embedding,
                    'match_threshold': 0.5,
                    'match_count': limit,
                    'filter_organization_id': organization_id
                }
            ).execute()

            results = response.data or []
            logger.info(f"🔎 V-Search: Found {len(results)} chunks for org {organization_id}")
            return results
        except Exception as e:
            logger.error(f"❌ Error in vector search: {e}")
            return []

vector_search_service = VectorSearchService()
