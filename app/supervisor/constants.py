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
    "emergency": "emergency_graph",
    "general": "symptoms_graph",  # Default to symptoms
    # Unimplemented graphs route to symptoms as fallback:
    "prescription": "symptoms_graph",
    "progress": "symptoms_graph",
}


