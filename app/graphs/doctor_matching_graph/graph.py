"""Doctor matching graph pipeline - Simplified 3-node flow."""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.graphs.doctor_matching_graph.state import DoctorMatchingState
from app.graphs.doctor_matching_graph.nodes import (
    symptoms_triage_node,
    specialty_recommendation_node,
    doctor_search_node
)
from app.utils.logger import get_logger

logger = get_logger()


def build_doctor_matching_graph():
    """Build and compile the simplified doctor matching graph.
    
    Flow:
    1. symptoms_triage_node: Check/collect symptoms
    2. specialty_recommendation_node: Map to specialties + collect location
    3. doctor_search_node: Search and present doctors (END)
    
    Returns:
        Compiled LangGraph workflow with checkpointer for interrupts
    """
    logger.info("Building simplified doctor matching graph...")
    
    # Create graph
    workflow = StateGraph(DoctorMatchingState)
    
    # Add 3 nodes only
    workflow.add_node("symptoms_triage", symptoms_triage_node)
    workflow.add_node("specialty_recommendation", specialty_recommendation_node)
    workflow.add_node("doctor_search", doctor_search_node)
    
    # Simple linear flow
    workflow.add_edge(START, "symptoms_triage")
    # symptoms_triage uses Command(goto=...) to route to specialty_recommendation
    # specialty_recommendation uses Command(goto=...) to route to doctor_search
    workflow.add_edge("doctor_search", END)
    
    # Compile with checkpointer for interrupt() support
    checkpointer = MemorySaver()
    compiled_graph = workflow.compile(checkpointer=checkpointer)
    
    logger.info("✅ Simplified doctor matching graph compiled (3 nodes)")
    
    return compiled_graph


# Create singleton instance
doctor_matching_graph = build_doctor_matching_graph()

