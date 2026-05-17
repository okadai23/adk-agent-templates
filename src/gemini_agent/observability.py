"""Observability helpers (request-id, access log, metrics, telemetry callbacks)."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import TYPE_CHECKING, Any
from uuid import uuid4

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from starlette.requests import Request
    from starlette.responses import Response


@dataclass
class MetricsCollector:
    """In-memory metrics collector for HTTP requests."""

    request_count: int = 0
    total_duration_seconds: float = 0.0

    def record(self, duration_seconds: float) -> None:
        """Record a request duration."""
        self.request_count += 1
        self.total_duration_seconds += duration_seconds

    @property
    def avg_duration_seconds(self) -> float:
        """Return average request duration."""
        if self.request_count == 0:
            return 0.0
        return self.total_duration_seconds / self.request_count


class AccessLogger:
    """Simple access logger abstraction for testing and callback telemetry."""

    def __init__(self) -> None:
        """Initialize in-memory log storage."""
        self.records: list[dict[str, object]] = []

    def log(self, *, request_id: str, method: str, path: str, status_code: int) -> None:
        """Append one access log record."""
        self.records.append(
            {
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": status_code,
            },
        )


class AdkCallbackTelemetry:
    """Collect ADK callback events for lightweight telemetry."""

    def __init__(self) -> None:
        """Initialize callback event storage."""
        self.events: list[dict[str, object]] = []

    def on_callback(self, *, callback_type: str, payload: dict[str, object]) -> None:
        """Record one callback event."""
        self.events.append({"callback_type": callback_type, "payload": payload})


def initialize_opentelemetry(*, service_name: str) -> dict[str, str]:
    """Initialize OpenTelemetry provider placeholder and return metadata."""
    return {"service_name": service_name, "status": "initialized"}


def build_observability_middleware(
    *,
    metrics: MetricsCollector,
    access_logger: AccessLogger,
) -> Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]:
    """Create middleware for request-id, access log, and metrics."""

    async def middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid4())
        request.state.request_id = request_id
        started_at = perf_counter()
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        metrics.record(perf_counter() - started_at)
        access_logger.log(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )
        return response

    return middleware


def metrics_snapshot(metrics: MetricsCollector) -> dict[str, Any]:
    """Return HTTP metrics snapshot payload."""
    return {
        "request_count": metrics.request_count,
        "total_duration_seconds": metrics.total_duration_seconds,
        "avg_duration_seconds": metrics.avg_duration_seconds,
    }
