"""Router for graph selection."""

from app.supervisor.constants import INTENT_TO_GRAPH
from app.utils.logger import get_logger

logger = get_logger()


def route_to_graph(intent: str, risk_level: str) -> str:
    """Route to appropriate graph based on intent and risk.
    
    Args:
        intent: Classified intent
        risk_level: Assessed risk level
        
    Returns:
        Graph name to execute
    """
    logger.info(f"🗺️  Router: Mapping intent='{intent}' + risk='{risk_level}' to graph...")
    
    # Emergency always takes priority
    if risk_level == "emergency":
        logger.warning("Emergency override: routing to emergency_graph")
        return "emergency_graph"
    
    # Map intent to graph
    graph_name = INTENT_TO_GRAPH.get(intent, "symptoms_graph")
    
    logger.info(f"✅ Routed to: {graph_name}")
    
    return graph_name
