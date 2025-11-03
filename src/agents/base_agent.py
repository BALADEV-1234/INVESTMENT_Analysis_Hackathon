# Base Agent Class for Multi-Agent System
import os
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langsmith import traceable
import langsmith
import asyncio
import os

class AgentState(TypedDict):
    """State for LangGraph agent workflow."""
    raw_text: str
    chunks: List[str]
    chunk_summaries: List[str]
    final_summary: str
    error: Optional[str]
    metadata: Dict[str, Any]

class BaseAgent(ABC):
    """Base class for all specialized agents."""

    # Guardrails: Agent execution limits
    AGENT_TIMEOUT_SECONDS = 600
    MAX_CONTENT_LENGTH = 1_000_000  # 1M characters
    MAX_CHUNKS = 100  # Maximum number of chunks to process
    MIN_CONTENT_LENGTH = 10  # Minimum meaningful content

    def __init__(self):
        """Initialize the base agent with LLM, text splitter, and StateGraph."""
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
            temperature=0.1
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200,
            length_function=len
        )
        self.workflow = self._build_workflow()

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass
    
    @abstractmethod
    def get_analysis_prompt(self) -> ChatPromptTemplate:
        """Return the analysis prompt template for this agent."""
        pass
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for this agent."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("chunk_text", self._chunk_text_node)
        workflow.add_node("map_chunks", self._map_chunks_node)
        workflow.add_node("reduce_summaries", self._reduce_summaries_node)
        
        # Add edges
        workflow.set_entry_point("chunk_text")
        workflow.add_edge("chunk_text", "map_chunks")
        workflow.add_edge("map_chunks", "reduce_summaries")
        workflow.add_edge("reduce_summaries", END)
        
        return workflow.compile()

    @traceable(name="analyze_content")
    async def analyze(self, content: str) -> Dict[str, Any]:
        """Main analysis method using LangGraph workflow."""
        try:
            # Guardrail: Wrap analysis in timeout
            result = await asyncio.wait_for(
                self._analyze_internal(content),
                timeout=self.AGENT_TIMEOUT_SECONDS
            )
            return result

        except asyncio.TimeoutError:
            return {
                "analysis": f"Agent {self.__class__.__name__} exceeded {self.AGENT_TIMEOUT_SECONDS}s timeout",
                "confidence": 0.0,
                "error": "timeout",
                "metadata": {
                    "agent_type": self.__class__.__name__,
                    "timeout_seconds": self.AGENT_TIMEOUT_SECONDS,
                    "status": "timeout"
                }
            }

        except Exception as e:
            return {
                "analysis": f"Error during analysis: {str(e)}",
                "confidence": 0.0,
                "error": str(e),
                "metadata": {"agent_type": self.__class__.__name__}
            }

    async def _analyze_internal(self, content: str) -> Dict[str, Any]:
        """Internal analysis logic separated for timeout handling."""

        # Guardrail: Validate content length
        if len(content) < self.MIN_CONTENT_LENGTH:
            return {
                "analysis": f"Content too short to analyze (minimum {self.MIN_CONTENT_LENGTH} characters)",
                "confidence": 0.0,
                "error": "content_too_short",
                "metadata": {"agent_type": self.__class__.__name__, "content_length": len(content)}
            }

        if len(content) > self.MAX_CONTENT_LENGTH:
            # Truncate instead of failing
            content = content[:self.MAX_CONTENT_LENGTH]
            truncated = True
        else:
            truncated = False

        # Initialize state
        initial_state = AgentState(
            raw_text=content,
            chunks=[],
            chunk_summaries=[],
            final_summary="",
            error=None,
            metadata={
                "agent_type": self.__class__.__name__,
                "content_truncated": truncated,
                "original_length": len(content)
            }
        )

        # Run the workflow
        result = await self.workflow.ainvoke(initial_state)

        if result.get("error"):
            return {
                "analysis": f"Error during analysis: {result.get('error', 'Unknown error')}",
                "confidence": 0.0,
                "error": result.get("error", "Unknown error"),
                "metadata": result.get("metadata", {})
            }

        # Guardrail: Safely access result fields
        final_summary = result.get("final_summary", "")
        if not final_summary:
            return {
                "analysis": "Analysis completed but no summary generated",
                "confidence": 0.0,
                "error": "missing_final_summary",
                "metadata": result.get("metadata", {})
            }

        return {
            "analysis": final_summary,
            "confidence": self._calculate_confidence(result),
            "metadata": result.get("metadata", {})
        }

    @traceable(name="chunk_text_node")
    async def _chunk_text_node(self, state: AgentState) -> AgentState:
        """Node to chunk the input text."""
        try:
            chunks = self.text_splitter.split_text(state["raw_text"])
            if not chunks:
                state["error"] = "No text chunks produced"
                return state

            # Guardrail: Limit number of chunks to prevent memory issues
            if len(chunks) > self.MAX_CHUNKS:
                print(f"⚠ Warning: {len(chunks)} chunks produced, limiting to {self.MAX_CHUNKS}")
                chunks = chunks[:self.MAX_CHUNKS]
                state["metadata"]["chunks_truncated"] = True
                state["metadata"]["original_chunk_count"] = len(chunks)

            state["chunks"] = chunks
            state["metadata"]["num_chunks"] = len(chunks)
            state["metadata"]["avg_chunk_length"] = sum(len(chunk) for chunk in chunks) / len(chunks)

            # Add LangSmith metadata
            if os.getenv("LANGSMITH_API_KEY"):
                langsmith.get_current_run_tree().add_metadata({
                    "num_chunks": len(chunks),
                    "avg_chunk_length": state["metadata"]["avg_chunk_length"],
                    "chunks_truncated": state["metadata"].get("chunks_truncated", False)
                })

            return state
        except Exception as e:
            state["error"] = f"Error chunking text: {str(e)}"
            return state

    @traceable(name="map_chunks_node")
    async def _map_chunks_node(self, state: AgentState) -> AgentState:
        """Node to analyze each chunk in parallel (map phase)."""
        try:
            chunks = state["chunks"]
            summaries = await asyncio.gather(*[self._summarize_chunk(chunk) for chunk in chunks])
            
            state["chunk_summaries"] = summaries
            state["metadata"]["chunks_processed"] = len(chunks)
            state["metadata"]["summaries_generated"] = len(summaries)
            
            # Add LangSmith metadata
            if os.getenv("LANGSMITH_API_KEY"):
                langsmith.get_current_run_tree().add_metadata({
                    "chunks_processed": len(chunks),
                    "summaries_generated": len(summaries)
                })
            
            return state
        except Exception as e:
            state["error"] = f"Error in map phase: {str(e)}"
            return state

    @traceable(name="reduce_summaries_node")
    async def _reduce_summaries_node(self, state: AgentState) -> AgentState:
        """Node to combine chunk summaries into final summary (reduce phase)."""
        try:
            summaries = state["chunk_summaries"]
            joined = "\n\n".join(summaries)
            
            reduce_prompt = ChatPromptTemplate.from_messages([
                ("system", self.get_system_prompt()),
                ("human", """
                Synthesize these individual analyses into a comprehensive final summary.
                Remove redundancy and create a cohesive, well-structured analysis.
                
                Individual Analyses:
                {summaries}
                
                Provide a comprehensive synthesis following the analysis format for this agent type.
                """)
            ])
            
            messages = reduce_prompt.format_messages(summaries=joined)
            response = await self.llm.ainvoke(messages)

            # Guardrail: Validate LLM response
            if not response or not response.content:
                state["error"] = "LLM returned empty response in reduce phase"
                return state

            if len(response.content) < 50:  # Suspiciously short
                state["error"] = f"LLM response too short: {len(response.content)} chars"
                return state

            state["final_summary"] = response.content
            state["metadata"]["final_summary_length"] = len(response.content)
            state["metadata"]["input_summaries_count"] = len(summaries)
            
            # Add LangSmith metadata
            if os.getenv("LANGSMITH_API_KEY"):
                langsmith.get_current_run_tree().add_metadata({
                    "input_summaries_count": len(summaries),
                    "combined_length": len(joined),
                    "final_summary_length": len(response.content)
                })
            
            return state
        except Exception as e:
            state["error"] = f"Error in reduce phase: {str(e)}"
            return state

    @traceable(name="summarize_chunk")
    async def _summarize_chunk(self, chunk: str) -> str:
        """Summarize a single chunk of content."""
        try:
            prompt = self.get_analysis_prompt()
            messages = prompt.format_messages(content=chunk)
            response = await self.llm.ainvoke(messages)

            # Guardrail: Validate LLM response
            if not response or not response.content:
                return "Error: LLM returned empty response"

            if len(response.content) < 20:  # Suspiciously short for a summary
                return f"Error: LLM response too short ({len(response.content)} chars)"

            return response.content
        except Exception as e:
            return f"Error analyzing chunk: {str(e)}"

    def _calculate_confidence(self, result: AgentState) -> float:
        """Calculate confidence score based on analysis results."""
        try:
            metadata = result.get("metadata", {})
            num_chunks = metadata.get("num_chunks", 1)
            final_length = metadata.get("final_summary_length", 0)
            
            # Base confidence from content volume
            volume_score = min(1.0, final_length / 1000)  # Normalize to 1000 chars
            
            # Chunk processing score
            chunk_score = min(1.0, num_chunks / 5)  # Optimal around 5 chunks
            
            # Combined confidence
            confidence = (volume_score * 0.6) + (chunk_score * 0.4)
            
            return min(0.95, max(0.1, confidence))
        except:
            return 0.5  # Default confidence
