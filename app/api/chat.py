"""Chat API endpoint with mock responses."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    intent: Optional[str] = None
    timestamp: str


@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint with mock responses."""
    
    # Mock intent classification based on keywords
    message_lower = request.message.lower()
    intent = "general"
    
    if any(word in message_lower for word in ["pain", "hurt", "sick", "symptom", "fever", "headache"]):
        intent = "symptom"
        response_text = "I understand you're experiencing some symptoms. Can you describe them in more detail? For example, when did they start and how severe are they?"
    elif any(word in message_lower for word in ["dosha", "ayurveda", "vata", "pitta", "kapha"]):
        intent = "dosha"
        response_text = "I can help you understand your Ayurvedic constitution. Let me ask you a few questions about your body type, digestion, and lifestyle."
    elif any(word in message_lower for word in ["doctor", "appointment", "book", "consultation"]):
        intent = "doctor"
        response_text = "I can help you find and book a doctor. What specialty are you looking for, or would you like me to suggest based on your symptoms?"
    elif any(word in message_lower for word in ["prescription", "medicine", "medication", "drug"]):
        intent = "prescription"
        response_text = "I can help with prescription information. Please note that I can provide information, but a licensed doctor must approve any prescriptions."
    elif any(word in message_lower for word in ["emergency", "urgent", "chest pain", "bleeding", "can't breathe"]):
        intent = "emergency"
        response_text = "⚠️ This sounds like it may require immediate medical attention. If you're experiencing a medical emergency, please call emergency services or go to the nearest emergency room immediately."
    else:
        response_text = (
            "Hello! I'm your medical assistant. I can help you with:\n\n"
            "• Symptom analysis and triage\n"
            "• Ayurvedic dosha assessment\n"
            "• Finding and booking doctors\n"
            "• Prescription information\n"
            "• Progress tracking\n\n"
            "How can I assist you today?"
        )
    
    return ChatResponse(
        response=response_text,
        intent=intent,
        timestamp=datetime.now().isoformat()
    )
