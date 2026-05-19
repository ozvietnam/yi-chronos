"""YI-Hermes Telegram bridge — long-polling bot for @Yihermesbot.

Architecture:
- Pure httpx long-polling against Telegram Bot API (no SDK dep).
- Each Telegram user_id → unique soul_key in YI-Hermes (so each chat user
  gets their own Soul + Memory).
- Messages → call HermesChat.send() → reply back via sendMessage.
- Slash commands handled inline:
    /start       — greeting + intro
    /help        — show available commands
    /modules     — list 7 schools
    /forget      — wipe my soul + memory
    /me          — show what Hermes remembers about me
    /clear       — clear current conversation history (in-memory)

Storage: per-user history kept in-process (not persistent across bridge restart).
This is intentional — Memory layer stores the persistent stuff.
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys
from dataclasses import dataclass

import httpx

from .chat import HermesChat, HermesContext, HermesTurn
from .memory import (
    fact_categories_summary,
    list_facts,
    list_summaries,
    top_viewed_terms,
)
from .soul import get_soul, reset_soul


LOGGER = logging.getLogger("yi_hermes.telegram")

TELEGRAM_API_BASE = "https://api.telegram.org"


@dataclass
class TelegramConfig:
    token: str
    allowed_users: set[int]      # empty set = open to all
    poll_timeout: int = 30
    request_timeout: int = 60
    max_message_chars: int = 4000   # Telegram limit is 4096


def _load_config_from_env() -> TelegramConfig | None:
    token = os.environ.get("YI_HERMES_TELEGRAM_TOKEN", "").strip()
    if not token:
        return None
    allowed_raw = os.environ.get("YI_HERMES_TELEGRAM_ALLOWED_USERS", "").strip()
    allowed_users: set[int] = set()
    if allowed_raw:
        for part in allowed_raw.split(","):
            part = part.strip()
            if part.isdigit():
                allowed_users.add(int(part))
    return TelegramConfig(token=token, allowed_users=allowed_users)


# ─── Per-user in-memory chat history ───────────────────────────────────────


_user_history: dict[int, list[HermesTurn]] = {}
_MAX_HISTORY = 10


def _trim_history(user_id: int) -> None:
    if user_id in _user_history and len(_user_history[user_id]) > _MAX_HISTORY:
        _user_history[user_id] = _user_history[user_id][-_MAX_HISTORY:]


# ─── Slash command handlers ────────────────────────────────────────────────


_HELP_TEXT = """🤖 *YI-Hermes Telegram* — trợ lý tử vi đa trường phái

*Lệnh có sẵn:*
/start — chào hỏi + giới thiệu
/help — hiển thị danh sách lệnh
/modules — 7 trường phái em quản lý
/me — em nhớ gì về anh (Soul + Memory)
/forget — xóa toàn bộ Soul + Memory của anh
/clear — xóa lịch sử chat hiện tại (in-memory)

*Cách dùng:*
- Hỏi trực tiếp: _"Dụng Thần là gì?"_ / _"Nhật chủ Kỷ thổ thì sao?"_
- Em sẽ tra từ điển + chart hoặc gọi LLM tuỳ câu hỏi.

Truy cập đầy đủ trên web: http://localhost:5173"""


def _handle_start(soul_key: str) -> str:
    soul = get_soul(soul_key)
    return (
        f"👋 *Chào anh!* Em là **YI-Hermes** — trợ lý tử vi đa trường phái.\n\n"
        f"Em đã có *{soul.session_count}* session trước với anh"
        + (f" (tone *{soul.tone}*)." if soul.session_count > 0 else ".")
        + "\n\nThử hỏi:\n"
        "• _Cách Cục là gì?_\n"
        "• _Tôi sinh 1985-08-15, Bát Tự thế nào?_\n"
        "• /modules để xem 7 trường phái\n"
        "• /me để xem em nhớ gì về anh"
    )


def _handle_modules() -> str:
    from .librarian import get_librarian
    sch = get_librarian().schools_summary()
    text = f"🏛️ *7 Trường Phái YI-CHRONOS*\n\n*Đông phương* ({len(sch['dong'])}):\n"
    text += "\n".join(f"• {n}" for n in sch["dong"])
    text += f"\n\n*Tây phương* ({len(sch['tay'])}):\n"
    text += "\n".join(f"• {n}" for n in sch["tay"])
    return text


def _handle_me(soul_key: str) -> str:
    soul = get_soul(soul_key)
    facts = list_facts(soul_key, limit=10)
    summaries = list_summaries(soul_key, limit=3)
    top_terms = top_viewed_terms(soul_key, limit=5)
    cats = fact_categories_summary(soul_key)

    text = "🧠 *Em nhớ về anh:*\n\n"
    text += f"*Soul* — tone _{soul.tone}_, verbosity _{soul.verbosity}_, "
    text += f"sessions: *{soul.session_count}*"
    if soul.focus_schools:
        text += f"\n  Focus: {', '.join(soul.focus_schools)}"
    if soul.notes:
        text += f"\n  Note: _{soul.notes}_"
    if soul.tabu_topics:
        text += f"\n  Tabu: {', '.join(soul.tabu_topics)}"

    text += f"\n\n*Facts* ({sum(cats.values())} cái"
    if cats:
        text += f", {dict(cats)}"
    text += "):\n"
    if facts:
        for f in facts[:5]:
            text += f"• [{f.category}] {f.fact}\n"
        if len(facts) > 5:
            text += f"  …và {len(facts) - 5} fact khác\n"
    else:
        text += "_(chưa có fact nào)_\n"

    text += f"\n*Summaries gần đây* ({len(summaries)}):\n"
    if summaries:
        for s in summaries:
            text += f"• {s.summary[:100]}\n"
    else:
        text += "_(chưa có)_\n"

    if top_terms:
        terms_str = ", ".join(f"{t}×{c}" for t, c in top_terms)
        text += f"\n*Terms hay xem:* {terms_str}"
    return text


def _handle_forget(soul_key: str) -> str:
    """Wipe soul. Memory facts/summaries kept for safety — user can manually
    delete via web. /forget for now is soul-only."""
    reset_soul(soul_key)
    return "🗑 Đã xóa Soul của anh. Memory (facts, summaries) vẫn còn — anh có thể xóa qua web nếu muốn."


def _handle_clear(user_id: int) -> str:
    _user_history.pop(user_id, None)
    return "🧹 Đã xóa lịch sử chat hiện tại (in-memory)."


# ─── Main message handler ──────────────────────────────────────────────────


async def _send_message(
    client: httpx.AsyncClient,
    token: str,
    chat_id: int,
    text: str,
    parse_mode: str = "Markdown",
) -> None:
    """Send a message — auto-chunked if too long."""
    chunks = [text]
    if len(text) > 4000:
        chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        try:
            await client.post(
                f"{TELEGRAM_API_BASE}/bot{token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": chunk,
                    "parse_mode": parse_mode,
                },
                timeout=15,
            )
        except httpx.HTTPError as e:
            LOGGER.warning(f"Failed to send to {chat_id}: {e}")
            # Retry without markdown (in case of formatting issues)
            try:
                await client.post(
                    f"{TELEGRAM_API_BASE}/bot{token}/sendMessage",
                    json={"chat_id": chat_id, "text": chunk},
                    timeout=15,
                )
            except httpx.HTTPError:
                pass


async def _process_message(
    client: httpx.AsyncClient,
    config: TelegramConfig,
    message: dict,
) -> None:
    """Process one Telegram message."""
    chat_id = message["chat"]["id"]
    user = message.get("from", {})
    tg_user_id = user.get("id")
    username = user.get("username", "")
    first_name = user.get("first_name", "")
    text = message.get("text", "").strip()

    if not tg_user_id or not text:
        return

    # Access control
    if config.allowed_users and tg_user_id not in config.allowed_users:
        await _send_message(
            client, config.token, chat_id,
            "🚫 Anh chưa được phép dùng bot này. Liên hệ admin.",
        )
        return

    soul_key = f"telegram:{tg_user_id}"
    LOGGER.info(f"Message from {username or first_name} ({tg_user_id}): {text[:80]}")

    # Slash commands (fast path, no LLM)
    reply: str
    if text.startswith("/start"):
        reply = _handle_start(soul_key)
    elif text.startswith("/help"):
        reply = _HELP_TEXT
    elif text.startswith("/modules"):
        reply = _handle_modules()
    elif text.startswith("/me"):
        reply = _handle_me(soul_key)
    elif text.startswith("/forget"):
        reply = _handle_forget(soul_key)
    elif text.startswith("/clear"):
        reply = _handle_clear(tg_user_id)
    else:
        # Regular chat → HermesChat
        chat = HermesChat()
        ctx = HermesContext(
            active_person_id=soul_key,
            active_person_name=first_name or username or f"User {tg_user_id}",
            active_tab="telegram",
        )
        history = _user_history.get(tg_user_id, [])
        try:
            result = chat.send(
                user_message=text,
                context=ctx,
                history=history,
            )
            reply = result["content"]
            # Append to history
            _user_history.setdefault(tg_user_id, []).extend([
                HermesTurn(role="user", content=text),
                HermesTurn(
                    role="hermes",
                    content=reply,
                    intent=result.get("intent", ""),
                    tokens_used=result.get("tokens_used", 0),
                ),
            ])
            _trim_history(tg_user_id)
        except Exception as e:
            LOGGER.exception(f"Chat error: {e}")
            reply = f"⚠️ Lỗi nội bộ: {str(e)[:200]}"

    await _send_message(client, config.token, chat_id, reply)


async def _poll_loop(config: TelegramConfig) -> None:
    """Long-polling loop. Runs until SIGTERM/SIGINT."""
    LOGGER.info("Starting Telegram polling for @Yihermesbot…")
    last_update_id = 0

    async with httpx.AsyncClient() as client:
        # Verify bot
        try:
            resp = await client.get(
                f"{TELEGRAM_API_BASE}/bot{config.token}/getMe",
                timeout=10,
            )
            bot_info = resp.json()
            if not bot_info.get("ok"):
                LOGGER.error(f"Bot auth failed: {bot_info}")
                return
            LOGGER.info(f"Bot OK: @{bot_info['result']['username']}")
        except httpx.HTTPError as e:
            LOGGER.error(f"Cannot reach Telegram API: {e}")
            return

        # Drop pending updates from before bridge start (avoid replay storms).
        try:
            r = await client.get(
                f"{TELEGRAM_API_BASE}/bot{config.token}/getUpdates",
                params={"offset": -1, "timeout": 0},
                timeout=10,
            )
            data = r.json()
            if data.get("ok") and data.get("result"):
                last_update_id = data["result"][-1]["update_id"]
                LOGGER.info(f"Skipping past updates, starting from {last_update_id + 1}")
        except httpx.HTTPError:
            pass

        # Main loop
        while True:
            try:
                resp = await client.get(
                    f"{TELEGRAM_API_BASE}/bot{config.token}/getUpdates",
                    params={
                        "offset": last_update_id + 1,
                        "timeout": config.poll_timeout,
                    },
                    timeout=config.poll_timeout + 5,
                )
                data = resp.json()
            except httpx.HTTPError as e:
                LOGGER.warning(f"Poll error: {e}")
                await asyncio.sleep(3)
                continue
            except Exception as e:
                LOGGER.exception(f"Unexpected poll error: {e}")
                await asyncio.sleep(5)
                continue

            if not data.get("ok"):
                LOGGER.warning(f"getUpdates not ok: {data}")
                await asyncio.sleep(5)
                continue

            updates = data.get("result", [])
            for update in updates:
                last_update_id = update["update_id"]
                msg = update.get("message") or update.get("edited_message")
                if msg:
                    try:
                        await _process_message(client, config, msg)
                    except Exception as e:
                        LOGGER.exception(f"Message processing error: {e}")


def run_bridge() -> int:
    """Sync entry point. Returns exit code."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    config = _load_config_from_env()
    if config is None:
        LOGGER.error("YI_HERMES_TELEGRAM_TOKEN env var not set. Add to .env.local.")
        return 1

    LOGGER.info(
        f"Bridge config: token=***{config.token[-6:]}, "
        f"allowed_users={config.allowed_users or 'OPEN'}"
    )

    # Handle Ctrl+C cleanly
    loop = asyncio.new_event_loop()

    def _shutdown(signum, frame):
        LOGGER.info(f"Shutdown signal {signum} received, stopping…")
        for task in asyncio.all_tasks(loop):
            task.cancel()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        loop.run_until_complete(_poll_loop(config))
    except (KeyboardInterrupt, asyncio.CancelledError):
        LOGGER.info("Stopped.")
    finally:
        loop.close()
    return 0


if __name__ == "__main__":
    sys.exit(run_bridge())
