"""Supervisor orchestrator for intent classification and routing."""

from typing import Dict, Any
from app.state.graph_state import SessionState
from app.supervisor.intent_classifier import classify_intent
from app.supervisor.risk_classifier import classify_risk
from app.supervisor.router import route_to_graph
from app.supervisor.constants import MOCK_GRAPH_RESPONSES


async def run_supervisor(message: str, state: SessionState) -> Dict[str, Any]:
    """Main supervisor orchestrator.
    
    Coordinates intent classification, risk assessment, and routing.
    
    Args:
        message: User message
        state: Current session state
        
    Returns:
        Dictionary with routing decision, mock response, and metadata
    """
    print("\n" + "="*60)
    print("🧠 SUPERVISOR: Starting orchestration...")
    print("="*60)
    
    # Check if resuming an active graph
    if state.active_graph and state.waiting_for_user_input:
        print(f"\n↩️  Resuming active graph: {state.active_graph}")
        return {
            "action": "resume",
            "graph": state.active_graph,
            "node": state.active_node,
            "response": "Continuing with your request...",
            "metadata": {
                "resumed": True,
                "previous_graph": state.active_graph
            }
        }
    
    # Step 1: Classify Intent
    print("\n📍 Step 1: Intent Classification")
    intent_result = await classify_intent(message, state.messages)
    
    # Step 2: Assess Risk
    print("\n📍 Step 2: Risk Assessment")
    risk_result = await classify_risk(message)
    
    # Step 3: Route to Graph
    print("\n📍 Step 3: Routing")
    target_graph = route_to_graph(intent_result["intent"], risk_result["risk_level"])
    
    # Step 4: Update Session State
    print("\n📍 Step 4: Updating Session State")
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
    
    print(f"✅ State updated: intent={state.current_intent}, risk={state.risk_level}, graph={state.active_graph}")
    
    # Step 5: Get mock response for the graph
    mock_response = MOCK_GRAPH_RESPONSES.get(target_graph, "I'm here to help. How can I assist you?")
    
    print("\n" + "="*60)
    print("✨ SUPERVISOR: Orchestration complete")
    print("="*60)
    
    # Return routing decision with metadata
    return {
        "action": "new",
        "graph": target_graph,
        "intent": intent_result["intent"],
        "risk": risk_result["risk_level"],
        "response": mock_response,
        "metadata": {
            "intent_confidence": intent_result["confidence"],
            "intent_reasoning": intent_result.get("reasoning"),
            "risk_reasoning": risk_result.get("reasoning"),
            "urgency_score": risk_result.get("urgency_score"),
            "emergency_keywords": risk_result.get("emergency_keywords", []),
            "classification_method": {
                "intent": intent_result.get("method"),
                "risk": risk_result.get("method")
            }
        }
    }
