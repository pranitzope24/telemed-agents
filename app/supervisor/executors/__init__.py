"""Graph executors - exports all executor classes and factory function."""

from app.supervisor.executors.base import GraphExecutor
from app.supervisor.executors.symptoms import SymptomsGraphExecutor
from app.supervisor.executors.dosha import DoshaGraphExecutor
from app.supervisor.executors.emergency import EmergencyGraphExecutor
from app.supervisor.executors.doctor_matching import DoctorMatchingGraphExecutor

# Registry of all graph executors
GRAPH_EXECUTORS = {
    "symptoms_graph": SymptomsGraphExecutor(),
    "dosha_graph": DoshaGraphExecutor(),
    "doctor_matching_graph": DoctorMatchingGraphExecutor(),
    "emergency_graph": EmergencyGraphExecutor(),
}


def get_graph_executor(graph_name: str) -> GraphExecutor:
    """Get the appropriate graph executor.
    
    Args:
        graph_name: Name of the graph (e.g., 'symptoms_graph')
        
    Returns:
        GraphExecutor instance for the specified graph
        
    Raises:
        ValueError: If no executor found for the graph
    """
    executor = GRAPH_EXECUTORS.get(graph_name)
    if not executor:
        raise ValueError(f"No executor found for graph: {graph_name}")
    return executor


__all__ = [
    "GraphExecutor",
    "SymptomsGraphExecutor",
    "DoshaGraphExecutor",
    "EmergencyGraphExecutor",
    "DoctorMatchingGraphExecutor",
    "get_graph_executor",
    "GRAPH_EXECUTORS",
]
