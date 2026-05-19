#!/usr/bin/env bash
# Daily SQLite backup for YI-Chronos on VPS.
# Layout: /opt/yi-chronos/backups/{daily,weekly,monthly}
# Retention: 7 daily, 4 weekly (Sunday), 3 monthly (1st of month)
set -euo pipefail

DATA=/opt/yi-chronos/data
BACKUPS=/opt/yi-chronos/backups
DATE=$(date +%Y-%m-%d)

mkdir -p "$BACKUPS"/{daily,weekly,monthly}

# Find all .sqlite3 files in data/ (recursive, skip backup dir itself)
find "$DATA" -name "*.sqlite3" -not -path "$BACKUPS/*" -print0 2>/dev/null | \
while IFS= read -r -d '' db; do
  rel="${db#$DATA/}"                       # path relative to data/
  safe_name=$(echo "$rel" | tr '/' '_')    # foo/bar.sqlite3 → foo_bar.sqlite3
  out="$BACKUPS/daily/${safe_name%.sqlite3}-${DATE}.sqlite3"
  # SQLite .backup is safe with WAL — no lock contention with running container
  sqlite3 "$db" ".backup '$out'" 2>/dev/null || {
    echo "[$(date)] WARN: backup failed for $db" >> "$BACKUPS/backup.log"
    continue
  }
done

# Rotate daily — keep last 7
find "$BACKUPS/daily" -name "*.sqlite3" -mtime +7 -delete 2>/dev/null || true

# Weekly: copy today's daily backups (only on Sunday, day-of-week=7)
if [ "$(date +%u)" -eq 7 ]; then
  cp -a "$BACKUPS"/daily/*-"$DATE".sqlite3 "$BACKUPS/weekly/" 2>/dev/null || true
  find "$BACKUPS/weekly" -name "*.sqlite3" -mtime +28 -delete 2>/dev/null || true
fi

# Monthly: copy today's daily backups (only on day 01)
if [ "$(date +%d)" = "01" ]; then
  cp -a "$BACKUPS"/daily/*-"$DATE".sqlite3 "$BACKUPS/monthly/" 2>/dev/null || true
  find "$BACKUPS/monthly" -name "*.sqlite3" -mtime +90 -delete 2>/dev/null || true
fi

# Compact log entry
size=$(du -sh "$BACKUPS" 2>/dev/null | cut -f1)
count=$(find "$BACKUPS/daily" -name "*.sqlite3" 2>/dev/null | wc -l)
echo "[$(date)] OK: $count daily backups, total $size" >> "$BACKUPS/backup.log"
