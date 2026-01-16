import os
import httpx
from typing import List, Dict, Any, Optional
from loguru import logger

class MistralService:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.api_url = "https://api.mistral.ai/v1/chat/completions"

    async def get_strategic_insight(self, prompt: str, context: str = "") -> str:
        """
        Uses Mistral to provide a strategic, high-level reasoning based on context.
        """
        if not self.api_key:
            logger.warning("Mistral API Key not found. Falling back to internal reasoning.")
            return "Strategist note: Mistral integration pending API key."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "system", "content": "Eres el Estratega de Elevate OS. Tu misión es analizar el contexto RAG y proporcionar una dirección clara y ejecutiva."},
            {"role": "user", "content": f"Contexto RAG: {context}\n\nPregunta: {prompt}"}
        ]

        payload = {
            "model": "mistral-large-latest",
            "messages": messages,
            "temperature": 0.3
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling Mistral API: {e}")
            return f"Strategic error: {str(e)}"

mistral_service = MistralService()
