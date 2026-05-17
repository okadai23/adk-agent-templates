"""Agent catalog / per-agent config schemas and graph validation."""

from __future__ import annotations

from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AgentGraphValidationError(RuntimeError):
    """Raised when agent dependency graph is invalid."""


class AgentCatalogEntry(BaseModel):
    """One exposed agent entry in agent_catalog.yaml."""

    config_path: str = Field(min_length=1)
    exposed: bool = True
    allowed_roles: list[str] = Field(default_factory=list)


class AgentCatalog(BaseModel):
    """Top-level catalog for all available agents."""

    version: int = Field(ge=1)
    root_agent: str = Field(min_length=1)
    agents: dict[str, AgentCatalogEntry] = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_root_agent_exists(self) -> AgentCatalog:
        if self.root_agent not in self.agents:
            msg = f"root_agent '{self.root_agent}' is not defined in agents."
            raise ValueError(msg)
        return self


class AgentIdentity(BaseModel):
    """Agent identity and prompt wiring."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    description: str | None = None
    instruction_file: str | None = None


class AgentModelConfig(BaseModel):
    """Model profile and per-agent override section."""

    profile: str = Field(min_length=1)
    overrides: dict[str, Any] = Field(default_factory=dict)


class AgentRuntimeConfig(BaseModel):
    """Runtime guardrails for one agent."""

    default_mode: str = "sync"
    max_llm_calls: int = Field(default=10, ge=1)
    include_contents: str | None = None


class AgentToolConfig(BaseModel):
    """Tool allow-list."""

    allowed: list[str] = Field(default_factory=list)


class AgentRagTool(BaseModel):
    """RAG tool descriptor."""

    name: str
    description: str | None = None


class AgentPreRetrievalConfig(BaseModel):
    """Pre-retrieval policy hints."""

    enabled: bool = False
    required_for: list[str] = Field(default_factory=list)


class AgentRagConfig(BaseModel):
    """RAG settings for one agent."""

    mode: str
    retriever: str
    tool: AgentRagTool
    pre_retrieval: AgentPreRetrievalConfig = Field(
        default_factory=AgentPreRetrievalConfig,
    )


class AgentSkillRef(BaseModel):
    """One skill reference."""

    skill_id: str
    source: str
    path: str
    additional_tools: list[str] = Field(default_factory=list)


class AgentSkillsConfig(BaseModel):
    """Skill integration settings."""

    enabled: bool = False
    refs: list[AgentSkillRef] = Field(
        default_factory=lambda: cast("list[AgentSkillRef]", []),
    )


class AgentObservabilityConfig(BaseModel):
    """Per-agent telemetry/logging toggles."""

    track_token_usage: bool = True
    track_latency: bool = True
    track_first_token_latency: bool = True
    prompt_logging: bool = False
    response_logging: bool = False


class AgentConfig(BaseModel):
    """Full config for one concrete agent."""

    version: int = Field(ge=1)
    agent: AgentIdentity
    model: AgentModelConfig
    runtime: AgentRuntimeConfig
    sub_agents: list[str] = Field(default_factory=list)
    tools: AgentToolConfig = Field(default_factory=AgentToolConfig)
    rag: AgentRagConfig | None = None
    skills: AgentSkillsConfig = Field(default_factory=AgentSkillsConfig)
    observability: AgentObservabilityConfig = Field(
        default_factory=AgentObservabilityConfig,
    )

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def _validate_self_reference(self) -> AgentConfig:
        if self.agent.id in self.sub_agents:
            msg = "sub_agents cannot contain self agent.id."
            raise ValueError(msg)
        return self


class AgentGraphValidator:
    """Validate inter-agent dependency graphs defined by sub_agents."""

    def validate(
        self,
        configs: dict[str, AgentConfig],
        *,
        root_agent: str | None = None,
    ) -> None:
        """Check missing references, graph cycles, and optional root reachability."""
        if root_agent is not None and root_agent not in configs:
            msg = f"Unknown root agent: {root_agent}"
            raise AgentGraphValidationError(msg)

        for agent_id, config in configs.items():
            for sub_id in config.sub_agents:
                if sub_id not in configs:
                    msg = f"Unknown sub-agent reference: '{agent_id}' -> '{sub_id}'"
                    raise AgentGraphValidationError(msg)

        state: dict[str, int] = dict.fromkeys(configs, 0)
        for agent_id in configs:
            if state[agent_id] == 0:
                self._visit(agent_id, configs, state, stack=[])

        if root_agent is not None:
            reachable = self._collect_reachable(root_agent, configs)
            orphaned = sorted(set(configs) - reachable)
            if orphaned:
                orphaned_list = ", ".join(orphaned)
                msg = (
                    f"Orphaned agents not reachable from root_agent '"
                    f"{root_agent}': {orphaned_list}"
                )
                raise AgentGraphValidationError(msg)

    def _visit(
        self,
        agent_id: str,
        configs: dict[str, AgentConfig],
        state: dict[str, int],
        stack: list[str],
    ) -> None:
        state[agent_id] = 1
        stack.append(agent_id)
        for child in configs[agent_id].sub_agents:
            if state[child] == 0:
                self._visit(child, configs, state, stack)
            elif state[child] == 1:
                cycle_start = stack.index(child)
                cycle = " -> ".join([*stack[cycle_start:], child])
                msg = f"Cycle detected in agent graph: {cycle}"
                raise AgentGraphValidationError(msg)
        stack.pop()
        state[agent_id] = 2

    def _collect_reachable(
        self,
        root_agent: str,
        configs: dict[str, AgentConfig],
    ) -> set[str]:
        seen: set[str] = set()
        queue = [root_agent]
        while queue:
            node = queue.pop()
            if node in seen:
                continue
            seen.add(node)
            queue.extend(configs[node].sub_agents)
        return seen
