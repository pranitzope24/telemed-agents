"""Session management API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime

router = APIRouter()

# In-memory storage for demo (will be replaced with Redis later)
sessions_store = {}


class CreateSessionRequest(BaseModel):
    """Request to create a new session."""
    user_id: Optional[str] = None


class SessionResponse(BaseModel):
    """Session response model."""
    session_id: str
    user_id: Optional[str] = None
    created_at: str
    message_count: int
    status: str


@router.post("/session")
async def create_session(request: CreateSessionRequest) -> SessionResponse:
    """Create a new chat session."""
    session_id = f"session_{uuid.uuid4().hex[:16]}"
    timestamp = datetime.now().isoformat()
    
    sessions_store[session_id] = {
        "session_id": session_id,
        "user_id": request.user_id,
        "created_at": timestamp,
        "messages": [],
        "status": "active"
    }
    
    return SessionResponse(
        session_id=session_id,
        user_id=request.user_id,
        created_at=timestamp,
        message_count=0,
        status="active"
    )


@router.get("/session/{session_id}")
async def get_session(session_id: str) -> SessionResponse:
    """Get session details."""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions_store[session_id]
    
    return SessionResponse(
        session_id=session["session_id"],
        user_id=session.get("user_id"),
        created_at=session["created_at"],
        message_count=len(session.get("messages", [])),
        status=session["status"]
    )


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions_store[session_id]
    
    return {
        "session_id": session_id,
        "status": "deleted",
        "message": "Session deleted successfully"
    }
