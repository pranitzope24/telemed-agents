"""Chat API endpoint with supervisor integration."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.state.graph_state import SessionState
from app.memory.session_memory import save_session_state, load_session_state
from app.supervisor.supervisor_graph import run_supervisor
import uuid

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    session_id: str
    intent: Optional[str] = None
    risk_level: Optional[str] = None
    active_graph: Optional[str] = None
    message_count: int
    timestamp: str
    metadata: Dict[str, Any] = {}
    warning: Optional[str] = None  # Emergency warning message


@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint with supervisor integration."""
    
    # ===== 1. Load or create session =====
    if request.session_id:
        state = load_session_state(request.session_id)
        if state:
            print(f"\n📂 Loaded existing session: {request.session_id}")
        else:
            print(f"\n⚠️  Session {request.session_id} not found, creating new one")
            state = SessionState(session_id=request.session_id)
    else:
        session_id = f"session_{uuid.uuid4().hex[:16]}"
        state = SessionState(session_id=session_id)
        print(f"\n✨ Created new session: {session_id}")
    
    # ===== 2. Add user message =====
    state.add_message("user", request.message)
    print(f"💬 User message added: {request.message[:50]}...")
    
    # ===== 3. Run supervisor for classification and routing =====
    try:
        supervisor_result = await run_supervisor(request.message, state)
        
        response_text = supervisor_result["response"]
        
        # ===== 4. Add assistant response =====
        state.add_message("assistant", response_text)
        
        # ===== 5. Save state to memory =====
        save_success = save_session_state(state)
        if save_success:
            print(f"\n💾 Saved session state: {state.session_id}")
        else:
            print(f"\n⚠️  Failed to save session state: {state.session_id}")
        
        # ===== 6. Prepare emergency warning if needed =====
        warning_message = None
        if state.risk_level == "emergency":
            warning_message = (
                "⚠️ EMERGENCY DETECTED: This appears to be a medical emergency. "
                "Please call emergency services (911) or go to the nearest emergency room immediately. "
                "Do not rely on this chatbot for emergency medical care."
            )
            print(f"\n🚨 Emergency warning issued for session {state.session_id}")
        
        # ===== 7. Return response with metadata =====
        return ChatResponse(
            response=response_text,
            session_id=state.session_id,
            intent=state.current_intent,
            risk_level=state.risk_level,
            active_graph=state.active_graph,
            message_count=state.message_count,
            timestamp=datetime.now().isoformat(),
            metadata=supervisor_result.get("metadata", {}),
            warning=warning_message
        )
    
    except Exception as e:
        print(f"\n❌ Error in supervisor: {e}")
        # Fallback response
        response_text = (
            "I apologize, but I'm having trouble processing your request. "
            "Please try again or contact support if the issue persists."
        )
        state.add_message("assistant", response_text)
        save_session_state(state)
        
        return ChatResponse(
            response=response_text,
            session_id=state.session_id,
            intent="general",
            risk_level="low",
            active_graph=None,
            message_count=state.message_count,
            timestamp=datetime.now().isoformat(),
            metadata={"error": str(e)}
        )
