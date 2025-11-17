from dataclasses import dataclass
from typing import Optional, List, Dict, Any


def normalize_result_type(value: str) -> str:
    """Normalize API result type strings to canonical types."""
    if not value:
        return ""
    value = value.strip().upper()
    mapping = {
        "ANALYZED RESULT": "ANALYZED",
        "RAW RESULTS": "RAW",
        "HTML REPORT": "HTML",
        "RICH REPORT": "RICH",
        "ERROR MESSAGES": "ERROR",
        "OUTPUT LOG": "LOG",
    }
    return mapping.get(value, value)


@dataclass
class RunResult:
    """Represents a single test result in a run."""
    id: int
    name: str
    type: str
    run_id: int

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'RunResult':
        result_id = int(data['ID']) if 'ID' in data else 0
        run_id = int(data['RunID']) if 'RunID' in data else 0
        type_normalized = normalize_result_type(data.get('Type', ''))
        return cls(
            id=result_id,
            name=data.get('Name', ''),
            type=type_normalized,
            run_id=run_id
        )

    @property
    def is_analyzed(self) -> bool:
        return self.type == "ANALYZED"

    @property
    def is_raw(self) -> bool:
        return self.type == "RAW"

    @property
    def is_html(self) -> bool:
        return self.type == "HTML"

    @property
    def is_rich(self) -> bool:
        return self.type == "RICH"

    @property
    def is_error(self) -> bool:
        return self.type == "ERROR"

    @property
    def is_log(self) -> bool:
        return self.type == "LOG"


@dataclass
class RunResultsCollection:
    """Collection of results for a specific run."""
    run_id: int
    results: List[RunResult]

    @classmethod
    def from_api_response(cls, run_id: int, data: List[Dict[str, Any]]) -> 'RunResultsCollection':
        results = [RunResult.from_api_response(item) for item in data]
        return cls(run_id=run_id, results=results)

    @property
    def analyzed(self) -> List[RunResult]:
        return [r for r in self.results if r.is_analyzed]

    @property
    def raw(self) -> List[RunResult]:
        return [r for r in self.results if r.is_raw]

    @property
    def html(self) -> List[RunResult]:
        return [r for r in self.results if r.is_html]

    @property
    def rich(self) -> List[RunResult]:
        return [r for r in self.results if r.is_rich]

    @property
    def error(self) -> List[RunResult]:
        return [r for r in self.results if r.is_error]

    @property
    def log(self) -> List[RunResult]:
        return [r for r in self.results if r.is_log]

    @property
    def latest_analyzed(self) -> Optional[RunResult]:
        return self.analyzed[0] if self.analyzed else None

    @property
    def latest_html(self) -> Optional[RunResult]:
        return self.html[0] if self.html else None

    def get_analyzed_result_id(self) -> Optional[int]:
        result = self.latest_analyzed
        return result.id if result else None

    def get_html_result_id(self) -> Optional[int]:
        result = self.latest_html
        return result.id if result else None

    def get_result_by_id(self, result_id: int) -> Optional[RunResult]:
        return next((r for r in self.results if r.id == result_id), None)

    def get_results_by_type(self, result_type: str) -> List[RunResult]:
        type_normalized = normalize_result_type(result_type)
        return [r for r in self.results if r.type == type_normalized]

    def summary(self) -> Dict[str, Any]:
        return {
            'run_id': self.run_id,
            'total_results': len(self.results),
            'analyzed_count': len(self.analyzed),
            'raw_count': len(self.raw),
            'html_count': len(self.html),
            'rich_count': len(self.rich),
            'error_count': len(self.error),
            'log_count': len(self.log),
            'analyzed_result_id': self.get_analyzed_result_id(),
            'html_result_id': self.get_html_result_id(),
            'available_types': list({r.type for r in self.results})
        }
