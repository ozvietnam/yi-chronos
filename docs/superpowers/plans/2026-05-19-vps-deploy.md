# YI-Chronos VPS Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Đưa YI-Chronos chạy live trên VPS Hostinger với edit-to-live workflow qua GitHub Actions, giữ Mac M4 là môi trường code chính.

**Architecture:** Multi-stage Docker image (Node 20 build Vue → Python 3.14 runtime serve API + static dist), Traefik labels cho subdomain `.nip.io` auto Let's Encrypt SSL, SQLite + `ai_keys.json` mount qua named volume, 8 LLM providers cấu hình qua mount file `ai_keys.json` (giữ nguyên flow hiện tại), GitHub Actions build image push GHCR + SSH restart container.

**Tech Stack:** Python 3.14 slim, FastAPI, Uvicorn, Vue 3, Vite 7, Docker 29, Traefik v3 (đã có sẵn trên VPS), GitHub Actions, GitHub Container Registry (GHCR), `.nip.io` DNS, Let's Encrypt.

**Cost:** $0/tháng thêm (VPS Hostinger Anh đã trả 5 năm, domain `.nip.io` free).

**Estimated time:** 4–6 giờ thực thi (chia 3 buổi: containerize → VPS setup → CI).

---

## 0. Context recap (decisions locked)

| Decision | Lựa chọn | Lý do |
|---|---|---|
| Hosting | VPS Hostinger 187.127.98.35 | Anh đã có, 2 vCPU/8GB/100GB, Singapore-ish |
| Domain | `kinhdich.online` (Anh vừa mua trên Hostinger) | Domain chính thức, Let's Encrypt cert chuẩn không warning |
| Reverse proxy | Traefik v3 (đã chạy sẵn) | Hoà vào stack OZ, auto-SSL |
| LLM | 8 providers cấu hình riêng (không qua Hermes pool) | Đơn giản, không phụ thuộc Hermes pool unhealthy |
| Ollama | KHÔNG deploy lên VPS phase này | Restoration chỉ chạy Mac. UI Mai Hoa cast/interpret dùng cloud LLM |
| Edit flow | Git push → GHCR build → SSH pull + restart | Chuẩn mực, ~1-2 phút edit-to-live |
| Initial data | rsync `data/` 700MB từ Mac lên VPS volume | One-time migration |
| Source of truth | VPS authoritative cho predictions/user data, Mac authoritative cho corpus/restored content (rsync khi update) | Tránh bidirectional sync phức tạp |

## 1. Architecture diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│ VPS Hostinger (187.127.98.35) — Ubuntu 24.04                         │
│                                                                       │
│  Traefik :80/:443 ──[Host: kinhdich.online]──┐               │
│                                                       │               │
│  ┌────────────────────────────────────────────────┐  │               │
│  │ Container: yi-chronos (Docker)                 │◄─┘               │
│  │  - uvicorn :8000 (internal)                    │                   │
│  │  - FastAPI serves /api/*  +  / (Vue dist)      │                   │
│  │  - StaticFiles mount: /figures /assets         │                   │
│  │  Volumes:                                      │                   │
│  │   /opt/yi-chronos/data → container /app/data   │                   │
│  │   /opt/yi-chronos/data/ai_keys.json (chmod 600)│                   │
│  │  Env:                                          │                   │
│  │   YI_CHRONOS_DATABASE_URL=sqlite:///data/...   │                   │
│  │   TZ=Asia/Ho_Chi_Minh                          │                   │
│  └────────────────────────────────────────────────┘                   │
│                                                                       │
│  Image source: ghcr.io/yi-chronos/yi-chronos:<sha>                    │
│                                                                       │
│  Co-tenant (existing, untouched):                                     │
│   • hermes-pool-proxy :4000 (LiteLLM, unhealthy)                      │
│   • hermes-pool-pg :5432  • hermes-pool-redis :6379                   │
│   • videoauto-n8n :5678   • traefik :80/:443                          │
│   • oz-* systemd services :7800 :8800                                 │
└──────────────────────────────────────────────────────────────────────┘
              ▲                                          ▲
              │  git push main                           │  rsync ssh
              │                                          │
┌─────────────┴──────────────────────────────────────────┴─────────────┐
│ Mac M4 (dev + restoration)                                            │
│  • Code editor + uvicorn local :8000 (dev cycle)                      │
│  • Ollama :11434 (restoration only, KHÔNG public)                     │
│  • git remote: origin (GitHub)                                        │
│  • GitHub Actions trigger on push to main                             │
└──────────────────────────────────────────────────────────────────────┘
              ▲
              │  HTTPS clone/pull
┌─────────────┴────────────────┐
│ GitHub repo + Actions runner │
│  - Build image (multi-arch?) │
│  - Push GHCR                 │
│  - SSH VPS: docker compose   │
│    pull && up -d             │
└──────────────────────────────┘
```

## 2. File structure (artifacts to create)

| File | Responsibility | Phase |
|---|---|---|
| `Dockerfile` | Multi-stage build: Node build webapp → Python runtime | 1 |
| `.dockerignore` | Loại bỏ `.venv`, `node_modules`, `data/*.sqlite3`, `data/cache` khỏi build context | 1 |
| `docker-compose.prod.yml` | Compose file cho VPS (traefik labels, volumes, env_file) | 1 |
| `api/main.py` (modify) | Thêm mount `/` cho Vue dist + thắt CORS prod | 1, 4 |
| `.github/workflows/deploy.yml` | CI: build image → push GHCR → SSH deploy | 3 |
| `scripts/deploy/vps-bootstrap.sh` | One-time VPS setup (mkdir, perms) | 2 |
| `scripts/deploy/migrate-data.sh` | rsync Mac → VPS data/ (idempotent) | 2 |
| `scripts/deploy/backup-sqlite.sh` | Cron daily backup các .sqlite3 sang `/opt/yi-chronos/backups/` | 4 |
| `docs/DEPLOY-RUNBOOK.md` | Quick ref: deploy/rollback/troubleshoot | 6 |

## 3. Pre-flight: things em đã verify

- ✅ `requirements.txt`: 7 packages (fastapi, httpx, pydantic, pytest, skyfield, sqlalchemy, uvicorn)
- ✅ `package.json`: vue@3.5, vite@7.1, three@0.180, lucide-vue-next, playwright, vitest
- ✅ `.gitignore` protects: `data/ai_keys.json`, `data/ai_provider_notes.json`, `data/*.sqlite3`, `.env`, `hermes_yi/`
- ✅ API routes: 194/195 use `/api/` prefix, 1 lone `/calculate` route (sẽ xử trong Task 1.1)
- ✅ Frontend: `VITE_API_BASE` (env var), default empty → relative URLs (perfect cho cùng-domain deploy)
- ✅ Static mounts hiện có: `/figures` only — sẽ thêm `/assets` + `/` cho Vue dist
- ✅ `engine/ai/registry.py:55` load `data/ai_keys.json` via `Path(__file__).resolve().parent.parent.parent / "data" / "ai_keys.json"` → relative tới project root, mount sẽ work
- ✅ Data size: ~988MB total (188MB published + 182MB hermes_yi + 163MB mineru + ephemeris 47MB tải lại được)

---

# Phase 0: Pre-flight verification (local)

**Goal:** Đảm bảo project chạy đúng local trước khi containerize.

### Task 0.1: Verify local build + run

**Files:** none modified.

- [ ] **Step 0.1.1: Build webapp local**

```bash
cd /Users/ozvietnamdesktop/Desktop/yi/client/webapp
npm install
npm run build
```

Expected output: `vite v7.x.x building for production... ✓ built in <2s` + `dist/` folder created.

- [ ] **Step 0.1.2: Verify dist artifacts**

```bash
ls -lah client/webapp/dist/
ls client/webapp/dist/assets/ | head
```

Expected: `index.html`, `assets/` dir với `*.js` + `*.css` files.

- [ ] **Step 0.1.3: Verify API starts local**

```bash
cd /Users/ozvietnamdesktop/Desktop/yi
source .venv/bin/activate
python3 -m uvicorn api.main:app --host 127.0.0.1 --port 8000 &
sleep 3
curl -s http://127.0.0.1:8000/api/health
kill %1
```

Expected: JSON `{"status": "ok", ...}` or similar healthy response.

- [ ] **Step 0.1.4: Verify ai_keys.json structure**

```bash
ls -lah data/ai_keys.json
python3 -c "import json; d=json.load(open('data/ai_keys.json')); print(list(d.keys()))"
```

Expected: file exists chmod 600, prints provider names list.

### Task 0.2: Identify hardcoded localhost references

**Files:** scan only.

- [ ] **Step 0.2.1: Find hardcoded :8000 / localhost / 127.0.0.1 in client**

```bash
grep -rn "127.0.0.1\|localhost\|http://" client/webapp/src/ 2>/dev/null | grep -v node_modules
```

Expected: only references in error messages (api.js) — these are user-facing strings, OK to leave. Real URL usage should be via `VITE_API_BASE`.

- [ ] **Step 0.2.2: Find hardcoded paths in api/main.py**

```bash
grep -n "127.0.0.1\|localhost\|http://localhost" api/main.py core/ engine/ 2>/dev/null | head -10
```

Expected: no hardcoded URLs in server-side code.

- [ ] **Step 0.2.3: Commit Phase 0 baseline**

If repo not yet initialized as git remote:
```bash
cd /Users/ozvietnamdesktop/Desktop/yi
git status
```

If many uncommitted files: stage and commit a baseline.

```bash
git add -A
git commit -m "baseline before VPS deploy plan execution"
```

### Task 0.3: Setup git remote to new `yi-chronos` GitHub account

**Files:** none modified, only git config + remote.

Hiện tại `gh auth status` cho thấy CLI đang login với `ozvietnam`. Trước khi push lên repo của `yi-chronos`, cần switch account.

- [ ] **Step 0.3.1: Login gh CLI với account yi-chronos**

```bash
gh auth login --git-protocol https --hostname github.com
# Chọn: GitHub.com → HTTPS → Yes (authenticate Git) → Login with web browser
# Browser sẽ mở yêu cầu login với account yi-chronos
gh auth status  # verify hiển thị yi-chronos
```

Nếu Anh muốn giữ cả 2 account, dùng `gh auth switch` để chuyển qua lại.

- [ ] **Step 0.3.2: Tạo repo trên GitHub (private hoặc public)**

```bash
# Private (recommended cho phase đầu):
gh repo create yi-chronos/yi-chronos --private --source=. --description="YI-Chronos — Đông phương học AI-driven"
# Hoặc public:
# gh repo create yi-chronos/yi-chronos --public --source=. --description="..."
```

Lệnh này tự động:
- Tạo repo `github.com/yi-chronos/yi-chronos`
- Set local remote `origin` → repo này

- [ ] **Step 0.3.3: Verify remote**

```bash
git remote -v
```

Expected: `origin  https://github.com/yi-chronos/yi-chronos.git (fetch)` + push.

- [ ] **Step 0.3.4: Push existing branch**

```bash
git branch -M main  # rename current branch to main if needed
git push -u origin main
```

Expected: all commits pushed to GitHub. Verify trên web: `https://github.com/yi-chronos/yi-chronos`.

⚠️ **Nếu .gitignore lỡ leak file nhạy cảm** (data/ai_keys.json, .env): kiểm tra trước push bằng `git ls-files | grep -E "ai_keys|\.env"` → expected empty. Nếu có file leak: `git rm --cached <file>` trước push.

- [ ] **Step 0.3.5: Set git user.name + user.email cho commits**

```bash
# Trong project this repo only (không ảnh hưởng global config)
git config user.name "yi-chronos"
git config user.email "<email_account_yi-chronos>"
```

---

# Phase 1: Containerization

**Goal:** Build a self-contained Docker image (~600MB) that serves both API and Vue dist on port 8000.

### Task 1.1: Add Vue dist static mount in main.py

**Files:**
- Modify: `api/main.py` (after line where `/figures` mount is, ~166)

- [ ] **Step 1.1.1: Find current mount location**

```bash
grep -n "app.mount" api/main.py
```

Expected: line ~166 with `/figures` mount.

- [ ] **Step 1.1.2: Add static dist mount AT THE END of main.py (after all routes)**

Open `api/main.py` and append BEFORE the `if __name__` block (if exists) or at very end:

```python
# ─── Serve built Vue webapp (production only) ────────────────────────────
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

_DIST_ROOT = Path(__file__).resolve().parent.parent / "client" / "webapp" / "dist"
if _DIST_ROOT.exists() and (_DIST_ROOT / "index.html").exists():
    # Mount /assets first (so it takes precedence)
    _ASSETS = _DIST_ROOT / "assets"
    if _ASSETS.exists():
        app.mount("/assets", StaticFiles(directory=str(_ASSETS)), name="assets")

    # SPA fallback: any GET not matched by /api/* or /figures/* serves index.html
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Don't intercept api/figures routes (they have their own handlers)
        if full_path.startswith("api/") or full_path.startswith("figures/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404)
        # Static file from dist?
        candidate = _DIST_ROOT / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        # SPA fallback
        return FileResponse(_DIST_ROOT / "index.html")
```

- [ ] **Step 1.1.3: Fix lone `/calculate` route to `/api/calculate`**

```bash
grep -n "/calculate\"" api/main.py
```

Expected output: ~line 276 `@app.post("/calculate")`.

Edit that line to `@app.post("/api/calculate")`.

Then check frontend usage:

```bash
grep -rn "/calculate" client/webapp/src/ 2>/dev/null | grep -v node_modules
```

If frontend has `fetch("/calculate")` calls, update to `/api/calculate`. If none, no further change needed.

- [ ] **Step 1.1.4: Run local smoke test**

```bash
cd client/webapp && npm run build && cd ../..
source .venv/bin/activate
python3 -m uvicorn api.main:app --host 127.0.0.1 --port 8000 &
sleep 3
curl -sI http://127.0.0.1:8000/ | head -3
curl -s http://127.0.0.1:8000/api/health
curl -sI http://127.0.0.1:8000/assets/ 2>/dev/null | head -1
kill %1
```

Expected: `/` returns 200 HTML, `/api/health` returns JSON, `/assets/` returns 404 or 200 (depends on Vite hash, OK either way).

- [ ] **Step 1.1.5: Commit**

```bash
git add api/main.py
git commit -m "serve Vue dist as SPA fallback for prod deployment"
```

### Task 1.2: Write `.dockerignore`

**Files:**
- Create: `/Users/ozvietnamdesktop/Desktop/yi/.dockerignore`

- [ ] **Step 1.2.1: Create .dockerignore**

```bash
cat > .dockerignore << 'EOF'
# Python
.venv/
**/__pycache__/
**/*.pyc
.pytest_cache/

# Node
client/webapp/node_modules/
client/webapp/dist/
**/.npm/

# Data (volume-mounted at runtime)
data/
!data/__init__.py

# Logs
*.log
**/_logs/

# IDE / OS
.DS_Store
.idea/
.vscode/
.cursor/
.claude/

# Git
.git/
.gitignore

# Docs (not needed in runtime image)
docs/
*.md
!README.md

# Tests
tests/
pytest.ini

# Vendor (already-installed third-party)
vendor/

# Misc
figures/
"thư viện sách/"
*.rtf
*.pdf
EOF

ls -lah .dockerignore
```

Expected: file exists, ~30 lines.

- [ ] **Step 1.2.2: Commit**

```bash
git add .dockerignore
git commit -m "add .dockerignore for Docker build context"
```

### Task 1.3: Write multi-stage Dockerfile

**Files:**
- Create: `/Users/ozvietnamdesktop/Desktop/yi/Dockerfile`

- [ ] **Step 1.3.1: Write Dockerfile**

```bash
cat > Dockerfile << 'EOF'
# syntax=docker/dockerfile:1.7

# ════════════════════════════════════════════════════════════
# Stage 1: Build Vue webapp
# ════════════════════════════════════════════════════════════
FROM node:20-alpine AS webapp-builder

WORKDIR /build

# Cache npm install layer
COPY client/webapp/package.json client/webapp/package-lock.json* ./
RUN npm install --no-audit --no-fund

# Build Vue dist
COPY client/webapp/ ./
RUN npm run build

# ════════════════════════════════════════════════════════════
# Stage 2: Python runtime
# ════════════════════════════════════════════════════════════
FROM python:3.14-slim AS runtime

# Use Asia/Ho_Chi_Minh timezone (matches Anh's locale)
ENV TZ=Asia/Ho_Chi_Minh \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install minimal system deps (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/share/zoneinfo/$TZ /etc/localtime

WORKDIR /app

# Install Python deps
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source (data/ excluded via .dockerignore, mounted at runtime)
COPY api/ ./api/
COPY core/ ./core/
COPY engine/ ./engine/
COPY collectors/ ./collectors/

# Copy Vue dist from stage 1
COPY --from=webapp-builder /build/dist ./client/webapp/dist

# Create data directory (mount point — actual data via volume)
RUN mkdir -p /app/data && chmod 755 /app/data

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/api/health || exit 1

# Run as non-root in production (data volume must be writable)
# Note: we keep root for now since SQLite + ai_keys.json chmod 600 needs careful UID alignment.
# TODO post-launch: add `RUN useradd -m appuser && chown -R appuser /app && USER appuser`

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

ls -lah Dockerfile
```

Expected: file exists ~50 lines.

- [ ] **Step 1.3.2: Build image locally on Mac (test)**

```bash
docker build -t yi-chronos:dev .
```

Expected output (last lines): `Successfully tagged yi-chronos:dev`. Time: 3-8 phút first build.

If error "no space left" or similar: `docker system prune -a`. If error on `python:3.14-slim`: check Docker Hub has tag — fall back to `python:3.13-slim` (Python 3.13 should work, project uses minimal features).

- [ ] **Step 1.3.3: Run container locally with data volume**

```bash
docker run --rm -d \
  --name yi-chronos-test \
  -p 8001:8000 \
  -v /Users/ozvietnamdesktop/Desktop/yi/data:/app/data \
  -e YI_CHRONOS_DATABASE_URL=sqlite:///data/yi_chronos.sqlite3 \
  yi-chronos:dev

sleep 5
docker logs yi-chronos-test 2>&1 | tail -20
```

Expected: log shows `Uvicorn running on http://0.0.0.0:8000`. No tracebacks.

- [ ] **Step 1.3.4: Smoke test endpoints**

```bash
curl -s http://127.0.0.1:8001/api/health
curl -sI http://127.0.0.1:8001/ | head -3
```

Expected: health returns JSON, `/` returns 200 with HTML content.

- [ ] **Step 1.3.5: Cleanup test container**

```bash
docker stop yi-chronos-test
```

- [ ] **Step 1.3.6: Commit**

```bash
git add Dockerfile
git commit -m "add multi-stage Dockerfile (Node build + Python runtime)"
```

### Task 1.4: Write `docker-compose.prod.yml`

**Files:**
- Create: `/Users/ozvietnamdesktop/Desktop/yi/docker-compose.prod.yml`

This compose file lives in the repo so Anh có thể đọc + edit easily. Trên VPS, em sẽ `git pull` repo và `docker compose -f docker-compose.prod.yml up -d`.

- [ ] **Step 1.4.1: Write compose file**

```bash
cat > docker-compose.prod.yml << 'EOF'
services:
  yi-chronos:
    image: ghcr.io/yi-chronos/yi-chronos:latest  # ← replaced by CI deploy
    container_name: yi-chronos
    restart: unless-stopped
    environment:
      - TZ=Asia/Ho_Chi_Minh
      - YI_CHRONOS_DATABASE_URL=sqlite:///data/yi_chronos.sqlite3
      # CORS: prod restricts to actual domain (set via .env on VPS)
      - YI_CHRONOS_CORS_ORIGINS=${YI_CHRONOS_CORS_ORIGINS:-https://kinhdich.online}
    volumes:
      - /opt/yi-chronos/data:/app/data
    networks:
      - traefik-network  # shared with existing Traefik on VPS
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.yi-chronos.rule=Host(`kinhdich.online`)"
      - "traefik.http.routers.yi-chronos.entrypoints=websecure"
      - "traefik.http.routers.yi-chronos.tls.certresolver=letsencrypt"
      - "traefik.http.services.yi-chronos.loadbalancer.server.port=8000"
      # Redirect HTTP → HTTPS
      - "traefik.http.routers.yi-chronos-insecure.rule=Host(`kinhdich.online`)"
      - "traefik.http.routers.yi-chronos-insecure.entrypoints=web"
      - "traefik.http.routers.yi-chronos-insecure.middlewares=https-redirect@docker"
      - "traefik.http.middlewares.https-redirect.redirectscheme.scheme=https"
      - "traefik.http.middlewares.https-redirect.redirectscheme.permanent=true"

networks:
  traefik-network:
    external: true
    name: traefik_default  # ← em sẽ verify actual name trên VPS in Task 2.4
EOF

ls -lah docker-compose.prod.yml
```

Expected: file exists ~35 lines.

- [ ] **Step 1.4.2: Commit**

```bash
git add docker-compose.prod.yml
git commit -m "add docker-compose.prod.yml with Traefik labels"
```

---

# Phase 2: VPS one-time setup

**Goal:** Prepare VPS Hostinger to host YI-Chronos. One-time manual ops (rsync data, create dirs, first deploy).

### Task 2.0: Setup DNS for `kinhdich.online` (Hostinger panel)

**Files:** none in repo. Manual ops trên Hostinger DNS panel.

⚠️ **Phải làm task này TRƯỚC khi deploy** — Traefik cần DNS resolve đúng IP thì Let's Encrypt mới issue được cert.

- [ ] **Step 2.0.1: Login Hostinger panel**

Mở `https://hpanel.hostinger.com` → Domains → `kinhdich.online` → DNS / Nameservers → DNS records.

- [ ] **Step 2.0.2: Add A records**

| Type | Name | Content | TTL |
|---|---|---|---|
| A | `@` (root) | `187.127.98.35` | 300 (5 min) |
| A | `www` | `187.127.98.35` | 300 |

⚠️ Nếu Hostinger đã có A record default trỏ về parking page: DELETE nó trước, sau đó add records trên.

- [ ] **Step 2.0.3: Wait propagation + verify**

```bash
# Trên Mac
for host in kinhdich.online www.kinhdich.online; do
  echo "=== $host ==="
  dig +short $host A
done
```

Expected: cả 2 lệnh return `187.127.98.35`. 

Propagation: thường 5-10 phút, max 60 phút. Nếu sau 60 phút vẫn empty: check lại Hostinger DNS records.

- [ ] **Step 2.0.4: Verify từ ngoài internet (không cache local)**

```bash
dig +short kinhdich.online A @1.1.1.1
dig +short kinhdich.online A @8.8.8.8
```

Expected: cả 2 (Cloudflare DNS + Google DNS) trả về `187.127.98.35`.

- [ ] **Step 2.0.5: (Optional) Add CAA record cho Let's Encrypt**

Trong Hostinger DNS panel, add:

| Type | Name | Flags | Tag | Value |
|---|---|---|---|---|
| CAA | `@` | 0 | issue | `letsencrypt.org` |

Lý do: ngăn cert authority khác issue cert cho domain này → security best practice.

### Task 2.1: SSH and verify VPS state

**Files:** none.

- [ ] **Step 2.1.1: Verify SSH access**

```bash
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 'echo OK; uptime'
```

Expected: `OK` + uptime line.

- [ ] **Step 2.1.2: Discover Traefik network name**

```bash
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 \
  'docker network ls --filter "name=traefik" --format "{{.Name}}"'
```

Expected: prints one or more network names. Likely `traefik_default` (compose default) or `traefik-traefik_default`. Note the EXACT name — needed for compose file Task 2.4.

- [ ] **Step 2.1.3: Discover Traefik cert resolver name**

```bash
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 \
  'docker inspect traefik-traefik-1 2>/dev/null | grep -A2 certificatesresolvers | head -20'
```

Expected: lines showing `--certificatesresolvers.<name>.acme...`. Note the resolver name (likely `letsencrypt` or `le`). If output empty, peek the compose file:

```bash
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 \
  'find /opt -name "docker-compose*.yml" -path "*traefik*" 2>/dev/null | head -3'
# Then cat the first hit to see config
```

### Task 2.2: Create directory structure on VPS

**Files:**
- Create on VPS: `/opt/yi-chronos/{data,backups,deploy}` directories

- [ ] **Step 2.2.1: Create bootstrap script**

```bash
mkdir -p scripts/deploy
cat > scripts/deploy/vps-bootstrap.sh << 'EOF'
#!/usr/bin/env bash
# One-time VPS prep for yi-chronos. Idempotent.
set -euo pipefail

YI_ROOT=/opt/yi-chronos

mkdir -p "$YI_ROOT"/{data,backups,deploy,logs}
chmod 755 "$YI_ROOT"
chmod 700 "$YI_ROOT"/data  # data dir restrictive (ai_keys.json lives here)

# Create empty placeholders if not migrated yet (avoids container crash on first run)
touch "$YI_ROOT"/data/yi_chronos.sqlite3
chmod 600 "$YI_ROOT"/data/yi_chronos.sqlite3

# .env file template (will be filled in Task 2.4)
if [ ! -f "$YI_ROOT"/.env ]; then
  cat > "$YI_ROOT"/.env << ENVEOF
# YI-Chronos production env
TZ=Asia/Ho_Chi_Minh
YI_CHRONOS_DATABASE_URL=sqlite:///data/yi_chronos.sqlite3
YI_CHRONOS_CORS_ORIGINS=https://kinhdich.online
ENVEOF
  chmod 600 "$YI_ROOT"/.env
fi

echo "Bootstrap done. Tree:"
ls -lah "$YI_ROOT"
EOF
chmod +x scripts/deploy/vps-bootstrap.sh
```

- [ ] **Step 2.2.2: Copy + run script on VPS**

```bash
scp -i ~/.ssh/id_ed25519_hostinger \
  scripts/deploy/vps-bootstrap.sh \
  root@187.127.98.35:/root/vps-bootstrap.sh

ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 \
  'bash /root/vps-bootstrap.sh'
```

Expected: prints "Bootstrap done." + tree listing /opt/yi-chronos.

- [ ] **Step 2.2.3: Commit**

```bash
git add scripts/deploy/vps-bootstrap.sh
git commit -m "add VPS bootstrap script for yi-chronos directory layout"
```

### Task 2.3: Migrate data from Mac to VPS

**Files:**
- Create: `scripts/deploy/migrate-data.sh`

Mac data dir = ~988MB. Em SẼ rsync NHỮNG file cần thiết (skip cache, logs, regenerable ephemeris):

- Include: `*.sqlite3`, `ai_keys.json`, `ai_provider_notes.json`, `yi_lexicon/`, `yi_wiki/`, `yi_restored/`, `yi_publishing/`, `published/`, `seeds/`, `hermes_yi/profiles/`, `phase2_reading/`
- Exclude: `cache/`, `_logs/`, `ephemeris/` (regen), `__pycache__/`

Estimated transfer: ~700MB. Time: 3-10 phút depending bandwidth.

- [ ] **Step 2.3.1: Write migrate script**

```bash
cat > scripts/deploy/migrate-data.sh << 'EOF'
#!/usr/bin/env bash
# Rsync data/ from Mac to VPS volume mount.
# Run từ project root: bash scripts/deploy/migrate-data.sh [--dry-run]
set -euo pipefail

DRY=""
[ "${1:-}" == "--dry-run" ] && DRY="--dry-run"

VPS_KEY=~/.ssh/id_ed25519_hostinger
VPS_HOST=root@187.127.98.35
VPS_DATA=/opt/yi-chronos/data

# Verify local data/ exists
if [ ! -d "data" ]; then
  echo "data/ not found in current dir. Run from project root." >&2
  exit 1
fi

# Confirm VPS dir exists
ssh -i $VPS_KEY $VPS_HOST "test -d $VPS_DATA" || {
  echo "VPS $VPS_DATA missing. Run vps-bootstrap.sh first." >&2
  exit 1
}

echo "=== Migrating data/ → VPS $VPS_DATA ==="
rsync -avz $DRY --progress \
  -e "ssh -i $VPS_KEY" \
  --include='*.sqlite3' \
  --include='ai_keys.json' \
  --include='ai_provider_notes.json' \
  --exclude='cache/' \
  --exclude='_logs/' \
  --exclude='ephemeris/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='*.log' \
  data/ $VPS_HOST:$VPS_DATA/

# Fix perms for sensitive files
ssh -i $VPS_KEY $VPS_HOST "
  chmod 600 $VPS_DATA/ai_keys.json 2>/dev/null || true
  chmod 600 $VPS_DATA/ai_provider_notes.json 2>/dev/null || true
  chmod 700 $VPS_DATA
  echo Done. Tree:
  du -sh $VPS_DATA/* 2>/dev/null | head -15
"
EOF
chmod +x scripts/deploy/migrate-data.sh
```

- [ ] **Step 2.3.2: Dry-run first**

```bash
bash scripts/deploy/migrate-data.sh --dry-run | head -40
```

Expected: list of files to transfer, NO actual transfer.

- [ ] **Step 2.3.3: Actual migrate**

```bash
bash scripts/deploy/migrate-data.sh
```

Expected: ~3-10 phút transfer, ends with size summary on VPS.

- [ ] **Step 2.3.4: Verify ai_keys.json on VPS**

```bash
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 \
  'ls -la /opt/yi-chronos/data/ai_keys.json && python3 -c "import json; print(list(json.load(open(\"/opt/yi-chronos/data/ai_keys.json\")).keys()))"'
```

Expected: file 600 perms, lists provider keys.

- [ ] **Step 2.3.5: Commit migrate script (script only, not data)**

```bash
git add scripts/deploy/migrate-data.sh
git commit -m "add rsync migrate-data script (Mac → VPS)"
```

### Task 2.4: Configure docker-compose for VPS

**Files:**
- Modify: `docker-compose.prod.yml` (replace placeholders with actual values from Task 2.1)

- [ ] **Step 2.4.1: Replace `yi-chronos` placeholder**

Get your GitHub username (the one who'll publish image to GHCR):

```bash
gh api user --jq .login 2>/dev/null || echo "<paste your gh username>"
```

Edit `docker-compose.prod.yml` line:
```yaml
image: ghcr.io/yi-chronos/yi-chronos:latest
```
→ replace `yi-chronos` with actual username (lowercase). Em sẽ ask Anh để confirm tên user.

- [ ] **Step 2.4.2: Replace Traefik network name**

Edit `docker-compose.prod.yml` bottom:
```yaml
networks:
  traefik-network:
    external: true
    name: traefik_default  # ← replace with actual from Task 2.1.2
```

Use the EXACT name printed in Task 2.1.2.

- [ ] **Step 2.4.3: Verify cert resolver name matches**

In `docker-compose.prod.yml` find:
```yaml
- "traefik.http.routers.yi-chronos.tls.certresolver=letsencrypt"
```

Replace `letsencrypt` with actual resolver name from Task 2.1.3 if different (e.g. `le`).

- [ ] **Step 2.4.4: Commit**

```bash
git add docker-compose.prod.yml
git commit -m "wire docker-compose.prod.yml to actual VPS Traefik network + resolver"
```

### Task 2.5: First manual deploy on VPS

**Goal:** Build image locally, push to GHCR manually, pull on VPS, start container.

- [ ] **Step 2.5.1: Create GHCR personal access token (PAT)**

On GitHub web: Settings → Developer settings → Personal access tokens (classic) → Generate new token.
- Name: `yi-chronos-ghcr-push`
- Scopes: `write:packages`, `read:packages`, `delete:packages`
- Copy token (starts with `ghp_...`)

- [ ] **Step 2.5.2: Login to GHCR locally**

```bash
echo "ghp_xxxxx" | docker login ghcr.io -u yi-chronos --password-stdin
```

Expected: `Login Succeeded`.

- [ ] **Step 2.5.3: Build + tag image (linux/amd64 for VPS)**

```bash
docker buildx build --platform linux/amd64 \
  -t ghcr.io/yi-chronos/yi-chronos:latest \
  --push \
  .
```

Expected: build (~5-10 phút first time, esp. with linux/amd64 cross-compile on Apple Silicon) → pushed to GHCR.

Verify image public/private:
```bash
# Make image public for unauthenticated pull (or skip if you want private + login on VPS)
gh api -X PATCH user/packages/container/yi-chronos --field visibility='public' 2>/dev/null || \
  echo "Set visibility manually at https://github.com/users/yi-chronos/packages/container/yi-chronos"
```

- [ ] **Step 2.5.4: Copy compose file to VPS**

```bash
scp -i ~/.ssh/id_ed25519_hostinger \
  docker-compose.prod.yml \
  root@187.127.98.35:/opt/yi-chronos/docker-compose.yml
```

- [ ] **Step 2.5.5: Pull + start on VPS**

```bash
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 << 'REMOTE'
cd /opt/yi-chronos
# Login to GHCR if image is private
# echo $GHCR_TOKEN | docker login ghcr.io -u yi-chronos --password-stdin
docker compose pull
docker compose up -d
sleep 5
docker compose ps
docker compose logs --tail 30
REMOTE
```

Expected: container `yi-chronos` running, logs show `Uvicorn running on http://0.0.0.0:8000`.

- [ ] **Step 2.5.6: Verify domain + SSL**

Wait 30-60s for Let's Encrypt to issue cert, then:

```bash
curl -sI https://kinhdich.online/api/health
curl -s https://kinhdich.online/api/health | head -5
```

Expected: HTTP 200, JSON health response. If first request returns SSL error, wait 30s and retry — Let's Encrypt takes a moment.

- [ ] **Step 2.5.7: Open in browser**

Mở `https://kinhdich.online/` trên Mac. Expected: trang web YI-Chronos load đầy đủ.

If 404 on `/`: SPA fallback ko hoạt động — quay lại Task 1.1 verify mount.
If CORS error in console: CORS chưa restrict → ok cho phase này (sẽ tighten Phase 4).

- [ ] **Step 2.5.8: Mark milestone**

```bash
git tag v0.1.0-vps-manual
git push origin v0.1.0-vps-manual
```

Update `docs/HANH-TRINH-NHAP-DAO.md` với entry "Lần update X — YI-Chronos lần đầu lên live tại https://kinhdich.online".

---

# Phase 3: GitHub Actions CI

**Goal:** Mỗi `git push` vào branch `main` → tự động build image → push GHCR → SSH VPS restart container. Edit-to-live trong 1-2 phút.

### Task 3.1: Generate deploy SSH key for GitHub Actions

**Files:** none in repo.

- [ ] **Step 3.1.1: Generate dedicated SSH key (KHÁC key chính của Anh)**

```bash
ssh-keygen -t ed25519 -f ~/.ssh/yi_chronos_deploy -N "" -C "github-actions-yi-chronos"
```

Expected: hai file `yi_chronos_deploy` + `yi_chronos_deploy.pub`.

- [ ] **Step 3.1.2: Add public key to VPS authorized_keys**

```bash
cat ~/.ssh/yi_chronos_deploy.pub | \
  ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 \
  'cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
```

- [ ] **Step 3.1.3: Verify deploy key works**

```bash
ssh -i ~/.ssh/yi_chronos_deploy -o StrictHostKeyChecking=accept-new \
  root@187.127.98.35 'echo deploy-key-ok'
```

Expected: `deploy-key-ok`.

### Task 3.2: Configure GitHub Secrets

- [ ] **Step 3.2.1: Set secrets via gh CLI**

```bash
# SSH private key for VPS
gh secret set VPS_SSH_KEY < ~/.ssh/yi_chronos_deploy

# VPS host
echo "187.127.98.35" | gh secret set VPS_HOST

# VPS user
echo "root" | gh secret set VPS_USER

# Verify
gh secret list
```

Expected: lists `VPS_SSH_KEY`, `VPS_HOST`, `VPS_USER`.

Note: GHCR token is NOT needed as a secret — workflow uses `${{ secrets.GITHUB_TOKEN }}` (auto-provided) with `packages: write` permission.

### Task 3.3: Write GitHub Actions workflow

**Files:**
- Create: `.github/workflows/deploy.yml`

- [ ] **Step 3.3.1: Create workflow**

```bash
mkdir -p .github/workflows
cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy YI-Chronos to VPS

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    outputs:
      image_tag: ${{ steps.meta.outputs.tags }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=raw,value=latest
            type=sha,prefix=sha-,format=short

      - name: Build and push image
        uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to VPS
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /opt/yi-chronos
            docker compose pull
            docker compose up -d --remove-orphans
            sleep 5
            docker compose ps
            docker image prune -af --filter "until=24h" || true

      - name: Verify live endpoint
        run: |
          for i in 1 2 3 4 5; do
            if curl -sf https://kinhdich.online/api/health; then
              echo "✅ Live"; exit 0
            fi
            echo "Retry $i..."; sleep 5
          done
          echo "❌ Health check failed"; exit 1
EOF
```

- [ ] **Step 3.3.2: Commit + push (this triggers first auto-deploy)**

```bash
git add .github/workflows/deploy.yml
git commit -m "add GitHub Actions deploy workflow (build → GHCR → SSH VPS)"
git push origin main
```

- [ ] **Step 3.3.3: Watch Actions run**

```bash
gh run watch
```

Expected: `build-and-push` succeeds (~3-5 phút), then `deploy` (~30s), then `Verify live endpoint` returns `✅ Live`.

If `build-and-push` fails: check logs `gh run view --log`. Common: image namespace conflicts (lowercase requirement), GHCR permissions.

If `deploy` fails on SSH: verify `VPS_SSH_KEY` secret has full private key including header lines `-----BEGIN OPENSSH PRIVATE KEY-----`.

### Task 3.4: Verify edit-to-live cycle

- [ ] **Step 3.4.1: Make a trivial change**

Edit `api/main.py` — change FastAPI title:
```python
app = FastAPI(title="YI-CHRONOS MVP — LIVE", version=ALGORITHM_VERSION, lifespan=lifespan)
```

- [ ] **Step 3.4.2: Push + verify**

```bash
git add api/main.py
git commit -m "smoke test: update FastAPI title"
git push
gh run watch
```

Then:
```bash
curl -s https://kinhdich.online/openapi.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['info']['title'])"
```

Expected: `YI-CHRONOS MVP — LIVE`.

- [ ] **Step 3.4.3: Revert smoke test**

```bash
git revert HEAD --no-edit
git push
```

- [ ] **Step 3.4.4: Tag milestone**

```bash
git tag v0.2.0-ci-live
git push origin v0.2.0-ci-live
```

---

# Phase 4: Production hardening

**Goal:** Restrict CORS, add auth gate cho settings tab (chỗ paste API keys), rate-limit AI endpoints, daily SQLite backup.

### Task 4.1: Tighten CORS in production

**Files:**
- Modify: `api/main.py` (CORS middleware block, ~line 147)

- [ ] **Step 4.1.1: Find current CORS config**

```bash
grep -n "allow_origins" api/main.py
```

Expected: line ~148 `allow_origins=["*"]`.

- [ ] **Step 4.1.2: Make CORS env-driven**

Replace the block:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    ...
)
```

With:
```python
_cors_env = os.environ.get("YI_CHRONOS_CORS_ORIGINS", "*").strip()
_cors_origins = ["*"] if _cors_env == "*" else [o.strip() for o in _cors_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

(Make sure `import os` is at top — line 3 area.)

- [ ] **Step 4.1.3: Commit**

```bash
git add api/main.py
git commit -m "make CORS origins env-driven (prod: https://yi-... only)"
git push
```

- [ ] **Step 4.1.4: Verify after deploy**

After `gh run watch` confirms deploy:
```bash
curl -sI -H "Origin: https://evil.com" \
  https://kinhdich.online/api/health | grep -i "access-control"
```

Expected: no `access-control-allow-origin: *` (or shows actual domain only).

### Task 4.2: Add Traefik basic auth gate for `/api/ai/*` settings endpoints

**Goal:** Anh tab ⚙️ Cài đặt phải nhập password mới gọi được. Public users xem được Mai Hoa cast/interpret nhưng không touch được key vault.

- [ ] **Step 4.2.1: Identify settings endpoints**

```bash
grep -n "@app.\(get\|post\|put\|delete\).*\"/api/ai/" api/main.py | head -20
```

Note these paths.

- [ ] **Step 4.2.2: Generate bcrypt hash for password**

```bash
# Choose a password (write down somewhere safe — KHÔNG paste vào chat)
htpasswd -nbB admin "MY_STRONG_PASSWORD_HERE"
# Output: admin:$2y$05$....
```

Replace `$` with `$$` for docker-compose escaping.

- [ ] **Step 4.2.3: Add Traefik auth middleware label**

In `docker-compose.prod.yml`, add labels:
```yaml
- "traefik.http.middlewares.yi-settings-auth.basicauth.users=admin:$$2y$$05$$..."
- "traefik.http.routers.yi-chronos-settings.rule=Host(`kinhdich.online`) && PathPrefix(`/api/ai/`)"
- "traefik.http.routers.yi-chronos-settings.entrypoints=websecure"
- "traefik.http.routers.yi-chronos-settings.tls.certresolver=letsencrypt"
- "traefik.http.routers.yi-chronos-settings.middlewares=yi-settings-auth"
- "traefik.http.routers.yi-chronos-settings.priority=10"
```

Note: this is for endpoints managing AI provider keys. If frontend tab Cài đặt also has UI routes, they need consideration too — but those are static SPA paths, không phải API. Tab Cài đặt sẽ HỎI password khi gọi `/api/ai/...`.

- [ ] **Step 4.2.4: Commit + verify**

```bash
git add docker-compose.prod.yml
git commit -m "add basic auth gate on /api/ai/* (settings endpoints)"
git push
gh run watch
```

Then test:
```bash
# Unauthenticated → 401
curl -sI https://kinhdich.online/api/ai/providers
# With auth → 200
curl -sI -u admin:MY_STRONG_PASSWORD_HERE https://kinhdich.online/api/ai/providers
```

Expected: first 401, second 200.

### Task 4.3: Backup SQLite cron

**Files:**
- Create: `scripts/deploy/backup-sqlite.sh`
- Create on VPS: cron entry

- [ ] **Step 4.3.1: Write backup script**

```bash
cat > scripts/deploy/backup-sqlite.sh << 'EOF'
#!/usr/bin/env bash
# Daily SQLite backup. Rotates: keep 7 daily + 4 weekly + 3 monthly.
set -euo pipefail

DATA=/opt/yi-chronos/data
BACKUPS=/opt/yi-chronos/backups
DATE=$(date +%Y-%m-%d)

mkdir -p "$BACKUPS"/{daily,weekly,monthly}

# Backup all *.sqlite3 using sqlite3 .backup (safe with WAL)
for db in "$DATA"/*.sqlite3 "$DATA"/yi_wiki/*.sqlite3; do
  [ -f "$db" ] || continue
  name=$(basename "$db" .sqlite3)
  sqlite3 "$db" ".backup '$BACKUPS/daily/${name}-${DATE}.sqlite3'"
done

# Rotate: keep last 7 daily, 4 weekly (Sundays), 3 monthly (first of month)
find "$BACKUPS/daily" -name "*.sqlite3" -mtime +7 -delete

# Weekly: copy Sunday's backup
if [ "$(date +%u)" -eq 7 ]; then
  cp -a "$BACKUPS"/daily/*-${DATE}.sqlite3 "$BACKUPS/weekly/" 2>/dev/null || true
  find "$BACKUPS/weekly" -name "*.sqlite3" -mtime +28 -delete
fi

# Monthly: first day of month
if [ "$(date +%d)" == "01" ]; then
  cp -a "$BACKUPS"/daily/*-${DATE}.sqlite3 "$BACKUPS/monthly/" 2>/dev/null || true
  find "$BACKUPS/monthly" -name "*.sqlite3" -mtime +90 -delete
fi

# Log
echo "[$(date)] Backup complete: $(du -sh $BACKUPS | cut -f1)" >> "$BACKUPS/backup.log"
EOF
chmod +x scripts/deploy/backup-sqlite.sh
```

- [ ] **Step 4.3.2: Install on VPS**

```bash
scp -i ~/.ssh/id_ed25519_hostinger \
  scripts/deploy/backup-sqlite.sh \
  root@187.127.98.35:/opt/yi-chronos/deploy/backup-sqlite.sh

ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 << 'REMOTE'
# Install sqlite3 cli if missing
which sqlite3 || apt-get update && apt-get install -y sqlite3
chmod +x /opt/yi-chronos/deploy/backup-sqlite.sh
# Add cron entry (3 AM Vietnam time = 20:00 UTC)
( crontab -l 2>/dev/null | grep -v 'yi-chronos backup' ; \
  echo "0 20 * * * /opt/yi-chronos/deploy/backup-sqlite.sh # yi-chronos backup" \
) | crontab -
crontab -l | tail -3
REMOTE
```

- [ ] **Step 4.3.3: Test manual run**

```bash
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 \
  '/opt/yi-chronos/deploy/backup-sqlite.sh && ls -lah /opt/yi-chronos/backups/daily/ | head'
```

Expected: backup files created với today's date.

- [ ] **Step 4.3.4: Commit**

```bash
git add scripts/deploy/backup-sqlite.sh
git commit -m "add daily SQLite backup script with rotation"
```

### Task 4.4: Rate limit AI endpoints (optional, low priority)

**Files:** docker-compose.prod.yml (Traefik middleware)

- [ ] **Step 4.4.1: Add rate limit middleware label**

In `docker-compose.prod.yml`, append to labels:
```yaml
- "traefik.http.middlewares.yi-ratelimit.ratelimit.average=10"
- "traefik.http.middlewares.yi-ratelimit.ratelimit.burst=30"
# Apply to main router
- "traefik.http.routers.yi-chronos.middlewares=yi-ratelimit"
```

- [ ] **Step 4.4.2: Commit + deploy**

```bash
git add docker-compose.prod.yml
git commit -m "add rate limit (10 req/s avg, 30 burst) on main router"
git push
```

- [ ] **Step 4.4.3: Verify**

```bash
for i in $(seq 1 50); do
  curl -s -o /dev/null -w "%{http_code}\n" \
    https://kinhdich.online/api/health
done | sort | uniq -c
```

Expected: most `200`, some `429` if exceed burst.

---

# Phase 5: End-to-end verification

**Goal:** Verify full UX works on live URL.

### Task 5.1: Browser smoke test

- [ ] **Step 5.1.1: Open live URL**

Mở `https://kinhdich.online/` trong Chrome.

Verify checklist:
- [ ] Page loads, no console errors
- [ ] Tab Mai Hoa visible
- [ ] Tab ⚙️ Cài đặt visible (basic auth prompt khi click)
- [ ] DevTools Network: tất cả `/api/...` returns 200, `/assets/...` returns 200, HTML returns 200

- [ ] **Step 5.1.2: Test Mai Hoa cast end-to-end**

1. Tab Mai Hoa
2. Nhập câu hỏi
3. Click "Lập quẻ"
4. Verify response shows 4 BƯỚC (Lời quẻ, Thể-Dụng, ngoại ứng, tư thế) — per IRON RULE #4

If error 500 on `/api/luc-hao/cast` or `/api/mai-hoa/cast`: SSH check logs:
```bash
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 \
  'docker logs yi-chronos --tail 50'
```

Common: `ai_keys.json` không có key cho provider → setup keys via tab Cài đặt.

- [ ] **Step 5.1.3: Test ai_keys.json NOT exposed publicly**

```bash
curl -sI https://kinhdich.online/data/ai_keys.json
curl -sI https://kinhdich.online/ai_keys.json
```

Expected: both 404 (not exposed via SPA fallback because not in `dist/`).

- [ ] **Step 5.1.4: Test no debug endpoints exposed**

```bash
curl -s https://kinhdich.online/openapi.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['paths']), 'routes')"
```

If you want to hide OpenAPI in prod:
- Modify `api/main.py`: `FastAPI(docs_url=None, redoc_url=None, openapi_url=None)` if env `YI_CHRONOS_HIDE_DOCS=1`.

### Task 5.2: Update HANH-TRINH-NHAP-DAO.md

**Files:**
- Modify: `docs/HANH-TRINH-NHAP-DAO.md` — add entry "Lần update X — VPS LIVE"

- [ ] **Step 5.2.1: Append milestone entry**

Add at appropriate timeline location:
```markdown
### Lần update <next number> — 2026-05-XX — YI-Chronos LIVE trên VPS

- URL: https://kinhdich.online
- Stack: Docker + Traefik + GitHub Actions CI
- Edit-to-live: git push main → ~1-2 phút
- VPS: Hostinger 187.127.98.35 (Ubuntu 24.04, 2 vCPU, 8GB)
- Co-tenant với OZ stack (Hermes pool, Traefik, n8n) — không conflict
- Backup: cron daily SQLite → /opt/yi-chronos/backups/
- Auth gate: /api/ai/* yêu cầu basic auth admin
- Next: mua domain riêng + thắt CORS theo domain mới
```

- [ ] **Step 5.2.2: Commit**

```bash
git add docs/HANH-TRINH-NHAP-DAO.md
git commit -m "log milestone: YI-Chronos live on VPS"
git push
```

---

# Phase 6: Operations runbook

**Goal:** Anh có 1 cheatsheet để vận hành: rollback, view logs, restore from backup, troubleshoot.

### Task 6.1: Write DEPLOY-RUNBOOK.md

**Files:**
- Create: `docs/DEPLOY-RUNBOOK.md`

- [ ] **Step 6.1.1: Write runbook**

```bash
cat > docs/DEPLOY-RUNBOOK.md << 'EOF'
# YI-Chronos Deploy Runbook

> Cheatsheet vận hành. Cập nhật khi process thay đổi.

## Live URL
- Production: https://kinhdich.online
- VPS: `ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35`
- Container: `yi-chronos` (Docker)
- Image: `ghcr.io/yi-chronos/yi-chronos:latest`

## Normal edit flow

```bash
# 1. Edit code on Mac
# 2. Test local
source .venv/bin/activate
python3 -m uvicorn api.main:app --reload --port 8000

# 3. Push to deploy
git add -A
git commit -m "your message"
git push origin main

# 4. Watch CI
gh run watch
```

Edit-to-live: ~3-5 phút (build 2-3 phút + deploy 30s + cert/health 30s).

## View live logs

```bash
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 \
  'docker logs yi-chronos --tail 100 -f'
```

## Restart container without rebuild

```bash
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 \
  'cd /opt/yi-chronos && docker compose restart'
```

## Rollback to previous image

```bash
# Find last good tag in GHCR
gh api /users/yi-chronos/packages/container/yi-chronos/versions --jq '.[0:5][].metadata.container.tags'

# Pin specific sha tag on VPS
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 << 'REMOTE'
cd /opt/yi-chronos
# Edit docker-compose.yml: image: ghcr.io/yi-chronos/yi-chronos:sha-abc1234
nano docker-compose.yml
docker compose pull
docker compose up -d
REMOTE
```

Or use `git revert` on Mac + push (full CI re-run, ~3-5 phút).

## Restore SQLite from backup

```bash
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 << 'REMOTE'
ls /opt/yi-chronos/backups/daily/
# Stop container
cd /opt/yi-chronos && docker compose stop yi-chronos
# Restore (replace <db_name> + <date>)
cp /opt/yi-chronos/backups/daily/<db_name>-<date>.sqlite3 \
   /opt/yi-chronos/data/<db_name>.sqlite3
chmod 600 /opt/yi-chronos/data/<db_name>.sqlite3
docker compose up -d
REMOTE
```

## Update data/ from Mac (after restoration/wiki work)

```bash
bash scripts/deploy/migrate-data.sh
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 \
  'cd /opt/yi-chronos && docker compose restart'
```

## Troubleshoot common issues

**1. Container restart loop**
```bash
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 \
  'docker logs yi-chronos --tail 50'
```
Common: missing `ai_keys.json` (re-run migrate-data.sh), corrupted SQLite (restore from backup).

**2. SSL cert error**
```bash
ssh -i ~/.ssh/id_ed25519_hostinger root@187.127.98.35 \
  'docker logs traefik-traefik-1 2>&1 | grep -i acme | tail -20'
```
Common: Let's Encrypt rate limit (wait 1h), DNS not propagated (verify `dig kinhdich.online`).

**3. 502 Bad Gateway**
- Container down: `docker compose up -d`
- Traefik network mismatch: `docker network inspect <traefik_net> | grep yi-chronos`

**4. GitHub Actions deploy fails**
- SSH key issue: regenerate, re-add to authorized_keys, update `VPS_SSH_KEY` secret
- GHCR push fails: token expired or wrong permissions

## Cost & monitoring

- VPS: $0 incremental (5-year prepaid)
- LLM: charged per ai_keys provider (DeepSeek/Anthropic/etc.)
- Bandwidth: < 10GB/month projected (page weight ~500KB)

## Domain upgrade path

When ready to leave `.nip.io`:
1. Buy domain (~$10/year), point A record to 187.127.98.35
2. Update `docker-compose.prod.yml` Host() rule
3. Update CORS env in `.env`
4. `git push` → auto deploy + Traefik issues new cert

## Contact / lessons

Lessons từ deploy này → ghi vào `docs/HANH-TRINH-NHAP-DAO.md`.
EOF
```

- [ ] **Step 6.1.2: Commit**

```bash
git add docs/DEPLOY-RUNBOOK.md
git commit -m "add deploy runbook with rollback + troubleshoot procedures"
git push
```

---

# Self-review checklist

Before declaring plan complete, em verify:

**1. Spec coverage:**
- ✅ Goal "đưa live": Phase 1-3 build + deploy
- ✅ Goal "sửa liên tục từ Mac": Phase 3 CI/CD
- ✅ Anh's choice "subdomain .nip.io tạm": Phase 2.4 uses `kinhdich.online`
- ✅ Anh's choice "8 providers riêng": ai_keys.json mount + migrate, không integrate Hermes pool
- ✅ Anh's choice "git push → GHCR auto deploy": Phase 3 full workflow
- ✅ Anh's choice "plan trước, review": this document
- ✅ Co-tenant với OZ stack: docker-compose external network + Traefik labels
- ✅ Security: CORS tighten, basic auth on /api/ai/*, SQLite backup
- ✅ Rollback path: documented
- ✅ Cost: $0 incremental

**2. Placeholder scan:**
- `yi-chronos` ← intentional placeholder, replaced in Task 2.4.1
- `yi-chronos`, `yi-chronos` in command examples ← intentional, em sẽ hỏi Anh confirm
- `MY_STRONG_PASSWORD_HERE` ← intentional, Anh tự chọn

**3. Type consistency:**
- Container name `yi-chronos` consistent across compose, runbook, CI
- Volume path `/opt/yi-chronos/data` consistent
- Image name `ghcr.io/yi-chronos/yi-chronos` consistent

**4. Identified gaps (Anh quyết khi gặp):**
- Ollama provider in registry → khi gọi từ VPS sẽ fail (no Ollama). Two options: (a) disable Ollama provider env-driven, (b) tunnel Mac→VPS Tailscale. Recommended (a) cho phase này.
- Python 3.14 vs 3.13: Dockerfile dùng `python:3.14-slim`. Nếu image tag chưa có khi build, fallback `3.13-slim` — tested manually in Task 1.3.2.
- Mac data update flow: rsync `migrate-data.sh` chạy manual. Future: auto webhook khi Mac restoration job done.

# Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-19-vps-deploy.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — Em dispatch fresh subagent per task, review giữa task, fast iteration. Tốt cho infrastructure task vì mỗi phase có verification rõ ràng (build, curl, SSL check).

2. **Inline Execution** — Execute trong session này với batch checkpoints. Tốt nếu Anh muốn xem real-time.

**Em cần Anh confirm 3 thứ trước khi execute:**

1. **GitHub username** để substitute `yi-chronos` (image namespace).
2. **Password admin** cho basic auth Task 4.2 (Anh chọn, không paste vào chat — em sẽ hỏi qua AskUserQuestion với password masked).
3. **Có muốn em DRY-RUN từng phase 1 không** (build local, build VPS, test, BUT không commit/push) — để Anh quan sát trước khi commit `main`.

**Which approach?**
