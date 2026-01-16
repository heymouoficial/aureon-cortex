from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import os
from fastapi import Request

from app.services.telegram_bot import init_telegram_bot, set_telegram_webhook, process_webhook_update, stop_telegram_bot
from app.core.config import get_settings

settings = get_settings()

# Lifespan Context Manager (MUST be defined before app)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🧠 Aureon Cortex is awakening...")
    
    # Initialize Telegram Bot
    bot_app = await init_telegram_bot()
    app.state.telegram_bot_app = bot_app
    
    if bot_app:
        await bot_app.start()
        if settings.DOMAIN:
            webhook_url = f"{settings.DOMAIN}/telegram/webhook"
            await set_telegram_webhook(bot_app, webhook_url)
        else:
            logger.warning("⚠️ DOMAIN not set in .env.cortex. Telegram Webhook NOT configured.")

    # Startup MCP Hub
    try:
        from app.services.mcp_client import mcp_client
        logger.info("🔌 Initializing MCP Hub connections...")
        await mcp_client.initialize_servers()
    except Exception as e:
        logger.error(f"❌ Failed to initialize MCP Hub: {e}")

    yield
    # Shutdown
    logger.info("💤 Aureon Cortex is sleeping...")
    
    # Cleanup MCP
    try:
        from app.services.mcp_client import mcp_client
        mcp_client.cleanup()
    except Exception as e:
        logger.error(f"Error cleaning up MCP: {e}")

    if app.state.telegram_bot_app:
        await stop_telegram_bot(app.state.telegram_bot_app)

# App Definition
app = FastAPI(
    title="Aureon Cortex",
    description="The Cognitive Operating System Backend for Portality",
    version="0.1.0-alpha",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    default_response_class=ORJSONResponse
)

# Instrument Prometheus
Instrumentator().instrument(app).expose(app)

# CORS Configuration (Permissive for Staging/Dev)
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://portality.elevatmarketing.com",
    "https://n8n.elevatmarketing.com",
    "*", # TODO: Restrict in Production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "system": "Aureon Cortex",
        "status": "operational",
        "version": "0.1.0-alpha",
        "quote": "Intelligence is the ability to adapt to change."
    }

@app.get("/health")
async def health_check():
    """
    Health check for VPS monitoring and Docker.
    """
    return {"status": "ok", "service": "cortex"}

# Include Routers
from app.api.v1.api import api_router
app.include_router(api_router, prefix="/api/v1")

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram updates."""
    bot_app = request.app.state.telegram_bot_app
    if not bot_app:
        return {"status": "ignored", "reason": "bot_not_initialized"}
        
    data = await request.json()
    await process_webhook_update(bot_app, data)
    return {"status": "ok"}
