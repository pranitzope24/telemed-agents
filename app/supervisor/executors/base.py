"""Base graph executor class."""

from typing import Any, Dict

from app.state.graph_state import SessionState
from app.utils.logger import get_logger

logger = get_logger()


class GraphExecutor:
    """Base class for graph executors."""
    
    def __init__(self, graph_name: str):
        self.graph_name = graph_name
    
    def get_thread_id(self, session_id: str) -> str:
        """Generate thread ID for this graph."""
        return f"{session_id}_{self.graph_name.replace('_graph', '')}"
    
    def get_config(self, session_id: str) -> Dict[str, Any]:
        """Get LangGraph config with thread ID."""
        return {
            "configurable": {
                "thread_id": self.get_thread_id(session_id)
            }
        }
    
    async def resume(self, message: str, session_id: str) -> Dict[str, Any]:
        """Resume an interrupted graph."""
        raise NotImplementedError
    
    async def execute(self, message: str, state: SessionState, intent_result: Dict, risk_result: Dict) -> Dict[str, Any]:
        """Execute the graph for the first time."""
        raise NotImplementedError
    
    def handle_interrupt(self, result: Dict[str, Any], state: SessionState, intent_result: Dict = None, risk_result: Dict = None) -> Dict[str, Any]:
        """Handle graph interruption (pause)."""
        interrupt_data = result["__interrupt__"][0].value
        state.waiting_for_user_input = True
        state.pending_question = interrupt_data["question"]
        
        logger.info(f"⏸️  {self.graph_name} paused: {interrupt_data['question']}")
        
        response = {
            "action": "paused",
            "graph": self.graph_name,
            "response": interrupt_data["question"],
            "metadata": self._build_pause_metadata(interrupt_data)
        }
        
        # Add classification metadata if available
        if intent_result:
            response["metadata"]["intent_confidence"] = intent_result.get("confidence")
        if risk_result:
            response["metadata"]["risk_reasoning"] = risk_result.get("reasoning")
        
        return response
    
    def handle_completion(self, result: Dict[str, Any], state: SessionState, intent_result: Dict = None, risk_result: Dict = None) -> Dict[str, Any]:
        """Handle graph completion."""
        state.waiting_for_user_input = False
        state.pending_question = None
        state.complete_graph()
        
        logger.info(f"✅ {self.graph_name} completed")
        
        response = {
            "action": "completed",
            "graph": self.graph_name,
            "response": result.get("final_response", self._get_default_completion_message()),
            "metadata": self._build_completion_metadata(result)
        }
        
        # Add classification metadata if available
        if intent_result:
            response["metadata"]["intent_confidence"] = intent_result.get("confidence")
        if risk_result:
            response["metadata"]["risk_reasoning"] = risk_result.get("reasoning")
        
        return response
    
    def _build_pause_metadata(self, interrupt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build metadata for paused state. Override in subclasses."""
        return {
            "type": interrupt_data.get("type"),
            "iteration": interrupt_data.get("iteration", 0)
        }
    
    def _build_completion_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Build metadata for completed state. Override in subclasses."""
        return {
            "next_action": result.get("next_action")
        }
    
    def _get_default_completion_message(self) -> str:
        """Get default completion message. Override in subclasses."""
        return f"Thank you for using {self.graph_name}."
