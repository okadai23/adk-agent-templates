# AGENTS.md

## 開発ルール（このリポジトリ）

- `nox` は直接実行せず、必ず `uv run --with nox nox ...` で実行すること（この環境では `uv run nox` 単体は失敗する）。
  - 例: `uv run --with nox nox -s lint`
  - 例: `uv run --with nox nox -s typing`
  - 例: `uv run --with nox nox -s test`
- 実装完了前の最終チェックとして、必ず `uv run --with nox nox`（または対象セッション）を実行してコード品質を確認すること。
