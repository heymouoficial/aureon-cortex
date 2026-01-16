from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Core
    APP_ENV: str = "development"
    PORT: int = 8000
    
    # Supabase (The Memory)
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str | None = None # Full Access (Backend)
    SUPABASE_ANON_KEY: str | None = None # Public/Client Access
    
    # Intelligence
    GEMINI_API_KEY: str | None = None
    VITE_GEMINI_KEY_POOL: str = "[]"
    OPENAI_API_KEY: str | None = None
    MISTRAL_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    TELEGRAM_BOT_TOKEN: str | None = None
    
    # WhatsApp
    WHATSAPP_VERIFY_TOKEN: str = "Aureon_Secret_2026"
    WHATSAPP_API_TOKEN: str | None = None
    WHATSAPP_PHONE_ID: str | None = None
    
    # Connectivity
    N8N_WEBHOOK_URL: str | None = None # Base URL for webhooks
    N8N_API_KEY: str | None = None # API Key for management
    
    # Google Workspace
    GOOGLE_APPLICATION_CREDENTIALS: str | None = "/app/aureon-google-creds.json"
    
    # Notion
    NOTION_TOKEN: str | None = None
    
    # Infrastructure
    HOSTINGER_API_KEY: str | None = None
    VITE_HOSTINGER_API_KEY: str | None = None # Legacy support
    
    # New MCP Integrations
    VERCEL_API_TOKEN: str | None = None
    TESTSPRITE_API_KEY: str | None = None
    DEEPSEEK_API_KEY: str | None = None
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REFRESH_TOKEN: str | None = None

    # Webhook Domain (Cloudflare/VPS IP)
    DOMAIN: str | None = None
    
    model_config = SettingsConfigDict(env_file=".env.cortex", env_file_encoding="utf-8", extra="ignore")

    def get_mcp_config(self) -> dict:
        import json
        import os
        from pathlib import Path
        
        config_path = Path(__file__).parent / "mcp_config.json"
        if not config_path.exists():
            return {"mcpServers": {}}
            
        with open(config_path, "r") as f:
            config = json.load(f)
            
        # Substitute environment variables
        env_vars = self.model_dump()
        for server in config.get("mcpServers", {}).values():
            if "env" in server:
                for key, value in server["env"].items():
                    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                        env_var_name = value[2:-1]
                        # Map specific config keys to env vars if names differ
                        if env_var_name == "SUPABASE_KEY":
                            server["env"][key] = self.SUPABASE_SERVICE_ROLE_KEY or ""
                        elif env_var_name == "NOTION_TOKEN":
                             server["env"][key] = self.NOTION_TOKEN
                        else:
                            # Generic lookup in settings
                            server["env"][key] = str(getattr(self, env_var_name, ""))
                            
        return config

@lru_cache()
def get_settings():
    return Settings()
