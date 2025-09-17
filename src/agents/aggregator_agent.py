# Aggregator Agent - Synthesizes all specialized agent analyses with LangGraph
from .base_agent import BaseAgent, AgentState
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict, Any

class AggregatorAgent(BaseAgent):
    """Agent that aggregates and synthesizes analyses from all specialized agents using LangGraph workflow."""
    
    def __init__(self):
        super().__init__()
    
    def get_system_prompt(self) -> str:
        return """You are a senior investment analyst responsible for synthesizing multiple specialized analyses into a comprehensive investment recommendation. 
        You excel at combining diverse insights into coherent investment theses and actionable recommendations."""
    
    def get_analysis_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """
            Synthesize the following specialized analyses into a comprehensive investment summary:

            **EXECUTIVE INVESTMENT SUMMARY**
            
            **Investment Thesis:**
            - One-sentence elevator pitch and core value proposition
            - Primary investment opportunity and market timing
            - Key differentiators and competitive advantages
            
            **Business Assessment:**
            - Business model viability and scalability
            - Market opportunity size and growth potential
            - Product-market fit evidence and traction
            - Revenue model and unit economics
            
            **Team & Execution:**
            - Founder and team quality assessment
            - Execution track record and capabilities
            - Leadership presence and vision clarity
            - Coachability and investor alignment
            
            **Financial Analysis:**
            - Current financial performance and metrics
            - Growth trajectory and projections
            - Capital efficiency and burn rate
            - Funding requirements and use of capital
            
            **Market Position:**
            - Competitive landscape and positioning
            - Customer validation and market demand
            - Go-to-market strategy effectiveness
            - Partnership and distribution channels
            
            **Risk Assessment:**
            - Primary investment risks and mitigation strategies
            - Market, execution, and competitive risks
            - Regulatory and operational challenges
            - Dependency risks and key assumptions
            
            **Investment Recommendation:**
            - Overall investment rating (Strong Buy/Buy/Hold/Pass)
            - Recommended investment amount and terms
            - Key milestones and success metrics
            - Exit strategy and return potential
            
            **Due Diligence Priorities:**
            - Critical areas requiring deeper investigation
            - Key questions for management team
            - Reference checks and validation points
            - Deal structure and negotiation considerations
            
            Specialized Analyses to Synthesize:
            {content}
            """)
        ])
    
    async def aggregate_analyses(self, agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate multiple agent analyses into a final summary."""
        # Combine all analyses
        combined_content = "\n\n" + "="*80 + "\n\n"
        
        for result in agent_results:
            agent_name = result.get("agent", "Unknown Agent")
            analysis = result.get("analysis", "No analysis available")
            confidence = result.get("confidence", 0.0)
            
            combined_content += f"**{agent_name.upper()} ANALYSIS** (Confidence: {confidence:.1f})\n"
            combined_content += f"{analysis}\n\n"
            combined_content += "="*80 + "\n\n"
        
        # Generate final aggregated analysis using new LangGraph workflow
        aggregation_result = await self.analyze(combined_content)
        
        # Add aggregation metadata
        aggregation_result["metadata"].update({
            "aggregation_type": "multi_agent_synthesis",
            "source_agents": [r.get("agent") for r in agent_results],
            "total_analyses": len(agent_results)
        })
        
        return aggregation_result
