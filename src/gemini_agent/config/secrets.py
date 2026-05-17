"""Placeholder resolution for environment and secret values in config data."""

import os
import re

from .types import ConfigValue

_PATTERN = re.compile(r"\$\{(ENV|SECRET):([A-Za-z_][A-Za-z0-9_]*)\}")


class SecretResolutionError(ValueError):
    """Raised when a placeholder cannot be resolved safely."""


class SecretResolver:
    """Resolve `${ENV:KEY}` and `${SECRET:KEY}` placeholders recursively."""

    def __init__(self, env_provider: dict[str, str] | None = None) -> None:
        """Initialize resolver with optional env provider."""
        self._env_provider = dict(os.environ) if env_provider is None else env_provider

    def resolve(self, value: ConfigValue) -> ConfigValue:
        """Resolve placeholders inside nested structures."""
        if isinstance(value, dict):
            return {key: self.resolve(nested) for key, nested in value.items()}
        if isinstance(value, list):
            return [self.resolve(item) for item in value]
        if isinstance(value, str):
            return self._resolve_text(value)
        return value

    def _resolve_text(self, text: str) -> str:
        def replacer(match: re.Match[str]) -> str:
            placeholder_type, key = match.group(1), match.group(2)
            return self._resolve_key(placeholder_type=placeholder_type, key=key)

        resolved_text = _PATTERN.sub(replacer, text)
        if "${" in resolved_text:
            msg = "Unresolved placeholder detected in config value."
            raise SecretResolutionError(msg)
        return resolved_text

    def _resolve_key(self, *, placeholder_type: str, key: str) -> str:
        value = self._env_provider.get(key)
        if value is None:
            msg = f"Missing {placeholder_type} value for key '{key}'."
            raise SecretResolutionError(msg)
        return value
