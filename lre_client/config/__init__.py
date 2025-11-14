import ssl
from .constants import PROJECT_ROOT, ENV_FILE_PATH
from .manager import SettingsManager
from .models import BaseLRESettings
from .ssl_context import SSLContextFactory

# Global settings manager
_settings_manager = SettingsManager(PROJECT_ROOT)

def get_settings() -> BaseLRESettings:
    """Get the settings instance."""
    return _settings_manager.get_settings()

def create_ssl_context(settings: BaseLRESettings) -> ssl.SSLContext | None:
    """Create SSL context from settings."""
    return SSLContextFactory.create(settings)

def get_ssl_verify_setting(settings: BaseLRESettings) -> bool | str:
    """Get SSL verify setting for requests."""
    return SSLContextFactory.get_verify_setting(settings)

__all__ = [
    "BaseLRESettings",
    "get_settings",
    "create_ssl_context",
    "get_ssl_verify_setting",
]