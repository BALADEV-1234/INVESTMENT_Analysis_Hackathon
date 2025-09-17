# Pitch Deck Agent - Specialized for pitch deck analysis with LangGraph
from .base_agent import BaseAgent, AgentState
from langchain_core.prompts import ChatPromptTemplate

class PitchDeckAgent(BaseAgent):
    """Agent specialized in analyzing pitch decks and business presentations using LangGraph workflow."""
    
    def __init__(self):
        super().__init__()
    
    def get_system_prompt(self) -> str:
        return """You are a specialized investment analyst focused on pitch deck evaluation. 
        You excel at extracting business model insights, market analysis, and investment potential from startup presentations."""
    
    def get_analysis_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """
            Analyze this pitch deck content and provide a structured investment analysis:

            **PITCH DECK ANALYSIS:**
            
            **Business Model:**
            - Value proposition and problem-solution fit
            - Revenue model and monetization strategy
            - Target market and customer segments
            - Competitive advantages and moat
            
            **Market Analysis:**
            - Market size and growth potential (TAM, SAM, SOM)
            - Market trends and timing
            - Competitive landscape analysis
            - Go-to-market strategy
            
            **Financial Projections:**
            - Revenue forecasts and growth assumptions
            - Unit economics and key metrics
            - Funding requirements and use of funds
            - Path to profitability
            
            **Team Assessment:**
            - Founder and team backgrounds
            - Relevant experience and expertise
            - Advisory board and key hires
            - Execution capability
            
            **Investment Perspective:**
            - Investment thesis and opportunity size
            - Risk factors and mitigation strategies
            - Exit potential and comparable transactions
            - Recommended investment decision
            
            Content to analyze:
            {content}
            
            Provide a comprehensive analysis focusing on investment attractiveness and business viability.
            """)
        ])
