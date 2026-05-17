"""Factories for knowledge retrievers and RAG tool adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from gemini_agent.config.knowledge import KnowledgeSourceConfig
from gemini_agent.rag.retrievers import (
    FakeKnowledgeRetriever,
    HybridKnowledgeRetriever,
    KnowledgeDocument,
    KnowledgeRetriever,
)


class KnowledgeSourceFactory:
    """Build retrievers from typed knowledge source configs."""

    def create(self, source: KnowledgeSourceConfig) -> KnowledgeRetriever:
        """Create one retriever from a source config."""
        if source.type == "fake":
            sample = [
                KnowledgeDocument(
                    id=f"{source.id}-doc-1",
                    content=f"Knowledge from {source.id}",
                    score=1.0,
                    source=source.id,
                ),
            ]
            return FakeKnowledgeRetriever(documents=sample)
        msg = f"Unsupported knowledge source type: {source.type}"
        raise ValueError(msg)

    def create_many(
        self, sources: list[KnowledgeSourceConfig],
    ) -> HybridKnowledgeRetriever:
        """Create one hybrid retriever from multiple source configs."""
        return HybridKnowledgeRetriever([self.create(source) for source in sources])


def build_rag_tool(retriever: KnowledgeRetriever) -> Callable[[str, int], str]:
    """Build a simple callable tool backed by a retriever."""

    def rag_tool(query: str, top_k: int = 5) -> str:
        docs = retriever.retrieve(query, top_k=top_k)
        if not docs:
            return ""
        return "\n".join(doc.content for doc in docs)

    return rag_tool
