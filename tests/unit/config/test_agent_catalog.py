"""Unit tests for agent catalog/config models and graph validator."""

import pytest

from gemini_agent.config.agent_catalog import (
    AgentCatalog,
    AgentConfig,
    AgentGraphValidationError,
    AgentGraphValidator,
)


def _agent_config(agent_id: str, *, sub_agents: list[str] | None = None) -> AgentConfig:
    return AgentConfig.model_validate(
        {
            "version": 1,
            "agent": {
                "id": agent_id,
                "name": agent_id,
                "type": "llm",
            },
            "model": {"profile": "gemini_flash_default"},
            "runtime": {"default_mode": "sync", "max_llm_calls": 5},
            "sub_agents": sub_agents or [],
        },
    )


def test_agent_catalog_validates_root_agent_exists() -> None:
    """Catalog with existing root_agent should validate."""
    catalog = AgentCatalog.model_validate(
        {
            "version": 1,
            "root_agent": "router_agent",
            "agents": {
                "router_agent": {"config_path": "configs/agents/router_agent.yaml"},
            },
        },
    )

    assert catalog.root_agent == "router_agent"


def test_agent_catalog_rejects_unknown_root_agent() -> None:
    """Unknown root_agent should fail validation."""
    with pytest.raises(ValueError, match="root_agent"):
        AgentCatalog.model_validate(
            {
                "version": 1,
                "root_agent": "missing",
                "agents": {
                    "router_agent": {"config_path": "configs/agents/router_agent.yaml"},
                },
            },
        )


def test_agent_config_rejects_self_reference_sub_agent() -> None:
    """Agent cannot reference itself in sub_agents."""
    with pytest.raises(ValueError, match="sub_agents"):
        _agent_config("router_agent", sub_agents=["router_agent"])


def test_graph_validator_accepts_valid_dag() -> None:
    """Acyclic graph with known nodes should pass."""
    validator = AgentGraphValidator()
    configs = {
        "router_agent": _agent_config(
            "router_agent",
            sub_agents=["billing_agent", "rag_agent"],
        ),
        "billing_agent": _agent_config("billing_agent"),
        "rag_agent": _agent_config("rag_agent"),
    }

    validator.validate(configs, root_agent="router_agent")


def test_graph_validator_rejects_unknown_sub_agent() -> None:
    """Reference to missing sub-agent should fail."""
    validator = AgentGraphValidator()
    configs = {
        "router_agent": _agent_config("router_agent", sub_agents=["missing_agent"]),
    }

    with pytest.raises(AgentGraphValidationError, match="Unknown sub-agent"):
        validator.validate(configs)


def test_graph_validator_rejects_cycle() -> None:
    """Cycle in sub-agent graph should be rejected."""
    validator = AgentGraphValidator()
    configs = {
        "a": _agent_config("a", sub_agents=["b"]),
        "b": _agent_config("b", sub_agents=["a"]),
    }

    with pytest.raises(AgentGraphValidationError, match="Cycle detected"):
        validator.validate(configs)


def test_graph_validator_rejects_orphan_from_root() -> None:
    """Agent disconnected from root should fail root reachability check."""
    validator = AgentGraphValidator()
    configs = {
        "router_agent": _agent_config("router_agent", sub_agents=["billing_agent"]),
        "billing_agent": _agent_config("billing_agent"),
        "orphan_agent": _agent_config("orphan_agent"),
    }

    with pytest.raises(AgentGraphValidationError, match="Orphaned agents"):
        validator.validate(configs, root_agent="router_agent")
