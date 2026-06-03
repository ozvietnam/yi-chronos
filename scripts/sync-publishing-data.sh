#!/usr/bin/env bash
# sync-publishing-data.sh
#
# Đồng bộ data yi_publishing (sách dịch, OCR output) từ Mac lên VPS.
# Chạy trên máy local (Mac) sau khi upload/dịch sách xong.
#
# Dữ liệu gitignored cần sync thủ công:
#   data/yi_publishing/         — books.json, metadata, translations
#   data/yi_publishing_mineru/  — OCR output từ MinerU
#
# Usage:
#   ./scripts/sync-publishing-data.sh [--dry-run]
#
# Yêu cầu: VPS_HOST trong env hoặc hardcode bên dưới.

set -euo pipefail

VPS_HOST="${VPS_HOST:-kinhdich.online}"
VPS_USER="${VPS_USER:-root}"
VPS_DATA_DIR="/opt/yi-chronos/data"
LOCAL_DATA_DIR="$(cd "$(dirname "$0")/.." && pwd)/data"

DRY_RUN=""
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN="--dry-run"
    echo "[DRY RUN] Sẽ hiển thị thay đổi nhưng KHÔNG sync thật."
fi

echo "=== Yi-Chronos Publishing Data Sync ==="
echo "Local : $LOCAL_DATA_DIR"
echo "Remote: $VPS_USER@$VPS_HOST:$VPS_DATA_DIR"
echo ""

# yi_publishing: sách dịch, metadata, jobs, translations
echo "[1/2] Sync data/yi_publishing/ ..."
rsync -avz $DRY_RUN \
    --exclude="*.tmp" \
    --exclude=".DS_Store" \
    "$LOCAL_DATA_DIR/yi_publishing/" \
    "$VPS_USER@$VPS_HOST:$VPS_DATA_DIR/yi_publishing/"

# yi_publishing_mineru: OCR output (có thể lớn, dùng --checksum)
echo "[2/2] Sync data/yi_publishing_mineru/ ..."
rsync -avz $DRY_RUN \
    --checksum \
    --exclude="*.tmp" \
    --exclude=".DS_Store" \
    "$LOCAL_DATA_DIR/yi_publishing_mineru/" \
    "$VPS_USER@$VPS_HOST:$VPS_DATA_DIR/yi_publishing_mineru/"

echo ""
if [[ -z "$DRY_RUN" ]]; then
    echo "✅ Sync xong. Truy cập kinhdich.online/thu-vien để kiểm tra."
else
    echo "✅ Dry run xong. Chạy lại không có --dry-run để sync thật."
fi
