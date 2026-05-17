"""Unit tests for model profile models and resolver."""

import pytest

from gemini_agent.config.model_profiles import ModelProfileError, ProfileResolver


def test_profile_resolver_applies_inheritance() -> None:
    """Child profiles should override parent fields via deep merge."""
    resolver = ProfileResolver(
        {
            "base": {
                "model": "gemini-2.5-pro",
                "temperature": 0.2,
                "safety_settings": {"harassment": "block_medium_and_above"},
            },
            "fast": {
                "extends": "base",
                "model": "gemini-2.5-flash",
                "max_output_tokens": 1024,
            },
        },
    )

    resolved = resolver.resolve("fast")

    assert resolved.model == "gemini-2.5-flash"
    assert resolved.temperature == 0.2
    assert resolved.max_output_tokens == 1024
    assert resolved.safety_settings == {"harassment": "block_medium_and_above"}


def test_profile_resolver_raises_for_unknown_profile() -> None:
    """Unknown profile names should raise explicit error."""
    resolver = ProfileResolver({"base": {"model": "gemini-2.5-pro"}})

    with pytest.raises(ModelProfileError, match="Unknown model profile"):
        resolver.resolve("missing")


def test_profile_resolver_detects_inheritance_cycle() -> None:
    """Cycle in profile inheritance should raise error."""
    resolver = ProfileResolver(
        {
            "a": {"extends": "b", "model": "gemini-2.5-pro"},
            "b": {"extends": "a", "model": "gemini-2.5-flash"},
        },
    )

    with pytest.raises(ModelProfileError, match="Cycle detected"):
        resolver.resolve("a")


def test_profile_model_validation_rejects_invalid_temperature() -> None:
    """Out-of-range temperature should fail pydantic validation."""
    resolver = ProfileResolver({"bad": {"model": "gemini-2.5-pro", "temperature": 3.0}})

    with pytest.raises(ValueError, match="temperature"):
        resolver.resolve("bad")
