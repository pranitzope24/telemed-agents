"""Dosha graph state definition."""

from typing import TypedDict, Annotated, Optional, List, Dict, Literal
from operator import add


class DoshaGraphState(TypedDict):
    """State for dosha assessment graph.
    
    This is the local graph state - separate from SessionState.
    Uses TypedDict for LangGraph compatibility.
    """
    
    # ===== Input =====
    user_message: str
    session_id: str
    
    # ===== Questionnaire Data =====
    answers_collected: Dict[str, str]  # question -> answer mapping
    confidence_score: float  # 0.0 to 1.0
    confidence_threshold: float  # Default 0.7
    
    # ===== Follow-up Tracking =====
    # Annotated with 'add' means append, not replace
    questions_asked: Annotated[List[str], add]
    needs_more_info: bool
    missing_areas: List[str]  # e.g., ["body_type", "digestion", "sleep"]
    
    # ===== Loop Control =====
    iteration_count: int
    max_iterations: int
    
    # ===== Dosha Results =====
    vata_score: Optional[float]  # 0-100
    pitta_score: Optional[float]  # 0-100
    kapha_score: Optional[float]  # 0-100
    dominant_dosha: Optional[str]  # "Vata", "Pitta", "Kapha", or combination
    dosha_explanation: Optional[str]
    
    # ===== Output =====
    final_response: Optional[str]
    safety_flags: List[str]
    next_action: Literal["complete", "handoff"]
