"""Symptoms graph pipeline implementation."""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.graphs.symptoms_graph.state import SymptomsGraphState
from app.graphs.symptoms_graph.nodes import (
    symptom_triage_node,
    followup_node,
    response_generator_node
)
from app.utils.logger import get_logger

logger = get_logger()


def should_ask_followup(state: SymptomsGraphState) -> str:
    """Conditional edge: determine if we need follow-up questions.
    
    Returns:
        "followup" if we need more info
        "response_generator" if we have enough info
    """
    needs_more = state.get("needs_more_info", False)
    iteration = state.get("iteration_count", 0)
    max_iter = state.get("max_iterations", 3)
    
    if needs_more and iteration < max_iter:
        logger.info(f"[should_ask_followup] Routing to followup (iteration {iteration}/{max_iter})")
        return "followup"
    else:
        logger.info("[should_ask_followup] Routing to response_generator")
        return "response_generator"


def build_symptoms_graph():
    """Build and compile the symptoms graph with checkpointer.
    
    Returns:
        Compiled LangGraph symptoms workflow
    """
    logger.info("Building symptoms graph...")
    
    # Create graph
    workflow = StateGraph(SymptomsGraphState)
    
    # Add nodes
    workflow.add_node("symptom_triage", symptom_triage_node)
    workflow.add_node("followup", followup_node)
    workflow.add_node("response_generator", response_generator_node)
    
    # Define flow
    workflow.add_edge(START, "symptom_triage")
    
    # Conditional edge: triage → followup OR response_generator
    workflow.add_conditional_edges(
        "symptom_triage",
        should_ask_followup,
        {
            "followup": "followup",
            "response_generator": "response_generator"
        }
    )
    
    # Note: followup_node uses Command(goto=...) to route itself
    # It can go back to symptom_triage or forward to response_generator
    # So we don't need explicit edges from followup
    
    workflow.add_edge("response_generator", END)
    
    # Compile with checkpointer for interrupt() support
    # Using MemorySaver for development (can switch to Redis checkpointer later)
    checkpointer = MemorySaver()
    compiled_graph = workflow.compile(checkpointer=checkpointer)
    
    logger.info("✅ Symptoms graph compiled successfully")
    
    return compiled_graph


# Create singleton instance
symptoms_graph = build_symptoms_graph()
