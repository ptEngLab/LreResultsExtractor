import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from lre_client.config import get_settings, get_ssl_verify_setting


class HttpSessionFactory:
    """Factory for creating configured HTTP sessions."""

    @staticmethod
    def create(settings=None):
        settings = settings or get_settings()
        session = requests.Session()

        # Retry configuration
        retry = Retry(
            total=settings.lre_max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
            backoff_factor=settings.lre_retry_backoff,
            respect_retry_after_header=True
        )

        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # SSL configuration
        session.verify = get_ssl_verify_setting(settings)

        # Headers
        session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": settings.lre_user_agent,
        })

        return session