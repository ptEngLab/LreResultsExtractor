from pathlib import Path
from typing import Optional
from lre_client.config.models import BaseLRESettings
from lre_client.config.path_resolver import PathResolver


class SettingsManager:
    """Manages settings lifecycle including resolution and validation."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self._instance: Optional[BaseLRESettings] = None

    def load_settings(self) -> BaseLRESettings:
        """Load and validate settings."""
        # noinspection PyArgumentList
        settings = BaseLRESettings()
        settings = self._resolve_paths(settings)
        self._validate_settings(settings)
        return settings

    def _resolve_paths(self, settings: BaseLRESettings) -> BaseLRESettings:
        """Resolve CA certificate file path."""
        settings.lre_ca_cert_path = PathResolver.resolve_config_path(
            self.project_root, settings.lre_ca_cert_path
        )
        return settings

    @staticmethod
    def _validate_settings(settings: BaseLRESettings) -> None:
        """Validate CA certificate file existence."""
        PathResolver.validate_ssl_files(settings)

    def get_settings(self) -> BaseLRESettings:
        """Get settings instance (singleton pattern)."""
        if self._instance is None:
            self._instance = self.load_settings()
        return self._instance