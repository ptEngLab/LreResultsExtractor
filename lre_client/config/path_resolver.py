from pathlib import Path
from typing import Optional
from .settings import BaseLRESettings


class PathResolver:
    """Utility class for resolving and validating filesystem paths."""

    @staticmethod
    def resolve_config_path(project_root: Path, path: Optional[Path]) -> Optional[Path]:
        """
        Resolve a file path relative to the project root if it's not absolute.
        """
        if not path:
            return None

        resolved = path if path.is_absolute() else project_root / path
        return resolved.resolve()

    @staticmethod
    def validate_file_exists(path: Optional[Path], file_type: str) -> None:
        """
        Ensure a file exists at the given path.
        """
        if path and not path.exists():
            raise ValueError(f"{file_type} file not found: {path}")

    @staticmethod
    def validate_ssl_files(settings: BaseLRESettings) -> None:
        """Validate CA certificate path if provided."""
        PathResolver.validate_file_exists(settings.lre_ca_cert_path, "CA certificate")
