#!/usr/bin/env bash
# sync-atoms-to-vps.sh
#
# Đồng bộ atom store (wiki.sqlite3 + mapping JSON) từ Mac lên VPS.
# CHẠY SAU MỖI LẦN ingest atoms mới — nếu quên, live không thấy data mới.
#
# Usage:
#   ./scripts/sync-atoms-to-vps.sh [--dry-run]

set -euo pipefail

VPS_HOST="${VPS_HOST:-kinhdich.online}"
VPS_USER="${VPS_USER:-root}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/yi_chronos_deploy}"
VPS_DATA_DIR="/opt/yi-chronos/data"
LOCAL_DATA_DIR="$(cd "$(dirname "$0")/.." && pwd)/data"

DRY_RUN=""
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN="--dry-run"
    echo "[DRY RUN]"
fi

echo "=== Yi-Chronos Atom Store Sync ==="

# 1. Backup DB trên VPS trước khi đè
STAMP=$(date +%Y%m%d-%H%M%S)
if [[ -z "$DRY_RUN" ]]; then
    ssh -i "$SSH_KEY" "$VPS_USER@$VPS_HOST" \
        "cp $VPS_DATA_DIR/yi_wiki/wiki.sqlite3 $VPS_DATA_DIR/yi_wiki/wiki.sqlite3.bak-$STAMP 2>/dev/null || true; \
         ls -t $VPS_DATA_DIR/yi_wiki/wiki.sqlite3.bak-* 2>/dev/null | tail -n +4 | xargs rm -f"
    echo "[1/3] Backup VPS DB → wiki.sqlite3.bak-$STAMP (giữ 3 bản gần nhất)"
fi

# 2. Sync DB (nén -z, 43MB → ~37MB transfer)
echo "[2/3] Sync wiki.sqlite3 ..."
rsync -avz $DRY_RUN -e "ssh -i $SSH_KEY" \
    "$LOCAL_DATA_DIR/yi_wiki/wiki.sqlite3" \
    "$VPS_USER@$VPS_HOST:$VPS_DATA_DIR/yi_wiki/wiki.sqlite3"

# 3. Sync mapping JSON
echo "[3/4] Sync tu_vi_cung_sao_mapping.json ..."
rsync -avz $DRY_RUN -e "ssh -i $SSH_KEY" \
    "$LOCAL_DATA_DIR/tu_vi_cung_sao_mapping.json" \
    "$VPS_USER@$VPS_HOST:$VPS_DATA_DIR/tu_vi_cung_sao_mapping.json"

# 3b. Sync dataset Ngũ Uẩn (Tử Vi Bôn Ba) — tầng narrative đọc file này (2026-06-12)
echo "[4/4] Sync tuvibonba_ngu_uan.json ..."
if [[ -f "$LOCAL_DATA_DIR/yi_wiki/tuvibonba_ngu_uan.json" ]]; then
    rsync -avz $DRY_RUN -e "ssh -i $SSH_KEY" \
        "$LOCAL_DATA_DIR/yi_wiki/tuvibonba_ngu_uan.json" \
        "$VPS_USER@$VPS_HOST:$VPS_DATA_DIR/yi_wiki/tuvibonba_ngu_uan.json"
else
    echo "  (bỏ qua — chưa có file local)"
fi

# 4. Verify atoms count trên VPS
if [[ -z "$DRY_RUN" ]]; then
    COUNT=$(ssh -i "$SSH_KEY" "$VPS_USER@$VPS_HOST" \
        "sqlite3 $VPS_DATA_DIR/yi_wiki/wiki.sqlite3 'SELECT COUNT(*) FROM atomic_questions;'")
    echo ""
    echo "✅ VPS atom count: $COUNT"
fi
