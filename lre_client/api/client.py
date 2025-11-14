from lre_client.api.base_api import LREBaseAPI
from lre_client.api.hosts_api import LREHostsAPI
from lre_client.api.runs_api import LRERunsAPI
from lre_client.utils.logger import get_logger
from lre_client.api.exceptions import LREAuthenticationError
from lre_client.api.results_api import LREResultsAPI

log = get_logger(__name__)

class LREClient(LREBaseAPI):
    """Unified client for all LRE APIs with automatic authentication."""

    def __init__(self, settings=None):
        super().__init__(settings)
        # Initialize API modules
        self.hosts = LREHostsAPI(self)
        self.runs = LRERunsAPI(self)
        self.results = LREResultsAPI(self)

    def _ensure_authenticated(self):
        """Authenticate automatically if not already authenticated."""
        if not self.auth.authenticated:
            log.debug("Automatically logging in...")
            try:
                self.auth.login_with_client_credentials()
            except LREAuthenticationError as e:
                log.error(f"Automatic login failed: {e}")
                raise

    def request(self, method: str, endpoint: str, **kwargs):
        """Override base request to ensure authentication automatically."""
        self._ensure_authenticated()
        return super().request(method, endpoint, **kwargs)

    def __enter__(self):
        """Context manager entry - authenticate immediately."""
        log.debug("Entering LREClient context manager")
        # Auto-login when entering context
        self._ensure_authenticated()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Logout automatically on context exit."""
        log.debug("Exiting LREClient context manager")
        try:
            if self.auth.authenticated:
                log.debug("Automatically logging out...")
                self.auth.logout()
        except Exception as e:
            log.warning(f"Error during logout: {e}")
        finally:
            self.close()