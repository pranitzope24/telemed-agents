"""Constants for supervisor system."""

from typing import Dict, List

# ===== Intent Types =====
INTENTS = [
    "symptom",
    "dosha",
    "doctor",
    "prescription",
    "progress",
    "emergency",
    "general"
]

# ===== Risk Levels =====
RISK_LEVELS = [
    "low",
    "medium",
    "high",
    "emergency"
]

# ===== Emergency Keywords =====
EMERGENCY_KEYWORDS = [
    "chest pain",
    "heart attack",
    "stroke",
    "can't breathe",
    "cannot breathe",
    "difficulty breathing",
    "bleeding heavily",
    "severe bleeding",
    "unconscious",
    "seizure",
    "overdose",
    "suicide",
    "suicidal",
    "choking",
    "severe burn",
    "anaphylaxis",
    "allergic reaction severe",
    "lost consciousness",
    "can't feel",
    "paralyzed",
    "extreme pain"
]

# ===== Intent to Graph Mapping =====
INTENT_TO_GRAPH: Dict[str, str] = {
    "symptom": "symptoms_graph",
    "dosha": "dosha_graph",
    "doctor": "doctor_matching_graph",
    "prescription": "prescription_graph",
    "progress": "progress_graph",
    "emergency": "emergency_graph",
    "general": "symptoms_graph"  # Default to symptoms
}

# ===== Mock Graph Responses =====
MOCK_GRAPH_RESPONSES: Dict[str, str] = {
    "symptoms_graph": (
        "I understand you're experiencing symptoms. "
        "Let me help you assess this. Can you describe:\n\n"
        "• When did the symptoms start?\n"
        "• How severe are they (mild/moderate/severe)?\n"
        "• Any other symptoms you've noticed?"
    ),
    "dosha_graph": (
        "Let's discover your Ayurvedic constitution (dosha). "
        "I'll ask you a few questions about your body type, digestion, and lifestyle.\n\n"
        "First question: How would you describe your body frame?\n"
        "• Thin/lean\n"
        "• Medium/athletic\n"
        "• Heavy/solid"
    ),
    "doctor_matching_graph": (
        "I can help you find and book a suitable doctor. "
        "To find the best match, let me know:\n\n"
        "• What specialty do you need? (or I can suggest based on symptoms)\n"
        "• Your preferred location\n"
        "• Any specific requirements (language, gender, etc.)"
    ),
    "prescription_graph": (
        "I can help with prescription information. "
        "Please note that any prescription must be reviewed and approved by a licensed doctor.\n\n"
        "What would you like to know about?\n"
        "• Current medications\n"
        "• Prescription refills\n"
        "• Medication information"
    ),
    "progress_graph": (
        "Let's track your treatment progress. "
        "I can help you:\n\n"
        "• Log daily symptoms\n"
        "• Review your progress over time\n"
        "• Identify trends\n"
        "• Schedule follow-ups\n\n"
        "How are you feeling today compared to your last update?"
    ),
    "emergency_graph": (
        "⚠️ MEDICAL EMERGENCY DETECTED ⚠️\n\n"
        "This appears to be a medical emergency. "
        "Please take immediate action:\n\n"
        "1. Call emergency services (112) or ambulance (108) immediately\n"
        "2. If safe, go to the nearest emergency room\n"
        "3. Do not wait for an appointment\n\n"
        "If you're experiencing:\n"
        "• Chest pain or pressure\n"
        "• Difficulty breathing\n"
        "• Severe bleeding\n"
        "• Loss of consciousness\n"
        "• Stroke symptoms\n\n"
        "SEEK IMMEDIATE MEDICAL ATTENTION. This assistant cannot provide emergency care."
    )
}
