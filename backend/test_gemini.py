#!/usr/bin/env python3
"""
Test script to verify Gemini API connection and functionality
Run this before starting the backend to ensure everything is working
"""

import asyncio
import sys
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

async def test_gemini_connection():
    """Test if Gemini API connection works"""
    print("\n" + "="*60)
    print("Testing Gemini API Connection")
    print("="*60)
    
    try:
        from app.orchestrators.gemini_orchestrator import GeminiOrchestrator
        
        print("\n✓ Successfully imported GeminiOrchestrator")
        
        # Test basic connection
        print("\n📝 Testing basic text generation...")
        response = await GeminiOrchestrator.generate_text(
            "Say 'Gemini API is working!' in exactly those words.",
            max_tokens=20
        )
        print(f"✓ Response: {response}")
        
        # Test JSON mode
        print("\n📝 Testing JSON mode...")
        json_response = await GeminiOrchestrator.generate_text(
            'Return only valid JSON: {"status": "working", "test": true}',
            json_mode=True,
            max_tokens=50
        )
        print(f"✓ JSON Response: {json_response}")
        
        print("\n✓ All tests passed!")
        return True
        
    except ValueError as e:
        print(f"\n✗ Configuration Error: {str(e)}")
        print("\n📌 ACTION REQUIRED:")
        print("   1. Get your Gemini API key at: https://makersuite.google.com/app/apikey")
        print("   2. Add GEMINI_API_KEY to backend/.env")
        print("   3. Run this script again")
        return False
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_research_agent():
    """Test the Research Agent with Gemini"""
    print("\n" + "="*60)
    print("Testing Research Agent")
    print("="*60)
    
    try:
        from app.agents.research_agent import ResearchAgent
        
        print("\n✓ Successfully imported ResearchAgent")
        
        agent = ResearchAgent()
        print("✓ Initialized ResearchAgent")
        
        print("\n📝 Running research query...")
        result = await agent.execute({
            "query": "SaaS companies in the AI/ML space with $50M+ revenue",
            "max_companies": 3
        })
        
        print(f"\n✓ Research completed!")
        print(f"  Status: {result.get('status')}")
        print(f"  Companies found: {result.get('total_researched')}")
        print(f"  Confidence: {result.get('confidence')}")
        
        if result.get('status') == 'success' and result.get('companies'):
            print("\n📊 Sample Company:")
            company = result['companies'][0]
            print(f"  Name: {company.get('name')}")
            print(f"  Industry: {company.get('industry')}")
            print(f"  Revenue: {company.get('revenue')}")
            print(f"  Confidence Score: {company.get('confidence_score')}")
        
        return result.get('status') == 'success'
        
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    try:
        # Test 1: Gemini connection
        gemini_ok = await test_gemini_connection()
        
        if not gemini_ok:
            print("\n❌ Gemini connection test failed. Please configure API key.")
            sys.exit(1)
        
        # Test 2: Research Agent
        research_ok = await test_research_agent()
        
        print("\n" + "="*60)
        if gemini_ok and research_ok:
            print("✓ All tests passed! Backend is ready.")
            print("\nYou can now start the backend with:")
            print("  python -m uvicorn app.main:app --reload")
            sys.exit(0)
        else:
            print("⚠ Some tests failed. Please check the errors above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
