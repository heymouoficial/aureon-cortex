"""
Hydra Pool v2.0 - Intelligent API Key Management
Exponential backoff, fail tracking, emergency reset
"""
import os
import json
import time
from typing import List, Optional
from loguru import logger


class HydraPool:
    """
    Gestor inteligente de llaves API con rotación agresiva 
    ante errores 429 (Rate Limit).
    """
    _instance = None

    def __init__(self):
        self.keys: List[dict] = []
        self._load_keys()
    
    def _load_keys(self):
        """Load keys from environment."""
        pool_json = os.getenv("VITE_GEMINI_KEY_POOL", "[]")
        
        # Clean up potential quoting issues from .env files
        if pool_json.startswith("'") and pool_json.endswith("'"):
            pool_json = pool_json[1:-1]
        elif pool_json.startswith('"') and pool_json.endswith('"'):
            pool_json = pool_json[1:-1]
            
        try:
            raw_keys = json.loads(pool_json)
            self.keys = [{"key": k, "cooldown": 0, "fails": 0} for k in raw_keys]
            logger.info(f"✅ Hydra: Loaded {len(self.keys)} keys from pool.")
        except Exception as e:
            logger.error(f"Hydra: Error parsing GEMINI_KEY_POOL: {e}. Raw: {pool_json[:20]}...")
            self.keys = []
        
        # Add the primary key if not in pool
        primary_key = os.getenv("GEMINI_API_KEY")
        if primary_key:
            primary_key = primary_key.strip("'").strip('"')
            if not any(k["key"] == primary_key for k in self.keys):
                self.keys.insert(0, {"key": primary_key, "cooldown": 0, "fails": 0})
                logger.info("🔑 Hydra: Added primary GEMINI_API_KEY to pool.")
            
        if not self.keys:
            logger.warning("Hydra: No API keys found in pool or GEMINI_API_KEY!")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = HydraPool()
        return cls._instance

    def get_active_key(self) -> Optional[str]:
        """Returns the next available key that is not in cooldown."""
        if not self.keys:
            return None
        
        now = time.time()
        
        # Filter keys that are not in cooldown
        available = [k for k in self.keys if k["cooldown"] < now]
        
        if not available:
            # Emergency reset - all keys in cooldown
            logger.error("🚨 Hydra: All keys are in cooldown! Emergency reset initiated.")
            for k in self.keys:
                k["cooldown"] = 0
                k["fails"] = max(0, k["fails"] - 1)  # Reduce penalty
            available = self.keys

        # Prioritize keys with fewer failures
        available.sort(key=lambda x: x["fails"])
        selected = available[0]["key"]
        return selected

    def report_failure(self, key: str, status_code: int = 429):
        """Marks a key as failed with exponential backoff."""
        for k in self.keys:
            if k["key"] == key:
                k["fails"] += 1
                
                if status_code == 429:
                    # Exponential backoff: 30s, 60s, 90s, etc. (reduced for faster rotation)
                    wait_time = 30 * k["fails"]
                    k["cooldown"] = time.time() + wait_time
                    logger.warning(f"⚠️ Hydra: Key {key[:8]}... 429 error. Cooldown for {wait_time}s")
                else:
                    # Other errors get shorter cooldown
                    k["cooldown"] = time.time() + 30
                    logger.warning(f"⚠️ Hydra: Key {key[:8]}... error {status_code}. Cooldown for 30s")
                
                break

    def get_status(self) -> dict:
        now = time.time()
        return {
            "total_keys": len(self.keys),
            "available_keys": len([k for k in self.keys if k["cooldown"] < now]),
            "blocked_keys": len([k for k in self.keys if k["cooldown"] >= now]),
            "keys_detail": [
                {
                    "key_prefix": k["key"][:8] + "...",
                    "fails": k["fails"],
                    "in_cooldown": k["cooldown"] >= now,
                    "cooldown_remaining": max(0, int(k["cooldown"] - now))
                }
                for k in self.keys
            ]
        }


hydra_pool = HydraPool.get_instance()
