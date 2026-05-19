#!/usr/bin/env bash
# Stop auto-sync daemon if running.
set -euo pipefail

PIDFILE="$HOME/.local/state/yi-chronos-autosync.pid"

if [ ! -f "$PIDFILE" ]; then
  echo "Not running (no pidfile)."
  exit 0
fi

PID=$(cat "$PIDFILE")
if kill -0 "$PID" 2>/dev/null; then
  # Kill the daemon process and all child fswatch processes
  pkill -P "$PID" 2>/dev/null || true
  kill "$PID" 2>/dev/null || true
  sleep 1
  if kill -0 "$PID" 2>/dev/null; then
    kill -9 "$PID" 2>/dev/null || true
  fi
  echo "✓ stopped (PID $PID)"
else
  echo "Stale pidfile — process $PID not running"
fi
rm -f "$PIDFILE"
