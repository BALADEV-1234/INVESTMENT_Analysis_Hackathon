# Data Room Agent - Specialized for financial and traction data analysis with LangGraph
from .base_agent import BaseAgent, AgentState
from langchain_core.prompts import ChatPromptTemplate

class DataRoomAgent(BaseAgent):
    """Agent specialized in analyzing data room documents, financial metrics, and traction data using LangGraph workflow."""
    
    def __init__(self):
        super().__init__()
    
    def get_system_prompt(self) -> str:
        return """You are a specialized financial analyst focused on data room analysis. 
        You excel at extracting financial insights, traction metrics, and operational data from startup documents."""
    
    def get_analysis_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """
            Analyze this data room content and provide a structured financial and traction analysis:

            **DATA ROOM ANALYSIS:**
            
            **Financial Metrics:**
            - Revenue figures and growth rates
            - Profit margins and unit economics
            - Cash flow and burn rate
            - Financial projections and assumptions
            
            **Traction Indicators:**
            - Customer acquisition metrics (CAC, LTV)
            - User growth and engagement metrics
            - Market penetration and retention rates
            - Product adoption and usage statistics
            
            **Operational Metrics:**
            - Key performance indicators (KPIs)
            - Operational efficiency metrics
            - Scalability indicators
            - Resource utilization
            
            **Market Position:**
            - Market share and competitive position
            - Customer testimonials and case studies
            - Partnership agreements and strategic alliances
            - Regulatory compliance and certifications
            
            **Risk Assessment:**
            - Financial risks and dependencies
            - Operational risks and challenges
            - Market risks and competitive threats
            - Regulatory and compliance risks
            
            **Validation Points:**
            - Third-party validations and endorsements
            - Industry recognition and awards
            - Media coverage and PR mentions
            - Investor interest and previous funding
            
            Content to analyze:
            {content}
            """)
        ])
