from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse, HTMLResponse, RedirectResponse
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import os
import json
from fastapi import Request

from app.services.telegram_bot import init_telegram_bot, set_telegram_webhook, process_webhook_update, stop_telegram_bot
from app.core.config import get_settings

settings = get_settings()

# Lifespan Context Manager (MUST be defined before app)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🧠 Aureon Cortex is awakening...")
    
    # Diagnostic: Check API Keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    key_pool = os.getenv("VITE_GEMINI_KEY_POOL", "[]")
    try:
        pool_count = len(json.loads(key_pool))
    except:
        pool_count = 0
    
    logger.info(f"🔑 API Status: Primary Key: {'PRESENT' if gemini_key else 'MISSING'} | Pool Keys: {pool_count}")
    
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
    description="The Cognitive Operating System Backend for Elevate OS - Multi-Agent Architecture",
    version="1.0.0-alpha",
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

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Aureon Cortex | Neural Hub</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Inter:wght@300;500&display=swap" rel="stylesheet">
        <style>
            :root {
                --obsidian: #050505;
                --lumina: #00f2ff;
                --glass: rgba(255, 255, 255, 0.03);
            }
            body, html {
                margin: 0; padding: 0; width: 100%; height: 100%;
                background: var(--obsidian);
                color: white;
                font-family: 'Outfit', sans-serif;
                display: flex; justify-content: center; align-items: center;
                overflow: hidden;
            }
            .background {
                position: absolute; width: 100%; height: 100%;
                background: radial-gradient(circle at center, #001a1d 0%, var(--obsidian) 70%);
                z-index: 1;
            }
            .blob {
                position: absolute; width: 500px; height: 500px;
                background: var(--lumina);
                filter: blur(150px);
                opacity: 0.1;
                border-radius: 50%;
                animation: float 20s infinite alternate;
                z-index: 2;
            }
            @keyframes float {
                from { transform: translate(-10%, -10%) scale(1); }
                to { transform: translate(10%, 10%) scale(1.1); }
            }
            .content {
                position: relative; z-index: 10;
                text-align: center;
                background: var(--glass);
                backdrop-filter: blur(20px);
                padding: 3rem;
                border-radius: 2rem;
                border: 1px solid rgba(0, 242, 255, 0.2);
                box-shadow: 0 0 50px rgba(0, 0, 0, 0.5);
            }
            .status-dot {
                width: 12px; height: 12px;
                background: var(--lumina);
                border-radius: 50%;
                display: inline-block;
                margin-right: 10px;
                box-shadow: 0 0 15px var(--lumina);
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { opacity: 0.5; transform: scale(0.8); }
                50% { opacity: 1; transform: scale(1.2); }
                100% { opacity: 0.5; transform: scale(0.8); }
            }
            h1 { font-weight: 300; letter-spacing: 5px; text-transform: uppercase; margin-bottom: 0.5rem; font-size: 1.2rem; color: #888; }
            .version { font-family: 'Inter', sans-serif; font-size: 0.8rem; color: #444; margin-top: 1rem; }
            .main-status { font-size: 2.5rem; font-weight: 600; margin: 1rem 0; background: linear-gradient(90deg, #fff, var(--lumina)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        </style>
    </head>
    <body>
        <div class="background"></div>
        <div class="blob"></div>
        <div class="content">
            <h1>Aureon Cortex Hub</h1>
            <div class="main-status"><span class="status-dot"></span>Operational</div>
            <p style="color: #666; font-style: italic;">"Intelligence is the ability to adapt to change."</p>
            <div class="version">Agnostic Intelligence Engine v0.1.0-alpha</div>
        </div>
    </body>
    </html>
    """

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

# --- TEMPORARY GOOGLE AUTH FLOW ---
from google_auth_oauthlib.flow import Flow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

@app.get("/google/auth")
async def google_auth():
    """Initiate Google OAuth2 flow."""
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    
    if not client_id or not client_secret:
        return {"error": "GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not configured"}
        
    redirect_uri = f"{settings.DOMAIN}/google/callback" if settings.DOMAIN else "https://cortex.elevatmarketing.com/google/callback"
    
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES
        )
        flow.redirect_uri = redirect_uri
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        logger.info(f"🔗 Google Auth URL generated: {authorization_url}")
        return RedirectResponse(authorization_url)
    except Exception as e:
        logger.error(f"❌ Google OAuth Error: {e}")
        return {"error": f"Failed to generate auth URL: {str(e)}"}

@app.get("/google/callback")
async def google_callback(code: str):
    """Handle Google OAuth2 callback and return Refresh Token."""
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    redirect_uri = f"{settings.DOMAIN}/google/callback" if settings.DOMAIN else "https://cortex.elevatmarketing.com/google/callback"
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = redirect_uri
    
    flow.fetch_token(code=code)
    creds = flow.credentials
    
    html_content = f"""
    <html>
        <head><title>Aureon Google Auth</title></head>
        <body style="font-family: sans-serif; padding: 40px; text-align: center; background: #0f172a; color: white;">
            <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #334155; border-radius: 12px; background: #1e293b;">
                <h1 style="color: #38bdf8;">✅ Google Auth Success</h1>
                <p>Copy the Refresh Token below and add it to your <b>Dokploy ENVIRONMENT VARIABLES</b>.</p>
                <div style="background: #000; padding: 15px; border-radius: 8px; font-family: monospace; word-break: break-all; margin: 20px 0; border: 1px solid #334155;">
                    {creds.refresh_token}
                </div>
                <p style="color: #94a3b8; font-size: 0.9em;">After saving the variable in Dokploy, delete these routes for security.</p>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
