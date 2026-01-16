import httpx
from typing import Dict, Any, Optional
from app.core.config import get_settings
from loguru import logger

settings = get_settings()

class N8nService:
    def __init__(self):
        self.base_url = settings.N8N_WEBHOOK_URL
        self.api_key = settings.N8N_API_KEY # Optional, for secured webhooks

    async def trigger_webhook(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Triggers a generic n8n webhook.
        
        Args:
            action: A string identifier for the action (e.g., "send_whatsapp", "create_notion_task").
                    This maps to the 'route' or 'type' expected by the n8n workflow.
            payload: The data dictionary to send.
        """
        if not self.base_url:
            logger.warning("N8N_WEBHOOK_URL not set. Action skipped.")
            return {"status": "skipped", "reason": "No URL configured"}

        # Construct the full URL. 
        # Strategy: We assume a single entry point (Router) in n8n, 
        # or we could append the action to the URL if using different webhooks.
        # For this implementation, we'll send the action inside the body to a central webhook.
        
        full_payload = {
            "action": action,
            "data": payload,
            "source": "cortex",
            "auth": self.api_key
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json=full_payload,
                    timeout=10.0
                )
                
                if response.status_code >= 200 and response.status_code < 300:
                    logger.info(f"n8n Triggered: {action}")
                    return {"status": "success", "n8n_response": response.json() if response.text else "ok"}
                else:
                    logger.error(f"n8n Error {response.status_code}: {response.text}")
                    return {"status": "error", "code": response.status_code}
                    
        except Exception as e:
            logger.error(f"n8n Connection Failed: {e}")
            return {"status": "error", "message": str(e)}

n8n_service = N8nService()
