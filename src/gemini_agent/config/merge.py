"""Configuration merge utilities for layered config composition."""

from copy import deepcopy
from typing import Any, ClassVar


class ConfigMergeError(ValueError):
    """Raised when an invalid merge directive is detected."""


class ConfigMerger:
    """Merge configuration values using framework-specific rules."""

    _LIST_DIRECTIVES: ClassVar[set[str]] = {"$append", "$remove"}

    def merge(self, base: Any, override: Any) -> Any:
        """Merge `override` onto `base` recursively."""
        if override is None:
            return None

        if isinstance(base, dict) and isinstance(override, dict):
            return self._merge_dict(base, override)

        if isinstance(base, list):
            return self._merge_list(base, override)

        if isinstance(override, dict) and self._has_list_directive(override):
            msg = "List directives are only valid when overriding list values."
            raise ConfigMergeError(msg)

        return deepcopy(override)

    def _merge_dict(
        self,
        base: dict[str, Any],
        override: dict[str, Any],
    ) -> dict[str, Any]:
        merged: dict[str, Any] = deepcopy(base)

        for key, override_value in override.items():
            if override_value is None:
                merged.pop(key, None)
                continue

            if key in merged:
                merged[key] = self.merge(merged[key], override_value)
            else:
                merged[key] = deepcopy(override_value)

        return merged

    def _merge_list(self, base: list[Any], override: Any) -> list[Any]:
        if isinstance(override, list):
            return deepcopy(override)

        if isinstance(override, dict):
            unknown = set(override) - self._LIST_DIRECTIVES
            if unknown:
                msg = (
                    "Unknown list operator(s): "
                    + ", ".join(sorted(unknown))
                    + ". Allowed operators: $append, $remove."
                )
                raise ConfigMergeError(msg)

            merged = deepcopy(base)
            merged.extend(deepcopy(override.get("$append", [])))
            remove_values = override.get("$remove", [])
            return [item for item in merged if item not in remove_values]

        return deepcopy(override)

    def _has_list_directive(self, value: dict[str, Any]) -> bool:
        return any(key in self._LIST_DIRECTIVES for key in value)
