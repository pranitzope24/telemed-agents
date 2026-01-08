"""Application settings and environment configuration."""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ===== LLM Configuration =====
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    default_llm_provider: str = Field(default="openai", env="DEFAULT_LLM_PROVIDER")
    default_model: str = Field(default="gpt-4o-mini", env="DEFAULT_MODEL")
    
    # ===== Backend API Configuration =====
    backend_api_url: str = Field(default="http://localhost:8000", env="BACKEND_API_URL")
    backend_api_token: str = Field(default="", env="BACKEND_API_TOKEN")
    
    # ===== Redis Configuration =====
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")
    redis_url: str = Field(default="", env="REDIS_URL")
    
    # ===== Application Configuration =====
    app_env: str = Field(default="development", env="APP_ENV")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    session_ttl: int = Field(default=3600, env="SESSION_TTL")
    max_turns_in_memory: int = Field(default=10, env="MAX_TURNS_IN_MEMORY")
    
    # ===== Retry Configuration =====
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay_base: float = Field(default=1.0, env="RETRY_DELAY_BASE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Convenience function for quick access
def get_env(key: str, default: str = "") -> str:
    """Get environment variable with fallback."""
    return os.getenv(key, default)
