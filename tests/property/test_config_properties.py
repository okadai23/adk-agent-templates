"""Property-like checks for config merge invariants."""

from gemini_agent.config.merge import ConfigMerger
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from gemini_agent.config.types import ConfigMap


def test_merge_is_idempotent_for_same_overlay() -> None:
    """Applying same overlay repeatedly should keep deterministic result."""
    merger = ConfigMerger()
    base = cast("ConfigMap", {"a": {"b": 1}, "tags": ["x"]})
    overlay = cast("ConfigMap", {"a": {"c": 2}, "tags": {"$append": ["y"]}})

    once = merger.merge(base, overlay)
    twice = merger.merge(base, overlay)

    assert once == twice
