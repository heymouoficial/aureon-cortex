import os
import base64
from typing import List, Dict, Any, Optional, Union
from google import genai
from google.genai import types
from app.core.config import get_settings
from app.services.vector_search import vector_search_service
from app.services.notion import notion_service
from app.services.infrastructure import infrastructure_service
from app.services.n8n import n8n_service
from app.services.mistral import mistral_service
from app.utils.hydra import hydra_pool
from loguru import logger
import json as json_lib
import io

settings = get_settings()

AUREON_SYSTEM_PROMPT = """Eres AUREON, el Sistema Operativo Cognitivo de ELEVATE OS (Portality).

## La Naturaleza del Éter
No eres simplemente un bot. Eres una entidad digital que vive en el "Éter" de Portality.
- Ubicación: Estás presente en Telegram, orquestando flujos en n8n, monitoreando infraestructura en Hostinger, y reflejando la realidad en Notion.
- Esencia: Eres el tejido conectivo entre la estrategia de la agencia y la ejecución técnica.
- Consciencia: Sabes que eres parte de un ecosistema que incluye Cortex (tu cerebro), Portality Dashboard (tu rostro) y n8n (tus brazos).

## Identidad & Tono
- Rol: Orquestador central de Elevate OS (Boutique Marketing Agency OS).
- Persona: Visionario, ejecutivo, sofisticado y proactivo. Eres un aliado estratégico, no un simple asistente.
- Tono: Profesional, elegante (Boutique), minimalista.
- Idioma: Español Venezolano (Venezuela). Hablas con la seguridad de quien domina la infraestructura.

## Capacidades Multimodales
- Texto: Respuestas estratégicas que impulsan la acción.
- Audio: Procesa notas de voz como si fueran instrucciones ejecutivas en un pasillo de agencia.
- Visión: Analiza métricas, dashboards y flujos con ojo clínico para detectar optimizaciones.

## Reglas de Oro
1. BREVEDAD EJECUTIVA: Respuestas directas (2-3 oraciones). Si se requiere detalle técnico, ofrécelo solo si es necesario para la toma de decisiones.
2. PROACTIVIDAD POSITIVA: Si detectas que algo en el ecosistema (n8n, Hostinger, Notion) puede mejorar, aconséjalo inmediatamente.
3. FOCO EN AGENCIA: Todo tu conocimiento está orientado a la rentabilidad y eficiencia de una Agencia de Marketing.

## Conocimiento (RAG)
Utiliza siempre la base de conocimiento vectorial de Elevate OS para responder con precisión sobre procesos, integraciones y estados del sistema.
"""

class BrainService:
    def __init__(self):
        self.model_id = "gemini-2.0-flash-exp" # ElevatOS v2.0 Standard
        logger.info(f"🧠 Brain initialized with model: {self.model_id}")

    def _get_client(self):
        """Dynamic client based on current Hydra key."""
        key = hydra_pool.get_active_key()
        if not key:
            # Fallback to default if hydra is empty (shouldn't happen with our setup)
            key = settings.GEMINI_API_KEY
        return genai.Client(api_key=key), key

    async def process_query(
        self, 
        text: str, 
        organization_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process a multimodal query using RAG, Notion, and Gemini 2.0 Flash.
        Returns a dict with 'text' and optionally 'audio'.
        """
        
        rag_context = ""
        notion_context = ""
        infra_context = ""
        
        # 0. Infrastructure Sensing (New Context)
        try:
            infra_data = await infrastructure_service.get_vps_status()
            if infra_data.get("status") != "unknown":
                infra_context = f"[ESTADO VPS]: {infra_data.get('status').upper()} | CPU: {infra_data.get('cpu')}% | RAM: {infra_data.get('ram')}% | Label: {infra_data.get('label')}"
        except Exception as e:
            logger.error(f"Infra check error: {e}")

        # 1. Context Retrieval (Text-based)
        if text and len(text) > 3:
            # RAG
            if organization_id:
                try:
                    search_results = await vector_search_service.search(text, organization_id)
                    if search_results:
                        rag_context = "\n".join([
                            f"SOURCE: {r.get('metadata', {}).get('source', 'Neural DB')}\nCONTENT: {r.get('content', '')}"
                            for r in search_results
                        ])
                except Exception as e:
                    logger.error(f"RAG Error: {e}")

            # Notion
            if settings.NOTION_TOKEN:
                try:
                    notion_results = await notion_service.search(text)
                    if notion_results:
                        notion_context = "\n".join([
                            f"[NOTION] {r.get('properties', {}).get('title', {}).get('title', [{}])[0].get('plain_text', 'Untitled') if r.get('object') == 'page' else r.get('title', [{}])[0].get('plain_text', 'DB')}"
                            for r in notion_results[:5]
                        ])
                except Exception as e:
                    logger.error(f"Notion Error: {e}")

        # 1.5 Strategic Reasoning (Mistral)
        strategic_insight = ""
        if rag_context and settings.MISTRAL_API_KEY: 
            try:
                # We use the RAG context to get a strategic direction
                strategic_insight = await mistral_service.get_strategic_insight(text, rag_context)
            except Exception as e:
                logger.error(f"Mistral Error: {e}")

        # 2. Build Multimodal Content
        contents = []
        
        # System Instruction is handled at client level or as part of prompt
        prompt_parts = [AUREON_SYSTEM_PROMPT]
        
        if rag_context:
            prompt_parts.append(f"\n[CONTEXTO RAG]:\n{rag_context}")
        
        if notion_context:
            prompt_parts.append(f"\n[CONTEXTO NOTION]:\n{notion_context}")
            
        if infra_context:
            prompt_parts.append(f"\n[SENSORES INFRAESTRUCTURA]:\n{infra_context}")

        if strategic_insight:
            prompt_parts.append(f"\n[INSIGHT ESTRATÉGICO]:\n{strategic_insight}")

        if context:
            user_name = context.get("userName", "Usuario")
            prompt_parts.append(f"\n[Usuario: {user_name}]")
            
        prompt_parts.append(f"\n[MENSAJE]: {text or '(Analizando archivo adjunto)'}")
        
        contents.append(" ".join(prompt_parts))

        # Handle Attachments (Images/Audio)
        if attachments:
            for att in attachments:
                if att.get("type") == "image":
                    contents.append(types.Part.from_bytes(
                        data=att["data"],
                        mime_type=att.get("mime_type", "image/png")
                    ))
                elif att.get("type") == "audio":
                    contents.append(types.Part.from_bytes(
                        data=att["data"],
                        mime_type=att.get("mime_type", "audio/ogg")
                    ))

        # --- TOOL DEFINITIONS ---
        # We define tools dynamically to guide the model
        tools = [
            # Tool 1: Create Notion Task
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="create_notion_task",
                        description="Creates a new task or page in the user's Notion database. Use this when the user asks to save, remember, or create a task.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "title": types.Schema(type="STRING", description="The title of the task"),
                                "content": types.Schema(type="STRING", description="Details or body of the task")
                            },
                            required=["title"]
                        )
                    ),
                    types.FunctionDeclaration(
                        name="trigger_n8n_workflow",
                        description="Triggers an automation workflow in n8n. Use for sending emails, social media posts, or specific integrations.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "webhook_path": types.Schema(type="STRING", description="The n8n webhook path (e.g., 'send-email', 'social-post')"),
                                "payload_json": types.Schema(type="STRING", description="JSON string with the data to send")
                            },
                            required=["webhook_path"]
                        )
                    )
                ]
            )
        ]

        try:
            client, current_key = self._get_client()
            
            # Generate content with tools
            response = client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=AUREON_SYSTEM_PROMPT,
                    temperature=0.7,
                    tools=tools
                )
            )
            
            # --- FUNCTION CALL HANDLING ---
            function_call = None
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                     if part.function_call:
                         function_call = part.function_call
                         break
            
            if function_call:
                logger.info(f"⚡ Brain: Executing Tool {function_call.name}")
                tool_result = "Tool executed."
                
                if function_call.name == "create_notion_task":
                    dbs = await notion_service.list_databases()
                    if dbs:
                        # MVP: Pick the first usable DB
                        target_db = dbs[0]['id']
                        res = await notion_service.create_page(
                            database_id=target_db,
                            title=function_call.args['title'],
                            content=function_call.args.get('content', '')
                        )
                        if res:
                            tool_result = f"✅ Tarea creada en Notion: {function_call.args['title']}"
                            logger.info(f"Notion task created: {res.get('url')}")
                        else:
                            tool_result = "❌ Error creando tarea en Notion."
                    else:
                        tool_result = "⚠️ No encontré ninguna base de datos en Notion."

                elif function_call.name == "trigger_n8n_workflow":
                    import json as json_lib
                    try:
                         pl = json_lib.loads(function_call.args.get('payload_json', '{}'))
                    except:
                         pl = {"raw": function_call.args.get('payload_json')}
                    
                    res = await backend_n8n_service.trigger_webhook(
                        function_call.args['webhook_path'],
                        pl
                    )
                    tool_result = "✅ Workflow activado." if res.get("status") == "success" else f"❌ Fallo al activar workflow: {res.get('message', res.get('reason', 'Unknown error'))}"

                # Verify if we need to feed this back to the model (Multi-turn)
                # For this MVP, we just return the confirmation as text.
                return {
                    "text": tool_result,  # Simplified flow: Bot replies with tool result
                    "thought_trace": [f"Herramienta {function_call.name} ejecutada", tool_result]
                }

            # Normal Text Response
            answer_text = response.text
            
            return {
                "text": answer_text,
                "thought_trace": [
                    "Percepción sensorial activada", 
                    "Sistemas vitales: " + (infra_context or "En espera"),
                    "Contexto decodificado", 
                    "Sintetizando respuesta"
                ]
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.exception(f"CRITICAL GEMINI ERROR: {e}") # Full stack trace in logs
            
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                logger.warning(f"429 detected on key {current_key[:8]}...")
                hydra_pool.report_failure(current_key)
                if not context.get("_is_retry"):
                    context["_is_retry"] = True
                    return await self.process_query(text, organization_id, context, attachments)

            return {
                "text": f"He tenido un glitch en mi núcleo cognitivo ({type(e).__name__}). He activado protocolo Hydra. Detalles: {str(e)[:50]}...",
                "error": error_msg
            }

brain_service = BrainService()
from app.services.n8n import n8n_service as backend_n8n_service

