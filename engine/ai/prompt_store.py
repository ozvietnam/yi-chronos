"""Prompt storage — defaults from filesystem + user overrides in SQLite.

API:
- get_prompt(agent_id) → str — returns override if exists, else default
- set_prompt(agent_id, content) → save user override
- reset_prompt(agent_id) → delete user override, fall back to default
- get_default(agent_id) → str — always return the canonical default
- list_agent_ids() → list[str]
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Lock


_PROMPT_DIR = Path(__file__).resolve().parent / "prompts"
_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "ai_prompts.sqlite3"

AGENT_IDS: tuple[str, ...] = (
    "mai_hoa",
    "luc_hao",
    "lien_hoa",
    "tu_vi",
    "bat_tu",
    "ha_lac",
    "western",
    "than_so",
    "chieu_dom",   # Tử Vi Bắc phái / 18 Phi Tinh — đọc nội tâm sâu (sage độc lập, Anh chốt 19/6)
)
ORCHESTRATOR_ID = "orchestrator"
ALL_PROMPT_IDS: tuple[str, ...] = AGENT_IDS + (ORCHESTRATOR_ID,)


_lock = Lock()


def _ensure_db() -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS prompt_overrides (
                agent_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )


def get_default(agent_id: str) -> str:
    """Return the canonical default prompt from filesystem."""
    if agent_id not in ALL_PROMPT_IDS:
        raise ValueError(f"Unknown agent_id: {agent_id!r}")
    path = _PROMPT_DIR / f"{agent_id}.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def get_prompt(agent_id: str) -> str:
    """Return user override if exists, else default."""
    if agent_id not in ALL_PROMPT_IDS:
        raise ValueError(f"Unknown agent_id: {agent_id!r}")
    _ensure_db()
    with sqlite3.connect(_DB_PATH) as conn:
        row = conn.execute(
            "SELECT content FROM prompt_overrides WHERE agent_id=?",
            (agent_id,),
        ).fetchone()
    if row:
        return row[0]
    return get_default(agent_id)


def set_prompt(agent_id: str, content: str) -> None:
    """Save user override."""
    if agent_id not in ALL_PROMPT_IDS:
        raise ValueError(f"Unknown agent_id: {agent_id!r}")
    _ensure_db()
    with _lock, sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            """INSERT INTO prompt_overrides (agent_id, content)
               VALUES (?, ?)
               ON CONFLICT(agent_id) DO UPDATE SET
                 content=excluded.content,
                 updated_at=CURRENT_TIMESTAMP""",
            (agent_id, content),
        )


def reset_prompt(agent_id: str) -> None:
    """Delete user override → fall back to default."""
    if agent_id not in ALL_PROMPT_IDS:
        raise ValueError(f"Unknown agent_id: {agent_id!r}")
    _ensure_db()
    with _lock, sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            "DELETE FROM prompt_overrides WHERE agent_id=?", (agent_id,)
        )


def list_agent_ids() -> list[str]:
    return list(AGENT_IDS)


def list_all_prompt_ids() -> list[str]:
    return list(ALL_PROMPT_IDS)


def is_overridden(agent_id: str) -> bool:
    """Check if there's a user override."""
    if agent_id not in ALL_PROMPT_IDS:
        return False
    _ensure_db()
    with sqlite3.connect(_DB_PATH) as conn:
        row = conn.execute(
            "SELECT 1 FROM prompt_overrides WHERE agent_id=?",
            (agent_id,),
        ).fetchone()
    return row is not None


# Agent metadata for UI listing
AGENT_METADATA: dict[str, dict] = {
    "mai_hoa": {
        "name_vi": "Mai Hoa Dịch Số",
        "icon": "🌸",
        "specialty": "Dịch Lý quan sát NNTT — Tượng / Số / Lý / Chiêm",
        "best_for": "Quan sát hiện tượng tự nhiên, gieo quẻ thời điểm",
    },
    "luc_hao": {
        "name_vi": "Lục Hào Văn Vương",
        "icon": "☷",
        "specialty": "Gieo 3 xu — Dụng Thần dứt khoát theo ngày",
        "best_for": "Câu hỏi rõ ràng có/không, timing ngắn hạn",
    },
    "lien_hoa": {
        "name_vi": "Liên Hoa Độn Pháp",
        "icon": "☘",
        "specialty": "2 số tâm ý → 5/9/13 Không Thời Sự + luận sự deeper",
        "best_for": "Câu chuyện theo chuỗi phase, đa lĩnh vực",
    },
    "tu_vi": {
        "name_vi": "Tử Vi Đẩu Số (Bắc Phái)",
        "icon": "🔮",
        "specialty": "12 cung an sao + Tứ Hóa + Đại Vận + Lưu Trú",
        "best_for": "Vận lớn đời người, từng giai đoạn 10 năm",
    },
    "bat_tu": {
        "name_vi": "Bát Tự Tử Bình",
        "icon": "🪙",
        "specialty": "Tứ Trụ + Thập Thần + Dụng Thần + Cách Cục",
        "best_for": "Gốc rễ ngũ hành, cân bằng năng lượng cá nhân",
    },
    "ha_lac": {
        "name_vi": "Hà Lạc Lý Số",
        "icon": "⭐",
        "specialty": "Tiên thiên + Hậu thiên + 12 hào ~84 năm",
        "best_for": "Bản chất bẩm sinh vs cách vận hành",
    },
    "western": {
        "name_vi": "Chiêm Tinh Phương Tây",
        "icon": "♈",
        "specialty": "Natal chart + Transits + Progressions + Psychology",
        "best_for": "Tâm lý nội tâm, khung tâm lý học Jung",
    },
    "than_so": {
        "name_vi": "Thần Số Học",
        "icon": "🔢",
        "specialty": "Pythagoras + Chaldean — số đường đời / linh hồn / biểu đạt",
        "best_for": "Soi tính qua con số ngày sinh + tên, đối chiếu chéo",
    },
    "chieu_dom": {
        "name_vi": "Chiếu Đởm Kinh (Bắc phái)",
        "icon": "🪞",
        "specialty": "Tử Vi Bắc phái — 18 Phi Tinh, soi chỗ sâu nhất của nội tâm",
        "best_for": "Đọc tâm hồn/chiều sâu tâm lý, cốt cách bên trong (không tiên tri sự kiện)",
    },
}
