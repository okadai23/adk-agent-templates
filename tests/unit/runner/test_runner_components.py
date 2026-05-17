# pyright: reportUnknownMemberType=none, reportUntypedFunctionDecorator=none, reportAttributeAccessIssue=none, reportArgumentType=none
"""Unit tests for runner components."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from pathlib import Path

from gemini_agent.config.agent_catalog import AgentConfig
from gemini_agent.runner import (
    AdkEmbeddedRunner,
    AdkHttpRunner,
    AgentFactory,
    EventMapper,
    RunRequest,
    RunResult,
    RunnerRegistry,
    RunnerRegistryError,
)


def _sample_agent_config(*, instruction_file: str | None = None) -> AgentConfig:
    return AgentConfig.model_validate(
        {
            "version": 1,
            "agent": {
                "id": "root",
                "name": "Root",
                "type": "llm",
                "instruction_file": instruction_file,
            },
            "model": {"profile": "default", "overrides": {}},
            "runtime": {"default_mode": "sync", "max_llm_calls": 2},
            "tools": {"allowed": ["rag.search_knowledge"]},
        },
    )


def test_agent_factory_loads_instruction_file(tmp_path: Path) -> None:
    """AgentFactory should load instruction content from file."""
    instruction_file = tmp_path / "prompt.md"
    instruction_file.write_text("You are helpful.", encoding="utf-8")

    built = AgentFactory(config_root=tmp_path).create(
        _sample_agent_config(instruction_file="prompt.md"),
    )

    assert built.instruction == "You are helpful."


def test_event_mapper_maps_known_and_unknown_events() -> None:
    """EventMapper should map known and unknown backend events."""
    mapper = EventMapper()

    known = mapper.map_event(
        {"type": "run_completed", "run_id": "r1", "payload": {}},
        agent_id="a1",
    )
    unknown = mapper.map_event(
        {"type": "weird", "run_id": "r2", "payload": {}},
        agent_id="a1",
    )

    assert known.event_type == "run.completed"
    assert unknown.event_type == "run.failed"


@pytest.mark.asyncio
async def test_embedded_runner_run_and_stream() -> None:
    """Embedded runner should return result and normalized stream."""
    runner = AdkEmbeddedRunner()
    request = RunRequest(agent_id="agent-1", input_text="hello", session_id="s1")

    result = await runner.run(request)
    events = [event async for event in runner.stream(request)]

    assert result.output_text == "hello"
    assert [event.event_type for event in events] == [
        "run.started",
        "message.completed",
        "run.completed",
    ]


class _FakeResponse:
    def __init__(self, data: dict[str, object]) -> None:
        self._data = data

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return self._data


class _FakeHttpClient:
    async def post(self, path: str, *, json: dict[str, str]) -> _FakeResponse:
        if path == "/run":
            return _FakeResponse({"run_id": "r-http", "output_text": json["input"]})
        return _FakeResponse(
            {
                "events": [
                    {"type": "run_started", "run_id": "r-http", "payload": {}},
                    {
                        "type": "run_completed",
                        "run_id": "r-http",
                        "payload": {},
                    },
                ],
            },
        )


@pytest.mark.asyncio
async def test_http_runner_run_and_stream() -> None:
    """HTTP runner should proxy and map run/stream responses."""
    runner = AdkHttpRunner(
        base_url="https://adk.example.test",
        client=_FakeHttpClient(),
    )
    request = RunRequest(agent_id="agent-http", input_text="hello")

    result = await runner.run(request)
    events = [event async for event in runner.stream(request)]

    assert result == RunResult(run_id="r-http", output_text="hello", status="completed")
    assert [event.event_type for event in events] == ["run.started", "run.completed"]


def test_runner_registry_lazy_build_and_unknown_mode() -> None:
    """RunnerRegistry should cache instances and reject unknown mode."""

    class DummyRunner:
        async def run(self, command: RunRequest) -> RunResult:
            return RunResult(run_id="dummy", output_text=command.input_text)

        async def stream(self, command: RunRequest) -> AsyncIterator[object]:
            _ = command
            if False:
                yield None

    registry = RunnerRegistry(
        mode="embedded",
        factories={"embedded": lambda _agent_id: DummyRunner()},
    )

    assert registry.get("a") is registry.get("a")
    with pytest.raises(RunnerRegistryError):
        RunnerRegistry(mode="missing", factories={}).get("a")
