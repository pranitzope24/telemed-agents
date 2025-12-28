"""Safety and compliance checker for medical responses."""

from typing import Dict, Any, List
from app.utils.logger import get_logger

logger = get_logger()


class SafetyComplianceChecker:
    """Simple safety checker to add disclaimers and validate responses."""
    
    # Keywords that might indicate medical concerns
    CONCERN_KEYWORDS = [
        "chest pain", "shortness of breath", "severe", "emergency",
        "blood", "unconscious", "seizure", "stroke", "heart attack",
        "pregnant", "pregnancy", "medication", "allergic"
    ]
    
    AYURVEDA_DISCLAIMER = """

⚠️ **Important Disclaimer:**
This dosha assessment is for informational and educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified Ayurvedic practitioner or healthcare provider before making any changes to your diet, lifestyle, or health regimen.
"""
    
    def __init__(self):
        pass
    
    def check_response(self, response: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate response and add safety disclaimers.
        
        Args:
            response: Generated response text
            context: Additional context (answers, scores, etc.)
            
        Returns:
            Dict with:
            - final_response: Response with disclaimers added
            - safety_flags: List of detected concerns
            - needs_escalation: bool
        """
        logger.info("Running safety and compliance check...")
        
        safety_flags = []
        needs_escalation = False
        
        # Check for concerning keywords
        response_lower = response.lower()
        context_text = str(context).lower() if context else ""
        
        for keyword in self.CONCERN_KEYWORDS:
            if keyword in response_lower or keyword in context_text:
                safety_flags.append(f"Detected: {keyword}")
                if keyword in ["chest pain", "shortness of breath", "unconscious", "seizure", "stroke", "heart attack"]:
                    needs_escalation = True
        
        # Add disclaimer to response
        final_response = response.strip()
        
        # Add emergency notice if needed
        if needs_escalation:
            emergency_notice = "\n\n🚨 **IMPORTANT:** Some of your symptoms may require immediate medical attention. Please consult a healthcare provider or emergency services if you're experiencing severe symptoms.\n"
            final_response = emergency_notice + final_response
            logger.warning(f"Safety escalation needed: {safety_flags}")
        
        # Always add Ayurveda disclaimer
        final_response += self.AYURVEDA_DISCLAIMER
        
        # Add consultation recommendation
        final_response += "\n\n💡 **Next Steps:** Consider consulting with a certified Ayurvedic practitioner for a personalized assessment and treatment plan tailored to your unique constitution.\n"
        
        logger.info(f"Safety check complete. Flags: {len(safety_flags)}, Escalation: {needs_escalation}")
        
        return {
            "final_response": final_response,
            "safety_flags": safety_flags,
            "needs_escalation": needs_escalation
        }
    
    def validate_dosha_response(self, dosha_data: Dict[str, Any]) -> bool:
        """Validate dosha inference results.
        
        Args:
            dosha_data: Dict with scores and dominant dosha
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ["vata_score", "pitta_score", "kapha_score", "dominant_dosha"]
        
        # Check all required fields present
        if not all(field in dosha_data for field in required_fields):
            logger.error(f"Missing required fields in dosha data: {dosha_data.keys()}")
            return False
        
        # Check scores are valid
        try:
            vata = float(dosha_data["vata_score"])
            pitta = float(dosha_data["pitta_score"])
            kapha = float(dosha_data["kapha_score"])
            
            if not (0 <= vata <= 100 and 0 <= pitta <= 100 and 0 <= kapha <= 100):
                logger.error(f"Dosha scores out of range: V={vata}, P={pitta}, K={kapha}")
                return False
                
            # Scores should roughly sum to 100
            total = vata + pitta + kapha
            if not (95 <= total <= 105):
                logger.warning(f"Dosha scores don't sum to ~100: {total}")
                # Don't fail, just warn
                
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid dosha score values: {e}")
            return False
        
        logger.info("Dosha data validation passed")
        return True

