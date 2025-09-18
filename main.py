# Enhanced Multi-Agent Investment Analysis System with Web Search and Questions
import os
import asyncio
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from langsmith import traceable
import langsmith

# Import enhanced multi-agent system
from src.core.enhanced_multi_agent_orchestrator import EnhancedMultiAgentOrchestrator

load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError("Please set GOOGLE_API_KEY in environment or .env file")

if not TAVILY_API_KEY:
    print("⚠ Warning: TAVILY_API_KEY not set. Web search features will be limited.")

# LangSmith configuration
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "enhanced-investment-analyzer")

if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
    print(f"✓ LangSmith tracing enabled for project: {LANGSMITH_PROJECT}")
else:
    print("⚠ LangSmith API key not found. Set LANGSMITH_API_KEY for tracing.")

LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Multi-Agent Investment Analysis System",
    description="AI-powered analyst platform with web search and founder question generation",
    version="3.0.0"
)

# Initialize enhanced orchestrator
orchestrator = EnhancedMultiAgentOrchestrator()

@app.post("/analyze")
@traceable(name="enhanced_investment_analysis")
async def analyze_investment(files: List[UploadFile] = File(...)):
    """
    Comprehensive investment analysis with web search and founder questions.
    
    Features:
    - Multi-agent specialized analysis
    - Tavily-powered web search for market validation
    - Automated scoring based on KPI framework
    - Targeted founder question generation
    - Gap analysis and due diligence priorities
    """
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for analysis")
    
    try:
        # Process files through enhanced multi-agent system
        analysis_result = await orchestrator.analyze_files(files)
        
        return {
            "status": "success",
            "investment_summary": analysis_result["final_summary"]["analysis"],
            "investment_scores": analysis_result["investment_scores"],
            "founder_questions": analysis_result["founder_questions"],
            "confidence_score": analysis_result["final_summary"].get("confidence", 0.0),
            "specialized_analyses": {
                result["agent"]: {
                    "analysis": result["analysis"],
                    "confidence": result.get("confidence", 0.0)
                }
                for result in analysis_result["agent_analyses"]
                if result.get("agent") != "error"
            },
            "web_intelligence": analysis_result["web_intelligence"],
            "identified_gaps": analysis_result["identified_gaps"],
            "processing_summary": analysis_result["file_processing_summary"],
            "metadata": analysis_result["metadata"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}"
        )

@app.post("/summary")
@traceable(name="investment_summary_with_scoring")
async def get_investment_summary(files: List[UploadFile] = File(...)):
    """
    Get focused investment summary with scoring and key questions.
    
    Returns investment thesis, scores, and top founder questions without detailed agent breakdowns.
    """
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for analysis")
    
    try:
        # Process files through enhanced system
        analysis_result = await orchestrator.analyze_files(files)
        
        # Extract top questions
        questions = analysis_result.get("founder_questions", "")
        top_questions = []
        if questions and "Priority 1 - Must Ask" in questions:
            # Extract just the top priority questions
            priority_section = questions.split("Priority 1 - Must Ask")[1]
            if "Priority 2" in priority_section:
                priority_section = priority_section.split("Priority 2")[0]
            # Simple extraction of questions
            lines = priority_section.split("\n")
            for line in lines:
                if line.strip() and not line.strip().startswith("[") and len(line.strip()) > 10:
                    top_questions.append(line.strip())
                if len(top_questions) >= 5:
                    break
        
        return {
            "status": "success",
            "investment_summary": analysis_result["final_summary"]["analysis"],
            "investment_scores": analysis_result["investment_scores"],
            "top_founder_questions": top_questions[:5],
            "confidence_score": analysis_result["final_summary"].get("confidence", 0.0),
            "agents_used": [r["agent"] for r in analysis_result["agent_analyses"] if r.get("agent") != "error"],
            "web_search_performed": analysis_result["web_intelligence"]["search_performed"],
            "files_processed": analysis_result["metadata"]["total_files_processed"],
            "processing_time": analysis_result["metadata"].get("processing_time_seconds")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Summary generation failed: {str(e)}"
        )

@app.post("/questions")
@traceable(name="founder_questions_only")
async def get_founder_questions(files: List[UploadFile] = File(...)):
    """
    Generate comprehensive founder interview questions based on startup materials.
    
    Returns categorized questions for due diligence interviews.
    """
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for analysis")
    
    try:
        # Process files through system
        analysis_result = await orchestrator.analyze_files(files)
        
        return {
            "status": "success",
            "founder_interview_guide": analysis_result["founder_questions"],
            "question_categories": analysis_result.get("question_categories", {}),
            "identified_gaps": analysis_result["identified_gaps"],
            "company_info": analysis_result["web_intelligence"].get("company_info", {}),
            "metadata": {
                "files_analyzed": analysis_result["metadata"]["total_files_processed"],
                "analysis_confidence": analysis_result["final_summary"].get("confidence", 0.0)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Question generation failed: {str(e)}"
        )

@app.post("/scoring")
@traceable(name="investment_scoring_only")
async def get_investment_scores(files: List[UploadFile] = File(...)):
    """
    Generate detailed investment scores based on the KPI framework.
    
    Returns scores across Team, Market, Product, Traction, Financials, and Moat dimensions.
    """
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for analysis")
    
    try:
        # Process files
        analysis_result = await orchestrator.analyze_files(files)
        
        scores = analysis_result["investment_scores"]
        
        return {
            "status": "success",
            "overall_score": scores.get("overall_weighted", 0),
            "recommendation": scores.get("recommendation", "Hold"),
            "detailed_scores": {
                "team": {
                    "score": scores.get("team", 0),
                    "weight": scores["weights"]["team"],
                    "weighted_contribution": scores.get("team", 0) * scores["weights"]["team"]
                },
                "market": {
                    "score": scores.get("market", 0),
                    "weight": scores["weights"]["market"],
                    "weighted_contribution": scores.get("market", 0) * scores["weights"]["market"]
                },
                "product": {
                    "score": scores.get("product", 0),
                    "weight": scores["weights"]["product"],
                    "weighted_contribution": scores.get("product", 0) * scores["weights"]["product"]
                },
                "traction": {
                    "score": scores.get("traction", 0),
                    "weight": scores["weights"]["traction"],
                    "weighted_contribution": scores.get("traction", 0) * scores["weights"]["traction"]
                },
                "financials": {
                    "score": scores.get("financials", 0),
                    "weight": scores["weights"]["financials"],
                    "weighted_contribution": scores.get("financials", 0) * scores["weights"]["financials"]
                },
                "moat": {
                    "score": scores.get("moat", 0),
                    "weight": scores["weights"]["moat"],
                    "weighted_contribution": scores.get("moat", 0) * scores["weights"]["moat"]
                }
            },
            "scoring_framework": {
                "scale": "0-100",
                "thresholds": {
                    "strong_buy": "75+",
                    "buy": "60-74",
                    "hold": "45-59",
                    "pass": "<45"
                },
                "weights_sum": sum(scores["weights"].values())
            },
            "company_info": analysis_result["web_intelligence"].get("company_info", {})
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scoring failed: {str(e)}"
        )

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Enhanced Multi-Agent Investment Analysis System",
        "version": "3.0.0",
        "status": "operational",
        "features": [
            "Multi-agent analysis",
            "Web search intelligence",
            "Investment scoring framework",
            "Founder question generation"
        ]
    }

@app.get("/health")
async def health():
    """Detailed system health check."""
    return {
        "status": "healthy",
        "system_type": "Enhanced Multi-Agent Investment Analyzer",
        "model": LLM_MODEL,
        "agents": [
            "PitchDeckAgent - Analyzes pitch decks and presentations",
            "DataRoomAgent - Analyzes financial and traction documents", 
            "EnhancedWebContentAgent - Web search and competitive intelligence with Tavily",
            "InteractionAgent - Analyzes calls, recordings, and interactions",
            "EnhancedAggregatorAgent - Synthesizes analyses with scoring and questions",
            "FounderQuestionAgent - Generates targeted interview questions"
        ],
        "enhanced_features": [
            "Tavily web search integration" if os.getenv("TAVILY_API_KEY") else "Web search (API key needed)",
            "KPI-based scoring framework (Team, Market, Product, Traction, Financials, Moat)",
            "Automated founder question generation",
            "Gap analysis and due diligence priorities",
            "Competitive intelligence gathering",
            "Market validation through online sources"
        ],
        "supported_formats": [
            ".pdf", ".pptx", ".key",  # Pitch decks
            ".xlsx", ".xls", ".csv",  # Data room docs
            ".txt", ".md", ".json",   # Web content
            "All text-based formats"  # Interaction signals
        ],
        "scoring_framework": {
            "dimensions": ["Team (25%)", "Market (25%)", "Product (20%)", "Traction (20%)", "Financials (5%)", "Moat (5%)"],
            "scale": "0-100",
            "recommendations": ["Strong Buy (75+)", "Buy (60-74)", "Hold (45-59)", "Pass (<45)"]
        },
        "api_keys_status": {
            "google_ai": bool(GOOGLE_API_KEY),
            "tavily_search": bool(TAVILY_API_KEY),
            "langsmith_tracing": bool(LANGSMITH_API_KEY)
        },
        "langsmith_project": LANGSMITH_PROJECT if LANGSMITH_API_KEY else None
    }

@app.get("/agents")
async def list_agents():
    """List all available specialized agents with enhanced capabilities."""
    return {
        "agents": {
            "pitch_deck": {
                "name": "Pitch Deck Agent",
                "specialization": "Pitch decks, presentations, business model analysis",
                "file_types": ["PDF", "PPTX", "Keynote"],
                "focus_areas": ["Business model", "Market analysis", "Financial projections", "Team assessment"]
            },
            "data_room": {
                "name": "Data Room Agent", 
                "specialization": "Financial documents, traction metrics, operational data",
                "file_types": ["Excel", "CSV", "Financial reports"],
                "focus_areas": ["Financial metrics", "Traction indicators", "Operational KPIs", "Risk assessment"]
            },
            "enhanced_web_content": {
                "name": "Enhanced Web Content Agent",
                "specialization": "Digital presence analysis with Tavily web search",
                "file_types": ["Text", "Markdown", "JSON", "Web scrapes"],
                "focus_areas": ["Brand positioning", "Market strategy", "Competitive intelligence", "Online validation"],
                "enhanced_capabilities": [
                    "Comprehensive web search across multiple dimensions",
                    "Competitive landscape analysis",
                    "Market validation through online sources",
                    "Team and talent signal extraction",
                    "Social proof and traction validation"
                ]
            },
            "interaction": {
                "name": "Interaction Agent",
                "specialization": "Human interactions, calls, presentations, feedback",
                "file_types": ["Transcripts", "Text files", "Questionnaires"],
                "focus_areas": ["Communication quality", "Founder assessment", "Market validation", "Investment readiness"]
            },
            "enhanced_aggregator": {
                "name": "Enhanced Aggregator Agent",
                "specialization": "Synthesis, scoring, and question generation",
                "file_types": ["All agent outputs"],
                "focus_areas": ["Investment thesis", "Risk assessment", "Scoring framework", "Due diligence"],
                "enhanced_capabilities": [
                    "KPI-based scoring (0-100 scale)",
                    "Weighted scoring across 6 dimensions",
                    "Investment recommendation generation",
                    "Automated founder question generation",
                    "Gap analysis and identification"
                ]
            },
            "founder_questions": {
                "name": "Founder Question Generator",
                "specialization": "Targeted interview question generation",
                "focus_areas": ["Domain expertise validation", "Vision alignment", "Risk assessment", "Due diligence"],
                "question_categories": [
                    "Technical & Product Questions",
                    "Business Model Questions",
                    "Market & Competition Questions",
                    "Vision & Mission Alignment",
                    "Strategic Alignment",
                    "Risk & Mitigation Questions"
                ]
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)