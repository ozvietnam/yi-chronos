#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_HOST="127.0.0.1"
API_PORT="8000"
WEB_HOST="127.0.0.1"
WEB_PORT="5173"

cd "$ROOT_DIR"

# Load local environment overrides (API keys, etc.) if present.
if [ -f ".env.local" ]; then
  set -a
  # shellcheck source=/dev/null
  . ".env.local"
  set +a
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Missing .venv. Run setup first:"
  echo "  python3 -m venv .venv && source .venv/bin/activate && python -m pip install -r requirements.txt"
  exit 1
fi

if lsof -nP -iTCP:"$API_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $API_PORT is already in use. Stop the other process (often lsof -nP -iTCP:$API_PORT -sTCP:LISTEN) or:"
  echo "  1) Run YI-CHRONOS on another port:  API_PORT=8010 python -m uvicorn api.main:app --host 127.0.0.1 --port 8010"
  echo "  2) In client/webapp/.env.development.local set:  VITE_DEV_PROXY_TARGET=http://127.0.0.1:8010"
  echo "  3) Restart npm run dev."
  exit 1
fi

if lsof -nP -iTCP:"$WEB_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $WEB_PORT is already in use. Stop existing process first."
  exit 1
fi

cleanup() {
  if [ -n "${BACKEND_PID:-}" ] && kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
  if [ -n "${FRONTEND_PID:-}" ] && kill -0 "$FRONTEND_PID" >/dev/null 2>&1; then
    kill "$FRONTEND_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

echo "Starting backend: http://$API_HOST:$API_PORT"
source .venv/bin/activate
python -m uvicorn api.main:app --host "$API_HOST" --port "$API_PORT" &
BACKEND_PID=$!

echo "Starting frontend: http://$WEB_HOST:$WEB_PORT"
(
  cd client/webapp
  VITE_API_BASE="http://$API_HOST:$API_PORT" npm run dev -- --host "$WEB_HOST" --port "$WEB_PORT"
) &
FRONTEND_PID=$!

echo "YI-CHRONOS dev stack is running."
echo "Backend:  http://$API_HOST:$API_PORT"
echo "Frontend: http://$WEB_HOST:$WEB_PORT"
echo "Press Ctrl+C to stop both."

while true; do
  if ! kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    echo "Backend exited."
    break
  fi
  if ! kill -0 "$FRONTEND_PID" >/dev/null 2>&1; then
    echo "Frontend exited."
    break
  fi
  sleep 1
done
