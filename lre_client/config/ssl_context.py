import ssl
from typing import Optional
from .settings import BaseLRESettings


class SSLContextFactory:
    """Factory for creating SSLContext objects based on configuration."""

    @staticmethod
    def create(settings: BaseLRESettings) -> Optional[ssl.SSLContext]:
        """
        Create and configure an SSL context.

        Returns:
            SSLContext instance or None if SSL verification is disabled.
        """
        if not settings.lre_verify_ssl:
            return None

        context = ssl.create_default_context()

        if settings.lre_ca_cert_path:
            context.load_verify_locations(cafile=str(settings.lre_ca_cert_path))

        return context

    @staticmethod
    def get_verify_setting(settings: BaseLRESettings) -> bool | str:
        """
        Get the correct "verify" value for `requests` (bool, path string).
        """
        if not settings.lre_verify_ssl:
            return False

        if settings.lre_ca_cert_path:
            return str(settings.lre_ca_cert_path)

        return True
