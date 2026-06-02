#!/bin/bash
# ĐÊM 2 — 8 sách Chu Dịch / Kỳ Môn / Tử Vi to + tướng số (~21h)
#
# Usage:
#   nohup bash scripts/batch_restore_night2.sh > /tmp/batch-night2.log 2>&1 &

set -u
ROOT="/Users/ozvietnamdesktop/Desktop/yi"
cd "$ROOT"

BOOKS=(
  "kinh-dich-va-he-nhi-phan|thư viện sách/Kinh Dich va he nhi phan.pdf|1|842"
  "ki-mon-don-giap|thư viện sách/Kỳ Môn Độn Giáp .pdf|1|367"
  "so-tien-dinh-lap-thanh|thư viện sách/So tien dinh lap thanh.pdf|1|184"
  "nhap-mon-chu-dich-du-doan-hoc|thư viện sách/Nhap-Mon-Chu-Dich-Du-Doan-Hoc.pdf|1|257"
  "can-chi-thong-luan|thư viện sách/CAN CHI THÔNG LUẬN.pdf|1|352"
  "ly-thuyet-tuong-so-hoang-tuan|thư viện sách/Ly Thuyet Tuong So-Hoang Tuan.pdf|1|375"
  "bi-an-cua-bat-quai|thư viện sách/Bi an cua bat quai.pdf|1|941"
  "trung-chau-tu-vi-dau-so-2|thư viện sách/Trung Chau tu vi dau so 2.pdf|1|900"
)

echo "═══════════════════════════════════════════════════════════════"
echo "ĐÊM 2 — 8 sách Chu Dịch / Kỳ Môn / Tướng Số (~21h)"
echo "Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Total pages: 4218"
echo "═══════════════════════════════════════════════════════════════"

TOTAL_START=$(date +%s)
SUCCESS=0
FAIL=0
declare -a SUMMARY

for entry in "${BOOKS[@]}"; do
  IFS='|' read -r book_id pdf_path start end <<< "$entry"
  pages=$((end - start + 1))

  if [ -f "data/restored_books/$book_id/manifest.json" ]; then
    pp=$(ls "data/restored_books/$book_id/pages/"p*.md 2>/dev/null | wc -l | tr -d ' ')
    if [ "$pp" -ge "$pages" ]; then
      echo "⏭  SKIP $book_id (đã xong, $pp pages)"
      SUMMARY+=("⏭ $book_id (skipped)")
      continue
    fi
  fi

  echo
  echo "───────────────────────────────────────────────────────────────"
  echo "📖 Book $((SUCCESS+FAIL+1))/${#BOOKS[@]}: $book_id ($pages p)"
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
  BOOK_ELAPSED=$(($(date +%s) - BOOK_START))

  if [ $EXIT_CODE -eq 0 ]; then
    SUCCESS=$((SUCCESS+1))
    SUMMARY+=("✅ $book_id ($pages p, $((BOOK_ELAPSED/60))m)")
    echo "✅ Done in $((BOOK_ELAPSED/60))m"
  else
    FAIL=$((FAIL+1))
    SUMMARY+=("❌ $book_id (exit $EXIT_CODE)")
    echo "❌ FAILED"
  fi
done

TOTAL=$(($(date +%s) - TOTAL_START))
echo
echo "═══════════════════════════════════════════════════════════════"
echo "ĐÊM 2 COMPLETE — $(date '+%Y-%m-%d %H:%M:%S')"
echo "Total: $((TOTAL/3600))h $((TOTAL%3600/60))m"
echo "Success: $SUCCESS/${#BOOKS[@]} | Failed: $FAIL"
echo "═══════════════════════════════════════════════════════════════"
for s in "${SUMMARY[@]}"; do echo "  $s"; done
