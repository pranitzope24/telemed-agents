"""Symptom triage agent for extracting and analyzing symptoms."""

from typing import Dict, List, Any
from app.config.llm import LLMConfig
from app.constants.openai_constants import OpenaiModels
from app.utils.logger import get_logger

logger = get_logger()


class SymptomTriageAgent:
    """Agent to extract structured symptom information."""
    
    def __init__(self):
        llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O_MINI.value, temperature=0.3)
        self.llm = llm_config.get_llm_instance()
    
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

Extract:
- name: Main symptom (e.g., "headache", "fever", "cough")
- duration: How long (e.g., "3 days", "since yesterday", "2 weeks")
- severity: mild, moderate, or severe
- location: Body part/area (e.g., "frontal", "chest", "left arm")
- associated_symptoms: Other symptoms mentioned

Previous Context:
{context_str if context_str else "(None)"}

Current Message:
{message}

Respond in this EXACT format:
SYMPTOMS: [list each symptom with available details]
NEEDS_MORE_INFO: yes/no
MISSING: [list what's missing: duration, severity, location]

Example:
SYMPTOMS: headache (moderate, frontal, 3 days)
NEEDS_MORE_INFO: no
MISSING: none
"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content.strip()
            
            # Parse response
            symptoms = []
            needs_more_info = False
            missing_info = []
            
            for line in content.split('\n'):
                if line.startswith('SYMPTOMS:'):
                    symptom_text = line.replace('SYMPTOMS:', '').strip()
                    # Simple parsing - extract what we can
                    symptom_data = {
                        "name": symptom_text.split('(')[0].strip() if '(' in symptom_text else symptom_text,
                        "duration": None,
                        "severity": None,
                        "location": None
                    }
                    # Try to extract severity, location, duration from parentheses
                    if '(' in symptom_text:
                        details = symptom_text.split('(')[1].split(')')[0]
                        detail_parts = [d.strip() for d in details.split(',')]
                        for detail in detail_parts:
                            if any(sev in detail.lower() for sev in ['mild', 'moderate', 'severe']):
                                symptom_data["severity"] = detail
                            elif any(dur in detail.lower() for dur in ['day', 'week', 'month', 'hour', 'yesterday', 'ago']):
                                symptom_data["duration"] = detail
                            else:
                                symptom_data["location"] = detail
                    symptoms.append(symptom_data)
                    
                elif line.startswith('NEEDS_MORE_INFO:'):
                    needs_more_info = 'yes' in line.lower()
                    
                elif line.startswith('MISSING:'):
                    missing_text = line.replace('MISSING:', '').strip().lower()
                    if 'none' not in missing_text:
                        missing_info = [m.strip() for m in missing_text.split(',') if m.strip()]
            
            # If we have empty fields, we need more info
            if symptoms:
                for symptom in symptoms:
                    if not symptom.get("duration") and "duration" not in missing_info:
                        missing_info.append("duration")
                    if not symptom.get("severity") and "severity" not in missing_info:
                        missing_info.append("severity")
            
            needs_more_info = needs_more_info or len(missing_info) > 0
            
            logger.info(f"Extracted {len(symptoms)} symptoms, needs_more_info={needs_more_info}")
            
            return {
                "symptoms": symptoms,
                "needs_more_info": needs_more_info,
                "missing_info": list(set(missing_info))  # Deduplicate
            }
            
        except Exception as e:
            logger.error(f"Error in symptom analysis: {e}")
            # Fallback: basic extraction
            return {
                "symptoms": [{"name": message[:100], "duration": None, "severity": None, "location": None}],
                "needs_more_info": True,
                "missing_info": ["duration", "severity", "location"]
            }
