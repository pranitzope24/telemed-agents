"""Emergency graph executor."""

from typing import Any, Dict

from langgraph.types import Command

from app.state.graph_state import SessionState
from app.supervisor.executors.base import GraphExecutor
from app.utils.logger import get_logger

logger = get_logger()


class EmergencyGraphExecutor(GraphExecutor):
    """Executor for emergency graph."""

    def __init__(self):
        super().__init__("emergency_graph")

    async def resume(self, message: str, session_id: str) -> Dict[str, Any]:
        """Resume emergency graph (no interrupts expected, but support resume)."""
        from app.graphs.emergency_graph.graph import emergency_graph
        
        config = self.get_config(session_id)
        # Emergency graph doesn't pause; forwarding resume as a fresh invoke
        result = await emergency_graph.ainvoke(Command(resume=message), config=config)
        return result

    async def _handle_result(self, result: Dict[str, Any], state: SessionState,
                            intent_result: Dict = None, risk_result: Dict = None) -> Dict[str, Any]:
        """Handle graph result - check for handoff to doctor or completion.
        
        This method is called after executing emergency graph.
        """
        # Check if we need to handoff to doctor_matching_graph
        next_action = result.get("next_action")
        if next_action == "handoff_doctor" and result.get("handoff_to_doctor"):
            logger.info("[EmergencyGraphExecutor] 🚨→🏥 Handoff to doctor_matching_graph requested")
            
            # IMPORTANT: Store the emergency first aid response before handoff
            emergency_first_aid = result.get("final_response", "")
            incident_summary = result.get("doctor_context", {}).get("incident_summary", "")
            emergency_type = result.get("doctor_context", {}).get("emergency_type", "unknown")
            
            # Prepare handoff data with emergency context as symptoms
            state.handoff_data = {
                "source": "emergency_graph",
                "emergency_type": emergency_type,
                "incident_summary": incident_summary,
                "risk_level": result.get("doctor_context", {}).get("risk_level", "emergency"),
                "detected_keywords": result.get("doctor_context", {}).get("detected_keywords", []),
                "urgency_level": "high",  # Emergency handoffs are always high urgency
                "requires_urgent_consultation": True,
                "first_aid_provided": True,
                "emergency_first_aid_response": emergency_first_aid,
                "prepend_to_response": emergency_first_aid,
                # Pass emergency as symptoms for doctor matching
                "symptoms_summary": f"Emergency: {incident_summary}",
                "structured_symptoms": [{
                    "name": f"{emergency_type} emergency",
                    "severity": "critical",
                    "description": incident_summary,
                    "urgency": "immediate"
                }]
            }
            
            # Complete current graph
            state.complete_graph()
            
            # Start doctor matching graph
            state.start_graph("doctor_matching_graph")
            
            logger.info("[EmergencyGraphExecutor] Starting doctor_matching_graph with emergency context")
            
            # Execute doctor matching graph
            from app.supervisor.executors import get_graph_executor
            doctor_executor = get_graph_executor("doctor_matching_graph")
            
            doctor_result = await doctor_executor.execute(
                message="",
                state=state,
                intent_result=intent_result,
                risk_result=risk_result
            )
            
            return doctor_result
        
        # No handoff, just complete normally
        return self.handle_completion(result, state, intent_result, risk_result)

    async def execute(self, message: str, state: SessionState, intent_result: Dict, risk_result: Dict) -> Dict[str, Any]:
        """Execute emergency graph with initial state."""
        from app.graphs.emergency_graph.graph import emergency_graph

        input_state = {
            "user_message": message,
            "session_id": state.session_id,
            "incident_summary": None,
            "emergency_type": None,
            "risk_level": None,
            "detected_keywords": [],
            "needs_911": False,
            "urgency_score": 0.0,
            "first_aid_instructions": None,
            "escalation_advice": None,
            "final_response": None,
            "safety_flags": [],
            "next_action": "complete",
            "completed": False,
            "handoff_to_doctor": False,
            "doctor_context": {}
        }

        config = self.get_config(state.session_id)
        logger.info(f"📍 Executing {self.graph_name}")

        result = await emergency_graph.ainvoke(input_state, config=config)
        logger.info("HERE??????????????????????????????????????")
        # Check for handoff or completion
        return await self._handle_result(result, state, intent_result, risk_result)

    def _get_default_completion_message(self) -> str:
        return "Emergency guidance provided. Please seek immediate medical attention."
