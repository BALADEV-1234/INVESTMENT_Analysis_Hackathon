# Enhanced Multi-Agent Orchestrator with Web Search and Question Generation
import asyncio
from typing import List, Dict, Any, Tuple
from fastapi import UploadFile
from langsmith import traceable
import langsmith
import os
from datetime import datetime

from ..agents.pitch_deck_agent import PitchDeckAgent
from ..agents.data_room_agent import DataRoomAgent
from ..agents.enhanced_web_content_agent import EnhancedWebContentAgent
from ..agents.interaction_agent import InteractionAgent
from ..agents.enhanced_aggregator_agent import EnhancedAggregatorAgent
from ..utils.file_processor import FileProcessor
from ..agents.founder_question_agent import FounderQuestionAgent  # Add this import

class EnhancedMultiAgentOrchestrator:
    """Enhanced orchestrator with comprehensive web search and founder question generation."""
    
    def __init__(self):
        self.agents = {
            "pitch_deck": PitchDeckAgent(),
            "data_room": DataRoomAgent(),
            "web_content": EnhancedWebContentAgent(),  # Using enhanced version
            "interaction": InteractionAgent()
        }
        self.aggregator = EnhancedAggregatorAgent()  # Using enhanced version
        self.file_processor = FileProcessor()
    
    @traceable(name="enhanced_multi_agent_analysis")
    async def analyze_files(self, files: List[UploadFile]) -> Dict[str, Any]:
        """Process files through specialized agents with enhanced web search and question generation."""
        
        start_time = datetime.now()
        
        # Add tracing metadata
        if os.getenv("LANGSMITH_API_KEY"):
            langsmith.get_current_run_tree().add_metadata({
                "total_files": len(files),
                "orchestrator_type": "enhanced_multi_agent",
                "features": ["web_search", "question_generation", "scoring_framework"]
            })
        
        # Step 1: Process and categorize files
        categorized_files = await self._process_and_categorize_files(files)
        
        # Step 2: Extract company information for enhanced web search
        company_info = await self._extract_company_information(categorized_files)
        
        # Step 3: Run specialized agents in parallel (with enhanced web agent)
        agent_tasks = []
        for category, file_data in categorized_files.items():
            if category in self.agents and file_data:
                # Pass company info to web agent for better searches
                if category == "web_content":
                    for data in file_data:
                        data["metadata"]["company_info"] = company_info
                
                agent_tasks.append(
                    self._run_agent_analysis(category, file_data)
                )
        
        # Execute all agent analyses in parallel
        agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        # Filter and format results
        valid_results = []
        web_search_performed = False
        
        for result in agent_results:
            if isinstance(result, Exception):
                valid_results.append({
                    "agent": "error",
                    "analysis": f"Agent error: {str(result)}",
                    "confidence": 0.0,
                    "metadata": {"error": True}
                })
            else:
                valid_results.append(result)
                # Check if web search was performed
                if result.get("agent") == "web_content":
                    web_search_performed = result.get("metadata", {}).get("web_results_count", 0) > 0
        
        # Step 4: Enhanced aggregation with scoring and question generation
        final_summary = await self.aggregator.aggregate_analyses(valid_results)
        
        # Add processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Step 5: Generate comprehensive output
        return {
            "final_summary": final_summary,
            "investment_scores": final_summary.get("scores", {}),
            "founder_questions": final_summary.get("founder_questions", ""),
            "question_categories": final_summary.get("question_categories", {}),
            "identified_gaps": final_summary.get("identified_gaps", ""),
            "agent_analyses": valid_results,
            "file_processing_summary": self._create_processing_summary(categorized_files),
            "web_intelligence": {
                "search_performed": web_search_performed,
                "company_info": company_info,
                "enhanced_with_tavily": bool(os.getenv("TAVILY_API_KEY"))
            },
            "metadata": {
                "total_files_processed": len(files),
                "agents_used": len(valid_results),
                "categories_analyzed": list(categorized_files.keys()),
                "processing_time_seconds": processing_time,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    async def _extract_company_information(self, categorized_files: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Extract company information from files for enhanced web search."""
        company_info = {
            "name": None,
            "industry": None,
            "products": [],
            "founders": [],
            "location": None,
            "stage": None
        }
        
        # Look through pitch deck files first (most likely to have company info)
        for category in ["pitch_deck", "web_content", "data_room"]:
            if category in categorized_files and categorized_files[category]:
                for file_data in categorized_files[category]:
                    content = file_data["content"][:5000]  # Check first 5000 chars
                    
                    # Extract company name
                    if not company_info["name"]:
                        import re
                        name_patterns = [
                            r'(?:Company|Startup)[\s:]+([A-Z][A-Za-z0-9\s&.]+)',
                            r'^([A-Z][A-Za-z0-9\s&.]+?)(?:\s*[-–—]\s*)',
                        ]
                        for pattern in name_patterns:
                            match = re.search(pattern, content, re.MULTILINE)
                            if match:
                                company_info["name"] = match.group(1).strip()
                                break
                    
                    # Extract industry
                    if not company_info["industry"]:
                        industry_keywords = {
                            "fintech": ["financial", "payments", "banking"],
                            "healthtech": ["health", "medical", "clinical"],
                            "saas": ["software", "platform", "cloud"],
                            "ai/ml": ["artificial intelligence", "machine learning"],
                            "biotech": ["biotech", "pharmaceutical", "drug"]
                        }
                        content_lower = content.lower()
                        for industry, keywords in industry_keywords.items():
                            if any(kw in content_lower for kw in keywords):
                                company_info["industry"] = industry
                                break
                    
                    # Extract stage
                    if not company_info["stage"]:
                        stage_patterns = [
                            (r'seed', 'Seed'),
                            (r'series\s+[a-c]', 'Series A/B/C'),
                            (r'pre-seed', 'Pre-seed')
                        ]
                        for pattern, stage in stage_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                company_info["stage"] = stage
                                break
        
        return company_info
    
    async def _process_and_categorize_files(self, files: List[UploadFile]) -> Dict[str, List[Dict[str, Any]]]:
        """Process files and categorize them by data source type."""
        categorized = {
            "pitch_deck": [],
            "data_room": [],
            "web_content": [],
            "interaction": [],
            "general": []
        }
        
        # Process files in parallel
        processing_tasks = [
            self._process_single_file(file) for file in files
        ]
        
        processed_files = await asyncio.gather(*processing_tasks, return_exceptions=True)
        
        # Categorize processed files
        for result in processed_files:
            if isinstance(result, Exception):
                continue
                
            content, metadata = result
            category = self.file_processor.categorize_file(
                metadata.get("filename", ""), 
                metadata.get("content_type", "")
            )
            
            file_data = {
                "content": content,
                "metadata": metadata
            }
            
            if category in categorized:
                categorized[category].append(file_data)
            else:
                categorized["general"].append(file_data)
        
        return categorized
    
    async def _process_single_file(self, file: UploadFile) -> Tuple[str, Dict[str, Any]]:
        """Process a single file and extract content."""
        return await self.file_processor.extract_text_from_upload(file)
    
    @traceable(name="enhanced_agent_analysis")
    async def _run_agent_analysis(self, category: str, file_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run analysis for a specific agent category."""
        agent = self.agents[category]
        
        # Combine all content for this category
        combined_content = []
        combined_metadata = {
            "category": category,
            "files_count": len(file_data_list),
            "files": []
        }
        
        # Check if this is web content agent with company info
        company_info = None
        for file_data in file_data_list:
            content = file_data["content"]
            metadata = file_data["metadata"]
            
            # Extract company info if available
            if "company_info" in metadata:
                company_info = metadata["company_info"]
            
            combined_content.append(f"=== File: {metadata.get('filename', 'Unknown')} ===\n{content}")
            combined_metadata["files"].append({
                "filename": metadata.get("filename"),
                "size": metadata.get("size_bytes"),
                "processing_method": metadata.get("processing_method")
            })
        
        full_content = "\n\n".join(combined_content)
        
        # Add company info to content if web agent
        if category == "web_content" and company_info:
            info_text = f"**COMPANY INFORMATION:**\n"
            info_text += f"Name: {company_info.get('name', 'Unknown')}\n"
            info_text += f"Industry: {company_info.get('industry', 'Unknown')}\n"
            info_text += f"Stage: {company_info.get('stage', 'Unknown')}\n\n"
            full_content = info_text + full_content
        
        # Add tracing metadata
        if os.getenv("LANGSMITH_API_KEY"):
            langsmith.get_current_run_tree().add_metadata({
                "agent_category": category,
                "files_processed": len(file_data_list),
                "total_content_length": len(full_content),
                "has_company_info": bool(company_info)
            })
        
        # Run analysis
        analysis_result = await agent.analyze(full_content)
        
        # Add category and metadata to the result
        analysis_result["agent"] = category
        analysis_result["metadata"].update(combined_metadata)
        
        return analysis_result
    
    def _create_processing_summary(self, categorized_files: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Create a summary of file processing results."""
        summary = {
            "categories": {},
            "total_files": 0,
            "processing_errors": [],
            "file_types": {}
        }
        
        for category, files in categorized_files.items():
            if files:
                summary["categories"][category] = {
                    "file_count": len(files),
                    "files": [f["metadata"].get("filename", "Unknown") for f in files],
                    "total_size_bytes": sum(f["metadata"].get("size_bytes", 0) for f in files)
                }
                summary["total_files"] += len(files)
                
                # Track file types
                for file_data in files:
                    ext = file_data["metadata"].get("file_extension", "unknown")
                    summary["file_types"][ext] = summary["file_types"].get(ext, 0) + 1
                
                # Check for processing errors
                for file_data in files:
                    if "error" in file_data["metadata"]:
                        summary["processing_errors"].append({
                            "filename": file_data["metadata"].get("filename"),
                            "error": file_data["metadata"]["error"]
                        })
        
        return summary