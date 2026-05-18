# Gemini ADK Agent Framework

Gemini ADK 互換のエージェント実行基盤（FastAPI + 設定駆動）です。

## 主な機能

- FastAPI App Factory (`create_app`) と API 群（`/healthz`, `/readyz`, `/agents`, `/run` など）
- YAML 設定ローダー（model profiles / knowledge sources / agent catalog / agents / environments）
- 認証モード（none / api_key / jwt 骨格）
- RAG Retriever / Tool Factory / Skill Factory
- Runner（embedded / http / fake / recorded）
- Observability（Request ID, access log, metrics, OTel初期化）

## クイックスタート

```bash
uv sync --extra dev
cp env.example .env
```

開発サーバ起動:

```bash
uv run uvicorn gemini_agent.api.main:create_app --factory --reload
```

主要エンドポイント確認:

```bash
curl -s http://127.0.0.1:8000/healthz
curl -s http://127.0.0.1:8000/agents
curl -s -X POST http://127.0.0.1:8000/run \
  -H 'content-type: application/json' \
  -d '{"agent_id":"root","input":"hello"}'
```

## 例示設定（Epic 11）

このリポジトリには最小構成の example config を同梱しています。

- `configs/model_profiles.yaml`
- `configs/knowledge_sources.yaml`
- `configs/agent_catalog.yaml`
- `configs/agents/root.yaml`
- `configs/environments/local.yaml`
- `configs/skills/welcome.md`

## スモークテスト

ローカル起動済みAPIに対して実行:

```bash
scripts/smoke_test.sh
# 必要に応じて BASE_URL を変更
BASE_URL=http://127.0.0.1:8000 scripts/smoke_test.sh
```

## テスト / 品質確認

> このリポジトリでは `nox` を直接実行せず、必ず `uv run --with nox nox ...` を使います。

```bash
uv run --with nox nox -s test
uv run --with nox nox -s typing
uv run --with nox nox -s lint
# 最終確認
uv run --with nox nox
```

## リリースチェック

v1 リリース時は `docs/release/v1-checklist.md` を利用してください。
