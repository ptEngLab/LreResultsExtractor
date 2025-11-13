from lre_client.utils.logger import get_logger
from lre_client.api.exceptions import LREAuthenticationError
from lre_client.api.endpoints import AUTHENTICATION_POINT, WEB_LOGIN, LOGOUT

log = get_logger(__name__)


class LREAuthenticator:
    """Handles login/logout for LoadRunner Enterprise using client credentials and project context."""



    def __init__(self, api):
        self.api = api
        self.settings = api.settings
        self.executor = api.executor
        self.session = api.session
        self.authenticated = False
        self.web_logged_in = False

    def login_with_client_credentials(self) -> None:
        """Authenticate with LRE using client credentials and log into the project."""
        if self.authenticated:
            log.debug("Already authenticated; skipping authentication.")
            return

        log.debug("Logging into LRE using client credentials...")
        url = self.api.build_url(AUTHENTICATION_POINT)

        payload = {
            "ClientIdKey": self.settings.lre_client_id,
            "ClientSecretKey": self.settings.lre_client_secret,
        }

        try:
            self.executor.execute("POST", url, json=payload)
            self.authenticated = True
            log.debug("LRE authentication succeeded.")
            self.login_to_project()
        except Exception as e:
            log.error(f"LRE authentication failed: {e}")
            raise LREAuthenticationError(f"Authentication failed: {e}")

    def login_to_project(self) -> None:
        """Login to specific domain/project after authenticating."""
        if not self.authenticated:
            raise LREAuthenticationError("Cannot log in to project before authenticating.")
        if self.web_logged_in:
            log.debug("Already logged into project; skipping.")
            return

        url = self.api.build_url(WEB_LOGIN)
        params = {
            "domain": self.settings.lre_domain,
            "project": self.settings.lre_project,
        }

        log.debug(f"Logging into project (domain={params['domain']}, project={params['project']})")
        try:
            self.executor.execute("GET", url, params=params)
            self.web_logged_in = True
            log.debug("Successfully logged into LRE project.")
        except Exception as e:
            log.error(f"Failed to log into project: {e}")
            raise LREAuthenticationError(f"Project login failed: {e}")

    def logout(self) -> None:
        """Logout from LRE and clear session cookies."""
        if not self.authenticated:
            log.debug("Logout skipped: not authenticated.")
            return

        log.debug("Logging out from LRE...")
        url = self.api.build_url(LOGOUT)
        try:
            self.executor.execute("GET", url)
            log.debug("Successfully logged out from LRE.")
        except Exception as e:
            log.warning(f"Logout encountered an issue: {e}")
        finally:
            self.session.cookies.clear()
            self.authenticated = False
            self.web_logged_in = False
