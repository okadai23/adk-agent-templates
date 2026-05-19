# Skeleton Implementation Audit

作成日: 2026-05-19

## 対象
- `src/` 配下の実装コードを対象に、`NotImplementedError` や skeleton を示す記述を点検。

## 発見事項（要実装候補）

対象を `src/gemini_agent` 全体へ再点検（2026-05-19 追補）。

1. `src/gemini_agent/runner/ports.py`
   - `AgentRunner.run()` が `raise NotImplementedError`。
   - `AgentRunner.stream()` が `raise NotImplementedError`。
   - Protocol定義としては妥当だが、実体クラスが未実装のまま使われると実行時エラーになるため、呼び出し側で concrete runner を必須化するガードが必要。

2. `src/gemini_agent/security/auth.py`
   - `JwtVerifier` に `"JWT verifier skeleton."` という説明があり、現状は token 非空チェック後に固定Principalを返す最小実装。
   - 署名検証・iss/aud/exp検証・鍵ローテーション対応などの本実装が未着手。

## メモ（スケルトンではないが注意）
- `src/clean_interfaces/utils/logger.py` の `try/except` 内 `pass` は、OpenTelemetry未導入時のフォールバック用でありスケルトン実装ではない。

## 推奨フォローアップ
- TASK-009（GenerateContentConfig変換）と合わせて、Runner/Auth周りの未完了タスクを Epic 化して管理。
- JWT検証の受け入れ条件として、最低限以下を追加:
  - RS256/ES256 署名検証
  - `exp` / `nbf` / `iat` 検証
  - `iss` / `aud` の設定駆動バリデーション
  - 失敗時の監査ログ（秘密情報マスク）


3. `src/gemini_agent/observability.py`
   - `initialize_opentelemetry()` は `"provider placeholder"` と明記され、`{"service_name", "status"}` を返すのみ。
   - 実際のTracerProvider/MeterProvider初期化、Exporter設定、サンプリング設定は未実装。

4. `src/gemini_agent/rag/factory.py`
   - `KnowledgeSourceFactory.create()` は現状 `source.type == "fake"` のみ実装。
   - `vertex_ai_rag` / `http` など仕様で想定されるretriever種別は未実装（未対応typeで `ValueError`）。

5. `src/gemini_agent/runner/runners.py`
   - `AdkEmbeddedRunner` は入力テキストをそのまま返す簡易実装（実LLM呼び出しなし）。
   - `AdkHttpRunner` はHTTPプロキシの形はあるが、認証・リトライ・タイムアウト・ストリーム例外処理など運用要件が未整備。

## 除外（意図的なテスト/モック実装）
- `FakeAgentRunner` / `RecordedAgentRunner` はテスト用モックのためスケルトン扱いから除外。
- `runner/ports.py` の `NotImplementedError` はProtocol契約を明示する定型であり、単体では問題ない（具象実装未接続時のみ実行時に顕在化）。
