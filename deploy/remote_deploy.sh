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

# ─── Seed dữ liệu TĨNH version-controlled vào volume (fix bind-mount shadow) ───
# Volume /opt/yi-chronos/data CHE data/ trong image → file tĩnh (data/tu_vi/*.json,
# seeds, restored_books, skills) KHÔNG thấy ở runtime → endpoint đọc chúng trả 500
# (vd /api/tu-vi/q4/chieu-dom-kinh-phi-tinh). Dockerfile đã copy chúng vào embedded_data/
# (path KHÔNG bị shadow). Đây copy embedded_data/* → data/* để populate volume. CHỈ ghi đè
# file tĩnh; embedded_data KHÔNG chứa *.sqlite3 nên data user (yi_users, yi_hermes/*.sqlite3)
# TUYỆT ĐỐI không bị đụng.
echo "═══ Seed embedded_data → data (tránh volume shadow) ═══"
docker exec yi-chronos sh -c '
  for d in tu_vi seeds than_so; do
    [ -d "embedded_data/$d" ] && mkdir -p "data/$d" && cp -rf "embedded_data/$d/." "data/$d/" 2>/dev/null || true
  done
  [ -d embedded_data/restored_books ] && cp -rf embedded_data/restored_books/. data/restored_books/ 2>/dev/null || true
  [ -d embedded_data/hermes_yi/skills ] && mkdir -p data/hermes_yi/skills && cp -rf embedded_data/hermes_yi/skills/. data/hermes_yi/skills/ 2>/dev/null || true
  [ -d embedded_data/yi_publishing ] && cp -rf embedded_data/yi_publishing/. data/yi_publishing/ 2>/dev/null || true
  echo "  seeded tu_vi json: $(ls data/tu_vi/*.json 2>/dev/null | wc -l) | seeds: $(ls data/seeds/ 2>/dev/null | wc -l) | q1 dicts: $(ls data/yi_publishing/q1_tuvi/master/*.json 2>/dev/null | wc -l)"
' || echo "  (seed bỏ qua — container chưa sẵn sàng?)"

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
