"""Runner protocol definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from gemini_agent.runner.models import AgentEvent, RunRequest, RunResult


class AgentRunner(Protocol):
    """Abstract execution interface for one agent runtime backend."""

    async def run(self, command: RunRequest) -> RunResult:
        """Execute one command and return the final result."""
        raise NotImplementedError

    async def stream(self, command: RunRequest) -> AsyncIterator[AgentEvent]:
        """Execute one command and emit normalized streaming events."""
        raise NotImplementedError
