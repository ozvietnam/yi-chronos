#!/usr/bin/env bash
# Start auto-sync daemon in background. Idempotent — won't double-start.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAEMON="$SCRIPT_DIR/auto-sync.sh"
PIDFILE="$HOME/.local/state/yi-chronos-autosync.pid"
LOG="$HOME/.local/state/yi-chronos-autosync.log"

mkdir -p "$(dirname "$PIDFILE")"

# Already running?
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "Already running (PID $(cat "$PIDFILE")). Tail log: $LOG"
  exit 0
fi

# Spawn in background
nohup bash "$DAEMON" >>"$LOG" 2>&1 &
echo $! > "$PIDFILE"

sleep 1
if kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "✓ auto-sync started (PID $(cat "$PIDFILE"))"
  echo "  log: $LOG"
  echo "  stop: $SCRIPT_DIR/auto-sync-stop.sh"
else
  echo "✗ failed to start (see $LOG)"
  exit 1
fi
