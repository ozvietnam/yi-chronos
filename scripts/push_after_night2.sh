#!/bin/bash
# Auto-commit + push 8 sách Đêm 2 sau khi batch hoàn thành.
# Tuân thủ Iron Rule #7.

set -u
ROOT="/Users/ozvietnamdesktop/Desktop/yi"
cd "$ROOT"

WATCH_NAME="batch_restore_night2.sh"
echo "[$(date)] Đợi $WATCH_NAME hoàn thành..."
while pgrep -f "$WATCH_NAME" > /dev/null; do
  sleep 60
done

echo "[$(date)] Night2 batch ĐÃ KẾT THÚC."

NIGHT2_BOOKS=(
  "kinh-dich-va-he-nhi-phan"
  "ki-mon-don-giap"
  "so-tien-dinh-lap-thanh"
  "nhap-mon-chu-dich-du-doan-hoc"
  "can-chi-thong-luan"
  "ly-thuyet-tuong-so-hoang-tuan"
  "bi-an-cua-bat-quai"
  "trung-chau-tu-vi-dau-so-2"
)

DONE=0
for bid in "${NIGHT2_BOOKS[@]}"; do
  if [ -f "data/restored_books/$bid/content.md" ] && [ -f "data/restored_books/$bid/manifest.json" ]; then
    DONE=$((DONE+1))
  fi
done
echo "[$(date)] Books verified: $DONE/${#NIGHT2_BOOKS[@]}"

if [ $DONE -eq 0 ]; then exit 0; fi

for bid in "${NIGHT2_BOOKS[@]}"; do
  if [ -d "data/restored_books/$bid" ]; then
    git add "data/restored_books/$bid/" 2>/dev/null
  fi
done

# Iron Rule #7 check
sensitive=$(git diff --cached --name-only | grep -iE "auth|\.env|secret|token|key.*\.json|\.db$" || true)
if [ -n "$sensitive" ]; then
  echo "[$(date)] 🚨 SENSITIVE — ABORT"; echo "$sensitive"
  git reset; exit 1
fi
STAGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
echo "[$(date)] Staged: $STAGED files"
[ "$STAGED" = "0" ] && exit 0

git commit -m "$(cat <<EOF
feat(library): Đêm 2 — $DONE sách Chu Dịch / Kỳ Môn / Tướng Số phục chế

Pipeline: Tesseract VN OCR + Gemma 4 cleanup (LM Studio local).
Auto-pushed bởi push_after_night2.sh.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"

echo "[$(date)] Pushing..."
git push origin main 2>&1 | tail -3
echo "[$(date)] DONE."
