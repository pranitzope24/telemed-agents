"""Doctor matching graph state definition - Simplified."""

from typing import TypedDict, Optional, List, Dict, Any


class DoctorMatchingState(TypedDict, total=False):
    """Simplified state for doctor matching workflow.
    
    Only includes essential fields for the 3-node flow:
    1. symptoms_triage_node
    2. specialty_recommendation_node  
    3. doctor_search_node
    """
    
    # ===== Input from handoff or user =====
    symptoms_summary: str
    structured_symptoms: List[Dict[str, Any]]
    severity_level: str
    handoff_source: str
    user_message: str
    
    # ===== Session context (from global SessionState) =====
    session_context: Dict[str, Any]  # Contains: reported_symptoms, recent_messages, etc.
    
    # ===== Collected during flow =====
    confirmed_specialties: List[str]
    user_location_city: str
    
    # ===== Search results =====
    available_doctors: List[Dict[str, Any]]
    
    # ===== Output =====
    final_response: str
    next_action: str  # "complete"
    booking_context: Dict[str, Any]  # For UI to use when user clicks booking button

