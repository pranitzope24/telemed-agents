"""Example usage of SessionState."""

from app.state.graph_state import SessionState, Message
import json

# ===== Create a new session =====
state = SessionState(
    session_id="sess_abc123",
    user_id="user_456",
    user_name="John Doe"
)

print("=== New Session Created ===")
print(f"Session ID: {state.session_id}")
print(f"Status: {state.status}")
print()

# ===== Add conversation messages =====
state.add_message("user", "I have a headache for 3 days")
state.add_message("assistant", "Can you describe the severity and location?")

print("=== After Adding Messages ===")
print(f"Message count: {state.message_count}")
print(f"Recent messages: {len(state.get_recent_messages(2))}")
print()

# ===== Set intent and routing =====
state.current_intent = "symptom"
state.risk_level = "medium"
state.reported_symptoms = ["headache"]
state.triage_outcome = "needs_doctor"

print("=== After Classification ===")
print(f"Intent: {state.current_intent}")
print(f"Risk: {state.risk_level}")
print(f"Symptoms: {state.reported_symptoms}")
print()

# ===== Start a graph =====
state.start_graph("symptoms_graph")
state.active_node = "triage_node"

print("=== Graph Execution Started ===")
print(f"Active graph: {state.active_graph}")
print(f"Active node: {state.active_node}")
print(f"Graph started at: {state.graph_started_at}")
print()

# ===== Add safety flags =====
state.add_safety_flag("requires_medical_attention")

print("=== Safety Flags ===")
print(f"Flags: {state.safety_flags}")
print(f"Is emergency: {state.is_emergency()}")
print()

# ===== Handoff data for next graph =====
state.handoff_data = {
    "symptoms": state.reported_symptoms,
    "specialties": ["neurology", "general_practitioner"]
}

state.complete_graph()
state.start_graph("doctor_matching_graph")

print("=== After Graph Handoff ===")
print(f"Previous graph: {state.previous_graph}")
print(f"Current graph: {state.active_graph}")
print(f"Graph history: {state.graph_history}")
print(f"Handoff data keys: {list(state.handoff_data.keys())}")
print()

# ===== Get conversation summary =====
print("=== Conversation Summary ===")
print(state.get_conversation_summary())
print()

# ===== Serialize to JSON =====
print("=== JSON Serialization ===")
json_str = state.model_dump_json(indent=2)
print(json_str[:300] + "...")
print()

# ===== Deserialize from JSON =====
restored_state = SessionState.model_validate_json(json_str)
print("=== Restored from JSON ===")
print(f"Session ID: {restored_state.session_id}")
print(f"Message count: {restored_state.message_count}")
print(f"Active graph: {restored_state.active_graph}")
print()

# ===== Emergency scenario =====
emergency_state = SessionState(
    session_id="sess_emergency_001",
    user_id="user_789"
)

emergency_state.add_message("user", "I have severe chest pain and can't breathe")
emergency_state.current_intent = "emergency"
emergency_state.risk_level = "emergency"
emergency_state.emergency_keywords_detected = ["chest pain", "can't breathe"]
emergency_state.requires_human_review = True

print("=== Emergency Session ===")
print(f"Is emergency: {emergency_state.is_emergency()}")
print(f"Risk level: {emergency_state.risk_level}")
print(f"Emergency keywords: {emergency_state.emergency_keywords_detected}")
print(f"Requires review: {emergency_state.requires_human_review}")
