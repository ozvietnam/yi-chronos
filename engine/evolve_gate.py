"""H6.2 (Vòng 2) — Cổng duyệt tự tiến hoá theo ĐỘ TỰ TIN (Anh chốt 2026-06-17).

Mọi đề xuất cập nhật "não chung" (skill/tri thức/trường phái mới) đi qua đây:
  - em (AI) chấm confidence + impact TRƯỚC.
  - tự-tin CAO + tác-động NHỎ  → auto_approved (em duyệt, anh được báo, rollback được).
  - tự-tin CAO + tác-động LỚN  → pending (trường phái mới/đụng paradigm → ANH duyệt).
  - tự-tin THẤP                → pending (anh quyết).
Data RIÊNG user KHÔNG đi qua đây (chỉ tri thức chung). Dual-driver (engine.db).
"""
from __future__ import annotations

import json
import time
from typing import Optional

from sqlalchemy import text

from engine.db import is_postgres, session_scope

CONF_AUTO = 0.85               # ngưỡng tự-tin để auto-merge (chỉ khi impact thấp)

_DDL = """
CREATE TABLE IF NOT EXISTS evolve_proposals (
    id          BIGSERIAL PRIMARY KEY,
    kind        TEXT NOT NULL,
    title       TEXT,
    payload     {json_type},
    confidence  REAL NOT NULL DEFAULT 0,
    impact      TEXT NOT NULL DEFAULT 'low',
    status      TEXT NOT NULL DEFAULT 'pending',
    source      TEXT,
    created_at  BIGINT NOT NULL,
    reviewed_at BIGINT,
    reviewer    TEXT,
    note        TEXT
)
"""
_DDL_SQLITE = _DDL.replace("BIGSERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT").format(json_type="TEXT")
_DDL_PG = _DDL.format(json_type="JSONB")


def _ensure(conn) -> None:
    conn.execute(text(_DDL_PG if is_postgres() else _DDL_SQLITE))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_evolve_status ON evolve_proposals(status)"))


def decide(confidence: float, impact: str) -> str:
    """Quyết theo bảng đã chốt. impact 'high' (trường phái mới/paradigm) → luôn cần anh."""
    if impact == "high":
        return "pending"
    return "auto_approved" if confidence >= CONF_AUTO else "pending"


def submit_proposal(*, kind: str, payload: dict, confidence: float, impact: str = "low",
                    title: str = "", source: str = "") -> dict:
    """em đề xuất 1 cập nhật não-chung (đã tự chấm confidence/impact). Trả {id, status}."""
    status = decide(float(confidence), impact)
    res_expr = "CAST(:p AS JSONB)" if is_postgres() else ":p"
    now = int(time.time())
    with session_scope(service=True) as conn:
        _ensure(conn)
        rid = conn.execute(
            text(f"""INSERT INTO evolve_proposals
                    (kind, title, payload, confidence, impact, status, source, created_at,
                     reviewed_at, reviewer)
                    VALUES (:k,:t,{res_expr},:c,:imp,:st,:src,:now,
                            :rat,:rev) RETURNING id"""),
            {"k": kind, "t": title, "p": json.dumps(payload, ensure_ascii=False),
             "c": float(confidence), "imp": impact, "st": status, "src": source, "now": now,
             "rat": now if status == "auto_approved" else None,
             "rev": "ai-auto" if status == "auto_approved" else None},
        ).scalar()
    return {"id": rid, "status": status}


def list_pending(limit: int = 50) -> list[dict]:
    """Hàng đợi anh duyệt (đã được em lọc + chấm) — pending, mới nhất trước."""
    with session_scope(service=True) as conn:
        _ensure(conn)
        rows = conn.execute(
            text("""SELECT id, kind, title, confidence, impact, source, created_at
                    FROM evolve_proposals WHERE status='pending'
                    ORDER BY id DESC LIMIT :l"""), {"l": limit},
        ).fetchall()
    return [{"id": r[0], "kind": r[1], "title": r[2], "confidence": r[3],
             "impact": r[4], "source": r[5], "created_at": r[6]} for r in rows]


def review(proposal_id: int, *, approve: bool, reviewer: str, note: str = "") -> dict:
    """Anh duyệt 1 đề xuất pending → approved | rejected."""
    new_status = "approved" if approve else "rejected"
    with session_scope(service=True) as conn:
        _ensure(conn)
        n = conn.execute(
            text("""UPDATE evolve_proposals
                    SET status=:s, reviewed_at=:t, reviewer=:r, note=:n
                    WHERE id=:id AND status='pending'"""),
            {"s": new_status, "t": int(time.time()), "r": reviewer, "n": note, "id": proposal_id},
        ).rowcount
    return {"id": proposal_id, "status": new_status if n else "not_pending", "updated": bool(n)}


def get_proposal(proposal_id: int) -> Optional[dict]:
    import json as _j
    with session_scope(service=True) as conn:
        _ensure(conn)
        r = conn.execute(
            text("""SELECT id, kind, title, payload, confidence, impact, status, source,
                    created_at, reviewed_at, reviewer, note FROM evolve_proposals WHERE id=:id"""),
            {"id": proposal_id}).fetchone()
    if not r:
        return None
    payload = r[3] if isinstance(r[3], (dict, list)) else (_j.loads(r[3]) if r[3] else {})
    return {"id": r[0], "kind": r[1], "title": r[2], "payload": payload, "confidence": r[4],
            "impact": r[5], "status": r[6], "source": r[7], "created_at": r[8],
            "reviewed_at": r[9], "reviewer": r[10], "note": r[11]}
