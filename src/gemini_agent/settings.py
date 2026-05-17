"""Application settings for Gemini ADK agent framework."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="AGENT_",
        extra="ignore",
    )

    environment: Literal["local", "staging", "prod"] = "local"
    auth_mode: Literal["none", "api_key", "jwt"] = "none"
    runner_mode: Literal["embedded", "http", "fake", "recorded"] = "embedded"
    config_root: Path = Path("configs")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()
