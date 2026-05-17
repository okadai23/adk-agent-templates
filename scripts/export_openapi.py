"""Export OpenAPI schema to a JSON file."""

from __future__ import annotations

import json
from pathlib import Path

from gemini_agent.api.main import create_app


def export_openapi(output_path: Path) -> None:
    """Create app and write its OpenAPI schema to ``output_path``."""
    app = create_app()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(app.openapi(), indent=2), encoding="utf-8")


if __name__ == "__main__":
    export_openapi(Path("artifacts/openapi.json"))
