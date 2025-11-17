from pathlib import Path
from typing import Optional
from .settings import BaseLRESettings
from .path_resolver import PathResolver
from .constants import PROJECT_ROOT


class SettingsManager:
    """
    Loads, resolves, and validates application settings.
    Singleton pattern ensures only one settings instance is created.
    """

    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = project_root
        self._instance: Optional[BaseLRESettings] = None

    def load_settings(self) -> BaseLRESettings:
        """Load settings from environment + .env file, then resolve and validate."""
        #noinspection PyArgumentList
        settings = BaseLRESettings()
        settings = self._resolve_paths(settings)
        self._validate_settings(settings)
        return settings

    def _resolve_paths(self, settings: BaseLRESettings) -> BaseLRESettings:
        """Resolve CA certificate relative paths."""
        settings.lre_ca_cert_path = PathResolver.resolve_config_path(
            self.project_root,
            settings.lre_ca_cert_path
        )
        return settings

    @staticmethod
    def _validate_settings(settings: BaseLRESettings) -> None:
        """Validate all required paths."""
        PathResolver.validate_ssl_files(settings)

    def get_settings(self) -> BaseLRESettings:
        """Return a cached settings instance."""
        if self._instance is None:
            self._instance = self.load_settings()
        return self._instance
