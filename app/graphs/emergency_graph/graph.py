"""Emergency graph pipeline implementation."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.graphs.emergency_graph.nodes import (
    classify_emergency_intent,
    finalize_and_end,
    generate_first_aid_response,
)
from app.graphs.emergency_graph.state import EmergencyGraphState
from app.utils.logger import get_logger

logger = get_logger()


def build_emergency_graph():
	"""Build and compile the emergency assistance graph.
    
	Flow: START → classify_emergency_intent → generate_first_aid_response → finalize_and_end → END
	"""
	logger.info("Building emergency graph...")

	workflow = StateGraph(EmergencyGraphState)

	# Nodes
	workflow.add_node("classifier", classify_emergency_intent)
	workflow.add_node("first_aid", generate_first_aid_response)
	workflow.add_node("finalize", finalize_and_end)

	# Edges
	workflow.add_edge(START, "classifier")
	workflow.add_edge("classifier", "first_aid")
	workflow.add_edge("first_aid", "finalize")
	workflow.add_edge("finalize", END)

	# Compile with checkpointer
	checkpointer = MemorySaver()
	compiled = workflow.compile(checkpointer=checkpointer)

	logger.info("✅ Emergency graph compiled successfully")
	return compiled


# Singleton instance
emergency_graph = build_emergency_graph()
