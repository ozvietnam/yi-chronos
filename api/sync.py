"""Firebase ↔ YI-Chronos identity sync + lịch sử (H1/H2) qua cầu service-keyed.

Phân vai (Anh chốt 2026-06-13):
    - AppChat (Firebase) sở hữu DANH TÍNH: Firebase UID (bất biến) + phone + email.
    - YI-Chronos sở hữu HỒ SƠ MỆNH LÝ: person 'self' (giờ sinh đã tìm lại, charts).
    - Khóa liên kết = Firebase UID.

Transport: service-to-service. Caller xác thực bằng header `X-API-Key` khớp env
`YI_SYNC_API_KEY`. `firebase_uid` trong body được TIN (đã do Firebase xác thực ở
phía AppChat).

P0-2b (2026-06-17): chuyển từ sqlite3 trực tiếp → `engine.db` (SQLAlchemy
dual-driver Postgres/SQLite). Mọi thao tác là service-to-service theo firebase_uid
tường minh → `session_scope(service=True)` (bypass RLS trên Postgres). API + hành vi
GIỮ NGUYÊN. Non-breaking: prod chưa set DATABASE_URL vẫn dùng users.sqlite3 cũ.
"""
from __future__ import annotations

import logging
import secrets
import sqlite3
import time
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text

from api import auth as _auth
from engine.db import database_url, is_postgres, session_scope

router = APIRouter(prefix="/api/sync", tags=["sync"])
logger = logging.getLogger(__name__)


# ─── service-to-service auth ────────────────────────────────────────────────

def _require_service_key(x_api_key: Optional[str]) -> None:
    """Caller must present X-API-Key matching env YI_SYNC_API_KEY.

    If the key is not configured, the sync surface is treated as disabled
    (503) so it can never be called unauthenticated by accident.
    """
    import os
    expected = os.environ.get("YI_SYNC_API_KEY", "")
    if not expected:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "identity sync disabled: YI_SYNC_API_KEY not configured",
        )
    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid service key")


# ─── schema ensure (driver-aware) ───────────────────────────────────────────

def _ensure_sync_columns(db: sqlite3.Connection) -> None:
    """Add firebase_uid (unique, nullable) + phone to users if missing (SQLite)."""
    cols = {r[1] for r in db.execute("PRAGMA table_info(users)").fetchall()}
    if "firebase_uid" not in cols:
        db.execute("ALTER TABLE users ADD COLUMN firebase_uid TEXT")
        db.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_firebase_uid "
            "ON users(firebase_uid) WHERE firebase_uid IS NOT NULL"
        )
    if "phone" not in cols:
        db.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    db.commit()


def _ensure_schema() -> None:
    """SQLite (dev/test): tạo + migrate schema user-store trên đúng file engine.
    Postgres (prod): no-op — schema.sql đã áp khi deploy (runbook P0)."""
    if is_postgres():
        return
    path = database_url().replace("sqlite:///", "", 1)
    con = sqlite3.connect(path)
    try:
        _auth._init_schema(con)
        _auth._migrate_v2_suspend_columns(con)
        _auth._migrate_casting_algo_version_column(con)
        _ensure_sync_columns(con)
    finally:
        con.close()


def _json_expr(col: str) -> str:
    """VALUES expr cho cột JSON: PG cast JSONB; SQLite giữ text."""
    return f"CAST(:{col} AS JSONB)" if is_postgres() else f":{col}"


def _as_obj(v):
    """Parse giá trị JSON đọc ra: psycopg trả dict/list sẵn; sqlite trả text."""
    import json as _json
    if v is None or isinstance(v, (dict, list)):
        return v
    try:
        return _json.loads(v)
    except Exception:
        return None


def _user_id_for_uid(conn, firebase_uid: str) -> Optional[int]:
    """Resolve a firebase_uid → YI user_id, or None if not synced yet."""
    row = conn.execute(
        text("SELECT user_id FROM users WHERE firebase_uid = :uid"),
        {"uid": firebase_uid},
    ).fetchone()
    return row[0] if row else None


# ─── sync-job result store (#50): khi broker Celery chưa sẵn sàng (prod chưa có
# Redis — #41), quick tier chạy ĐỒNG BỘ inline rồi lưu kết quả ở đây để endpoint
# poll vẫn trả {state:SUCCESS} theo đúng contract AppChat. Portable SQLite+PG. ──

def _ensure_quick_jobs(conn) -> None:
    conn.execute(text(
        "CREATE TABLE IF NOT EXISTS quick_job_results ("
        "job_id TEXT PRIMARY KEY, result_json TEXT, created_at BIGINT)"
    ))


def _save_quick_result(conn, job_id: str, result: dict) -> None:
    import json
    _ensure_quick_jobs(conn)
    conn.execute(
        text("INSERT INTO quick_job_results (job_id, result_json, created_at) "
             "VALUES (:j, :r, :t)"),
        {"j": job_id, "r": json.dumps(result, ensure_ascii=False), "t": int(time.time())},
    )


def _get_quick_result(conn, job_id: str) -> Optional[dict]:
    import json
    _ensure_quick_jobs(conn)
    row = conn.execute(
        text("SELECT result_json FROM quick_job_results WHERE job_id = :j"),
        {"j": job_id},
    ).fetchone()
    if not row:
        return None
    try:
        return json.loads(row[0])
    except Exception:
        return None


# ─── request models ─────────────────────────────────────────────────────────

class BirthInfo(BaseModel):
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


class SyncPersonUpsertRequest(BaseModel):
    """Y5 (#36) — lưu hồ sơ 'đối tượng so khớp' (partner/candidate) cho 1 user.

    person_key tự do (KHÁC 'self' — 'self' set qua upsert-from-firebase): vd
    'partner', 'crush', 'candidate_1'. Idempotent theo (user_id, person_key).
    """
    firebase_uid: str
    person_key: str
    name: str
    gender: Optional[str] = None
    birth_datetime_local: Optional[str] = None
    timezone: str = "Asia/Ho_Chi_Minh"
    birth_place: Optional[str] = None
    relationship: Optional[str] = None         # 'partner' | 'spouse' | 'crush' | ...


# ─── endpoints ───────────────────────────────────────────────────────────────

@router.post("/upsert-from-firebase")
def upsert_from_firebase(
    req: UpsertFromFirebaseRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Lazily provision / update a YI user keyed by firebase_uid. Idempotent."""
    _require_service_key(x_api_key)
    _ensure_schema()
    now = int(time.time())
    with session_scope(service=True) as conn:
        row = conn.execute(
            text("SELECT user_id FROM users WHERE firebase_uid = :uid"),
            {"uid": req.firebase_uid},
        ).fetchone()

        created = False
        if row:
            user_id = row[0]
            if req.phone is not None:
                conn.execute(text("UPDATE users SET phone=:p WHERE user_id=:id"),
                             {"p": req.phone, "id": user_id})
            if req.display_name:
                conn.execute(text("UPDATE users SET display_name=:d WHERE user_id=:id"),
                             {"d": req.display_name, "id": user_id})
        else:
            email = req.email or f"fb_{req.firebase_uid}@appchat.local"
            # Link, don't duplicate: a user may already exist by email.
            existing = conn.execute(
                text("SELECT user_id FROM users WHERE email = :e"), {"e": email},
            ).fetchone()
            if existing:
                user_id = existing[0]
                conn.execute(
                    text("UPDATE users SET firebase_uid=:uid, phone=COALESCE(:p, phone) "
                         "WHERE user_id=:id"),
                    {"uid": req.firebase_uid, "p": req.phone, "id": user_id},
                )
            else:
                created = True
                display_name = req.display_name or f"AppChat {req.firebase_uid[:8]}"
                pw_hash, salt = _auth._hash_password(secrets.token_urlsafe(24))
                user_id = conn.execute(
                    text("INSERT INTO users (email, display_name, password_hash, "
                         "password_salt, role, firebase_uid, phone, created_at) "
                         "VALUES (:e,:d,:h,:s,'user',:uid,:p,:now) RETURNING user_id"),
                    {"e": email, "d": display_name, "h": pw_hash, "s": salt,
                     "uid": req.firebase_uid, "p": req.phone, "now": now},
                ).scalar()

        person_key = "self"
        if req.birth is not None:
            b = req.birth
            name = req.display_name or "self"
            existing_p = conn.execute(
                text("SELECT id FROM user_persons WHERE user_id=:id AND person_key=:pk"),
                {"id": user_id, "pk": person_key},
            ).fetchone()
            if existing_p:
                conn.execute(
                    text("""UPDATE user_persons
                               SET name=:name, gender=COALESCE(:g, gender),
                                   birth_datetime_local=COALESCE(:bdt, birth_datetime_local),
                                   timezone=:tz, birth_place=COALESCE(:bp, birth_place),
                                   updated_at=:now
                             WHERE id=:pid"""),
                    {"name": name, "g": b.gender, "bdt": b.datetime_local, "tz": b.timezone,
                     "bp": b.birth_place, "now": now, "pid": existing_p[0]},
                )
            else:
                conn.execute(
                    text("""INSERT INTO user_persons (user_id, person_key, name, relationship,
                                gender, birth_datetime_local, timezone, birth_place,
                                created_at, updated_at)
                            VALUES (:id,'self',:name,'self',:g,:bdt,:tz,:bp,:now,:now)"""),
                    {"id": user_id, "name": name, "g": b.gender, "bdt": b.datetime_local,
                     "tz": b.timezone, "bp": b.birth_place, "now": now},
                )

        return {
            "yi_user_id": user_id,
            "person_key": person_key,
            "firebase_uid": req.firebase_uid,
            "created": created,
        }


@router.get("/resolve/{firebase_uid}")
def resolve_firebase_uid(
    firebase_uid: str,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Look up the YI user + 'self' person linked to a firebase_uid."""
    _require_service_key(x_api_key)
    _ensure_schema()
    with session_scope(service=True) as conn:
        row = conn.execute(
            text("SELECT user_id, email, display_name, phone FROM users WHERE firebase_uid = :uid"),
            {"uid": firebase_uid},
        ).fetchone()
        if not row:
            return {"found": False}
        user_id = row[0]
        p = conn.execute(
            text("""SELECT person_key, name, gender, birth_datetime_local, timezone, birth_place
                      FROM user_persons WHERE user_id=:id AND person_key='self'"""),
            {"id": user_id},
        ).fetchone()
        self_person = None
        if p:
            self_person = {
                "person_key": p[0], "name": p[1], "gender": p[2],
                "birth_datetime_local": p[3], "timezone": p[4], "birth_place": p[5],
            }
        return {
            "found": True, "yi_user_id": user_id, "email": row[1],
            "display_name": row[2], "phone": row[3], "self_person": self_person,
        }


# ─── Y5 (#36): person store cho so khớp tình duyên (service-keyed) ───────────
# Kiến trúc đã chốt (contract §7 item 4): YI là sổ cái, person qua /api/sync/*.
# 'self' set qua upsert-from-firebase; đối tượng so khớp (partner/candidate) set
# qua đây. Compatibility VẪN stateless (§5.2) — AppChat đọc person rồi gọi cast.

@router.post("/persons")
def upsert_person(
    req: SyncPersonUpsertRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Lưu/cập nhật 1 person (đối tượng so khớp) cho user. Idempotent theo person_key."""
    _require_service_key(x_api_key)
    _ensure_schema()
    now = int(time.time())
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, req.firebase_uid)
        if user_id is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "user chưa sync — gọi /api/sync/upsert-from-firebase trước",
            )
        existing = conn.execute(
            text("SELECT id FROM user_persons WHERE user_id=:id AND person_key=:pk"),
            {"id": user_id, "pk": req.person_key},
        ).fetchone()
        created = existing is None
        if existing:
            conn.execute(
                text("""UPDATE user_persons
                           SET name=:name, relationship=COALESCE(:rel, relationship),
                               gender=COALESCE(:g, gender),
                               birth_datetime_local=COALESCE(:bdt, birth_datetime_local),
                               timezone=:tz, birth_place=COALESCE(:bp, birth_place),
                               updated_at=:now
                         WHERE id=:pid"""),
                {"name": req.name, "rel": req.relationship, "g": req.gender,
                 "bdt": req.birth_datetime_local, "tz": req.timezone,
                 "bp": req.birth_place, "now": now, "pid": existing[0]},
            )
        else:
            conn.execute(
                text("""INSERT INTO user_persons (user_id, person_key, name, relationship,
                            gender, birth_datetime_local, timezone, birth_place,
                            created_at, updated_at)
                        VALUES (:id,:pk,:name,:rel,:g,:bdt,:tz,:bp,:now,:now)"""),
                {"id": user_id, "pk": req.person_key, "name": req.name,
                 "rel": req.relationship, "g": req.gender,
                 "bdt": req.birth_datetime_local, "tz": req.timezone,
                 "bp": req.birth_place, "now": now},
            )
        return {"yi_user_id": user_id, "person_key": req.person_key, "created": created}


@router.get("/persons/{firebase_uid}")
def list_persons(
    firebase_uid: str,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Liệt kê mọi person của user (self + đối tượng so khớp) — cho AppChat pick."""
    _require_service_key(x_api_key)
    _ensure_schema()
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, firebase_uid)
        if user_id is None:
            return {"found": False, "persons": []}
        rows = conn.execute(
            text("""SELECT person_key, name, relationship, gender,
                           birth_datetime_local, timezone, birth_place
                      FROM user_persons WHERE user_id=:id ORDER BY person_key"""),
            {"id": user_id},
        ).fetchall()
        persons = [
            {"person_key": r[0], "name": r[1], "relationship": r[2], "gender": r[3],
             "birth_datetime_local": r[4], "timezone": r[5], "birth_place": r[6]}
            for r in rows
        ]
        return {"found": True, "yi_user_id": user_id, "persons": persons}


@router.delete("/persons/{firebase_uid}/{person_key}")
def delete_person(
    firebase_uid: str,
    person_key: str,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Xóa 1 person. KHÔNG cho xóa 'self' (hồ sơ gốc của user)."""
    _require_service_key(x_api_key)
    if person_key == "self":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "không thể xóa person 'self'")
    _ensure_schema()
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, firebase_uid)
        if user_id is None:
            return {"deleted": False, "reason": "user not found"}
        res = conn.execute(
            text("DELETE FROM user_persons WHERE user_id=:id AND person_key=:pk"),
            {"id": user_id, "pk": person_key},
        )
        return {"deleted": bool(getattr(res, "rowcount", 0)), "person_key": person_key}


# ─── H1: lịch sử chảy qua cầu (service-keyed) ────────────────────────────────

@router.post("/castings")
def save_casting_from_bridge(
    req: CastingSaveRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Lưu một lần cast/luận vào lịch sử user, đóng dấu `algo_version`. 404 nếu uid chưa sync."""
    _require_service_key(x_api_key)
    _ensure_schema()
    import json as _json
    from engine.algo_version import algo_version

    av = algo_version(req.method)
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, req.firebase_uid)
        if user_id is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "firebase_uid not synced")
        new_id = conn.execute(
            text(f"""INSERT INTO user_castings
                    (user_id, method, subject_person_key, question,
                     input_json, result_json, verdict, tags, note, algo_version, created_at)
                    VALUES (:uid,:method,:spk,:q,{_json_expr('inp')},{_json_expr('res')},
                            :verdict,:tags,:note,:av,:now) RETURNING id"""),
            {
                "uid": user_id, "method": req.method, "spk": req.subject_person_key,
                "q": req.question,
                "inp": _json.dumps(req.input_json, ensure_ascii=False) if req.input_json else None,
                "res": _json.dumps(req.result_json, ensure_ascii=False),
                "verdict": req.verdict, "tags": req.tags, "note": req.note,
                "av": av, "now": int(time.time()),
            },
        ).scalar()
        return {"status": "ok", "id": new_id, "algo_version": av}


@router.post("/favorites")
def save_favorite_from_bridge(
    req: FavoriteSaveRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Lưu một mục favorite (vd gieo duyên couple_match) vào lịch sử user."""
    _require_service_key(x_api_key)
    _ensure_schema()
    import json as _json

    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, req.firebase_uid)
        if user_id is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "firebase_uid not synced")
        new_id = conn.execute(
            text(f"INSERT INTO user_favorites (user_id, kind, label, payload_json, created_at) "
                 f"VALUES (:uid,:kind,:label,{_json_expr('payload')},:now) RETURNING id"),
            {"uid": user_id, "kind": req.kind, "label": req.label,
             "payload": _json.dumps(req.payload_json, ensure_ascii=False),
             "now": int(time.time())},
        ).scalar()
        return {"status": "ok", "id": new_id}


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
    """Lịch sử hợp nhất của 1 user, mới nhất trước, phân trang + lọc."""
    _require_service_key(x_api_key)
    _ensure_schema()
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, firebase_uid)
        if user_id is None:
            return {"found": False}

        items: list[dict] = []

        if type in (None, "casting") and not kind:
            sql = ("SELECT id, method, subject_person_key, question, result_json, "
                   "verdict, tags, note, algo_version, created_at "
                   "FROM user_castings WHERE user_id=:uid")
            params: dict = {"uid": user_id}
            if method:
                sql += " AND method=:method"
                params["method"] = method
            for r in conn.execute(text(sql), params).fetchall():
                items.append({
                    "type": "casting", "id": r[0], "method": r[1],
                    "subject_person_key": r[2], "question": r[3], "result": _as_obj(r[4]),
                    "verdict": r[5], "tags": r[6], "note": r[7],
                    "algo_version": r[8], "created_at": r[9],
                })

        if type in (None, "favorite") and not method:
            sql = "SELECT id, kind, label, payload_json, created_at FROM user_favorites WHERE user_id=:uid"
            params = {"uid": user_id}
            if kind:
                sql += " AND kind=:kind"
                params["kind"] = kind
            for r in conn.execute(text(sql), params).fetchall():
                items.append({
                    "type": "favorite", "id": r[0], "kind": r[1], "label": r[2],
                    "payload": _as_obj(r[3]), "created_at": r[4],
                })

        # Hợp nhất theo thời gian, mới nhất trước; phân trang trong bộ nhớ
        # (per-user nên nhỏ — nếu phình to sẽ chuyển sang UNION + index/partition).
        items.sort(key=lambda it: it["created_at"], reverse=True)
        total = len(items)
        page = items[offset:offset + limit]
        return {
            "found": True, "yi_user_id": user_id,
            "items": page, "count": len(page), "total": total,
        }


# ─── H5: luận sâu DeepSeek (async qua Celery q_deepread) ─────────────────────

class DeepReadingRequest(BaseModel):
    firebase_uid: str
    person_key: str = "self"


@router.post("/deep-reading")
def enqueue_deep_reading(
    req: DeepReadingRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """H5 — xếp hàng job luận sâu (gói trả phí). Pre-check nhanh: 404 chưa sync,
    422 thiếu giờ sinh, 403 không có quyền (gói). Hợp lệ → enqueue → trả job_id."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine.deep_reading import precheck

    pc = precheck(req.firebase_uid, req.person_key)
    if not pc["ok"]:
        raise HTTPException(pc["code"], pc["reason"])

    from engine.tasks.jobs import deepread_run
    async_res = deepread_run.delay(firebase_uid=req.firebase_uid, person_key=req.person_key)
    return {"status": "processing", "job_id": async_res.id}


@router.get("/deep-reading/{job_id}")
def deep_reading_status(
    job_id: str,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Trạng thái job luận sâu. AppChat poll cho tới khi state=SUCCESS → result."""
    _require_service_key(x_api_key)
    from engine.tasks.celery_app import celery_app
    res = celery_app.AsyncResult(job_id)
    out: dict = {"job_id": job_id, "state": res.state}
    if res.successful():
        out["result"] = res.result
    elif res.failed():
        out["error"] = str(res.result)[:300]
    return out


# ─── H6.0: Hội Đồng Hermes (async qua Celery q_hermes) ──────────────────────

class HermesCouncilRequest(BaseModel):
    firebase_uid: str
    question: str
    person_key: str = "self"


@router.post("/hermes-council")
def enqueue_hermes_council(
    req: HermesCouncilRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """H6.0 — xếp hàng 1 lượt Hội Đồng. Rào phạm vi chạy NGAY (đồng bộ): ngoài miền /
    chưa rõ việc → trả lời mời luôn (200, KHÔNG enqueue, KHÔNG tốn LLM). Hợp lệ →
    404 chưa sync · 422 thiếu giờ sinh · 403 không có quyền → enqueue → job_id."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine.hermes_service import precheck

    pc = precheck(req.firebase_uid, req.question, req.person_key)
    if not pc["ok"]:
        if "scope" in pc:                       # ngoài miền / cần làm rõ → trả lời, không lỗi
            return {"status": pc["scope"], "reply": pc["reply"]}
        raise HTTPException(pc["code"], pc["reason"])

    from engine.tasks.jobs import hermes_council_run
    res = hermes_council_run.delay(firebase_uid=req.firebase_uid, question=req.question,
                                   person_key=req.person_key)
    return {"status": "processing", "job_id": res.id}


@router.get("/hermes-council/{job_id}")
def hermes_council_status(
    job_id: str,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Trạng thái job Hội Đồng. AppChat poll tới khi SUCCESS → result (synthesis...)."""
    _require_service_key(x_api_key)
    from engine.tasks.celery_app import celery_app
    res = celery_app.AsyncResult(job_id)
    out: dict = {"job_id": job_id, "state": res.state}
    if res.successful():
        out["result"] = res.result
    elif res.failed():
        out["error"] = str(res.result)[:300]
    return out


# ─── H6.0: Trả lời nhanh 1-sage (async qua q_hermes) ────────────────────────

class HermesQuickRequest(BaseModel):
    firebase_uid: str
    question: str
    person_key: str = "self"


@router.post("/hermes-quick")
def enqueue_hermes_quick(
    req: HermesQuickRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """H6.0 — xếp hàng 1 lượt trả lời nhanh 1-sage (everyday, rẻ). Rào phạm vi chạy NGAY
    (ngoài miền/cần làm rõ → reply, không enqueue). 404/422/403 như council."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine.hermes_service import precheck_quick

    pc = precheck_quick(req.firebase_uid, req.question, req.person_key)
    if not pc["ok"]:
        if "scope" in pc:
            return {"status": pc["scope"], "reply": pc["reply"]}
        raise HTTPException(pc["code"], pc["reason"])

    try:
        from engine.tasks.jobs import hermes_quick_run
        res = hermes_quick_run.delay(firebase_uid=req.firebase_uid, question=req.question,
                                     person_key=req.person_key)
        return {"status": "processing", "job_id": res.id}
    except Exception as e:
        # Broker Celery (Redis) chưa sẵn sàng / celery chưa cài (#41) → enqueue throw → 500 (#50).
        # Quick tier vốn ĐỒNG BỘ (run_quick "trả ngay") → chạy inline + lưu kết quả để
        # poll vẫn theo contract {processing→job_id→SUCCESS}. KHÔNG áp cho council/deep
        # (quá chậm cho HTTP sync — chờ Redis #41).
        logger.warning("hermes-quick enqueue failed (%s) → sync fallback", e)
        from engine.hermes_service import run_quick
        result = run_quick(req.firebase_uid, req.question, req.person_key)
        job_id = f"sync-{secrets.token_hex(16)}"
        with session_scope(service=True) as conn:
            _save_quick_result(conn, job_id, result)
        return {"status": "processing", "job_id": job_id}


@router.get("/hermes-quick/{job_id}")
def hermes_quick_status(
    job_id: str,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Trạng thái job trả lời nhanh."""
    _require_service_key(x_api_key)
    # Job chạy đồng bộ (sync fallback #50) → đọc từ store, không qua Celery.
    if job_id.startswith("sync-"):
        with session_scope(service=True) as conn:
            result = _get_quick_result(conn, job_id)
        if result is None:
            return {"job_id": job_id, "state": "PENDING"}
        return {"job_id": job_id, "state": "SUCCESS", "result": result}
    from engine.tasks.celery_app import celery_app
    res = celery_app.AsyncResult(job_id)
    out: dict = {"job_id": job_id, "state": res.state}
    if res.successful():
        out["result"] = res.result
    elif res.failed():
        out["error"] = str(res.result)[:300]
    return out
