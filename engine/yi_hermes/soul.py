"""YI-Hermes Soul — persistent persona profile per user.

"Soul" = how Hermes tailors itself to each user over time:
- Tone (formal vs casual vs warm)
- Verbosity (terse / balanced / verbose)
- Focus schools (which trường phái user cares about most)
- Greeting style
- Tabu topics (user said "đừng nói về X")
- Learned mannerisms (auto-evolved from interactions)

Storage: SQLite per-user. Loads default if user not seen before. Auto-evolves
after N interactions via `evolve_soul(user_id, session_summary)`.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path
from threading import Lock


_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "yi_hermes" / "soul.sqlite3"
_lock = Lock()


# Default soul — applied to all new users.
DEFAULT_SOUL = {
    "tone": "warm",                    # warm / formal / casual / scholarly
    "verbosity": "balanced",           # terse / balanced / verbose
    "focus_schools": [],               # learned over time, e.g. ["bat_tu", "tu_vi"]
    "greeting_style": "context_aware", # context_aware / brief / quote
    "tabu_topics": [],                 # user said "đừng nói về X"
    "preferred_language": "vi",        # vi / en (fallback)
    "addressing": {                    # how Hermes refers to user
        "pronoun": "anh",              # anh / chị / bạn / em
        "self": "em",                  # em / mình / tôi
    },
    "learned_traits": [],              # auto-discovered, e.g. "skeptical of mock answers"
    "session_count": 0,
}


@dataclass
class SoulProfile:
    user_id: str
    tone: str = "warm"
    verbosity: str = "balanced"
    focus_schools: list[str] = field(default_factory=list)
    greeting_style: str = "context_aware"
    tabu_topics: list[str] = field(default_factory=list)
    preferred_language: str = "vi"
    addressing: dict = field(default_factory=lambda: {"pronoun": "anh", "self": "em"})
    learned_traits: list[str] = field(default_factory=list)
    session_count: int = 0
    notes: str = ""             # free-form user notes about themselves
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def as_persona_addendum(self) -> str:
        """Render soul as a system-prompt addendum for the chat LLM."""
        parts = []
        addr = self.addressing
        parts.append(
            f"## Hồ sơ user (Soul)\n"
            f"- Xưng hô: gọi user là **'{addr.get('pronoun', 'anh')}'**, "
            f"em xưng **'{addr.get('self', 'em')}'**.\n"
            f"- Tone: **{self.tone}** ({'ấm áp thân thiện' if self.tone == 'warm' else self.tone})\n"
            f"- Verbosity: **{self.verbosity}** "
            f"({'ngắn gọn' if self.verbosity == 'terse' else 'cân bằng' if self.verbosity == 'balanced' else 'chi tiết'})"
        )
        if self.focus_schools:
            parts.append(f"- User quan tâm chính: {', '.join(self.focus_schools)}")
        if self.tabu_topics:
            parts.append(f"- TRÁNH nói về: {', '.join(self.tabu_topics)}")
        if self.learned_traits:
            parts.append("- Đặc tính user (học từ tương tác trước):")
            for t in self.learned_traits[:5]:
                parts.append(f"  - {t}")
        if self.notes:
            parts.append(f"- Ghi chú: {self.notes}")
        parts.append(f"- Số session đã có với user này: {self.session_count}")
        return "\n".join(parts)


def _ensure_db() -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS soul_profiles (
                user_id TEXT PRIMARY KEY,
                profile_json TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )


def get_soul(user_id: str) -> SoulProfile:
    """Load soul for user — create default if not seen before."""
    if not user_id:
        user_id = "_anon"
    _ensure_db()
    with sqlite3.connect(_DB_PATH) as conn:
        row = conn.execute(
            "SELECT profile_json, updated_at FROM soul_profiles WHERE user_id=?",
            (user_id,),
        ).fetchone()
    if row:
        data = json.loads(row[0])
        data["user_id"] = user_id
        data["updated_at"] = row[1]
        return SoulProfile(**data)
    # New user — return default soul
    default = dict(DEFAULT_SOUL)
    default["user_id"] = user_id
    return SoulProfile(**default)


def save_soul(soul: SoulProfile) -> None:
    """Persist soul profile."""
    _ensure_db()
    data = soul.to_dict()
    data.pop("user_id", None)   # stored separately
    data.pop("updated_at", None)
    with _lock, sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            """INSERT INTO soul_profiles (user_id, profile_json)
               VALUES (?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                 profile_json=excluded.profile_json,
                 updated_at=CURRENT_TIMESTAMP""",
            (soul.user_id, json.dumps(data, ensure_ascii=False)),
        )


def update_soul(user_id: str, patch: dict) -> SoulProfile:
    """Apply partial update — merge with existing soul."""
    soul = get_soul(user_id)
    for k, v in patch.items():
        if hasattr(soul, k):
            setattr(soul, k, v)
    save_soul(soul)
    return soul


def reset_soul(user_id: str) -> SoulProfile:
    """Wipe user's soul → restart with default."""
    _ensure_db()
    with _lock, sqlite3.connect(_DB_PATH) as conn:
        conn.execute("DELETE FROM soul_profiles WHERE user_id=?", (user_id,))
    return get_soul(user_id)


def evolve_soul(user_id: str, session_signals: dict) -> SoulProfile:
    """Auto-evolve soul based on session signals.

    Signals can include:
    - schools_visited: list of school IDs accessed
    - new_traits: list of learned traits from session
    - explicit_tabu: topics user said to avoid
    - tone_signal: "user prefers shorter answers" → adjust verbosity
    """
    soul = get_soul(user_id)
    soul.session_count += 1

    # Update focus schools (most-visited)
    if "schools_visited" in session_signals:
        for sch in session_signals["schools_visited"]:
            if sch and sch not in soul.focus_schools:
                soul.focus_schools.append(sch)
        # Keep most recent 5
        soul.focus_schools = soul.focus_schools[-5:]

    if "new_traits" in session_signals:
        for t in session_signals["new_traits"]:
            if t and t not in soul.learned_traits:
                soul.learned_traits.append(t)
        soul.learned_traits = soul.learned_traits[-10:]

    if "explicit_tabu" in session_signals:
        for tabu in session_signals["explicit_tabu"]:
            if tabu and tabu not in soul.tabu_topics:
                soul.tabu_topics.append(tabu)
        # Cap like focus_schools/learned_traits — SOUL injects into every prompt, so an
        # uncapped tabu list bloats the system prompt over many sessions (#20).
        soul.tabu_topics = soul.tabu_topics[-15:]

    if "tone_signal" in session_signals:
        signal = session_signals["tone_signal"]
        if signal == "shorter":
            soul.verbosity = "terse"
        elif signal == "longer":
            soul.verbosity = "verbose"

    save_soul(soul)
    return soul
