"""Centralized configuration for AeroSense."""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="AEROSENSE_", extra="ignore")

    # Application Identity
    app_name: str = Field(
        default="AeroSense — Urban Air Quality & Smog Assistant",
        description="User-facing title of the application",
    )
    environment: str = Field(
        default="development",
        description="Deployment stage: development, staging, or production",
    )
    version: str = Field(
        default="1.0.0",
        description="Semantic application version",
    )

    # Persistence & Enterprise Connection Pooling
    database_url: str = Field(
        default="sqlite:///./aerosense.db",
        description="Database connection URL (PostgreSQL in production, SQLite in local dev)",
    )
    db_pool_size: int = Field(
        default=10,
        description="Base connection pool size for enterprise relational databases",
    )
    db_max_overflow: int = Field(
        default=20,
        description="Maximum temporary connections above pool_size during peak loads",
    )
    db_pool_recycle: int = Field(
        default=3600,
        description="Connection recycling interval in seconds to prevent stale pool drops",
    )

    # Security, Cryptography & Privacy
    secret_key: str = Field(
        default="dev-only-insecure-secret-change-me-32b",
        description="Cryptographic secret key for signing anonymous JWT tokens and deriving Fernet keys",
    )
    token_expire_minutes: int = Field(
        default=120,
        description="Validity lifetime in minutes for anonymous JWT session tokens",
    )
    encryption_key: str = Field(
        default="",
        description="Fernet symmetric key for encrypting user sensitive profiles at rest",
    )
    allowed_origins: list[str] = Field(
        default=["*"],
        description="CORS allowed origins for API consumers",
    )

    # In-Memory Rate Limiting
    rate_limit_requests: int = Field(
        default=60,
        description="Maximum allowed requests per client IP within the sliding rate limit window",
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        description="Sliding rate limiter duration in seconds",
    )

    # Pluggable GenAI Provider Selection (Google Gemini or Deterministic Mock)
    llm_provider: str = Field(
        default="mock",
        description="Active LLM provider interface: 'gemini' for Google Gemini API, 'mock' for offline evaluation",
    )
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key for live inference",
    )
    gemini_model: str = Field(
        default="gemini-2.5-flash",
        description="Gemini generative model ID",
    )


@lru_cache
def get_settings() -> Settings:
    """Provide a cached singleton instance of application settings."""
    return Settings()
