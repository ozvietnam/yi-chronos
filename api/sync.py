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
from fastapi.responses import JSONResponse
from pydantic import AliasChoices, BaseModel, Field, model_validator
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
            # KHÔNG ghi literal "self" vào NAME (chỉ là khóa). name rỗng → None để UPDATE
            # dùng COALESCE giữ tên đẹp cũ; INSERT mới thì lấy display_name / "Bạn".
            name = (req.display_name or "").strip() or None
            insert_name = name or (display_name or "").strip() or "Bạn"
            existing_p = conn.execute(
                text("SELECT id FROM user_persons WHERE user_id=:id AND person_key=:pk"),
                {"id": user_id, "pk": person_key},
            ).fetchone()
            if existing_p:
                conn.execute(
                    text("""UPDATE user_persons
                               SET name=COALESCE(:name, name), gender=COALESCE(:g, gender),
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
                    {"id": user_id, "name": insert_name, "g": b.gender, "bdt": b.datetime_local,
                     "tz": b.timezone, "bp": b.birth_place, "now": now},
                )

        result = {
            "yi_user_id": user_id,
            "person_key": person_key,
            "firebase_uid": req.firebase_uid,
            "created": created,
        }

    # ADR 3-tầng task 4: T2 LUÔN SẴN — pre-compute hồ sơ mệnh-lý (an sao/tứ trụ) ngay
    # sau khi có giờ sinh → lần luận sau đọc T2 tức thì (không cast lại). Best-effort:
    # cast tất định (KHÔNG LLM), lỗi KHÔNG được phá sync identity. (Ngoài with-block →
    # không nested session_scope.)
    if req.birth is not None and req.birth.datetime_local:
        try:
            from engine.menh_profile import build_profile
            build_profile(user_id)
        except Exception as e:
            logger.warning("build_profile sau sync uid=%s lỗi: %s", user_id, e)
    return result


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

    try:
        from engine.tasks.jobs import deepread_run
        async_res = deepread_run.delay(firebase_uid=req.firebase_uid, person_key=req.person_key)
        return {"status": "processing", "job_id": async_res.id}
    except Exception as e:
        # Broker Redis chưa lên prod (#41/PR#53). Tier luận sâu 30-90s → KHÔNG
        # sync-fallback được như quick (#50) → trả 503 sạch để AppChat báo graceful.
        logger.warning("deep-reading enqueue failed (broker down? #41): %s", e)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Luận sâu tạm chưa sẵn sàng (đang nâng cấp hạ tầng async). Thử lại sau.",
        )


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

    try:
        from engine.tasks.jobs import hermes_council_run
        res = hermes_council_run.delay(firebase_uid=req.firebase_uid, question=req.question,
                                       person_key=req.person_key)
        return {"status": "processing", "job_id": res.id}
    except Exception as e:
        # Broker Redis chưa lên prod (#41/PR#53). Hội Đồng nhiều phút → KHÔNG
        # sync-fallback → 503 sạch (graceful) thay vì 500 thô.
        logger.warning("hermes-council enqueue failed (broker down? #41): %s", e)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Hội Đồng tạm chưa sẵn sàng (đang nâng cấp hạ tầng async). Thử lại sau.",
        )


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


# ─── Chân Dung khách hàng — bệ phóng sang AppChat (Anh chốt 2026-06-24) ──────

class ChanDungSyncRequest(BaseModel):
    firebase_uid: str
    person_key: str = "self"


@router.post("/chan-dung")
def sync_chan_dung(req: ChanDungSyncRequest,
                   x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> dict:
    """AppChat KÉO Chân Dung khách (tổng hợp 3 lá số DETERMINISTIC: cốt cách Bát Tự + mệnh/cách-cục/
    đại-vận Tử Vi + nội tâm Chiếu Đởm + hướng dẫn) để hiển thị trong app. Đọc đồng dạng, KHÔNG predict.
    Nhanh/free; bản LLM văn xuôi sâu = sản phẩm trả phí riêng (Luận Sâu/Hội Đồng)."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine.hermes_service import _person_of
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, req.firebase_uid)
    if user_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user chưa sync")
    person = _person_of(user_id, req.person_key)
    if not person or not person.get("birth_datetime_local"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "person thiếu giờ sinh")
    from engine.chan_dung import build_chan_dung
    return build_chan_dung(person)


@router.get("/tu-vi/per-cung")
def sync_tu_vi_per_cung(firebase_uid: str, person_key: str = "self",
                        x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> dict:
    """Luận TỪNG CUNG theo SAO (free) cho AppChat (yêu cầu #2 2026-06-24): mỗi cung kèm chính tinh
    thực tế + nghĩa sao + câu luận-theo-sao. Biến lá số 'nông' → có chiều sâu. Đọc đồng dạng."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine.hermes_service import _person_of
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, firebase_uid)
    if user_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user chưa sync")
    person = _person_of(user_id, person_key)
    if not person or not person.get("birth_datetime_local"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "person thiếu giờ sinh")
    from engine.tu_vi.from_birth import cast_la_so_from_birth
    from engine.tu_vi.per_cung_reading import per_cung_star_reading
    ls = cast_la_so_from_birth(birth_datetime_local=person["birth_datetime_local"],
                               timezone=person.get("timezone") or "Asia/Ho_Chi_Minh",
                               gender=person.get("gender") or "nam")
    return {"found": True, "cung": per_cung_star_reading(ls)}


class DeepCungRequest(BaseModel):
    firebase_uid: str
    cung_key: str
    person_key: str = "self"


@router.post("/deep-cung")
def sync_deep_cung(req: DeepCungRequest,
                   x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """Luận SÂU 1 cung −10 xu (cache vĩnh viễn) cho AppChat (yêu cầu #3 2026-06-24).
    → 200 {interpretation, xu_balance, cached} · 402 {reason,need,have} · 404 not_synced · 422 missing_birth."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine.hermes_service import _person_of
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, req.firebase_uid)
    if user_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not_synced")
    person = _person_of(user_id, req.person_key)
    if not person or not person.get("birth_datetime_local"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "missing_birth")
    from engine.tu_vi.deep_cung import deep_cung_reading
    r = deep_cung_reading(user_id, person, req.cung_key)
    if r.get("error") == "invalid_cung":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid_cung")
    if r.get("insufficient"):
        return JSONResponse(status_code=402,
                            content={"reason": "insufficient_xu", "need": r["need"], "have": r["have"]})
    if r.get("error"):
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, r["error"])
    return {"interpretation": r["interpretation"], "xu_balance": r["xu_balance"], "cached": r["cached"]}


# ─── Vận hạn Tử Vi (Đại Vận / Lưu Niên / Lưu Nguyệt / Tuần) cho AppChat ──────

class VanHanSyncRequest(BaseModel):
    """Cầu AppChat cho engine van_han (P1 2026-07-14). Thiếu year/month/tuan →
    tự lấy kỳ HIỆN TẠI giờ VN — AppChat hỏi 'nguyệt vận bây giờ' không cần tự tính."""
    firebase_uid: str
    person_key: str = "self"
    tang: str = "luu_nguyet"            # dai_van | luu_nien | luu_nguyet | tuan
    cycle_index: Optional[int] = None   # dai_van (1..12) — bắt buộc cho tầng này
    year: Optional[int] = None          # luu_nien | luu_nguyet | tuan
    month: Optional[int] = None         # luu_nguyet | tuan
    tuan: Optional[int] = None          # tuan: 1 thượng · 2 trung · 3 hạ
    want_llm: bool = False              # mặc định block tất định (nhanh/free); LLM = opt-in


@router.post("/tu-vi/van-han")
def sync_tu_vi_van_han(req: VanHanSyncRequest,
                       x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> dict:
    """Vận hạn GROUNDED 1 tầng cho AppChat — mirror POST /api/tu-vi/van-han (web).

    Trả block tất định (Thể-Dụng + Tứ Hóa rọi cung + sao founder_verified, quote-or-
    silence) + narrative LLM biên-tập-từ-nguồn khi want_llm=True (per-user 30/h như
    web). Đọc đồng dạng, KHÔNG predict. Phục vụ lá số AppChat + nhắc Lưu Niên
    (prvchat#46 C2: 'cung nào được kích hoạt kỳ này')."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine.hermes_service import _person_of
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, req.firebase_uid)
    if user_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not_synced")
    person = _person_of(user_id, req.person_key)
    if not person or not person.get("birth_datetime_local"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "missing_birth")

    from datetime import datetime
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    kw: dict = {}
    if req.tang == "dai_van":
        if req.cycle_index is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "dai_van cần cycle_index (1..12)")
        kw["cycle_index"] = req.cycle_index
    elif req.tang in ("luu_nien", "luu_nguyet", "tuan"):
        kw["year"] = req.year if req.year is not None else now.year
        if req.tang in ("luu_nguyet", "tuan"):
            kw["month"] = req.month if req.month is not None else now.month
        if req.tang == "tuan":
            kw["tuan"] = req.tuan if req.tuan is not None else (
                1 if now.day <= 10 else (2 if now.day <= 20 else 3))
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"tang không hợp lệ: {req.tang}")

    if req.want_llm:                      # parity web: tuvi_llm 30/h, nhưng theo TỪNG user
        from engine import ratelimit
        if not ratelimit.allow(f"tuvi_llm_sync:{user_id}", 30, 3600):
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "tuvi_llm rate limit")

    from engine.tu_vi import van_han as vh
    try:
        out = vh.van_han_luan(person, req.tang, want_llm=req.want_llm, **kw)
    except (ValueError, KeyError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)[:120])
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


# ─── Ví Xu trung tâm (YI = nguồn chân lý) — kênh AppChat (service-keyed) ──────
# AppChat KHÔNG tự trừ ở Firestore nữa: nạp (sau RevenueCat/IAP) + đọc số dư +
# tặng xu đăng nhập đều gọi xuống đây. Tiêu xu xảy ra TRONG luồng Hermes
# (engine.hermes_service._gate) — không có endpoint "spend" rời (chống double-charge).

class XuGrantRequest(BaseModel):
    firebase_uid: str
    amount: int
    reason: str = "topup"
    ref: Optional[str] = None   # vd RevenueCat transaction id (idempotency phía caller)


@router.get("/wallet/{firebase_uid}")
def wallet_balance(
    firebase_uid: str,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Số dư ví + chi phí + lượt quick free còn lại hôm nay."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine import ratelimit, xu_wallet
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, firebase_uid)
    if user_id is None:
        return {"found": False}
    return {
        "found": True,
        "balance": xu_wallet.get_balance(user_id),
        "xu_cost": xu_wallet.XU_COST,
        "free_quick_remaining": ratelimit.remaining(
            f"quick_free:{user_id}", xu_wallet.FREE_QUICK_PER_DAY, 86400),
        "free_quick_per_day": xu_wallet.FREE_QUICK_PER_DAY,
    }


@router.get("/wallet/{firebase_uid}/transactions")
def wallet_transactions(
    firebase_uid: str,
    limit: int = 50,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Sổ cái giao dịch xu (nạp +, luận −) — màn lịch sử giao dịch AppChat (yêu cầu #4 2026-06-24).
    Contract app: items[{type:grant|spend|daily, amount:+/-, reason, created_at:iso, balance_after}]."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from datetime import datetime
    from datetime import timezone as _tz
    from engine import xu_wallet
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, firebase_uid)
    if user_id is None:
        return {"found": False, "items": []}
    n = min(max(limit, 1), 100)

    def _type(delta: int, reason: str) -> str:
        r = (reason or "").lower()
        if "daily" in r:
            return "daily"
        return "grant" if delta > 0 else "spend"

    def _iso(ts) -> Optional[str]:
        try:
            return datetime.fromtimestamp(int(ts), _tz.utc).isoformat()
        except Exception:
            return None

    items = [{"type": _type(t["delta"], t["reason"]), "amount": t["delta"],
              "reason": t["reason"], "created_at": _iso(t["ts"]),
              "balance_after": t["balance_after"]} for t in xu_wallet.recent_ledger(user_id, n)]
    return {"found": True, "balance": xu_wallet.get_balance(user_id), "items": items}


@router.post("/wallet/grant")
def wallet_grant(
    req: XuGrantRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Nạp/tặng xu (sau thanh toán đã xác thực ở AppChat). Trả số dư mới."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine import xu_wallet
    if req.amount <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "amount phải > 0")
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, req.firebase_uid)
    if user_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "firebase_uid not synced")
    bal = xu_wallet.grant(user_id, req.amount, req.reason, ref=req.ref)
    return {"status": "ok", "balance": bal}


class XuDeductRequest(BaseModel):
    firebase_uid: str
    amount: int
    reason: str = "spend"
    ref: Optional[str] = None   # idempotency key (vd hongBaoId) — cùng ref KHÔNG trừ 2 lần


@router.post("/wallet/deduct")
def wallet_deduct(
    req: XuDeductRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """Trừ xu (PRVchat lì xì / hong bao) — đối xứng /wallet/grant. IDEMPOTENT theo `ref`.
    200 {balance} · 402 {error:insufficient_funds, balance} · 404 {error:user_not_found}
    · 400 {error:invalid_request, message}. `ref`=hongBaoId để Cloud Function retry (timeout)
    KHÔNG trừ trùng tiền. Xu là ví TRUNG TÂM chung với web → trừ ở đây web thấy ngay."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine import xu_wallet
    if not isinstance(req.amount, int) or isinstance(req.amount, bool) or req.amount <= 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "invalid_request", "message": "amount must be positive"})
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, req.firebase_uid)
    if user_id is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "user_not_found"})
    r = xu_wallet.spend(user_id, req.amount, req.reason or "spend",
                        ref=req.ref, idempotent=True)
    if not r["ok"]:
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={"error": "insufficient_funds", "balance": r["balance"]})
    return {"balance": r["balance"]}


class PromoRedeemBridgeRequest(BaseModel):
    firebase_uid: str
    code: str


@router.post("/promo/redeem")
def promo_redeem_bridge(
    req: PromoRedeemBridgeRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """AppChat: user nhập MÃ QUÀ → cộng xu qua ví TRUNG TÂM (chung với web → đồng bộ 2 chiều).
    Service-keyed. 1 lần/user theo cấu hình mã (chống đổi trùng dù web hay app)."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine import promo_codes
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, req.firebase_uid)
    if user_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "firebase_uid not synced")
    r = promo_codes.redeem(user_id, req.code)
    if not r.get("ok"):
        return {"status": "error", "reason": r.get("reason")}
    return {"status": "ok", **r}


class XuClaimRequest(BaseModel):
    firebase_uid: str


@router.post("/wallet/claim-daily")
def wallet_claim_daily(
    req: XuClaimRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Tặng xu đăng nhập (login bonus) 1 lần/ngày trong cửa sổ welcome."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine import xu_wallet
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, req.firebase_uid)
    if user_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "firebase_uid not synced")
    return xu_wallet.claim_daily(user_id)


# ─── Cross-paradigm liên-phái (Bát Tự THỂ × Tử Vi DỤNG) — kênh AppChat ───────
# #55 hôn nhân song phái (1 lá, 12 khía cạnh) + #56 so đôi đích danh (2 lá).
# Trừ 30 xu qua ví TRUNG TÂM (engine.cross_paradigm.service → xu_wallet), cache "một
# việc một lần" (Iron #4) KHÔNG trừ lại. Engine LÕI đọc-đồng-dạng (Iron #4/#6/#8).

def _self_person(conn, user_id: int) -> Optional[dict]:
    """Person 'self' của user → {gender, birth_datetime_local, timezone} hoặc None."""
    p = conn.execute(
        text("""SELECT gender, birth_datetime_local, timezone
                FROM user_persons WHERE user_id=:u AND person_key='self'"""),
        {"u": user_id},
    ).fetchone()
    if not p:
        return None
    return {"gender": p[0], "birth_datetime_local": p[1],
            "timezone": p[2] or "Asia/Ho_Chi_Minh"}


def _person_by_key(conn, user_id: int, person_key: str) -> Optional[dict]:
    p = conn.execute(
        text("""SELECT gender, birth_datetime_local, timezone
                FROM user_persons WHERE user_id=:u AND person_key=:pk"""),
        {"u": user_id, "pk": person_key},
    ).fetchone()
    if not p:
        return None
    return {"gender": p[0], "birth_datetime_local": p[1],
            "timezone": p[2] or "Asia/Ho_Chi_Minh"}


class HonNhanSongPhaiRequest(BaseModel):
    firebase_uid: str
    person_key: str = "self"


@router.post("/hon-nhan-song-phai")
def hon_nhan_song_phai_bridge(
    req: HonNhanSongPhaiRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """#55 — hợp nhất song phái (12 khía cạnh) cho AppChat. 404 chưa sync · 422 thiếu
    giờ sinh · 402 không đủ xu (insufficient_xu). Trừ 30 xu (cache Iron #4 không trừ lại)."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine.cross_paradigm import service as cps
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, req.firebase_uid)
        if user_id is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "firebase_uid not synced")
        person = _person_by_key(conn, user_id, req.person_key)
    if not person or not person.get("birth_datetime_local"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "thiếu giờ sinh cho person — cần cập nhật trước khi luận")
    out = cps.run_hon_nhan_song_phai(user_id, person)
    if out.get("status") == "insufficient_xu":
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, out)
    return out


class TinhDuyenRequest(BaseModel):
    firebase_uid: str
    person_key: str = "self"


@router.post("/tinh-duyen")
def tinh_duyen_bridge(
    req: TinhDuyenRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Tình duyên nữ mệnh (engine làm giàu) cho AppChat. 404 chưa sync · 422 thiếu giờ
    sinh · 402 không đủ xu. Trừ 30 xu (cache Iron #4 không trừ lại)."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine.cross_paradigm import service as cps
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, req.firebase_uid)
        if user_id is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "firebase_uid not synced")
        person = _person_by_key(conn, user_id, req.person_key)
    if not person or not person.get("birth_datetime_local"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "thiếu giờ sinh cho person — cần cập nhật trước khi luận")
    out = cps.run_tinh_duyen(user_id, person)
    if out.get("status") == "insufficient_xu":
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, out)
    # Presentation-ready cho prvchat render (sections JSON thuần kind→widget).
    from engine.tinh_duyen.display import build_display
    out["display"] = build_display(out, person.get("gender") or "nữ",
                                    action_base="/api/sync/tinh-duyen")
    return out


class CoupleSyncRequest(BaseModel):
    firebase_uid: str
    partner_person_key: Optional[str] = None   # đối tượng đã lưu (đã có đồng thuận)
    partner_birth: Optional[BirthInfo] = None  # hoặc nhập trực tiếp (PDPL: KHÔNG lưu)
    person_key: str = "self"                   # lá của chính user


@router.post("/couple-sync")
def couple_sync_bridge(
    req: CoupleSyncRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """#56 — so đôi đích danh 2 lá cho AppChat. Người thứ 2 lấy từ partner_person_key
    (đã lưu, đã đồng thuận) hoặc partner_birth (nhập trực tiếp, KHÔNG lưu — PDPL).
    404 chưa sync · 422 thiếu giờ sinh · 402 không đủ xu. Trừ 30 xu (cache Iron #4)."""
    _require_service_key(x_api_key)
    _ensure_schema()
    from engine.cross_paradigm import service as cps
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, req.firebase_uid)
        if user_id is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "firebase_uid not synced")
        person_a = _person_by_key(conn, user_id, req.person_key)
        person_b = None
        if req.partner_person_key:
            person_b = _person_by_key(conn, user_id, req.partner_person_key)
    if req.partner_birth and req.partner_birth.datetime_local:
        person_b = {"gender": req.partner_birth.gender,
                    "birth_datetime_local": req.partner_birth.datetime_local,
                    "timezone": req.partner_birth.timezone}
    if not person_a or not person_a.get("birth_datetime_local"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "thiếu giờ sinh của bạn (person 'self')")
    if not person_b or not person_b.get("birth_datetime_local"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "thiếu giờ sinh người thứ 2 (partner_person_key hoặc partner_birth)")
    out = cps.run_couple_sync(user_id, person_a, person_b)
    if out.get("status") == "insufficient_xu":
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, out)
    return out


# ════════════════════════════════════════════════════════════════════════════
# Gieo Duyên — bridge các món còn web-only sang /api/sync cho AppChat (2026-06-25)
# 4 free (duyen/duyen-tho/hop-hon/so-sanh) + 3 sub-flow tình duyên (phac-hoa 50xu/
# gieo-que/narrate). TÁI DÙNG core web (Iron #1): KHÔNG luận lại, chỉ wrap service-key.
# ════════════════════════════════════════════════════════════════════════════

def _synced_person(firebase_uid: str, person_key: str) -> tuple[int, dict]:
    """Lookup (user_id, person) của user đã sync → raise 404 chưa sync / 422 thiếu giờ
    sinh. Dùng chung các bridge duyên (DRY)."""
    _ensure_schema()
    with session_scope(service=True) as conn:
        user_id = _user_id_for_uid(conn, firebase_uid)
        if user_id is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "firebase_uid not synced")
        person = _person_by_key(conn, user_id, person_key)
    if not person or not person.get("birth_datetime_local"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "thiếu giờ sinh cho person — cập nhật trước khi luận")
    return user_id, person


class DuyenSyncRequest(BaseModel):
    firebase_uid: str
    person_key: str = "self"


@router.post("/duyen")
async def duyen_bridge(
    req: DuyenSyncRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Bộ 4 món FREE 'đang tìm': chân dung nửa kia · đường tình duyên · năm có duyên ·
    tuổi hợp. Deterministic, không trừ xu. 404 chưa sync · 422 thiếu giờ sinh."""
    _require_service_key(x_api_key)
    _, person = _synced_person(req.firebase_uid, req.person_key)
    from api.tu_vi_3layer import DuyenInput, duyen_ca_nhan_endpoint
    from engine.tinh_duyen.duyen_display import build_duyen_display
    out = await duyen_ca_nhan_endpoint(DuyenInput(
        birth=person["birth_datetime_local"],
        gender=person.get("gender") or "nam",
        timezone=person.get("timezone") or "Asia/Ho_Chi_Minh"))
    if isinstance(out, dict) and not out.get("error"):
        out["display"] = build_duyen_display(out)
    return out


@router.post("/duyen-tho")
async def duyen_tho_bridge(
    req: DuyenSyncRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Lời văn ấm (LLM) cho 'Duyên của tôi' — FREE (service-keyed, không rate-limit user)."""
    _require_service_key(x_api_key)
    _, person = _synced_person(req.firebase_uid, req.person_key)
    from api.tu_vi_3layer import DuyenInput, duyen_ca_nhan_endpoint
    from engine.atomization.narrative_gen import generate_duyen_narrative
    base = await duyen_ca_nhan_endpoint(DuyenInput(
        birth=person["birth_datetime_local"],
        gender=person.get("gender") or "nam",
        timezone=person.get("timezone") or "Asia/Ho_Chi_Minh"))
    if base.get("error"):
        return base
    try:
        return generate_duyen_narrative(base)
    except Exception as e:  # noqa: BLE001
        return {"error": f"Lỗi sinh lời: {e}"}


class HopHonSyncRequest(BaseModel):
    firebase_uid: str
    person_key: str = "self"
    partner_birth: BirthInfo
    ten_self: str = "Bạn"
    ten_partner: str = "Người ấy"


@router.post("/hop-hon")
async def hop_hon_bridge(
    req: HopHonSyncRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Xem tuổi đôi lứa BA HỆ (Tử Vi + Bát Tự + Kinh Dịch) — FREE. Self từ firebase_uid +
    partner_birth (nhập trực tiếp, KHÔNG lưu — PDPL)."""
    _require_service_key(x_api_key)
    _, person = _synced_person(req.firebase_uid, req.person_key)
    if not req.partner_birth or not req.partner_birth.datetime_local:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "thiếu giờ sinh người ấy (partner_birth)")
    from api.tu_vi_3layer import HopHonInput, hop_hon
    from engine.tinh_duyen.duyen_display import build_hop_hon_display
    out = await hop_hon(HopHonInput(
        birth1=person["birth_datetime_local"], gender1=person.get("gender") or "nam", ten1=req.ten_self,
        birth2=req.partner_birth.datetime_local, gender2=req.partner_birth.gender or "nam", ten2=req.ten_partner,
        timezone=person.get("timezone") or req.partner_birth.timezone or "Asia/Ho_Chi_Minh"))
    if isinstance(out, dict) and not out.get("error"):
        out["display"] = build_hop_hon_display(out)
    return out


class SoSanhOther(BaseModel):
    """1 người để so. `birth` nhận CẢ object lồng `{datetime_local, gender, timezone}`
    (khớp `partner_birth` của hop-hon) LẪN chuỗi ISO phẳng (tự bọc). `gender` top-level
    = fallback nếu trong birth thiếu."""
    birth: BirthInfo
    ten: str = ""
    gender: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_flat_birth(cls, data):
        # Cho phép birth là chuỗi ISO phẳng → bọc thành {datetime_local}.
        if isinstance(data, dict) and isinstance(data.get("birth"), str):
            data = {**data, "birth": {"datetime_local": data["birth"],
                                      "gender": data.get("gender")}}
        return data


class SoSanhSyncRequest(BaseModel):
    firebase_uid: str
    person_key: str = "self"
    ten_self: str = "Bạn"
    # Nhận 'nguoi_khac' (app), 'others' (doc cũ), 'candidates' — đều map vào 1 field.
    others: list[SoSanhOther] = Field(
        default_factory=list,
        validation_alias=AliasChoices("nguoi_khac", "others", "candidates"),
    )


@router.post("/so-sanh-duyen")
async def so_sanh_duyen_bridge(
    req: SoSanhSyncRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """So nhiều người (≤8) với mình → xếp hạng tương ứng — FREE. Self từ firebase_uid,
    others nhập trực tiếp (KHÔNG lưu — PDPL)."""
    _require_service_key(x_api_key)
    _, person = _synced_person(req.firebase_uid, req.person_key)
    from api.tu_vi_3layer import SoSanhInput, _so_sanh_duyen_core
    from engine.tinh_duyen.duyen_display import build_so_sanh_display
    inp = SoSanhInput(
        me={"birth": person["birth_datetime_local"],
            "gender": person.get("gender") or "nam", "ten": req.ten_self},
        others=[{"birth": o.birth.datetime_local,
                 "gender": (o.birth.gender or o.gender or "nam"), "ten": o.ten}
                for o in req.others if o.birth and o.birth.datetime_local],
        timezone=person.get("timezone") or "Asia/Ho_Chi_Minh")
    out = await _so_sanh_duyen_core(inp)
    if isinstance(out, dict) and not out.get("error"):
        out["display"] = build_so_sanh_display(out)
    return out


class PhacHoaSyncRequest(BaseModel):
    firebase_uid: str
    person_key: str = "self"
    vung_mien: Optional[str] = None
    dan_toc: Optional[str] = None
    do_tuoi: Optional[str] = None
    gen_anh: bool = True


@router.post("/tinh-duyen/phac-hoa")
def phac_hoa_bridge(
    req: PhacHoaSyncRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Phác hoạ CHÂN DUNG BIỂU TƯỢNG người phối ngẫu (+ ảnh) — 50 xu. HOÀN xu nếu yêu cầu
    ảnh mà không tạo được (Iron #4 cache). 402 thiếu xu · 404 chưa sync · 422 thiếu giờ sinh."""
    _require_service_key(x_api_key)
    user_id, person = _synced_person(req.firebase_uid, req.person_key)
    from engine.cross_paradigm import service as cps
    out = cps.run_phac_hoa_phoi_ngau(
        user_id, person, vung_mien=req.vung_mien, dan_toc=req.dan_toc,
        do_tuoi=req.do_tuoi, gen_anh=req.gen_anh)
    if out.get("status") == "insufficient_xu":
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, out)
    from engine.tinh_duyen.duyen_display import build_phac_hoa_display
    out["display"] = build_phac_hoa_display(out)
    return out


class GieoQueSyncRequest(BaseModel):
    firebase_uid: str
    cau_hoi: str
    seed_numbers: Optional[list[int]] = None


@router.post("/tinh-duyen/gieo-que")
def gieo_que_bridge(
    req: GieoQueSyncRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Gieo 1 quẻ Mai Hoa cho câu hỏi QUYẾT ĐỊNH tình duyên — 0 xu (deterministic).
    Iron #4: không nghi không bói, KHÔNG cát/hung, KHÔNG chốt nên/không cưới-chia."""
    _require_service_key(x_api_key)
    cau_hoi = (req.cau_hoi or "").strip()
    if not cau_hoi:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "thiếu câu hỏi quyết định — không nghi không bói (Iron #4)")
    from engine.tinh_duyen.gieo_que_quyet_dinh import gieo_que_tinh_duyen
    from engine.tinh_duyen.duyen_display import build_gieo_que_display
    out = gieo_que_tinh_duyen(cau_hoi, req.seed_numbers)
    if isinstance(out, dict):
        out["display"] = build_gieo_que_display(out)
    return out


@router.post("/tinh-duyen/narrate")
def narrate_bridge(
    req: DuyenSyncRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> dict:
    """Lời thầy diễn đạt tình duyên đã luận — 0 xu nếu đã cached trong TTL (Iron #4);
    chỉ trừ 30 xu nếu user CHƯA từng luận (miss cache). 402 thiếu xu."""
    _require_service_key(x_api_key)
    user_id, person = _synced_person(req.firebase_uid, req.person_key)
    from engine.cross_paradigm import service as cps
    from engine.cross_paradigm.narrate import narrate_tinh_duyen
    out = cps.run_tinh_duyen(user_id, person)
    if out.get("status") == "insufficient_xu":
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, out)
    return {"narration": narrate_tinh_duyen(person, out)}
