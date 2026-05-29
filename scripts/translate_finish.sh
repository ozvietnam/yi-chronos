#!/bin/bash
# Finish translation — fire batches covering pages 251-588 with overwrite=false
# API skips already-translated pages, only does missing ones.
# Includes API health check + reasonable timeouts.

set -u
BOOK_ID="shao-yong-shao-yuan-heng-etc-z-library-sk-1lib-sk-z-lib-sk"
DELAY=2.0
RETRIES=3
LOG_DIR=/tmp/translate-finish-$(date +%Y%m%d-%H%M%S)
mkdir -p $LOG_DIR

echo "=== Translation FINISH (cover all missing) ==="
echo "Log: $LOG_DIR"
echo "Started: $(date +%H:%M:%S)"
echo

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

# Batches covering 251-587 (skip 1-250 mostly done; overwrite=false on rest)
BATCHES=(
  "251-300"
  "301-350"
  "351-400"
  "401-450"
  "451-500"
  "501-587"
)

batch_num=1
for range in "${BATCHES[@]}"; do
  start=$(echo $range | cut -d- -f1)
  end=$(echo $range | cut -d- -f2)
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
    echo "  ⚠ Empty response — API may have crashed"
    sleep 30
  fi

  batch_num=$((batch_num + 1))
done

echo
echo "=== Done at $(date +%H:%M:%S) ==="
