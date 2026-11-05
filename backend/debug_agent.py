#!/usr/bin/env python3
"""Debug test for agent router"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load env first
from dotenv import load_dotenv
load_dotenv()

async def test():
    try:
        from app.router.agent_router import AgentRouter
        print("✓ Imported AgentRouter")
        
        payload = {"topic": "AI automation tools"}
        print(f"✓ Testing with payload: {payload}")
        print(f"✓ GEMINI_API_KEY is set: {'GEMINI_API_KEY' in os.environ}")
        
        result = await AgentRouter.run_agent("research", payload)
        print(f"✓ Result: {result}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
