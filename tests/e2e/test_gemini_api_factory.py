"""E2E tests for FastAPI app factory."""

from fastapi.testclient import TestClient

from gemini_agent.api.main import create_app


def test_healthz_and_readyz_and_openapi() -> None:
    """Factory app should expose health and OpenAPI endpoints."""
    client = TestClient(create_app())

    health = client.get("/healthz")
    ready = client.get("/readyz")
    openapi = client.get("/openapi.json")

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    assert ready.status_code == 200
    assert ready.json() == {"status": "ok"}

    assert openapi.status_code == 200
    assert openapi.headers["content-type"].startswith("application/json")
