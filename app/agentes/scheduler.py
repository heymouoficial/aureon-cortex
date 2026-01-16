from typing import Dict, Any, List, Optional
from loguru import logger
from app.services.mcp_client import mcp_client
from app.services.notion import notion_service
from app.services.google_workspace import google_service
import asyncio


class Scheduler:
    """
    📅 Scheduler Agent - Specialists in Notion-based meeting and calendar management.
    """
    
    def __init__(self):
        self.server_name = "notion"

    async def sync_emails(self, query: str = None) -> Dict[str, List[str]]:
        """
        Public method to sync Gmail to Notion. Returns structured results.
        query: Optional specific gmail query. Defaults to Andrea's filter.
        """
        # 1. Search Emails (Dual Persona: Personal & Agency)
        # Prepare query logic
        target_senders = ["andreachimarasonlinebusiness@gmail.com", "christomoreno6@gmail.com", "elevatmarketing.com"]

        query = query or (
            f"from:({', '.join(target_senders)}) "
            f"newer_than:2d"
        )
        
        emails = await google_service.search_emails(query)
        if not emails:
            return {"created": [], "ignored": []}
        
        # 2. Get Notion Context
        notion_summary = await notion_service.get_tasks_summary()
        
        # 3. Process & Sync
        created_tasks = []
        ignored_tasks = []
        
        # Simple logic: Subject/Snippet is the task
        dbs = await notion_service.list_databases()
        if not dbs:
             logger.warning("No Notion DB found in sync_emails")
             return {"created": [], "ignored": [], "error": "No databases found"}
             
        target_db = dbs[0]["id"]
        
        for email in emails:
            candidate_task = email['subject']
            # De-duplication check (Naive)
            if candidate_task.lower() in notion_summary.lower():
                ignored_tasks.append(candidate_task)
                continue
                
            # Create Task
            await notion_service.create_page(target_db, f"📧 {candidate_task}")
            created_tasks.append(candidate_task)
            
        return {"created": created_tasks, "ignored": ignored_tasks}

    async def act(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process the user query to manage appointments/tasks in Notion.
        """
        logger.info(f"📅 Scheduler acting on: {query}")
        
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

            # intent: SYNC GMAIL TASKS (Specific Mission)
            elif any(kw in query_lower for kw in ["correo", "email", "gmail"]) and "andrea" in query_lower:
                results = await self.sync_emails()
                
                if not results["created"] and not results["ignored"]:
                     return "📧 Busqué correos recientes de Andrea/Elevat pero no encontré nada nuevo."
                
                response = f"📧 **Sincronización con Andrea Completada:**\n"
                if results["created"]:
                    response += f"\n✅ **Nuevas Tareas Creadas:**\n" + "\n".join([f"- {t}" for t in results["created"]])
                if results["ignored"]:
                    response += f"\n\n👀 **Ya existían en Notion:**\n" + "\n".join([f"- {t}" for t in results["ignored"]])
                    
                return response

            else:
                return "📅 Puedo leer tu agenda en Notion, crear tareas, o sincronizar correos. ¿Qué necesitas?"
            
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
            return f"Tuve un problema al acceder a Notion: {e}"

scheduler = Scheduler()
