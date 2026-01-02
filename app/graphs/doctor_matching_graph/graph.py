"""Doctor matching graph pipeline."""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.graphs.doctor_matching_graph.state import DoctorMatchingState
from app.graphs.doctor_matching_graph.nodes import (
    specialty_mapper_node,
    doctor_search_node
)
from app.utils.logger import get_logger

logger = get_logger()


def build_doctor_matching_graph():
    """Build and compile the doctor matching graph.
    
    Simple 2-node flow for handoff cases only:
    1. specialty_mapper_node: Map symptoms → Ayurvedic specialties (LLM)
    2. doctor_search_node: Search doctors and present results (Tool + LLM)
    
    Note: This graph should ONLY be called via handoff from symptoms graph.
    Direct intent routing should go to symptoms graph first.
    
    Returns:
        Compiled LangGraph workflow with checkpointer
    """
    logger.info("Building doctor matching graph...")
    
    # Create graph
    workflow = StateGraph(DoctorMatchingState)
    
    # Add 2 nodes
    workflow.add_node("specialty_mapper", specialty_mapper_node)
    workflow.add_node("doctor_search", doctor_search_node)
    
    # Simple linear flow
    workflow.add_edge(START, "specialty_mapper")
    workflow.add_edge("specialty_mapper", "doctor_search")
    workflow.add_edge("doctor_search", END)
    
    # Compile with checkpointer
    checkpointer = MemorySaver()
    compiled_graph = workflow.compile(checkpointer=checkpointer)
    
    logger.info("✅ Doctor matching graph compiled (2 nodes: specialty_mapper → doctor_search)")
    
    return compiled_graph


# Create singleton instance
doctor_matching_graph = build_doctor_matching_graph()

