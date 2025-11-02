# src/core/enhanced_multi_agent_orchestrator.py
# Enhanced Multi-Agent Orchestrator with LLM-based Company Extraction

import asyncio
import os
import re
import json
from typing import List, Dict, Any, Tuple, Optional
from fastapi import UploadFile
from langsmith import traceable
import langsmith
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from ..agents.pitch_deck_agent import PitchDeckAgent
from ..agents.data_room_agent import DataRoomAgent
from ..agents.enhanced_web_content_agent import EnhancedWebContentAgent
from ..agents.interaction_agent import InteractionAgent
from ..agents.enhanced_aggregator_agent import EnhancedAggregatorAgent
from ..utils.file_processor import FileProcessor


class IntelligentCompanyExtractor:
    """Use LLM to intelligently extract company information from documents."""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("LLM_MODEL", "gemini-2.0-flash-exp"),
            temperature=0.1  # Low temperature for factual extraction
        )
    
    async def extract_company_info(self, content: str) -> Dict[str, Any]:
        """Extract company information using LLM intelligence."""
        
        # Take first 5000 characters for extraction (to fit in context)
        content_sample = content[:5000]
        
        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting company information from pitch decks and business documents.
            Your task is to identify the actual company being presented, not templates, tools, or watermarks.
            
            Focus on:
            - The company actually seeking investment
            - The business being described
            - Ignore template names, watermarks, or tool mentions like "Template by...", "Created with...", etc.
            
            Return information in valid JSON format only."""),
            
            ("human", """Extract the company information from this document.
            
            IMPORTANT: 
            - Identify the ACTUAL company being pitched, not template providers
            - If you see "AirBed&Breakfast" or "Airbnb", that's the company
            - Ignore watermarks like "Template by PitchDeckCoach" or similar
            - Focus on the business description and value proposition
            
            Document content:
            {content}
            
            Return ONLY a valid JSON object with these fields:
            {{
                "company_name": "actual company name",
                "website": "company website if found",
                "industry": "industry or sector",
                "description": "brief company description",
                "founders": ["founder names if found"],
                "location": "headquarters location",
                "stage": "funding stage if mentioned",
                "products": ["main products or services"],
                "target_market": "target customer segment"
            }}
            
            If a field is not found, use null.
            """)
        ])
        
        try:
            messages = extraction_prompt.format_messages(content=content_sample)
            response = await self.llm.ainvoke(messages)
            
            # Parse the JSON response
            json_str = response.content
            
            # Clean up the response to ensure valid JSON
            if '```json' in json_str:
                json_str = json_str.split('```json')[1].split('```')[0]
            elif '```' in json_str:
                json_str = json_str.split('```')[1].split('```')[0]
            
            # Parse JSON
            company_info = json.loads(json_str)
            
            # Validate and clean the company name
            if company_info.get("company_name"):
                # Remove any template references if they slipped through
                name = company_info["company_name"]
                if "template" in name.lower() or "pitchdeck" in name.lower():
                    # Try to find the real company name in the content
                    company_info["company_name"] = await self._get_real_company_name(content_sample)
            
            # Map to expected format
            return {
                "name": company_info.get("company_name"),
                "website": company_info.get("website"),
                "industry": company_info.get("industry", "technology"),
                "description": company_info.get("description"),
                "founders": company_info.get("founders", []),
                "location": company_info.get("location"),
                "stage": company_info.get("stage"),
                "products": company_info.get("products", [])
            }
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"LLM JSON extraction failed: {e}")
            # Fallback to simple extraction
            return await self._simple_llm_extraction(content_sample)
    
    async def _get_real_company_name(self, content: str) -> Optional[str]:
        """Get the real company name when template name was extracted."""
        
        simple_prompt = ChatPromptTemplate.from_messages([
            ("system", "You extract the actual company name from pitch decks, ignoring templates."),
            ("human", """This pitch deck contains a company presentation.
            What is the REAL company name being pitched?
            
            Look for the actual business, like "AirBed&Breakfast", "Uber", "Dropbox", etc.
            Ignore template watermarks.
            
            Content:
            {content}
            
            Respond with ONLY the company name.
            """)
        ])
        
        try:
            messages = simple_prompt.format_messages(content=content[:1000])
            response = await self.llm.ainvoke(messages)
            name = response.content.strip()
            
            # Validate it's not a template
            if "template" not in name.lower() and "coach" not in name.lower():
                return name
        except:
            pass
        
        return None
    
    async def _simple_llm_extraction(self, content: str) -> Dict[str, Any]:
        """Simpler extraction when JSON parsing fails."""
        
        simple_prompt = ChatPromptTemplate.from_messages([
            ("system", "You identify companies from pitch decks."),
            ("human", """What is the company name in this pitch deck?
            
            Look for the actual business being pitched (like AirBed&Breakfast, Uber, etc.)
            NOT template names.
            
            Document:
            {content}
            
            Respond with: Company: [name] | Industry: [industry]
            """)
        ])
        
        try:
            messages = simple_prompt.format_messages(content=content[:2000])
            response = await self.llm.ainvoke(messages)
            
            # Parse the simple format
            parts = response.content.split('|')
            company_name = None
            industry = "technology"
            
            for part in parts:
                if "Company:" in part:
                    company_name = part.replace("Company:", "").strip()
                elif "Industry:" in part:
                    industry = part.replace("Industry:", "").strip()
            
            return {
                "name": company_name,
                "industry": industry,
                "products": [],
                "founders": [],
                "location": None,
                "website": None,
                "stage": None,
                "description": None
            }
        except Exception as e:
            print(f"Simple extraction failed: {e}")
            return {"name": None, "industry": "technology"}


class EnhancedMultiAgentOrchestrator:
    """Enhanced orchestrator with LLM-based company extraction and web search."""

    # Guardrails: System limits
    MAX_FILES_PER_REQUEST = 10
    ANALYSIS_TIMEOUT_SECONDS = 600

    def __init__(self):
        # Guardrail: Validate required API keys
        required_keys = ["GOOGLE_API_KEY"]
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        if missing_keys:
            raise EnvironmentError(
                f"Missing required API keys: {', '.join(missing_keys)}. "
                f"Please set them in your environment or .env file."
            )

        self.agents = {
            "pitch_deck": PitchDeckAgent(),
            "data_room": DataRoomAgent(),
            "web_content": EnhancedWebContentAgent(),
            "interaction": InteractionAgent()
        }
        self.aggregator = EnhancedAggregatorAgent()
        self.file_processor = FileProcessor()
        self.company_extractor = IntelligentCompanyExtractor()

        print(f"✓ Orchestrator initialized with API keys validated")
    
    @traceable(name="enhanced_multi_agent_analysis")
    async def analyze_files(self, files: List[UploadFile]) -> Dict[str, Any]:
        """Process files through specialized agents with intelligent web search."""

        # Guardrail: Validate file count
        if len(files) > self.MAX_FILES_PER_REQUEST:
            raise ValueError(
                f"Too many files uploaded. "
                f"Maximum: {self.MAX_FILES_PER_REQUEST}, Received: {len(files)}"
            )

        # Guardrail: Validate total upload size
        total_size = 0
        for file in files:
            # Peek at file size without consuming the stream
            content_start = await file.read(1)
            if content_start:
                await file.seek(0)  # Reset file pointer
                # Read a chunk to estimate size
                chunk = await file.read(1024)
                await file.seek(0)  # Reset again
                # Note: We'll do full validation in file_processor per-file

        start_time = datetime.now()

        # Add tracing metadata
        if os.getenv("LANGSMITH_API_KEY"):
            langsmith.get_current_run_tree().add_metadata({
                "total_files": len(files),
                "orchestrator_type": "enhanced_multi_agent_llm",
                "features": ["llm_extraction", "intelligent_web_search", "question_generation", "scoring_framework"]
            })

        # Guardrail: Wrap entire analysis in timeout
        try:
            return await asyncio.wait_for(
                self._analyze_files_internal(files, start_time),
                timeout=self.ANALYSIS_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            processing_time = (datetime.now() - start_time).total_seconds()
            # Return structure consistent with normal response
            return {
                "final_summary": {
                    "analysis": f"Analysis exceeded {self.ANALYSIS_TIMEOUT_SECONDS}s timeout",
                    "confidence": 0.0,
                    "error": "timeout",
                    "metadata": {"status": "timeout"}
                },
                "investment_scores": {},
                "founder_questions": "",
                "question_categories": {},
                "identified_gaps": "",
                "agent_analyses": [],
                "file_processing_summary": {"error": "timeout"},
                "web_intelligence": {
                    "search_performed": False,
                    "company_info": {},
                    "enhanced_with_tavily": bool(os.getenv("TAVILY_API_KEY"))
                },
                "metadata": {
                    "total_files_processed": len(files),
                    "agents_used": 0,
                    "categories_analyzed": [],
                    "processing_time_seconds": processing_time,
                    "timeout_limit": self.ANALYSIS_TIMEOUT_SECONDS,
                    "status": "timeout",
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            # Handle any other errors with consistent structure
            processing_time = (datetime.now() - start_time).total_seconds()
            return {
                "final_summary": {
                    "analysis": f"Analysis failed: {str(e)}",
                    "confidence": 0.0,
                    "error": str(e),
                    "metadata": {"status": "error"}
                },
                "investment_scores": {},
                "founder_questions": "",
                "question_categories": {},
                "identified_gaps": "",
                "agent_analyses": [],
                "file_processing_summary": {"error": str(e)},
                "web_intelligence": {
                    "search_performed": False,
                    "company_info": {},
                    "enhanced_with_tavily": bool(os.getenv("TAVILY_API_KEY"))
                },
                "metadata": {
                    "total_files_processed": len(files),
                    "agents_used": 0,
                    "categories_analyzed": [],
                    "processing_time_seconds": processing_time,
                    "status": "error",
                    "error_details": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }

    async def _analyze_files_internal(self, files: List[UploadFile], start_time: datetime) -> Dict[str, Any]:
        """Internal method containing the actual analysis logic."""

        # Step 1: Process and categorize files
        categorized_files = await self._process_and_categorize_files(files)
        
        # Step 2: Extract company information using LLM
        company_info = await self._llm_company_extraction(categorized_files)
        
        # Step 3: Ensure web search runs if we have company info and Tavily is available
        if company_info.get("name") and os.getenv("TAVILY_API_KEY"):
            # Force web search by ensuring web_content category exists
            if "web_content" not in categorized_files:
                categorized_files["web_content"] = []
            
            # Add company info as a web search trigger
            categorized_files["web_content"].append({
                "content": self._create_web_search_content(company_info),
                "metadata": {
                    "filename": "company_intelligence.txt",
                    "company_info": company_info,
                    "trigger_web_search": True,
                    "synthetic": True
                }
            })
            
            print(f"✓ Web search triggered for company: {company_info.get('name')}")
        else:
            if not company_info.get("name"):
                print("⚠ No company name extracted - web search skipped")
            elif not os.getenv("TAVILY_API_KEY"):
                print("⚠ Tavily API key not found - web search skipped")
        
        # Step 4: Run specialized agents in parallel
        agent_tasks = []
        for category, file_data in categorized_files.items():
            if category in self.agents and file_data:
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
        
        # Step 5: Enhanced aggregation with scoring and question generation
        final_summary = await self.aggregator.aggregate_analyses(valid_results)

        # Guardrail: Ensure final_summary has required structure
        if not isinstance(final_summary, dict):
            final_summary = {
                "analysis": str(final_summary),
                "confidence": 0.0,
                "error": "invalid_aggregator_result",
                "metadata": {},
                "scores": {},
                "founder_questions": "",
                "question_categories": {},
                "identified_gaps": ""
            }

        # Ensure analysis key exists
        if "analysis" not in final_summary:
            final_summary["analysis"] = "Aggregation completed but no summary generated"
            final_summary["confidence"] = 0.0
            final_summary["error"] = "missing_analysis"

        # Add processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Step 6: Generate comprehensive output
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
    
    async def _llm_company_extraction(self, categorized_files: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Use LLM to intelligently extract company information."""
        
        # Combine content from all files (prioritize pitch decks)
        all_content = []
        
        # First, add pitch deck content (most likely to have company info)
        if "pitch_deck" in categorized_files:
            for file_data in categorized_files["pitch_deck"]:
                all_content.append(file_data["content"][:3000])
        
        # Then add other content
        for category, files in categorized_files.items():
            if category != "pitch_deck":
                for file_data in files:
                    all_content.append(file_data["content"][:2000])
        
        combined_content = "\n\n".join(all_content)
        
        # Use LLM extraction
        print("Using LLM to extract company information...")
        company_info = await self.company_extractor.extract_company_info(combined_content)
        
        print(f"LLM extracted company info: {company_info}")
        
        # If LLM didn't find a name, try fallback regex (but this is rare)
        if not company_info.get("name"):
            print("LLM couldn't find company name, trying fallback...")
            company_info["name"] = self._fallback_company_extraction(combined_content)
        
        return company_info
    
    def _fallback_company_extraction(self, content: str) -> Optional[str]:
        """Simple fallback if LLM fails."""
        # Look for common patterns
        patterns = [
            r'(?:^|\n)([A-Z][A-Za-z0-9&\s.-]+?)(?:\n|\s+(?:is|are|provides|offers))',
            r'Welcome to\s+([A-Z][A-Za-z0-9&\s.-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content[:1000], re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if "template" not in name.lower() and len(name) > 2:
                    return name
        return None
    
    def _create_web_search_content(self, company_info: Dict[str, Any]) -> str:
        """Create content for web search agent based on extracted company info."""
        
        content_parts = [
            f"Company Name: {company_info.get('name', 'Unknown')}",
            f"Website: {company_info.get('website', 'Not found')}",
            f"Industry: {company_info.get('industry', 'Technology')}",
            f"Location: {company_info.get('location', 'Not specified')}",
            f"Funding Stage: {company_info.get('stage', 'Not specified')}",
        ]
        
        if company_info.get('description'):
            content_parts.append(f"\nDescription: {company_info['description']}")
        
        if company_info.get('products'):
            content_parts.append(f"\nProducts/Services: {', '.join(company_info['products'][:3])}")
        
        if company_info.get('founders'):
            content_parts.append(f"\nFounders: {', '.join(company_info['founders'][:3])}")
        
        content = '\n'.join(content_parts)
        
        # Add search instructions
        content += "\n\nPerform web searches for:\n"
        content += f"1. {company_info.get('name', 'company')} recent news updates funding\n"
        content += f"2. {company_info.get('name', 'company')} competitors market analysis\n"
        content += f"3. {company_info.get('name', 'company')} customer reviews testimonials\n"
        content += f"4. {company_info.get('name', 'company')} team hiring linkedin\n"
        
        return content
    
    # Keep all the existing helper methods unchanged
    async def _process_and_categorize_files(self, files: List[UploadFile]) -> Dict[str, List[Dict[str, Any]]]:
        """Process files and categorize them by data source type."""
        categorized = {
            "pitch_deck": [],
            "data_room": [],
            "web_content": [],
            "interaction": [],
            "general": []
        }
        
        processing_tasks = [
            self._process_single_file(file) for file in files
        ]
        
        processed_files = await asyncio.gather(*processing_tasks, return_exceptions=True)
        
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
        
        if os.getenv("LANGSMITH_API_KEY"):
            langsmith.get_current_run_tree().add_metadata({
                "agent_category": category,
                "files_processed": len(file_data_list),
                "total_content_length": len(full_content)
            })
        
        analysis_result = await agent.analyze(full_content)

        # Guardrail: Ensure result has required structure
        if not isinstance(analysis_result, dict):
            analysis_result = {
                "analysis": str(analysis_result),
                "confidence": 0.0,
                "error": "invalid_result_type",
                "metadata": {}
            }

        # Ensure metadata exists
        if "metadata" not in analysis_result:
            analysis_result["metadata"] = {}

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
                # Skip synthetic web search triggers
                real_files = [f for f in files if not f["metadata"].get("synthetic", False)]
                
                if real_files:
                    summary["categories"][category] = {
                        "file_count": len(real_files),
                        "files": [f["metadata"].get("filename", "Unknown") for f in real_files],
                        "total_size_bytes": sum(f["metadata"].get("size_bytes", 0) for f in real_files)
                    }
                    summary["total_files"] += len(real_files)
                    
                    for file_data in real_files:
                        ext = file_data["metadata"].get("file_extension", "unknown")
                        summary["file_types"][ext] = summary["file_types"].get(ext, 0) + 1
                        
                        if "error" in file_data["metadata"]:
                            summary["processing_errors"].append({
                                "filename": file_data["metadata"].get("filename"),
                                "error": file_data["metadata"]["error"]
                            })
        
        return summary