"""Unit tests for skill API endpoint."""

from pathlib import Path

from fastapi.testclient import TestClient

from gemini_agent.api.main import create_app


def test_get_skill_returns_prompt() -> None:
    """GET /skills/{skill_id} should return the loaded skill."""
    skills_dir = Path("configs/skills")
    skills_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skills_dir / "router.md"
    skill_file.write_text("route requests", encoding="utf-8")

    try:
        client = TestClient(create_app())
        response = client.get("/skills/router")
    finally:
        skill_file.unlink(missing_ok=True)

    assert response.status_code == 200
    assert response.json()["skill_id"] == "router"
    assert response.json()["prompt"] == "route requests"


def test_get_skill_returns_404_for_missing() -> None:
    """GET /skills/{skill_id} returns 404 for unknown skill."""
    client = TestClient(create_app())

    response = client.get("/skills/not-found")

    assert response.status_code == 404
    assert "detail" in response.json()
