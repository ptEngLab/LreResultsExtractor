from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class RunResult:
    """Represents a test result within a run based on the actual API response."""
    id: int
    name: str
    type: str  # Changed from result_type to type to match API
    run_id: int

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'RunResult':
        """Create RunResult from API response data."""
        # Convert string IDs to integers
        result_id = int(data['ID']) if 'ID' in data else 0
        run_id = int(data['RunID']) if 'RunID' in data else 0

        return cls(
            id=result_id,
            name=data.get('Name', ''),
            type=data.get('Type', ''),
            run_id=run_id
        )

    @property
    def is_analyzed(self) -> bool:
        """Check if this result is an analyzed result."""
        return self.type.upper() == "ANALYZED RESULT"

    @property
    def is_raw_results(self) -> bool:
        """Check if this result is raw results."""
        return self.type.upper() == "RAW RESULTS"

    @property
    def is_html_report(self) -> bool:
        """Check if this result is HTML report."""
        return self.type.upper() == "HTML REPORT"

    @property
    def is_rich_report(self) -> bool:
        """Check if this result is rich report."""
        return self.type.upper() == "RICH REPORT"


@dataclass
class RunResultsCollection:
    """Collection of results for a specific run."""
    run_id: int
    results: List[RunResult]

    @classmethod
    def from_api_response(cls, run_id: int, data: List[Dict[str, Any]]) -> 'RunResultsCollection':
        """Create RunResultsCollection from API response data."""
        results = [RunResult.from_api_response(item) for item in data]
        return cls(run_id=run_id, results=results)

    @property
    def analyzed_results(self) -> List[RunResult]:
        """Get all analyzed results."""
        return [result for result in self.results if result.is_analyzed]

    @property
    def raw_results(self) -> List[RunResult]:
        """Get all raw results."""
        return [result for result in self.results if result.is_raw_results]

    @property
    def html_reports(self) -> List[RunResult]:
        """Get all HTML reports."""
        return [result for result in self.results if result.is_html_report]

    @property
    def rich_reports(self) -> List[RunResult]:
        """Get all rich reports."""
        return [result for result in self.results if result.is_rich_report]

    @property
    def latest_analyzed_result(self) -> Optional[RunResult]:
        """Get the analyzed result (should be only one per run)."""
        analyzed = self.analyzed_results
        return analyzed[0] if analyzed else None

    def get_analyzed_result_id(self) -> Optional[int]:
        """Get the ID of the analyzed result."""
        analyzed = self.latest_analyzed_result
        return analyzed.id if analyzed else None

    def get_result_by_id(self, result_id: int) -> Optional[RunResult]:
        """Get a specific result by ID."""
        return next((result for result in self.results if result.id == result_id), None)

    def get_results_by_type(self, result_type: str) -> List[RunResult]:
        """Get all results of a specific type."""
        return [result for result in self.results if result.type.upper() == result_type.upper()]

    def summary(self) -> Dict[str, Any]:
        """Get summary information about the result's collection."""
        return {
            'run_id': self.run_id,
            'total_results': len(self.results),
            'analyzed_results_count': len(self.analyzed_results),
            'raw_results_count': len(self.raw_results),
            'html_reports_count': len(self.html_reports),
            'rich_reports_count': len(self.rich_reports),
            'analyzed_result_id': self.get_analyzed_result_id(),
            'available_types': list(set(result.type for result in self.results))
        }