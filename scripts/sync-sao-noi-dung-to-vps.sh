#!/usr/bin/env bash
# sync-sao-noi-dung-to-vps.sh
#
# SURGICAL SYNC: đồng bộ DUY NHẤT bảng `sao_noi_dung` (kèm verdict duyệt đối kháng
# founder_verified) từ Mac lên VPS — trả nợ B4 vòng sao (bàn giao 2026-07-03).
#
# VÌ SAO KHÔNG dùng sync-atoms-to-vps.sh: script đó rsync ĐÈ CẢ wiki.sqlite3 —
# clobber mọi thứ chỉ có trên prod (bảng sqlite-vec embeddings, v.v.).
# Script này chỉ chạm 1 bảng, mọi bảng khác trên prod giữ nguyên.
#
# Cách hoạt động:
#   1. Dump bảng sao_noi_dung từ DB local (.dump = CREATE TABLE + INSERT + index)
#   2. Backup wiki.sqlite3 trên VPS (giữ 3 bản gần nhất)
#   3. Trên VPS: DROP bảng cũ → apply dump (transaction, busy_timeout 10s)
#   4. Verify: đếm dòng + fv=1 theo lớp trên VPS so với local; curl endpoint live
#
# Usage:
#   ./scripts/sync-sao-noi-dung-to-vps.sh [--dry-run]
#
# ⚠️ Script viết từ container remote (2026-07-16), CHƯA chạy thật với VPS —
#    chạy --dry-run trước để soát stats local + lệnh sẽ thực thi.

set -euo pipefail

VPS_HOST="${VPS_HOST:-kinhdich.online}"
VPS_USER="${VPS_USER:-root}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/yi_chronos_deploy}"
VPS_DATA_DIR="/opt/yi-chronos/data"
LOCAL_DB="$(cd "$(dirname "$0")/.." && pwd)/data/yi_wiki/wiki.sqlite3"
VPS_DB="$VPS_DATA_DIR/yi_wiki/wiki.sqlite3"
TABLE="sao_noi_dung"
DUMP_LOCAL="/tmp/${TABLE}_dump.sql"
DUMP_REMOTE="/tmp/${TABLE}_dump.sql"

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=1
    echo "[DRY RUN — không đụng VPS]"
fi

echo "=== Surgical sync bảng $TABLE → VPS ==="

# 0. Precondition + stats local
[[ -f "$LOCAL_DB" ]] || { echo "❌ Không thấy $LOCAL_DB"; exit 1; }
echo "[0/4] Stats LOCAL:"
sqlite3 "$LOCAL_DB" "SELECT '  total: ' || COUNT(*) FROM $TABLE;"
sqlite3 "$LOCAL_DB" \
    "SELECT '  lớp ' || lop || ': ' || COUNT(*) || ' dòng, fv=1: ' ||
            SUM(CASE WHEN founder_verified=1 THEN 1 ELSE 0 END)
     FROM $TABLE GROUP BY lop;"

# 1. Dump đúng 1 bảng (CREATE TABLE + INSERT + index của bảng đó)
echo "[1/4] Dump $TABLE từ local ..."
sqlite3 "$LOCAL_DB" ".dump $TABLE" > "$DUMP_LOCAL"
echo "  → $DUMP_LOCAL ($(du -h "$DUMP_LOCAL" | cut -f1))"

if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Sẽ: backup VPS DB → scp dump → DROP+apply trên VPS → verify."
    exit 0
fi

# 2. Backup DB trên VPS (giữ 3 bản)
STAMP=$(date +%Y%m%d-%H%M%S)
echo "[2/4] Backup VPS DB → wiki.sqlite3.bak-$STAMP ..."
ssh -i "$SSH_KEY" "$VPS_USER@$VPS_HOST" \
    "cp $VPS_DB $VPS_DB.bak-$STAMP && \
     ls -t $VPS_DB.bak-* 2>/dev/null | tail -n +4 | xargs -r rm -f"

# 3. Đẩy dump + thay bảng trong 1 phiên sqlite (dump tự bọc BEGIN/COMMIT)
echo "[3/4] Apply dump trên VPS (chỉ bảng $TABLE) ..."
scp -i "$SSH_KEY" "$DUMP_LOCAL" "$VPS_USER@$VPS_HOST:$DUMP_REMOTE"
ssh -i "$SSH_KEY" "$VPS_USER@$VPS_HOST" \
    "sqlite3 -cmd 'PRAGMA busy_timeout=10000' $VPS_DB 'DROP TABLE IF EXISTS $TABLE;' && \
     sqlite3 -cmd 'PRAGMA busy_timeout=10000' $VPS_DB < $DUMP_REMOTE && \
     rm -f $DUMP_REMOTE"

# 4. Verify VPS vs local + endpoint live
echo "[4/4] Verify:"
echo "  Stats VPS:"
ssh -i "$SSH_KEY" "$VPS_USER@$VPS_HOST" \
    "sqlite3 $VPS_DB \"SELECT '    total: ' || COUNT(*) FROM $TABLE;\" && \
     sqlite3 $VPS_DB \"SELECT '    lớp ' || lop || ': ' || COUNT(*) || ' dòng, fv=1: ' ||
                       SUM(CASE WHEN founder_verified=1 THEN 1 ELSE 0 END)
                       FROM $TABLE GROUP BY lop;\""
echo "  Endpoint live /api/tu-vi/vong-sao:"
curl -sS "https://$VPS_HOST/api/tu-vi/vong-sao" | head -c 300 || echo "  (curl fail — check tay)"
echo ""
echo "✅ Xong. Nếu số fv=1 trên VPS khớp local và endpoint trả data → B4 prod hết RỖNG."
echo "   Rollback nếu cần: cp $VPS_DB.bak-$STAMP $VPS_DB"
