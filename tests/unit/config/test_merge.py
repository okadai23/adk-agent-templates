"""Unit tests for ConfigMerger."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from gemini_agent.config.merge import ConfigMergeError, ConfigMerger

if TYPE_CHECKING:
    from gemini_agent.config.types import ConfigMap, ConfigValue


def test_deep_merge_with_scalar_override() -> None:
    """Nested dict values should be merged while scalar is overwritten."""
    merger = ConfigMerger()
    parent: ConfigMap = {
        "model": {
            "name": "gemini-2.5",
            "temperature": 0.2,
            "safety": {"level": "high"},
        },
        "timeout": 30,
    }
    child: ConfigMap = {"model": {"temperature": 0.7}, "timeout": 45}

    merged = merger.merge(parent, child)
    assert isinstance(merged, dict)

    assert merged == {
        "model": {
            "name": "gemini-2.5",
            "temperature": 0.7,
            "safety": {"level": "high"},
        },
        "timeout": 45,
    }


def test_list_replace_by_default() -> None:
    """List override should replace parent list when given plain list."""
    merger = ConfigMerger()

    merged = merger.merge({"tools": ["search", "rag"]}, {"tools": ["calc"]})
    assert isinstance(merged, dict)

    assert merged["tools"] == ["calc"]


def test_list_append_and_remove() -> None:
    """List directives should append and remove items."""
    merger = ConfigMerger()
    parent: ConfigMap = {"tools": ["search", "rag", "calc"]}
    child: ConfigMap = {"tools": {"$append": ["planner", "calc"], "$remove": ["rag"]}}

    merged = merger.merge(parent, child)
    assert isinstance(merged, dict)

    assert merged["tools"] == ["search", "calc", "planner", "calc"]


def test_null_removes_parent_value() -> None:
    """Null value in override should remove key inherited from parent."""
    merger = ConfigMerger()

    merged = merger.merge(
        {"auth": {"api_key": "secret", "mode": "api_key"}},
        {"auth": {"api_key": None}},
    )

    assert merged == {"auth": {"mode": "api_key"}}


def test_unknown_list_operator_raises_error() -> None:
    """Unknown list operators should raise validation error."""
    merger = ConfigMerger()

    with pytest.raises(ConfigMergeError, match="Unknown list operator"):
        merger.merge({"tools": ["search"]}, {"tools": {"$prepend": ["calc"]}})


def test_list_operator_requires_list_operand() -> None:
    """List operators must reject non-list operand values."""
    merger = ConfigMerger()
    invalid_cases: list[tuple[str, ConfigValue]] = [
        ("$append", {"x": 1}),
        ("$remove", "rag"),
    ]

    for operator, invalid_value in invalid_cases:
        with pytest.raises(ConfigMergeError, match="expects a list value"):
            merger.merge({"tools": ["search"]}, {"tools": {operator: invalid_value}})
