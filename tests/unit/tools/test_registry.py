"""Unit tests for tool registry."""

import pytest

from gemini_agent.tools import ToolRegistry, ToolRegistryError


def _echo_tool(value: str) -> str:
    return value


def test_registry_register_get_and_list() -> None:
    """Registered tools can be listed and instantiated."""
    registry = ToolRegistry()
    registry.register("echo", lambda: _echo_tool)

    tool = registry.get("echo")

    assert registry.has_tool("echo")
    assert registry.list_tool_ids() == ["echo"]
    assert tool("hello") == "hello"


def test_registry_rejects_duplicate_registration() -> None:
    """Duplicate tool id should raise an error."""
    registry = ToolRegistry()
    registry.register("echo", lambda: _echo_tool)

    with pytest.raises(ToolRegistryError, match="already registered"):
        registry.register("echo", lambda: _echo_tool)


def test_registry_rejects_unknown_tool() -> None:
    """Unknown tool id should raise an error."""
    registry = ToolRegistry()

    with pytest.raises(ToolRegistryError, match="Unknown tool"):
        registry.get("missing")
