"""Doctor matching graph executor."""

from typing import Any, Dict

from langgraph.types import Command

from app.state.graph_state import SessionState
from app.supervisor.executors.base import GraphExecutor
from app.utils.logger import get_logger

logger = get_logger()


class DoctorMatchingGraphExecutor(GraphExecutor):
    """Executor for doctor matching graph."""
    
    def __init__(self):
        super().__init__("doctor_matching_graph")
    
    async def resume(self, message: str, session_id: str) -> Dict[str, Any]:
        """Resume doctor matching graph with user's answer."""
        from app.graphs.doctor_matching_graph.graph import doctor_matching_graph
        
        config = self.get_config(session_id)
        result = await doctor_matching_graph.ainvoke(Command(resume=message), config=config)
        
        return result
    
    async def execute(self, message: str, state: SessionState, intent_result: Dict, risk_result: Dict) -> Dict[str, Any]:
        """Execute simplified doctor matching graph."""
        from app.graphs.doctor_matching_graph.graph import doctor_matching_graph

        # Check for handoff data from previous graph (may be empty if called directly)
        handoff_data = state.handoff_data if state.handoff_data else {}
        
        logger.info(f"[DoctorMatchingExecutor] Preparing to execute with handoff data: {state}")
        logger.info(f"[DoctorMatchingExecutor] Handoff data content: {message}")
        # Build session context for symptoms triage - ALWAYS pass this
        # This allows the graph to check conversation history even without handoff
        recent_messages = state.get_recent_messages(n=15)  # Increased to 15 for better context
        logger.info(f"[DoctorMatchingExecutor] Retrieved {recent_messages} recent messages for context")
        session_context = {
            "reported_symptoms": state.reported_symptoms,
            "recent_messages": [
                {"role": msg.role, "content": msg.content}
                for msg in recent_messages
            ],
            "user_location_city": state.user_location_city,
            "suggested_specialties": state.suggested_specialties
        }
        
        logger.info(f"[DoctorMatchingExecutor] Handoff data: {bool(handoff_data)}, Reported symptoms: {state.reported_symptoms}, Recent messages: {len(recent_messages)}")
        
        # Input state for doctor matching (expects handoff from symptoms graph)
        input_state = {
            # Session context from global state
            "session_context": session_context,
            
            # Input from symptoms graph handoff
            "structured_symptoms": handoff_data.get("structured_symptoms", []),
            "symptoms_summary": handoff_data.get("symptoms_summary", ""),
            
            # Will be populated by graph
            "recommended_specialties": [],
            "specialty_explanation": "",
            "doctor_search_results": [],
            "available_doctors": [],
            "final_response": "",
            "next_action": "complete",
            "booking_context": {}
        }
        
        config = self.get_config(state.session_id)
        logger.info(f"📍 Executing simplified {self.graph_name}")
        
        result = await doctor_matching_graph.ainvoke(input_state, config=config)
        
        # Check if emergency graph wants to prepend its response
        prepend_text = handoff_data.get("prepend_to_response", "")
        logger.info(f"[DoctorMatchingExecutor] Checking for prepend_to_response: {bool(prepend_text)}, final_response exists: {bool(result.get('final_response'))}")
        if prepend_text and result.get("final_response"):
            # Combine emergency first aid + doctor recommendations
            combined = f"{prepend_text}\n\n{result['final_response']}"
            result["final_response"] = combined
            logger.info("[DoctorMatchingExecutor] ✅ Prepended emergency response to doctor recommendations")
        elif prepend_text:
            logger.warning(f"[DoctorMatchingExecutor] ⚠️ prepend_to_response found but final_response missing in result")
        
        if "__interrupt__" in result:
            return self.handle_interrupt(result, state, intent_result, risk_result)
        else:
            # Store available doctors in session state for UI
            if result.get("available_doctors"):
                state.available_doctors = result["available_doctors"]
            if result.get("booking_context"):
                state.booking_context = result["booking_context"]
            
            return self.handle_completion(result, state, intent_result, risk_result)
    
    def _build_pause_metadata(self, interrupt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build doctor matching specific pause metadata."""
        return {
            "type": interrupt_data.get("type"),
            "doctors": interrupt_data.get("doctors"),
            "available_slots": interrupt_data.get("available_slots"),
            "booking_details": interrupt_data.get("booking_details")
        }
    
    def _build_completion_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Build doctor matching specific completion metadata."""
        return {
            "next_action": result.get("next_action"),
            "appointment_id": result.get("appointment_id"),
            "available_doctors": result.get("available_doctors", []),
            "booking_context": result.get("booking_context", {}),
            "selected_doctor": result.get("selected_doctor", {}).get("name"),
            "appointment_date": result.get("preferred_date"),
            "appointment_time": result.get("selected_time_slot")
        }
    
    def _get_default_completion_message(self) -> str:
        return "Thank you for using our doctor booking service."
