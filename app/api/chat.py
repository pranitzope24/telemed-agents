"""Chat API endpoint with session persistence."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.state.graph_state import SessionState
from app.memory.session_memory import save_session_state, load_session_state
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
    message_count: int
    timestamp: str


@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint with session persistence."""
    
    # ===== 1. Load or create session =====
    if request.session_id:
        state = load_session_state(request.session_id)
        if state:
            print(f"📂 Loaded existing session: {request.session_id}")
        else:
            print(f"⚠️  Session {request.session_id} not found, creating new one")
            state = SessionState(session_id=request.session_id)
    else:
        session_id = f"session_{uuid.uuid4().hex[:16]}"
        state = SessionState(session_id=session_id)
        print(f"✨ Created new session: {session_id}")
    
    # ===== 2. Add user message =====
    state.add_message("user", request.message)
    
    # ===== 3. Mock intent classification =====
    message_lower = request.message.lower()
    
    if any(word in message_lower for word in ["pain", "hurt", "sick", "symptom", "fever", "headache", "nausea"]):
        state.current_intent = "symptom"
        state.risk_level = "medium"
        response_text = "I understand you're experiencing symptoms. Can you tell me more about when they started and how severe they are?"
    
    elif any(word in message_lower for word in ["dosha", "ayurveda", "vata", "pitta", "kapha", "constitution"]):
        state.current_intent = "dosha"
        response_text = "I can help you discover your Ayurvedic constitution. Let me ask you a few questions about your body type and lifestyle."
    
    elif any(word in message_lower for word in ["doctor", "appointment", "book", "consultation", "specialist"]):
        state.current_intent = "doctor"
        response_text = "I can help you find and book a doctor. What specialty are you looking for, or would you like me to suggest based on your symptoms?"
    
    elif any(word in message_lower for word in ["prescription", "medicine", "medication", "drug", "dosage"]):
        state.current_intent = "prescription"
        response_text = "I can provide prescription information. Please note that a licensed doctor must review and approve any prescriptions."
    
    elif any(word in message_lower for word in ["emergency", "urgent", "chest pain", "bleeding", "can't breathe", "unconscious"]):
        state.current_intent = "emergency"
        state.risk_level = "emergency"
        state.add_safety_flag("emergency_keywords_detected")
        response_text = "⚠️ This sounds urgent. If you're experiencing a medical emergency, please call emergency services immediately or go to the nearest emergency room."
    
    else:
        state.current_intent = "general"
        response_text = (
            "Hello! I'm your medical assistant. I can help you with:\n\n"
            "• Symptom analysis and triage\n"
            "• Ayurvedic dosha assessment\n"
            "• Finding and booking doctors\n"
            "• Prescription information\n"
            "• Progress tracking\n\n"
            "How can I assist you today?"
        )
    
    # ===== 4. Add assistant response =====
    state.add_message("assistant", response_text)
    
    # ===== 5. Save state to memory =====
    save_success = save_session_state(state)
    if save_success:
        print(f"💾 Saved session state: {state.session_id}")
    else:
        print(f"⚠️  Failed to save session state: {state.session_id}")
    
    # ===== 6. Return response =====
    return ChatResponse(
        response=response_text,
        session_id=state.session_id,
        intent=state.current_intent,
        message_count=state.message_count,
        timestamp=datetime.now().isoformat()
    )
