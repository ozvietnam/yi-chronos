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

# Install minimal system deps (curl for healthcheck, sqlite3 for backup)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/share/zoneinfo/$TZ /etc/localtime

# WORKDIR matches Mac path to keep absolute path references working
# (Future cleanup task: refactor 20+ hardcoded paths to Path(__file__).resolve()...)
WORKDIR /Users/ozvietnamdesktop/Desktop/yi

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

# Create data mount point (actual data via volume)
RUN mkdir -p ./data && chmod 755 ./data

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/api/health || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
