"""Symptoms graph executor."""

from typing import Any, Dict, List

from langgraph.types import Command

from app.state.graph_state import SessionState
from app.supervisor.executors.base import GraphExecutor
from app.utils.logger import get_logger

logger = get_logger()


class SymptomsGraphExecutor(GraphExecutor):
    """Executor for symptoms graph."""
    
    def __init__(self):
        super().__init__("symptoms_graph")
    
    async def resume(self, message: str, session_id: str) -> Dict[str, Any]:
        """Resume symptoms graph with user's answer."""
        from app.graphs.symptoms_graph.graph import symptoms_graph
        
        config = self.get_config(session_id)
        result = await symptoms_graph.ainvoke(Command(resume=message), config=config)
        
        return result
    
    async def _handle_result(self, result: Dict[str, Any], state: SessionState, 
                            intent_result: Dict = None, risk_result: Dict = None) -> Dict[str, Any]:
        """Handle graph result - check for handoff or completion.
        
        This method is called from both execute() and after processing resume results.
        """
        # Check if we need to handoff to doctor_matching_graph
        next_action = result.get("next_action")
        if next_action == "handoff_doctor":
            logger.info("[SymptomsGraphExecutor] Handoff to doctor_matching_graph requested")
            
            # Prepare handoff data
            state.handoff_data = {
                "source": "symptoms_graph",
                "symptoms_summary": self._build_symptoms_summary(result),
                "structured_symptoms": result.get("structured_symptoms", []),
                "urgency_level": self._determine_urgency(result)
            }
            
            # Update session state
            state.reported_symptoms = [
                symp.get("name", "") for symp in result.get("structured_symptoms", [])
            ]
            
            # Complete current graph
            state.complete_graph()
            
            # Start doctor matching graph
            state.start_graph("doctor_matching_graph")
            
            # Execute doctor matching graph
            from app.supervisor.executors import get_graph_executor
            doctor_executor = get_graph_executor("doctor_matching_graph")
            
            return await doctor_executor.execute(
                message="", 
                state=state, 
                intent_result=intent_result, 
                risk_result=risk_result
            )
        
        # No handoff, just complete normally
        return self.handle_completion(result, state, intent_result, risk_result)
    
    async def execute(self, message: str, state: SessionState, intent_result: Dict, risk_result: Dict) -> Dict[str, Any]:
        """Execute symptoms graph."""
        from app.graphs.symptoms_graph.graph import symptoms_graph
        
        input_state = {
            "user_message": message,
            "session_id": state.session_id,
            "raw_symptoms": "",  # Will be set by first triage node
            "structured_symptoms": [],
            "questions_asked": [],
            "answers_collected": [],  # List, not dict
            "needs_more_info": False,
            "missing_info": [],
            "iteration_count": 0,
            "max_iterations": 3,
            "final_response": None,
            "next_action": "complete"
        }
        
        config = self.get_config(state.session_id)
        logger.info(f"📍 Executing {self.graph_name}")
        
        result = await symptoms_graph.ainvoke(input_state, config=config)
        
        if "__interrupt__" in result:
            return self.handle_interrupt(result, state, intent_result, risk_result)
        else:
            # Use _handle_result to check for handoff or complete
            return await self._handle_result(result, state, intent_result, risk_result)
    
    def _build_symptoms_summary(self, result: Dict[str, Any]) -> str:
        """Build a summary of symptoms for handoff."""
        symptoms = result.get("structured_symptoms", [])
        if not symptoms:
            return result.get("raw_symptoms", "")
        
        summary_parts = []
        for symp in symptoms:
            parts = [symp.get("name", "")]
            if symp.get("severity"):
                parts.append(f"({symp['severity']})")
            if symp.get("duration"):
                parts.append(f"for {symp['duration']}")
            summary_parts.append(" ".join(parts))
        
        return ", ".join(summary_parts)
    
    
    def _determine_urgency(self, result: Dict[str, Any]) -> str:
        """Determine urgency level from symptoms."""
        symptoms = result.get("structured_symptoms", [])
        
        for symp in symptoms:
            if symp.get("severity") == "severe":
                return "high"
            elif symp.get("severity") == "moderate":
                return "medium"
        
        return "low"
    
    def _build_pause_metadata(self, interrupt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build symptoms-specific pause metadata."""
        return {
            "type": interrupt_data.get("type"),
            "missing_info": interrupt_data.get("missing_info", []),
            "iteration": interrupt_data.get("iteration", 0),
            "symptoms_summary": interrupt_data.get("symptoms_summary"),
            "structured_symptoms": interrupt_data.get("structured_symptoms")
        }
    
    def _build_completion_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Build symptoms-specific completion metadata."""
        return {
            "next_action": result.get("next_action"),
            "structured_symptoms": result.get("structured_symptoms", [])
        }
    
    def _get_default_completion_message(self) -> str:
        return "Thank you for sharing your symptoms."
