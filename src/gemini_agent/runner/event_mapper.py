# pyright: reportUnknownVariableType=none, reportUnknownArgumentType=none
"""Map backend-specific event structures into domain AgentEvent values."""

from __future__ import annotations

from gemini_agent.runner.models import AgentEvent

_EVENT_NAME_MAP = {
    "run_started": "run.started",
    "text_delta": "message.delta",
    "text_completed": "message.completed",
    "tool_started": "tool.call.started",
    "tool_completed": "tool.call.completed",
    "rag_started": "rag.search.started",
    "rag_completed": "rag.search.completed",
    "usage": "usage.reported",
    "run_completed": "run.completed",
    "run_failed": "run.failed",
}


class EventMapper:
    """Translate backend events into public domain events."""

    def map_event(self, event: dict[str, object], *, agent_id: str) -> AgentEvent:
        """Map one event payload from a backend."""
        backend_type = str(event.get("type", ""))
        event_type = _EVENT_NAME_MAP.get(backend_type, "run.failed")
        run_id = str(event.get("run_id", ""))

        raw_payload = event.get("payload", {})
        payload: dict[str, str] = {}
        if isinstance(raw_payload, dict):
            for key, value in raw_payload.items():
                payload[str(key)] = str(value)

        if event_type == "run.failed" and backend_type not in _EVENT_NAME_MAP:
            payload["reason"] = f"unknown event type: {backend_type}"

        return AgentEvent(
            event_type=event_type,
            run_id=run_id,
            agent_id=agent_id,
            payload=payload,
        )
