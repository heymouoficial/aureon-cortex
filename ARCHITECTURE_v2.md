# ElevatOS v2.0: Arquitectura de Contratos de Datos

## 1. El Núcleo: FastAPI + Pydantic (El Cerebro)

- **Orquestador:** FastAPI en VPS Hostinger.
- **Contratos de Datos:** Pydantic define esquemas estrictos para:
  - **Inputs:** Webhooks de Telegram/WhatsApp.
  - **Outputs:** Acciones hacia Notion y Google Workspace.
- **Performance:**
  - `uvloop` + `httptools` para event loop.
  - `ORJSONResponse` para serialización de alta velocidad (20-50% más rápido).
- **Estrategia:** Validación única en frontera. Estructuras ligeras internamente.

## 2. Integración MCP (Model Context Protocol)

- **Filosofía:** Eliminación de fricción. Aureon debe "ver" los datos, no pedir que se los traigan.
- **Hub MCP:** Servidores en Node.js/Python en VPS.
- **Tipado:** Cada herramienta MCP usa esquemas Pydantic para generar su JSON-RPC dinámicamente.

## 3. Sincronización Híbrida (Supabase <-> Notion)

- **Fuente de Verdad:** Supabase (PostgreSQL + pgvector).
- **Interfaz Humana:** Notion.
- **Mecanismo:**
  - **Rápido (<150ms):** Edge Functions (Supabase) -> Notion API para cambios críticos.
  - **Integridad (99.98%):** n8n Workflow (Self-hosted) reconcilia discrepancias cada 5 min.

## 4. Consciencia y Memoria (RAG)

- **MemoriesDB:** `pgvector` con embeddings de 1536 dimensiones (text-embedding-3-small o gemini-embedding).
- **Vibe Engineering:** Capa de post-procesamiento para ajustar tono (Empatía/Autoridad) según el usuario y contexto.

## 5. Infraestructura (Hostinger VPS)

- **Contención:** Docker para aislar servicios (FastAPI, n8n, MCP Hub).
- **Seguridad:** RBAC (Clerk/Supabase Auth) y Secretos vía Variables de Entorno (NO hardcoded).

## 6. Interfaces Líquidas

- **Telegram:** Webhook -> FastAPI -> Pydantic -> MCP -> Respuesta (Vibe Checked).
- **Multimedia:** Whisper para voz, Vision para imágenes.
