#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

curl -fsS "$BASE_URL/healthz" > /dev/null
curl -fsS "$BASE_URL/readyz" > /dev/null
curl -fsS "$BASE_URL/agents" > /dev/null
curl -fsS -X POST "$BASE_URL/run" \
  -H 'content-type: application/json' \
  -d '{"agent_id":"root","input":"hello"}' > /dev/null

echo "Smoke test passed: $BASE_URL"
