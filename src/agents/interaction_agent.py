# Interaction Agent - Specialized for interaction signals analysis with LangGraph
from .base_agent import BaseAgent, AgentState
from langchain_core.prompts import ChatPromptTemplate

class InteractionAgent(BaseAgent):
    """Agent specialized in analyzing interaction signals, calls, and human communication using LangGraph workflow."""
    
    def __init__(self):
        super().__init__()
    
    def get_system_prompt(self) -> str:
        return """You are a specialized behavioral analyst focused on interaction analysis. 
        You excel at extracting insights from human interactions, communication patterns, and behavioral signals."""
    
    def get_analysis_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """
            Analyze this interaction content and provide a structured behavioral and communication analysis:

            **INTERACTION ANALYSIS:**
            
            **Communication Quality:**
            - Clarity and coherence of messaging
            - Confidence and conviction in delivery
            - Ability to handle questions and objections
            - Presentation skills and engagement level
            
            **Stakeholder Engagement:**
            - Investor questions and areas of interest
            - Concerns and objections raised
            - Follow-up requests and due diligence items
            - Overall investor sentiment and feedback
            
            **Founder Assessment:**
            - Leadership presence and charisma
            - Domain expertise and knowledge depth
            - Coachability and receptiveness to feedback
            - Vision articulation and strategic thinking
            
            **Market Validation:**
            - Customer feedback and testimonials
            - Market demand indicators from conversations
            - Competitive insights from discussions
            - Partnership interest and opportunities
            
            **Execution Insights:**
            - Operational challenges discussed
            - Resource needs and constraints
            - Timeline and milestone discussions
            - Risk mitigation strategies
            
            **Investment Readiness:**
            - Fundraising sophistication and preparation
            - Understanding of investor requirements
            - Negotiation approach and flexibility
            - Due diligence readiness and transparency
            
            Content to analyze:
            {content}
            """)
        ])
