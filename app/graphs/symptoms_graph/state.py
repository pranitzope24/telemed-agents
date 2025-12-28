"""Symptoms graph state definition."""

from typing import TypedDict, Annotated, Optional, List, Dict, Literal
from operator import add


class SymptomData(TypedDict, total=False):
    """Structured symptom information."""
    name: str
    duration: Optional[str]
    severity: Optional[str]  # mild, moderate, severe
    location: Optional[str]
    associated_symptoms: Optional[List[str]]


class SymptomsGraphState(TypedDict):
    """State for symptoms triage graph.
    
    This is the local graph state - separate from SessionState.
    Uses TypedDict for LangGraph compatibility.
    """
    
    # ===== Input =====
    user_message: str
    session_id: str
    
    # ===== Symptom Data =====
    raw_symptoms: str
    structured_symptoms: List[SymptomData]
    
    # ===== Follow-up Tracking =====
    # Annotated with 'add' means append, not replace
    questions_asked: Annotated[List[str], add]
    answers_collected: Dict[str, str]
    needs_more_info: bool
    missing_info: List[str]
    
    # ===== Loop Control =====
    iteration_count: int
    max_iterations: int
    
    # ===== Output =====
    final_response: Optional[str]
    next_action: Literal["complete", "handoff_emergency", "handoff_doctor"]
