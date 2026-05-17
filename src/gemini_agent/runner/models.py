# pyright: reportUnknownVariableType=none
"""Domain models for agent running and event transport."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RunRequest:
    """Input payload for one agent execution."""

    agent_id: str
    input_text: str
    session_id: str | None = None
    user_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class RunResult:
    """Final execution result for sync operation."""

    run_id: str
    output_text: str
    status: str = "completed"


@dataclass(slots=True)
class AgentEvent:
    """Normalized domain event emitted by runners."""

    event_type: str
    run_id: str
    agent_id: str
    payload: dict[str, str] = field(default_factory=dict)
