"""FastAPI application factory."""

from fastapi import APIRouter, FastAPI

router = APIRouter()


@router.get("/healthz")
def healthz() -> dict[str, str]:
    """Health check endpoint response."""
    return {"status": "ok"}


@router.get("/readyz")
def readyz() -> dict[str, str]:
    """Readiness endpoint response."""
    return {"status": "ok"}


def create_app() -> FastAPI:
    """Create and configure FastAPI app."""
    app = FastAPI(title="Gemini ADK Agent Framework API", version="0.1.0")
    app.include_router(router)
    return app
