from lre_client.utils.logger import get_logger
import requests
from lre_client.api.exceptions import (
    LREConnectionError,
    LREAuthenticationError,
    LREAPIError,
)




class LRERequestExecutor:
    """Executes HTTP requests with consistent error handling and defaults."""

    def __init__(self, session: requests.Session, settings):
        self.session = session
        self.settings = settings
        self.logger = get_logger(__name__)

    def execute(
            self,
            method: str,
            url: str,
            headers: dict | None = None,
            params: dict | None = None,
            json: dict | None = None,
            timeout: float | None = None,
            **kwargs,
    ) -> requests.Response:
        """
        Execute an HTTP request with retries, timeouts, and error translation.
        """

        headers = {**self.session.headers, **(headers or {})}
        timeout = timeout or self.settings.lre_timeout

        self.logger.debug(
            "HTTP %s %s | headers=%s | params=%s | json=%s | timeout=%s",
            method, url, headers, params, json, timeout
        )

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                timeout=timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response

        except requests.exceptions.ConnectionError as e:
            raise LREConnectionError(f"Connection error: {e}")

        except requests.exceptions.Timeout:
            raise LREConnectionError(f"Timeout after {timeout}s")

        except requests.exceptions.HTTPError as e:
            resp = e.response
            status = resp.status_code if resp else "unknown"
            body = resp.text.strip() if resp and resp.text else str(e)

            if status in (401, 403):
                raise LREAuthenticationError(f"Authentication failed: HTTP {status}")
            raise LREAPIError(f"HTTP {status}: {body}")
