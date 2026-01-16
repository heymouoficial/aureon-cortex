import httpx
from typing import Dict, Any
from app.core.config import get_settings
from loguru import logger

settings = get_settings()

class HostingerService:
    def __init__(self):
        self.api_key = settings.VITE_HOSTINGER_API_KEY
        self.base_url = "https://developers.hostinger.com/api/vps/v1"

    async def get_vps_status(self) -> Dict[str, Any]:
        """Fetch VPS health from Hostinger API."""
        if not self.api_key:
            return {"status": "unknown", "message": "Hostinger API Key missing"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/virtual-machines",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Accept": "application/json"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # We assume the first VM is the production one for Multiversa
                    vm = data.get("data", [{}])[0]
                    return {
                        "status": "online" if vm.get("status") == "running" else "warning",
                        "cpu": vm.get("metrics", {}).get("cpu", {}).get("usage", 0),
                        "ram": vm.get("metrics", {}).get("memory", {}).get("usage", 0),
                        "disk": vm.get("metrics", {}).get("disk", {}).get("usage", 0),
                        "label": vm.get("name", "Multiversa-VPS")
                    }
                else:
                    logger.error(f"Hostinger API Error: {response.status_code} - {response.text}")
                    return {"status": "error", "message": f"API returned {response.status_code}"}
        except Exception as e:
            logger.error(f"Hostinger Service Exception: {e}")
            return {"status": "offline", "error": str(e)}

infrastructure_service = HostingerService()
