#!/bin/bash
# Batch restore 5 sách Tứ Trụ / Chu Dịch Việt tuần tự với Gemma 4 local.
# Sách 681p Thiệu Vỹ Hoa đã xong (đêm 30/5 → sáng 31/5).
#
# Usage:
#   nohup bash scripts/batch_restore_vn_books.sh > /tmp/batch-restore.log 2>&1 &
#
# Output per sách: data/restored_books/<book_id>/

set -u
ROOT="/Users/ozvietnamdesktop/Desktop/yi"
cd "$ROOT"

# Format: <book_id>|<pdf_path>|<start>|<end>
BOOKS=(
  "tu-xem-van-menh-theo-tu-tru|thư viện sách/Tu-xem-van-menh-theo-tu-tru.pdf|1|188"
  "nguyen-ly-chon-ngay-theo-bat-tu-ha-lac|thư viện sách/Nguyên lý chọn ngày theo bát tự hà lạc (Phương pháp chọn ngày.pdf|1|177"
  "chu-dich-du-doan-cac-vi-du-co-giai-thieu-vi-hoa|thư viện sách/Chu Dịch Dự Đoán Các Ví Dụ Có Giải - Thiệu Vĩ Hoa.pdf|1|360"
  "du-bao-theo-tu-binh|thư viện sách/Du Bao Theo Tu Binh.pdf|1|424"
  "chu-dich-voi-du-doan-hoc|thư viện sách/Chu dich voi du doan hoc.pdf|1|798"
)

echo "═══════════════════════════════════════════════════════════════"
echo "BATCH RESTORE — 5 sách Tứ Trụ / Chu Dịch Việt"
echo "Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════════════════════════"
echo

TOTAL_START=$(date +%s)
SUCCESS=0
FAIL=0
declare -a SUMMARY

for entry in "${BOOKS[@]}"; do
  IFS='|' read -r book_id pdf_path start end <<< "$entry"
  pages=$((end - start + 1))

  echo
  echo "───────────────────────────────────────────────────────────────"
  echo "📖 Book $((SUCCESS+FAIL+1))/5: $book_id"
  echo "📄 $pages pages | PDF: $pdf_path"
  echo "🕐 $(date '+%H:%M:%S')"
  echo "───────────────────────────────────────────────────────────────"

  BOOK_START=$(date +%s)
  LOG="/tmp/restore-${book_id}.log"

  .venv/bin/python3 scripts/restore_vn_book.py \
    --pdf "$pdf_path" \
    --book-id "$book_id" \
    --start "$start" --end "$end" \
    --concurrency 3 \
    > "$LOG" 2>&1

  EXIT_CODE=$?
  BOOK_END=$(date +%s)
  BOOK_ELAPSED=$((BOOK_END - BOOK_START))

  if [ $EXIT_CODE -eq 0 ]; then
    SUCCESS=$((SUCCESS+1))
    SUMMARY+=("✅ $book_id — $pages pages — $((BOOK_ELAPSED/60))m")
    echo "✅ Done in $((BOOK_ELAPSED/60))m $((BOOK_ELAPSED%60))s"
  else
    FAIL=$((FAIL+1))
    SUMMARY+=("❌ $book_id — exit $EXIT_CODE — log: $LOG")
    echo "❌ FAILED (exit $EXIT_CODE) — see $LOG"
  fi
done

TOTAL_END=$(date +%s)
TOTAL_ELAPSED=$((TOTAL_END - TOTAL_START))

echo
echo "═══════════════════════════════════════════════════════════════"
echo "BATCH COMPLETE — $(date '+%Y-%m-%d %H:%M:%S')"
echo "Total elapsed: $((TOTAL_ELAPSED/3600))h $((TOTAL_ELAPSED%3600/60))m"
echo "Success: $SUCCESS/5 | Failed: $FAIL/5"
echo "═══════════════════════════════════════════════════════════════"
for s in "${SUMMARY[@]}"; do
  echo "  $s"
done
