from typing import Optional

from lre_client.api.base_api import LREBaseAPI
from lre_client.api.endpoints import RUN_STATUS
from lre_client.api.exceptions import LREAPIError
from lre_client.utils.logger import get_logger

log = get_logger(__name__)


class LRERunsAPI:
    """Provides access to the LRE Runs API."""

    BASE_PATH = "loadTest/rest-pcweb/Runs"

    def __init__(self, base_api: LREBaseAPI):
        self.api = base_api
        self.settings = base_api.settings  # settings contains username, password, run_id, etc.

    def get_run_status(self, run_id: Optional[int] = None) -> Optional[dict]:
        """
        Get a single run by ID (default to settings.run_id).

        :param run_id: Optional run ID to filter
        :return: First run dict from the API response, or None if not found
        """
        # Use run_id from settings if not explicitly provided
        if run_id is None:
            run_id = getattr(self.settings, "lre_run_id", None)
            if run_id is None:
                raise ValueError("Run ID not provided and not found in settings.")

        payload = {
            "Filters": [{"Field": "Id", "Type": "EqualTo", "Values": [run_id]}],
            "Sorting": [],
            "PageIndex": -1,
            "PageSize": 0
        }

        log.debug(f"Fetching run with payload: {payload}")
        response = self.api.post(RUN_STATUS, json=payload)
        if response.status_code != 200:
            raise LREAPIError(f"Failed to fetch run: {response.text}")

        data = response.json()
        if not data:
            log.warning(f"No runs found for run_id={run_id}")
            return None

        return data[0]
