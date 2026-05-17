"""Contract-level checks for generated OpenAPI schema."""

from pathlib import Path

from scripts.export_openapi import export_openapi


def test_openapi_export_contains_core_paths(tmp_path: Path) -> None:
    """Exported schema should include core runtime API paths."""
    output_path = tmp_path / "openapi.json"
    export_openapi(output_path)

    text = output_path.read_text(encoding="utf-8")
    assert '"/healthz"' in text
    assert '"/run"' in text
    assert '"/metrics"' in text
