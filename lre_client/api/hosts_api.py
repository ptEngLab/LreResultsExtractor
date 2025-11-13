from lre_client.api.base_api import LREBaseAPI
from lre_client.api.exceptions import LREAPIError
from lre_client.utils.logger import get_logger

log = get_logger(__name__)


class LREHostsAPI:
    """Provides access to the LRE Hosts Management API."""

    BASE_PATH = "LoadTest/rest/domains/{domain}/projects/{project}/hosts"

    def __init__(self, base_api: LREBaseAPI):
        self.api = base_api
        self.settings = base_api.settings

    def _path(self, suffix: str = "") -> str:
        """Build domain/project-scoped endpoint path."""
        return self.BASE_PATH.format(
            domain=self.settings.lre_domain,
            project=self.settings.lre_project,
        ) + suffix

    def list_hosts(self):
        """Get a list of all hosts."""
        endpoint = self._path()
        log.debug(f"Fetching host list: {endpoint}")
        response = self.api.get(endpoint)
        return response.json()

    def get_host(self, host_id: int):
        """Get host details by ID."""
        endpoint = self._path(f"/{host_id}")
        log.debug(f"Fetching host details for host_id={host_id}")
        response = self.api.get(endpoint)
        return response.json()

    def add_host(self, name: str, description: str = ""):
        """Add a new host to LRE."""
        endpoint = self._path()
        payload = {
            "name": name,
            "description": description,
        }

        log.debug(f"Adding new host: {payload}")
        response = self.api.post(endpoint, json=payload)
        if response.status_code not in (200, 201):
            raise LREAPIError(f"Failed to add host: {response.text}")
        return response.json()

    def delete_host(self, host_id: int):
        """Delete a host by ID."""
        endpoint = self._path(f"/{host_id}")
        log.debug(f"Deleting host: {host_id}")
        response = self.api.delete(endpoint)
        return response.status_code == 200
