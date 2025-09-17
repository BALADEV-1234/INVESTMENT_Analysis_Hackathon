# Multi-Agent Investment Analysis System
import os
import asyncio
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from langsmith import traceable
import langsmith

# Import multi-agent system
from src.core.multi_agent_orchestrator import MultiAgentOrchestrator

load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("Please set GOOGLE_API_KEY in environment or .env file")

# LangSmith configuration
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "multi-agent-investment-analyzer")

if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
    print(f"✓ LangSmith tracing enabled for project: {LANGSMITH_PROJECT}")
else:
    print("⚠ LangSmith API key not found. Set LANGSMITH_API_KEY for tracing.")

LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Investment Analysis System",
    description="Specialized agents for comprehensive startup analysis",
    version="2.0.0"
)

# Initialize multi-agent orchestrator
orchestrator = MultiAgentOrchestrator()

@app.post("/analyze")
@traceable(name="investment_analysis_endpoint")
async def analyze_investment(files: List[UploadFile] = File(...)):
    """
    Comprehensive investment analysis using specialized agents.
    
    Supports multiple file types and data sources:
    - Pitch decks (PDF, PPTX, Keynote)
    - Data room documents (Excel, CSV, financial docs)
    - Web content (text files, JSON, markdown)
    - Interaction signals (transcripts, recordings, questionnaires)
    """
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for analysis")
    
    try:
        # Process files through multi-agent system
        analysis_result = await orchestrator.analyze_files(files)
        
        return {
            "status": "success",
            "investment_summary": analysis_result["final_summary"]["analysis"],
            "confidence_score": analysis_result["final_summary"].get("confidence", 0.0),
            "specialized_analyses": {
                result["agent"]: {
                    "analysis": result["analysis"],
                    "confidence": result.get("confidence", 0.0)
                }
                for result in analysis_result["agent_analyses"]
                if result.get("agent") != "error"
            },
            "processing_summary": analysis_result["file_processing_summary"],
            "metadata": analysis_result["metadata"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}"
        )

@app.post("/summary")
@traceable(name="investment_summary_endpoint")
async def get_investment_summary(files: List[UploadFile] = File(...)):
    """
    Get a focused investment summary from specialized agents.
    
    Returns only the final aggregated investment summary without individual agent details.
    Uses all available specialized agents based on uploaded file types.
    """
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for analysis")
    
    try:
        # Process files through multi-agent system
        analysis_result = await orchestrator.analyze_files(files)
        
        # Extract which agents were used
        agents_used = []
        for result in analysis_result["agent_analyses"]:
            if result.get("agent") != "error":
                agents_used.append(result["agent"])
        
        return {
            "status": "success",
            "investment_summary": analysis_result["final_summary"]["analysis"],
            "confidence_score": analysis_result["final_summary"].get("confidence", 0.0),
            "agents_used": agents_used,
            "files_processed": analysis_result["metadata"]["total_files_processed"],
            "processing_time": analysis_result["metadata"].get("processing_time"),
            "web_search_enhanced": "web_content" in agents_used and "web_results_count" in str(analysis_result)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Summary generation failed: {str(e)}"
        )

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Multi-Agent Investment Analysis System",
        "version": "2.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health():
    """Detailed system health check."""
    return {
        "status": "healthy",
        "system_type": "Multi-Agent Investment Analyzer",
        "model": LLM_MODEL,
        "agents": [
            "PitchDeckAgent - Analyzes pitch decks and presentations",
            "DataRoomAgent - Analyzes financial and traction documents", 
            "WebContentAgent - Analyzes web presence and marketing content",
            "InteractionAgent - Analyzes calls, recordings, and interactions",
            "AggregatorAgent - Synthesizes all analyses into investment summary"
        ],
        "supported_formats": [
            ".pdf", ".pptx", ".key",  # Pitch decks
            ".xlsx", ".xls", ".csv",  # Data room docs
            ".txt", ".md", ".json",   # Web content
            "All text-based formats"  # Interaction signals
        ],
        "features": [
            "Parallel multi-agent processing",
            "Automatic file categorization",
            "Specialized domain analysis",
            "Comprehensive investment synthesis",
            "No file size limits"
        ],
        "langsmith_tracing": bool(LANGSMITH_API_KEY),
        "langsmith_project": LANGSMITH_PROJECT if LANGSMITH_API_KEY else None
    }

@app.get("/agents")
async def list_agents():
    """List all available specialized agents."""
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
            "web_content": {
                "name": "Web Content Agent",
                "specialization": "Digital presence, marketing materials, brand positioning with web search",
                "file_types": ["Text", "Markdown", "JSON", "Web scrapes"],
                "focus_areas": ["Brand positioning", "Market strategy", "Customer insights", "Digital presence", "Competitive intelligence"],
                "enhanced_features": ["Tavily web search integration", "Real-time competitive analysis", "Company information gathering"]
            },
            "interaction": {
                "name": "Interaction Agent",
                "specialization": "Human interactions, calls, presentations, feedback",
                "file_types": ["Transcripts", "Text files", "Questionnaires"],
                "focus_areas": ["Communication quality", "Founder assessment", "Market validation", "Investment readiness"]
            },
            "aggregator": {
                "name": "Aggregator Agent",
                "specialization": "Synthesis and investment recommendation",
                "file_types": ["All agent outputs"],
                "focus_areas": ["Investment thesis", "Risk assessment", "Due diligence priorities", "Final recommendation"]
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
