"""Authentication and authorization helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from starlette.exceptions import HTTPException

if TYPE_CHECKING:
    from gemini_agent.settings import Settings


@dataclass(frozen=True)
class Principal:
    """Authenticated principal."""

    subject: str
    roles: tuple[str, ...] = ()


class JwtVerifier:
    """JWT verifier skeleton."""

    def verify(self, token: str) -> Principal:
        """Verify JWT token and return principal."""
        if not token.strip():
            raise HTTPException(status_code=401, detail="invalid jwt token")
        return Principal(subject="jwt-user", roles=("user",))


class AuthorizationPolicy:
    """Simple role-based authorization policy."""

    def authorize(self, principal: Principal, allowed_roles: list[str] | None) -> None:
        """Authorize principal against allowed roles."""
        if not allowed_roles:
            return
        if any(role in principal.roles for role in allowed_roles):
            return
        raise HTTPException(status_code=403, detail="forbidden")


class Authenticator:
    """Resolve request principal based on configured auth mode."""

    def __init__(
        self,
        settings: Settings,
        *,
        jwt_verifier: JwtVerifier | None = None,
    ) -> None:
        """Initialize authenticator with settings and optional JWT verifier."""
        self._settings = settings
        self._jwt_verifier = jwt_verifier or JwtVerifier()

    def authenticate(
        self, authorization: str | None, x_api_key: str | None,
    ) -> Principal:
        """Authenticate incoming request using api key or jwt mode."""
        auth_mode = self._settings.auth_mode
        if auth_mode == "none":
            return Principal(subject="anonymous")
        if auth_mode == "api_key":
            expected = self._settings.api_key
            if not expected:
                raise HTTPException(
                    status_code=500, detail="api key auth is not configured",
                )
            if x_api_key != expected:
                raise HTTPException(status_code=401, detail="invalid api key")
            return Principal(subject="api-key-client")
        if auth_mode == "jwt":
            if authorization is None or not authorization.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="missing bearer token")
            return self._jwt_verifier.verify(authorization.removeprefix("Bearer "))
        raise HTTPException(
            status_code=500, detail=f"unsupported auth mode: {auth_mode}",
        )
