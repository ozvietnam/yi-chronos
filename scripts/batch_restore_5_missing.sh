#!/bin/bash
# OCR 4 sách scan ảnh còn lại sau pilot phong-thuy (2026-06-05)
# 4 sách × tổng 1145 trang (đã trừ phong-thuy 42 trang)
#
# Pipeline: pdf2image → Tesseract VN → Gemma cleanup (LM Studio localhost:1234)
# Concurrency 2, DPI 200 (tốc độ ~2.5 pages/min)
# ETA: 1145 / 2.5 = ~460 phút = ~7.5 giờ
#
# Run:
#   nohup bash scripts/batch_restore_5_missing.sh > /tmp/batch-5-missing.log 2>&1 &

set -u
ROOT="/Users/ozvietnamdesktop/Desktop/yi"
cd "$ROOT"

# Format: <book_id>|<pdf_relative>|<start>|<end>
# Sort theo size, nhỏ trước
BOOKS=(
  "don-toan-than-dieu|thư viện sách/DON TOAN THAN DIEU.pdf|1|121"
  "chon-viec-theo-lich-am|thư viện sách/chon viec theo lich am.pdf|1|198"
  "12-con-giap-theo-lich-van-nien|thư viện sách/12 con giap theo lich van nien.pdf|1|336"
  "lac-thu-cuu-tinh-phong-thuy-nha-o|thư viện sách/Lac thu cuu tinh phong thuy nha o.pdf|1|490"
)

echo "═══════════════════════════════════════════════════════════════"
echo "BATCH OCR 4 sách còn lại (sau pilot phong-thuy)"
echo "Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Total pages: $(echo "${BOOKS[@]}" | tr ' ' '\n' | awk -F'|' '{sum+=$4} END {print sum}')"
echo "═══════════════════════════════════════════════════════════════"
echo ""

OVERALL_T0=$(date +%s)

for i in "${!BOOKS[@]}"; do
  IFS='|' read -r book_id pdf_rel start end <<< "${BOOKS[$i]}"
  num=$((i + 1))
  total=${#BOOKS[@]}
  pages=$((end - start + 1))

  echo "─── [$num/$total] $book_id ($pages pages) ────────────────────"
  echo "    Started: $(date '+%H:%M:%S')"
  T0=$(date +%s)

  .venv/bin/python3 scripts/restore_vn_book.py \
    --pdf "$pdf_rel" \
    --book-id "$book_id" \
    --start "$start" --end "$end" \
    --concurrency 2 \
    --dpi 200 \
    --model "google/gemma-4-e4b" \
    2>&1 | tail -5

  T1=$(date +%s)
  ELAPSED=$((T1 - T0))
  MINS=$((ELAPSED / 60))
  echo "    Done in ${MINS}m ($(date '+%H:%M:%S'))"
  echo ""
done

OVERALL_T1=$(date +%s)
TOTAL_MINS=$(( (OVERALL_T1 - OVERALL_T0) / 60 ))

echo "═══════════════════════════════════════════════════════════════"
echo "BATCH DONE in ${TOTAL_MINS}m at $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════════════════════════"

# Verify counts
echo ""
echo "=== Final verification ==="
for entry in "${BOOKS[@]}"; do
  IFS='|' read -r book_id _ _ end <<< "$entry"
  done_count=$(ls "data/restored_books/$book_id/pages/" 2>/dev/null | grep -c "\.md$")
  echo "  $book_id: $done_count/$end pages"
done
