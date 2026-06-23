"""Mã khuyến mãi tặng xu (promo / redeem codes) — cho chiến dịch trả thưởng lôi kéo user.

Anh chốt 2026-06-23: tạo mã (vd OZFREIGHT = 50 xu, 1 LẦN/user) → user nhập trên web/AppChat →
cộng xu qua **ví TRUNG TÂM** `engine.xu_wallet` (#54) → AppChat đọc số dư chung nên TỰ đồng bộ.
Admin tạo mã để tái dùng cho các campaign sau.

An toàn (like pro):
- 1-LẦN/user: UNIQUE(code, user_id) ở promo_redemptions → lần 2 chèn fail → chặn.
- Idempotent kép: grant `ref=promo:{code}:{user_id}` (xu_wallet.grant chống cộng trùng).
- Cap tổng (max_total) + hạn (expires_at) + bật/tắt (active). Dual-driver Postgres/SQLite.
"""
from __future__ import annotations

import time
from typing import Optional

from sqlalchemy import text

from engine.db import session_scope

_DDL_CODES = """
CREATE TABLE IF NOT EXISTS promo_codes (
    code         TEXT PRIMARY KEY,
    xu           BIGINT NOT NULL,
    campaign     TEXT,
    per_user_once INT NOT NULL DEFAULT 1,
    max_total    BIGINT,                 -- NULL = không giới hạn tổng lượt
    used_count   BIGINT NOT NULL DEFAULT 0,
    active       INT NOT NULL DEFAULT 1,
    expires_at   BIGINT,                 -- epoch giây; NULL = vô hạn
    note         TEXT,
    created_by   BIGINT,
    created_at   BIGINT
)
"""
_DDL_REDEMP = """
CREATE TABLE IF NOT EXISTS promo_redemptions (
    code        TEXT NOT NULL,
    user_id     BIGINT NOT NULL,
    xu          BIGINT NOT NULL,
    redeemed_at BIGINT NOT NULL
)
"""
_DDL_REDEMP_UNIQ = ("CREATE UNIQUE INDEX IF NOT EXISTS uq_promo_redemp "
                    "ON promo_redemptions(code, user_id)")


def _ensure(conn) -> None:
    conn.execute(text(_DDL_CODES))
    conn.execute(text(_DDL_REDEMP))
    conn.execute(text(_DDL_REDEMP_UNIQ))


def _norm(code: str) -> str:
    return (code or "").strip().upper()


def create_code(code: str, xu: int, *, campaign: str = "", per_user_once: bool = True,
                max_total: Optional[int] = None, expires_at: Optional[int] = None,
                note: str = "", created_by: Optional[int] = None) -> dict:
    """Tạo mã mới (owner). xu > 0. Trùng code → lỗi."""
    code = _norm(code)
    if not code:
        raise ValueError("Thiếu mã code")
    if int(xu) <= 0:
        raise ValueError("xu phải > 0")
    with session_scope(service=True) as conn:
        _ensure(conn)
        if conn.execute(text("SELECT 1 FROM promo_codes WHERE code=:c"), {"c": code}).fetchone():
            raise ValueError(f"Mã '{code}' đã tồn tại")
        conn.execute(text(
            """INSERT INTO promo_codes (code, xu, campaign, per_user_once, max_total,
                   used_count, active, expires_at, note, created_by, created_at)
               VALUES (:c,:x,:cp,:once,:mx,0,1,:exp,:note,:by,:now)"""),
            {"c": code, "x": int(xu), "cp": campaign, "once": 1 if per_user_once else 0,
             "mx": max_total, "exp": expires_at, "note": note,
             "by": created_by, "now": int(time.time())})
    return get_code(code)


def get_code(code: str) -> Optional[dict]:
    code = _norm(code)
    with session_scope(service=True) as conn:
        _ensure(conn)
        r = conn.execute(text(
            """SELECT code, xu, campaign, per_user_once, max_total, used_count, active,
                      expires_at, note, created_at FROM promo_codes WHERE code=:c"""),
            {"c": code}).fetchone()
    if not r:
        return None
    return {"code": r[0], "xu": int(r[1]), "campaign": r[2], "per_user_once": bool(r[3]),
            "max_total": r[4], "used_count": int(r[5]), "active": bool(r[6]),
            "expires_at": r[7], "note": r[8], "created_at": r[9]}


def list_codes() -> list[dict]:
    with session_scope(service=True) as conn:
        _ensure(conn)
        rows = conn.execute(text(
            """SELECT code, xu, campaign, per_user_once, max_total, used_count, active,
                      expires_at, note, created_at FROM promo_codes ORDER BY created_at DESC""")).fetchall()
    return [{"code": r[0], "xu": int(r[1]), "campaign": r[2], "per_user_once": bool(r[3]),
             "max_total": r[4], "used_count": int(r[5]), "active": bool(r[6]),
             "expires_at": r[7], "note": r[8], "created_at": r[9]} for r in rows]


def set_active(code: str, active: bool) -> None:
    with session_scope(service=True) as conn:
        _ensure(conn)
        conn.execute(text("UPDATE promo_codes SET active=:a WHERE code=:c"),
                     {"a": 1 if active else 0, "c": _norm(code)})


def seed_default_codes() -> None:
    """Seed mã mặc định (idempotent, gọi lúc startup). OZFREIGHT = 50 xu, 1 lần/user
    (Anh chốt 2026-06-23 — chiến dịch lôi kéo user OZ Freight)."""
    try:
        if not get_code("OZFREIGHT"):
            create_code("OZFREIGHT", 50, campaign="OZ Freight — lôi kéo user",
                        per_user_once=True, note="Seed mặc định 2026-06-23")
    except Exception:
        pass


def redeem(user_id: int, code: str) -> dict:
    """User đổi mã → cộng xu qua ví trung tâm. Trả {ok, xu, balance, reason?}.

    Lý do từ chối: not_found · inactive · expired · exhausted · already_redeemed."""
    code = _norm(code)
    if not code:
        return {"ok": False, "reason": "empty"}
    from engine import xu_wallet

    now = int(time.time())
    with session_scope(service=True) as conn:
        _ensure(conn)
        r = conn.execute(text(
            "SELECT xu, per_user_once, max_total, used_count, active, expires_at "
            "FROM promo_codes WHERE code=:c"), {"c": code}).fetchone()
        if not r:
            return {"ok": False, "reason": "not_found"}
        xu, once, max_total, used, active, expires = int(r[0]), int(r[1]), r[2], int(r[3]), int(r[4]), r[5]
        if not active:
            return {"ok": False, "reason": "inactive"}
        if expires and now > int(expires):
            return {"ok": False, "reason": "expired"}
        if max_total is not None and used >= int(max_total):
            return {"ok": False, "reason": "exhausted"}
        if once:
            dup = conn.execute(text(
                "SELECT 1 FROM promo_redemptions WHERE code=:c AND user_id=:u"),
                {"c": code, "u": int(user_id)}).fetchone()
            if dup:
                return {"ok": False, "reason": "already_redeemed"}
        # ghi redemption TRƯỚC (UNIQUE chặn đua); nếu trùng → đã đổi rồi
        try:
            conn.execute(text(
                "INSERT INTO promo_redemptions (code, user_id, xu, redeemed_at) "
                "VALUES (:c,:u,:x,:t)"),
                {"c": code, "u": int(user_id), "x": xu, "t": now})
        except Exception:
            return {"ok": False, "reason": "already_redeemed"}
        conn.execute(text("UPDATE promo_codes SET used_count=used_count+1 WHERE code=:c"),
                     {"c": code})
    # cộng xu qua ví trung tâm (idempotent theo ref) — AppChat đọc số dư chung → tự đồng bộ
    bal = xu_wallet.grant(user_id, xu, f"promo_{code}", ref=f"promo:{code}:{int(user_id)}")
    return {"ok": True, "xu": xu, "balance": bal, "code": code, "campaign": get_code(code)["campaign"]}
