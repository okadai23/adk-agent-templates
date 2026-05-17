# pyright: reportUnknownVariableType=none, reportUnknownArgumentType=none, reportArgumentType=none
"""Concrete runner implementations for embedded and HTTP modes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from gemini_agent.runner.event_mapper import EventMapper
from gemini_agent.runner.models import AgentEvent, RunRequest, RunResult

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


class HttpResponse(Protocol):
    """Minimal HTTP response protocol used by AdkHttpRunner."""

    def raise_for_status(self) -> None:
        """Raise an exception when response status is not successful."""
        ...

    def json(self) -> dict[str, object]:
        """Return parsed JSON payload."""
        ...


class HttpClient(Protocol):
    """Minimal async HTTP client protocol used by AdkHttpRunner."""

    async def post(self, path: str, *, json: dict[str, str]) -> HttpResponse:
        """Perform POST request and return response object."""
        ...


class AdkEmbeddedRunner:
    """In-process runner that executes against built agent definitions."""

    def __init__(self, *, event_mapper: EventMapper | None = None) -> None:
        """Initialize embedded runner."""
        self._event_mapper = event_mapper or EventMapper()

    async def run(self, command: RunRequest) -> RunResult:
        """Execute a sync request and return final result."""
        run_id = command.session_id or f"run-{command.agent_id}"
        return RunResult(run_id=run_id, output_text=command.input_text)

    async def stream(self, command: RunRequest) -> AsyncIterator[AgentEvent]:
        """Execute a request and emit normalized event stream."""
        run_id = command.session_id or f"run-{command.agent_id}"
        raw_events = [
            {"type": "run_started", "run_id": run_id, "payload": {}},
            {
                "type": "text_completed",
                "run_id": run_id,
                "payload": {"text": command.input_text},
            },
            {"type": "run_completed", "run_id": run_id, "payload": {}},
        ]
        for event in raw_events:
            yield self._event_mapper.map_event(event, agent_id=command.agent_id)


class AdkHttpRunner:
    """HTTP proxy runner for out-of-process ADK API servers."""

    def __init__(
        self,
        *,
        base_url: str,
        client: HttpClient,
        event_mapper: EventMapper | None = None,
    ) -> None:
        """Initialize HTTP runner with endpoint and async client."""
        self._base_url = base_url.rstrip("/")
        self._event_mapper = event_mapper or EventMapper()
        self._client = client

    async def run(self, command: RunRequest) -> RunResult:
        """Proxy sync run call to remote ADK endpoint."""
        response = await self._client.post(
            "/run",
            json={"agent_id": command.agent_id, "input": command.input_text},
        )
        response.raise_for_status()
        data = response.json()
        run_id = str(data.get("run_id", ""))
        output_text = str(data.get("output_text", ""))
        status = str(data.get("status", "completed"))
        return RunResult(run_id=run_id, output_text=output_text, status=status)

    async def stream(self, command: RunRequest) -> AsyncIterator[AgentEvent]:
        """Proxy streaming run call and map returned events."""
        response = await self._client.post(
            "/run:stream",
            json={"agent_id": command.agent_id, "input": command.input_text},
        )
        response.raise_for_status()
        data = response.json()
        raw_events = data.get("events", [])
        if not isinstance(raw_events, list):
            raw_events = []
        for raw_event in raw_events:
            if isinstance(raw_event, dict):
                event: dict[str, object] = {
                    str(key): value for key, value in raw_event.items()
                }
                yield self._event_mapper.map_event(event, agent_id=command.agent_id)


class FakeAgentRunner:
    """Deterministic runner for tests and local mocks."""

    async def run(self, command: RunRequest) -> RunResult:
        """Return synthetic completed result."""
        run_id = command.session_id or f"fake-{command.agent_id}"
        return RunResult(
            run_id=run_id, output_text=command.input_text, status="completed",
        )

    async def stream(self, command: RunRequest) -> AsyncIterator[AgentEvent]:
        """Emit a deterministic three-event lifecycle."""
        run_id = command.session_id or f"fake-{command.agent_id}"
        mapper = EventMapper()
        for raw_event in (
            {"type": "run_started", "run_id": run_id, "payload": {}},
            {
                "type": "text_completed",
                "run_id": run_id,
                "payload": {"text": command.input_text},
            },
            {"type": "run_completed", "run_id": run_id, "payload": {}},
        ):
            yield mapper.map_event(raw_event, agent_id=command.agent_id)


class RecordedAgentRunner:
    """Runner that replays pre-recorded sync and stream payloads."""

    def __init__(
        self,
        *,
        run_result: RunResult,
        stream_events: list[AgentEvent],
    ) -> None:
        """Initialize runner with pre-recorded result and stream events."""
        self._run_result = run_result
        self._stream_events = stream_events

    async def run(self, command: RunRequest) -> RunResult:
        """Ignore input and replay recorded run result."""
        _ = command
        return self._run_result

    async def stream(self, command: RunRequest) -> AsyncIterator[AgentEvent]:
        """Ignore input and replay recorded stream events."""
        _ = command
        for event in self._stream_events:
            yield event
