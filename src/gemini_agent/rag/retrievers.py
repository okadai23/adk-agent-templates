"""Knowledge retriever ports and implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class KnowledgeDocument:
    """One retrieved knowledge document."""

    id: str
    content: str
    score: float = 0.0
    source: str | None = None


class KnowledgeRetriever(Protocol):
    """Port for all knowledge retrievers."""

    def retrieve(self, query: str, *, top_k: int = 5) -> list[KnowledgeDocument]:
        """Retrieve top-k documents for the query."""
        ...


class FakeKnowledgeRetriever:
    """In-memory retriever mainly for tests/dev."""

    def __init__(self, documents: list[KnowledgeDocument] | None = None) -> None:
        """Initialize with optional static documents."""
        self._documents = documents or []

    def retrieve(self, query: str, *, top_k: int = 5) -> list[KnowledgeDocument]:
        """Retrieve documents containing the query text."""
        normalized_query = query.lower().strip()
        matched = [
            doc
            for doc in self._documents
            if normalized_query in doc.content.lower()
            or normalized_query in doc.id.lower()
        ]
        if not matched:
            matched = self._documents
        return matched[:top_k]


class HybridKnowledgeRetriever:
    """Aggregator retriever that merges results from child retrievers."""

    def __init__(self, retrievers: list[KnowledgeRetriever]) -> None:
        """Initialize with child retrievers."""
        self._retrievers = retrievers

    def retrieve(self, query: str, *, top_k: int = 5) -> list[KnowledgeDocument]:
        """Merge child results and return the highest-scored docs."""
        merged: dict[str, KnowledgeDocument] = {}
        for retriever in self._retrievers:
            for doc in retriever.retrieve(query, top_k=top_k):
                existing = merged.get(doc.id)
                if existing is None or doc.score > existing.score:
                    merged[doc.id] = doc
        return sorted(merged.values(), key=lambda doc: doc.score, reverse=True)[:top_k]
