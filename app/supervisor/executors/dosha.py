"""Dosha graph executor."""

from typing import Any, Dict

from langgraph.types import Command

from app.state.graph_state import SessionState
from app.supervisor.executors.base import GraphExecutor
from app.utils.logger import get_logger

logger = get_logger()


class DoshaGraphExecutor(GraphExecutor):
    """Executor for dosha graph."""
    
    def __init__(self):
        super().__init__("dosha_graph")
    
    async def resume(self, message: str, session_id: str) -> Dict[str, Any]:
        """Resume dosha graph with user's answer."""
        from app.graphs.dosha_graph.graph import dosha_graph
        
        config = self.get_config(session_id)
        result = await dosha_graph.ainvoke(Command(resume=message), config=config)
        
        return result
    
    async def execute(self, message: str, state: SessionState, intent_result: Dict, risk_result: Dict) -> Dict[str, Any]:
        """Execute dosha graph."""
        from app.graphs.dosha_graph.graph import dosha_graph
        
        input_state = {
            "user_message": message,
            "session_id": state.session_id,
            "answers_collected": {},
            "confidence_score": 0.0,
            "confidence_threshold": 0.7,
            "questions_asked": [],
            "needs_more_info": True,
            "missing_areas": [],
            "iteration_count": 0,
            "max_iterations": 5,
            "vata_score": None,
            "pitta_score": None,
            "kapha_score": None,
            "dominant_dosha": None,
            "dosha_explanation": None,
            "final_response": None,
            "safety_flags": [],
            "next_action": "complete"
        }
        
        config = self.get_config(state.session_id)
        logger.info(f"📍 Executing {self.graph_name}")
        
        result = await dosha_graph.ainvoke(input_state, config=config)
        
        if "__interrupt__" in result:
            return self.handle_interrupt(result, state, intent_result, risk_result)
        else:
            return self.handle_completion(result, state, intent_result, risk_result)
    
    def _build_pause_metadata(self, interrupt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build dosha-specific pause metadata."""
        return {
            "type": interrupt_data.get("type"),
            "missing_areas": interrupt_data.get("missing_areas", []),
            "confidence": interrupt_data.get("confidence", 0.0),
            "iteration": interrupt_data.get("iteration", 0)
        }
    
    def _build_completion_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Build dosha-specific completion metadata."""
        return {
            "next_action": result.get("next_action"),
            "vata_score": result.get("vata_score"),
            "pitta_score": result.get("pitta_score"),
            "kapha_score": result.get("kapha_score"),
            "dominant_dosha": result.get("dominant_dosha"),
            "safety_flags": result.get("safety_flags", [])
        }
    
    def _get_default_completion_message(self) -> str:
        return "Thank you for completing the dosha assessment."
