"""Phòng Quản Trị Hermes (task 1) — tổng hợp roster + metrics + audit helper.

Owner-only governance console backend. Tái dùng: prompt_store (SOUL/persona),
kanban_council.SAGES_BY_TAG (roster), llm_spend (chi phí), evolve_gate (cổng duyệt),
system_meta (knowledge_version + enable flag), audit_log (nhật ký). Dual-driver,
resilient (lỗi 1 nguồn → vẫn trả phần còn lại).
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from sqlalchemy import text

from engine.db import session_scope

_PROFILES_DIR = Path(__file__).resolve().parent.parent / "data" / "hermes_yi" / "profiles"
_AUDIT_PREFIX = "admin_hermes:"


# ─── enable/disable sage (system_meta flag) ─────────────────────────────────

def is_sage_enabled(tag: str) -> bool:
    from engine.system_meta import get_meta
    return get_meta(f"sage_enabled:{tag}", "1") != "0"


def set_sage_enabled(tag: str, enabled: bool) -> None:
    from engine.system_meta import set_meta
    set_meta(f"sage_enabled:{tag}", "1" if enabled else "0")


def _profile_soul_size(profile: str) -> int:
    try:
        p = _PROFILES_DIR / profile / "SOUL.md"
        return p.stat().st_size if p.exists() else 0
    except Exception:
        return 0


# ─── roster (10 vai: 8 sage + arbiter + orchestrator) ───────────────────────

def get_roster() -> list[dict]:
    """Danh sách vai Hermes: tag, tên, icon, chuyên môn, enabled, SOUL override/size,
    knowledge_version. Resilient từng vai."""
    from engine.ai import prompt_store as ps
    from engine.ai.kanban_council import SAGES_BY_TAG, ARBITER_PROFILE
    from engine.system_meta import get_knowledge_version

    kv = get_knowledge_version()
    roster: list[dict] = []
    for tag in ps.list_all_prompt_ids():        # 8 sage + orchestrator
        meta = ps.AGENT_METADATA.get(tag, {}) if hasattr(ps, "AGENT_METADATA") else {}
        try:
            soul = ps.get_prompt(tag) or ""
        except Exception:
            soul = ""
        try:
            overridden = ps.is_overridden(tag)
        except Exception:
            overridden = False
        roster.append({
            "tag": tag,
            "name_vi": meta.get("name_vi", tag),
            "icon": meta.get("icon", "🔮"),
            "specialty": meta.get("specialty", ""),
            "profile": SAGES_BY_TAG.get(tag, tag),
            "enabled": is_sage_enabled(tag),
            "soul_overridden": overridden,
            "soul_size": len(soul),
            "knowledge_version": kv,
        })
    # arbiter — profile riêng (không qua prompt_store)
    roster.append({
        "tag": "arbiter", "name_vi": "Trọng tài (tổng hợp)", "icon": "⚖️",
        "specialty": "Tổng hợp đồng thuận/mâu thuẫn đa phái", "profile": ARBITER_PROFILE,
        "enabled": is_sage_enabled("arbiter"), "soul_overridden": False,
        "soul_size": _profile_soul_size(ARBITER_PROFILE), "knowledge_version": kv,
    })
    return roster


# ─── metrics (chi phí + paradigm flags + lượt theo feature + evolve pending) ─

def get_metrics() -> dict:
    """Giám sát: chi phí/ngày (theo provider), #cờ paradigm, lượt theo feature,
    số đề xuất evolve đang chờ. Resilient từng nguồn."""
    out: dict = {}
    try:
        from engine import llm_spend
        out["spend"] = llm_spend.spend_summary()
    except Exception as e:
        out["spend"] = {"error": str(e)[:100]}

    # lượt theo feature + #cờ paradigm (đếm user_castings)
    try:
        with session_scope(service=True) as conn:
            rows = conn.execute(text(
                "SELECT method, COUNT(*) FROM user_castings GROUP BY method"
            )).fetchall()
            flags = conn.execute(text(
                "SELECT COUNT(*) FROM user_castings WHERE verdict='paradigm_flag'"
            )).scalar()
        out["by_method"] = {r[0]: r[1] for r in rows}
        out["paradigm_flags"] = int(flags or 0)
    except Exception as e:
        out["by_method"] = {}
        out["paradigm_flags"] = 0
        out["_castings_error"] = str(e)[:100]

    try:
        from engine import evolve_gate
        out["evolve_pending"] = len(evolve_gate.list_pending(limit=200))
    except Exception:
        out["evolve_pending"] = 0
    return out


# ─── audit (mọi hành động admin) ────────────────────────────────────────────

def audit(action: str, *, actor_user_id: Optional[int] = None,
          details: Optional[dict] = None) -> None:
    """Ghi 1 dòng audit_log cho thao tác admin (dual-driver). Tiền tố action để lọc.
    Best-effort — KHÔNG để lỗi audit phá hành động chính."""
    try:
        now = int(time.time())
        with session_scope(service=True) as conn:
            conn.execute(
                text("""INSERT INTO audit_log (user_id, actor_user_id, action, details_json,
                            created_at)
                        VALUES (:u,:a,:act,:d,:t)"""),
                {"u": actor_user_id, "a": actor_user_id, "act": _AUDIT_PREFIX + action,
                 "d": json.dumps(details or {}, ensure_ascii=False), "t": now},
            )
    except Exception:
        pass


def commander_answer(question: str) -> dict:
    """Chỉ huy (orchestrator chế độ operator) — task 4. Trả lời câu hỏi quản trị bằng
    CÔNG CỤ ĐỌC (roster/metrics/evolve). CHỈ báo cáo + đề xuất; KHÔNG tự thực thi —
    hành động đụng não-chung (toggle/SOUL/duyệt) qua endpoint riêng + owner xác nhận tay.
    Deterministic (không LLM → rẻ, không predict — tuân Iron #4/#6/#8)."""
    q = (question or "").lower()
    parts: list[str] = []
    data: dict = {}
    if any(k in q for k in ("duyệt", "evolve", "chờ", "pending", "đề xuất")):
        from engine import evolve_gate
        pending = evolve_gate.list_pending(limit=20)
        data["pending"] = pending
        parts.append(f"Có {len(pending)} đề xuất đang chờ Anh duyệt."
                     + (" (xem /evolve/pending)" if pending else ""))
    if any(k in q for k in ("chi phí", "tiền", "ngân sách", "spend", "cost", "metric",
                            "giám sát", "thế nào", "tình hình", "sao rồi")):
        m = get_metrics()
        data["metrics"] = m
        sp = m.get("spend", {})
        parts.append(f"Chi phí hôm nay {sp.get('total_usd', '?')}$/{sp.get('budget_usd', '?')}$; "
                     f"{m.get('paradigm_flags', 0)} cờ paradigm; {m.get('evolve_pending', 0)} chờ duyệt.")
    if any(k in q for k in ("roster", "sage", "vai", "ai đang", "bật", "tắt")):
        roster = get_roster()
        data["roster"] = roster
        enabled = sum(1 for r in roster if r.get("enabled"))
        parts.append(f"{len(roster)} vai ({enabled} đang bật). Bật/tắt qua /sage/{{tag}}/toggle.")
    if not parts:
        m = get_metrics()
        data["metrics"] = m
        parts.append(f"Tổng quan: {m.get('evolve_pending', 0)} chờ duyệt · "
                     f"{m.get('paradigm_flags', 0)} cờ paradigm · chi phí "
                     f"{m.get('spend', {}).get('total_usd', '?')}$.")
    return {"answer": " ".join(parts), "data": data,
            "note": "Chỉ huy CHỈ đọc + đề xuất. Hành động đụng não-chung cần Anh xác nhận tay."}


def list_audit(limit: int = 50) -> list[dict]:
    """Nhật ký thao tác admin Hermes (mới nhất trước)."""
    try:
        with session_scope(service=True) as conn:
            rows = conn.execute(
                text("""SELECT id, actor_user_id, action, details_json, created_at
                        FROM audit_log WHERE action LIKE :p
                        ORDER BY id DESC LIMIT :l"""),
                {"p": _AUDIT_PREFIX + "%", "l": limit},
            ).fetchall()
    except Exception:
        return []
    out = []
    for r in rows:
        try:
            details = json.loads(r[3]) if r[3] else {}
        except Exception:
            details = {}
        out.append({"id": r[0], "actor_user_id": r[1],
                    "action": (r[2] or "").replace(_AUDIT_PREFIX, ""),
                    "details": details, "created_at": r[4]})
    return out
