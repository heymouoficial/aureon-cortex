from typing import Dict, Any, List, Optional
from loguru import logger
from app.services.mcp_client import mcp_client
from app.services.notion import notion_service
from app.services.notion import notion_service

class Scheduler:
    """
    📅 Scheduler Agent - Specialists in Notion-based meeting and calendar management.
    """
    
    def __init__(self):
        self.server_name = "notion"

    async def act(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process the user query to manage appointments/tasks in Notion.
        """
        logger.info(f"📅 Scheduler acting on: {query}")
        
        try:
        try:
            # Analyze intent
            query_lower = query.lower()
            
            # intent: LIST / READ
            if any(kw in query_lower for kw in ["qué tengo", "revisa", "lee", "busca", "muéstrame", "agenda", "calendario"]):
                summary = await notion_service.get_tasks_summary()
                return f"📅 He consultado tu Notion:\n\n{summary}"
            
            # intent: CREATE / WRITE
            elif any(kw in query_lower for kw in ["agendar", "crear", "nueva reunión", "tarea", "anota", "cita"]):
                # Simple logic to find a database (MVP: takes the first one found)
                dbs = await notion_service.list_databases()
                if not dbs:
                    return "❌ No encontré ninguna base de datos en Notion para guardar esto."
                
                target_db = dbs[0]["id"]
                # Extract title (rudimentary)
                title = query.replace("agendar", "").replace("crear", "").replace("tarea", "").strip() or "Nueva Tarea Aureon"
                
                result = await notion_service.create_page(target_db, f"📅 {title}")
                if result:
                    return f"✅ Entendido. He creado '**{title}**' en tu base de datos principal de Notion."
                else:
                    return "⚠️ Pude conectar con Notion pero hubo un error creando la página. Verifica los permisos de integración."

            else:
                return "📅 Soy el Scheduler. Puedo leer tu agenda en Notion o crear nuevas tareas. ¿Qué necesitas?"
            
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
            return f"Tuve un problema al acceder a Notion: {e}"

scheduler = Scheduler()
