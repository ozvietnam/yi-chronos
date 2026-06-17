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
    _auth._migrate_casting_algo_version_column(db)
    _ensure_sync_columns(db)
    return db


def _user_id_for_uid(db: sqlite3.Connection, firebase_uid: str) -> Optional[int]:
    """Resolve a firebase_uid → YI user_id, or None if not synced yet."""
    row = db.execute(
        "SELECT user_id FROM users WHERE firebase_uid = ?", (firebase_uid,)
    ).fetchone()
    return row[0] if row else None


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


class CastingSaveRequest(BaseModel):
    """H1 — một lần cast / luận do AppChat đẩy sang (qua Cloud Functions)."""
    firebase_uid: str
    method: str                                # 'tu_vi' | 'bat_tu' | 'luc_hao' | ...
    subject_person_key: Optional[str] = None
    question: Optional[str] = None
    input_json: Optional[dict] = None
    result_json: dict
    verdict: Optional[str] = None
    tags: Optional[str] = None
    note: Optional[str] = None


class FavoriteSaveRequest(BaseModel):
    """H1 — một mục favorite (vd gieo duyên couple_match) do AppChat đẩy sang."""
    firebase_uid: str
    kind: str                                  # 'couple_match' | 'auspicious_day' | ...
    label: str
    payload_json: dict


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


# ─── H1: lịch sử chảy qua cầu (service-keyed) ────────────────────────────────

@router.post("/castings")
def save_casting_from_bridge(
    req: CastingSaveRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Lưu một lần cast/luận vào lịch sử user, đóng dấu `algo_version`.

    Gọi bởi Cloud Functions của AppChat sau khi cast xong → mọi tương tác đều
    thành lịch sử (Anh: "những lần hỏi … đều cần lưu lại"). 404 nếu uid chưa sync.
    """
    _require_service_key(x_api_key)
    import json as _json
    from engine.algo_version import algo_version

    av = algo_version(req.method)
    db = _open()
    try:
        user_id = _user_id_for_uid(db, req.firebase_uid)
        if user_id is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "firebase_uid not synced")
        cur = db.execute(
            """
            INSERT INTO user_castings
                (user_id, method, subject_person_key, question,
                 input_json, result_json, verdict, tags, note, algo_version, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, req.method, req.subject_person_key, req.question,
                _json.dumps(req.input_json, ensure_ascii=False) if req.input_json else None,
                _json.dumps(req.result_json, ensure_ascii=False),
                req.verdict, req.tags, req.note, av, int(time.time()),
            ),
        )
        db.commit()
        return {"status": "ok", "id": cur.lastrowid, "algo_version": av}
    finally:
        db.close()


@router.post("/favorites")
def save_favorite_from_bridge(
    req: FavoriteSaveRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Lưu một mục favorite (vd gieo duyên couple_match) vào lịch sử user."""
    _require_service_key(x_api_key)
    import json as _json

    db = _open()
    try:
        user_id = _user_id_for_uid(db, req.firebase_uid)
        if user_id is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "firebase_uid not synced")
        cur = db.execute(
            "INSERT INTO user_favorites (user_id, kind, label, payload_json, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, req.kind, req.label,
             _json.dumps(req.payload_json, ensure_ascii=False), int(time.time())),
        )
        db.commit()
        return {"status": "ok", "id": cur.lastrowid}
    finally:
        db.close()


# ─── H2: lịch sử hợp nhất (castings + favorites) cho AppChat ─────────────────

@router.get("/history/{firebase_uid}")
def history_for_uid(
    firebase_uid: str,
    method: Optional[str] = None,
    kind: Optional[str] = None,
    type: Optional[str] = None,        # 'casting' | 'favorite' | None (cả hai)
    limit: int = 50,
    offset: int = 0,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Lịch sử hợp nhất của 1 user, mới nhất trước, phân trang + lọc.

    Gộp `user_castings` (type=casting) + `user_favorites` (type=favorite), mỗi
    item gắn `type` + `algo_version` (nếu có). AppChat dựng tab "Lịch sử" từ đây.
    """
    _require_service_key(x_api_key)
    import json as _json

    db = _open()
    try:
        user_id = _user_id_for_uid(db, firebase_uid)
        if user_id is None:
            return {"found": False}

        items: list[dict] = []

        if type in (None, "casting") and not kind:
            sql = (
                "SELECT id, method, subject_person_key, question, result_json, "
                "verdict, tags, note, algo_version, created_at FROM user_castings WHERE user_id=?"
            )
            params: list = [user_id]
            if method:
                sql += " AND method=?"
                params.append(method)
            for r in db.execute(sql, params).fetchall():
                try:
                    result = _json.loads(r[4]) if r[4] else None
                except Exception:
                    result = None
                items.append({
                    "type": "casting", "id": r[0], "method": r[1],
                    "subject_person_key": r[2], "question": r[3], "result": result,
                    "verdict": r[5], "tags": r[6], "note": r[7],
                    "algo_version": r[8], "created_at": r[9],
                })

        if type in (None, "favorite") and not method:
            sql = "SELECT id, kind, label, payload_json, created_at FROM user_favorites WHERE user_id=?"
            params = [user_id]
            if kind:
                sql += " AND kind=?"
                params.append(kind)
            for r in db.execute(sql, params).fetchall():
                try:
                    payload = _json.loads(r[3]) if r[3] else None
                except Exception:
                    payload = None
                items.append({
                    "type": "favorite", "id": r[0], "kind": r[1], "label": r[2],
                    "payload": payload, "created_at": r[4],
                })

        # Hợp nhất theo thời gian, mới nhất trước; phân trang trong bộ nhớ
        # (per-user nên nhỏ — nếu sau này phình to sẽ chuyển sang UNION + index).
        items.sort(key=lambda it: it["created_at"], reverse=True)
        total = len(items)
        page = items[offset:offset + limit]
        return {
            "found": True,
            "yi_user_id": user_id,
            "items": page,
            "count": len(page),
            "total": total,
        }
    finally:
        db.close()
