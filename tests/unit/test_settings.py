"""Unit tests for settings."""

import pytest

from gemini_agent.settings import Settings, get_settings


def test_settings_reads_agent_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings should read values from AGENT_ prefixed environment variables."""
    monkeypatch.setenv("AGENT_ENVIRONMENT", "prod")
    monkeypatch.setenv("AGENT_AUTH_MODE", "api_key")
    monkeypatch.setenv("AGENT_RUNNER_MODE", "http")

    settings = Settings()

    assert settings.environment == "prod"
    assert settings.auth_mode == "api_key"
    assert settings.runner_mode == "http"


def test_settings_ignores_unknown_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings should ignore unknown AGENT_ environment variables."""
    monkeypatch.setenv("AGENT_UNKNOWN", "value")

    settings = Settings()

    assert settings.environment == "local"


def test_get_settings_is_cached() -> None:
    """get_settings should return a cached singleton instance."""
    get_settings.cache_clear()

    first = get_settings()
    second = get_settings()

    assert first is second
