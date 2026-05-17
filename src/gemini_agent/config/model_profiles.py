"""Model profile schema and resolver."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

from .merge import ConfigMerger

if TYPE_CHECKING:
    from collections.abc import Mapping


class ModelProfileError(RuntimeError):
    """Raised when model profile resolution fails."""


class ModelProfile(BaseModel):
    """One model profile definition."""

    extends: str | None = None
    model: str
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_output_tokens: int | None = Field(default=None, ge=1)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    top_k: int | None = Field(default=None, ge=1)
    safety_settings: dict[str, Any] | None = None

    model_config = ConfigDict(extra="allow")


class ProfileResolver:
    """Resolve profiles including inheritance."""

    def __init__(self, profiles: Mapping[str, Mapping[str, Any]]) -> None:
        """Initialize resolver with raw model profile mapping."""
        self._profiles = {name: dict(raw) for name, raw in profiles.items()}
        self._merger = ConfigMerger()

    def resolve(self, profile_name: str) -> ModelProfile:
        """Resolve one profile into final expanded profile."""
        resolved = self._resolve_raw(profile_name, stack=[])
        return ModelProfile.model_validate(resolved)

    def _resolve_raw(self, profile_name: str, stack: list[str]) -> dict[str, Any]:
        if profile_name not in self._profiles:
            msg = f"Unknown model profile: {profile_name}"
            raise ModelProfileError(msg)
        if profile_name in stack:
            cycle = " -> ".join([*stack, profile_name])
            msg = f"Cycle detected in model profile inheritance: {cycle}"
            raise ModelProfileError(msg)

        current = self._profiles[profile_name]
        parent_name = current.get("extends")
        if not isinstance(parent_name, str):
            return current

        parent_raw = self._resolve_raw(parent_name, stack=[*stack, profile_name])
        child_raw = {k: v for k, v in current.items() if k != "extends"}
        merged = self._merger.merge(parent_raw, child_raw)
        if not isinstance(merged, dict):
            msg = f"Invalid merged model profile payload for '{profile_name}'."
            raise ModelProfileError(msg)
        return merged
