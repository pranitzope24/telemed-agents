"""Graph executors for different subgraphs."""

from typing import Dict, Any
from langgraph.types import Command
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
    
    async def execute(self, message: str, state: SessionState, intent_result: Dict, risk_result: Dict) -> Dict[str, Any]:
        """Execute symptoms graph."""
        from app.graphs.symptoms_graph.graph import symptoms_graph
        
        input_state = {
            "user_message": message,
            "session_id": state.session_id,
            "raw_symptoms": message,
            "structured_symptoms": [],
            "questions_asked": [],
            "answers_collected": {},
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
            return self.handle_completion(result, state, intent_result, risk_result)
    
    def _build_pause_metadata(self, interrupt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build symptoms-specific pause metadata."""
        return {
            "type": interrupt_data.get("type"),
            "missing_info": interrupt_data.get("missing_info", []),
            "iteration": interrupt_data.get("iteration", 0)
        }
    
    def _build_completion_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Build symptoms-specific completion metadata."""
        return {
            "next_action": result.get("next_action"),
            "structured_symptoms": result.get("structured_symptoms", [])
        }
    
    def _get_default_completion_message(self) -> str:
        return "Thank you for sharing your symptoms."


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


# Registry of all graph executors
GRAPH_EXECUTORS = {
    "symptoms_graph": SymptomsGraphExecutor(),
    "dosha_graph": DoshaGraphExecutor(),
}


def get_graph_executor(graph_name: str) -> GraphExecutor:
    """Get the appropriate graph executor."""
    executor = GRAPH_EXECUTORS.get(graph_name)
    if not executor:
        raise ValueError(f"No executor found for graph: {graph_name}")
    return executor
