#!/bin/bash
# Auto-commit + push restored books sau khi night1 batch xong.
#
# Tuân thủ Iron Rule #7:
#  - Verify NO sensitive files (auth, .env, *.db, key, secret, token)
#  - Show diff stat trước khi commit
#  - Commit message rõ ràng, atomic
#
# Usage:
#   nohup bash scripts/push_after_night1.sh > /tmp/push-after-night1.log 2>&1 &

set -u
ROOT="/Users/ozvietnamdesktop/Desktop/yi"
cd "$ROOT"

# Watch process — find the bash batch_restore_night1.sh PID
WATCH_NAME="batch_restore_night1.sh"

echo "[$(date)] Đợi $WATCH_NAME hoàn thành..."
while pgrep -f "$WATCH_NAME" > /dev/null; do
  sleep 60
done

echo "[$(date)] Night1 batch ĐÃ KẾT THÚC. Kiểm tra output..."

# Verify all 9 night1 books có manifest
NIGHT1_BOOKS=(
  "trich-thien-tuy-binh-chu-nham-thiet-tieu"
  "thien-nhan-hoc-co-dai-trich-thien-tuy"
  "tu-vi-dau-so-toan-thu-vu-tai-luc"
  "tu-vi-nghiem-ly-toan-thu-thien-luong"
  "tang-san-boc-dich"
  "tu-vi-ham-so"
  "ha-do-trong-van-minh-dai-viet"
  "boc-phe-chinh-tong"
  "bat-tu-ha-lac-va-quy-dao-doi-nguoi"
)

DONE=0
MISSING=0
for bid in "${NIGHT1_BOOKS[@]}"; do
  if [ -f "data/restored_books/$bid/content.md" ] && [ -f "data/restored_books/$bid/manifest.json" ]; then
    DONE=$((DONE+1))
  else
    echo "  ❌ MISSING: $bid"
    MISSING=$((MISSING+1))
  fi
done
echo "[$(date)] Books verified: $DONE/${#NIGHT1_BOOKS[@]} (missing: $MISSING)"

if [ $DONE -eq 0 ]; then
  echo "[$(date)] ⚠️ Không có sách nào đêm 1 — skip push."
  exit 0
fi

# Stage chỉ content.md + manifest.json (skip pages/ để image gọn — đã handle qua .dockerignore)
echo "[$(date)] Stage files..."
for bid in "${NIGHT1_BOOKS[@]}"; do
  if [ -d "data/restored_books/$bid" ]; then
    git add "data/restored_books/$bid/content.md" 2>/dev/null
    git add "data/restored_books/$bid/manifest.json" 2>/dev/null
    # Pages/ cũng add để track full output (gitignore không chặn, dockerignore handle)
    git add "data/restored_books/$bid/pages/" 2>/dev/null
  fi
done

# Iron Rule #7: verify NO sensitive files
sensitive=$(git diff --cached --name-only | grep -iE "auth|\.env|secret|token|key.*\.json|\.db$" || true)
if [ -n "$sensitive" ]; then
  echo "[$(date)] 🚨 SENSITIVE FILES STAGED — ABORT PUSH"
  echo "$sensitive"
  git reset
  exit 1
fi

# Iron Rule #7: show staged count
STAGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
echo "[$(date)] Staged: $STAGED files"

if [ "$STAGED" = "0" ]; then
  echo "[$(date)] Nothing to commit."
  exit 0
fi

# Commit
git commit -m "$(cat <<EOF
feat(library): Đêm 1 — $DONE sách Tổ sư kinh điển phục chế

Books OCR + Gemma cleanup:
$(for bid in "${NIGHT1_BOOKS[@]}"; do
  if [ -f "data/restored_books/$bid/content.md" ]; then
    chars=\$(wc -c < "data/restored_books/$bid/content.md" | tr -d ' ')
    pages=\$(ls "data/restored_books/$bid/pages/"p*.md 2>/dev/null | wc -l | tr -d ' ')
    echo "- $bid (\${pages}p, \${chars}c)"
  fi
done)

Pipeline: Tesseract VN OCR + Gemma 4 cleanup (LM Studio local, 0\$).
Auto-pushed bởi push_after_night1.sh sau khi batch hoàn thành.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"

# Push
echo "[$(date)] Pushing to origin/main..."
if git push origin main 2>&1 | tail -3; then
  echo "[$(date)] ✅ PUSHED OK"
  echo "[$(date)] CI/CD sẽ auto-deploy trong ~3-5 phút"
else
  echo "[$(date)] ❌ Push failed — anh check manual"
  exit 1
fi

echo "[$(date)] DONE."
