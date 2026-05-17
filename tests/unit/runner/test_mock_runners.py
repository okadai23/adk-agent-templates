# pyright: reportUnknownMemberType=none, reportUntypedFunctionDecorator=none, reportAttributeAccessIssue=none
"""Unit tests for fake and recorded runners."""

import pytest

from gemini_agent.runner import (
    AgentEvent,
    FakeAgentRunner,
    RecordedAgentRunner,
    RunRequest,
    RunResult,
)


@pytest.mark.asyncio
async def test_fake_agent_runner_behaviour() -> None:
    """Fake runner should echo input and emit deterministic events."""
    runner = FakeAgentRunner()
    command = RunRequest(agent_id="a1", input_text="hello")

    result = await runner.run(command)
    events = [event async for event in runner.stream(command)]

    assert result.output_text == "hello"
    assert [event.event_type for event in events] == [
        "run.started",
        "message.completed",
        "run.completed",
    ]


@pytest.mark.asyncio
async def test_recorded_agent_runner_replay() -> None:
    """Recorded runner should replay stored outputs without execution."""
    runner = RecordedAgentRunner(
        run_result=RunResult(run_id="r1", output_text="recorded", status="completed"),
        stream_events=[
            AgentEvent(
                event_type="run.started",
                run_id="r1",
                agent_id="a1",
                payload={},
            ),
            AgentEvent(
                event_type="run.completed",
                run_id="r1",
                agent_id="a1",
                payload={},
            ),
        ],
    )

    command = RunRequest(agent_id="a1", input_text="ignored")
    result = await runner.run(command)
    events = [event async for event in runner.stream(command)]

    assert result.output_text == "recorded"
    assert [event.event_type for event in events] == ["run.started", "run.completed"]
