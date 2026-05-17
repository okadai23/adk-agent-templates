"""Runner registry with per-agent lazy initialization."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from gemini_agent.runner.ports import AgentRunner


class RunnerRegistryError(RuntimeError):
    """Raised when runner mode is unknown or unsupported."""


class RunnerRegistry:
    """Lazily construct and cache runners by agent id and mode."""

    def __init__(
        self,
        *,
        mode: str,
        factories: dict[str, Callable[[str], AgentRunner]],
    ) -> None:
        """Store runner mode and factory map."""
        self._mode = mode
        self._factories = factories
        self._runners: dict[str, AgentRunner] = {}

    def get(self, agent_id: str) -> AgentRunner:
        """Get or lazily build a runner for the specified agent."""
        if agent_id in self._runners:
            return self._runners[agent_id]
        factory = self._factories.get(self._mode)
        if factory is None:
            msg = f"Unsupported runner mode: {self._mode}"
            raise RunnerRegistryError(msg)
        runner = factory(agent_id)
        self._runners[agent_id] = runner
        return runner
