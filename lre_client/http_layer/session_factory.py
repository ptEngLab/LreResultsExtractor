import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from lre_client.config.settings import create_ssl_context

class HttpSessionFactory:
    @staticmethod
    def create(settings):
        session = requests.Session()

        # Retry config
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

        # SSL setup
        if not settings.lre_verify_ssl:
            session.verify = False
        else:
            ssl_context = create_ssl_context(settings)
            session.verify = str(settings.lre_ca_cert_path) if ssl_context else True

        # Headers
        session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": settings.lre_user_agent,
        })
        return session
