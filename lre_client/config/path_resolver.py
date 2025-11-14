from pathlib import Path
from typing import Optional
from lre_client.config.models import BaseLRESettings


class PathResolver:
    """Handles path resolution and validation for CA certificate files."""

    @staticmethod
    def resolve_config_path(project_root: Path, path: Optional[Path]) -> Optional[Path]:
        """Resolve relative paths relative to project root."""
        if not path:
            return None

        if not path.is_absolute():
            resolved_path = project_root / path
        else:
            resolved_path = path

        return resolved_path.resolve()

    @staticmethod
    def validate_file_exists(path: Optional[Path], file_type: str) -> None:
        """Validate that a file exists at the given path."""
        if path and not path.exists():
            raise ValueError(f"{file_type} file not found: {path}")

    @staticmethod
    def validate_ssl_files(settings: BaseLRESettings) -> None:
        """Validate CA certificate file path."""
        if settings.lre_ca_cert_path:
            PathResolver.validate_file_exists(settings.lre_ca_cert_path, "CA certificate")