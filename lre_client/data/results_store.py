from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from lre_client.utils.logger import get_logger

log = get_logger(__name__)

@dataclass
class ResultsStore:
    """Stores and manages LRE results data."""

    run_status: Optional[Dict[str, Any]] = None
    hosts: list = field(default_factory=list)
    test_results: list = field(default_factory=list)

    def update_run_status(self, run_status: Dict[str, Any]) -> None:
        """Update run status and log the change."""
        self.run_status = run_status
        log.info(f"Run status updated: {run_status.get('State', 'Unknown')}")

    def update_hosts(self, hosts: list) -> None:
        """Update hosts list."""
        self.hosts = hosts
        log.info(f"Hosts updated: {len(hosts)} hosts")

    def get_run_status_summary(self) -> str:
        """Get a summary of the run status."""
        if not self.run_status:
            return "No run status available"

        status = self.run_status.get('State', 'Unknown')
        run_id = self.run_status.get('Id', 'Unknown')
        return f"Run {run_id} status: {status}"

    def clear(self) -> None:
        """Clear all stored results."""
        self.run_status = None
        self.hosts.clear()
        self.test_results.clear()
        log.debug("Results store cleared")