"""Unit tests for filesystem skill factory."""

from pathlib import Path

import pytest

from gemini_agent.skills import FilesystemSkillFactory, SkillFactoryError


def test_skill_factory_loads_skill_file(tmp_path: Path) -> None:
    """Factory should load skill prompt from file."""
    skill_file = tmp_path / "router.md"
    skill_file.write_text("route requests", encoding="utf-8")

    spec = FilesystemSkillFactory(tmp_path).create("router")

    assert spec.skill_id == "router"
    assert spec.path == skill_file
    assert spec.prompt == "route requests"


def test_skill_factory_rejects_missing_file(tmp_path: Path) -> None:
    """Missing skill file should raise an error."""
    with pytest.raises(SkillFactoryError, match="not found"):
        FilesystemSkillFactory(tmp_path).create("missing")


def test_skill_factory_rejects_empty_prompt(tmp_path: Path) -> None:
    """Empty skill file should raise an error."""
    (tmp_path / "empty.md").write_text("\n", encoding="utf-8")

    with pytest.raises(SkillFactoryError, match="empty"):
        FilesystemSkillFactory(tmp_path).create("empty")
