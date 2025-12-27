"""Base state class with serialization support."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict


class BaseState(BaseModel):
    """Base state class with common functionality."""
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True  # Validate on attribute assignment
        extra = 'forbid'  # Don't allow extra fields
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()
        return self
