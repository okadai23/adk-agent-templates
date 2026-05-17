"""Unit tests for auth/security components."""

import pytest
from typing import Any
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException

from gemini_agent.api.main import create_app
from gemini_agent.security import Authenticator, AuthorizationPolicy, Principal
from gemini_agent.settings import Settings, get_settings


def test_api_key_authenticator_accepts_valid_key() -> None:
    """API key mode accepts matching key."""
    settings = Settings(auth_mode="api_key", api_key="secret")
    principal = Authenticator(settings).authenticate(None, "secret")
    assert principal.subject == "api-key-client"


def test_api_key_authenticator_rejects_invalid_key() -> None:
    """API key mode rejects non-matching key."""
    settings = Settings(auth_mode="api_key", api_key="secret")
    with pytest.raises(HTTPException) as exc_info:
        Authenticator(settings).authenticate(None, "wrong")
    assert exc_info.value.status_code == 401


def test_jwt_authenticator_requires_bearer_header() -> None:
    """JWT mode requires Authorization Bearer header."""
    settings = Settings(auth_mode="jwt")
    with pytest.raises(HTTPException) as exc_info:
        Authenticator(settings).authenticate(None, None)
    assert exc_info.value.status_code == 401


def test_authorization_policy_forbidden_when_role_not_allowed() -> None:
    """Authorization policy raises 403 when role is not allowed."""
    policy = AuthorizationPolicy()
    principal = Principal(subject="u1", roles=("user",))
    with pytest.raises(HTTPException) as exc_info:
        policy.authorize(principal, ["admin"])
    assert exc_info.value.status_code == 403


def test_api_routes_require_api_key_when_mode_enabled(monkeypatch: Any) -> None:
    """Protected endpoints require x-api-key in api_key mode."""
    monkeypatch.setenv("AGENT_AUTH_MODE", "api_key")
    monkeypatch.setenv("AGENT_API_KEY", "secret")

    get_settings.cache_clear()
    client = TestClient(create_app())
    unauthorized = client.post("/run", json={"agent_id": "a1", "input": "hello"})
    assert unauthorized.status_code == 401

    authorized = client.post(
        "/run",
        json={"agent_id": "a1", "input": "hello"},
        headers={"x-api-key": "secret"},
    )
    assert authorized.status_code == 200
    get_settings.cache_clear()
