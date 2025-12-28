"""Backend API client configuration."""

from typing import Dict, Optional
import httpx
from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger()


class BackendAPIConfig:
    """Configuration for backend API calls."""
    
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.backend_api_url.rstrip('/')
        # Hardcoded token for testing - replace with your actual token
        self.api_token = "your_hardcoded_token_here"  # TODO: Move to .env
        self.timeout = 30.0
        self.max_retries = settings.max_retries
        self.retry_delay_base = settings.retry_delay_base
    
    def get_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        
        return headers
    
    def get_client(self, timeout: Optional[float] = None) -> httpx.AsyncClient:
        """Get configured async HTTP client.
        
        Args:
            timeout: Optional custom timeout (defaults to 30s)
            
        Returns:
            Configured AsyncClient instance
        """
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.get_headers(),
            timeout=timeout or self.timeout,
            follow_redirects=True
        )


# Global instance
_api_config: Optional[BackendAPIConfig] = None


def get_api_config() -> BackendAPIConfig:
    """Get or create API config singleton."""
    global _api_config
    if _api_config is None:
        _api_config = BackendAPIConfig()
    return _api_config
