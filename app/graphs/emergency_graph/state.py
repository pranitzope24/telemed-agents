"""Emergency graph state definition."""

from operator import add
from typing import Annotated, Dict, List, Literal, Optional, TypedDict


class EmergencyGraphState(TypedDict):
	"""State for emergency assistance graph.
    
	Local per-graph state used by LangGraph. Mirrors patterns in DoshaGraphState.
	"""
    
	# ===== Input =====
	user_message: str
	session_id: str
    
	# ===== Classification =====
	incident_summary: Optional[str]
	emergency_type: Optional[str]  # e.g., "cardiac", "respiratory", "bleeding", "neurological", "allergic", "unknown"
	risk_level: Optional[Literal["low", "medium", "high", "emergency"]]
	detected_keywords: Annotated[List[str], add]
	needs_911: bool
	urgency_score: Optional[float]
    
	# ===== Output =====
	first_aid_instructions: Optional[str]
	escalation_advice: Optional[str]
	final_response: Optional[str]
	safety_flags: List[str]
	next_action: Literal["complete", "handoff"]
	completed: bool
