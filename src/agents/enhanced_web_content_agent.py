# Fixed Enhanced Web Content Agent - Preserves company info from orchestrator
import os
import asyncio
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentState
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langsmith import traceable
import langsmith
import re

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

class EnhancedWebContentAgent(BaseAgent):
    """Agent specialized in analyzing web content with Tavily search integration."""
    
    def __init__(self):
        super().__init__()
        self.tavily_client = None
        if TavilyClient and os.getenv("TAVILY_API_KEY"):
            try:
                self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
                print(f"✓ Tavily client initialized in WebContentAgent")
            except Exception as e:
                print(f"Warning: Could not initialize Tavily client: {e}")
    
    def _build_workflow(self) -> StateGraph:
        """Build enhanced workflow with web search capabilities."""
        workflow = StateGraph(AgentState)
        
        # Modified workflow - extract_company_info now preserves existing data
        workflow.add_node("extract_company_info", self._extract_or_preserve_company_info_node)
        workflow.add_node("search_web_content", self._search_web_content_node)
        workflow.add_node("competitive_analysis", self._competitive_analysis_node)
        workflow.add_node("market_validation", self._market_validation_node)
        workflow.add_node("chunk_text", self._chunk_text_node)
        workflow.add_node("map_chunks", self._map_chunks_node)
        workflow.add_node("reduce_summaries", self._reduce_summaries_node)
        
        # Add edges
        workflow.set_entry_point("extract_company_info")
        workflow.add_edge("extract_company_info", "search_web_content")
        workflow.add_edge("search_web_content", "competitive_analysis")
        workflow.add_edge("competitive_analysis", "market_validation")
        workflow.add_edge("market_validation", "chunk_text")
        workflow.add_edge("chunk_text", "map_chunks")
        workflow.add_edge("map_chunks", "reduce_summaries")
        workflow.add_edge("reduce_summaries", END)
        
        return workflow.compile()
    
    @traceable(name="extract_or_preserve_company_info")
    async def _extract_or_preserve_company_info_node(self, state: AgentState) -> AgentState:
        """Extract company info from content OR preserve if already provided."""
        try:
            content = state["raw_text"]
            
            # CHECK IF COMPANY INFO ALREADY EXISTS IN CONTENT
            # The orchestrator sends structured content like "Company Name: AirBed&Breakfast"
            company_name = None
            
            # First, check if this is structured content from orchestrator
            if "Company Name:" in content:
                # Parse the structured format
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith("Company Name:"):
                        company_name = line.replace("Company Name:", "").strip()
                        if company_name and company_name != "Unknown":
                            print(f"✓ Preserving company name from orchestrator: {company_name}")
                            break
            
            # If no company name found in structured format, try extraction
            if not company_name:
                print("No structured company info, attempting extraction...")
                company_name = self._simple_extract_company(content)
            
            # Store in metadata
            state["metadata"]["company_name"] = company_name
            state["metadata"]["search_enabled"] = bool(self.tavily_client)
            
            print(f"Company info node result: {company_name}")
            
            return state
        except Exception as e:
            state["error"] = f"Error in company info node: {str(e)}"
            return state
    
    def _simple_extract_company(self, content: str) -> str:
        """Simple extraction when no structured data is provided."""
        # Look for company patterns but avoid template names
        patterns = [
            r'(?:about|introducing|welcome to)\s+([A-Z][A-Za-z0-9&\s.-]+)',
            r'^([A-Z][A-Za-z0-9&\s.-]+)\s+(?:is|are|provides)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content[:500], re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if "template" not in name.lower() and len(name) > 2:
                    return name
        
        return None
    
    @traceable(name="search_web_content")
    async def _search_web_content_node(self, state: AgentState) -> AgentState:
        """Search for additional web content using Tavily."""
        try:
            print(f"Search node called. Tavily client: {bool(self.tavily_client)}")
            
            if not self.tavily_client:
                state["metadata"]["web_search_results"] = "Tavily not available"
                state["metadata"]["web_results_count"] = 0
                return state
            
            company_name = state["metadata"].get("company_name", "")
            print(f"Searching for company: '{company_name}'")
            
            if not company_name or company_name == "Unknown":
                state["metadata"]["web_search_results"] = "No company name for search"
                state["metadata"]["web_results_count"] = 0
                return state
            
            # Perform web searches
            search_queries = [
                f'"{company_name}" company website about',
                f'"{company_name}" startup funding investment news',
                f'"{company_name}" product features customer reviews',
                f'"{company_name}" competitors market analysis'
            ]
            
            # Handle special cases like AirBed&Breakfast -> Airbnb
            if "airbed" in company_name.lower() or "breakfast" in company_name.lower():
                search_queries.append("Airbnb company news funding history")
            
            all_results = []
            for query in search_queries:
                try:
                    print(f"  Searching: {query}")
                    results = self.tavily_client.search(
                        query=query,
                        search_depth="basic",
                        max_results=3
                    )
                    
                    if results and "results" in results:
                        for result in results["results"]:
                            all_results.append({
                                "title": result.get("title", ""),
                                "content": result.get("content", ""),
                                "url": result.get("url", ""),
                                "query": query
                            })
                        print(f"    Found {len(results['results'])} results")
                except Exception as search_error:
                    print(f"  Search error: {search_error}")
                    continue
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
            
            print(f"Total web results: {len(all_results)}")
            
            # Add web content to state
            if all_results:
                web_content = "\n\n**WEB SEARCH RESULTS:**\n\n"
                for i, result in enumerate(all_results, 1):
                    web_content += f"{i}. **{result['title']}**\n"
                    web_content += f"   URL: {result['url']}\n"
                    web_content += f"   {result['content'][:300]}...\n\n"
                
                # Append to raw text
                state["raw_text"] = state["raw_text"] + "\n\n" + web_content
                state["metadata"]["web_results_count"] = len(all_results)
                state["metadata"]["web_search_performed"] = True
            else:
                state["metadata"]["web_results_count"] = 0
                state["metadata"]["web_search_performed"] = False
            
            # Add LangSmith metadata
            if os.getenv("LANGSMITH_API_KEY"):
                langsmith.get_current_run_tree().add_metadata({
                    "company_name": company_name,
                    "web_results_count": len(all_results),
                    "search_queries": len(search_queries)
                })
            
            return state
        except Exception as e:
            print(f"Error in web search: {e}")
            state["error"] = f"Web search error: {str(e)}"
            state["metadata"]["web_results_count"] = 0
            return state
    
    @traceable(name="competitive_analysis")
    async def _competitive_analysis_node(self, state: AgentState) -> AgentState:
        """Perform competitive landscape analysis."""
        try:
            if not self.tavily_client:
                return state
            
            company_name = state["metadata"].get("company_name", "")
            if not company_name or company_name == "Unknown":
                return state
            
            # Extract industry from content if available
            content = state["raw_text"]
            industry = "technology"  # default
            if "Industry:" in content:
                for line in content.split('\n'):
                    if "Industry:" in line:
                        industry = line.split("Industry:")[1].strip().split('\n')[0]
                        break
            
            competitive_queries = [
                f'"{company_name}" competitors alternatives comparison',
                f'{industry} market leaders companies'
            ]
            
            competitive_results = []
            for query in competitive_queries:
                try:
                    results = self.tavily_client.search(
                        query=query,
                        search_depth="basic",
                        max_results=2
                    )
                    if results and "results" in results:
                        competitive_results.extend(results["results"])
                except Exception as e:
                    print(f"Competitive search error: {e}")
            
            if competitive_results:
                comp_content = "\n\n**COMPETITIVE INTELLIGENCE:**\n"
                for result in competitive_results[:5]:
                    comp_content += f"- {result.get('title', '')}: {result.get('content', '')[:200]}...\n"
                
                state["raw_text"] += comp_content
                state["metadata"]["competitive_results"] = len(competitive_results)
            
            return state
        except Exception as e:
            state["error"] = f"Competitive analysis error: {str(e)}"
            return state
    
    @traceable(name="market_validation")
    async def _market_validation_node(self, state: AgentState) -> AgentState:
        """Validate market demand and customer sentiment."""
        try:
            if not self.tavily_client:
                return state
            
            company_name = state["metadata"].get("company_name", "")
            if not company_name or company_name == "Unknown":
                return state
            
            validation_queries = [
                f'"{company_name}" customer reviews testimonials',
                f'"{company_name}" problems issues complaints'
            ]
            
            validation_results = []
            for query in validation_queries:
                try:
                    results = self.tavily_client.search(
                        query=query,
                        search_depth="basic",
                        max_results=2
                    )
                    if results and "results" in results:
                        validation_results.extend(results["results"])
                except Exception as e:
                    print(f"Validation search error: {e}")
            
            if validation_results:
                val_content = "\n\n**MARKET VALIDATION:**\n"
                for result in validation_results[:5]:
                    val_content += f"- {result.get('title', '')}: {result.get('content', '')[:200]}...\n"
                
                state["raw_text"] += val_content
                state["metadata"]["validation_results"] = len(validation_results)
            
            return state
        except Exception as e:
            state["error"] = f"Market validation error: {str(e)}"
            return state
    
    def get_system_prompt(self) -> str:
        return """You are an advanced web intelligence analyst specializing in comprehensive online research and competitive intelligence. 
        You excel at synthesizing information from multiple online sources to provide deep market insights, competitive analysis, and validation of startup claims."""
    
    def get_analysis_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """
            Analyze all available content including web search results to provide comprehensive intelligence.
            
            Focus on extracting insights from the web search results about the company.
            
            Content to analyze:
            {content}
            
            Provide a comprehensive analysis focusing on web intelligence findings.
            """)
        ])