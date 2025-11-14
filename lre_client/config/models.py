from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from .constants import ENV_FILE_PATH


class BaseLRESettings(BaseSettings):
    """Base settings model focusing only on configuration definition and validation."""
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # LRE Connection Settings
    lre_server: str = Field("https://lre.example.com", description="LRE server base URL")
    lre_client_id: str = Field(..., description="LRE client ID")
    lre_client_secret: str = Field(..., description="LRE client secret", repr=False)
    lre_domain: str = Field("", description="LRE domain")
    lre_project: str = Field(..., description="LRE project name")
    lre_run_id: int = Field(0, description="LRE Run ID")

    # SSL/TLS Settings (CA certificates only)
    lre_ca_cert_path: Optional[Path] = Field(None, description="Path to custom CA certificate")
    lre_verify_ssl: bool = Field(True, description="Verify SSL certificates")

    # API Settings
    lre_timeout: int = Field(30, ge=1, le=300, description="Request timeout in seconds")
    lre_max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts")
    lre_retry_backoff: float = Field(1.0, ge=0.1, le=10.0, description="Retry backoff factor")

    # HTTP Settings
    lre_user_agent: str = Field("LRE-Python-Client/1.0.0", description="HTTP User-Agent header")

    @property
    def base_url(self) -> str:
        """Get normalized base URL."""
        return self.lre_server.rstrip('/')
