"""Factory that builds executable agent definitions from AgentConfig."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from gemini_agent.config.agent_catalog import AgentConfig


@dataclass(slots=True)
class BuiltAgent:
    """Runner-consumable built agent representation."""

    agent_id: str
    name: str
    agent_type: str
    instruction: str
    model_profile: str
    tool_names: list[str]
    sub_agents: list[str]


class AgentFactory:
    """Build ADK-ready agent specs from typed configuration."""

    def __init__(self, *, config_root: Path) -> None:
        """Initialize with a root path for relative instruction files."""
        self._config_root = config_root

    def create(self, config: AgentConfig) -> BuiltAgent:
        """Create one built agent from configuration."""
        instruction = self._read_instruction(config)
        return BuiltAgent(
            agent_id=config.agent.id,
            name=config.agent.name,
            agent_type=config.agent.type,
            instruction=instruction,
            model_profile=config.model.profile,
            tool_names=list(config.tools.allowed),
            sub_agents=list(config.sub_agents),
        )

    def _read_instruction(self, config: AgentConfig) -> str:
        if config.agent.instruction_file is None:
            return ""
        return (self._config_root / config.agent.instruction_file).read_text(
            encoding="utf-8",
        )
