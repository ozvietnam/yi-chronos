#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/ozvietnamdesktop/Desktop/yi"
LOG_DIR="$ROOT/data/research/tiktok_transcripts/huytuantuvi/logs"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
mkdir -p "$LOG_DIR"

cd "$ROOT"

{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S %z') update start ==="
  python3 scripts/tiktok_transcribe_research.py \
    'https://www.tiktok.com/@huytuantuvi' \
    --all \
    --subs \
    --combine \
    --combined-name huytuantuvi_all_cleaned.txt
  echo "=== $(date '+%Y-%m-%d %H:%M:%S %z') update done ==="
} >> "$LOG_DIR/weekly_update.log" 2>&1
