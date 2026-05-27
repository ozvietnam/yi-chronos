#!/bin/bash
# Translate full book sequentially in 50-page batches
# Usage: bash scripts/translate_full_book.sh <book_id> <total_pages>

set -u
BOOK_ID="${1:-shao-yong-shao-yuan-heng-etc-z-library-sk-1lib-sk-z-lib-sk}"
TOTAL_PAGES="${2:-588}"
BATCH_SIZE=50
DELAY=1.5
RETRIES=3
LOG_DIR=/tmp/translate-fullbook
mkdir -p $LOG_DIR

echo "=== Translate full book ==="
echo "Book: $BOOK_ID"
echo "Total pages: $TOTAL_PAGES"
echo "Batch size: $BATCH_SIZE"
echo "Started: $(date +%H:%M:%S)"
echo

batch_num=1
start=1
while [ $start -le $TOTAL_PAGES ]; do
  end=$((start + BATCH_SIZE - 1))
  [ $end -gt $TOTAL_PAGES ] && end=$TOTAL_PAGES

  echo "[$(date +%H:%M:%S)] Batch $batch_num: pages $start-$end"

  curl -s -X POST "http://localhost:8000/api/yi-publishing/books/$BOOK_ID/auto-batch" \
    -H "Content-Type: application/json" \
    --max-time 3600 \
    -d "{\"start_page\": $start, \"end_page\": $end, \"overwrite\": false, \"delay_seconds\": $DELAY, \"retry_on_429\": $RETRIES, \"allow_paid_fallback\": true}" \
    > $LOG_DIR/batch-${batch_num}.json 2>&1

  # Parse summary
  if [ -s $LOG_DIR/batch-${batch_num}.json ]; then
    python3 -c "
import json
try:
    d = json.load(open('$LOG_DIR/batch-${batch_num}.json'))
    s = d.get('summary', {})
    print(f'  Lines: {s.get(\"total_lines_translated\", 0)}/{s.get(\"total_lines_attempted\", 0)} | FIT: {s.get(\"avg_fit_score\", 0)}% | Cost: \${s.get(\"total_cost_usd\", 0):.4f} | Time: {s.get(\"batch_elapsed_seconds\", 0)}s')
except Exception as e:
    print(f'  Error parsing: {e}')
"
  fi

  start=$((end + 1))
  batch_num=$((batch_num + 1))
done

echo
echo "=== Done at $(date +%H:%M:%S) ==="
echo "Total batches: $((batch_num - 1))"
echo "Logs in: $LOG_DIR/"
