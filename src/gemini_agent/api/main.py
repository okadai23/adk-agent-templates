"""FastAPI application factory."""

from pathlib import Path

from fastapi import FastAPI

from gemini_agent.skills import FilesystemSkillFactory, SkillFactoryError


def healthz() -> dict[str, str]:
    """Health check endpoint response."""
    return {"status": "ok"}


def readyz() -> dict[str, str]:
    """Readiness endpoint response."""
    return {"status": "ok"}


def get_skill(skill_id: str) -> dict[str, str]:
    """Return skill metadata and prompt."""
    skill_factory = FilesystemSkillFactory(Path("configs/skills"))
    try:
        spec = skill_factory.create(skill_id)
    except SkillFactoryError as exc:
        return {"error": str(exc)}
    return {
        "skill_id": spec.skill_id,
        "path": str(spec.path),
        "prompt": spec.prompt,
    }


def create_app() -> FastAPI:
    """Create and configure FastAPI app."""
    app = FastAPI(title="Gemini ADK Agent Framework API", version="0.1.0")
    app.get("/healthz")(healthz)
    app.get("/readyz")(readyz)
    app.get("/skills/{skill_id}")(get_skill)
    return app
