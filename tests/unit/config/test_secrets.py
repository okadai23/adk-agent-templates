"""Unit tests for SecretResolver."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from gemini_agent.config.secrets import SecretResolutionError, SecretResolver

if TYPE_CHECKING:
    from gemini_agent.config.types import ConfigMap


def test_resolve_env_and_secret_placeholders() -> None:
    """Resolver should substitute ENV and SECRET placeholders."""
    resolver = SecretResolver(
        env_provider={
            "GOOGLE_CLOUD_PROJECT": "project-local",
            "API_TOKEN": "token-value",
        },
    )

    value: ConfigMap = {
        "project": "${ENV:GOOGLE_CLOUD_PROJECT}",
        "auth": {"credential": "Bearer ${SECRET:API_TOKEN}"},
    }

    resolved = resolver.resolve(value)
    assert isinstance(resolved, dict)
    auth = resolved["auth"]
    assert isinstance(auth, dict)

    assert resolved["project"] == "project-local"
    assert auth["credential"] == "Bearer token-value"


def test_missing_secret_does_not_leak_secret_value() -> None:
    """Missing secrets should fail without exposing secret values."""
    resolver = SecretResolver(env_provider={})

    with pytest.raises(SecretResolutionError, match="MISSING_KEY") as exc_info:
        resolver.resolve("${SECRET:MISSING_KEY}")

    assert "secret-token" not in str(exc_info.value)


def test_empty_env_provider_does_not_fallback_to_os_environ(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Explicit empty provider should not read process environment values."""
    monkeypatch.setenv("API_TOKEN", "present-in-process-env")
    resolver = SecretResolver(env_provider={})

    with pytest.raises(SecretResolutionError, match="API_TOKEN"):
        resolver.resolve("${SECRET:API_TOKEN}")


def test_unresolved_placeholder_is_detected() -> None:
    """Any unresolved placeholder syntax should trigger validation error."""
    resolver = SecretResolver(env_provider={"KNOWN": "value"})

    with pytest.raises(SecretResolutionError, match="Unresolved placeholder"):
        resolver.resolve("prefix-${UNKNOWN:KNOWN}")
