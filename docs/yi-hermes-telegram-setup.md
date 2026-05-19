# @Yihermesbot — YI-Hermes Telegram Bridge

**Bot:** [@Yihermesbot](https://t.me/Yihermesbot) (id: 8700536245)
**Bridge:** long-polling Python service trong `engine/yi_hermes/telegram_bridge.py`
**Token:** lưu tại `.env.local` (gitignored — KHÔNG commit)

## 🚨 BẢO MẬT — ĐỌC TRƯỚC

Token bot xuất hiện trong tin nhắn của @BotFather → có nguy cơ bị log/cache. **Sau khi test xong, anh nên rotate token**:

1. Mở chat với [@BotFather](https://t.me/BotFather)
2. Gõ `/token`
3. Chọn `Yihermesbot`
4. Bấm `revoke` để hủy token cũ
5. BotFather sinh token mới → copy
6. Update `.env.local`:
   ```bash
   # Sửa dòng:
   YI_HERMES_TELEGRAM_TOKEN=<token-mới>
   ```
7. Restart bridge:
   ```bash
   pkill -f "yi_hermes.telegram_bridge"
   ./scripts/yi-hermes-telegram &
   ```

## 🏗️ Kiến trúc

```
Telegram user → @Yihermesbot → Telegram API
                                       │
                                  long-polling
                                       │
                                       ▼
                       engine/yi_hermes/telegram_bridge.py
                                       │
                       ┌───────────────┼────────────────┐
                       ▼               ▼                ▼
              slash commands    HermesChat.send()   Soul+Memory
              /start /help      (web chat engine)   per user
              /modules /me                           (telegram:user_id)
              /forget /clear
```

Mỗi Telegram user → unique `soul_key = telegram:{user_id}` → riêng Soul + Memory + Glossary views. Không share với user web (vì web dùng `active_person_id` từ ProfilesStore).

## 📋 Slash commands

| Lệnh | Tác dụng |
|---|---|
| `/start` | Chào + giới thiệu, hiện session count |
| `/help` | Liệt kê lệnh |
| `/modules` | 7 trường phái (Đông + Tây) |
| `/me` | Soul + Facts + Summaries + Top terms |
| `/forget` | Xoá Soul (giữ Memory) |
| `/clear` | Xoá lịch sử chat hiện tại (in-memory) |

Câu hỏi thường (không phải slash) → routed qua `HermesChat.send()`:
- Glossary hit (free, instant)
- Council suggest (nếu mention "tranh luận", "hội đồng")
- LLM chat (z.ai glm-4.5-flash mặc định)

## 🚀 Setup & vận hành

### Lần đầu (đã làm xong)
1. ✅ Token trong `.env.local` (`YI_HERMES_TELEGRAM_TOKEN`)
2. ✅ Bridge module `engine/yi_hermes/telegram_bridge.py`
3. ✅ Wrapper `scripts/yi-hermes-telegram`
4. ✅ httpx dependency có sẵn trong `.venv`

### Khởi động bridge

**Foreground (test):**
```bash
./scripts/yi-hermes-telegram
# Ctrl+C để dừng
```

**Background (recommended):**
```bash
nohup ./scripts/yi-hermes-telegram > /tmp/yi-hermes-tg.log 2>&1 &
disown
```

**Xem log:**
```bash
tail -f /tmp/yi-hermes-tg.log
```

**Dừng background:**
```bash
pkill -f "yi_hermes.telegram_bridge"
```

### Restrict access (optional)

Mặc định bot **OPEN** — ai có link cũng chat được. Để restrict, set trong `.env.local`:

```bash
YI_HERMES_TELEGRAM_ALLOWED_USERS=123456789,987654321
```

Lấy `user_id` Telegram của anh qua [@userinfobot](https://t.me/userinfobot).

## 🔄 Auto-restart trên Mac (launchd)

Để bridge tự khởi động khi Mac boot:

```bash
cat > ~/Library/LaunchAgents/com.yi-hermes.telegram.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yi-hermes.telegram</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/ozvietnamdesktop/Desktop/yi/scripts/yi-hermes-telegram</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/ozvietnamdesktop/Desktop/yi</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/yi-hermes-tg.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/yi-hermes-tg.err</string>
</dict>
</plist>
EOF
launchctl load ~/Library/LaunchAgents/com.yi-hermes.telegram.plist
```

Dừng:
```bash
launchctl unload ~/Library/LaunchAgents/com.yi-hermes.telegram.plist
```

## 💰 Cost

Mỗi câu hỏi qua bridge:
- **Slash commands** (/start, /me, /modules): **$0** (no LLM)
- **Glossary hit** (single term): **$0** (no LLM)
- **LLM chat** (z.ai glm-4.5-flash): **~$0** (free tier)
- **LLM chat** (claude-sonnet-4-5, nếu cấu hình): ~$0.01-0.03

Bridge dùng `glm-4.5-flash` mặc định → effectively free vì model nằm trong free tier của z.ai.

## 🛡️ Tách biệt với Hermes Agent v0.13.0

Bridge này **KHÔNG** dùng Hermes Agent v0.13.0 (NousResearch) installed tại `vendor/hermes-agent/`. Đó là CLI agent dùng cho dev work, chạy độc lập.

Bridge chỉ call `HermesChat.send()` của YI-Hermes (web concierge, in-process FastAPI).

**Khi nào dùng cái nào?**
- `@Yihermesbot` (Telegram): user-facing, tử vi cho người dùng cuối
- `./scripts/hermes-yi` (CLI): dev work với Hermes Agent's tool ecosystem

## 📊 Monitor

Trong UI YI-CHRONOS web, anh có thể xem:
- Soul + Memory của Telegram users qua `GET /api/yi-hermes/memory/telegram:{user_id}/full`
- Glossary views: `GET /api/yi-hermes/memory/telegram:{user_id}/top-terms`

## ⚠️ Limitations hiện tại

1. **In-memory history**: lịch sử chat (10 turn gần nhất) chỉ giữ trong RAM. Restart bridge → mất. Memory facts/summaries persistent — chỉ history conversation bị clear.
2. **No streaming**: response trả 1 lần khi LLM xong. Câu hỏi phức tạp có thể chờ 5-15s.
3. **No media**: hiện chỉ text. Future: voice memo → STT → chat.
4. **No webhook**: dùng long-polling. Production scale có thể chuyển sang webhook để tiết kiệm resource.
5. **Markdown rendering**: Telegram dùng Markdown V1 — một số ký tự đặc biệt có thể vỡ format → bridge auto-fallback sang plain text.
