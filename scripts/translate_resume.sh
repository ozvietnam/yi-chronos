#!/bin/bash
# Resume translation: fire pages 301-588 with API health check between batches.
# Robust to API restart (waits + retries if API down).

set -u
BOOK_ID="shao-yong-shao-yuan-heng-etc-z-library-sk-1lib-sk-z-lib-sk"
BATCH_SIZE=50
DELAY=1.5
RETRIES=3
LOG_DIR=/tmp/translate-resume
mkdir -p $LOG_DIR

echo "=== Translation RESUME pages 301-588 ==="
echo "Started: $(date +%H:%M:%S)"
echo

# Wait for API up before each batch
wait_for_api() {
  local n=0
  while [ $n -lt 60 ]; do
    if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
      return 0
    fi
    n=$((n + 1))
    sleep 5
  done
  return 1
}

start=301
batch_num=1
while [ $start -le 588 ]; do
  end=$((start + BATCH_SIZE - 1))
  [ $end -gt 588 ] && end=588

  echo "[$(date +%H:%M:%S)] Batch $batch_num: pages $start-$end"

  if ! wait_for_api; then
    echo "  ❌ API not responding after 5 min — aborting"
    exit 1
  fi

  curl -s -X POST "http://localhost:8000/api/yi-publishing/books/$BOOK_ID/auto-batch" \
    -H "Content-Type: application/json" \
    --max-time 7200 \
    -d "{\"start_page\": $start, \"end_page\": $end, \"overwrite\": false, \"delay_seconds\": $DELAY, \"retry_on_429\": $RETRIES, \"allow_paid_fallback\": true}" \
    > $LOG_DIR/batch-${batch_num}.json 2>&1

  if [ -s $LOG_DIR/batch-${batch_num}.json ]; then
    python3 -c "
import json
try:
    d = json.load(open('$LOG_DIR/batch-${batch_num}.json'))
    s = d.get('summary', {})
    print(f'  Lines: {s.get(\"total_lines_translated\", 0)}/{s.get(\"total_lines_attempted\", 0)} | FIT: {s.get(\"avg_fit_score\", 0)}% | Cost: \${s.get(\"total_cost_usd\", 0):.4f} | Time: {s.get(\"batch_elapsed_seconds\", 0)}s')
except Exception as e:
    print(f'  Parse error: {e}')
"
  else
    echo "  ⚠ Empty response — API may have restarted"
    sleep 30
  fi

  start=$((end + 1))
  batch_num=$((batch_num + 1))
done

echo
echo "=== Done at $(date +%H:%M:%S) ==="
