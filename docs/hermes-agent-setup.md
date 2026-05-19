# Hermes Agent v0.13.0 — Setup riêng cho YI-CHRONOS

**Ngày cài:** 2026-05-11
**Version:** v0.13.0 (Tenacity Release, 2026-05-07)
**Repo:** https://github.com/NousResearch/hermes-agent (MIT)

## 🛡️ Cách ly với Hermes của Mac

Anh đã có Hermes v0.12.0 tại `~/.hermes/` đang phục vụ workflow hàng ngày. Instance này TÁCH HOÀN TOÀN:

| Thuộc tính | Hermes Mac | **Hermes YI-CHRONOS** |
|---|---|---|
| **Source code** | `~/.hermes/hermes-agent/` | `vendor/hermes-agent/` |
| **Binary** | `~/.local/bin/hermes` | `vendor/hermes-agent/.venv/bin/hermes` |
| **Data + config** (`HERMES_HOME`) | `~/.hermes/` | `data/hermes_yi/` |
| **Python** | 3.11.15 | 3.14.4 |
| **Version** | v0.12.0 | **v0.13.0** (mới hơn 864 commits) |
| **Wrapper** | `hermes` (PATH) | `./scripts/hermes-yi` |

Hai instance không chia sẻ:
- Skills (mỗi cái có skill library riêng)
- Conversations / sessions
- Auth credentials (OAuth, API keys)
- Cron jobs
- Memory / FTS index

## 📁 Layout files trong dự án

```
YI-CHRONOS/
├── vendor/hermes-agent/       # source code (clone NousResearch/hermes-agent)
│   ├── .venv/                  # Python venv isolated cho hermes
│   ├── src/
│   ├── pyproject.toml
│   └── ...
├── data/hermes_yi/             # HERMES_HOME — config + data
│   ├── .env                    # API keys (anh sẽ paste)
│   ├── config.yaml             # provider/model config
│   ├── skills/                 # skills tự tạo riêng cho YI
│   ├── memory.db               # SQLite memory
│   └── sessions/               # conversation history
└── scripts/
    └── hermes-yi               # wrapper: export HERMES_HOME + exec
```

## 🚀 Cách dùng

### Lần đầu — setup wizard
```bash
./scripts/hermes-yi setup
# Wizard hỏi: chọn model provider, paste API key, etc.
# Skip phần Telegram/Discord/Slack nếu không cần.
```

### Chat tương tác
```bash
./scripts/hermes-yi chat
# Mở TUI — gõ chat với Hermes như Claude Code
```

### Cấu hình
```bash
./scripts/hermes-yi config          # mở config UI
./scripts/hermes-yi model            # chọn provider/model mặc định
./scripts/hermes-yi auth             # quản lý API keys
./scripts/hermes-yi status           # check sức khoẻ
./scripts/hermes-yi doctor           # diagnostic
```

### Cron + automation
```bash
./scripts/hermes-yi cron list
./scripts/hermes-yi cron add ...
```

### Skills (self-improving loop)
```bash
./scripts/hermes-yi skills list
./scripts/hermes-yi skills new ...
```

### Update lên version mới
```bash
cd vendor/hermes-agent
git pull
./.venv/bin/pip install -e . --upgrade
```

## 🔌 Integration với YI-CHRONOS web app

**Phase 1 (đã có):** Web app dùng YI-Hermes (in-process, Vietnamese concierge) cho người dùng cuối qua floating chat. Tách biệt với Hermes Agent CLI.

**Phase 2 (sắp tới):** Hermes Agent CLI có thể:
1. Đọc kết quả engine YI-CHRONOS qua HTTP API (`localhost:8000/api/*`)
2. Tự tạo skills theo dõi changes trong glossary
3. Cron job 6h/lần — gọi observer agent → đề xuất cải tiến
4. Tăng cường YI-Hermes web (gửi suggestions vào suggestion queue)

## ⚠️ Lưu ý quan trọng

1. **Đừng chạy `hermes` (không có wrapper) trong thư mục dự án** — vì sẽ dùng PATH binary = Hermes Mac v0.12.0, không phải v0.13.0 của project.

2. **Đừng set `HERMES_HOME` global** trong shell rc (`.zshrc`) — sẽ làm Hermes Mac dùng path của YI. Chỉ wrapper script set tạm thời.

3. **Nếu muốn update Hermes Mac lên v0.13.0:** thực hiện riêng qua `~/.local/bin/hermes update`. Hai instance độc lập update.

## 🧪 Verify isolation

```bash
# Mac Hermes
~/.local/bin/hermes --version
# → Hermes Agent v0.12.0 ... Project: /Users/ozvietnamdesktop/.hermes/hermes-agent

# YI Hermes
./scripts/hermes-yi --version
# → Hermes Agent v0.13.0 ... Project: /Users/ozvietnamdesktop/Desktop/yi/vendor/hermes-agent
```

2 path khác hoàn toàn → 100% isolation.

## 🔑 API keys

Hermes Agent supports many providers — anh sẽ paste keys qua wizard hoặc `.env`:

- **z.ai** (đã có ZAI_API_KEY trong `.env.local` của YI-CHRONOS — wrapper sẽ tự source)
- **Anthropic Claude** (Sonnet 4.5, Opus 4.5)
- **OpenAI GPT**
- **DeepSeek R1**
- **Google Gemini**
- **OpenRouter** (200+ models)
- **Local Ollama**

Wrapper `scripts/hermes-yi` tự động source `.env.local` của YI-CHRONOS, nên ZAI_API_KEY sẵn sàng dùng được.

## Next steps

1. Anh chạy `./scripts/hermes-yi setup` — config provider + model
2. Test chat: `./scripts/hermes-yi chat`
3. Đợi Phase 2: tích hợp Hermes Agent với YI-Hermes web (skill đọc engine APIs)
