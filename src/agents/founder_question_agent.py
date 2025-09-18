# Founder Question Generator Agent - Generates targeted questions for due diligence
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentState
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langsmith import traceable

class FounderQuestionAgent(BaseAgent):
    """Agent that generates targeted questions for founder interviews based on analysis results."""
    
    def __init__(self):
        super().__init__()
    
    def _build_workflow(self) -> StateGraph:
        """Build workflow for question generation."""
        workflow = StateGraph(AgentState)
        
        # Custom workflow for question generation
        workflow.add_node("analyze_gaps", self._analyze_gaps_node)
        workflow.add_node("generate_domain_questions", self._generate_domain_questions_node)
        workflow.add_node("generate_alignment_questions", self._generate_alignment_questions_node)
        workflow.add_node("generate_risk_questions", self._generate_risk_questions_node)
        workflow.add_node("compile_questions", self._compile_questions_node)
        
        # Define flow
        workflow.set_entry_point("analyze_gaps")
        workflow.add_edge("analyze_gaps", "generate_domain_questions")
        workflow.add_edge("generate_domain_questions", "generate_alignment_questions")
        workflow.add_edge("generate_alignment_questions", "generate_risk_questions")
        workflow.add_edge("generate_risk_questions", "compile_questions")
        workflow.add_edge("compile_questions", END)
        
        return workflow.compile()
    
    @traceable(name="analyze_gaps")
    async def _analyze_gaps_node(self, state: AgentState) -> AgentState:
        """Identify gaps and areas needing clarification from the analysis."""
        try:
            content = state["raw_text"]
            
            # Parse the analysis to identify gaps
            gap_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert at identifying information gaps and areas requiring clarification in investment analyses."),
                ("human", """
                Review this comprehensive analysis and identify:
                1. Missing critical information
                2. Unverified claims that need validation
                3. Inconsistencies or contradictions
                4. Areas with insufficient depth
                5. Red flags requiring investigation
                
                Analysis:
                {content}
                
                List the key gaps and areas needing founder clarification.
                """)
            ])
            
            messages = gap_prompt.format_messages(content=content[:8000])
            response = await self.llm.ainvoke(messages)
            
            state["metadata"]["identified_gaps"] = response.content
            return state
            
        except Exception as e:
            state["error"] = f"Error analyzing gaps: {str(e)}"
            return state
    
    @traceable(name="generate_domain_questions")
    async def _generate_domain_questions_node(self, state: AgentState) -> AgentState:
        """Generate domain-specific technical and business questions."""
        try:
            gaps = state["metadata"].get("identified_gaps", "")
            content = state["raw_text"][:8000]
            
            domain_prompt = ChatPromptTemplate.from_messages([
                ("system", self.get_domain_question_system_prompt()),
                ("human", """
                Based on this analysis and identified gaps, generate 15-20 domain-specific questions for founders.
                
                Analysis Summary:
                {content}
                
                Identified Gaps:
                {gaps}
                
                Generate questions in these categories:
                
                **TECHNICAL & PRODUCT QUESTIONS:**
                - Core technology and IP
                - Product architecture and scalability
                - Technical differentiation and moat
                - Development roadmap and milestones
                - Integration and API strategy
                
                **BUSINESS MODEL QUESTIONS:**
                - Revenue model validation
                - Unit economics deep dive
                - Pricing strategy and elasticity
                - Customer acquisition strategy
                - Market expansion plans
                
                **MARKET & COMPETITION QUESTIONS:**
                - Market sizing methodology
                - Competitive positioning
                - Customer pain points and urgency
                - Go-to-market strategy
                - Partnership and channel strategy
                
                Format each question with context and what we're trying to validate.
                """)
            ])
            
            messages = domain_prompt.format_messages(content=content, gaps=gaps)
            response = await self.llm.ainvoke(messages)
            
            state["metadata"]["domain_questions"] = response.content
            return state
            
        except Exception as e:
            state["error"] = f"Error generating domain questions: {str(e)}"
            return state
    
    @traceable(name="generate_alignment_questions")
    async def _generate_alignment_questions_node(self, state: AgentState) -> AgentState:
        """Generate questions to assess founder alignment with vision, mission, and strategy."""
        try:
            content = state["raw_text"][:8000]
            
            alignment_prompt = ChatPromptTemplate.from_messages([
                ("system", self.get_alignment_question_system_prompt()),
                ("human", """
                Generate 10-15 questions to assess founder alignment with vision, mission, and strategy.
                
                Context from analysis:
                {content}
                
                Generate alignment assessment questions:
                
                **VISION & MISSION ALIGNMENT:**
                - Long-term vision clarity and commitment
                - Mission consistency across communications
                - Personal motivation and founder-market fit
                - Values alignment with stated goals
                
                **STRATEGIC ALIGNMENT:**
                - Strategic priorities and trade-offs
                - Resource allocation decisions
                - Growth philosophy and scaling approach
                - Exit strategy and investor alignment
                
                **TEAM ALIGNMENT:**
                - Co-founder dynamics and role clarity
                - Team building philosophy
                - Culture and values implementation
                - Decision-making process
                
                **EXECUTION ALIGNMENT:**
                - Milestone prioritization
                - Risk tolerance and mitigation
                - Pivot philosophy and adaptability
                - Operational excellence commitment
                
                Format questions to reveal depth of thinking and consistency of vision.
                """)
            ])
            
            messages = alignment_prompt.format_messages(content=content)
            response = await self.llm.ainvoke(messages)
            
            state["metadata"]["alignment_questions"] = response.content
            return state
            
        except Exception as e:
            state["error"] = f"Error generating alignment questions: {str(e)}"
            return state
    
    @traceable(name="generate_risk_questions")
    async def _generate_risk_questions_node(self, state: AgentState) -> AgentState:
        """Generate questions to probe identified risks and red flags."""
        try:
            gaps = state["metadata"].get("identified_gaps", "")
            content = state["raw_text"][:8000]
            
            risk_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert at identifying and probing investment risks through targeted questioning."),
                ("human", """
                Generate 10-12 risk-focused questions based on the analysis and gaps.
                
                Analysis context:
                {content}
                
                Identified concerns:
                {gaps}
                
                Generate risk assessment questions:
                
                **FINANCIAL RISKS:**
                - Burn rate and runway scenarios
                - Revenue concentration risks
                - Working capital requirements
                - Financial controls and reporting
                
                **MARKET RISKS:**
                - Market timing and adoption risks
                - Regulatory and compliance risks
                - Competitive response scenarios
                - Customer churn and retention
                
                **OPERATIONAL RISKS:**
                - Key person dependencies
                - Technical debt and scalability
                - Supply chain and vendor risks
                - IP and legal vulnerabilities
                
                **EXECUTION RISKS:**
                - Past pivots and learnings
                - Milestone achievement track record
                - Crisis management examples
                - Resource planning accuracy
                
                Frame questions to uncover hidden risks and test preparedness.
                """)
            ])
            
            messages = risk_prompt.format_messages(content=content, gaps=gaps)
            response = await self.llm.ainvoke(messages)
            
            state["metadata"]["risk_questions"] = response.content
            return state
            
        except Exception as e:
            state["error"] = f"Error generating risk questions: {str(e)}"
            return state
    
    @traceable(name="compile_questions")
    async def _compile_questions_node(self, state: AgentState) -> AgentState:
        """Compile and prioritize all generated questions."""
        try:
            domain_q = state["metadata"].get("domain_questions", "")
            alignment_q = state["metadata"].get("alignment_questions", "")
            risk_q = state["metadata"].get("risk_questions", "")
            
            compile_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert at structuring due diligence interviews for maximum insight."),
                ("human", """
                Compile and organize these questions into a structured interview guide.
                
                Domain Questions:
                {domain}
                
                Alignment Questions:
                {alignment}
                
                Risk Questions:
                {risk}
                
                Create a final structured output:
                
                **FOUNDER INTERVIEW GUIDE**
                
                **Priority 1 - Must Ask (Top 10 Questions)**
                [Most critical questions that could be deal-breakers]
                
                **Priority 2 - Domain Deep Dive**
                [Technical and business model questions specific to their industry]
                
                **Priority 3 - Vision & Alignment Assessment**
                [Questions to assess founder quality and alignment]
                
                **Priority 4 - Risk & Mitigation**
                [Questions to understand and quantify risks]
                
                **Follow-up Questions Bank**
                [Additional questions based on responses]
                
                For each question, include:
                - The question itself
                - What we're trying to learn
                - Red flag responses to watch for
                """)
            ])
            
            messages = compile_prompt.format_messages(
                domain=domain_q,
                alignment=alignment_q,
                risk=risk_q
            )
            response = await self.llm.ainvoke(messages)
            
            state["final_summary"] = response.content
            state["metadata"]["questions_generated"] = True
            
            return state
            
        except Exception as e:
            state["error"] = f"Error compiling questions: {str(e)}"
            return state
    
    def get_domain_question_system_prompt(self) -> str:
        return """You are a seasoned venture capitalist and domain expert who excels at asking penetrating questions 
        that reveal the true potential and risks of a startup. You understand what separates great founders from mediocre ones 
        and know how to uncover critical insights through strategic questioning."""
    
    def get_alignment_question_system_prompt(self) -> str:
        return """You are an expert at assessing founder psychology, team dynamics, and strategic alignment. 
        You excel at asking questions that reveal authenticity, depth of thinking, and true motivations. 
        Your questions help identify whether founders have the resilience, vision, and adaptability to build a unicorn."""
    
    def get_system_prompt(self) -> str:
        return """You are a master interviewer and due diligence expert who generates insightful questions 
        for founder interviews. You excel at identifying information gaps and creating questions that reveal 
        both opportunities and risks in startup investments."""
    
    def get_analysis_prompt(self) -> ChatPromptTemplate:
        # This is used for the chunk analysis, but we're overriding the workflow
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", "Analyze: {content}")
        ])
    
    async def generate_questions_from_analyses(self, aggregated_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate questions based on the aggregated analysis from all agents."""
        
        # Format the analysis into text for processing
        analysis_text = self._format_analysis_for_questions(aggregated_analysis)
        
        # Initialize state for question generation
        initial_state = AgentState(
            raw_text=analysis_text,
            chunks=[],
            chunk_summaries=[],
            final_summary="",
            error=None,
            metadata={
                "agent_type": "FounderQuestionAgent",
                "generation_type": "targeted_questions"
            }
        )
        
        # Run the question generation workflow
        result = await self.workflow.ainvoke(initial_state)
        
        if result.get("error"):
            return {
                "questions": f"Error generating questions: {result['error']}",
                "metadata": result["metadata"],
                "error": result["error"]
            }
        
        return {
            "questions": result["final_summary"],
            "metadata": result["metadata"],
            "gaps_identified": result["metadata"].get("identified_gaps", ""),
            "categories": {
                "domain": result["metadata"].get("domain_questions", ""),
                "alignment": result["metadata"].get("alignment_questions", ""),
                "risk": result["metadata"].get("risk_questions", "")
            }
        }
    
    def _format_analysis_for_questions(self, aggregated_analysis: Dict[str, Any]) -> str:
        """Format the aggregated analysis for question generation."""
        formatted = "**COMPREHENSIVE INVESTMENT ANALYSIS SUMMARY**\n\n"
        
        # Add the final summary
        if "analysis" in aggregated_analysis:
            formatted += f"**Executive Summary:**\n{aggregated_analysis['analysis']}\n\n"
        
        # Add confidence score
        if "confidence" in aggregated_analysis:
            formatted += f"**Overall Confidence:** {aggregated_analysis['confidence']:.2f}\n\n"
        
        # Add metadata insights
        if "metadata" in aggregated_analysis:
            meta = aggregated_analysis["metadata"]
            if "source_agents" in meta:
                formatted += f"**Analysis Sources:** {', '.join(meta['source_agents'])}\n\n"
        
        return formatted