"""Configuration merge utilities for layered config composition."""

from copy import deepcopy
from typing import ClassVar


class ConfigMergeError(ValueError):
    """Raised when an invalid merge directive is detected."""


class ConfigMerger:
    """Merge configuration values using framework-specific rules."""

    _LIST_DIRECTIVES: ClassVar[set[str]] = {"$append", "$remove"}

    def merge(self, base: object, override: object) -> object:
        """Merge `override` onto `base` recursively."""
        if override is None:
            return None

        if _is_str_object_dict(base) and _is_str_object_dict(override):
            return self._merge_dict(base, override)

        if _is_object_list(base):
            return self._merge_list(base, override)

        if _is_str_object_dict(override) and self._has_list_directive(override):
            msg = "List directives are only valid when overriding list values."
            raise ConfigMergeError(msg)

        return deepcopy(override)

    def _merge_dict(
        self,
        base: dict[str, object],
        override: dict[str, object],
    ) -> dict[str, object]:
        merged: dict[str, object] = deepcopy(base)

        for key, override_value in override.items():
            if override_value is None:
                merged.pop(key, None)
                continue

            if key in merged:
                merged[key] = self.merge(merged[key], override_value)
            else:
                merged[key] = deepcopy(override_value)

        return merged

    def _merge_list(self, base: list[object], override: object) -> object:
        if isinstance(override, list):
            return deepcopy(override)

        if isinstance(override, dict):
            unknown = set(override.keys()) - self._LIST_DIRECTIVES
            if unknown:
                msg = (
                    "Unknown list operator(s): "
                    + ", ".join(sorted(unknown))
                    + ". Allowed operators: $append, $remove."
                )
                raise ConfigMergeError(msg)

            append_values = override.get("$append", [])
            if not isinstance(append_values, list):
                msg = "List operator '$append' expects a list value."
                raise ConfigMergeError(msg)

            remove_values = override.get("$remove", [])
            if not isinstance(remove_values, list):
                msg = "List operator '$remove' expects a list value."
                raise ConfigMergeError(msg)

            merged: list[object] = deepcopy(base)
            merged.extend(deepcopy(append_values))
            return [item for item in merged if item not in remove_values]

        return deepcopy(override)

    def _has_list_directive(self, value: dict[str, object]) -> bool:
        return any(key in self._LIST_DIRECTIVES for key in value)


def _is_str_object_dict(value: object) -> bool:
    return isinstance(value, dict) and all(isinstance(key, str) for key in value)


def _is_object_list(value: object) -> bool:
    return isinstance(value, list)
