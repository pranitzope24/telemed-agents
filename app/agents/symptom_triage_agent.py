"""Symptom triage agent for extracting and analyzing symptoms."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from app.config.llm import LLMConfig
from app.constants.openai_constants import OpenaiModels
from app.utils.logger import get_logger

logger = get_logger()


class SymptomData(BaseModel):
    """Structured symptom information."""
    name: str = Field(description="The main symptom (e.g., 'fever', 'headache', 'cough')")
    duration: Optional[str] = Field(None, description="How long they've had it (e.g., '2 days', '1 week', 'since yesterday')")
    severity: Optional[str] = Field(None, description="Severity level: 'mild', 'moderate', or 'severe'")
    location: Optional[str] = Field(None, description="Body part/area (e.g., 'head', 'chest', 'stomach')")


class SymptomAnalysisResult(BaseModel):
    """Result of symptom analysis."""
    symptoms: List[SymptomData] = Field(description="List of extracted symptoms with details")
    needs_more_info: bool = Field(description="Whether additional information is needed")
    missing_info: List[str] = Field(default_factory=list, description="List of missing critical information (e.g., ['duration', 'severity'])")


class SymptomTriageAgent:
    """Agent to extract structured symptom information."""
    
    def __init__(self):
        llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O_MINI.value, temperature=0.3)
        # Get structured output LLM
        self.llm = llm_config.get_llm_instance().with_structured_output(SymptomAnalysisResult)
    
    async def analyze(self, message: str, context: List[str] = None, existing_symptoms: List[Dict] = None) -> Dict[str, Any]:
        """Extract structured symptoms and identify missing information.
        
        Args:
            message: User's symptom description or follow-up answer
            context: Previous answers from follow-ups (list of strings)
            existing_symptoms: Previously extracted symptoms to update
            
        Returns:
            Dict with:
            - symptoms: List of structured symptom dicts
            - needs_more_info: bool
            - missing_info: List of missing fields
        """
        logger.info(f"Analyzing symptoms from message: {message[:100]}...")
        logger.info(f"With context: {context}")
        logger.info(f"Existing symptoms: {existing_symptoms}")
        # Build context string
        context_str = ""
        if context:
            context_str = "\n".join([f"- {answer}" for answer in context])
        
        # Build existing symptoms context
        existing_symptoms_str = ""
        if existing_symptoms:
            existing_symptoms_str = "Previously extracted symptoms:\n"
            for symp in existing_symptoms:
                parts = [symp.get('name', 'Unknown')]
                if symp.get('severity'):
                    parts.append(f"severity: {symp['severity']}")
                if symp.get('duration'):
                    parts.append(f"duration: {symp['duration']}")
                if symp.get('location'):
                    parts.append(f"location: {symp['location']}")
                existing_symptoms_str += f"- {', '.join(parts)}\n"
        
        prompt = f"""You are a medical symptom analyzer. Your job is to extract and update structured symptom information.

{existing_symptoms_str if existing_symptoms_str else "No symptoms extracted yet."}

Previous Follow-up Answers:
{context_str if context_str else "(None)"}

Current Message:
{message}

Your task:
1. If this is a follow-up answer (e.g., answering "where", "how long", "how bad"), UPDATE the existing symptom(s) with the new information
2. If this is describing NEW symptoms, extract them
3. Identify what CRITICAL information is still missing

For each symptom, extract/update:
- name: The symptom (e.g., "fever", "headache", "cough")
- duration: How long they've had it (e.g., "2 days", "since yesterday"). Use null if not mentioned.
- severity: One of "mild", "moderate", or "severe".
  Infer severity if possible:
    * "severe", "unbearable", "can't sleep", "worst ever", "getting much worse" → severe
    * "moderate", "uncomfortable", "affecting daily activities" → moderate
    * "mild", "slight", "bearable", "not too bad" → mild
  Use null if truly no clues.
- location: Body part or area (e.g., "head", "chest", "front of head"). Use null if not mentioned or not applicable.

IMPORTANT - FOLLOW-UP HANDLING:
- If existing symptoms are provided AND the current message is a short answer (like "head", "2 days", "moderate"), it's likely answering a follow-up question
- UPDATE the existing symptom with this new information instead of creating a new symptom
- Keep all previously gathered information (name, duration, severity, location) and only add/update the missing piece

MISSING INFO RULES:
- Only mark as missing if it's CRITICAL and NOT provided
- Duration and severity are usually critical
- Location is critical for pain/discomfort symptoms
- If info is provided in ANY previous message or context, do NOT mark it missing

EXAMPLE:
Existing: headache, duration: 2 days, severity: moderate, location: null
Current message: "front of my head"
→ Return: headache, duration: 2 days, severity: moderate, location: front of head
→ Missing: [] (all info collected)
"""

        
        try:
            # Structured output automatically returns SymptomAnalysisResult object
            result: SymptomAnalysisResult = await self.llm.ainvoke(prompt)
            
            logger.info(f"Symptom analysis completed successfully: {result}")
            
            # Convert Pydantic models to dicts for compatibility
            symptoms = [symptom.model_dump() for symptom in result.symptoms]
            needs_more_info = result.needs_more_info
            missing_info = result.missing_info
            
            logger.info(f"Extracted {len(symptoms)} symptoms: {[s.get('name') for s in symptoms]}")
            logger.info(f"Details: {symptoms}")
            logger.info(f"Needs more info: {needs_more_info}, Missing: {missing_info}")
            
            return {
                "symptoms": symptoms,
                "needs_more_info": needs_more_info,
                "missing_info": missing_info
            }
            
        except Exception as e:
            logger.error(f"Error in symptom analysis: {e}")
            # Fallback: basic extraction
            return {
                "symptoms": [{"name": message[:100], "duration": None, "severity": None, "location": None}],
                "needs_more_info": True,
                "missing_info": ["duration", "severity"]
            }
