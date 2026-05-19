#!/usr/bin/env bash
# Smoke test cho POST /api/luc-hao/cast (không cần trình khác chiếm :8000).
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
if [ ! -d ".venv" ]; then
  echo "Thiếu .venv trong $ROOT_DIR"
  exit 1
fi
# shellcheck source=/dev/null
source .venv/bin/activate
PORT="${VERIFY_PORT:-8766}"
python -m uvicorn api.main:app --host 127.0.0.1 --port "${PORT}" &
PID=$!
cleanup() {
  kill "${PID}" 2>/dev/null || true
}
trap cleanup EXIT
sleep 1
CODE="$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://127.0.0.1:${PORT}/api/luc-hao/cast" \
  -H "Content-Type: application/json" \
  -d '{"question_text":"smoke-verify","timezone":"Asia/Ho_Chi_Minh","interaction_signal":{"hold_duration_ms":1,"move_event_count":1,"path_length_px":1,"release_timestamp_ms":1}}')"
if [[ "${CODE}" != "200" ]]; then
  echo "verify-luc-hao-backend: expected HTTP 200, got ${CODE}"
  exit 1
fi
echo "verify-luc-hao-backend: OK (HTTP ${CODE} @ port ${PORT})"
