"""Intent classification for routing."""

import json
from typing import Any, Dict, List

from app.config.llm import LLMConfig
from app.constants.openai_constants import OpenaiModels
from app.state.graph_state import Message
from app.supervisor.constants import INTENTS
from app.utils.logger import get_logger

logger = get_logger()


INTENT_PROMPT = """You are an AI assistant that classifies user intent for a medical telemedicine chatbot.

Available Intents:
- symptom: User reporting symptoms or health concerns
- dosha: User asking about Ayurvedic constitution/prakriti
- doctor: User wants to find or book a doctor
- prescription: User asking about medications or prescriptions
- progress: User tracking progress or follow-up
- emergency: Urgent medical emergency
- general: General questions or greetings

Conversation Context:
{context}

Current User Message: {message}

Respond with ONLY a JSON object:
{{
  "intent": "symptom|dosha|doctor|prescription|progress|emergency|general",
  "confidence": 0.0 to 1.0,
  "reasoning": "brief explanation"
}}"""


def build_context_string(messages: List[Message], max_messages: int = 3) -> str:
    """Build context string from recent messages.
    
    Args:
        messages: List of recent messages
        max_messages: Maximum number of messages to include
        
    Returns:
        Formatted context string
    """
    if not messages:
        return "(No previous context)"
    
    recent = messages[-max_messages:]
    context_lines = []
    
    for msg in recent:
        context_lines.append(f"{msg.role}: {msg.content}")
    
    return "\n".join(context_lines)


async def classify_intent(message: str, context_messages: List[Message] = None) -> Dict[str, Any]:
    """Classify user intent.
    
    Args:
        message: User message to classify
        context_messages: Recent conversation messages for context
        
    Returns:
        Dictionary with intent, confidence, and reasoning
    """
    logger.info("🎯 Intent Classifier: Analyzing message...")
    
    try:
        llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O_MINI.value, temperature=0.3)
        llm = llm_config.get_llm_instance()
        
        # Build context
        context = build_context_string(context_messages or [])
        
        prompt = INTENT_PROMPT.format(
            context=context,
            message=message
        )
        
        logger.info("🤖 Using LLM for intent classification...")
        response = await llm.ainvoke(prompt)
        
        # Parse LLM response
        content = response.content.strip()
        
        # Try to extract JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        
        # Validate intent
        intent = result.get("intent", "general")
        if intent not in INTENTS:
            logger.warning(f"Invalid intent '{intent}', defaulting to 'general'")
            intent = "general"
        
        confidence = result.get("confidence", 0.7)
        
        logger.info(f"✅ Intent classified as: {intent} (confidence: {confidence:.2f})")
        
        return {
            "intent": intent,
            "confidence": confidence,
            "reasoning": result.get("reasoning", "Intent classification completed"),
            "method": "llm_classification"
        }
    
    except Exception as e:
        logger.error(f"Error in intent classification: {e}")
        logger.warning("Falling back to 'general' intent")
        # Fallback to general on error
        return {
            "intent": "general",
            "confidence": 0.5,
            "reasoning": "Unable to classify intent, defaulting to general",
            "method": "fallback",
            "error": str(e)
        }
