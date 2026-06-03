#!/bin/bash
# Cron wrapper for daily health brief (7h sáng VN time mỗi ngày)
# Setup: crontab entry → "0 7 * * * /Users/ozvietnamdesktop/Desktop/yi/scripts/cron_daily_health_brief.sh"

set -e
cd /Users/ozvietnamdesktop/Desktop/yi
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

LOG="/tmp/yi_daily_health.log"
echo "════════════════════════════════════════" >> "$LOG"
echo "$(date '+%Y-%m-%d %H:%M:%S') START" >> "$LOG"

/Users/ozvietnamdesktop/Desktop/yi/.venv/bin/python3 \
    /Users/ozvietnamdesktop/Desktop/yi/scripts/daily_health_brief.py \
    >> "$LOG" 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') END" >> "$LOG"
echo "" >> "$LOG"
