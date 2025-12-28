"""Dosha graph pipeline implementation."""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.graphs.dosha_graph.state import DoshaGraphState
from app.graphs.dosha_graph.nodes import (
    questionnaire_node,
    followup_node,
    dosha_inference_node,
    response_generator_node
)
from app.utils.logger import get_logger

logger = get_logger()


def should_ask_followup(state: DoshaGraphState) -> str:
    """Conditional edge: determine if we need follow-up questions.
    
    Returns:
        "followup" if confidence < threshold
        "dosha_inference" if confidence >= threshold
    """
    confidence = state.get("confidence_score", 0.0)
    threshold = state.get("confidence_threshold", 0.7)
    iteration = state.get("iteration_count", 0)
    max_iter = state.get("max_iterations", 5)
    
    if confidence < threshold and iteration < max_iter:
        logger.info(f"[should_ask_followup] Confidence {confidence:.2f} < {threshold}, routing to followup")
        return "followup"
    else:
        logger.info(f"[should_ask_followup] Confidence {confidence:.2f} >= {threshold}, routing to inference")
        return "dosha_inference"


def build_dosha_graph():
    """Build and compile the dosha graph with checkpointer.
    
    Returns:
        Compiled LangGraph dosha assessment workflow
    """
    logger.info("Building dosha graph...")
    
    # Create graph
    workflow = StateGraph(DoshaGraphState)
    
    # Add nodes
    workflow.add_node("questionnaire", questionnaire_node)
    workflow.add_node("followup", followup_node)
    workflow.add_node("dosha_inference", dosha_inference_node)
    workflow.add_node("response_generator", response_generator_node)
    
    # Define flow
    workflow.add_edge(START, "questionnaire")
    
    # Conditional edge: questionnaire → followup OR dosha_inference
    workflow.add_conditional_edges(
        "questionnaire",
        should_ask_followup,
        {
            "followup": "followup",
            "dosha_inference": "dosha_inference"
        }
    )
    
    # Note: followup_node uses Command(goto=...) to route itself
    # It can go back to questionnaire or forward to dosha_inference
    # So we don't need explicit edges from followup
    
    # Linear flow after inference
    workflow.add_edge("dosha_inference", "response_generator")
    workflow.add_edge("response_generator", END)
    
    # Compile with checkpointer for interrupt() support
    # Using MemorySaver for development (can switch to Redis checkpointer later)
    checkpointer = MemorySaver()
    compiled_graph = workflow.compile(checkpointer=checkpointer)
    
    logger.info("✅ Dosha graph compiled successfully")
    
    return compiled_graph


# Create singleton instance
dosha_graph = build_dosha_graph()

