"""Unit tests for run and agent APIs."""

from pathlib import Path

from fastapi.testclient import TestClient

from gemini_agent.api.main import create_app


def test_get_agents_returns_exposed_agents_only() -> None:
    """GET /agents returns only exposed agent entries."""
    config_root = Path("configs")
    config_root.mkdir(exist_ok=True)
    catalog = config_root / "agent_catalog.yaml"
    catalog.write_text(
        """
version: 1
root_agent: root
agents:
  root:
    config_path: agents/root.yaml
    exposed: true
  hidden:
    config_path: agents/hidden.yaml
    exposed: false
""".strip(),
        encoding="utf-8",
    )

    try:
        client = TestClient(create_app())
        response = client.get("/agents")
    finally:
        catalog.unlink(missing_ok=True)

    assert response.status_code == 200
    body = response.json()
    assert body["root_agent"] == "root"
    assert [agent["agent_id"] for agent in body["agents"]] == ["root"]


def test_run_sync_and_stream_and_async_jobs() -> None:
    """Run endpoints should return sync, stream, and async job payloads."""
    client = TestClient(create_app())

    run_response = client.post("/run", json={"agent_id": "a1", "input": "hello"})
    assert run_response.status_code == 200
    assert run_response.json()["output_text"] == "hello"

    stream_response = client.post(
        "/run:stream",
        json={"agent_id": "a1", "input": "hello"},
    )
    assert stream_response.status_code == 200
    events = stream_response.json()["events"]
    assert [event["event_type"] for event in events] == [
        "run.started",
        "message.completed",
        "run.completed",
    ]

    create_job = client.post("/jobs", json={"agent_id": "a1", "input": "hello"})
    assert create_job.status_code == 200
    job_id = create_job.json()["job_id"]

    get_job = client.get(f"/jobs/{job_id}")
    assert get_job.status_code == 200
    assert get_job.json()["status"] == "completed"
