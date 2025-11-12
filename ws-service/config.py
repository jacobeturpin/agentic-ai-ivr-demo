"""Configuration management using pydantic-settings."""
import logging
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Configuration
    app_name: str = "Agentic AI IVR Demo"
    app_version: str = "0.1.0"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "text"] = "text"

    # Environment
    environment: Literal["development", "staging", "production"] = "development"

    @property
    def log_level_int(self) -> int:
        """Convert log level string to logging module constant."""
        return getattr(logging, self.log_level.upper())


# Create global settings instance
settings = Settings()
