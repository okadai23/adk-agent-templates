# Gemini ADK Agent Framework 仕様書 v1

作成日: 2026-05-16  
ステータス: Draft v1  
対象: Google Gemini / Google ADK を利用した、FastAPI公開可能なAI Agent開発フレームワーク

---

## 1. 目的

本仕様書は、Google Gemini と Google ADK を使ったAI Agentを、簡易に動かせ、かつ本番運用に向けて拡張できる形で実装するためのフレームワーク仕様を定義する。

主な目的は以下である。

1. FastAPI によるREST API公開
2. Auth認証、認可、監査ログへの対応
3. Google ADK を内側のAgent実行基盤として利用
4. クリーンアーキテクチャとTDDを前提にした構造
5. Pydantic / Pydantic Settings による型安全な設定管理
6. YAML DSLによる複数Agent、LLMパラメータ、RAG、Skill、Tool、環境差分の宣言的管理
7. OpenAPI Spec、Mock、Contract Test、Property-based Testingへの対応
8. RAGナレッジソースのFactory切替
9. 同期、Streaming、非同期Job実行への対応
10. LLM Token Usage、Latency、Trace、Tool/RAG実行を含むObservability

---

## 2. 設計原則

### 2.1 Config-first

Agent、Model Profile、RAG Retriever、Skill、Tool、Runtime、Observabilityは設定ファイルから注入する。コードを変更せずにAgentの追加やLLMパラメータ変更を可能にする。

### 2.2 ADKは内部Runtimeとして扱う

外部APIにはADKの `/run` 形式をそのまま出さない。FastAPI側でプロダクトAPIを設計し、ADK依存は `infrastructure/adk` に閉じ込める。

### 2.3 Clean Architecture

依存方向は以下とする。

```text
API Layer
  -> Application Layer
    -> Domain Layer
Application Layer
  -> Ports
Infrastructure Layer
  -> Ports implementations
```

Domain / Application は FastAPI、ADK、Vector DB、OpenTelemetryを知らない。

### 2.4 Testability by Design

ADK/Geminiを呼ばなくても、Fake Runner / Recorded RunnerによりAPI、Auth、Config、RAG、Telemetryをテストできる設計にする。

### 2.5 Secure by Default

本番では以下を禁止または制限する。

- `auth_mode=none`
- prompt/response全文の標準ログ出力
- YAMLから任意Python import
- Skill内scriptの自動実行
- LLMによるtenant filterの決定
- 通常ユーザーによるmodel override

### 2.6 Observable by Default

すべてのAgent実行で以下を記録する。

- `trace_id`
- `request_id`
- `run_id`
- `agent_id`
- `model_profile`
- `model`
- `config_hash`
- `latency_ms`
- `first_token_latency_ms`
- `input_tokens`
- `output_tokens`
- `total_tokens`
- `tool_calls`
- `rag_chunks`
- `status`

---

## 3. スコープ

### 3.1 v1で実装するもの

- FastAPI REST API
- API Key Auth / JWT Authの設計とAPI Key実装
- ADK Embedded Runner
- ADK HTTP Runner
- Fake Runner
- Recorded Runner
- Model Profile Resolver
- Agent Config Loader
- Knowledge Source Factory
- Tool Registry
- RAG Tool Factory
- ADK Skill Factory
- Agent Factory
- Runner Registry
- Sync API
- SSE Streaming API
- Async Job APIの基礎
- OpenAPI snapshot test
- SchemathesisによるContract / Property-based API test
- HypothesisによるConfig / RAG property tests
- Structured logging
- OpenTelemetry tracing
- Prometheus-compatible metrics
- Token usage / latency collection

### 3.2 v1で実装しないもの

- GUI管理画面
- Runtime hot reloadの完全対応
- 複雑なHuman-in-the-loop approval UI
- 本格的なQueue基盤の専用実装
- すべてのVector DB provider実装
- 音声双方向streamingの本番対応
- Side-effect toolの業務実装

---

## 4. 推奨リポジトリ構成

```text
gemini-adk-agent-starter/
├── README.md
├── pyproject.toml
├── Makefile
├── Dockerfile
├── .env.example
├── configs/
│   ├── app.yaml
│   ├── model_profiles.yaml
│   ├── knowledge_sources.yaml
│   ├── agent_catalog.yaml
│   ├── environments/
│   │   ├── local.yaml
│   │   ├── staging.yaml
│   │   └── prod.yaml
│   └── agents/
│       ├── router_agent.yaml
│       ├── rag_answer_agent.yaml
│       └── billing_agent.yaml
├── prompts/
│   ├── router_agent.md
│   ├── rag_answer_agent.md
│   └── billing_agent.md
├── skills/
│   ├── policy-qa/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── answer_policy.md
│   └── invoice-processing/
│       ├── SKILL.md
│       ├── references/
│       │   └── invoice_rules.md
│       ├── assets/
│       │   └── invoice_response_template.json
│       └── scripts/
│           └── normalize_invoice.py
├── specs/
│   ├── openapi/
│   │   ├── openapi.json
│   │   └── openapi.yaml
│   └── examples/
│       ├── run.sync.request.json
│       ├── run.sync.response.json
│       └── run.stream.sse.txt
├── mocks/
│   ├── recorded/
│   │   ├── rag_answer_agent.basic.json
│   │   └── billing_agent.invoice.json
│   └── fixtures/
│       └── knowledge_search.json
├── scripts/
│   ├── export_openapi.py
│   ├── validate_config.py
│   └── smoke_run_agent.py
├── src/
│   └── gemini_agent/
│       ├── settings.py
│       ├── domain/
│       │   ├── models.py
│       │   ├── events.py
│       │   └── policies.py
│       ├── application/
│       │   ├── ports/
│       │   │   ├── agent_runner.py
│       │   │   ├── agent_registry.py
│       │   │   ├── auth_verifier.py
│       │   │   ├── job_store.py
│       │   │   ├── knowledge_retriever.py
│       │   │   ├── session_store.py
│       │   │   ├── skill_registry.py
│       │   │   └── telemetry_recorder.py
│       │   └── use_cases/
│       │       ├── list_agents.py
│       │       ├── run_agent_sync.py
│       │       ├── stream_agent.py
│       │       ├── start_agent_job.py
│       │       ├── get_agent_run.py
│       │       └── cancel_agent_run.py
│       ├── config/
│       │   ├── models.py
│       │   ├── loader.py
│       │   ├── merger.py
│       │   ├── profile_resolver.py
│       │   ├── secret_resolver.py
│       │   ├── validators.py
│       │   └── config_hash.py
│       ├── api/
│       │   ├── main.py
│       │   ├── deps/
│       │   │   ├── auth.py
│       │   │   └── container.py
│       │   ├── middleware/
│       │   │   ├── request_id.py
│       │   │   ├── access_log.py
│       │   │   └── telemetry.py
│       │   ├── routes/
│       │   │   ├── health.py
│       │   │   ├── agents.py
│       │   │   ├── runs.py
│       │   │   ├── stream.py
│       │   │   └── skills.py
│       │   └── schemas/
│       │       ├── agents.py
│       │       ├── runs.py
│       │       ├── events.py
│       │       ├── usage.py
│       │       ├── rag.py
│       │       └── errors.py
│       └── infrastructure/
│           ├── adk/
│           │   ├── agent_factory.py
│           │   ├── embedded_runner.py
│           │   ├── http_runner.py
│           │   ├── event_mapper.py
│           │   ├── model_config_factory.py
│           │   ├── runner_registry.py
│           │   ├── skill_factory.py
│           │   └── callbacks.py
│           ├── auth/
│           │   ├── api_key.py
│           │   └── jwt.py
│           ├── knowledge/
│           │   ├── factory.py
│           │   ├── fake.py
│           │   ├── pgvector.py
│           │   ├── vertex_ai_rag.py
│           │   ├── adk_memory.py
│           │   ├── opensearch.py
│           │   ├── http.py
│           │   └── hybrid.py
│           ├── tools/
│           │   ├── registry.py
│           │   ├── rag_tool_factory.py
│           │   └── current_time.py
│           ├── jobs/
│           │   ├── memory_job_store.py
│           │   └── sqlite_job_store.py
│           ├── sessions/
│           │   ├── memory.py
│           │   └── sqlite.py
│           ├── mocks/
│           │   ├── fake_agent_runner.py
│           │   └── recorded_agent_runner.py
│           └── telemetry/
│               ├── logging.py
│               ├── metrics.py
│               └── tracing.py
└── tests/
    ├── unit/
    ├── integration/
    ├── contract/
    ├── property/
    └── e2e/
```

---

## 5. API仕様

### 5.1 エンドポイント一覧

| Method | Path | 用途 |
|---|---|---|
| GET | `/healthz` | process alive check |
| GET | `/readyz` | config / dependency readiness check |
| GET | `/v1/agents` | 公開Agent一覧 |
| GET | `/v1/agents/{agent_id}` | Agent詳細 |
| GET | `/v1/skills` | 公開Skill一覧 |
| POST | `/v1/agents/{agent_id}/runs:sync` | 同期実行 |
| POST | `/v1/agents/{agent_id}/runs:stream` | SSE streaming実行 |
| POST | `/v1/agents/{agent_id}/runs` | 非同期Job開始 |
| GET | `/v1/runs/{run_id}` | Job状態取得 |
| GET | `/v1/runs/{run_id}/events` | Event replay |
| POST | `/v1/runs/{run_id}:cancel` | Job cancel |

### 5.2 認証

全APIは原則 `Authorization: Bearer <token>` を要求する。

Auth mode:

| Mode | 用途 | 本番利用 |
|---|---|---|
| `none` | local dev only | 禁止 |
| `api_key` | PoC / 社内MVP | 条件付き可 |
| `jwt` | 本番API | 推奨 |

### 5.3 `RunAgentRequest`

```json
{
  "user_message": "社内FAQから経費精算の締め日を教えて",
  "session_id": "s_001",
  "metadata": {
    "tenant_id": "tenant-a"
  },
  "override": {
    "generate_content_config": {
      "temperature": 0.0,
      "max_output_tokens": 1024
    }
  }
}
```

`override` は設定で許可されたroleとfieldに限る。

### 5.4 `AgentRunResponse`

```json
{
  "run_id": "run_01JABC",
  "agent_id": "rag_answer_agent",
  "session_id": "s_001",
  "status": "completed",
  "message": "経費精算の締め日は...",
  "usage": {
    "input_tokens": 721,
    "output_tokens": 143,
    "total_tokens": 864,
    "cached_tokens": 0,
    "thoughts_tokens": 0
  },
  "latency_ms": 842.3,
  "first_token_latency_ms": null,
  "trace_id": "0f4c...",
  "citations": [
    {
      "source_id": "internal_faq",
      "document_id": "doc_123",
      "chunk_id": "chunk_02",
      "title": "経費精算ルール",
      "uri": "kb://internal_faq/doc_123"
    }
  ],
  "events": []
}
```

### 5.5 SSE Event形式

`/runs:stream` は `text/event-stream` を返す。

```text
event: run.started
data: {"run_id":"run_01JABC","agent_id":"rag_answer_agent"}

event: tool.call.started
data: {"tool_name":"rag.search_knowledge"}

event: message.delta
data: {"text":"経費精算の"}

event: usage.reported
data: {"input_tokens":721,"output_tokens":143,"total_tokens":864}

event: run.completed
data: {"status":"completed"}
```

---

## 6. 設定ファイル仕様

### 6.1 `configs/model_profiles.yaml`

```yaml
version: 1

default_profile: gemini_flash_default

profiles:
  gemini_flash_base:
    provider: google
    model: gemini-2.5-flash
    generate_content_config:
      temperature: 0.2
      top_p: 0.9
      top_k: 40
      max_output_tokens: 2048
      stop_sequences: []
    safety:
      profile: standard
    observability:
      track_token_usage: true
      track_latency: true

  gemini_flash_default:
    extends: gemini_flash_base
    generate_content_config:
      temperature: 0.3

  gemini_flash_deterministic:
    extends: gemini_flash_base
    generate_content_config:
      temperature: 0.0
      top_p: 0.8
      max_output_tokens: 1536

  gemini_flash_creative:
    extends: gemini_flash_base
    generate_content_config:
      temperature: 0.8
      top_p: 0.95
      max_output_tokens: 4096

  gemini_pro_reasoning:
    extends: gemini_flash_base
    model: gemini-2.5-pro
    generate_content_config:
      temperature: 0.2
      max_output_tokens: 8192
```

### 6.2 Model Profile解決ルール

Agentが `model.profile` を指定しない場合は `default_profile` を利用する。

優先順位:

```text
1. parent profile
2. child profile
3. agent.model.overrides
4. environment override
5. request-time override
```

merge semantics:

| 型 | 挙動 |
|---|---|
| dict | deep merge |
| scalar | childがparentを上書き |
| list | デフォルトはreplace |
| list append | `$append` を明示 |
| list remove | `$remove` を明示 |
| null | 親値を削除 |

### 6.3 `configs/knowledge_sources.yaml`

```yaml
version: 1

default_retriever: internal_knowledge_hybrid

sources:
  internal_docs_vector:
    type: vertex_ai_rag
    config:
      corpus_id: ${SECRET:VERTEX_RAG_CORPUS_ID}
      project: ${ENV:GOOGLE_CLOUD_PROJECT}
      location: us-central1
      top_k: 8
      distance_threshold: 0.65

  internal_faq_pgvector:
    type: pgvector
    config:
      dsn: ${SECRET:PGVECTOR_DSN}
      table: document_chunks
      embedding_model: text-embedding-004
      top_k: 5
      min_score: 0.7

  long_term_memory:
    type: adk_memory
    config:
      provider: vertex_ai_memory_bank
      project: ${ENV:GOOGLE_CLOUD_PROJECT}
      location: us-central1
      agent_engine_id: ${SECRET:AGENT_ENGINE_ID}
      top_k: 5

  local_fake_knowledge:
    type: fake
    config:
      fixture_path: mocks/fixtures/knowledge_search.json

retrievers:
  internal_knowledge_hybrid:
    type: hybrid
    config:
      strategy: weighted_merge
      sources:
        - source_id: internal_docs_vector
          weight: 0.7
        - source_id: internal_faq_pgvector
          weight: 0.3
      top_k: 5
      min_score: 0.65

  memory_first:
    type: hybrid
    config:
      strategy: priority
      sources:
        - source_id: long_term_memory
        - source_id: internal_docs_vector
      top_k: 5
```

### 6.4 `configs/agent_catalog.yaml`

```yaml
version: 1

root_agent: router_agent

agents:
  router_agent:
    config_path: configs/agents/router_agent.yaml
    exposed: true
    allowed_roles: ["employee", "admin"]

  rag_answer_agent:
    config_path: configs/agents/rag_answer_agent.yaml
    exposed: true
    allowed_roles: ["employee", "admin"]

  billing_agent:
    config_path: configs/agents/billing_agent.yaml
    exposed: false
    allowed_roles: ["employee", "admin"]
```

### 6.5 Agent Config例

```yaml
version: 1

agent:
  id: rag_answer_agent
  name: rag_answer_agent
  type: llm
  description: Answers questions using approved knowledge sources.
  instruction_file: prompts/rag_answer_agent.md

model:
  profile: gemini_flash_deterministic
  overrides:
    generate_content_config:
      max_output_tokens: 3072

runtime:
  default_mode: sync
  max_llm_calls: 15
  include_contents: default

sub_agents: []

tools:
  allowed:
    - rag.search_knowledge
    - local.current_time

rag:
  mode: hybrid
  retriever: internal_knowledge_hybrid
  tool:
    name: rag.search_knowledge
    description: Search approved internal knowledge sources.
  pre_retrieval:
    enabled: true
    required_for:
      - internal_policy_question
      - contract_question
      - company_knowledge_question

skills:
  enabled: true
  refs:
    - skill_id: policy-qa
      source: filesystem
      path: skills/policy-qa
      additional_tools:
        - rag.search_knowledge

observability:
  track_token_usage: true
  track_latency: true
  track_first_token_latency: true
  prompt_logging: false
  response_logging: false
```

### 6.6 Environment Override例

```yaml
version: 1

model_profiles:
  gemini_flash_default:
    generate_content_config:
      max_output_tokens: 2048

agents:
  rag_answer_agent:
    model:
      overrides:
        generate_content_config:
          temperature: 0.0
    runtime:
      max_llm_calls: 10
    observability:
      prompt_logging: false
      response_logging: false

knowledge_sources:
  internal_docs_vector:
    type: vertex_ai_rag
    config:
      corpus_id: ${SECRET:VERTEX_RAG_CORPUS_ID}
```

---

## 7. Pydantic Settings

`.env` や環境変数から外側の設定を読む。

```python
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AGENT_",
        extra="ignore",
    )

    environment: Literal["local", "staging", "prod"] = "local"
    config_root: Path = Path("configs")

    auth_mode: Literal["none", "api_key", "jwt"] = "api_key"
    api_keys: list[SecretStr] = []

    runner_mode: Literal["fake", "recorded", "adk_embedded", "adk_http"] = "adk_embedded"
    adk_http_base_url: str = "http://localhost:8001"

    google_api_key: SecretStr | None = None
    google_cloud_project: str | None = None
    google_cloud_location: str = "us-central1"

    secrets_provider: Literal["env", "gcp_secret_manager"] = "env"

    otel_enabled: bool = True
    otel_exporter_otlp_endpoint: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

## 8. Domain Model

```python
from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class Principal:
    subject: str
    roles: frozenset[str]
    tenant_id: str | None = None


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    cached_tokens: int | None = None
    thoughts_tokens: int | None = None


@dataclass(frozen=True)
class AgentEvent:
    type: str
    run_id: str
    sequence: int
    data: dict[str, Any]


@dataclass(frozen=True)
class AgentReply:
    message: str
    events: list[AgentEvent]
    usage: TokenUsage | None
    latency_ms: float | None
    first_token_latency_ms: float | None = None
```

---

## 9. Application Ports

### 9.1 AgentRunner

```python
from typing import AsyncIterator, Protocol
from dataclasses import dataclass


@dataclass(frozen=True)
class RunAgentCommand:
    agent_id: str
    user_id: str
    session_id: str
    message: str
    metadata: dict


class AgentRunner(Protocol):
    async def run(self, command: RunAgentCommand) -> AgentReply:
        ...

    async def stream(self, command: RunAgentCommand) -> AsyncIterator[AgentEvent]:
        ...
```

### 9.2 KnowledgeRetriever

```python
from typing import Protocol
from pydantic import BaseModel, Field


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    top_k: int = Field(default=5, ge=1, le=20)
    source_ids: list[str] = Field(default_factory=list)
    filters: dict[str, str] = Field(default_factory=dict)
    principal: Principal


class KnowledgeChunk(BaseModel):
    source_id: str
    document_id: str
    chunk_id: str
    title: str
    text: str
    score: float = Field(ge=0.0, le=1.0)
    uri: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class KnowledgeSearchResult(BaseModel):
    query: str
    chunks: list[KnowledgeChunk]
    latency_ms: float | None = None


class KnowledgeRetriever(Protocol):
    async def search(self, request: KnowledgeSearchRequest) -> KnowledgeSearchResult:
        ...
```

---

## 10. Factory設計

### 10.1 ProfileResolver

責務:

- `default_profile` 解決
- `extends` 解決
- 継承cycle検出
- Agent override適用
- Environment override適用
- Request override適用
- request override許可field検証
- 最終ProfileのPydantic validation
- `config_hash` 生成

### 10.2 KnowledgeSourceFactory

責務:

- `knowledge_sources.yaml` のsource定義を読み込む
- `type` に応じたBuilderへ委譲
- retriever logical nameをsourceまたはhybrid retrieverに解決
- singleton cache管理
- productionでfake sourceを禁止

対応source type:

| type | v1実装方針 |
|---|---|
| `fake` | fixtureから返す |
| `pgvector` | interfaceとconfig validationまで。実装はMVP後半 |
| `vertex_ai_rag` | interfaceとconfig validationまで。実装はMVP後半 |
| `adk_memory` | ADK Memory連携用interface |
| `opensearch` | optional |
| `http` | external retriever API |

### 10.3 ToolRegistry

責務:

- static tool解決
- agent-specific tool解決
- `rag.search_knowledge` のRetriever注入
- unknown tool拒否
- disallowed tool拒否

### 10.4 SkillFactory

責務:

- `skills/*.yaml` / Agent Config内のskill refsを解決
- filesystem skill pathの安全検証
- `SKILL.md` の存在検証
- ADK SkillToolsetへの変換
- skillに渡すadditional_toolsのToolRegistry解決
- script executionの禁止制御

### 10.5 AgentFactory

責務:

- Agent ConfigからADK Agent objectを生成
- LLM Agent / Sequential / Parallel / Loop Agent生成
- instruction file読み込み
- resolved model profile注入
- `generate_content_config` 変換
- tools注入
- skill toolset注入
- sub_agents注入

### 10.6 RunnerRegistry

責務:

- `agent_id -> Runner` のlazy build
- `agent_id -> SessionService` の管理
- Agent tree構築
- Runner mode切替
  - `fake`
  - `recorded`
  - `adk_embedded`
  - `adk_http`

---

## 11. ADK統合仕様

### 11.1 ADK Embedded Runner

FastAPIプロセス内でADK Runnerを実行する。同期APIでは `run_async()` を最後までconsumeし、最終応答を返す。Streaming APIではeventをdomain eventに変換しながらSSEで返す。

### 11.2 ADK HTTP Runner

ADK API Serverを別プロセスで起動し、FastAPIからHTTP proxyする。PoCやADK標準API確認に利用する。

### 11.3 RunConfig

Agent runtime設定から以下を生成する。

- `streaming_mode`
- `max_llm_calls`
- speech / live options, if enabled

### 11.4 Event Mapper

ADK Eventは外部公開しない。以下のdomain eventへ変換する。

```text
run.started
message.delta
message.completed
tool.call.started
tool.call.completed
rag.search.started
rag.search.completed
usage.reported
run.completed
run.failed
```

---

## 12. RAG仕様

### 12.1 RAGの3分類

| 種類 | 実装 | 用途 |
|---|---|---|
| Optional RAG | `rag.search_knowledge` tool | Agentが必要に応じて検索 |
| Required RAG | Application層pre-retrieval | 社内規約、契約、FAQなど根拠必須 |
| Memory | ADK Memory / Memory Retriever | 長期記憶、ユーザー嗜好 |

### 12.2 RAG Tool

Agentごとの `rag.retriever` に応じてToolを生成する。

LLMがtenant filterを決めてはいけない。`principal` から `tenant_id`, `roles`, `user_id` を取得し、Retriever内部で必ずfilterする。

### 12.3 Hybrid Retriever

対応strategy:

- `weighted_merge`
- `priority`

Hybrid結果は重複chunkを `(document_id, chunk_id)` でdeduplicateする。

### 12.4 Citation

RAG回答では可能な限りcitationを返す。

```json
{
  "source_id": "internal_faq",
  "document_id": "doc_123",
  "chunk_id": "chunk_02",
  "title": "経費精算ルール",
  "uri": "kb://internal_faq/doc_123"
}
```
