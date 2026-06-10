#!/bin/bash
# Repair Hoàng Cực OCR: rerun failed chunk_0 (p1-122) + chunk_1 (p123-244)
# SEQUENTIALLY (avoid 4-way resource contention that killed the swarm run),
# then merge all 4 chunks into canonical folder + recompute book progress.
set -e
cd /Users/ozvietnamdesktop/Desktop/yi

SWARM=data/yi_publishing_mineru/_swarm/ocr-20260610-093347-982187-1338
PDF=data/raw_pdfs/hoang-cuc-kinh-the-kim-thuyet-thuong.pdf
BOOK=hoang-cuc-kinh-the-kim-thuyet-thuong

echo "[$(date +%H:%M:%S)] wipe stale chunk_0 + chunk_1"
rm -rf "$SWARM/chunk_0" "$SWARM/chunk_1"
mkdir -p "$SWARM/chunk_0" "$SWARM/chunk_1"

echo "[$(date +%H:%M:%S)] chunk_0 pages 1-122 starting (sequential)"
.venv-mineru/bin/mineru -p "$PDF" -o "$SWARM/chunk_0" -b pipeline -l ch -s 1 -e 122 -m auto -f False > /tmp/hoangcuc_chunk0.log 2>&1
echo "[$(date +%H:%M:%S)] chunk_0 done"

echo "[$(date +%H:%M:%S)] chunk_1 pages 123-244 starting"
.venv-mineru/bin/mineru -p "$PDF" -o "$SWARM/chunk_1" -b pipeline -l ch -s 123 -e 244 -m auto -f False > /tmp/hoangcuc_chunk1.log 2>&1
echo "[$(date +%H:%M:%S)] chunk_1 done"

echo "[$(date +%H:%M:%S)] verify all 4 chunks have middle.json"
for i in 0 1 2 3; do
  test -f "$SWARM/chunk_$i/$BOOK/auto/${BOOK}_middle.json" || { echo "FATAL: chunk_$i missing middle.json"; exit 1; }
done

echo "[$(date +%H:%M:%S)] merging 4 chunks into canonical folder"
python3 - <<'EOF'
import sys
from pathlib import Path
sys.path.insert(0, '/Users/ozvietnamdesktop/Desktop/yi')
from engine.yi_publishing.jobs import JobsStore
from engine.yi_publishing.books_store import BooksStore

root = Path('/Users/ozvietnamdesktop/Desktop/yi')
store = JobsStore()
store._merge_swarm_chunks(
    'hoang-cuc-kinh-the-kim-thuyet-thuong',
    root / 'data/yi_publishing_mineru/_swarm/ocr-20260610-093347-982187-1338',
    4,
    pdf_path=root / 'data/raw_pdfs/hoang-cuc-kinh-the-kim-thuyet-thuong.pdf',
)
print('merge OK')
bs = BooksStore()
print('progress:', bs.recompute_progress('hoang-cuc-kinh-the-kim-thuyet-thuong'))
EOF
echo "[$(date +%H:%M:%S)] ALL DONE — canonical folder ready (swarm dir kept for verify)"
