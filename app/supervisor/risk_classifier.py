"""Risk classification for medical assessment."""

import json
from typing import Any, Dict, List

from app.config.llm import LLMConfig
from app.constants.openai_constants import OpenaiModels
from app.supervisor.constants import EMERGENCY_KEYWORDS, RISK_LEVELS
from app.utils.logger import get_logger

logger = get_logger()


RISK_PROMPT = """You are a medical triage AI assistant. Assess the risk level of this patient message.

Risk Levels:
- low: Minor concerns, can wait, self-care possible
- medium: Should see doctor soon, not urgent
- high: Serious concern, needs doctor promptly
- emergency: Life-threatening, immediate medical attention required

Patient Message: {message}

Respond with ONLY a JSON object:
{{
  "risk_level": "low|medium|high|emergency",
  "reasoning": "brief explanation",
  "urgency_score": 0.0 to 1.0
}}"""


def check_emergency_keywords(message: str) -> List[str]:
    """Quick check for emergency keywords.
    
    Args:
        message: User message to check
        
    Returns:
        List of detected emergency keywords
    """
    message_lower = message.lower()
    detected = []
    
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in message_lower:
            detected.append(keyword)
    
    return detected


async def classify_risk(message: str) -> Dict[str, Any]:
    """Classify medical risk level.
    
    Args:
        message: User message to assess
        
    Returns:
        Dictionary with risk level, reasoning, and metadata
    """
    logger.info("🔍 Risk Classifier: Analyzing message...")
    
    # Step 1: Quick emergency keyword check
    emergency_keywords = check_emergency_keywords(message)
    
    if emergency_keywords:
        logger.warning(f"Emergency keywords detected: {emergency_keywords}")
        return {
            "risk_level": "emergency",
            "reasoning": f"Emergency keywords detected: {', '.join(emergency_keywords)}",
            "emergency_keywords": emergency_keywords,
            "urgency_score": 1.0,
            "method": "keyword_detection"
        }
    
    # Step 2: LLM-based risk assessment
    try:
        logger.info("🤖 Using LLM for risk assessment...")
        llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O_MINI.value, temperature=0.3)
        llm = llm_config.get_llm_instance()
        
        prompt = RISK_PROMPT.format(message=message)
        response = await llm.ainvoke(prompt)
        
        # Parse LLM response
        content = response.content.strip()
        
        # Try to extract JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        
        # Validate risk level
        risk_level = result.get("risk_level", "medium")
        if risk_level not in RISK_LEVELS:
            logger.warning(f"Invalid risk level '{risk_level}', defaulting to 'medium'")
            risk_level = "medium"
        
        logger.info(f"✅ Risk classified as: {risk_level} (score: {result.get('urgency_score', 0.5)})")
        
        return {
            "risk_level": risk_level,
            "reasoning": result.get("reasoning", "Risk assessment completed"),
            "emergency_keywords": [],
            "urgency_score": result.get("urgency_score", 0.5),
            "method": "llm_assessment"
        }
    
    except Exception as e:
        logger.error(f"Error in risk classification: {e}")
        logger.warning("Falling back to 'medium' risk")
        # Fallback to medium risk on error
        return {
            "risk_level": "medium",
            "reasoning": "Unable to assess risk, defaulting to medium for safety",
            "emergency_keywords": [],
            "urgency_score": 0.5,
            "method": "fallback",
            "error": str(e)
        }
