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
        }

        config = self.get_config(session_id)
        logger.info(f"📍 Executing {self.graph_name}")

        result = await emergency_graph.ainvoke(input_state, config=config)

        # Emergency graph is linear; handle as completion
        return self.handle_completion(result, state, intent_result, risk_result)

    def _get_default_completion_message(self) -> str:
        return "Emergency guidance provided. Please seek immediate medical attention."
