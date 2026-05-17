"""Filesystem-based skill factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class SkillFactoryError(ValueError):
    """Raised when skill metadata cannot be loaded."""


@dataclass(frozen=True)
class SkillSpec:
    """Resolved skill metadata loaded from the filesystem."""

    skill_id: str
    path: Path
    prompt: str


class FilesystemSkillFactory:
    """Load skill prompts from `<root>/<skill_id>.md` files."""

    def __init__(self, skills_root: Path) -> None:
        """Initialize with a skills root directory."""
        self._skills_root = skills_root

    def create(self, skill_id: str) -> SkillSpec:
        """Load a skill definition from filesystem."""
        skill_path = self._skills_root / f"{skill_id}.md"
        if not skill_path.exists():
            msg = f"Skill file not found: {skill_path}"
            raise SkillFactoryError(msg)

        prompt = skill_path.read_text(encoding="utf-8").strip()
        if not prompt:
            msg = f"Skill prompt is empty: {skill_path}"
            raise SkillFactoryError(msg)

        return SkillSpec(skill_id=skill_id, path=skill_path, prompt=prompt)
