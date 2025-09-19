#!/usr/bin/env python3
"""
Diagnose why web search isn't executing despite correct company extraction
"""

import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_web_agent_directly():
    """Test the EnhancedWebContentAgent directly with AirBed&Breakfast."""
    
    print("=" * 60)
    print("TESTING WEB AGENT DIRECTLY")
    print("=" * 60)
    
    # Import the agent
    try:
        from src.agents.enhanced_web_content_agent import EnhancedWebContentAgent
        print("✓ EnhancedWebContentAgent imported")
    except ImportError as e:
        print(f"❌ Cannot import EnhancedWebContentAgent: {e}")
        return
    
    # Create agent instance
    agent = EnhancedWebContentAgent()
    print(f"✓ Agent created. Tavily client: {bool(agent.tavily_client)}")
    
    if not agent.tavily_client:
        print("❌ Tavily client not initialized in agent")
        print(f"   TAVILY_API_KEY exists: {bool(os.getenv('TAVILY_API_KEY'))}")
        return
    
    # Create test content mimicking what the orchestrator sends
    test_content = """
    Company Name: AirBed&Breakfast
    Website: Not found
    Industry: Travel/Hospitality
    Location: Not specified
    Funding Stage: Not specified
    
    Description: A web platform where users can rent out their space to host travelers.
    
    Products/Services: Web platform for booking rooms with locals
    
    Perform web searches for:
    1. AirBed&Breakfast recent news updates funding
    2. AirBed&Breakfast competitors market analysis
    3. AirBed&Breakfast customer reviews testimonials
    4. AirBed&Breakfast team hiring linkedin
    """
    
    print("\nTesting with content:")
    print(test_content[:200] + "...")
    print("\nRunning analysis...")
    
    try:
        result = await agent.analyze(test_content)
        
        print("\nResult metadata:")
        print(f"  - Web results count: {result.get('metadata', {}).get('web_results_count', 0)}")
        print(f"  - Search performed: {result.get('metadata', {}).get('search_performed', False)}")
        
        # Check if web search actually happened
        if 'web_search_results' in result.get('metadata', {}):
            print(f"  - Web search status: {result['metadata']['web_search_results']}")
        
        # Check the analysis content
        analysis = result.get('analysis', '')
        if 'airbnb' in analysis.lower() or 'airbed' in analysis.lower():
            print("✓ Analysis mentions the company")
        else:
            print("❌ Analysis doesn't mention the company")
            
        if 'search results' in analysis.lower() or 'web search' in analysis.lower():
            print("✓ Analysis references web search")
        else:
            print("❌ Analysis doesn't reference web search")
            
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
        import traceback
        traceback.print_exc()

async def check_agent_workflow():
    """Check if the agent's workflow includes web search nodes."""
    
    print("\n" + "=" * 60)
    print("CHECKING AGENT WORKFLOW")
    print("=" * 60)
    
    try:
        from src.agents.enhanced_web_content_agent import EnhancedWebContentAgent
        agent = EnhancedWebContentAgent()
        
        # Check if the workflow has the right nodes
        if hasattr(agent, 'workflow'):
            print("✓ Agent has workflow")
            
            # The compiled workflow should have nodes
            if hasattr(agent.workflow, 'nodes'):
                print(f"  Workflow nodes: {agent.workflow.nodes}")
            
        else:
            print("❌ Agent missing workflow")
            
    except Exception as e:
        print(f"❌ Error checking workflow: {e}")

async def test_minimal_search():
    """Test Tavily search directly with AirBed&Breakfast."""
    
    print("\n" + "=" * 60)
    print("TESTING TAVILY DIRECTLY")
    print("=" * 60)
    
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("❌ No TAVILY_API_KEY")
        return
    
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        
        # Search for AirBed&Breakfast / Airbnb
        results = client.search(
            query="AirBed&Breakfast Airbnb company news funding",
            search_depth="basic",
            max_results=3
        )
        
        if results and "results" in results:
            print(f"✓ Tavily search works: {len(results['results'])} results")
            for r in results['results'][:2]:
                print(f"  - {r.get('title', 'No title')[:50]}...")
        else:
            print("❌ No results from Tavily")
            
    except Exception as e:
        print(f"❌ Tavily error: {e}")

def check_env_setup():
    """Check environment setup."""
    
    print("\n" + "=" * 60)
    print("ENVIRONMENT CHECK")
    print("=" * 60)
    
    checks = {
        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "LLM_MODEL": os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")
    }
    
    for key, value in checks.items():
        if value:
            if "KEY" in key:
                print(f"✓ {key}: {value[:8]}..." if len(value) > 8 else value)
            else:
                print(f"✓ {key}: {value}")
        else:
            print(f"❌ {key}: Not set")

async def main():
    """Run all diagnostics."""
    
    print("\n🔍 DIAGNOSING WEB SEARCH ISSUE\n")
    
    # Check environment
    check_env_setup()
    
    # Test Tavily directly
    await test_minimal_search()
    
    # Check agent workflow
    await check_agent_workflow()
    
    # Test the web agent directly
    await test_web_agent_directly()
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS COMPLETE")
    print("=" * 60)
    
    print("\nPossible issues:")
    print("1. The web agent's _extract_company_info_node might be overwriting company info")
    print("2. The web agent's search node might not be getting the right state")
    print("3. The metadata might not be properly passed through the workflow")
    print("\nCheck the agent's node execution order and state passing.")

if __name__ == "__main__":
    asyncio.run(main())