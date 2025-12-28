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
    
    async def analyze(self, message: str, context: List[str] = None) -> Dict[str, Any]:
        """Extract structured symptoms and identify missing information.
        
        Args:
            message: User's symptom description
            context: Previous answers from follow-ups (list of strings)
            
        Returns:
            Dict with:
            - symptoms: List of structured symptom dicts
            - needs_more_info: bool
            - missing_info: List of missing fields
        """
        logger.info(f"Analyzing symptoms from message: {message[:100]}...")
        
        # Build context string
        context_str = ""
        if context:
            context_str = "\n".join([f"- {answer}" for answer in context])
        
        prompt = f"""You are a medical symptom analyzer. Extract structured information from the patient's description.

Previous Context:
{context_str if context_str else "(None)"}

Current Message:
{message}

Your task:
1. Extract ALL symptoms mentioned and their details
2. Identify CRITICAL information that is still missing and needed for safe guidance

For each symptom, extract:
- name: The symptom (e.g., "fever", "headache", "cough")
- duration: How long they've had it (e.g., "2 days", "since yesterday"). If not mentioned, use null.
- severity: One of "mild", "moderate", or "severe".
  Infer severity if possible using these rules:
    * "severe", "unbearable", "can't sleep", "worst ever", "getting much worse" → severe
    * "moderate", "uncomfortable", "affecting daily activities" → moderate
    * "mild", "slight", "bearable", "not too bad" → mild
  If there are truly no clues, use null.
- location: Body part or area (e.g., "head", "chest"). If not mentioned or not applicable, use null.

CRITICAL MISSING INFORMATION RULES:
- Duration and severity are CRITICAL for most symptoms
- Location is critical when relevant (e.g., pain)
- Do NOT mark information as missing if it is clearly provided
- Do NOT mark information as missing if the user explicitly says they don't know
- If a symptom has duration or severity as null, AND it is important for understanding the symptom, add it to missing_info

IMPORTANT:
- If duration is mentioned (e.g., "for 2 days"), include it and do NOT mark it missing
- If severity is mentioned or can be inferred, include it and do NOT mark it missing
- If the user says "no other symptoms", do NOT mark anything as missing
- Do NOT invent information
- Be conservative but explicit about what is missing

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
