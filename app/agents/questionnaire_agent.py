"""Dosha questionnaire agent for analyzing responses and calculating confidence."""

from typing import Dict, List, Any
from app.config.llm import LLMConfig
from app.constants.openai_constants import OpenaiModels
from app.utils.logger import get_logger

logger = get_logger()


class DoshaQuestionnaireAgent:
    """Agent to analyze dosha-related answers and calculate confidence score."""
    
    # Common dosha assessment areas
    REQUIRED_AREAS = [
        "body_type",
        "digestion",
        "sleep_pattern",
        "temperament",
        "skin_type",
        "energy_level"
    ]
    
    def __init__(self):
        llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O_MINI.value, temperature=0.3)
        self.llm = llm_config.get_llm_instance()
    
    async def analyze(self, message: str, context: Dict[str, str] = None) -> Dict[str, Any]:
        """Analyze dosha questionnaire responses and calculate confidence.
        
        Args:
            message: User's response to dosha questions
            context: Previous Q&A context from follow-ups
            
        Returns:
            Dict with:
            - answers: Updated answers dict with extracted info
            - confidence_score: float (0.0 to 1.0)
            - needs_more_info: bool
            - missing_areas: List of areas needing more info
        """
        logger.info(f"Analyzing dosha questionnaire response: {message[:100]}...")
        
        # Build context string
        context_str = ""
        if context:
            context_str = "\n".join([f"Q: {q}\nA: {a}" for q, a in context.items()])
        
        prompt = f"""You are an Ayurvedic dosha assessment expert. Analyze the user's response and extract information about these areas:

1. Body Type: Build, weight, frame (thin/medium/heavy)
2. Digestion: Appetite, digestion speed, food preferences
3. Sleep Pattern: Quality, duration, ease of falling asleep
4. Temperament: Energy, emotions, stress response
5. Skin Type: Dry, oily, combination, sensitive
6. Energy Level: Consistent, variable, steady

Previous Context:
{context_str if context_str else "(None)"}

Current Message:
{message}

Respond in this EXACT format:
EXTRACTED_INFO:
body_type: [what you found or "unknown"]
digestion: [what you found or "unknown"]
sleep_pattern: [what you found or "unknown"]
temperament: [what you found or "unknown"]
skin_type: [what you found or "unknown"]
energy_level: [what you found or "unknown"]

CONFIDENCE: [0.0 to 1.0 - based on how much info you have]
NEEDS_MORE: yes/no
MISSING: [comma separated list of areas that need more info]

Example:
EXTRACTED_INFO:
body_type: thin, light frame
digestion: variable appetite, fast metabolism
sleep_pattern: unknown
temperament: energetic, creative
skin_type: dry
energy_level: variable

CONFIDENCE: 0.6
NEEDS_MORE: yes
MISSING: sleep_pattern
"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content.strip()
            
            # Parse response
            answers = context.copy() if context else {}
            confidence_score = 0.0
            needs_more_info = True
            missing_areas = []
            
            current_section = None
            for line in content.split('\n'):
                line = line.strip()
                
                if line.startswith('EXTRACTED_INFO:'):
                    current_section = 'info'
                    continue
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence_score = float(line.replace('CONFIDENCE:', '').strip())
                    except ValueError:
                        confidence_score = 0.5
                    current_section = None
                elif line.startswith('NEEDS_MORE:'):
                    needs_more_info = 'yes' in line.lower()
                    current_section = None
                elif line.startswith('MISSING:'):
                    missing_text = line.replace('MISSING:', '').strip()
                    if missing_text and 'none' not in missing_text.lower():
                        missing_areas = [m.strip() for m in missing_text.split(',') if m.strip()]
                    current_section = None
                elif current_section == 'info' and ':' in line:
                    # Parse extracted info
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if value and value.lower() != 'unknown':
                        answers[key] = value
            
            # Calculate confidence based on coverage
            covered_areas = len([area for area in self.REQUIRED_AREAS if area in answers and answers[area]])
            calculated_confidence = covered_areas / len(self.REQUIRED_AREAS)
            
            # Use the higher of LLM confidence or calculated confidence
            confidence_score = max(confidence_score, calculated_confidence)
            
            # Determine missing areas if not provided
            if not missing_areas:
                missing_areas = [area for area in self.REQUIRED_AREAS if area not in answers or not answers[area]]
            
            needs_more_info = confidence_score < 0.7 or len(missing_areas) > 0
            
            logger.info(f"Questionnaire analysis: confidence={confidence_score:.2f}, needs_more={needs_more_info}, missing={missing_areas}")
            
            return {
                "answers": answers,
                "confidence_score": confidence_score,
                "needs_more_info": needs_more_info,
                "missing_areas": missing_areas
            }
            
        except Exception as e:
            logger.error(f"Error in questionnaire analysis: {e}")
            # Fallback: basic extraction
            return {
                "answers": context.copy() if context else {"initial_response": message},
                "confidence_score": 0.3,
                "needs_more_info": True,
                "missing_areas": self.REQUIRED_AREAS.copy()
            }

