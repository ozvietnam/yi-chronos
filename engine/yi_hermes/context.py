"""Context assembly for YI-Hermes — system-level project + founder knowledge.

Every chat session, Hermes loads:
1. **Project Manifest** — `data/yi_hermes/project_manifest.md` (canonical YI-CHRONOS info)
2. **Founder Profile** — `data/yi_hermes/founder_profile.md` (only if soul_key matches founder)
3. **Per-user Soul** — from soul.py
4. **Per-user Memory** — from memory.py

This makes Hermes "know" the project + know who the founder is, without anh
having to teach from scratch in every chat.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "yi_hermes"
_MANIFEST_PATH = _DATA_DIR / "project_manifest.md"
_FOUNDER_PATH = _DATA_DIR / "founder_profile.md"


# Founder soul_keys (multiple — anh có thể chat từ web hoặc Telegram, mỗi nơi 1 soul_key).
# Override via env: YI_HERMES_FOUNDER_SOUL_KEYS="telegram:6452658353,anh_thang,ceo"
_DEFAULT_FOUNDER_KEYS = (
    "telegram:6452658353",   # anh @minhthang0506 trên Telegram
    "_founder",              # generic
)


def get_founder_soul_keys() -> set[str]:
    """Return set of soul_keys that identify the founder.

    Allows multiple identifiers (anh trên web + Telegram + CLI all map to founder).
    """
    env = os.environ.get("YI_HERMES_FOUNDER_SOUL_KEYS", "").strip()
    if env:
        return {k.strip() for k in env.split(",") if k.strip()}
    return set(_DEFAULT_FOUNDER_KEYS)


def is_founder(soul_key: str) -> bool:
    """Check if this soul_key identifies the founder."""
    if not soul_key:
        return False
    return soul_key in get_founder_soul_keys()


# ─── File loaders (cached) ────────────────────────────────────────────────────


@lru_cache(maxsize=1)
def _load_manifest() -> str:
    """Load project manifest. Cached after first read."""
    if _MANIFEST_PATH.exists():
        return _MANIFEST_PATH.read_text(encoding="utf-8")
    return ""


@lru_cache(maxsize=1)
def _load_founder_profile() -> str:
    """Load founder profile. Cached after first read."""
    if _FOUNDER_PATH.exists():
        return _FOUNDER_PATH.read_text(encoding="utf-8")
    return ""


def reload_files() -> None:
    """Clear cache — call after manifest/founder file edits."""
    _load_manifest.cache_clear()
    _load_founder_profile.cache_clear()


def get_manifest() -> str:
    return _load_manifest()


def get_founder_profile() -> str:
    return _load_founder_profile()


def update_manifest(content: str) -> None:
    """Overwrite manifest from API."""
    _MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    _MANIFEST_PATH.write_text(content, encoding="utf-8")
    reload_files()


def update_founder_profile(content: str) -> None:
    """Overwrite founder profile from API."""
    _FOUNDER_PATH.parent.mkdir(parents=True, exist_ok=True)
    _FOUNDER_PATH.write_text(content, encoding="utf-8")
    reload_files()


# ─── Context assembly for system prompt ──────────────────────────────────────


def assemble_system_context(*, soul_key: str, query_hint: str = "") -> list[dict]:
    """Build the system-level context messages to prepend to every LLM call.

    Returns list of {role: 'system', content: str} dicts in priority order:
    1. Project manifest (always)
    2. Founder profile (only if is_founder)
    3. Soul addendum (per-user)
    4. Memory context (per-user)

    Caller still adds the agent persona (concierge.md) BEFORE this.
    """
    from .memory import build_memory_context
    from .soul import get_soul

    messages: list[dict] = []

    # 1. Project manifest — always
    manifest = get_manifest()
    if manifest:
        messages.append({
            "role": "system",
            "content": "## CONTEXT: PROJECT YI-CHRONOS\n\n" + manifest,
        })

    # 2. Founder profile — only if this user IS the founder
    if is_founder(soul_key):
        founder = get_founder_profile()
        if founder:
            messages.append({
                "role": "system",
                "content": "## CONTEXT: FOUNDER (đây là boss của em)\n\n" + founder,
            })

    # 3. Soul (per-user persona)
    soul = get_soul(soul_key)
    soul_block = soul.as_persona_addendum()
    if soul_block:
        messages.append({"role": "system", "content": soul_block})

    # 4. Memory (per-user facts + summaries)
    memory_block = build_memory_context(soul_key, query_hint=query_hint)
    if memory_block:
        messages.append({"role": "system", "content": memory_block})

    return messages


def context_summary(soul_key: str) -> dict:
    """Lightweight summary for UI panel: what's currently injected."""
    from .memory import fact_categories_summary, list_facts, list_summaries
    from .soul import get_soul

    soul = get_soul(soul_key)
    return {
        "soul_key": soul_key,
        "is_founder": is_founder(soul_key),
        "has_manifest": bool(get_manifest()),
        "has_founder_profile": bool(get_founder_profile()) if is_founder(soul_key) else None,
        "manifest_size_chars": len(get_manifest()),
        "founder_size_chars": len(get_founder_profile()) if is_founder(soul_key) else 0,
        "soul": {
            "tone": soul.tone,
            "verbosity": soul.verbosity,
            "session_count": soul.session_count,
            "focus_schools": soul.focus_schools,
            "tabu_topics": soul.tabu_topics,
        },
        "facts_count": len(list_facts(soul_key, limit=999)),
        "fact_categories": fact_categories_summary(soul_key),
        "summaries_count": len(list_summaries(soul_key, limit=999)),
    }
