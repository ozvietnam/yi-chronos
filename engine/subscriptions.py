"""Subscription / VIP feature permission engine.

Admin grants users access to premium features (VIP1+) with optional expiry +
remaining uses. Engine deducts on each use.

Feature catalog:
  - tu_vi_phe_menh_sau: DeepSeek-pro phê mệnh (deeper than free MiniMax)
  - mai_hoa_premium: (future)
  - bat_tu_dyad_premium: (future)

P0-2 (2026-06-17): chuyển từ sqlite3 trực tiếp → `engine.db` (SQLAlchemy
dual-driver Postgres/SQLite). Đây là module gating SERVER-SIDE thao tác theo
user_id tường minh (admin grant cho user khác, check_access gọi nội bộ) →
dùng `session_scope(service=True)` (bypass RLS trên Postgres). API + hành vi
GIỮ NGUYÊN; chỉ đổi tầng truy cập DB.
"""
from __future__ import annotations

import time
from typing import Optional

from sqlalchemy import text

from engine.db import session_scope

# Feature catalog — single source of truth
FEATURE_CATALOG = {
    "tu_vi_phe_menh_sau": {
        "name_vi": "Luận giải sâu Tử Vi (DeepSeek Pro)",
        "name_zh": "紫微深度论命",
        "description": "Phê mệnh sâu dùng DeepSeek V4 Pro — 10 sections theo 10 bước Trần Đoàn, ~30-40k chars Việt thuần.",
        "tier_required": "vip1",
        "cost_estimate_usd": 0.05,
        "approx_duration_sec": 60,
    },
    "tu_vi_cdk_luan_cung": {
        "name_vi": "Luận giải cung Chiếu Đởm Kinh (DeepSeek V4 Pro)",
        "name_zh": "照胆经宫位深度解读",
        "description": "Luận sâu 1 cung CDK (5 sections Việt thuần) — bản chất cung, sao đóng, quan hệ với Mệnh, áp dụng đời sống, lời khuyên. DeepSeek V4 Pro, ~60-90s, tự lưu wiki.",
        "tier_required": "vip1",
        "cost_estimate_usd": 0.02,
        "approx_duration_sec": 75,
    },
    # Future features:
    # "mai_hoa_premium": {...},
    # "bat_tu_dyad_premium": {...},
}


def list_features() -> list[dict]:
    """List all features in catalog."""
    return [{"feature_id": k, **v} for k, v in FEATURE_CATALOG.items()]


def check_access(user_id: int, feature_id: str) -> dict:
    """Check if user has access to a feature.

    Returns:
        {
          "allowed": bool,
          "reason": str (if denied),
          "subscription": {expires_at, remaining_uses, total_uses, tier} (if exists),
          "feature": catalog entry,
        }
    """
    if feature_id not in FEATURE_CATALOG:
        return {"allowed": False, "reason": "unknown_feature", "feature": None}

    feature = FEATURE_CATALOG[feature_id]
    with session_scope(service=True) as conn:
        row = conn.execute(
            text("""SELECT enabled, expires_at, remaining_uses, total_uses, tier, granted_at, notes
                    FROM user_subscriptions WHERE user_id = :uid AND feature_id = :fid"""),
            {"uid": user_id, "fid": feature_id},
        ).fetchone()

    if not row:
        return {
            "allowed": False, "reason": "no_subscription",
            "feature": feature, "subscription": None,
        }

    enabled, expires_at, remaining_uses, total_uses, tier, granted_at, notes = row
    sub_info = {
        "tier": tier,
        "enabled": bool(enabled),
        "expires_at": expires_at,
        "remaining_uses": remaining_uses,
        "total_uses": total_uses,
        "granted_at": granted_at,
        "notes": notes,
    }

    if not enabled:
        return {"allowed": False, "reason": "disabled", "feature": feature, "subscription": sub_info}

    now = int(time.time())
    if expires_at and now > expires_at:
        return {"allowed": False, "reason": "expired", "feature": feature, "subscription": sub_info}

    if remaining_uses is not None and remaining_uses <= 0:
        return {"allowed": False, "reason": "no_uses_left", "feature": feature, "subscription": sub_info}

    return {"allowed": True, "feature": feature, "subscription": sub_info}


def consume_use(user_id: int, feature_id: str) -> dict:
    """Deduct 1 use from remaining_uses + increment total_uses.

    Called AFTER successful use of feature. If no remaining_uses (unlimited), only
    increment total_uses.

    Returns:
        {"ok": bool, "remaining_uses": int | None, "total_uses": int}
    """
    with session_scope(service=True) as conn:
        row = conn.execute(
            text("SELECT remaining_uses, total_uses FROM user_subscriptions "
                 "WHERE user_id=:uid AND feature_id=:fid"),
            {"uid": user_id, "fid": feature_id},
        ).fetchone()
        if not row:
            return {"ok": False, "error": "no_subscription"}
        remaining, total = row
        new_total = total + 1
        new_remaining = remaining - 1 if remaining is not None else None
        conn.execute(
            text("UPDATE user_subscriptions SET total_uses=:t, remaining_uses=:r "
                 "WHERE user_id=:uid AND feature_id=:fid"),
            {"t": new_total, "r": new_remaining, "uid": user_id, "fid": feature_id},
        )
    return {"ok": True, "remaining_uses": new_remaining, "total_uses": new_total}


def grant_subscription(
    user_id: int,
    feature_id: str,
    *,
    tier: str = "vip1",
    enabled: bool = True,
    expires_at: Optional[int] = None,
    remaining_uses: Optional[int] = None,
    granted_by: Optional[int] = None,
    notes: Optional[str] = None,
) -> dict:
    """Grant or update a subscription. Upsert: if exists, update; else create."""
    if feature_id not in FEATURE_CATALOG:
        return {"ok": False, "error": "unknown_feature"}

    now = int(time.time())
    with session_scope(service=True) as conn:
        existing = conn.execute(
            text("SELECT id FROM user_subscriptions WHERE user_id=:uid AND feature_id=:fid"),
            {"uid": user_id, "fid": feature_id},
        ).fetchone()
        if existing:
            conn.execute(
                text("""UPDATE user_subscriptions
                        SET tier=:tier, enabled=:en, expires_at=:exp, remaining_uses=:rem,
                            granted_by=:by, granted_at=:at, notes=:notes
                        WHERE id=:id"""),
                {"tier": tier, "en": 1 if enabled else 0, "exp": expires_at,
                 "rem": remaining_uses, "by": granted_by, "at": now, "notes": notes,
                 "id": existing[0]},
            )
            action = "updated"
        else:
            conn.execute(
                text("""INSERT INTO user_subscriptions
                        (user_id, feature_id, tier, enabled, expires_at, remaining_uses,
                         granted_by, granted_at, notes)
                        VALUES (:uid, :fid, :tier, :en, :exp, :rem, :by, :at, :notes)"""),
                {"uid": user_id, "fid": feature_id, "tier": tier, "en": 1 if enabled else 0,
                 "exp": expires_at, "rem": remaining_uses, "by": granted_by, "at": now,
                 "notes": notes},
            )
            action = "created"
    return {"ok": True, "action": action, "feature_id": feature_id, "user_id": user_id}


def revoke_subscription(user_id: int, feature_id: str) -> dict:
    """Disable subscription (keeps record for audit, but enabled=0)."""
    with session_scope(service=True) as conn:
        conn.execute(
            text("UPDATE user_subscriptions SET enabled=0 WHERE user_id=:uid AND feature_id=:fid"),
            {"uid": user_id, "fid": feature_id},
        )
    return {"ok": True}


def list_user_subscriptions(user_id: int) -> list[dict]:
    """List all subscriptions for a user."""
    with session_scope(service=True) as conn:
        rows = conn.execute(
            text("""SELECT feature_id, tier, enabled, expires_at, remaining_uses, total_uses,
                           granted_at, notes
                    FROM user_subscriptions WHERE user_id=:uid"""),
            {"uid": user_id},
        ).fetchall()
    return [
        {
            "feature_id": r[0], "tier": r[1], "enabled": bool(r[2]),
            "expires_at": r[3], "remaining_uses": r[4], "total_uses": r[5],
            "granted_at": r[6], "notes": r[7],
            "feature_meta": FEATURE_CATALOG.get(r[0], {}),
        }
        for r in rows
    ]


def list_all_subscriptions(feature_id: Optional[str] = None) -> list[dict]:
    """Admin: list all subscriptions, optionally filtered by feature."""
    base = """SELECT s.user_id, u.email, u.display_name, s.feature_id, s.tier, s.enabled,
                     s.expires_at, s.remaining_uses, s.total_uses, s.granted_at, s.notes
              FROM user_subscriptions s
              JOIN users u ON u.user_id = s.user_id"""
    with session_scope(service=True) as conn:
        if feature_id:
            rows = conn.execute(
                text(base + " WHERE s.feature_id = :fid ORDER BY s.granted_at DESC"),
                {"fid": feature_id},
            ).fetchall()
        else:
            rows = conn.execute(text(base + " ORDER BY s.granted_at DESC")).fetchall()
    return [
        {
            "user_id": r[0], "email": r[1], "display_name": r[2],
            "feature_id": r[3], "tier": r[4], "enabled": bool(r[5]),
            "expires_at": r[6], "remaining_uses": r[7], "total_uses": r[8],
            "granted_at": r[9], "notes": r[10],
        }
        for r in rows
    ]
