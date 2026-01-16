import httpx
from typing import List, Dict, Any, Optional
from app.core.config import get_settings
from loguru import logger

settings = get_settings()

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

class NotionService:
    def __init__(self):
        self.token = settings.NOTION_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION
        }

    async def search(self, query: str, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search across all Notion pages and databases."""
        if not self.token:
            logger.warning("Notion token not configured.")
            return []

        payload = {"query": query}
        if filter_type:
            payload["filter"] = {"value": filter_type, "property": "object"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{NOTION_API_BASE}/search",
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
            except Exception as e:
                logger.error(f"Notion search error: {e}")
                return []

    async def get_page(self, page_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific Notion page."""
        if not self.token:
            return None

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{NOTION_API_BASE}/pages/{page_id}",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Notion get_page error: {e}")
                return None

    async def query_database(self, database_id: str, filter_obj: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Query a Notion database."""
        if not self.token:
            return []

        payload = {}
        if filter_obj:
            payload["filter"] = filter_obj

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{NOTION_API_BASE}/databases/{database_id}/query",
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
            except Exception as e:
                logger.error(f"Notion query_database error: {e}")
                return []

    async def list_databases(self) -> List[Dict[str, Any]]:
        """List all databases Aureon has access to."""
        results = await self.search("", filter_type="database")
        return [
            {
                "id": r["id"],
                "title": r.get("title", [{}])[0].get("plain_text", "Untitled") if r.get("title") else "Untitled"
            }
            for r in results
        ]

    async def get_tasks_summary(self) -> str:
        """Get a summary of tasks from Notion (searches for common task-related databases)."""
        databases = await self.list_databases()
        if not databases:
            return "No se encontraron bases de datos en Notion."

        summary = f"📋 **Bases de datos disponibles en Notion ({len(databases)}):**\n"
        for db in databases[:10]:  # Limit to 10
            summary += f"- {db['title']} (`{db['id'][:8]}...`)\n"
        return summary

    async def create_page(self, database_id: str, title: str, content: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create a new page in a database."""
        if not self.token:
            return None

        # Build properties (Assumes "Name" or "Title" is the title property)
        # We try "Name" first, as it's common in Databases. If it fails, user needs to adjust.
        # Actually safer to just use "title" in properties for generic implementation if we knew the schema.
        # But standard databases usually have a title property.
        
        # NOTE: We'll assume the primary title property is named "Name" or "Task" or "Title".
        # For robustness, we construct a generic payload often accepted if we create into a database.
        
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        }

        children = []
        if content:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content
                            }
                        }
                    ]
                }
            })

        payload = {
            "parent": {"database_id": database_id},
            "properties": properties,
            "children": children
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{NOTION_API_BASE}/pages",
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )
                if response.status_code != 200:
                    # Try adapting title property name if "Name" fails? 
                    # For now just log usage
                    logger.error(f"Notion create error: {response.text}")
                    return None
                    
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Notion create_page Exception: {e}")
                return None

notion_service = NotionService()

