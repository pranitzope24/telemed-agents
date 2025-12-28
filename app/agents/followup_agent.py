"""Follow-up agent for generating clarifying questions."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from app.config.llm import LLMConfig
from app.constants.openai_constants import OpenaiModels
from app.utils.logger import get_logger

logger = get_logger()


class FollowupQuestion(BaseModel):
    """Generated follow-up question."""
    question: str = Field(description="A clear, empathetic follow-up question to ask the patient")
    reasoning: str = Field(description="Brief explanation of why this question is important")


class FollowupAgent:
    """Agent to generate relevant follow-up questions."""
    
    def __init__(self):
        llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O_MINI.value, temperature=0.7)
        # Get structured output LLM
        self.llm = llm_config.get_llm_instance().with_structured_output(FollowupQuestion)
    
    async def generate_question(self, 
                               symptoms: List[Dict[str, Any]], 
                               missing_info: List[str],
                               already_asked: List[str]) -> str:
        """Generate a follow-up question based on missing information.
        
        Args:
            symptoms: List of structured symptom dicts
            missing_info: List of missing fields (duration, severity, location)
            already_asked: Questions already asked to avoid repetition
            
        Returns:
            A clear, empathetic follow-up question
        """
        logger.info(f"Generating follow-up for missing: {missing_info}")
        
        # Build symptom summary
        symptom_summary = ""
        if symptoms:
            symptom_summary = ", ".join([s.get("name", "symptom") for s in symptoms])
        
        # Build already asked string
        asked_str = "\n".join([f"- {q}" for q in already_asked]) if already_asked else "(None)"
        
        prompt = f"""You are a compassionate medical interviewer. Ask ONE clear follow-up question.

Patient's symptoms: {symptom_summary}
Missing information: {', '.join(missing_info)}

Questions already asked:
{asked_str}

Generate ONE follow-up question that:
1. Asks about the MOST important missing information
2. Is clear and easy to understand
3. Is empathetic and non-alarming
4. Doesn't repeat questions already asked

Examples:
- "When did your headache start?"
- "On a scale of 1-10, how severe is the pain?"
- "Where exactly do you feel the pain?"
- "Is the pain constant or does it come and go?"

Your question:"""
        
        try:
            # Structured output automatically returns FollowupQuestion object
            result: FollowupQuestion = await self.llm.ainvoke(prompt)
            
            logger.info(f"Generated question: {result.question}")
            logger.info(f"Reasoning: {result.reasoning}")
            return result.question
            
        except Exception as e:
            logger.error(f"Error generating follow-up: {e}")
            # Fallback questions based on missing info
            if "duration" in missing_info:
                return "When did these symptoms start?"
            elif "severity" in missing_info:
                return "How severe are your symptoms? (mild, moderate, or severe)"
            elif "location" in missing_info:
                return "Where exactly are you experiencing these symptoms?"
            else:
                return "Can you tell me more about your symptoms?"
