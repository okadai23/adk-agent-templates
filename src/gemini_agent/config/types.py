"""Shared typed configuration value aliases."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

type ConfigScalar = str | int | float | bool | None
type ConfigValue = ConfigScalar | list[ConfigValue] | dict[str, ConfigValue]
type ConfigMap = dict[str, ConfigValue]
type ReadonlyConfigMap = Mapping[str, ConfigValue]
type ReadonlyConfigSeq = Sequence[ConfigValue]
type ConfigList = list[ConfigValue]
