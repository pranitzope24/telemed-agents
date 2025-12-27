"""
Test script for Supervisor integration.

Tests various scenarios including:
- Normal symptom check
- Emergency detection
- Different intent types
- Session continuity
"""

import asyncio
import os
from dotenv import load_dotenv
from app.state.graph_state import SessionState
from app.supervisor.supervisor_graph import run_supervisor
from app.memory.session_memory import save_session_state, load_session_state
import uuid

# Load environment variables
load_dotenv()


async def test_scenario(description: str, message: str, session_id: str = None):
    """Test a single scenario."""
    print("\n" + "="*80)
    print(f"TEST: {description}")
    print("="*80)
    print(f"Message: {message}")
    
    # Load or create session
    if session_id:
        state = load_session_state(session_id)
        if not state:
            state = SessionState(session_id=session_id)
    else:
        session_id = f"test_{uuid.uuid4().hex[:8]}"
        state = SessionState(session_id=session_id)
    
    # Add user message
    state.add_message("user", message)
    
    # Run supervisor
    try:
        result = await run_supervisor(message, state)
        
        # Add response to state
        state.add_message("assistant", result["response"])
        
        # Save state
        save_session_state(state)
        
        # Display results
        print(f"\n✅ Result:")
        print(f"   Intent: {result.get('intent')}")
        print(f"   Risk: {result.get('risk')}")
        print(f"   Graph: {result.get('graph')}")
        print(f"   Confidence: {result.get('metadata', {}).get('intent_confidence', 'N/A')}")
        print(f"\n💬 Response Preview:")
        print(f"   {result['response'][:200]}...")
        
        if result.get('metadata', {}).get('emergency_keywords'):
            print(f"\n🚨 Emergency Keywords Detected: {result['metadata']['emergency_keywords']}")
        
        return session_id, state, result
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return session_id, state, None


async def main():
    """Run all test scenarios."""
    print("\n" + "🧪 "*20)
    print("SUPERVISOR INTEGRATION TEST SUITE")
    print("🧪 "*20)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  WARNING: OPENAI_API_KEY not set in .env file")
        print("   LLM-based classification will use fallback methods")
    
    # Test 1: Simple symptom check
    await test_scenario(
        "Simple Symptom Check",
        "I have a mild headache and feeling tired"
    )
    
    # Test 2: Emergency detection (keyword-based)
    await test_scenario(
        "Emergency Detection - Chest Pain",
        "I'm having severe chest pain and difficulty breathing"
    )
    
    # Test 3: Dosha assessment
    await test_scenario(
        "Dosha Assessment Request",
        "I want to know my Ayurvedic dosha type"
    )
    
    # Test 4: Doctor booking
    await test_scenario(
        "Doctor Booking Request",
        "Can you help me book an appointment with a cardiologist?"
    )
    
    # Test 5: Prescription query
    await test_scenario(
        "Prescription Refill",
        "I need to refill my blood pressure medication prescription"
    )
    
    # Test 6: Follow-up/Progress
    await test_scenario(
        "Treatment Follow-up",
        "I want to track my progress from last week's consultation"
    )
    
    # Test 7: Session continuity
    print("\n" + "-"*80)
    print("Testing session continuity...")
    print("-"*80)
    
    session_id, state, _ = await test_scenario(
        "First message in conversation",
        "Hi, I've been having stomach pain",
        session_id=None  # New session
    )
    
    # Continue in same session
    await test_scenario(
        "Follow-up in same session",
        "It started yesterday after eating",
        session_id=session_id
    )
    
    # Test 8: Emergency override
    await test_scenario(
        "Emergency with Stroke Keywords",
        "I can't feel my left arm and I'm having trouble speaking"
    )
    
    print("\n" + "="*80)
    print("✨ TEST SUITE COMPLETED")
    print("="*80)
    print("\nNext steps:")
    print("1. Check that intents are classified correctly")
    print("2. Verify risk levels are appropriate")
    print("3. Confirm emergency cases show warnings")
    print("4. Review metadata for classification reasoning")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
