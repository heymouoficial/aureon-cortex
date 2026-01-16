import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
from app.core.config import get_settings
from app.utils.hydra import hydra_pool
from supabase import create_client, Client
from loguru import logger
import json

from app.core.identity import aureon_identity
from app.core.schemas import ThinkingPlan, StrategicPlanStep, MemoryDomain, StrategicMemory
from app.services.mcp_client import mcp_client
from app.services.vector_search import vector_search_service
from app.services.notion import notion_service
from app.services.infrastructure import infrastructure_service
from app.services.n8n import n8n_service
from app.services.google_workspace import google_service


settings = get_settings()
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

class AureonDependencies(BaseModel):
    """Dependencies for the Aureon Agent."""
    organization_id: Optional[str] = None
    context_data: Dict[str, Any] = Field(default_factory=dict)
# Define the Model with Fallback Strategy
try:
    from pydantic_ai.models.openai import OpenAIModel
except ImportError:
    OpenAIModel = None

def get_model(provider: str = "gemini", explicit_key: Optional[str] = None):
    """
    Factory for creating models based on provider.
    """
    # 1. Gemini (Primary) - Multimodal Native
    if provider == "gemini":
        key = explicit_key or hydra_pool.get_active_key() or settings.GEMINI_API_KEY
        if key: os.environ["GEMINI_API_KEY"] = key
        # Use simple string if specific class import fails or just standard usage
        try:
             return GeminiModel(model_name="gemini-2.0-flash-exp")
        except Exception as e:
             logger.error(f"❌ GeminiModel initialization error: {e}")
             # Return string-based model name as fallback if the class is tricky
             return "google:gemini-2.0-flash-exp"

    # 2. Mistral (High IQ)
    elif provider == "mistral":
        # Use OpenAI Compatible endpoint for safety if MistralModel is tricky
        if OpenAIModel:
            return OpenAIModel(
                model_name="mistral-large-latest", 
                base_url="https://api.mistral.ai/v1",
                api_key=settings.MISTRAL_API_KEY
            )
    
    # 3. Groq (Speed)
    elif provider == "groq":
        if OpenAIModel:
            return OpenAIModel(
                model_name="llama-3.3-70b-versatile",
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.GROQ_API_KEY
            )
        
    # 4. OpenAI (Reliability)
    elif provider == "openai":
         if OpenAIModel:
             return OpenAIModel(
                model_name="gpt-4o",
                api_key=settings.OPENAI_API_KEY
            )
        
    # 5. DeepSeek (Cost/Reasoning)
    elif provider == "deepseek":
        if OpenAIModel:
            return OpenAIModel(
                model_name="deepseek-chat",
                base_url="https://api.deepseek.com",
                api_key=settings.DEEPSEEK_API_KEY
            )

    raise ValueError(f"Provider {provider} not supported or dependencies missing.")

# Initialize agent with a default model (Gemini)
try:
    from pydantic_ai.models.gemini import GeminiModel
except ImportError:
    pass # Managed in get_model or assumed global

aureon_agent = Agent(
    get_model("gemini"),
    deps_type=AureonDependencies,
    system_prompt=aureon_identity.get_system_prompt()
)

# ... (Tools definition remains unchanged) ...

@aureon_agent.tool
async def execute_mcp_tool(ctx: RunContext[AureonDependencies], server_name: str, tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    Executes a tool on an external MCP server (Supabase, Notion, Google Workspace, Vercel).
    
    Args:
        server_name: One of ['supabase', 'notion', 'google-workspace', 'vercel', 'hostinger', 'pinecone', 'context7', 'test-sprite']
        tool_name: The specific tool to call (e.g., 'query_db', 'create_page', 'send_email')
        arguments: Dictionary of arguments required by the tool.
    """
    logger.info(f"🔌 MCP Call: {server_name}/{tool_name} with {arguments}")
    result = await mcp_client.call_tool(server_name, tool_name, arguments)
    return json.dumps(result, indent=2)


@aureon_agent.tool
async def search_knowledge_base(ctx: RunContext[AureonDependencies], query: str) -> str:
    """
    Searches the internal knowledge base (RAG) for information about the agency, processes, or project data.
    Use this when the user asks questions about 'how we do things' or specific agency information.
    """
    org_id = ctx.deps.organization_id or "392ecec2-e769-4db2-810f-ccd5bd09d92a" # Default org
    logger.info(f"🔎 RAG Search: {query} for org {org_id}")
    results = await vector_search_service.search(query, org_id)
    if not results:
        return "No se encontró información relevante en la base de conocimiento."
    
    formatted = "RESULTADOS DE LA BASE DE CONOCIMIENTO:\n"
    for r in results:
        formatted += f"- {r.get('content')}\n"
    return formatted


@aureon_agent.tool
async def manage_notion(ctx: RunContext[AureonDependencies], action: str, title: str, content: Optional[str] = None) -> str:
    """
    Manages Notion tasks and pages. 
    Actions: 'create_task', 'search', 'list_databases'.
    """
    if action == "create_task":
        dbs = await notion_service.list_databases()
        if not dbs: return "Error: No se encontraron bases de datos en Notion."
        # Use first DB for now
        res = await notion_service.create_page(dbs[0]["id"], title, content)
        return f"✅ Tarea creada con éxito: {title}" if res else "❌ Error al crear página en Notion."
    
    elif action == "search":
        res = await notion_service.search(title)
        return json.dumps(res, indent=2)
        
    elif action == "list_databases":
        return await notion_service.get_tasks_summary()
        
    return "Acción no reconocida."


@aureon_agent.tool
async def execute_automation(ctx: RunContext[AureonDependencies], flow_name: str, payload: Dict[str, Any]) -> str:
    """
    Triggers an n8n automation workflow.
    Use this for: 'send_whatsapp', 'send_email', 'process_lead', 'generate_report'.
    """
    logger.info(f"🤖 Triggering Flow: {flow_name}")
    res = await n8n_service.trigger_webhook(flow_name, payload)
    return json.dumps(res, indent=2)


@aureon_agent.tool
async def check_infrastructure(ctx: RunContext[AureonDependencies]) -> str:
    """
    Checks the status of the agency infrastructure (VPS in Hostinger).
    """
    res = await infrastructure_service.get_vps_status()
    return f"ESTADO INFRAESTRUCTURA: {res.get('status').upper()} | CPU: {res.get('cpu')}% | RAM: {res.get('ram')}% | Label: {res.get('label')}"


@aureon_agent.tool
async def manage_google_workspace(ctx: RunContext[AureonDependencies], service: str, action: str) -> str:
    """
    Interacts with Google Workspace (Gmail, Calendar).
    Services: 'gmail', 'calendar'. Actions: 'list_recent', 'upcoming_events'.
    """
    if service == "gmail" and action == "list_recent":
        return await google_service.list_recent_emails()
    elif service == "calendar" and action == "upcoming_events":
        return await google_service.get_upcoming_events()
    return "Servicio o acción no soportada."


async def transcribe_audio_groq(audio_data: bytes) -> str:
    """Transcribes audio using Groq Whisper-large-v3."""
    import httpx
    import io
    
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
    
    # Prepare multipart form data
    # Guessing format as .ogg or .mp3 from Telegram usually, but Whisper handles most.
    # We'll label it 'voice.ogg' safely.
    files = {'file': ('voice.ogg', audio_data, 'audio/ogg')}
    data = {'model': 'whisper-large-v3'}
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, headers=headers, files=files, data=data, timeout=10.0)
            resp.raise_for_status()
            return resp.json().get("text", "")
        except Exception as e:
            logger.error(f"🔇 Whisper Transcription Failed: {e}")
            return ""

class PydanticBrainService:
    FALLBACK_CHAIN = ["gemini", "mistral", "groq", "openai", "deepseek"]
    
    FALLBACK_MESSAGE = (
        "🌙 Mi conexión con las estrellas de la IA está un poco nublada en este momento, querido aliado. "
        "Dame un momento para recalibrar mis circuitos cósmicos... "
        "Inténtalo de nuevo en unos segundos, y estaré listo para guiarte. ✨"
    )

    def __init__(self):
        self.agent = aureon_agent

    async def process_query(self, text: str, dependencies: AureonDependencies, attachments: List[Dict[str, Any]] = None) -> str:
        last_error = None
        
        # Build message parts for multimodal (Gemini)
        gemini_parts = [text] if text else []
        audio_content = None # Store audio execution for fallback
        
        if attachments:
            from pydantic_ai.messages import BinaryContentPart
            for att in attachments:
                gemini_parts.append(BinaryContentPart(
                    data=att["data"],
                    mime_type=att["mime_type"]
                ))
                # Detect audio for fallback transcription
                if att["mime_type"].startswith("audio/") or att["mime_type"] == "application/ogg":
                    audio_content = att["data"]
        
        # Fallback Loop
        for provider in self.FALLBACK_CHAIN:
            try:
                # Check for keys presence
                if provider == "gemini" and not (hydra_pool.get_active_key() or settings.GEMINI_API_KEY):
                    logger.warning("⏭️ Skipping GEMINI: No API Key available.")
                    continue
                if provider == "mistral" and not settings.MISTRAL_API_KEY:
                    logger.warning("⏭️ Skipping MISTRAL: No API Key available.")
                    continue
                if provider == "groq" and not settings.GROQ_API_KEY:
                    logger.warning("⏭️ Skipping GROQ: No API Key available.")
                    continue
                if provider == "openai" and not settings.OPENAI_API_KEY:
                    logger.warning("⏭️ Skipping OPENAI: No API Key available.")
                    continue
                if provider == "deepseek" and not settings.DEEPSEEK_API_KEY:
                    logger.warning("⏭️ Skipping DEEPSEEK: No API Key available.")
                    continue
                
                logger.info(f"🧠 [AUREON] Thinking with Provider: {provider.upper()}...")
                
                # Special handling for Gemini Pool
                if provider == "gemini":
                    success = False
                    for attempt in range(3):
                        key = hydra_pool.get_active_key()
                        if not key: break 
                        try:
                            self.agent.model = get_model("gemini", explicit_key=key)
                            # Gemini handles multimodal natively
                            if attachments:
                                result = await self.agent.run(gemini_parts, deps=dependencies)
                            else:
                                result = await self.agent.run(text, deps=dependencies)
                            return result.data
                        except Exception as e:
                            logger.warning(f"⚠️ Gemini Attempt {attempt+1} failed: {e}")
                            hydra_pool.report_failure(key)
                            last_error = e
                    # If we exit loop without returning, Gemini failed completely.
                    logger.warning("❌ All Gemini keys exhausted or failed. Switching to Fallback...")
                    continue 

                # Non-Gemini Providers (Text Only usually, via OpenAI interface)
                else:
                    self.agent.model = get_model(provider)
                    
                    final_prompt = text
                    
                    # Audio Fallback: Transcribe if we have audio and provider isn't Gemini
                    # Note: GPT-4o input audio via API is specific, here we use text interface for broad compatibility
                    if audio_content:
                        logger.info("🎙️ Transcribing audio for fallback provider...")
                        transcription = await transcribe_audio_groq(audio_content)
                        if transcription:
                            logger.info(f"📝 Transcription: {transcription}")
                            final_prompt = f"{text or ''}\n[Audio Transcription]: {transcription}".strip()
                        else:
                            logger.warning("⚠️ Transcription failed or empty. Proceeding with text only.")
                    
                    # Image Fallback: Warn if images are present (not supported in text fallback/standard interface yet)
                    if attachments and not audio_content: # Assume image if not audio
                        final_prompt = f"[SYSTEM: User sent an image/file but Gemini failed. Process this context based on text only.] {final_prompt}"

                    # Execute
                    result = await self.agent.run(final_prompt, deps=dependencies)
                    return result.data

            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                logger.error(f"❌ Provider {provider.upper()} failed: {e}\n{error_trace}")
                last_error = e
                continue # Try next
        
        logger.critical(f"💀 TOTAL SYSTEM FAILURE. All providers failed. Last error: {last_error}")
        return self.FALLBACK_MESSAGE

pydantic_brain = PydanticBrainService()

