"""Doctor matching graph state definition."""

from typing import TypedDict, List, Dict, Any


class DoctorMatchingState(TypedDict, total=False):
    """State for doctor matching workflow.
    
    Simple 2-node flow (only receives handoffs from symptoms graph):
    1. specialty_mapper_node: Map symptoms to Ayurvedic specialties
    2. doctor_search_node: Search and present doctors
    
    This graph should NOT be called directly on first intent routing.
    It only handles handoffs with structured symptom data.
    """
    
    # ===== Input from Handoff =====
    session_context: Dict[str, Any]  # Contains: reported_symptoms, recent_messages, user_location_city
    structured_symptoms: List[Dict[str, Any]]  # From symptoms graph
    symptoms_summary: str  # Brief summary for specialty mapping
    
    # ===== Specialty Mapping Output =====
    recommended_specialties: List[str]
    specialty_explanation: str
    
    # ===== Doctor Search Output =====
    doctor_search_results: List[Dict[str, Any]]
    
    # ===== Final Output =====
    final_response: str
    next_action: str  # "complete"
    available_doctors: List[Dict[str, Any]]
    booking_context: Dict[str, Any]

