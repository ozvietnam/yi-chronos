#!/usr/bin/env bash
# Chạy TRÊN VPS, được nạp qua: ssh ... 'bash -s' < deploy/remote_deploy.sh
# (bước scp trước đó đã đặt docker-compose.yml vào /opt/yi-chronos/)
#
# Tách script ra file riêng để tránh heredoc lồng trong nick-fields/retry,
# đồng thời mỗi lần deploy chỉ mở 1 kết nối SSH cho toàn bộ thao tác remote.
set -euo pipefail
cd /opt/yi-chronos

echo "═══ Compose file hiện tại ═══"
ls -la /opt/yi-chronos/docker-compose.yml

echo "═══ Pull image mới từ GHCR ═══"
docker compose pull

echo "═══ Recreate container ═══"
docker compose up -d --remove-orphans
sleep 8

echo "═══ Trạng thái container ═══"
docker compose ps

echo "═══ Log container (120 dòng cuối — chẩn đoán crash) ═══"
docker logs --tail 120 yi-chronos 2>&1 || true

echo "═══ Log Celery worker + beat (#41 — xác nhận nối broker + ready) ═══"
docker logs --tail 40 yi-worker 2>&1 || true
docker logs --tail 15 yi-beat 2>&1 || true

echo "═══ Trạng thái container sau start-period (worker healthy chưa?) ═══"
sleep 45
docker compose ps

echo "═══ Prune image rác (>24h) ═══"
docker image prune -f --filter "until=24h" || true
