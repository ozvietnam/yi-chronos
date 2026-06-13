"""Firebase ↔ YI-Chronos identity sync.

Phân vai (Anh chốt 2026-06-13):
    - AppChat (Firebase) sở hữu DANH TÍNH: Firebase UID (bất biến) + phone + email.
    - YI-Chronos sở hữu HỒ SƠ MỆNH LÝ: person 'self' (giờ sinh đã tìm lại, charts).
    - Khóa liên kết = Firebase UID.

Mô hình đồng bộ: lazy provisioning. Lần đầu AppChat (qua Cloud Functions của nó,
cầm service key dùng chung) gọi sang → YI tạo một "shadow user" gắn theo
firebase_uid + một person 'self' giữ birth data. Các lần sau là idempotent
upsert (cập nhật birth/display_name/phone).

Transport: service-to-service. Caller xác thực bằng header `X-API-Key` khớp env
`YI_SYNC_API_KEY`. `firebase_uid` trong body được TIN (đã do Firebase xác thực ở
phía AppChat). YI KHÔNG cầm credential Firebase — chiều đẩy notification do
Cloud Functions của AppChat đảm nhiệm (YI chỉ gọi 1 webhook).

Module này KHÔNG đụng luồng auth session hiện có; nó chỉ thêm 2 cột vào bảng
`users` (idempotent) và một router riêng `/api/sync/*`.
"""
from __future__ import annotations

import os
import secrets
import sqlite3
import time
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel

from api import auth as _auth

router = APIRouter(prefix="/api/sync", tags=["sync"])


# ─── service-to-service auth ────────────────────────────────────────────────

def _require_service_key(x_api_key: Optional[str]) -> None:
    """Caller must present X-API-Key matching env YI_SYNC_API_KEY.

    If the key is not configured, the sync surface is treated as disabled
    (503) so it can never be called unauthenticated by accident.
    """
    expected = os.environ.get("YI_SYNC_API_KEY", "")
    if not expected:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "identity sync disabled: YI_SYNC_API_KEY not configured",
        )
    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid service key")


# ─── schema migration (idempotent) ──────────────────────────────────────────

def _ensure_sync_columns(db: sqlite3.Connection) -> None:
    """Add firebase_uid (unique, nullable) + phone to users if missing."""
    cols = {r[1] for r in db.execute("PRAGMA table_info(users)").fetchall()}
    if "firebase_uid" not in cols:
        db.execute("ALTER TABLE users ADD COLUMN firebase_uid TEXT")
        # Partial unique index: many NULLs allowed, but each non-null uid unique.
        db.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_firebase_uid "
            "ON users(firebase_uid) WHERE firebase_uid IS NOT NULL"
        )
    if "phone" not in cols:
        db.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    db.commit()


def _open() -> sqlite3.Connection:
    """Open the auth DB with full schema + sync columns guaranteed present."""
    db = _auth._connect()
    _auth._init_schema(db)
    _auth._migrate_v2_suspend_columns(db)
    _ensure_sync_columns(db)
    return db


# ─── request models ─────────────────────────────────────────────────────────

class BirthInfo(BaseModel):
    # datetime_local may be missing/approximate when giờ sinh chưa được tìm lại.
    datetime_local: Optional[str] = None  # ISO 'YYYY-MM-DDTHH:MM:SS'
    gender: Optional[str] = None          # 'nam' | 'nữ'
    timezone: str = "Asia/Ho_Chi_Minh"
    birth_place: Optional[str] = None


class UpsertFromFirebaseRequest(BaseModel):
    firebase_uid: str
    phone: Optional[str] = None
    email: Optional[str] = None
    display_name: Optional[str] = None
    birth: Optional[BirthInfo] = None


# ─── endpoints ───────────────────────────────────────────────────────────────

@router.post("/upsert-from-firebase")
def upsert_from_firebase(
    req: UpsertFromFirebaseRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Lazily provision / update a YI user keyed by firebase_uid.

    Returns {yi_user_id, person_key, firebase_uid, created}. Idempotent: a
    second call with the same uid updates mutable fields and reports
    created=false.
    """
    _require_service_key(x_api_key)
    db = _open()
    try:
        now = int(time.time())
        row = db.execute(
            "SELECT user_id FROM users WHERE firebase_uid = ?", (req.firebase_uid,)
        ).fetchone()

        created = False
        if row:
            user_id = row[0]
            if req.phone is not None:
                db.execute("UPDATE users SET phone=? WHERE user_id=?", (req.phone, user_id))
            if req.display_name:
                db.execute(
                    "UPDATE users SET display_name=? WHERE user_id=?",
                    (req.display_name, user_id),
                )
        else:
            email = req.email or f"fb_{req.firebase_uid}@appchat.local"
            # Link, don't duplicate: a user may already exist by email (e.g.
            # registered earlier on YI web) — attach the firebase_uid to it.
            existing = db.execute(
                "SELECT user_id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if existing:
                user_id = existing[0]
                db.execute(
                    "UPDATE users SET firebase_uid=?, phone=COALESCE(?, phone) WHERE user_id=?",
                    (req.firebase_uid, req.phone, user_id),
                )
            else:
                created = True
                display_name = req.display_name or f"AppChat {req.firebase_uid[:8]}"
                # Shadow users authenticate via Firebase on AppChat, never via a
                # YI session → give them a random, unusable password.
                pw_hash, salt = _auth._hash_password(secrets.token_urlsafe(24))
                cur = db.execute(
                    """
                    INSERT INTO users (email, display_name, password_hash, password_salt,
                                       role, firebase_uid, phone, created_at)
                    VALUES (?, ?, ?, ?, 'user', ?, ?, ?)
                    """,
                    (email, display_name, pw_hash, salt, req.firebase_uid, req.phone, now),
                )
                user_id = cur.lastrowid

        person_key = "self"
        if req.birth is not None:
            b = req.birth
            name = req.display_name or "self"
            existing_p = db.execute(
                "SELECT id FROM user_persons WHERE user_id=? AND person_key=?",
                (user_id, person_key),
            ).fetchone()
            if existing_p:
                db.execute(
                    """
                    UPDATE user_persons
                       SET name=?,
                           gender=COALESCE(?, gender),
                           birth_datetime_local=COALESCE(?, birth_datetime_local),
                           timezone=?,
                           birth_place=COALESCE(?, birth_place),
                           updated_at=?
                     WHERE id=?
                    """,
                    (name, b.gender, b.datetime_local, b.timezone, b.birth_place, now, existing_p[0]),
                )
            else:
                db.execute(
                    """
                    INSERT INTO user_persons (user_id, person_key, name, relationship,
                                              gender, birth_datetime_local, timezone,
                                              birth_place, created_at, updated_at)
                    VALUES (?, 'self', ?, 'self', ?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, name, b.gender, b.datetime_local, b.timezone, b.birth_place, now, now),
                )

        db.commit()
        return {
            "yi_user_id": user_id,
            "person_key": person_key,
            "firebase_uid": req.firebase_uid,
            "created": created,
        }
    finally:
        db.close()


@router.get("/resolve/{firebase_uid}")
def resolve_firebase_uid(
    firebase_uid: str,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Look up the YI user + 'self' person linked to a firebase_uid.

    Used by AppChat to confirm linkage and to fetch the canonical (possibly
    rectified) birth profile YI holds.
    """
    _require_service_key(x_api_key)
    db = _open()
    try:
        row = db.execute(
            "SELECT user_id, email, display_name, phone FROM users WHERE firebase_uid = ?",
            (firebase_uid,),
        ).fetchone()
        if not row:
            return {"found": False}
        user_id = row[0]
        p = db.execute(
            """
            SELECT person_key, name, gender, birth_datetime_local, timezone, birth_place
              FROM user_persons WHERE user_id=? AND person_key='self'
            """,
            (user_id,),
        ).fetchone()
        self_person = None
        if p:
            self_person = {
                "person_key": p[0],
                "name": p[1],
                "gender": p[2],
                "birth_datetime_local": p[3],
                "timezone": p[4],
                "birth_place": p[5],
            }
        return {
            "found": True,
            "yi_user_id": user_id,
            "email": row[1],
            "display_name": row[2],
            "phone": row[3],
            "self_person": self_person,
        }
    finally:
        db.close()
