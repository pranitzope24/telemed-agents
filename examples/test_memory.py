"""Simple test to verify memory layer implementation."""

from app.state.graph_state import SessionState
from app.memory.session_memory import (
    save_session_state,
    load_session_state,
    delete_session_state,
    session_exists
)

print("="*60)
print("MEMORY LAYER TEST")
print("="*60)

# Test 1: Create and save a session
print("\n1️⃣  Creating new session...")
state = SessionState(
    session_id="test_123",
    user_id="user_456"
)
state.add_message("user", "I have a headache")
state.add_message("assistant", "Tell me more about it")
state.current_intent = "symptom"
state.risk_level = "medium"

print(f"   Session ID: {state.session_id}")
print(f"   Messages: {state.message_count}")
print(f"   Intent: {state.current_intent}")

# Test 2: Save to memory
print("\n2️⃣  Saving session to memory...")
success = save_session_state(state)
print(f"   Save successful: {success}")

# Test 3: Check if exists
print("\n3️⃣  Checking if session exists...")
exists = session_exists("test_123")
print(f"   Session exists: {exists}")

# Test 4: Load from memory
print("\n4️⃣  Loading session from memory...")
loaded_state = load_session_state("test_123")
if loaded_state:
    print(f"   ✅ Loaded successfully!")
    print(f"   Session ID: {loaded_state.session_id}")
    print(f"   Messages: {loaded_state.message_count}")
    print(f"   Intent: {loaded_state.current_intent}")
    print(f"   Risk level: {loaded_state.risk_level}")
else:
    print(f"   ❌ Failed to load")

# Test 5: Modify and save again
if loaded_state:
    print("\n5️⃣  Adding more messages and saving...")
    loaded_state.add_message("user", "It's been 3 days")
    loaded_state.add_message("assistant", "That's concerning")
    save_session_state(loaded_state)
    print(f"   Total messages now: {loaded_state.message_count}")

# Test 6: Load again to verify persistence
print("\n6️⃣  Loading again to verify...")
final_state = load_session_state("test_123")
if final_state:
    print(f"   ✅ Messages persisted: {final_state.message_count}")
    print("\n   Recent messages:")
    for msg in final_state.get_recent_messages(3):
        print(f"      {msg.role}: {msg.content}")

# Test 7: Delete session
print("\n7️⃣  Deleting session...")
deleted = delete_session_state("test_123")
print(f"   Delete successful: {deleted}")

# Test 8: Verify deletion
print("\n8️⃣  Verifying deletion...")
exists_after = session_exists("test_123")
print(f"   Session exists after delete: {exists_after}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
