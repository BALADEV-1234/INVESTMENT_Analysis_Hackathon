# Analysis Storage Manager - Local JSON-based storage
import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class AnalysisStorage:
    """Manages local storage of investment analysis results."""

    def __init__(self, storage_dir: str = "data/analyses"):
        """Initialize storage with a directory path."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        self._initialize_index()

    def _initialize_index(self):
        """Initialize or load the index file."""
        if not self.index_file.exists():
            self._save_index([])

    def _load_index(self) -> List[Dict[str, Any]]:
        """Load the index of all saved analyses."""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading index: {e}")
            return []

    def _save_index(self, index: List[Dict[str, Any]]):
        """Save the index file."""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving index: {e}")

    def _sanitize_filename(self, company_name: str) -> str:
        """Convert company name to safe filename."""
        # Remove special characters and replace spaces
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in company_name)
        safe_name = safe_name.strip().replace(' ', '_')
        return safe_name.lower()

    def _generate_analysis_id(self, company_name: str) -> str:
        """Generate unique ID for analysis."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = self._sanitize_filename(company_name)
        return f"{safe_name}_{timestamp}"

    async def save_analysis(
        self,
        company_name: str,
        analysis_result: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save analysis result to local storage.

        Args:
            company_name: Name of the company analyzed
            analysis_result: Full analysis result dictionary
            metadata: Optional additional metadata

        Returns:
            Storage record with ID and metadata
        """
        # Generate unique ID
        analysis_id = self._generate_analysis_id(company_name)
        filename = f"{analysis_id}.json"
        filepath = self.storage_dir / filename

        # Create storage record
        storage_record = {
            "id": analysis_id,
            "company_name": company_name,
            "timestamp": datetime.now().isoformat(),
            "filename": filename,
            "scores": analysis_result.get("investment_scores", {}),
            "recommendation": analysis_result.get("investment_scores", {}).get("recommendation", "Unknown"),
            "confidence": analysis_result.get("final_summary", {}).get("confidence", 0.0),
            "metadata": {
                "files_processed": analysis_result.get("metadata", {}).get("total_files_processed", 0),
                "processing_time": analysis_result.get("metadata", {}).get("processing_time_seconds", 0),
                "web_search_performed": analysis_result.get("web_intelligence", {}).get("search_performed", False),
                **(metadata or {})
            }
        }

        # Save full analysis data
        analysis_data = {
            "storage_record": storage_record,
            "analysis_result": analysis_result
        }

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)

            # Update index
            index = self._load_index()
            index.append(storage_record)
            # Keep index sorted by timestamp (newest first)
            index.sort(key=lambda x: x["timestamp"], reverse=True)
            self._save_index(index)

            print(f"✓ Analysis saved: {analysis_id}")
            return storage_record

        except Exception as e:
            print(f"Error saving analysis: {e}")
            raise

    async def load_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Load analysis by ID."""
        filename = f"{analysis_id}.json"
        filepath = self.storage_dir / filename

        if not filepath.exists():
            print(f"Analysis not found: {analysis_id}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("analysis_result")
        except Exception as e:
            print(f"Error loading analysis {analysis_id}: {e}")
            return None

    async def delete_analysis(self, analysis_id: str) -> bool:
        """Delete analysis by ID."""
        filename = f"{analysis_id}.json"
        filepath = self.storage_dir / filename

        try:
            # Delete file
            if filepath.exists():
                filepath.unlink()

            # Update index
            index = self._load_index()
            index = [record for record in index if record["id"] != analysis_id]
            self._save_index(index)

            print(f"✓ Analysis deleted: {analysis_id}")
            return True

        except Exception as e:
            print(f"Error deleting analysis {analysis_id}: {e}")
            return False

    async def list_analyses(
        self,
        company_name: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List all saved analyses with optional filtering.

        Args:
            company_name: Filter by company name (partial match)
            limit: Maximum number of results

        Returns:
            List of analysis records (metadata only, not full data)
        """
        index = self._load_index()

        # Filter by company name if provided
        if company_name:
            company_lower = company_name.lower()
            index = [
                record for record in index
                if company_lower in record["company_name"].lower()
            ]

        # Apply limit
        if limit:
            index = index[:limit]

        return index

    async def get_latest_analysis(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Get the most recent analysis for a company."""
        analyses = await self.list_analyses(company_name=company_name, limit=1)
        if analyses:
            return await self.load_analysis(analyses[0]["id"])
        return None

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get statistics about stored analyses."""
        index = self._load_index()

        total_size = 0
        for record in index:
            filepath = self.storage_dir / record["filename"]
            if filepath.exists():
                total_size += filepath.stat().st_size

        return {
            "total_analyses": len(index),
            "storage_path": str(self.storage_dir.absolute()),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "companies_analyzed": len(set(record["company_name"] for record in index)),
            "oldest_analysis": index[-1]["timestamp"] if index else None,
            "newest_analysis": index[0]["timestamp"] if index else None
        }
