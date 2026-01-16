# Aureon Cortex - Changelog

All notable changes to this project will be documented in this file.

## [1.0.0-alpha] - 2026-01-16

### 🧠 Multi-Agent Architecture

- **Aureon Cortex** - Polímata Enrutador (Orchestrator)
- **Lumina** ✨ - Estrategia e Insights (Mistral)
- **Nux** ⚡ - Prospección y Ventas (Groq)
- **Memorís** 📚 - RAG Guardian (Gemini + Supabase)
- **Vox** 🎙️ - Comunicación (Gemini 2.0 Flash)

### Infrastructure

- Dockerfile optimized for Dokploy/Traefik (port 80)
- Edge-TTS for voice responses
- HydraPool for Gemini API key rotation

### Integrations

- Telegram Bot (`@aureon_elevatbot`)
- Notion (bidirectional)
- n8n webhooks
- Supabase RAG (pgvector)
- Hostinger VPS monitoring

### API Endpoints

- `/api/v1/synapse` - Main intelligence endpoint
- `/api/v1/whatsapp/webhook` - WhatsApp integration
- `/health` - Healthcheck
