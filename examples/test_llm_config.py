"""
Quick test to verify LLM configuration is working.
"""

import asyncio
from app.config.llm import LLMConfig
from app.constants.openai_constants import OpenaiModels


async def test_llm_config():
    """Test that LLMConfig works correctly."""
    print("\n🧪 Testing LLMConfig integration...")
    
    # Test 1: Create LLM instance
    print("\n1️⃣ Creating LLM instance...")
    llm_config = LLMConfig(model_name=OpenaiModels.GPT_4O_MINI.value, temperature=0.3)
    llm = llm_config.get_llm_instance()
    print(f"✅ LLM instance created: {llm.model_name}, temp={llm.temperature}")
    
    # Test 2: Simple invocation
    print("\n2️⃣ Testing LLM invocation...")
    try:
        response = await llm.ainvoke("Say 'Hello from the supervisor system!' in one sentence.")
        print(f"✅ LLM Response: {response.content[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure OPENAI_API_KEY is set in .env file")
        return False
    
    print("\n✅ All tests passed! LLMConfig is working correctly.")
    return True


if __name__ == "__main__":
    asyncio.run(test_llm_config())
