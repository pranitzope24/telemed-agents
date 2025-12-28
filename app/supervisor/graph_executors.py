"""Graph executors for different subgraphs.

DEPRECATED: This file is kept for backward compatibility.
Import from app.supervisor.executors instead.

New modular structure:
- app.supervisor.executors.base - GraphExecutor base class
- app.supervisor.executors.symptoms - SymptomsGraphExecutor
- app.supervisor.executors.dosha - DoshaGraphExecutor
- app.supervisor.executors.emergency - EmergencyGraphExecutor
- app.supervisor.executors.doctor_matching - DoctorMatchingGraphExecutor
"""

# Re-export everything from the new modular structure
from app.supervisor.executors import (
    GraphExecutor,
    SymptomsGraphExecutor,
    DoshaGraphExecutor,
    EmergencyGraphExecutor,
    DoctorMatchingGraphExecutor,
    get_graph_executor,
    GRAPH_EXECUTORS,
)

__all__ = [
    "GraphExecutor",
    "SymptomsGraphExecutor",
    "DoshaGraphExecutor",
    "EmergencyGraphExecutor",
    "DoctorMatchingGraphExecutor",
    "get_graph_executor",
    "GRAPH_EXECUTORS",
]
