# Multi-Agent Orchestrator
import asyncio
from typing import List, Dict, Any, Tuple
from fastapi import UploadFile
from langsmith import traceable
import langsmith
import os

from ..agents.pitch_deck_agent import PitchDeckAgent
from ..agents.data_room_agent import DataRoomAgent
from ..agents.web_content_agent import WebContentAgent
from ..agents.interaction_agent import InteractionAgent
from ..agents.aggregator_agent import AggregatorAgent
from ..utils.file_processor import FileProcessor

class MultiAgentOrchestrator:
    """Orchestrates multiple specialized agents for comprehensive analysis."""
    
    def __init__(self):
        self.agents = {
            "pitch_deck": PitchDeckAgent(),
            "data_room": DataRoomAgent(),
            "web_content": WebContentAgent(),
            "interaction": InteractionAgent()
        }
        self.aggregator = AggregatorAgent()
        self.file_processor = FileProcessor()
    
    @traceable(name="multi_agent_analysis")
    async def analyze_files(self, files: List[UploadFile]) -> Dict[str, Any]:
        """Process multiple files through specialized agents and aggregate results."""
        
        # Add tracing metadata
        if os.getenv("LANGSMITH_API_KEY"):
            langsmith.get_current_run_tree().add_metadata({
                "total_files": len(files),
                "orchestrator_type": "multi_agent_parallel"
            })
        
        # Step 1: Process and categorize files
        categorized_files = await self._process_and_categorize_files(files)
        
        # Step 2: Run specialized agents in parallel
        agent_tasks = []
        for category, file_data in categorized_files.items():
            if category in self.agents and file_data:
                agent_tasks.append(
                    self._run_agent_analysis(category, file_data)
                )
        
        # Execute all agent analyses in parallel
        agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        # Filter out exceptions and format results
        valid_results = []
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
        
        # Step 3: Aggregate all analyses
        final_summary = await self.aggregator.aggregate_analyses(valid_results)
        
        return {
            "final_summary": final_summary,
            "agent_analyses": valid_results,
            "file_processing_summary": self._create_processing_summary(categorized_files),
            "metadata": {
                "total_files_processed": len(files),
                "agents_used": len(valid_results),
                "categories_analyzed": list(categorized_files.keys())
            }
        }
    
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
    
    @traceable(name="agent_analysis")
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
        
        for file_data in file_data_list:
            content = file_data["content"]
            metadata = file_data["metadata"]
            
            combined_content.append(f"=== File: {metadata.get('filename', 'Unknown')} ===\n{content}")
            combined_metadata["files"].append({
                "filename": metadata.get("filename"),
                "size": metadata.get("size_bytes"),
                "processing_method": metadata.get("processing_method")
            })
        
        full_content = "\n\n".join(combined_content)
        
        # Add tracing metadata
        if os.getenv("LANGSMITH_API_KEY"):
            langsmith.get_current_run_tree().add_metadata({
                "agent_category": category,
                "files_processed": len(file_data_list),
                "total_content_length": len(full_content)
            })
        
        # Run analysis using the new LangGraph-based agent
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
            "processing_errors": []
        }
        
        for category, files in categorized_files.items():
            if files:
                summary["categories"][category] = {
                    "file_count": len(files),
                    "files": [f["metadata"].get("filename", "Unknown") for f in files]
                }
                summary["total_files"] += len(files)
                
                # Check for processing errors
                for file_data in files:
                    if "error" in file_data["metadata"]:
                        summary["processing_errors"].append({
                            "filename": file_data["metadata"].get("filename"),
                            "error": file_data["metadata"]["error"]
                        })
        
        return summary
