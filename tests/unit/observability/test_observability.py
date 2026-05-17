# pyright: reportUnknownMemberType=none, reportAttributeAccessIssue=none
"""Unit tests for observability helpers and API integration."""

from fastapi.testclient import TestClient

from gemini_agent.api.main import create_app
from gemini_agent.observability import AdkCallbackTelemetry, MetricsCollector


def test_metrics_collector_average() -> None:
    """Average duration is computed from cumulative totals."""
    metrics = MetricsCollector()
    metrics.record(0.2)
    metrics.record(0.4)
    assert metrics.request_count == 2
    assert round(metrics.avg_duration_seconds, 5) == 0.3


def test_request_id_middleware_and_metrics_endpoint() -> None:
    """Middleware should preserve request ID and expose metrics endpoint."""
    client = TestClient(create_app())
    response = client.get("/healthz", headers={"x-request-id": "req-1"})
    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-1"

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert metrics.json()["request_count"] >= 1


def test_app_has_otel_and_callback_state() -> None:
    """App state should include telemetry-related placeholders."""
    app = create_app()
    assert app.state.otel["status"] == "initialized"
    telemetry = AdkCallbackTelemetry()
    telemetry.on_callback(callback_type="tool.start", payload={"tool": "rag"})
    assert telemetry.events[0]["callback_type"] == "tool.start"
