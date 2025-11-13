import ssl
from pathlib import Path
from typing import Optional, ClassVar
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support using Pydantic v2."""

    project_root: ClassVar[Path] = Path(__file__).resolve().parents[2]
    env_file_path: ClassVar[Path] = project_root / "resources/.env"

    model_config = SettingsConfigDict(
        env_file=str(env_file_path),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # LRE Connection Settings
    lre_server: str = Field("https://lre.example.com", description="LRE server base URL")
    lre_client_id: str = Field("", description="LRE username")
    lre_client_secret: str = Field("", description="LRE password", repr=False)
    lre_domain: str = Field("", description="LRE domain")
    lre_project: str = Field("", description="LRE project name")
    lre_run_id: int = Field(0, description="LRE Run ID")

    # SSL/TLS Settings
    lre_ca_cert_path: Optional[Path] = Field(None, description="Path to custom CA certificate")
    lre_client_cert_path: Optional[Path] = Field(None, description="Path to client certificate")
    lre_client_key_path: Optional[Path] = Field(None, description="Path to client private key")
    lre_verify_ssl: bool = Field(True, description="Verify SSL certificates")

    # API Settings
    lre_timeout: int = Field(30, ge=1, le=300, description="Request timeout in seconds")
    lre_max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts")
    lre_retry_backoff: float = Field(1.0, ge=0.1, le=10.0, description="Retry backoff factor")

    # HTTP Settings
    lre_user_agent: str = Field("LRE-Python-Client/1.0.0", description="HTTP User-Agent header")

    @model_validator(mode='after')
    def validate_ssl_settings(self) -> 'Settings':
        """Validate and normalize SSL-related settings."""

        def resolve_path(p: Optional[Path]) -> Optional[Path]:
            if not p:
                return None
            if not p.is_absolute():
                p = self.project_root / p
            return p

        # Normalize paths
        self.lre_ca_cert_path = resolve_path(self.lre_ca_cert_path)
        self.lre_client_cert_path = resolve_path(self.lre_client_cert_path)
        self.lre_client_key_path = resolve_path(self.lre_client_key_path)

        # Validate file existence
        if self.lre_client_cert_path and not self.lre_client_key_path:
            raise ValueError("Client key path must be provided when client certificate is specified")

        if self.lre_client_key_path and not self.lre_client_cert_path:
            raise ValueError("Client certificate path must be provided when client key is specified")

        if self.lre_ca_cert_path and not self.lre_ca_cert_path.exists():
            raise ValueError(f"CA certificate file not found: {self.lre_ca_cert_path}")

        if self.lre_client_cert_path and not self.lre_client_cert_path.exists():
            raise ValueError(f"Client certificate file not found: {self.lre_client_cert_path}")

        if self.lre_client_key_path and not self.lre_client_key_path.exists():
            raise ValueError(f"Client key file not found: {self.lre_client_key_path}")

        return self

    @property
    def base_url(self) -> str:
        """Get normalized base URL."""
        return self.lre_server.rstrip('/')

    @property
    def auth_credentials(self) -> str:
        """Get formatted authentication credentials."""
        return f"{self.lre_domain}\\{self.lre_username}:{self.lre_password}"


def create_ssl_context(settings: Settings) -> Optional[ssl.SSLContext]:
    """
    Create SSL context with custom CA certificates if provided.

    Args:
        settings: Application settings

    Returns:
        Configured SSLContext or None if SSL verification is disabled
    """
    if not settings.lre_verify_ssl:
        return None

    ssl_context = ssl.create_default_context()

    # Load custom CA certificate if provided
    if settings.lre_ca_cert_path:
        ssl_context.load_verify_locations(cafile=str(settings.lre_ca_cert_path))

    # Load client certificate and key if provided
    if settings.lre_client_cert_path and settings.lre_client_key_path:
        ssl_context.load_cert_chain(
            certfile=str(settings.lre_client_cert_path),
            keyfile=str(settings.lre_client_key_path)
        )

    return ssl_context


# Global settings instance
_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get settings instance (singleton pattern).
    Returns:
        Settings instance
    """

    global _settings_instance
    if _settings_instance is None:
        # noinspection PyArgumentList
        _settings_instance = Settings()
    return _settings_instance
