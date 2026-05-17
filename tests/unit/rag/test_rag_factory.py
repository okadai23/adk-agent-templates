"""Unit tests for knowledge config and RAG factories."""

from gemini_agent.config.knowledge import KnowledgeConfig
from gemini_agent.rag.factory import KnowledgeSourceFactory, build_rag_tool
from gemini_agent.rag.retrievers import (
    FakeKnowledgeRetriever,
    HybridKnowledgeRetriever,
    KnowledgeDocument,
)


def test_knowledge_config_model_validate() -> None:
    """KnowledgeConfig can parse typed source entries."""
    config = KnowledgeConfig.model_validate(
        {
            "version": 1,
            "sources": [{"id": "faq", "type": "fake", "top_k": 3}],
        },
    )

    assert config.sources[0].id == "faq"


def test_fake_knowledge_retriever_returns_matching_docs() -> None:
    """Fake retriever should filter documents by query."""
    retriever = FakeKnowledgeRetriever(
        documents=[
            KnowledgeDocument(id="1", content="Gemini FAQ", score=0.8),
            KnowledgeDocument(id="2", content="Billing guide", score=0.2),
        ],
    )

    docs = retriever.retrieve("faq", top_k=1)

    assert len(docs) == 1
    assert docs[0].id == "1"


def test_hybrid_retriever_merges_and_sorts_by_score() -> None:
    """Hybrid retriever should merge and rank child results."""
    high = FakeKnowledgeRetriever([KnowledgeDocument(id="a", content="A", score=0.9)])
    low = FakeKnowledgeRetriever([KnowledgeDocument(id="b", content="B", score=0.1)])

    hybrid = HybridKnowledgeRetriever([low, high])
    docs = hybrid.retrieve("", top_k=2)

    assert [doc.id for doc in docs] == ["a", "b"]


def test_knowledge_source_factory_and_rag_tool() -> None:
    """Factory and tool builder should provide queryable output."""
    factory = KnowledgeSourceFactory()
    retriever = factory.create_many(
        KnowledgeConfig.model_validate(
            {"sources": [{"id": "faq", "type": "fake"}]},
        ).sources,
    )

    result = build_rag_tool(retriever)("faq", 5)

    assert "Knowledge from faq" in result
