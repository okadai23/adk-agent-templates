"""MVP integration smoke tests."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from gemini_agent.api.main import create_app
from gemini_agent.settings import get_settings


def _write_example_config(config_root: Path) -> None:
    (config_root / "agents").mkdir(parents=True, exist_ok=True)

    (config_root / "agent_catalog.yaml").write_text(
        """
version: 1
root_agent: root
agents:
  root:
    config_path: agents/root.yaml
    exposed: true
""".strip(),
        encoding="utf-8",
    )

    (config_root / "agents" / "root.yaml").write_text(
        """
agent_id: root
name: Root Agent
model:
  profile: default
system_instruction: MVP smoke test agent
tools: []
skills: []
""".strip(),
        encoding="utf-8",
    )


def test_mvp_core_endpoints_smoke(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Core endpoints work with isolated test config."""
    config_root = tmp_path / "configs"
    _write_example_config(config_root)

    monkeypatch.setenv("AGENT_CONFIG_ROOT", str(config_root))
    get_settings.cache_clear()

    try:
        client = TestClient(create_app())

        assert client.get("/healthz").status_code == 200
        assert client.get("/readyz").status_code == 200

        agents = client.get("/agents")
        assert agents.status_code == 200
        assert agents.json()["root_agent"] == "root"

        run_resp = client.post("/run", json={"agent_id": "root", "input": "hello"})
        assert run_resp.status_code == 200
        assert run_resp.json()["status"] == "completed"
    finally:
        get_settings.cache_clear()
