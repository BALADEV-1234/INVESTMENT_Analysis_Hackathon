# Enhanced Web Content Agent with Comprehensive Online Analysis
import os
import asyncio
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentState
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langsmith import traceable
import langsmith
import re
from datetime import datetime

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

class EnhancedWebContentAgent(BaseAgent):
    """Enhanced agent for comprehensive web analysis including competitive intelligence and market validation."""
    
    def __init__(self):
        super().__init__()
        self.tavily_client = None
        if TavilyClient and os.getenv("TAVILY_API_KEY"):
            try:
                self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
            except Exception as e:
                print(f"Warning: Could not initialize Tavily client: {e}")
    
    def _build_workflow(self) -> StateGraph:
        """Build enhanced workflow with comprehensive search capabilities."""
        workflow = StateGraph(AgentState)
        
        # Enhanced node structure
        workflow.add_node("extract_company_info", self._extract_company_info_node)
        workflow.add_node("comprehensive_search", self._comprehensive_search_node)
        workflow.add_node("competitive_analysis", self._competitive_analysis_node)
        workflow.add_node("market_validation", self._market_validation_node)
        workflow.add_node("chunk_text", self._chunk_text_node)
        workflow.add_node("map_chunks", self._map_chunks_node)
        workflow.add_node("reduce_summaries", self._reduce_summaries_node)
        
        # Define workflow
        workflow.set_entry_point("extract_company_info")
        workflow.add_edge("extract_company_info", "comprehensive_search")
        workflow.add_edge("comprehensive_search", "competitive_analysis")
        workflow.add_edge("competitive_analysis", "market_validation")
        workflow.add_edge("market_validation", "chunk_text")
        workflow.add_edge("chunk_text", "map_chunks")
        workflow.add_edge("map_chunks", "reduce_summaries")
        workflow.add_edge("reduce_summaries", END)
        
        return workflow.compile()
    
    @traceable(name="extract_company_info")
    async def _extract_company_info_node(self, state: AgentState) -> AgentState:
        """Enhanced extraction of company information for targeted searches."""
        try:
            content = state["raw_text"]
            
            # Extract company name
            company_name = self._extract_company_name(content)
            
            # Extract industry/sector
            industry = self._extract_industry(content)
            
            # Extract key products/services
            products = self._extract_products(content)
            
            # Extract founders/team
            founders = self._extract_founders(content)
            
            state["metadata"]["company_info"] = {
                "name": company_name,
                "industry": industry,
                "products": products,
                "founders": founders,
                "search_enabled": bool(self.tavily_client)
            }
            
            return state
        except Exception as e:
            state["error"] = f"Error extracting company info: {str(e)}"
            return state
    
    @traceable(name="comprehensive_search")
    async def _comprehensive_search_node(self, state: AgentState) -> AgentState:
        """Perform comprehensive web searches across multiple dimensions."""
        if not self.tavily_client:
            state["metadata"]["web_search_results"] = "Tavily API not configured"
            return state
        
        company_info = state["metadata"].get("company_info", {})
        company_name = company_info.get("name", "")
        
        if not company_name:
            return state
        
        # Comprehensive search queries
        search_categories = {
            "corporate_info": [
                f'"{company_name}" incorporated registration company',
                f'"{company_name}" headquarters location employees',
                f'"{company_name}" legal entity structure'
            ],
            "funding_news": [
                f'"{company_name}" funding round investment seed series',
                f'"{company_name}" investors venture capital backing',
                f'"{company_name}" valuation raise capital'
            ],
            "product_presence": [
                f'"{company_name}" product launch features announcement',
                f'"{company_name}" customer reviews testimonials feedback',
                f'"{company_name}" pricing plans subscription model'
            ],
            "market_presence": [
                f'"{company_name}" market share industry report',
                f'"{company_name}" growth metrics users customers',
                f'"{company_name}" partnerships integrations deals'
            ],
            "team_talent": [
                f'"{company_name}" hiring jobs careers openings',
                f'"{company_name}" team founders leadership',
                f'"{company_name}" employees linkedin growth'
            ],
            "technical_signals": [
                f'"{company_name}" github repository open source',
                f'"{company_name}" API documentation developers',
                f'"{company_name}" technology stack infrastructure'
            ],
            "social_proof": [
                f'"{company_name}" product hunt launch',
                f'"{company_name}" twitter social media presence',
                f'"{company_name}" press coverage media mentions'
            ]
        }
        
        all_results = {}
        
        for category, queries in search_categories.items():
            category_results = []
            for query in queries:
                try:
                    results = await self._search_with_tavily(query, search_depth="advanced")
                    category_results.extend(results)
                    await asyncio.sleep(0.5)  # Rate limiting
                except Exception as e:
                    print(f"Search error for {category}: {e}")
            
            all_results[category] = category_results
        
        # Store structured results
        state["metadata"]["search_results"] = all_results
        state["metadata"]["total_search_results"] = sum(len(r) for r in all_results.values())
        
        # Append to raw text for analysis
        search_content = self._format_search_results(all_results)
        state["raw_text"] = f"{state['raw_text']}\n\n{search_content}"
        
        return state
    
    @traceable(name="competitive_analysis")
    async def _competitive_analysis_node(self, state: AgentState) -> AgentState:
        """Perform competitive landscape analysis."""
        if not self.tavily_client:
            return state
        
        company_info = state["metadata"].get("company_info", {})
        company_name = company_info.get("name", "")
        industry = company_info.get("industry", "")
        
        competitive_queries = [
            f'"{company_name}" competitors alternatives comparison versus',
            f'{industry} market leaders top companies ranking',
            f'"{company_name}" competitive advantage differentiation unique',
            f'{industry} market size growth forecast trends 2024 2025'
        ]
        
        competitive_results = []
        for query in competitive_queries:
            try:
                results = await self._search_with_tavily(query)
                competitive_results.extend(results)
            except Exception as e:
                print(f"Competitive search error: {e}")
        
        state["metadata"]["competitive_analysis"] = competitive_results
        
        # Add to content
        if competitive_results:
            comp_content = "\n\n**COMPETITIVE INTELLIGENCE:**\n"
            comp_content += self._format_search_results({"competitive": competitive_results})
            state["raw_text"] += comp_content
        
        return state
    
    @traceable(name="market_validation")
    async def _market_validation_node(self, state: AgentState) -> AgentState:
        """Validate market demand and customer sentiment."""
        if not self.tavily_client:
            return state
        
        company_info = state["metadata"].get("company_info", {})
        company_name = company_info.get("name", "")
        products = company_info.get("products", [])
        
        validation_queries = [
            f'"{company_name}" customer success case study ROI',
            f'"{company_name}" complaints issues problems reddit',
            f'"{company_name}" review rating stars testimonial'
        ]
        
        # Add product-specific queries
        for product in products[:3]:  # Limit to top 3 products
            validation_queries.append(f'"{product}" review comparison benchmark')
        
        validation_results = []
        for query in validation_queries:
            try:
                results = await self._search_with_tavily(query)
                validation_results.extend(results)
            except Exception as e:
                print(f"Validation search error: {e}")
        
        state["metadata"]["market_validation"] = validation_results
        
        # Add to content
        if validation_results:
            val_content = "\n\n**MARKET VALIDATION:**\n"
            val_content += self._format_search_results({"validation": validation_results})
            state["raw_text"] += val_content
        
        return state
    
    async def _search_with_tavily(self, query: str, search_depth: str = "basic") -> List[Dict]:
        """Perform search with Tavily and return structured results."""
        try:
            response = self.tavily_client.search(
                query=query,
                search_depth=search_depth,
                max_results=5,
                include_domains=[],
                exclude_domains=[]
            )
            
            results = []
            if response and "results" in response:
                for result in response["results"]:
                    results.append({
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "url": result.get("url", ""),
                        "score": result.get("score", 0),
                        "published_date": result.get("published_date", ""),
                        "query": query
                    })
            
            return results
        except Exception as e:
            print(f"Tavily search error: {e}")
            return []
    
    def _extract_company_name(self, content: str) -> str:
        """Extract company name from content."""
        patterns = [
            r'(?:Company|Startup|Business)[\s:]+([A-Z][A-Za-z0-9\s&.]+?)(?:\s+(?:Inc|Corp|LLC|Ltd|Limited|Technologies|Tech|Labs|AI|Bio|Health))?',
            r'^([A-Z][A-Za-z0-9\s&.]+?)(?:\s+(?:Inc|Corp|LLC|Ltd))?(?:\s*[-–—]\s*)',
            r'(?:We are |Introducing |About )\s*([A-Z][A-Za-z0-9\s&.]+?)(?:[,.]|\s+(?:is|are))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content[:1000], re.MULTILINE | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: first capitalized phrase
        words = content.split()[:5]
        for word in words:
            if word[0].isupper() and len(word) > 2:
                return word
        
        return "Unknown Company"
    
    def _extract_industry(self, content: str) -> str:
        """Extract industry/sector from content."""
        industry_keywords = {
            "fintech": ["financial", "payments", "banking", "lending", "crypto"],
            "healthtech": ["health", "medical", "patient", "clinical", "therapy"],
            "edtech": ["education", "learning", "students", "training", "course"],
            "saas": ["software", "platform", "cloud", "enterprise", "b2b"],
            "ecommerce": ["shopping", "retail", "marketplace", "store", "commerce"],
            "ai/ml": ["artificial intelligence", "machine learning", "ai", "neural", "llm"],
            "biotech": ["biotech", "pharmaceutical", "drug", "molecule", "therapeutic"]
        }
        
        content_lower = content.lower()
        for industry, keywords in industry_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return industry
        
        return "technology"
    
    def _extract_products(self, content: str) -> List[str]:
        """Extract product names from content."""
        products = []
        
        # Look for product mentions
        patterns = [
            r'(?:product|service|platform|solution|app|application)[\s:]+([A-Za-z0-9\s]+?)(?:[,.]|\s+(?:is|are|provides))',
            r'(?:launching|introducing|built|created|developed)\s+([A-Za-z0-9\s]+?)(?:[,.]|\s+(?:to|for|that))',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content[:2000], re.IGNORECASE)
            products.extend([m.strip() for m in matches if len(m.strip()) > 2])
        
        return list(set(products))[:5]  # Return top 5 unique products
    
    def _extract_founders(self, content: str) -> List[str]:
        """Extract founder names from content."""
        founders = []
        
        # Look for founder mentions
        patterns = [
            r'(?:Founder|CEO|Co-founder|CTO|CPO)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)(?:,?\s+(?:Founder|CEO|Co-founder|CTO))',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content[:2000])
            founders.extend([m.strip() if isinstance(m, str) else m[0].strip() for m in matches])
        
        return list(set(founders))[:5]  # Return top 5 unique founders
    
    def _format_search_results(self, results_dict: Dict[str, List]) -> str:
        """Format search results for analysis."""
        formatted = "\n**WEB SEARCH INSIGHTS:**\n"
        
        for category, results in results_dict.items():
            if results:
                formatted += f"\n**{category.upper().replace('_', ' ')}:**\n"
                for i, result in enumerate(results[:10], 1):
                    formatted += f"\n{i}. **{result.get('title', 'No title')}**\n"
                    formatted += f"   Source: {result.get('url', 'No URL')}\n"
                    if result.get('published_date'):
                        formatted += f"   Date: {result.get('published_date')}\n"
                    formatted += f"   {result.get('content', 'No content')[:500]}...\n"
        
        return formatted
    
    def get_system_prompt(self) -> str:
        return """You are an advanced web intelligence analyst specializing in comprehensive online research and competitive intelligence. 
        You excel at synthesizing information from multiple online sources to provide deep market insights, competitive analysis, and validation of startup claims."""
    
    def get_analysis_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """
            Analyze all available content including web search results to provide comprehensive intelligence:

            **COMPREHENSIVE WEB INTELLIGENCE ANALYSIS:**
            
            **Company Verification & Credibility:**
            - Legal entity verification and registration status
            - Founding date and corporate history
            - Physical presence and headquarters location
            - Team size and growth trajectory
            - Previous pivots or business model changes
            
            **Funding & Financial Signals:**
            - Confirmed funding rounds and amounts
            - Investor quality and reputation
            - Valuation indicators and multiples
            - Burn rate signals from hiring/expansion
            - Financial health indicators
            
            **Product & Market Validation:**
            - Product launch dates and version history
            - User reviews and ratings across platforms
            - Customer testimonials and case studies
            - Adoption metrics and growth indicators
            - Technical capabilities and limitations
            
            **Competitive Positioning:**
            - Direct and indirect competitors identified
            - Market share estimates and positioning
            - Unique differentiators validated
            - Pricing comparison and strategy
            - Partnership and integration ecosystem
            
            **Team & Talent Assessment:**
            - Founder backgrounds and track records
            - Key hire quality and expertise
            - Employee growth and retention signals
            - Technical talent density (engineers/product)
            - Advisory board and investor network
            
            **Market Presence & Traction:**
            - Media coverage and PR momentum
            - Social media presence and engagement
            - Developer/community activity (GitHub, forums)
            - SEO strength and web traffic estimates
            - Industry recognition and awards
            
            **Red Flags & Risk Indicators:**
            - Inconsistencies between claims and evidence
            - Negative reviews or customer complaints
            - Legal issues or regulatory concerns
            - Competitive threats or market saturation
            - Team turnover or leadership changes
            
            **Investment Signals:**
            - Third-party validation strength
            - Market timing and momentum
            - Scalability indicators
            - Exit potential and comparables
            - Overall investment attractiveness
            
            Content to analyze:
            {content}
            
            Provide data-driven insights with specific examples from search results. Distinguish between verified facts and indicators requiring further validation.
            """)
        ])