from urllib.parse import urljoin
from lre_client.http_layer.session_factory import HttpSessionFactory
from lre_client.http_layer.request_executor import LRERequestExecutor
from lre_client.config import get_settings
from lre_client.api.auth import LREAuthenticator
from lre_client.api.exceptions import LREAuthenticationError
from lre_client.utils.logger import get_logger

log = get_logger(__name__)


class LREBaseAPI:
    """Base client interface for LoadRunner Enterprise API."""

    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        log.debug(f"Initializing LREBaseAPI with settings: {self.settings}")

        self.session = HttpSessionFactory.create(self.settings)
        self.executor = LRERequestExecutor(self.session, self.settings)
        self.auth = LREAuthenticator(self)

    def build_url(self, endpoint: str) -> str:
        url = urljoin(self.settings.base_url + "/", endpoint.lstrip("/"))
        log.debug(f"Built URL: {url}")
        return url


    def request(self, method: str, endpoint: str, **kwargs):
        """Generic API request method with authentication enforcement."""
        if not self.auth.authenticated and not endpoint.startswith("LoadTest/rest/authentication-point/"):
            raise LREAuthenticationError("Client not authenticated. Call login_with_client_credentials() first.")

        url = self.build_url(endpoint)
        log.debug(f"Preparing {method} request for endpoint: {endpoint}")

        try:
            response = self.executor.execute(method, url, **kwargs)
            log.debug(f"Response received (HTTP {response.status_code})")
            return response
        except Exception as e:
            log.error(f"Request to {url} failed: {e}")
            raise

    # Convenience methods
    def get(self, endpoint, **kwargs): return self.request("GET", endpoint, **kwargs)
    def post(self, endpoint, **kwargs): return self.request("POST", endpoint, **kwargs)
    def put(self, endpoint, **kwargs): return self.request("PUT", endpoint, **kwargs)
    def delete(self, endpoint, **kwargs): return self.request("DELETE", endpoint, **kwargs)

    def close(self) -> None:
        log.debug("Closing HTTP session...")
        self.session.close()

    def __enter__(self):
        log.debug("Entering LREBaseAPI context manager")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.debug("Exiting LREBaseAPI context manager")
        self.auth.logout()
        self.close()
