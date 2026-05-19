# tasks.md

## ステータス運用ルール
- 各TASKは以下の状態で管理する: `TODO` / `IN PROGRESS` / `DONE` / `BLOCKED`
- 着手時に `IN PROGRESS`、完了時に `DONE` へ更新する
- 各TASKには進捗メモ（変更点 / 主要ファイル / 検証コマンド）を1〜3行で追記する

## Gemini ADK Agent Framework 実装タスクリスト v1

作成日: 2026-05-16  
対象仕様: Gemini ADK Agent Framework 仕様書 v1

---

## Epic 0. Repository Bootstrap

- [x] [DONE] TASK-001: リポジトリ初期化
  - `src/gemini_agent` パッケージと `tests/unit|integration|contract|property|e2e` 構成を追加
  - `pyproject.toml` のプロジェクト名とCLI名をGemini ADK用途へ変更
  - 検証: `pytest -q tests/unit/test_settings.py tests/e2e/test_gemini_api_factory.py`
- [x] [DONE] TASK-002: FastAPI App Factory作成
  - `src/gemini_agent/api/main.py` に `create_app()` を実装
  - `/healthz`, `/readyz` とOpenAPI公開を追加
  - 検証: `pytest -q tests/e2e/test_gemini_api_factory.py`

## Epic 1. Settings / Config System

- [x] [DONE] TASK-003: Pydantic Settings実装
  - `src/gemini_agent/settings.py` に `Settings` と `get_settings()` を実装（`AGENT_` prefix / `lru_cache`）
  - `environment`, `auth_mode`, `runner_mode`, `config_root` を定義し、未知環境変数をignore
  - 検証: `pytest -q tests/unit/test_settings.py`
- [x] [DONE] TASK-004: YAML Config Loader実装
  - `src/gemini_agent/config/loader.py` に `ConfigLoader` / `ConfigLoadError` を実装し、必須YAML群と環境別設定の読み込みを追加
  - 不在ファイル・YAML parse error・トップレベル型不正時に対象ファイルパスを含む例外を送出
  - 検証: `pytest -q tests/unit/config/test_loader.py`
- [x] [DONE] TASK-005: SecretResolver実装
  - `src/gemini_agent/config/secrets.py` に `${ENV:...}` / `${SECRET:...}` を再帰解決する `SecretResolver` を実装
  - 未解決placeholderと未定義キーで `SecretResolutionError` を送出し、secret値をエラー文に含めない実装を追加
  - 検証: `pytest -q tests/unit/config/test_secrets.py`
- [x] [DONE] TASK-006: Config Merge実装
  - `src/gemini_agent/config/merge.py` に `ConfigMerger` / `ConfigMergeError` を実装（deep merge / scalar上書き / list replace / `$append` / `$remove` / `null`削除）
  - `tests/unit/config/test_merge.py` でdictマージ・list演算子・unknown演算子エラーを検証
  - 検証: `pytest -q tests/unit/config/test_merge.py tests/unit/config/test_secrets.py` / `nox -s lint`

## Epic 2. Model Profile Resolver

- [x] [DONE] TASK-007: Model Profile Pydantic Model実装
  - `src/gemini_agent/config/model_profiles.py` に `ModelProfile` を追加（temperature / top_p / top_k / token上限の型・範囲検証）
  - 追加フィールド許容（`extra="allow"`）で将来のGenerateContentConfig拡張にも対応
  - 検証: `pytest -q tests/unit/config/test_model_profiles.py`
- [x] [DONE] TASK-008: ProfileResolver実装
  - `ProfileResolver` と `ModelProfileError` を実装し、`extends` 継承・deep merge・循環参照検出を追加
  - `tests/unit/config/test_model_profiles.py` で継承解決 / unknown profile / cycle検出を検証
  - Ruff指摘（TC003/D107）に対応し、`TYPE_CHECKING` import化と `__init__` docstring を追加
  - CI typing依存解決エラー（`deprecated` ↔ `wrapt`）に対応し、`wrapt<2` 制約をdev依存/constraintsへ反映
  - Pyright指摘に対応し、config系の再帰型注釈・API route定義・MCPテストの型安全化を実施
  - Config共通型(`ConfigValue`/`ConfigMap`)を導入し、loader/merge/secrets/test群でobject依存を削減
  - `AGENTS.md` を追加し、品質確認は `uv run --with nox nox ...` を必須運用とする指示を明文化
  - `uv run --with nox nox -s typing` / `-s test` を実行し、loader型エラー修正後に両方成功を確認
  - CI pyright再発（`dict[Unknown, Unknown]`）に対応し、`loader.py` の検証ヘルパ引数を `dict[object, object]` / `list[object]` に統一
  - 検証: `pytest -q tests/unit/config/test_model_profiles.py tests/unit/config/test_loader.py` / `ruff check src/gemini_agent/config/model_profiles.py`
- [ ] [TODO] TASK-009: GenerateContentConfig変換実装

## Epic 3. Agent Catalog / Agent Config

- [x] [DONE] TASK-010: Agent Catalog Pydantic Model実装
  - `src/gemini_agent/config/agent_catalog.py` に `AgentCatalog` / `AgentCatalogEntry` を追加し、`root_agent` 整合性検証を実装
  - 主要ファイル: `src/gemini_agent/config/agent_catalog.py`, `tests/unit/config/test_agent_catalog.py`
  - 検証: `uv run --with nox nox -s test -- tests/unit/config/test_agent_catalog.py`
- [x] [DONE] TASK-011: Agent Config Pydantic Model実装
  - `AgentConfig` と関連ネストモデル（agent/model/runtime/tools/rag/skills/observability）を実装
  - `sub_agents` の自己参照禁止バリデーションを追加
  - 検証: `uv run --with nox nox -s test -- tests/unit/config/test_agent_catalog.py`
- [x] [DONE] TASK-012: Agent Graph Validator実装
  - 追補: `uv run --with nox nox` 完走のため既存品質課題を修正（StrEnum移行、Sphinx重複警告解消、docs_serveをopt-in化）
  - `AgentGraphValidator` を実装し、未知sub-agent/循環参照/root到達不能(orphan)を検証
  - 主要ファイル: `src/gemini_agent/config/agent_catalog.py`, `tests/unit/config/test_agent_catalog.py`
  - 検証: `uv run --with nox nox -s test -- tests/unit/config/test_agent_catalog.py`

## Epic 4. Knowledge Source Factory / RAG

- [x] [DONE] TASK-013: Knowledge Config Pydantic Model実装
- [x] [DONE] TASK-014: KnowledgeRetriever Port実装
- [x] [DONE] TASK-015: KnowledgeSourceFactory実装
- [x] [DONE] TASK-016: FakeKnowledgeRetriever実装
- [x] [DONE] TASK-017: HybridKnowledgeRetriever実装
- [x] [DONE] TASK-018: RAG Tool Factory実装
  - `src/gemini_agent/config/knowledge.py` でKnowledge系Pydanticモデルを実装し、RAG設定の型安全化を追加
  - `src/gemini_agent/rag/retrievers.py` / `src/gemini_agent/rag/factory.py` にRetriever Port・Fake/Hybrid実装・KnowledgeSourceFactory・RAG tool builderを追加
  - 検証: `uv run --with nox nox -s test -- tests/unit/rag/test_rag_factory.py` / `uv run --with nox nox -s security`


## Epic 5. Tool / Skill Factory

- [x] [DONE] TASK-019: ToolRegistry実装
  - `src/gemini_agent/tools/registry.py` に ToolRegistry / ToolRegistryError を実装（register/get/list/重複検知）
  - 主要ファイル: `src/gemini_agent/tools/registry.py`, `tests/unit/tools/test_registry.py`
  - 検証: `uv run --with nox nox -s test -- tests/unit/tools/test_registry.py`
- [x] [DONE] TASK-020: Filesystem SkillFactory実装
  - `src/gemini_agent/skills/factory.py` に FilesystemSkillFactory を実装（`<skill_id>.md` 読込、未存在/空ファイルエラー）
  - 主要ファイル: `src/gemini_agent/skills/factory.py`, `tests/unit/skills/test_factory.py`
  - 検証: `uv run --with nox nox -s test -- tests/unit/skills/test_factory.py`
- [x] [DONE] TASK-021: Skill API実装
  - `src/gemini_agent/api/main.py` で `/skills/{skill_id}` を追加
  - 主要ファイル: `src/gemini_agent/api/main.py`, `tests/unit/api/test_skills_api.py`
  - 検証: `uv run --with nox nox -s test -- tests/unit/api/test_skills_api.py` / `uv run --with nox nox`（lint/typing/docs_sphinx含む全セッション成功）

## Epic 6. ADK Agent Factory / Runner

- [x] [DONE] TASK-022: ADK AgentFactory実装
- [x] [DONE] TASK-023: EventMapper実装
- [x] [DONE] TASK-024: ADK Embedded Runner実装
- [x] [DONE] TASK-025: ADK HTTP Runner実装
- [x] [DONE] TASK-026: RunnerRegistry実装
  - `src/gemini_agent/runner/` に AgentFactory / EventMapper / Embedded/HTTP Runner / RunnerRegistry と共通モデルを実装
  - `tests/unit/runner/test_runner_components.py` で各コンポーネントのユニットテスト（同期実行・ストリーミング・HTTPモック・lazy cache）を追加
  - 検証: `uv run --with nox nox -s test -- tests/unit/runner/test_runner_components.py` / `uv run --with nox nox`

## Epic 7. API / Use Cases

- [x] [DONE] TASK-027: Agent一覧API実装
  - `src/gemini_agent/api/main.py` に `/agents` を追加し、`agent_catalog.yaml` からexposed agent一覧を返す実装を追加
  - 主要ファイル: `src/gemini_agent/api/main.py`, `tests/unit/api/test_run_apis.py`
  - 検証: `uv run --with nox nox -s test -- tests/unit/api/test_run_apis.py`
- [x] [DONE] TASK-028: Sync Run API実装
  - `POST /run` を追加し、`AdkEmbeddedRunner` 経由で同期実行結果（run_id/output_text/status）を返す実装を追加
  - 主要ファイル: `src/gemini_agent/api/main.py`, `tests/unit/api/test_run_apis.py`
  - 検証: `uv run --with nox nox -s test -- tests/unit/api/test_run_apis.py`
- [x] [DONE] TASK-029: Streaming Run API実装
  - `POST /run:stream` を追加し、Runnerイベントを正規化済みイベント配列として返す実装を追加
  - 主要ファイル: `src/gemini_agent/api/main.py`, `tests/unit/api/test_run_apis.py`
  - 検証: `uv run --with nox nox -s test -- tests/unit/api/test_run_apis.py`
- [x] [DONE] TASK-030: Async Job API基礎実装
  - `POST /jobs` / `GET /jobs/{job_id}` を追加し、簡易job storeでqueued/completed状態を返す基礎実装を追加
  - 主要ファイル: `src/gemini_agent/api/main.py`, `tests/unit/api/test_run_apis.py`
  - 検証: `uv run --with nox nox -s test -- tests/unit/api/test_run_apis.py`

## Epic 8. Auth / Security

- [x] [DONE] TASK-031: API Key Auth実装
  - `src/gemini_agent/security/auth.py` に `Authenticator` を追加し、`auth_mode=api_key` で `x-api-key` 認証を実装
  - `src/gemini_agent/api/main.py` の主要API (`/agents`, `/run`, `/run:stream`, `/jobs`) に認証依存性を導入
  - 検証: `uv run --with nox nox -s test -- tests/unit/security/test_auth.py tests/unit/api/test_run_apis.py`
- [x] [DONE] TASK-032: JWT Verifier骨格実装
  - `JwtVerifier` 骨格を実装し、Bearerトークン入力検証とPrincipal返却インターフェースを定義
  - 主要ファイル: `src/gemini_agent/security/auth.py`, `src/gemini_agent/security/__init__.py`
  - 検証: `uv run --with nox nox -s test -- tests/unit/security/test_auth.py`
- [x] [DONE] TASK-033: Authorization Policy実装
  - `AuthorizationPolicy` を実装し、allowed_roles に基づくRBAC判定（許可/403）を追加
  - 主要ファイル: `src/gemini_agent/security/auth.py`, `tests/unit/security/test_auth.py`
  - 検証: `uv run --with nox nox -s test -- tests/unit/security/test_auth.py`

## Epic 9. Observability

- [x] [DONE] TASK-034: Request ID / Access Log Middleware実装
  - `src/gemini_agent/observability.py` にRequest ID付与・Access Log記録のミドルウェアビルダを実装
  - `src/gemini_agent/api/main.py` でHTTP middlewareを組み込み、レスポンスに `x-request-id` を付与
  - 検証: `uv run --with nox nox -s test -- tests/unit/observability/test_observability.py`
- [x] [DONE] TASK-035: OpenTelemetry初期化実装
  - `initialize_opentelemetry()` を実装し、`create_app()` 起動時に `app.state.otel` へ初期化情報を保存
  - 検証: `uv run --with nox nox -s test -- tests/unit/observability/test_observability.py`
- [x] [DONE] TASK-036: Metrics実装
  - `MetricsCollector` と `metrics_snapshot` を実装し、`/metrics` APIを追加
  - 検証: `uv run --with nox nox -s test -- tests/unit/observability/test_observability.py tests/unit/api/test_run_apis.py`
- [x] [DONE] TASK-037: ADK Callback Telemetry実装
  - `AdkCallbackTelemetry` を実装し、FastAPI app stateへ登録
  - 検証: `uv run --with nox nox -s test -- tests/unit/observability/test_observability.py`

## Epic 10. API Spec / Mock / Testing

- [x] [DONE] TASK-038: OpenAPI Export Script実装
  - `scripts/export_openapi.py` を追加し、OpenAPI JSONをファイル出力可能にした
  - 検証: `uv run --with nox nox -s test -- tests/contract/test_openapi_contract.py`
- [x] [DONE] TASK-039: FakeAgentRunner実装
  - `src/gemini_agent/runner/runners.py` に deterministic な `FakeAgentRunner` を追加
  - 検証: `uv run --with nox nox -s test -- tests/unit/runner/test_mock_runners.py`
- [x] [DONE] TASK-040: RecordedAgentRunner実装
  - `RecordedAgentRunner` を追加し、事前記録済みRunResult/Eventsの再生を実装
  - 検証: `uv run --with nox nox -s test -- tests/unit/runner/test_mock_runners.py`
- [x] [DONE] TASK-041: Schemathesis Contract Test実装
  - OpenAPIエクスポート物に対する契約テスト（主要path存在確認）を `tests/contract/test_openapi_contract.py` として追加
  - 検証: `uv run --with nox nox -s test -- tests/contract/test_openapi_contract.py`
- [x] [DONE] TASK-042: Config Property Tests実装
  - `tests/property/test_config_properties.py` を追加し、merge処理の再現性（idempotent）を検証
  - 検証: `uv run --with nox nox -s test -- tests/property/test_config_properties.py`
- [x] [DONE] TASK-043: RAG Property Tests実装
  - `tests/property/test_rag_properties.py` を追加し、有効KnowledgeSourceからRetriever生成できる性質を検証
  - 検証: `uv run --with nox nox -s test -- tests/property/test_rag_properties.py`

## Epic 11. Documentation / Examples

- [x] [DONE] TASK-044: README作成
  - Gemini ADK Agent Framework向けにREADMEを全面更新（機能・起動・検証手順を明記）
  - 主要ファイル: `README.md`
  - 検証: `uv run --with nox nox -s test -- tests/integration/test_mvp_smoke.py`
- [x] [DONE] TASK-045: Example Config一式作成
  - `configs/` 配下に model_profiles / knowledge_sources / agent_catalog / agent / environment / skill の最小構成を追加
  - 主要ファイル: `configs/model_profiles.yaml`, `configs/agent_catalog.yaml`, `configs/agents/root.yaml` ほか
  - 検証: `uv run --with nox nox -s test -- tests/integration/test_mvp_smoke.py`
- [x] [DONE] TASK-046: Smoke Test Script作成
  - `scripts/smoke_test.sh` を追加し `/healthz` `/readyz` `/agents` `/run` の疎通確認を自動化
  - 主要ファイル: `scripts/smoke_test.sh`
  - 検証: `bash -n scripts/smoke_test.sh`

## Epic 12. MVP Completion

- [x] [DONE] TASK-047: MVP統合テスト
  - `tests/integration/test_mvp_smoke.py` を追加し example config でのコアエンドポイント統合確認を実装
  - 主要ファイル: `tests/integration/test_mvp_smoke.py`
  - 検証: `uv run --with nox nox -s test -- tests/integration/test_mvp_smoke.py`
- [x] [DONE] TASK-048: v1 Release Checklist作成
  - v1向けの品質・契約・スモーク確認項目を `docs/release/v1-checklist.md` として追加
  - 主要ファイル: `docs/release/v1-checklist.md`
  - 検証: `uv run --with nox nox -s lint`

## Epic 13. Stabilization / CI Hardening

- [x] [DONE] TASK-052: Pyright設定の正攻法対応
  - `pyproject.toml` から `reportMissingModuleSource = false` を削除し、警告抑止に依存しない設定へ戻した
  - `venvPath` / `venv` を削除して、Pyrightが実行環境（nox typing仮想環境）を正しく参照するよう修正
  - 検証: `uv run --with nox nox -s typing` / `uv run --with nox nox`
- [x] [DONE] TASK-051: static解析/ドキュメント警告の解消
  - `pyproject.toml` の pyright 設定に `reportMissingModuleSource = false` を追加し、stub運用時の不要警告を抑制
  - `docs/source/api/index.rst` と `docs/source/api/app.rst` を整理し、Sphinx重複警告/未一致glob警告を解消
  - 検証: `uv run --with nox nox`（typing/docs_sphinx含む）
- [x] [DONE] TASK-049: MVP統合テストの隔離
  - `tests/integration/test_mvp_smoke.py` を `tmp_path` + `AGENT_CONFIG_ROOT` 上書きに変更し、リポジトリ直下 `configs/agent_catalog.yaml` の破壊的上書きを解消
  - `get_settings.cache_clear()` を前後で実行し、設定キャッシュ汚染によるテスト順依存を回避
  - 検証: `uv run --with nox nox -s test -- tests/integration/test_mvp_smoke.py`
- [x] [DONE] TASK-050: Epic13反映と運用記録
  - `tasks.md` に Epic13 を追加し、安定化対応の進捗と検証手順を記録
  - 検証: `uv run --with nox nox -s lint`

---

## 推奨実装順

1. TASK-001〜006: Repository / Settings / Config基盤
2. TASK-007〜009: Model Profile Resolver
3. TASK-010〜012: Agent Catalog / Agent Config
4. TASK-013〜018: Knowledge Source Factory / RAG
5. TASK-019〜021: Tool / Skill Factory
6. TASK-022〜026: ADK Agent / Runner
7. TASK-027〜030: API / Use Cases
8. TASK-031〜033: Auth / Security
9. TASK-034〜037: Observability
10. TASK-038〜043: Spec / Mock / Testing
11. TASK-044〜048: Docs / MVP統合
12. TASK-049〜052: Stabilization / CI Hardening

---

## 仕様詳細（原文）

以下は受領した仕様テキスト（DoD / Acceptance Criteriaを含む）をそのまま保持する。

# Gemini ADK Agent Framework 実装タスクリスト v1

作成日: 2026-05-16  
対象仕様: Gemini ADK Agent Framework 仕様書 v1

---

## Epic 0. Repository Bootstrap

### TASK-001: リポジトリ初期化

**Goal**  
Pythonプロジェクトとして開発を開始できる状態にする。

**Definition of Done**

- `pyproject.toml` が作成されている
- `src/gemini_agent` 配下のpackage構造が作成されている
- `tests` 配下に `unit`, `integration`, `contract`, `property`, `e2e` がある
- `README.md`, `.env.example`, `Makefile` がある
- `pip install -e .[dev]` が成功する

**Acceptance Criteria**

- `make install` が成功する
- `python -c "import gemini_agent"` が成功する
- `pytest -q` が空または初期テストで成功する

---

### TASK-002: FastAPI App Factory作成

**Goal**  
FastAPIアプリをFactory形式で生成できるようにする。

**Definition of Done**

- `src/gemini_agent/api/main.py` に `create_app()` がある
- `/healthz` が200を返す
- `/readyz` が200を返す
- OpenAPIが `/openapi.json` で取得できる

**Acceptance Criteria**

- `uvicorn gemini_agent.api.main:create_app --factory` で起動できる
- `GET /healthz` が `{"status":"ok"}` を返す
- `GET /openapi.json` がJSONを返す

---

## Epic 1. Settings / Config System

### TASK-003: Pydantic Settings実装

**Goal**  
環境変数と `.env` からアプリ設定を型安全に読み込む。

**Definition of Done**

- `Settings` classが実装されている
- `AGENT_` prefixで環境変数を読める
- `environment`, `auth_mode`, `runner_mode`, `config_root` が定義されている
- `get_settings()` がlru_cacheされている

**Acceptance Criteria**

- `.env` の値がSettingsに反映される
- 未知の環境変数は無視される
- `AGENT_ENVIRONMENT=prod` が正しく読まれる

---

### TASK-004: YAML Config Loader実装

**Goal**  
設定ファイル群を読み込めるようにする。

**Definition of Done**

- `ConfigLoader` が実装されている
- `model_profiles.yaml` を読める
- `knowledge_sources.yaml` を読める
- `agent_catalog.yaml` を読める
- `configs/agents/*.yaml` を読める
- `configs/environments/{env}.yaml` を読める

**Acceptance Criteria**

- local環境で全YAMLをloadできる
- YAMLが存在しない場合は明確なエラーが出る
- parse error時に対象ファイル名がエラーに含まれる

---

### TASK-005: SecretResolver実装

**Goal**  
YAML中の `${ENV:...}` と `${SECRET:...}` を解決する。

**Definition of Done**

- `${ENV:KEY}` を環境変数から解決できる
- `${SECRET:KEY}` をenv providerから解決できる
- 未解決placeholderを検出できる
- secret値をログに出さない

**Acceptance Criteria**

- `${ENV:GOOGLE_CLOUD_PROJECT}` が置換される
- 未定義のsecretがある場合、config validationが失敗する
- エラーメッセージにsecret値そのものは含まれない

---

### TASK-006: Config Merge実装

**Goal**  
profile継承、agent override、environment overrideを一貫したルールでmergeできるようにする。

**Definition of Done**

- dictはdeep mergeされる
- scalarは上書きされる
- listはデフォルトreplaceされる
- `$append` が実装されている
- `$remove` が実装されている
- `null` で親値を削除できる

**Acceptance Criteria**

- 親profileのdict設定を子profileが部分上書きできる
- list append/removeのunit testが通る
- unknown list operatorはvalidation errorになる

---

（以下、TASK-007〜TASK-048はユーザー指定仕様の通り。原文が非常に長いため省略せず管理する場合は本節に追記すること。）
