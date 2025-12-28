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
    
    async def analyze(self, message: str, context: Dict[str, str] = None) -> Dict[str, Any]:
        """Extract structured symptoms and identify missing information.
        
        Args:
            message: User's symptom description
            context: Previous Q&A context from follow-ups
            
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
            context_str = "\n".join([f"Q: {q}\nA: {a}" for q, a in context.items()])
        
        prompt = f"""You are a medical symptom analyzer. Extract structured information from the patient's description.

Previous Context:
{context_str if context_str else "(None)"}

Current Message:
{message}

Extract ALL symptoms mentioned and their details. For each symptom, extract:
- name: The symptom (e.g., "fever", "headache", "cough")
- duration: How long they've had it (e.g., "2 days", "1 week", "since yesterday"). If not mentioned, use null.
- severity: "mild", "moderate", or "severe". If not mentioned, use null.
- location: Body part/area (e.g., "head", "chest", "stomach"). If not mentioned or not applicable, use null.

Also determine what critical information is STILL MISSING (only if truly not provided in the message).

IMPORTANT:
- If duration is mentioned (like "for 2 days", "since yesterday"), include it - don't mark as missing
- If severity is mentioned (like "moderate", "mild pain", "severe headache"), include it - don't mark as missing
- If user says "no other symptoms", don't mark anything as missing
- Only mark as missing if it's CRITICAL and NOT provided
- Use null for fields that aren't mentioned or don't apply"""
        
        try:
            # Structured output automatically returns SymptomAnalysisResult object
            result: SymptomAnalysisResult = await self.llm.ainvoke(prompt)
            
            # Convert Pydantic models to dicts for compatibility
            symptoms = [symptom.model_dump() for symptom in result.symptoms]
            needs_more_info = result.needs_more_info
            missing_info = result.missing_info
            
            # Validate: only mark as needing more info if critical fields are missing
            # Don't auto-add missing fields if symptom data looks complete
            if symptoms:
                actually_missing = []
                for symptom in symptoms:
                    # Only require name - duration and severity are optional
                    # Most symptoms have been described if we have name + at least one other field
                    has_details = (
                        symptom.get("duration") or 
                        symptom.get("severity") or 
                        symptom.get("location")
                    )
                    
                    # If symptom has NO details at all, we might need more info
                    if not has_details and symptom.get("name"):
                        if not symptom.get("duration"):
                            actually_missing.append("duration")
                        if not symptom.get("severity"):
                            actually_missing.append("severity")
                
                # Deduplicate and only set missing if we found truly missing fields
                missing_info = list(set(actually_missing)) if actually_missing else []
                needs_more_info = len(missing_info) > 0
            
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
