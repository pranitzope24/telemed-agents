"""Simple Redis wrapper for short-term memory."""

import json
from typing import Any, Dict, Optional

from app.utils.logger import get_logger

logger = get_logger()


class RedisMemory:
    """Redis wrapper with in-memory fallback."""
    
    def __init__(self):
        """Initialize Redis client with fallback to in-memory dict."""
        self.redis_client = None
        self.memory_store: Dict[str, str] = {}  # Fallback in-memory storage
        self.use_redis = False
        
        try:
            import redis
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True,
                socket_connect_timeout=2
            )
            # Test connection
            self.redis_client.ping()
            self.use_redis = True
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory storage: {e}")
            self.use_redis = False
    
    def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Store value with TTL (time to live in seconds)."""
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.setex(key, ttl, value)
            else:
                # In-memory fallback (no TTL support for simplicity)
                self.memory_store[key] = value
            return True
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        try:
            if self.use_redis and self.redis_client:
                return self.redis_client.get(key)
            else:
                return self.memory_store.get(key)
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete key."""
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_store.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            if self.use_redis and self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                return key in self.memory_store
        except Exception as e:
            logger.error(f"Error checking key {key}: {e}")
            return False
    
    def ping(self) -> bool:
        """Check if storage is available."""
        try:
            if self.use_redis and self.redis_client:
                return self.redis_client.ping()
            else:
                return True  # In-memory is always available
        except Exception:
            return False


# Singleton instance
redis_memory = RedisMemory()
