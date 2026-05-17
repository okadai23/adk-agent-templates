"""FastAPI application factory."""

from fastapi import FastAPI


def healthz() -> dict[str, str]:
    """Health check endpoint response."""
    return {"status": "ok"}


def readyz() -> dict[str, str]:
    """Readiness endpoint response."""
    return {"status": "ok"}


def create_app() -> FastAPI:
    """Create and configure FastAPI app."""
    app = FastAPI(title="Gemini ADK Agent Framework API", version="0.1.0")
    app.get("/healthz")(healthz)
    app.get("/readyz")(readyz)
    return app
