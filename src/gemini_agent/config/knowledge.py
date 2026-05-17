"""Knowledge source config schemas."""

from typing import cast

from pydantic import BaseModel, Field


class KnowledgeSourceConfig(BaseModel):
    """One knowledge source descriptor."""

    id: str = Field(min_length=1)
    type: str = Field(min_length=1)
    path: str | None = None
    endpoint: str | None = None
    top_k: int = Field(default=5, ge=1)


class KnowledgeConfig(BaseModel):
    """Top-level knowledge source collection."""

    version: int = Field(default=1, ge=1)
    sources: list[KnowledgeSourceConfig] = Field(
        default_factory=lambda: cast("list[KnowledgeSourceConfig]", []),
    )
