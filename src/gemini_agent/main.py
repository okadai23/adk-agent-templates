"""CLI entrypoint for Gemini ADK agent framework."""

import uvicorn


def main() -> None:
    """Run development server."""
    uvicorn.run("gemini_agent.api.main:create_app", factory=True)
