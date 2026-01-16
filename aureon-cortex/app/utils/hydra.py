import os
import json
import time
from typing import List, Optional
from loguru import logger

class HydraPool:
    _instance = None

    def __init__(self):
        self.keys: List[str] = []
        self.current_index = 0
        self.last_failure: dict[str, float] = {}
        self.cooldown_period = 60  # Shortened for rapid failover testing on free tier
        
        # Load keys from environment
        pool_json = os.getenv("VITE_GEMINI_KEY_POOL", "[]")
        try:
            self.keys = json.loads(pool_json)
        except Exception as e:
            logger.error(f"Hydra: Error parsing GEMINI_KEY_POOL: {e}")
        
        # Add the primary key if not in pool
        primary_key = os.getenv("GEMINI_API_KEY")
        if primary_key and primary_key not in self.keys:
            self.keys.insert(0, primary_key)
            
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
        
        start_index = self.current_index
        while True:
            key = self.keys[self.current_index]
            
            # Check if key is in cooldown
            if key in self.last_failure:
                if time.time() - self.last_failure[key] < self.cooldown_period:
                    # Move to next key
                    self.current_index = (self.current_index + 1) % len(self.keys)
                    if self.current_index == start_index:
                        logger.error("Hydra: ALL KEYS ARE IN COOLDOWN!")
                        return None
                    continue
            
            return key

    def report_failure(self, key: str):
        """Marks a key as failed and triggers rotation."""
        if key in self.keys:
            logger.warning(f"Hydra: Key {key[:8]}... reported error 429. Entering cooldown.")
            self.last_failure[key] = time.time()
            # Advance index immediately
            self.current_index = (self.current_index + 1) % len(self.keys)

    def get_status(self) -> dict:
        return {
            "total_keys": len(self.keys),
            "blocked_keys": len([k for k in self.last_failure if time.time() - self.last_failure[k] < self.cooldown_period]),
            "current_index": self.current_index
        }

hydra_pool = HydraPool.get_instance()
