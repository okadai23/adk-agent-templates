"""Unit tests for ConfigLoader."""

from pathlib import Path

import pytest

from gemini_agent.config.loader import ConfigLoadError, ConfigLoader


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
    loaded = loader.load_all(environment="local")

    assert loaded["model_profiles"]["default"]["model"] == "gemini-2.5"
    assert loaded["knowledge_sources"]["sources"] == []
    assert loaded["agent_catalog"]["agents"] == ["assistant"]
    assert loaded["agents"]["assistant"]["name"] == "assistant"
    assert loaded["environment"]["debug"] is True


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
