# Enhanced Aggregator Agent with Question Generation
from .base_agent import BaseAgent, AgentState
from .founder_question_agent import FounderQuestionAgent
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict, Any
from langsmith import traceable
import asyncio

class EnhancedAggregatorAgent(BaseAgent):
    """Enhanced aggregator that synthesizes analyses and generates founder questions."""
    
    def __init__(self):
        super().__init__()
        self.question_generator = FounderQuestionAgent()
    
    def get_system_prompt(self) -> str:
        return """You are a senior investment partner responsible for synthesizing multiple specialized analyses 
        into comprehensive investment recommendations with detailed scoring based on the specified KPI framework. 
        You excel at combining diverse insights, calculating confidence scores, and identifying key questions for due diligence."""
    
    def get_analysis_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """
            Synthesize the following specialized analyses into a comprehensive investment summary with scoring:

            **EXECUTIVE INVESTMENT SUMMARY**
            
            **Investment Thesis:**
            - One-sentence elevator pitch and core value proposition
            - Primary investment opportunity and market timing
            - Key differentiators and competitive advantages
            - Investment recommendation: [Strong Buy/Buy/Hold/Pass]
            
            **SCORING FRAMEWORK (0-100 scale):**
            
            **Team Score (Weight: 25%)**
            - Founder-market fit (0-30): Prior domain experience, industry knowledge
            - Technical execution (0-25): GitHub activity, release cadence, technical depth
            - Hiring velocity (0-20): Senior talent density, growth rate
            - Prior outcomes (0-25): Exits, notable companies, track record
            - TEAM TOTAL: [X/100]
            
            **Market Score (Weight: 25%)**
            - TAM/SAM/SOM (0-40): Market size and accessibility
            - Growth indicators (0-20): Market growth rate, regulatory tailwinds
            - Pain acuteness (0-20): Customer urgency, willingness to pay
            - Competitive intensity (0-20): Market fragmentation, barriers to entry
            - MARKET TOTAL: [X/100]
            
            **Product Score (Weight: 20%)**
            - Differentiation/moat (0-35): Data advantage, network effects, IP
            - UX & activation (0-25): User experience, onboarding metrics
            - Tech defensibility (0-25): Architecture, scalability, innovation
            - Unit economics (0-15): Gross margins, contribution margin
            - PRODUCT TOTAL: [X/100]
            
            **Traction Score (Weight: 20%)**
            - Growth metrics (0-40): User/revenue growth rates, momentum
            - Retention (0-25): Cohort retention, engagement metrics
            - Sales efficiency (0-20): CAC/LTV, sales cycle, win rate
            - External proof (0-15): Reviews, rankings, social proof
            - TRACTION TOTAL: [X/100]
            
            **Financials Score (Weight: 5%)**
            - Runway & burn (0-40): Months of runway, burn multiple
            - Revenue quality (0-30): Recurring revenue, concentration
            - Capital efficiency (0-30): Revenue per dollar raised
            - FINANCIALS TOTAL: [X/100]
            
            **Moat Score (Weight: 5%)**
            - Data advantage (0-25): Proprietary data, feedback loops
            - Network effects (0-25): User value multiplication
            - Platform lock-in (0-25): Switching costs, integrations
            - Regulatory moat (0-25): Licenses, compliance barriers
            - MOAT TOTAL: [X/100]
            
            **OVERALL WEIGHTED SCORE: [X/100]**
            
            **Business Assessment:**
            - Business model viability and scalability
            - Product-market fit evidence
            - Revenue model and growth trajectory
            - Competitive positioning and differentiation
            
            **Risk Assessment:**
            - Primary risks: [List top 3-5 with mitigation strategies]
            - Platform/technology risks
            - Market and competitive risks
            - Execution and team risks
            - Regulatory and compliance risks
            
            **Investment Recommendation:**
            - Recommended action: [Invest/Pass/Follow-up needed]
            - Suggested investment: $[X]K at $[Y]M valuation
            - Expected return: [X]x in [Y] years
            - Key milestones for next round
            - Exit strategy considerations
            
            **Due Diligence Priorities:**
            - Top 5 areas requiring deeper investigation
            - Critical validation points
            - Reference check priorities
            - Data room requirements
            
            **Web Intelligence Highlights:**
            - Key findings from online research
            - Competitive intelligence insights
            - Market validation signals
            - Red flags or concerns identified
            
            Specialized Analyses to Synthesize:
            {content}
            
            Provide specific scores for each category and calculate the weighted overall score.
            Base recommendations on concrete evidence from the analyses.
            """)
        ])
    
    @traceable(name="enhanced_aggregate_analyses")
    async def aggregate_analyses(self, agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate multiple agent analyses and generate founder questions."""
        
        # Combine all analyses into formatted content
        combined_content = "\n\n" + "="*80 + "\n\n"
        
        for result in agent_results:
            agent_name = result.get("agent", "Unknown Agent")
            analysis = result.get("analysis", "No analysis available")
            confidence = result.get("confidence", 0.0)
            
            combined_content += f"**{agent_name.upper()} ANALYSIS** (Confidence: {confidence:.1f})\n"
            combined_content += f"{analysis}\n\n"
            combined_content += "="*80 + "\n\n"
        
        # Use the base analyze method to process combined content
        aggregation_result = await self.analyze(combined_content)
        
        # Ensure proper structure
        if "metadata" not in aggregation_result:
            aggregation_result["metadata"] = {}
        
        aggregation_result["metadata"].update({
            "aggregation_type": "multi_agent_synthesis",
            "source_agents": [r.get("agent") for r in agent_results],
            "total_analyses": len(agent_results)
        })
        
        # Generate founder questions
        try:
            if hasattr(self, 'question_generator'):
                questions_result = await self.question_generator.generate_questions_from_analyses(
                    aggregation_result
                )
                aggregation_result["founder_questions"] = questions_result.get("questions", "")
                aggregation_result["question_categories"] = questions_result.get("categories", {})
                aggregation_result["identified_gaps"] = questions_result.get("gaps_identified", "")
            else:
                aggregation_result["founder_questions"] = "Question generator not initialized"
                aggregation_result["question_categories"] = {}
                aggregation_result["identified_gaps"] = ""
        except Exception as e:
            print(f"Error generating questions: {e}")
            aggregation_result["founder_questions"] = ""
            aggregation_result["question_categories"] = {}
            aggregation_result["identified_gaps"] = ""
        
        # Calculate scores
        aggregation_result["scores"] = self._calculate_investment_scores(aggregation_result)
        
        return aggregation_result
    
    def _calculate_investment_scores(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed investment scores based on the KPI framework."""
        
        # Extract signals from the analysis text
        analysis_text = analysis.get("analysis", "").lower()
        
        scores = {
            "team": self._calculate_team_score(analysis_text),
            "market": self._calculate_market_score(analysis_text),
            "product": self._calculate_product_score(analysis_text),
            "traction": self._calculate_traction_score(analysis_text),
            "financials": self._calculate_financials_score(analysis_text),
            "moat": self._calculate_moat_score(analysis_text)
        }
        
        # Calculate weighted overall score
        weights = {
            "team": 0.25,
            "market": 0.25,
            "product": 0.20,
            "traction": 0.20,
            "financials": 0.05,
            "moat": 0.05
        }
        
        weighted_score = sum(
            scores[category] * weights[category] 
            for category in scores
        )
        
        scores["overall_weighted"] = round(weighted_score, 2)
        scores["weights"] = weights
        
        # Determine recommendation based on score
        if weighted_score >= 75:
            scores["recommendation"] = "Strong Buy"
        elif weighted_score >= 60:
            scores["recommendation"] = "Buy"
        elif weighted_score >= 45:
            scores["recommendation"] = "Hold"
        else:
            scores["recommendation"] = "Pass"
        
        return scores
    
    def _calculate_team_score(self, text: str) -> float:
        """Calculate team score based on analysis."""
        score = 40  # Base score
        
        # Positive indicators
        positive_signals = [
            ("founder", 5), ("experience", 5), ("track record", 5),
            ("technical", 5), ("domain expert", 10), ("previous exit", 10),
            ("strong team", 5), ("seasoned", 5), ("veteran", 5)
        ]
        
        for signal, points in positive_signals:
            if signal in text:
                score += points
        
        # Negative indicators
        negative_signals = [
            ("first-time", -5), ("inexperienced", -10), ("solo founder", -5),
            ("no technical", -10), ("team risk", -5)
        ]
        
        for signal, points in negative_signals:
            if signal in text:
                score += points
        
        return min(100, max(0, score))
    
    def _calculate_market_score(self, text: str) -> float:
        """Calculate market score based on analysis."""
        score = 40  # Base score
        
        positive_signals = [
            ("large market", 10), ("billion", 10), ("growing market", 5),
            ("tam", 5), ("market opportunity", 5), ("unmet need", 5),
            ("pain point", 5), ("urgent", 5)
        ]
        
        for signal, points in positive_signals:
            if signal in text:
                score += points
        
        negative_signals = [
            ("small market", -10), ("declining", -10), ("saturated", -10),
            ("competitive", -5), ("low barrier", -5)
        ]
        
        for signal, points in negative_signals:
            if signal in text:
                score += points
        
        return min(100, max(0, score))
    
    def _calculate_product_score(self, text: str) -> float:
        """Calculate product score based on analysis."""
        score = 40  # Base score
        
        positive_signals = [
            ("innovative", 5), ("proprietary", 10), ("patent", 10),
            ("unique", 5), ("differentiated", 5), ("scalable", 5),
            ("platform", 5), ("network effect", 10), ("moat", 10)
        ]
        
        for signal, points in positive_signals:
            if signal in text:
                score += points
        
        negative_signals = [
            ("commodity", -10), ("no differentiation", -10), ("me too", -10),
            ("easily copied", -5), ("no moat", -5)
        ]
        
        for signal, points in negative_signals:
            if signal in text:
                score += points
        
        return min(100, max(0, score))
    
    def _calculate_traction_score(self, text: str) -> float:
        """Calculate traction score based on analysis."""
        score = 30  # Lower base for traction
        
        positive_signals = [
            ("revenue", 10), ("growth", 10), ("customers", 5),
            ("retention", 10), ("engagement", 5), ("viral", 10),
            ("testimonial", 5), ("case study", 5), ("mrr", 10),
            ("arr", 10)
        ]
        
        for signal, points in positive_signals:
            if signal in text:
                score += points
        
        negative_signals = [
            ("no revenue", -15), ("no customers", -15), ("churn", -10),
            ("declining", -10), ("no traction", -15)
        ]
        
        for signal, points in negative_signals:
            if signal in text:
                score += points
        
        return min(100, max(0, score))
    
    def _calculate_financials_score(self, text: str) -> float:
        """Calculate financials score based on analysis."""
        score = 40  # Base score
        
        positive_signals = [
            ("profitable", 20), ("positive cash", 15), ("efficient", 10),
            ("low burn", 10), ("runway", 5), ("unit economics", 10)
        ]
        
        for signal, points in positive_signals:
            if signal in text:
                score += points
        
        negative_signals = [
            ("high burn", -15), ("no runway", -20), ("cash crunch", -20),
            ("unsustainable", -15)
        ]
        
        for signal, points in negative_signals:
            if signal in text:
                score += points
        
        return min(100, max(0, score))
    
    def _calculate_moat_score(self, text: str) -> float:
        """Calculate moat score based on analysis."""
        score = 30  # Base score
        
        positive_signals = [
            ("network effect", 20), ("data advantage", 15), ("patent", 15),
            ("proprietary", 10), ("switching cost", 10), ("brand", 5),
            ("regulatory barrier", 10), ("exclusive", 10)
        ]
        
        for signal, points in positive_signals:
            if signal in text:
                score += points
        
        negative_signals = [
            ("no moat", -20), ("easily replicated", -15), ("commodity", -15)
        ]
        
        for signal, points in negative_signals:
            if signal in text:
                score += points
        
        return min(100, max(0, score))