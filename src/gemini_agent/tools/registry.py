"""Tool registry for callable tool factories."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

ToolCallable = Callable[..., Any]
ToolFactory = Callable[[], ToolCallable]


class ToolRegistryError(ValueError):
    """Base error type for tool registry operations."""


class ToolRegistry:
    """Register and instantiate tools by id."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self._factories: dict[str, ToolFactory] = {}

    def register(self, tool_id: str, factory: ToolFactory) -> None:
        """Register a tool factory.

        Args:
            tool_id: Unique tool identifier.
            factory: No-arg factory that returns the executable callable.

        """
        if tool_id in self._factories:
            msg = f"Tool already registered: {tool_id}"
            raise ToolRegistryError(msg)
        self._factories[tool_id] = factory

    def has_tool(self, tool_id: str) -> bool:
        """Return True when a tool id is registered."""
        return tool_id in self._factories

    def get(self, tool_id: str) -> ToolCallable:
        """Instantiate and return a registered tool callable."""
        factory = self._factories.get(tool_id)
        if factory is None:
            msg = f"Unknown tool: {tool_id}"
            raise ToolRegistryError(msg)
        return factory()

    def list_tool_ids(self) -> list[str]:
        """Return sorted registered tool ids."""
        return sorted(self._factories)
