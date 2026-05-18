# v1 Release Checklist

- [ ] 全テスト成功: `uv run --with nox nox -s test`
- [ ] 型チェック成功: `uv run --with nox nox -s typing`
- [ ] Lint成功: `uv run --with nox nox -s lint`
- [ ] セキュリティチェック成功: `uv run --with nox nox -s security`
- [ ] OpenAPI出力確認: `uv run python scripts/export_openapi.py --output openapi.json`
- [ ] スモークテスト成功: `scripts/smoke_test.sh`
- [ ] `tasks.md` の Epic 11 / 12 が `DONE`
- [ ] 変更履歴に反映（必要時）
