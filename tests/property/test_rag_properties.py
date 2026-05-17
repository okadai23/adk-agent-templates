"""Property-like checks for RAG factory invariants."""

from gemini_agent.config.knowledge import KnowledgeSourceConfig
from gemini_agent.rag.factory import KnowledgeSourceFactory


def test_factory_returns_retriever_for_valid_source() -> None:
    """Factory should create a retriever for supported source types."""
    source = KnowledgeSourceConfig.model_validate(
        {"id": "local-docs", "type": "fake", "path": "docs"},
    )
    retriever = KnowledgeSourceFactory().create(source)
    assert retriever is not None
