# Web Content Agent - Specialized for web presence analysis with Tavily search
import os
import asyncio
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentState
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langsmith import traceable
import langsmith

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

class WebContentAgent(BaseAgent):
    """Agent specialized in analyzing web content with Tavily search integration."""
    
    def __init__(self):
        super().__init__()
        self.tavily_client = None
        if TavilyClient and os.getenv("TAVILY_API_KEY"):
            try:
                self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
            except Exception as e:
                print(f"Warning: Could not initialize Tavily client: {e}")
    
    def _build_workflow(self) -> StateGraph:
        """Build enhanced workflow with web search capabilities."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("extract_company_info", self._extract_company_info_node)
        workflow.add_node("search_web_content", self._search_web_content_node)
        workflow.add_node("chunk_text", self._chunk_text_node)
        workflow.add_node("map_chunks", self._map_chunks_node)
        workflow.add_node("reduce_summaries", self._reduce_summaries_node)
        
        # Add edges
        workflow.set_entry_point("extract_company_info")
        workflow.add_edge("extract_company_info", "search_web_content")
        workflow.add_edge("search_web_content", "chunk_text")
        workflow.add_edge("chunk_text", "map_chunks")
        workflow.add_edge("map_chunks", "reduce_summaries")
        workflow.add_edge("reduce_summaries", END)
        
        return workflow.compile()
    
    def get_system_prompt(self) -> str:
        return """You are a specialized digital marketing and content analyst focused on comprehensive web presence analysis. 
        You excel at extracting brand positioning, market messaging, customer communication, and competitive intelligence from web content and search results."""
    
    @traceable(name="extract_company_info")
    async def _extract_company_info_node(self, state: AgentState) -> AgentState:
        """Extract company name and key info for web search."""
        try:
            # Simple extraction of company name from content
            content = state["raw_text"]
            
            # Look for company name patterns
            import re
            company_patterns = [
                r'Company[:\s]+([A-Za-z\s&]+)',
                r'([A-Za-z\s&]+)\s+Inc',
                r'([A-Za-z\s&]+)\s+Corp',
                r'([A-Za-z\s&]+)\s+LLC',
                r'([A-Za-z\s&]+)\s+-\s+',
                r'^([A-Za-z\s&]+)\s+is\s+',
            ]
            
            company_name = None
            for pattern in company_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                if match:
                    company_name = match.group(1).strip()
                    break
            
            if not company_name:
                # Fallback: use first few words as potential company name
                words = content.split()[:3]
                company_name = " ".join(words)
            
            state["metadata"]["company_name"] = company_name
            state["metadata"]["search_enabled"] = bool(self.tavily_client)
            
            return state
        except Exception as e:
            state["error"] = f"Error extracting company info: {str(e)}"
            return state
    
    @traceable(name="search_web_content")
    async def _search_web_content_node(self, state: AgentState) -> AgentState:
        """Search for additional web content using Tavily."""
        try:
            if not self.tavily_client:
                # Skip web search if Tavily not available
                state["metadata"]["web_search_results"] = "Web search not available - Tavily API key not configured"
                return state
            
            company_name = state["metadata"].get("company_name", "")
            if not company_name:
                state["metadata"]["web_search_results"] = "No company name extracted for search"
                return state
            
            # Perform web searches for different aspects
            search_queries = [
                f"{company_name} company website about",
                f"{company_name} startup funding investment",
                f"{company_name} product features benefits",
                f"{company_name} customer reviews testimonials",
                f"{company_name} competitors market analysis"
            ]
            
            all_results = []
            for query in search_queries:
                try:
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
                except Exception as search_error:
                    print(f"Search error for query '{query}': {search_error}")
                    continue
            
            # Combine web search results with original content
            web_content = "\n\n".join([
                f"**{result['title']}** ({result['url']})\n{result['content']}"
                for result in all_results
            ])
            
            if web_content:
                enhanced_content = f"{state['raw_text']}\n\n**WEB SEARCH RESULTS:**\n{web_content}"
                state["raw_text"] = enhanced_content
                state["metadata"]["web_results_count"] = len(all_results)
            else:
                state["metadata"]["web_search_results"] = "No web search results found"
            
            # Add LangSmith metadata
            if os.getenv("LANGSMITH_API_KEY"):
                langsmith.get_current_run_tree().add_metadata({
                    "company_name": company_name,
                    "web_results_count": len(all_results),
                    "search_queries": len(search_queries)
                })
            
            return state
        except Exception as e:
            state["error"] = f"Error in web search: {str(e)}"
            return state
    
    def get_analysis_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """
            Analyze this content (including web search results if available) and provide a comprehensive web presence and brand analysis:

            **WEB PRESENCE & BRAND ANALYSIS:**
            
            **Brand Positioning:**
            - Brand messaging and value proposition
            - Target audience and customer personas
            - Unique selling points and differentiation
            - Brand voice and communication style
            
            **Digital Presence:**
            - Website quality and user experience
            - Content marketing strategy
            - SEO and online visibility
            - Social media presence and engagement
            
            **Product Presentation:**
            - Product features and benefits highlighted
            - Use cases and customer success stories
            - Pricing strategy and packaging
            - Product roadmap and future plans
            
            **Market Strategy:**
            - Go-to-market approach and channels
            - Customer acquisition strategy
            - Partnership and integration strategies
            - Geographic and market expansion plans
            
            **Competitive Intelligence:**
            - Competitive positioning and advantages
            - Market differentiation factors
            - Competitive threats and opportunities
            - Industry trends and positioning
            
            **Customer Insights:**
            - Customer feedback and sentiment analysis
            - User experience and interface design
            - Community engagement and social proof
            - Customer support and service quality
            
            **Investment Perspective:**
            - Brand strength and market positioning
            - Digital marketing effectiveness
            - Customer acquisition potential
            - Scalability of web presence and brand
            - Online reputation and credibility
            
            Content to analyze:
            {content}
            
            Provide a comprehensive analysis focusing on brand positioning, digital strategy, competitive intelligence, and investment attractiveness from a web presence perspective.
            """)
        ])
