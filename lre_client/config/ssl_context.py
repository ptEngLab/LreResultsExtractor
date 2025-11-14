import ssl
from typing import Optional

from lre_client.config.models import BaseLRESettings


class SSLContextFactory:
    """Creates and configures SSL contexts for CA certificates only."""

    @staticmethod
    def create(settings: BaseLRESettings) -> Optional[ssl.SSLContext]:
        """
        Create SSL context with custom CA certificates if provided.

        Returns:
            Configured SSLContext or None if SSL verification is disabled
        """
        if not settings.lre_verify_ssl:
            return None

        ssl_context = ssl.create_default_context()

        # Load custom CA certificate if provided
        if settings.lre_ca_cert_path:
            ssl_context.load_verify_locations(cafile=str(settings.lre_ca_cert_path))

        return ssl_context

    @staticmethod
    def get_verify_setting(settings: BaseLRESettings) -> bool | str:
        """Get the appropriate verify setting for requests."""
        if not settings.lre_verify_ssl:
            return False

        if settings.lre_ca_cert_path:
            return str(settings.lre_ca_cert_path)

        return True