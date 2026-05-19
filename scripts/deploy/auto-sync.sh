#!/usr/bin/env bash
# YI-Chronos auto-sync daemon.
#
# Watches code dirs on Mac. When changes idle for DEBOUNCE seconds, runs
# `git add -A && git commit && git push` — which triggers GHA CI auto-deploy.
#
# Run via:
#   scripts/deploy/auto-sync-start.sh  (background)
#   scripts/deploy/auto-sync-stop.sh
# or directly (foreground, for debugging):
#   scripts/deploy/auto-sync.sh
#
# Tunables (env vars):
#   DEBOUNCE_SECONDS — idle window before committing (default 120)
#   AUTO_SYNC_LOG    — log file path
set -uo pipefail

REPO="/Users/ozvietnamdesktop/Desktop/yi"
DEBOUNCE="${DEBOUNCE_SECONDS:-120}"
LOG="${AUTO_SYNC_LOG:-$HOME/.local/state/yi-chronos-autosync.log}"

mkdir -p "$(dirname "$LOG")"

log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

commit_and_push() {
  cd "$REPO" || return 1

  # Quick check: anything changed?
  if git diff --quiet && git diff --cached --quiet && \
     [ -z "$(git ls-files --others --exclude-standard)" ]; then
    return
  fi

  git add -A 2>>"$LOG"
  if git diff --cached --quiet; then
    return  # nothing staged after .gitignore filter
  fi

  local count files msg
  count=$(git diff --cached --name-only | wc -l | tr -d ' ')
  files=$(git diff --cached --name-only | head -3 | tr '\n' ' ' | sed 's/ $//')
  msg="auto-sync $(date +'%Y-%m-%d %H:%M') · ${count} file(s)"

  if ! git commit -m "$msg" >>"$LOG" 2>&1; then
    log "commit failed"
    return 1
  fi
  log "committed ${count} files: ${files}"

  if git push >>"$LOG" 2>&1; then
    log "pushed → CI deploy triggered"
  else
    log "push failed (see log)"
  fi
}

log "==================== daemon starting (debounce ${DEBOUNCE}s) ===================="

# Watch only code + config dirs. Skip data/, .venv/, node_modules/ etc.
# fswatch outputs one line per change event; read drains the queue.
fswatch -o \
  --exclude='\.pyc$' \
  --exclude='__pycache__' \
  --exclude='\.DS_Store' \
  --exclude='node_modules' \
  --exclude='\.venv' \
  --exclude='dist' \
  "$REPO/api" \
  "$REPO/core" \
  "$REPO/engine" \
  "$REPO/collectors" \
  "$REPO/client/webapp/src" \
  "$REPO/client/webapp/package.json" \
  "$REPO/scripts" \
  "$REPO/docs" \
  "$REPO/Dockerfile" \
  "$REPO/docker-compose.prod.yml" \
  "$REPO/.github/workflows" \
  "$REPO/requirements.txt" \
  "$REPO/.gitignore" \
  "$REPO/.dockerignore" \
  2>/dev/null \
| while read -r _; do
    # Drain any further events within the debounce window. -t timeout means
    # "wait at most N seconds for next line; exit loop if none arrives" —
    # giving us a quiet-period detection.
    while read -t "$DEBOUNCE" -r _; do :; done
    commit_and_push
  done
