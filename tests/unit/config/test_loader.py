"""Unit tests for ConfigLoader."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from gemini_agent.config.loader import ConfigLoadError, ConfigLoader

if TYPE_CHECKING:
    from pathlib import Path
    from gemini_agent.config.types import ConfigMap


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_load_all_local_environment(tmp_path: Path) -> None:
    """Loader should read all required YAML files."""
    _write(tmp_path / "model_profiles.yaml", "default: {model: gemini-2.5}\n")
    _write(tmp_path / "knowledge_sources.yaml", "sources: []\n")
    _write(tmp_path / "agent_catalog.yaml", "agents: [assistant]\n")
    _write(tmp_path / "agents" / "assistant.yaml", "name: assistant\n")
    _write(tmp_path / "environments" / "local.yaml", "debug: true\n")

    loader = ConfigLoader(tmp_path)
    loaded: ConfigMap = loader.load_all(environment="local")

    model_profiles = loaded["model_profiles"]
    knowledge_sources = loaded["knowledge_sources"]
    agent_catalog = loaded["agent_catalog"]
    agents = loaded["agents"]
    environment = loaded["environment"]
    assert isinstance(model_profiles, dict)
    assert isinstance(knowledge_sources, dict)
    assert isinstance(agent_catalog, dict)
    assert isinstance(agents, dict)
    assert isinstance(environment, dict)

    default_profile = model_profiles["default"]
    assistant_cfg = agents["assistant"]
    assert isinstance(default_profile, dict)
    assert isinstance(assistant_cfg, dict)

    assert default_profile["model"] == "gemini-2.5"
    assert knowledge_sources["sources"] == []
    assert agent_catalog["agents"] == ["assistant"]
    assert assistant_cfg["name"] == "assistant"
    assert environment["debug"] is True


def test_missing_yaml_contains_file_path(tmp_path: Path) -> None:
    """Missing config files should raise error with path."""
    loader = ConfigLoader(tmp_path)

    with pytest.raises(ConfigLoadError, match=r"model_profiles\.yaml"):
        loader.load_model_profiles()


def test_parse_error_contains_target_file(tmp_path: Path) -> None:
    """Parse error should include broken filename."""
    broken = tmp_path / "knowledge_sources.yaml"
    _write(broken, "invalid: [\n")

    loader = ConfigLoader(tmp_path)

    with pytest.raises(ConfigLoadError, match=r"knowledge_sources\.yaml"):
        loader.load_knowledge_sources()
