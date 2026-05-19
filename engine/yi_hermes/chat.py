"""YI-Hermes Chat engine — multi-turn, context-aware concierge.

Flow:
- User sends message + context (current tab, active person, last chart data).
- Hermes detects intent: greeting / explain_term / explain_chart / question / route_to_council.
- For glossary lookups → answers directly from store (no LLM call needed).
- For chart questions → LLM call with persona + context.
- All sessions persisted in SQLite for memory.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path
from threading import Lock

from engine.ai.providers import LLMProvider, ProviderError
from engine.ai.registry import get_registry

from .glossary import get_glossary_store
from .librarian import get_librarian


_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "yi_hermes" / "chat.sqlite3"
_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
_lock = Lock()


@dataclass
class HermesContext:
    """Context provided by the frontend with each chat message."""

    active_tab: str = ""              # 'tu-vi' / 'bat-tu' / 'lien-hoa' / ...
    active_person_id: str = ""        # stable user_id for soul/memory keying
    active_person_name: str = ""
    active_person_birth: str = ""
    chart_data_excerpt: dict = field(default_factory=dict)  # compact chart subset
    user_gender: str = "nam"

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def soul_key(self) -> str:
        """Stable identifier for soul/memory lookups."""
        return self.active_person_id or self.active_person_name or "_anon"


@dataclass
class HermesTurn:
    role: str         # 'user' | 'hermes'
    content: str
    intent: str = ""  # tagged by Hermes
    tokens_used: int = 0


def _ensure_db() -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                active_person TEXT,
                turns_json TEXT,
                total_tokens INTEGER DEFAULT 0
            )"""
        )


# ─── Intent detection ────────────────────────────────────────────────────────


_GREETING_KEYWORDS = ("chào", "hi", "hello", "xin chào", "ê hermes", "alo")
_TERM_LOOKUP_KEYWORDS = (
    "là gì", "nghĩa là", "định nghĩa", "giải thích thuật ngữ",
    "khái niệm", "explain term",
)
_COUNCIL_KEYWORDS = (
    "tranh luận", "hội đồng", "council", "đa góc nhìn",
    "tổng hợp đông tây",
)
# Deep questions trigger council automatically (no opt-in needed) — these
# topics typically require multi-school cross-validation, not a single sage.
_DEEP_QUESTION_KEYWORDS = (
    "sự nghiệp", "công việc", "đổi việc", "thăng chức",
    "tài lộc", "tiền bạc", "đầu tư", "kinh doanh",
    "hôn nhân", "tình duyên", "kết hôn", "ly hôn",
    "đời em", "đời tôi", "vận mệnh", "lá số", "đại vận",
    "năm sau", "năm tới", "2026", "2027",
    "có nên", "có được",
)


def _detect_intent(text: str) -> str:
    t = text.lower().strip()
    if not t:
        return "empty"
    # Word-boundary check for greetings (avoid "hi" matching "thiên")
    words = t.replace("?", "").replace("!", "").replace(",", "").split()
    if words and any(w in _GREETING_KEYWORDS for w in words) and len(t) < 30:
        return "greeting"
    if t in _GREETING_KEYWORDS:   # exact match for "chào", "hello", etc.
        return "greeting"
    if any(k in t for k in _COUNCIL_KEYWORDS):
        return "route_to_council"
    # Deep questions auto-route to council (multi-school cross-validation)
    if any(k in t for k in _DEEP_QUESTION_KEYWORDS) and len(t) > 12:
        return "route_to_council"
    if any(k in t for k in _TERM_LOOKUP_KEYWORDS):
        return "explain_term"
    # Detect single-word query likely a term lookup
    if len(t.split()) <= 3 and not t.endswith("?"):
        return "explain_term"
    return "question"


def _try_glossary_lookup(text: str) -> str | None:
    """If the user mentions a glossary term, return formatted answer.

    Strategy:
    1. Clean text (strip punctuation + suffixes like "là gì", "nghĩa là").
    2. Try exact match on full cleaned text.
    3. Try exact match on shortened forms (drop suffix words).
    4. Try fuzzy search; accept top hit if reasonable confidence.
    """
    store = get_glossary_store()

    cleaned = text.replace("?", "").replace(",", "").replace(".", "").strip()

    # Try exact match first
    direct = store.get(cleaned)
    if direct:
        return _format_term(direct)

    # Strip common question suffixes — order matters: longest first.
    suffix_patterns = (
        " nghĩa là gì",
        " là cái gì",
        " giải nghĩa",
        " giải thích",
        " định nghĩa",
        " ý nghĩa",
        " nghĩa là",
        " là sao",
        " là gì",
    )
    candidate = cleaned.lower()
    for suffix in suffix_patterns:
        if candidate.endswith(suffix):
            stripped = cleaned[:-len(suffix)].strip()
            # Try exact match on stripped form (case-insensitive)
            for t in store.list_all():
                if t.term_vi.lower() == stripped.lower():
                    return _format_term(t)
            # Update candidate for fuzzy search
            cleaned = stripped
            break

    # Fuzzy search on cleaned text
    matches = store.search(cleaned, limit=5)
    if matches:
        top = matches[0]
        # Accept if top match is reasonably close in length
        if len(top.term_vi) <= len(cleaned) + 8:
            response = _format_term(top)
            if len(matches) > 1:
                response += "\n\n" + _format_related(matches[1:3])
            return response
    return None


def _format_term(term) -> str:
    out = f"**{term.term_vi}**"
    if term.term_zh:
        out += f" ({term.term_zh})"
    out += f" — *{term.module}*\n\n"
    out += f"{term.short_def}\n\n"
    out += f"{term.long_def}"
    if term.example:
        out += f"\n\n**Ví dụ:** {term.example}"
    if term.see_also:
        out += f"\n\n**Liên quan:** {', '.join(term.see_also)}"
    return out


def _format_related(terms: list) -> str:
    if not terms:
        return ""
    return "**Có thể anh cũng tìm:** " + ", ".join(t.term_vi for t in terms)


# ─── Greeting + Modules Q&A ──────────────────────────────────────────────────


def _greeting_response(context: HermesContext) -> str:
    librarian = get_librarian()
    sch = librarian.schools_summary()
    base = "Chào anh, em là **Hermes** — trợ lý YI-CHRONOS của anh.\n\n"
    if context.active_person_name:
        base += f"Em thấy anh đang dùng profile **{context.active_person_name}**. "
    if context.active_tab:
        tab_name = {
            "tu-vi": "Tử Vi Đẩu Số 🔮",
            "bat-tu": "Bát Tự + Hà Lạc 🪙",
            "lien-hoa": "Liên Hoa Độn Pháp ☘",
            "luc-hao": "Lục Hào Văn Vương ☷",
            "maihoa": "Mai Hoa Dịch Số 🌸",
            "western": "Chiêm Tinh Tây ♈",
        }.get(context.active_tab, context.active_tab)
        base += f"Anh đang xem **{tab_name}**. "

    base += "\n\nEm có thể giúp anh:\n"
    base += "- 🔎 **Giải thích một khái niệm** (vd: gõ 'Dụng Thần' hoặc 'Hổ quái')\n"
    base += "- 📖 **Đọc chart hiện tại** (anh đang xem) — em phân tích thay\n"
    base += "- ⚖️ **Hỏi Hội Đồng** với câu hỏi quan trọng (gọi 2-7 chuyên gia tranh luận)\n"
    base += "- 👤 **Tạo profile mới** (nếu chưa có sinh thần)\n\n"
    base += f"Hiện tại em đang nắm {sch['total']} trường phái: "
    base += f"Đông ({len(sch['dong'])}) + Tây ({len(sch['tay'])})."
    return base


def _modules_help() -> str:
    sch = get_librarian().schools_summary()
    out = "## 🏛️ 7 Trường Phái trong YI-CHRONOS\n\n"
    out += "### Đông phương\n"
    for name in sch["dong"]:
        out += f"- {name}\n"
    out += "\n### Tây phương\n"
    for name in sch["tay"]:
        out += f"- {name}\n"
    out += "\n*Anh muốn em giải thích kỹ trường phái nào?*"
    return out


# ─── Main chat function ──────────────────────────────────────────────────────


def _load_concierge_prompt() -> str:
    p = _PROMPTS_DIR / "concierge.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _provider_for_hermes() -> tuple[LLMProvider, str]:
    """Hermes provider preference:
    - Anthropic Sonnet 4.5 (best Vietnamese + reasoning) if key configured
    - DeepSeek V3 (cheap, capable) fallback
    - z.ai glm-4.5-flash (FREE tier, no balance needed) fallback
    - Mock (deterministic, always-on) last resort
    """
    reg = get_registry()
    for name in ("anthropic", "deepseek", "zai", "mock"):
        try:
            p = reg.get(name)
            if p.is_configured and not reg.is_unhealthy(name):
                model_map = {
                    "anthropic": "claude-sonnet-4-5-20250929",
                    "deepseek": "deepseek-chat",
                    "zai": "glm-4.5-flash",   # free tier — works even with empty balance
                    "mock": "mock-v1",
                }
                return p, model_map[name]
        except KeyError:
            continue
    return reg.get("mock"), "mock-v1"


class HermesChat:
    """Public chat interface — handles 1 turn at a time."""

    def __init__(self):
        _ensure_db()

    def send(
        self,
        *,
        user_message: str,
        context: HermesContext | None = None,
        history: list[HermesTurn] | None = None,
    ) -> dict:
        """Process one user message + return Hermes response + metadata."""
        ctx = context or HermesContext()
        history = history or []
        intent = _detect_intent(user_message)

        # FAST PATHS (no LLM call needed)
        if intent == "greeting":
            return {
                "intent": intent,
                "content": _greeting_response(ctx),
                "provider": "local",
                "model": "rule-based",
                "tokens_used": 0,
            }

        # Always try glossary lookup first for short messages — even "question" intent
        # might be a term lookup ("Cung Mệnh là cái gì?").
        if intent in ("explain_term", "question") and len(user_message) <= 60:
            glossary_answer = _try_glossary_lookup(user_message)
            if glossary_answer:
                # Log the view to memory for soul evolution.
                try:
                    from .memory import log_glossary_view
                    # Extract term name from the answer header.
                    import re
                    m = re.search(r"\*\*(.+?)\*\*", glossary_answer)
                    if m:
                        log_glossary_view(ctx.soul_key, m.group(1))
                except Exception:
                    pass
                return {
                    "intent": "glossary_hit",
                    "content": glossary_answer,
                    "provider": "local",
                    "model": "glossary-lookup",
                    "tokens_used": 0,
                }
            # Fall through to LLM if no match

        if intent == "route_to_council":
            return self._handle_council_route(user_message, ctx)

        # LLM PATH — for actual reasoning
        return self._llm_response(user_message, ctx, history)

    # ─── Council bridge ─────────────────────────────────────────────────────

    def _handle_council_route(
        self, user_message: str, ctx: HermesContext
    ) -> dict:
        """Spawn a kanban council consultation when the user asks a deep question.

        Strategy:
        - If we have birth data on the active person → auto-spawn with precast.
        - If not → reply asking for birth data + offer to use placeholder.
        """
        from engine.ai.kanban_council import (
            consult, save_session, select_sages,
        )
        from engine.ai.precast import precast_for_sages

        sages = select_sages(user_message)
        birth = self._extract_birth_from_context(ctx)

        precast: dict = {}
        if birth:
            precast = precast_for_sages(sages, birth=birth)

        session = consult(
            question=user_message,
            sages=sages,
            precast_data=precast,
            chart_context={
                "active_person": ctx.active_person_name,
                "active_tab": ctx.active_tab,
            },
            soul_key=ctx.soul_key,
        )
        save_session(session)

        # Build user-facing reply
        sage_list = ", ".join(sages)
        reply = (
            f"Câu hỏi của anh cần đa góc nhìn — em đã triệu tập **Hội Đồng** "
            f"gồm {len(sages)} sage: *{sage_list}*.\n\n"
            f"🎯 **Session ID**: `{session.root_id}`\n"
            f"⏱️ Mỗi sage chạy ~30-60s, arbiter tổng hợp ~30s sau khi N sage xong.\n\n"
        )
        if not birth:
            reply += (
                "⚠️ Em chưa có dữ liệu sinh của anh trong context — sage sẽ "
                "đánh dấu `engine_gap` thay vì cast Bát Tự thật. Anh bổ sung "
                "ngày-giờ sinh ở profile để lần sau em precast đầy đủ.\n\n"
            )
        else:
            reply += (
                f"✅ Engine đã pre-cast cho: {', '.join(precast.keys())}.\n\n"
            )
        reply += (
            f"Theo dõi real-time tại: `GET /api/ai/council/kanban/sessions/"
            f"{session.root_id}`"
        )

        return {
            "intent": "route_to_council",
            "content": reply,
            "provider": "local",
            "model": "rule-based",
            "tokens_used": 0,
            "council_root_id": session.root_id,
            "council_sages": list(session.sage_task_ids.keys()),
            "council_precast_sages": list(precast.keys()),
        }

    @staticmethod
    def _extract_birth_from_context(ctx: HermesContext) -> dict | None:
        """Try to assemble a birth payload from chat context.

        chart_data_excerpt may have raw birth_datetime_local. active_person_birth
        is a free-form string ("1985-08-15 10:30") — parse if shaped right.
        """
        excerpt = ctx.chart_data_excerpt or {}
        if "birth_datetime_local" in excerpt:
            return {
                "birth_datetime_local": excerpt["birth_datetime_local"],
                "timezone": excerpt.get("timezone", "Asia/Ho_Chi_Minh"),
                "gender": excerpt.get("gender", ctx.user_gender),
            }
        if ctx.active_person_birth:
            return {
                "birth_datetime_local": ctx.active_person_birth.strip(),
                "timezone": "Asia/Ho_Chi_Minh",
                "gender": ctx.user_gender,
            }
        return None

    def poll_council(self, root_id: str) -> dict:
        """Convenience: full snapshot for a council session.

        Frontend / Telegram bot can call this every 5-10s to update UI.
        """
        from engine.ai.kanban_council import load_session, session_snapshot

        session = load_session(root_id)
        if session is None:
            return {"status": "not_found", "root_id": root_id}
        return {"status": "ok", "snapshot": session_snapshot(session)}

    def _llm_response(
        self,
        user_message: str,
        ctx: HermesContext,
        history: list[HermesTurn],
    ) -> dict:
        provider, model = _provider_for_hermes()
        persona = _load_concierge_prompt()

        # Build messages
        messages = [{"role": "system", "content": persona}]

        # Inject system-level context (project manifest + founder profile if applicable
        # + Soul + Memory) — handled by context.assemble_system_context.
        from .context import assemble_system_context
        for sys_msg in assemble_system_context(
            soul_key=ctx.soul_key, query_hint=user_message,
        ):
            messages.append(sys_msg)

        # Inject context info as a system note (compact)
        ctx_note_parts = []
        if ctx.active_person_name:
            ctx_note_parts.append(f"User profile: {ctx.active_person_name}")
            if ctx.active_person_birth:
                ctx_note_parts.append(f"sinh {ctx.active_person_birth}")
        if ctx.active_tab:
            ctx_note_parts.append(f"đang ở tab: {ctx.active_tab}")
        if ctx.chart_data_excerpt:
            excerpt = json.dumps(ctx.chart_data_excerpt, ensure_ascii=False)[:1500]
            ctx_note_parts.append(f"chart excerpt: {excerpt}")

        if ctx_note_parts:
            messages.append({
                "role": "system",
                "content": "## Bối cảnh hiện tại\n" + "\n".join(ctx_note_parts),
            })

        # Add recent history (last 6 turns max)
        for t in history[-6:]:
            messages.append({
                "role": "user" if t.role == "user" else "assistant",
                "content": t.content,
            })

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        try:
            resp = provider.chat(
                messages=messages,
                model=model,
                temperature=0.7,
                max_tokens=800,
            )
            return {
                "intent": "question",
                "content": resp.content,
                "provider": resp.provider,
                "model": resp.model,
                "tokens_used": resp.total_tokens,
            }
        except ProviderError as e:
            # Fallback to mock
            get_registry().mark_unhealthy(provider.name, str(e))
            mock = get_registry().get("mock")
            mock_resp = mock.chat(
                messages=messages, model="mock-v1",
                temperature=0.7, max_tokens=600,
            )
            return {
                "intent": "question_fallback",
                "content": (
                    f"*(Hermes đang dùng Mock vì {provider.name} lỗi: {str(e)[:80]}. "
                    "Paste API key thật vào để có trả lời thực.)*\n\n" + mock_resp.content
                ),
                "provider": "mock",
                "model": "mock-v1",
                "tokens_used": 0,
            }

    def list_recent_sessions(self, limit: int = 10) -> list[dict]:
        _ensure_db()
        with sqlite3.connect(_DB_PATH) as conn:
            rows = conn.execute(
                "SELECT id, created_at, active_person, turns_json, total_tokens "
                "FROM sessions ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "id": r[0],
                "created_at": r[1],
                "active_person": r[2],
                "turn_count": len(json.loads(r[3])) if r[3] else 0,
                "total_tokens": r[4],
            }
            for r in rows
        ]

    def save_session(self, turns: list[HermesTurn], active_person: str = "") -> int:
        _ensure_db()
        with _lock, sqlite3.connect(_DB_PATH) as conn:
            cur = conn.execute(
                "INSERT INTO sessions (active_person, turns_json, total_tokens) VALUES (?, ?, ?)",
                (
                    active_person,
                    json.dumps([asdict(t) for t in turns], ensure_ascii=False),
                    sum(t.tokens_used for t in turns),
                ),
            )
            return cur.lastrowid
