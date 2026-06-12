#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/ozvietnamdesktop/Desktop/yi"
LOG_DIR="$ROOT/data/research/tiktok_transcripts/tuvibonba/logs"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
mkdir -p "$LOG_DIR"

cd "$ROOT"

{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S %z') update start ==="
  python3 scripts/tiktok_transcribe_research.py \
    'https://www.tiktok.com/@tuvibonba?lang=vi-VN' \
    --all \
    --subs \
    --combine
  echo "=== $(date '+%Y-%m-%d %H:%M:%S %z') update done ==="
} >> "$LOG_DIR/weekly_update.log" 2>&1
