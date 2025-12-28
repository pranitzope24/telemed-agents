"""Supervisor orchestrator for intent classification and routing."""

from typing import Dict, Any
from app.state.graph_state import SessionState
from app.supervisor.intent_classifier import classify_intent
from app.supervisor.risk_classifier import classify_risk
from app.supervisor.router import route_to_graph
from app.supervisor.graph_executors import get_graph_executor, GRAPH_EXECUTORS
from app.utils.logger import get_logger

logger = get_logger()


async def handle_graph_resume(message: str, state: SessionState) -> Dict[str, Any]:
    """Handle resuming an active graph with user's answer.
    
    Args:
        message: User's answer to the pending question
        state: Current session state
        
    Returns:
        Response dict with action, graph, response, and metadata
    """
    logger.info(f"↩️  Resuming {state.active_graph}")
    
    try:
        # Get the appropriate executor
        executor = get_graph_executor(state.active_graph)
        
        # Resume the graph
        result = await executor.resume(message, state.session_id)
        
        # Handle the result (pause, handoff, or completion)
        if "__interrupt__" in result:
            return executor.handle_interrupt(result, state)
        else:
            # Check if executor has custom result handling (for handoffs)
            if hasattr(executor, '_handle_result'):
                # Executor will handle handoff logic (e.g., symptoms → doctor matching)
                return await executor._handle_result(result, state)
            else:
                # Standard completion
                return executor.handle_completion(result, state)
            
    except ValueError as e:
        logger.error(f"Unknown graph type: {state.active_graph}")
        # Fallback: clear state and continue
        state.waiting_for_user_input = False
        state.complete_graph()
        return {
            "action": "error",
            "graph": state.active_graph,
            "response": "I encountered an error. Let's start fresh. How can I help you?",
            "metadata": {"error": str(e)}
        }


async def handle_new_request(message: str, state: SessionState) -> Dict[str, Any]:
    """Handle a new user request (classify, route, and execute).
    
    Args:
        message: User message
        state: Current session state
        
    Returns:
        Response dict with action, graph, response, and metadata
    """
    # Step 1: Classify Intent
    logger.info("📍 Step 1: Intent Classification")
    intent_result = await classify_intent(message, state.messages)
    
    # Step 2: Assess Risk
    logger.info("📍 Step 2: Risk Assessment")
    risk_result = await classify_risk(message)
    
    # Step 3: Route to Graph
    logger.info("📍 Step 3: Routing")
    target_graph = route_to_graph(intent_result["intent"], risk_result["risk_level"])
    
    # Step 4: Update Session State
    logger.info("📍 Step 4: Updating Session State")
    _update_session_state(state, intent_result, risk_result, target_graph)
    
    # Step 5: Execute the graph
    logger.info(f"📍 Step 5: Executing {target_graph}")
    
    # All intents route to implemented graphs
    executor = get_graph_executor(target_graph)
    return await executor.execute(message, state, intent_result, risk_result)


def _update_session_state(state: SessionState, intent_result: Dict, risk_result: Dict, target_graph: str):
    """Update session state with classification results.
    
    Args:
        state: Session state to update
        intent_result: Intent classification result
        risk_result: Risk assessment result
        target_graph: Target graph name
    """
    state.current_intent = intent_result["intent"]
    state.intent_confidence = intent_result["confidence"]
    state.risk_level = risk_result["risk_level"]
    
    # Add emergency keywords if detected
    if risk_result.get("emergency_keywords"):
        state.emergency_keywords_detected = risk_result["emergency_keywords"]
        state.add_safety_flag("emergency_keywords_detected")
        state.requires_human_review = True
    
    # Start the graph
    state.start_graph(target_graph)
    
    logger.info(
        f"✅ State updated: intent={state.current_intent}, "
        f"risk={state.risk_level}, graph={state.active_graph}"
    )


async def run_supervisor(message: str, state: SessionState) -> Dict[str, Any]:
    """Main supervisor orchestrator.
    
    Coordinates intent classification, risk assessment, and routing.
    Handles both new requests and resuming active graphs.
    
    Args:
        message: User message
        state: Current session state
        
    Returns:
        Dictionary with routing decision, response (or pause info), and metadata
    """
    logger.info("="*60)
    logger.info("🧠 SUPERVISOR: Starting orchestration...")
    logger.info("="*60)
    
    # Check if resuming an active graph
    if state.active_graph and state.waiting_for_user_input:
        return await handle_graph_resume(message, state)
    
    # Handle new request
    return await handle_new_request(message, state)
