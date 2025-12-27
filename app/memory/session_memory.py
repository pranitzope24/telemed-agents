"""Session memory helpers for easy state management."""

from typing import Optional
from app.memory.short_term import redis_memory
from app.state.graph_state import SessionState


def save_session_state(state: SessionState, ttl: int = 3600) -> bool:
    """Save session state to memory.
    
    Args:
        state: SessionState object to save
        ttl: Time to live in seconds (default: 1 hour)
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        key = f"session:{state.session_id}:state"
        json_data = state.model_dump_json()
        return redis_memory.set(key, json_data, ttl)
    except Exception as e:
        print(f"Error saving session {state.session_id}: {e}")
        return False


def load_session_state(session_id: str) -> Optional[SessionState]:
    """Load session state from memory.
    
    Args:
        session_id: Session identifier
        
    Returns:
        SessionState object if found, None otherwise
    """
    try:
        key = f"session:{session_id}:state"
        json_data = redis_memory.get(key)
        
        if json_data:
            return SessionState.model_validate_json(json_data)
        return None
    except Exception as e:
        print(f"Error loading session {session_id}: {e}")
        return None


def delete_session_state(session_id: str) -> bool:
    """Delete session state from memory.
    
    Args:
        session_id: Session identifier
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        key = f"session:{session_id}:state"
        return redis_memory.delete(key)
    except Exception as e:
        print(f"Error deleting session {session_id}: {e}")
        return False


def session_exists(session_id: str) -> bool:
    """Check if session exists in memory.
    
    Args:
        session_id: Session identifier
        
    Returns:
        True if session exists, False otherwise
    """
    try:
        key = f"session:{session_id}:state"
        return redis_memory.exists(key)
    except Exception as e:
        print(f"Error checking session {session_id}: {e}")
        return False
