"""Dosha inference agent for determining constitutional type."""

from typing import Dict, Any
from app.config.llm import LLMConfig
from app.constants.openai_constants import OpenaiModels
from app.utils.logger import get_logger

logger = get_logger()


class DoshaInferenceAgent:
    """Agent to infer dosha composition from questionnaire data."""
    
    def __init__(self):
        llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O_MINI.value, temperature=0.3)
        self.llm = llm_config.get_llm_instance()
    
    async def infer_dosha(self, answers: Dict[str, str]) -> Dict[str, Any]:
        """Determine dosha composition based on collected answers.
        
        Args:
            answers: Dictionary of questionnaire responses
            
        Returns:
            Dict with:
            - vata_score: float (0-100)
            - pitta_score: float (0-100)
            - kapha_score: float (0-100)
            - dominant_dosha: str
            - explanation: str
        """
        logger.info(f"Inferring dosha from {len(answers)} answers...")
        
        # Format answers for prompt
        answers_text = "\n".join([f"{key}: {value}" for key, value in answers.items()])
        
        prompt = f"""You are an Ayurvedic expert trained in dosha analysis. Based on the following characteristics, determine the person's dosha composition.

**Ayurvedic Dosha Basics:**

VATA (Air + Space):
- Thin/light body frame
- Dry skin and hair
- Variable appetite and digestion
- Light, interrupted sleep
- Quick, creative mind
- Enthusiastic but anxious under stress
- Cold hands and feet

PITTA (Fire + Water):
- Medium build, muscular
- Warm body, sweats easily
- Strong appetite, sharp digestion
- Sound sleep, moderate duration
- Sharp intellect, focused
- Intense, competitive nature
- Sensitive to heat

KAPHA (Earth + Water):
- Heavy/solid build, gains weight easily
- Smooth, oily skin
- Slow but steady digestion
- Deep, prolonged sleep
- Calm, steady mind
- Patient, loving nature
- Resistant to change

**User's Characteristics:**
{answers_text}

Analyze the above and respond in this EXACT format:
VATA_SCORE: [0-100]
PITTA_SCORE: [0-100]
KAPHA_SCORE: [0-100]
DOMINANT: [Vata/Pitta/Kapha or combination like "Vata-Pitta"]
EXPLANATION: [2-3 sentences explaining the assessment]

Example:
VATA_SCORE: 65
PITTA_SCORE: 25
KAPHA_SCORE: 10
DOMINANT: Vata
EXPLANATION: You show strong Vata characteristics with your light frame, variable energy, and creative nature. The dry skin and light sleep patterns further confirm Vata dominance. A small Pitta influence appears in your focused mental activity.
"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content.strip()
            
            # Parse response
            vata_score = 0.0
            pitta_score = 0.0
            kapha_score = 0.0
            dominant_dosha = "Unknown"
            explanation = ""
            
            for line in content.split('\n'):
                line = line.strip()
                
                if line.startswith('VATA_SCORE:'):
                    try:
                        vata_score = float(line.replace('VATA_SCORE:', '').strip())
                    except ValueError:
                        vata_score = 33.3
                        
                elif line.startswith('PITTA_SCORE:'):
                    try:
                        pitta_score = float(line.replace('PITTA_SCORE:', '').strip())
                    except ValueError:
                        pitta_score = 33.3
                        
                elif line.startswith('KAPHA_SCORE:'):
                    try:
                        kapha_score = float(line.replace('KAPHA_SCORE:', '').strip())
                    except ValueError:
                        kapha_score = 33.3
                        
                elif line.startswith('DOMINANT:'):
                    dominant_dosha = line.replace('DOMINANT:', '').strip()
                    
                elif line.startswith('EXPLANATION:'):
                    explanation = line.replace('EXPLANATION:', '').strip()
            
            # Normalize scores to sum to 100
            total = vata_score + pitta_score + kapha_score
            if total > 0:
                vata_score = (vata_score / total) * 100
                pitta_score = (pitta_score / total) * 100
                kapha_score = (kapha_score / total) * 100
            else:
                vata_score = pitta_score = kapha_score = 33.3
            
            # Determine dominant if not provided correctly
            if dominant_dosha == "Unknown" or not dominant_dosha:
                scores = {
                    "Vata": vata_score,
                    "Pitta": pitta_score,
                    "Kapha": kapha_score
                }
                dominant_dosha = max(scores, key=scores.get)
            
            logger.info(f"Dosha inference: {dominant_dosha} (V:{vata_score:.1f} P:{pitta_score:.1f} K:{kapha_score:.1f})")
            
            return {
                "vata_score": round(vata_score, 1),
                "pitta_score": round(pitta_score, 1),
                "kapha_score": round(kapha_score, 1),
                "dominant_dosha": dominant_dosha,
                "explanation": explanation or f"Your constitution shows {dominant_dosha} dominance based on your characteristics."
            }
            
        except Exception as e:
            logger.error(f"Error in dosha inference: {e}")
            # Fallback: balanced tridosha
            return {
                "vata_score": 33.3,
                "pitta_score": 33.3,
                "kapha_score": 33.3,
                "dominant_dosha": "Balanced Tridosha",
                "explanation": "Unable to determine specific dosha dominance. You may have a balanced constitution."
            }

