#!/usr/bin/env bash
# Chạy TRÊN VPS (nạp qua: ssh ... 'bash -s' < deploy/verify_health.sh).
#
# ── VÌ SAO check từ VPS chứ KHÔNG từ runner GitHub ───────────────────────────
# Runner GitHub dùng dải IP Azure dùng-chung. Firewall edge Hostinger thỉnh
# thoảng DROP gói từ một IP runner "nóng" — trên CẢ port 22 (đã né bằng đường
# hầm Tailscale ở bước deploy) LẪN port 443. Khi bị DROP, `curl
# https://kinhdich.online` TỪ RUNNER treo ~2 phút (SYN timeout) rồi trả "000"
# DÙ site vẫn sống 200 với mọi người khác → bước verify đỏ GIẢ (false-red).
# Bằng chứng: trong run 27836992209, 6 lần thử cách nhau ~2'23" = đúng dấu hiệu
# gói bị DROP (REJECT thì trả "connection refused" tức thì).
#
# Check tại VPS đi qua loopback (127.0.0.1) nên KHÔNG ra Internet → KHÔNG đụng
# firewall edge đó. `--resolve kinhdich.online:443:127.0.0.1` ép tên miền trỏ
# loopback nhưng vẫn giữ SNI + Host = kinhdich.online → vẫn đi ĐÚNG stack
# production: Traefik route theo Host + phục vụ TLS cert Let's Encrypt thật
# (curl verify cert khớp kinhdich.online). Tức là vẫn kiểm "cái user thấy"
# (DNS-less): Traefik OK + TLS OK + app trả 200 — chỉ khác điểm đứng nhìn.
set -u

URL="https://kinhdich.online/api/health"
RESOLVE="kinhdich.online:443:127.0.0.1"
ATTEMPTS=10
SLEEP=8

echo "═══ Verify health TỪ VPS (loopback → Traefik → app) ═══"
for i in $(seq 1 "$ATTEMPTS"); do
  code=$(curl -sS --resolve "$RESOLVE" \
    --connect-timeout 10 --max-time 20 \
    -o /tmp/yi_health.json -w '%{http_code}' \
    "$URL" 2>/tmp/yi_health.err || true)
  if [ "$code" = "200" ]; then
    echo "✅ Health OK (HTTP 200) ở lần thử $i:"
    cat /tmp/yi_health.json 2>/dev/null
    echo
    # Smoke Thần Số cast — bắt volume-stale / missing master JSON sớm
    cast_code=$(curl -sS --resolve "$RESOLVE" \
      --connect-timeout 10 --max-time 30 \
      -o /tmp/yi_than_so_cast.json -w '%{http_code}' \
      -X POST "https://kinhdich.online/api/than-so/cast" \
      -H 'Content-Type: application/json' \
      -d '{"name":"Nguyen Van A","birth_date":"1988-06-05"}' 2>/tmp/yi_than_so_cast.err || true)
    if [ "$cast_code" = "200" ]; then
      echo "✅ than-so/cast OK (HTTP 200)"
      python3 -c 'import json;d=json.load(open("/tmp/yi_than_so_cast.json")); assert "balliett" in d and "core" in d; print("  life_path", d["core"]["life_path"]["value"], "balliett_digit", d["balliett"]["birth_digit"]["birth_digit"])' 2>&1 || true
      exit 0
    fi
    echo "❌ than-so/cast HTTP=$cast_code (health OK nhưng cast gãy — thường do data/than_so/master thiếu JSON mới)"
    echo "─── cast body (head) ───"
    head -c 800 /tmp/yi_than_so_cast.json 2>/dev/null; echo
    echo "─── than_so files in container ───"
    docker exec yi-chronos sh -c 'ls -la data/than_so/master/ 2>&1; ls -la embedded_data/than_so/master/ 2>&1 | head -30' || true
    echo "─── 80 dòng log yi-chronos ───"
    docker logs --tail 80 yi-chronos 2>&1 || true
    exit 1
  fi
  echo "  ⏳ thử $i/$ATTEMPTS: HTTP=$code — $(tr '\n' ' ' </tmp/yi_health.err 2>/dev/null)"
  sleep "$SLEEP"
done

echo "❌ /api/health KHÔNG trả 200 sau $ATTEMPTS lần (~$((ATTEMPTS * SLEEP))s)."
echo "   ĐÂY LÀ LỖI THẬT (app/Traefik trên VPS không phục vụ), không phải"
echo "   chặn-runner như trước. Dump chẩn đoán:"
echo "─── docker compose ps ───"
docker compose -f /opt/yi-chronos/docker-compose.yml ps 2>/dev/null || docker ps
echo "─── 60 dòng log yi-chronos cuối ───"
docker logs --tail 60 yi-chronos 2>&1 || true
echo "─── thử app trực tiếp trong container (bỏ qua Traefik) để khoanh vùng ───"
docker exec yi-chronos sh -c 'curl -sS --max-time 10 -o - http://127.0.0.1:8000/api/health' 2>&1 || true
echo
exit 1
