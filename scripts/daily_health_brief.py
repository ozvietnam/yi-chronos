#!/usr/bin/env python3
"""Daily Health Brief — sinh báo cáo sức khỏe HÔM NAY cho founder.

Chạy mỗi sáng 7h qua cron. Output:
- data/daily_briefs/YYYY-MM-DD.md (markdown lưu lại)
- Optional: send qua Hermes Telegram nếu config có

Logic: gọi engine weekly_planner cho ngày HÔM NAY (1 ngày).
"""
from __future__ import annotations
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Founder birth (default — có thể override qua ENV)
FOUNDER_BIRTH = os.environ.get("YI_FOUNDER_BIRTH", "1988-06-05T23:30:00")
FOUNDER_GENDER = os.environ.get("YI_FOUNDER_GENDER", "nam")
FOUNDER_TZ = "Asia/Ho_Chi_Minh"


def get_today_vn() -> str:
    """Lấy ngày hiện tại theo VN timezone."""
    vn_tz = timezone(timedelta(hours=7))
    return datetime.now(vn_tz).strftime("%Y-%m-%d")


def build_daily_brief(date_str: str) -> str:
    """Build daily brief markdown cho 1 ngày."""
    from engine.dong_y.weekly_planner import build_weekly_plan

    # Build 1-day plan (weekly với start = today, lấy day[0])
    weekly = build_weekly_plan(
        birth_datetime_local=FOUNDER_BIRTH,
        timezone=FOUNDER_TZ,
        gender=FOUNDER_GENDER,
        start_date=date_str,
    )
    today = weekly.days[0]

    # Cảnh báo đặc biệt theo level
    cb = ""
    if today["level"] == "🔴":
        cb = "\n⚠️ **HÔM NAY KIM khắc MỘC** — Anh cần:\n- Quàng khăn cổ + tránh gió lùa\n- Tránh tranh luận / suy nghĩ căng\n- Niệm `80.20` (cổ vai gáy) sáng + `260.50.30.80` (nửa đầu trái) trước stress\n- Ngủ sớm hơn\n"
    elif today["level"] == "🟢":
        cb = "\n✨ **HÔM NAY thuận** — Mộc dưỡng hoặc Thủy nuôi. Anh:\n- Niệm `640` mỗi sáng để bồi Can-Thận\n- Hành động chính được\n- Đậu đen + sách sâu vào buổi tối\n"
    elif today["level"] == "🟡":
        cb = "\n💛 **HÔM NAY Hỏa tiết khí** — Mộc Anh tỏa năng lượng. Cẩn:\n- Tránh suy nghĩ căng (đốt Can → đau nửa đầu trái dễ bùng)\n- Thiền 15-20 phút buổi tối\n- Tránh tranh luận căng\n"
    elif today["level"] == "🟠":
        cb = "\n🟠 **HÔM NAY Tài (Thổ) hao** — Mộc khắc Thổ. Cẩn:\n- Dưỡng Tỳ Vị (gạo lứt, bí đỏ, ăn ấm)\n- Không ép kinh doanh / mở rộng\n- Bài niệm: `650.30.820` (KHÍ NGŨ TẠNG)\n"

    md = f"""# 🌿 Daily Health Brief — {date_str}

## {today['level']} {today['weekday_vn']} {date_str} — {today['can_chi']}

**Quan hệ với Day Master (Mộc):** {today['relation_to_dm']}

**⏰ Giờ vượng:** {today['gio_vuong']} → tạng **{today['tang_dac_biet']}**

**🎭 Mood ngày:** {today['mood']}
{cb}
---

## 🌅 Bài niệm SÁNG
`{today['bai_niem_sang']}`

## 🌙 Bài niệm TỐI
`{today['bai_niem_toi']}`

## 🍵 Thực phẩm dưỡng
{chr(10).join(f"- {f}" for f in today['thuc_an_dac_biet'])}

## 🚶 Vận động
{today['van_dong']}

{f"## 💡 Reminder{chr(10)}{today['reminder']}" if today['reminder'] else ""}

---

🪷 _"Tâm đức là số một" — TTT chương 26._
_Engine: cấu trúc khí. Hành động: của Anh._
"""
    return md


def save_brief(date_str: str, md: str) -> Path:
    """Lưu brief vào data/daily_briefs/."""
    out_dir = ROOT / "data" / "daily_briefs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{date_str}.md"
    out_path.write_text(md, encoding="utf-8")
    return out_path


def send_telegram(md: str) -> bool:
    """Optional: gửi qua Hermes Telegram nếu có config.

    Returns True nếu gửi thành công.
    """
    # Check Hermes config
    config_path = ROOT / "data" / "hermes_yi" / "config.json"
    if not config_path.exists():
        return False

    try:
        import json
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
        telegram_token = cfg.get("telegram_bot_token") or os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = cfg.get("telegram_founder_chat_id") or os.environ.get("TELEGRAM_FOUNDER_CHAT_ID")
        if not telegram_token or not chat_id:
            return False

        import urllib.request
        import urllib.parse
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": md[:4000],  # Telegram limit
            "parse_mode": "Markdown",
        }).encode()
        urllib.request.urlopen(url, data=data, timeout=10)
        return True
    except Exception as e:
        print(f"Telegram error: {e}", file=sys.stderr)
        return False


def main():
    date_str = get_today_vn()
    print(f"📅 Building daily brief for {date_str}...")
    md = build_daily_brief(date_str)
    out_path = save_brief(date_str, md)
    print(f"✅ Saved: {out_path}")

    # Optional Telegram
    if send_telegram(md):
        print(f"📨 Sent to Telegram")
    else:
        print(f"⏭ Telegram skipped (no config)")

    print(f"\n--- PREVIEW ---")
    print(md[:1500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
