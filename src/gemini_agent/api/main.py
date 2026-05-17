# pyright: reportUnknownMemberType=none, reportAttributeAccessIssue=none
"""FastAPI application factory."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException
from starlette.requests import Request  # noqa: TC002

from gemini_agent.config import AgentCatalog, ConfigLoader, ConfigLoadError
from gemini_agent.observability import (
    AccessLogger,
    AdkCallbackTelemetry,
    MetricsCollector,
    build_observability_middleware,
    initialize_opentelemetry,
    metrics_snapshot,
)
from gemini_agent.runner import AdkEmbeddedRunner, RunRequest
from gemini_agent.security.auth import Authenticator, Principal
from gemini_agent.settings import get_settings
from gemini_agent.skills import FilesystemSkillFactory, SkillFactoryError


class RunRequestBody(BaseModel):
    """Request payload for run endpoints."""

    agent_id: str = Field(min_length=1)
    input: str = Field(min_length=1)
    session_id: str | None = None


class AsyncJobCreateResponse(BaseModel):
    """Response for async job creation."""

    job_id: str
    status: str


class AsyncJobStatusResponse(BaseModel):
    """Response for async job status."""

    job_id: str
    status: str
    run_id: str | None = None
    output_text: str | None = None


class _JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, AsyncJobStatusResponse] = {}

    def create_pending(self, job_id: str) -> AsyncJobStatusResponse:
        status = AsyncJobStatusResponse(job_id=job_id, status="queued")
        self._jobs[job_id] = status
        return status

    def complete(
        self,
        job_id: str,
        *,
        run_id: str,
        output_text: str,
    ) -> AsyncJobStatusResponse:
        status = AsyncJobStatusResponse(
            job_id=job_id,
            status="completed",
            run_id=run_id,
            output_text=output_text,
        )
        self._jobs[job_id] = status
        return status

    def get(self, job_id: str) -> AsyncJobStatusResponse | None:
        return self._jobs.get(job_id)


_JOB_STORE = _JobStore()
_METRICS = MetricsCollector()
_ACCESS_LOGGER = AccessLogger()
_CALLBACK_TELEMETRY = AdkCallbackTelemetry()


def _authenticate_request(request: Request) -> Principal:
    """Authenticate a request from headers."""
    settings = get_settings()
    authenticator = Authenticator(settings)
    headers: Any = getattr(request, "headers", {})
    auth_header = headers.get("authorization")
    api_key = headers.get("x-api-key")
    return authenticator.authenticate(auth_header, api_key)


def healthz() -> dict[str, str]:
    """Return health status."""
    return {"status": "ok"}


def readyz() -> dict[str, str]:
    """Return readiness status."""
    return {"status": "ok"}


def list_agents(request: Request) -> dict[str, object]:
    """Return exposed agents from catalog."""
    _authenticate_request(request)
    settings = get_settings()
    loader = ConfigLoader(settings.config_root)
    try:
        raw_catalog = loader.load_agent_catalog()
    except ConfigLoadError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    catalog = AgentCatalog.model_validate(raw_catalog)
    agents = [
        {
            "agent_id": agent_id,
            "exposed": entry.exposed,
            "config_path": entry.config_path,
            "allowed_roles": entry.allowed_roles,
        }
        for agent_id, entry in catalog.agents.items()
        if entry.exposed
    ]
    return {"root_agent": catalog.root_agent, "agents": agents}


def get_skill(skill_id: str, request: Request) -> dict[str, str]:
    """Return skill prompt by skill ID."""
    _authenticate_request(request)
    skill_factory = FilesystemSkillFactory(Path("configs/skills"))
    try:
        spec = skill_factory.create(skill_id)
    except SkillFactoryError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"skill_id": spec.skill_id, "path": str(spec.path), "prompt": spec.prompt}


async def run_sync(body: RunRequestBody, request: Request) -> dict[str, str]:
    """Run one synchronous execution."""
    _authenticate_request(request)
    runner = AdkEmbeddedRunner()
    run_request = RunRequest(
        agent_id=body.agent_id,
        input_text=body.input,
        session_id=body.session_id,
    )
    result = await runner.run(run_request)
    return {
        "run_id": result.run_id,
        "output_text": result.output_text,
        "status": result.status,
    }


async def run_stream(
    body: RunRequestBody,
    request: Request,
) -> dict[str, list[dict[str, object]]]:
    """Run one streaming execution."""
    _authenticate_request(request)
    runner = AdkEmbeddedRunner()
    run_request = RunRequest(
        agent_id=body.agent_id,
        input_text=body.input,
        session_id=body.session_id,
    )
    events = [asdict(event) async for event in runner.stream(run_request)]
    return {"events": events}


async def create_async_job(
    body: RunRequestBody,
    request: Request,
) -> AsyncJobCreateResponse:
    """Create async job and persist completion state."""
    _authenticate_request(request)
    runner = AdkEmbeddedRunner()
    job_id = f"job-{uuid4().hex}"
    _JOB_STORE.create_pending(job_id)
    run_request = RunRequest(
        agent_id=body.agent_id,
        input_text=body.input,
        session_id=body.session_id,
    )
    result = await runner.run(run_request)
    _JOB_STORE.complete(job_id, run_id=result.run_id, output_text=result.output_text)
    return AsyncJobCreateResponse(job_id=job_id, status="queued")


def get_async_job(job_id: str, request: Request) -> AsyncJobStatusResponse:
    """Return async job current status."""
    _authenticate_request(request)
    found = _JOB_STORE.get(job_id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"job not found: {job_id}")
    return found


def get_metrics(request: Request) -> dict[str, object]:
    """Return in-memory HTTP metrics."""
    _authenticate_request(request)
    return metrics_snapshot(_METRICS)


def create_app() -> FastAPI:
    """Create and configure FastAPI app."""
    app = FastAPI(title="Gemini ADK Agent Framework API", version="0.1.0")
    app.get("/healthz")(healthz)
    app.get("/readyz")(readyz)
    app.get("/agents")(list_agents)
    app.get("/skills/{skill_id}")(get_skill)
    app.get("/metrics")(get_metrics)
    app.add_api_route("/run", run_sync, methods=["POST"])
    app.add_api_route("/run:stream", run_stream, methods=["POST"])
    app.add_api_route("/jobs", create_async_job, methods=["POST"])
    app.get("/jobs/{job_id}")(get_async_job)
    app.middleware("http")(
        build_observability_middleware(metrics=_METRICS, access_logger=_ACCESS_LOGGER),
    )
    app.state.otel = initialize_opentelemetry(service_name="gemini-adk-agent-framework")
    app.state.callback_telemetry = _CALLBACK_TELEMETRY
    return app
