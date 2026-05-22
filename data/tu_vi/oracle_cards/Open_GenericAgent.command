#!/bin/zsh
set -u

WORKDIR="/Users/ozvietnamdesktop/Desktop/yi/data/tu_vi/oracle_cards"
VENV_PYTHON="$WORKDIR/runtime/genericagent-venv/bin/python"
APP_FILE="/Users/ozvietnamdesktop/Library/CloudStorage/GoogleDrive-ceo@ngantin.vn/Bộ nhớ dùng chung/Oz vận hành 2025/marketting AI 2026/lead hunter/scripts/GenericAgent/frontends/stapp2.py"
LOG_DIR="$WORKDIR/logs"
LOG_FILE="$LOG_DIR/genericagent-streamlit.log"
PORT="8507"
URL="http://localhost:$PORT"

mkdir -p "$LOG_DIR"

if ! test -x "$VENV_PYTHON"; then
  osascript -e 'display alert "GenericAgent chưa chạy được" message "Không tìm thấy Python venv trong runtime/genericagent-venv. Hãy mở lại Codex để kiểm tra cài đặt."'
  exit 1
fi

if ! test -f "$APP_FILE"; then
  osascript -e 'display alert "GenericAgent chưa chạy được" message "Không tìm thấy frontends/stapp2.py trong thư mục Google Drive GenericAgent."'
  exit 1
fi

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  open "$URL"
  exit 0
fi

cd "$WORKDIR" || exit 1

export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_HEADLESS=true

(
  for _ in {1..30}; do
    if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
      open "$URL"
      exit 0
    fi
    sleep 0.5
  done
) &

echo "GenericAgent dang khoi dong..."
echo "URL: $URL"
echo "Log: $LOG_FILE"
echo
echo "Giu cua so Terminal nay mo khi dang dung GenericAgent."
echo "Muon tat he thong: quay lai cua so nay va bam Control+C, hoac dong cua so Terminal."
echo

exec "$VENV_PYTHON" -m streamlit run "$APP_FILE" \
  --server.port "$PORT" \
  --server.address localhost \
  2>&1 | tee "$LOG_FILE"
