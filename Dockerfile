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

# Install minimal system deps + WeasyPrint libs (Pango/Cairo/HarfBuzz for PDF rendering)
# Build deps (g++ + python3-dev) needed for sxtwl + ephem C++ extensions on Python 3.14
# (sxtwl chưa có wheel cp314 trên PyPI tại thời điểm Python 3.14 release)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    curl \
    sqlite3 \
    g++ \
    python3-dev \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libharfbuzz0b \
    libgdk-pixbuf-2.0-0 \
    libffi8 \
    libfontconfig1 \
    shared-mime-info \
    fonts-dejavu-core \
    fonts-noto-cjk \
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

# Copy knowledge citations (knowledge from sách — version-controlled,
# must be in image, not via volume mount which contains user data).
# Volume mount /opt/yi-chronos/data sẽ shadow data/ → cần copy skills/
# vào path KHÁC trong image, hoặc copy vào data/ rồi container đọc
# direct nhưng runtime volume mount sẽ overwrite. Workaround: copy
# vào /app/embedded_data/, engine resolve path qua env var.
RUN mkdir -p ./embedded_data/hermes_yi/skills
COPY data/hermes_yi/skills/kinh-dich/ ./embedded_data/hermes_yi/skills/kinh-dich/

# Restored books markdown (live reading library)
# Path /app/embedded_data/restored_books/ — engine resolve qua env hoặc fallback
RUN mkdir -p ./embedded_data/restored_books
COPY data/restored_books/ ./embedded_data/restored_books/

# Seed JSON paradigm files (cung Phu Thê Trung Châu, Mai Hoa thời tiết, Bát Tự ...)
# Volume mount /opt/yi-chronos/data shadows data/, so seeds must be in embedded_data/
RUN mkdir -p ./embedded_data/seeds
COPY data/seeds/ ./embedded_data/seeds/

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
