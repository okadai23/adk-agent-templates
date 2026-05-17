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
  - 検証: `pytest -q tests/unit/config/test_model_profiles.py tests/unit/config/test_loader.py`
- [ ] [TODO] TASK-009: GenerateContentConfig変換実装

## Epic 3. Agent Catalog / Agent Config

- [ ] [TODO] TASK-010: Agent Catalog Pydantic Model実装
- [ ] [TODO] TASK-011: Agent Config Pydantic Model実装
- [ ] [TODO] TASK-012: Agent Graph Validator実装

## Epic 4. Knowledge Source Factory / RAG

- [ ] [TODO] TASK-013: Knowledge Config Pydantic Model実装
- [ ] [TODO] TASK-014: KnowledgeRetriever Port実装
- [ ] [TODO] TASK-015: KnowledgeSourceFactory実装
- [ ] [TODO] TASK-016: FakeKnowledgeRetriever実装
- [ ] [TODO] TASK-017: HybridKnowledgeRetriever実装
- [ ] [TODO] TASK-018: RAG Tool Factory実装

## Epic 5. Tool / Skill Factory

- [ ] [TODO] TASK-019: ToolRegistry実装
- [ ] [TODO] TASK-020: Filesystem SkillFactory実装
- [ ] [TODO] TASK-021: Skill API実装

## Epic 6. ADK Agent Factory / Runner

- [ ] [TODO] TASK-022: ADK AgentFactory実装
- [ ] [TODO] TASK-023: EventMapper実装
- [ ] [TODO] TASK-024: ADK Embedded Runner実装
- [ ] [TODO] TASK-025: ADK HTTP Runner実装
- [ ] [TODO] TASK-026: RunnerRegistry実装

## Epic 7. API / Use Cases

- [ ] [TODO] TASK-027: Agent一覧API実装
- [ ] [TODO] TASK-028: Sync Run API実装
- [ ] [TODO] TASK-029: Streaming Run API実装
- [ ] [TODO] TASK-030: Async Job API基礎実装

## Epic 8. Auth / Security

- [ ] [TODO] TASK-031: API Key Auth実装
- [ ] [TODO] TASK-032: JWT Verifier骨格実装
- [ ] [TODO] TASK-033: Authorization Policy実装

## Epic 9. Observability

- [ ] [TODO] TASK-034: Request ID / Access Log Middleware実装
- [ ] [TODO] TASK-035: OpenTelemetry初期化実装
- [ ] [TODO] TASK-036: Metrics実装
- [ ] [TODO] TASK-037: ADK Callback Telemetry実装

## Epic 10. API Spec / Mock / Testing

- [ ] [TODO] TASK-038: OpenAPI Export Script実装
- [ ] [TODO] TASK-039: FakeAgentRunner実装
- [ ] [TODO] TASK-040: RecordedAgentRunner実装
- [ ] [TODO] TASK-041: Schemathesis Contract Test実装
- [ ] [TODO] TASK-042: Config Property Tests実装
- [ ] [TODO] TASK-043: RAG Property Tests実装

## Epic 11. Documentation / Examples

- [ ] [TODO] TASK-044: README作成
- [ ] [TODO] TASK-045: Example Config一式作成
- [ ] [TODO] TASK-046: Smoke Test Script作成

## Epic 12. MVP Completion

- [ ] [TODO] TASK-047: MVP統合テスト
- [ ] [TODO] TASK-048: v1 Release Checklist作成

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
