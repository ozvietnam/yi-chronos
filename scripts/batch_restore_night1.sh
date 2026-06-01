#!/bin/bash
# ĐÊM 1 — 9 sách Tổ sư / kinh điển Bát Tự + Tử Vi + Bốc Phệ (scan PDF, OCR + Gemma)
# ETA ~13h. Kick off SAU KHI batch hiện tại (sách 5 Chu Dịch Dự Đoán Học) xong.
#
# Usage:
#   nohup bash scripts/batch_restore_night1.sh > /tmp/batch-night1.log 2>&1 &

set -u
ROOT="/Users/ozvietnamdesktop/Desktop/yi"
cd "$ROOT"

# Format: <book_id>|<pdf_path>|<start>|<end>
# Priority Top-Down: kinh điển nhất trước
BOOKS=(
  "trich-thien-tuy-binh-chu-nham-thiet-tieu|thư viện sách/Trích Thiên tuỷ bình chú (Full)- Nhậm Thiết Tiều.pdf|1|202"
  "thien-nhan-hoc-co-dai-trich-thien-tuy|thư viện sách/Thiên nhân học cổ đại trích thiên tủy.pdf|1|119"
  "tu-vi-dau-so-toan-thu-vu-tai-luc|thư viện sách/Tu Vi dau so toan thu.pdf|1|171"
  "tu-vi-nghiem-ly-toan-thu-thien-luong|thư viện sách/TỬ-VI-NGHIỆM-LÝ-TOAN-THƯ-THIÊN_LƯƠNG.pdf|1|186"
  "tang-san-boc-dich|thư viện sách/Tăng San Bốc Dịch.pdf|1|429"
  "tu-vi-ham-so|thư viện sách/Tu-vi-ham-so.pdf|1|238"
  "ha-do-trong-van-minh-dai-viet|thư viện sách/Hà đồ trong văn minh đại việt.pdf|1|304"
  "boc-phe-chinh-tong|thư viện sách/Boc phe chinh tong.pdf|1|277"
  "bat-tu-ha-lac-va-quy-dao-doi-nguoi|thư viện sách/Tám chữ hà lạc và quỹ đạo đời người [Bát tự Hà Lạc].pdf|1|608"
)

echo "═══════════════════════════════════════════════════════════════"
echo "ĐÊM 1 — 9 sách Tổ sư kinh điển"
echo "Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Total pages: $(echo "${BOOKS[@]}" | tr ' ' '\n' | awk -F'|' '{sum+=$4} END {print sum}')"
echo "═══════════════════════════════════════════════════════════════"
echo

TOTAL_START=$(date +%s)
SUCCESS=0
FAIL=0
declare -a SUMMARY

for entry in "${BOOKS[@]}"; do
  IFS='|' read -r book_id pdf_path start end <<< "$entry"
  pages=$((end - start + 1))

  # Skip nếu đã có manifest (idempotent — anh re-run an toàn)
  if [ -f "data/restored_books/$book_id/manifest.json" ]; then
    pp=$(ls "data/restored_books/$book_id/pages/"p*.md 2>/dev/null | wc -l | tr -d ' ')
    if [ "$pp" -ge "$pages" ]; then
      echo "⏭  SKIP $book_id (already done, $pp pages)"
      SUMMARY+=("⏭ $book_id (skipped — already done)")
      continue
    fi
  fi

  echo
  echo "───────────────────────────────────────────────────────────────"
  echo "📖 Book $((SUCCESS+FAIL+1))/${#BOOKS[@]}: $book_id"
  echo "📄 $pages pages | $pdf_path"
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
    SUMMARY+=("✅ $book_id ($pages p, $((BOOK_ELAPSED/60))m)")
    echo "✅ Done in $((BOOK_ELAPSED/60))m"
  else
    FAIL=$((FAIL+1))
    SUMMARY+=("❌ $book_id (exit $EXIT_CODE, log: $LOG)")
    echo "❌ FAILED (exit $EXIT_CODE)"
  fi
done

TOTAL_END=$(date +%s)
TOTAL_ELAPSED=$((TOTAL_END - TOTAL_START))

echo
echo "═══════════════════════════════════════════════════════════════"
echo "ĐÊM 1 COMPLETE — $(date '+%Y-%m-%d %H:%M:%S')"
echo "Total: $((TOTAL_ELAPSED/3600))h $((TOTAL_ELAPSED%3600/60))m"
echo "Success: $SUCCESS/${#BOOKS[@]} | Failed: $FAIL"
echo "═══════════════════════════════════════════════════════════════"
for s in "${SUMMARY[@]}"; do echo "  $s"; done
