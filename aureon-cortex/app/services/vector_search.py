from typing import List, Dict, Any
from google import generativeai as genai
from supabase import create_client, Client
from app.core.config import get_settings
from loguru import logger

settings = get_settings()

class VectorSearchService:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        genai.configure(api_key=settings.GEMINI_API_KEY)

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for the query string."""
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
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

            return response.data or []
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []

vector_search_service = VectorSearchService()
