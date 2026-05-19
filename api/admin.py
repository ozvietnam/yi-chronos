"""Admin router — owner-only management dashboard.

Mounted at /api/admin/* — all endpoints require role=owner.

Endpoints:
    GET    /api/admin/dashboard              KPIs + signup trend + top spenders
    GET    /api/admin/users                  list with per-user stats
    GET    /api/admin/users/{id}             detail (persons + castings + cache size)
    PATCH  /api/admin/users/{id}             update role / reset password / display_name
    DELETE /api/admin/users/{id}             cascade delete (CANNOT delete owner)
    GET    /api/admin/audit-log              paginated audit trail
    GET    /api/admin/export-csv             CSV export of all users
"""
from __future__ import annotations

import csv
import io
import json
import logging
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from api.auth import (
    AUTH_DB, _connect, _hash_password, _record_audit, require_owner,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])

CACHE_ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi/data/yi_publishing/analysis_cache")


# ─── helpers ─────────────────────────────────────────────────────────────────

def _dir_size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except Exception:
                pass
    return total


def _user_cache_paths(person_keys: list[str]) -> list[Path]:
    return [CACHE_ROOT / pk for pk in person_keys if (CACHE_ROOT / pk).exists()]


# ─── 1. Dashboard ────────────────────────────────────────────────────────────

@router.get("/dashboard")
def dashboard(request: Request) -> dict:
    """KPIs + signup trend 30d + top spenders."""
    require_owner(request)
    db = _connect()
    try:
        # KPIs
        kpis = {}
        kpis["total_users"] = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        kpis["total_owners"] = db.execute("SELECT COUNT(*) FROM users WHERE role='owner'").fetchone()[0]
        kpis["total_persons"] = db.execute("SELECT COUNT(*) FROM user_persons").fetchone()[0]
        kpis["total_castings"] = db.execute("SELECT COUNT(*) FROM user_castings").fetchone()[0]
        now = int(time.time())
        d30 = now - 30 * 86400
        d7 = now - 7 * 86400
        kpis["signups_30d"] = db.execute("SELECT COUNT(*) FROM users WHERE created_at >= ?", (d30,)).fetchone()[0]
        kpis["signups_7d"] = db.execute("SELECT COUNT(*) FROM users WHERE created_at >= ?", (d7,)).fetchone()[0]
        kpis["active_7d"] = db.execute(
            "SELECT COUNT(*) FROM users WHERE last_login_at IS NOT NULL AND last_login_at >= ?", (d7,)
        ).fetchone()[0]
        kpis["failed_logins_7d"] = db.execute(
            "SELECT COUNT(*) FROM audit_log WHERE action='login_fail' AND created_at >= ?", (d7,)
        ).fetchone()[0]

        # Signup trend — 30 buckets of 1 day each
        signup_trend = []
        for i in range(30, -1, -1):
            day_start = now - (i + 1) * 86400
            day_end = now - i * 86400
            cnt = db.execute(
                "SELECT COUNT(*) FROM users WHERE created_at >= ? AND created_at < ?",
                (day_start, day_end),
            ).fetchone()[0]
            signup_trend.append({
                "day_offset": -i,
                "label": time.strftime("%m/%d", time.localtime(day_start)),
                "count": cnt,
            })

        # Top users by # castings (proxy for engagement)
        top_users = db.execute("""
            SELECT u.user_id, u.email, u.display_name, u.role,
                   COALESCE(c.cnt, 0) AS castings_count,
                   COALESCE(p.cnt, 0) AS persons_count,
                   u.created_at, u.last_login_at
            FROM users u
            LEFT JOIN (SELECT user_id, COUNT(*) cnt FROM user_castings GROUP BY user_id) c ON c.user_id=u.user_id
            LEFT JOIN (SELECT user_id, COUNT(*) cnt FROM user_persons GROUP BY user_id) p ON p.user_id=u.user_id
            ORDER BY castings_count DESC, persons_count DESC
            LIMIT 10
        """).fetchall()
    finally:
        db.close()

    # Disk usage — sum analysis_cache for all person_keys
    disk_total_bytes = _dir_size_bytes(CACHE_ROOT)

    return {
        "status": "ok",
        "kpis": kpis,
        "signup_trend": signup_trend,
        "top_users": [
            {
                "user_id": r[0], "email": r[1], "display_name": r[2], "role": r[3],
                "castings_count": r[4], "persons_count": r[5],
                "created_at": r[6], "last_login_at": r[7],
            }
            for r in top_users
        ],
        "disk_usage_mb": round(disk_total_bytes / (1024 * 1024), 2),
        "generated_at": now,
    }


# ─── 2. List users ───────────────────────────────────────────────────────────

@router.get("/users")
def admin_list_users(
    request: Request,
    search: str = "",
    role: str = "",
    sort: str = "created_at_desc",
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Paginated list with per-user stats. Supports search by email/name + role filter."""
    require_owner(request)
    where = "WHERE 1=1"
    params: list = []
    if search:
        where += " AND (u.email LIKE ? OR u.display_name LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if role and role in ("owner", "user"):
        where += " AND u.role = ?"
        params.append(role)

    order = {
        "created_at_desc": "u.created_at DESC",
        "created_at_asc": "u.created_at ASC",
        "last_login_desc": "u.last_login_at DESC NULLS LAST",
        "email_asc": "u.email ASC",
        "castings_desc": "castings_count DESC",
    }.get(sort, "u.created_at DESC")

    db = _connect()
    try:
        total = db.execute(f"SELECT COUNT(*) FROM users u {where}", params).fetchone()[0]
        rows = db.execute(f"""
            SELECT u.user_id, u.email, u.display_name, u.role,
                   u.default_person_id, u.created_at, u.last_login_at,
                   u.must_change_password,
                   COALESCE(c.cnt, 0) AS castings_count,
                   COALESCE(p.cnt, 0) AS persons_count
            FROM users u
            LEFT JOIN (SELECT user_id, COUNT(*) cnt FROM user_castings GROUP BY user_id) c ON c.user_id=u.user_id
            LEFT JOIN (SELECT user_id, COUNT(*) cnt FROM user_persons GROUP BY user_id) p ON p.user_id=u.user_id
            {where}
            ORDER BY {order}
            LIMIT ? OFFSET ?
        """, params + [limit, offset]).fetchall()
    finally:
        db.close()

    return {
        "status": "ok",
        "total": total,
        "limit": limit,
        "offset": offset,
        "users": [
            {
                "user_id": r[0], "email": r[1], "display_name": r[2], "role": r[3],
                "default_person_id": r[4], "created_at": r[5], "last_login_at": r[6],
                "must_change_password": bool(r[7]),
                "castings_count": r[8], "persons_count": r[9],
            }
            for r in rows
        ],
    }


# ─── 3. User detail ──────────────────────────────────────────────────────────

@router.get("/users/{user_id}")
def admin_user_detail(user_id: int, request: Request) -> dict:
    """Detail view: user info + persons list + castings count + cache size."""
    require_owner(request)
    db = _connect()
    try:
        urow = db.execute("""
            SELECT user_id, email, display_name, role, default_person_id,
                   created_at, last_login_at, must_change_password
            FROM users WHERE user_id = ?
        """, (user_id,)).fetchone()
        if not urow:
            raise HTTPException(404, "User not found")
        persons = db.execute("""
            SELECT id, person_key, name, relationship, gender, birth_datetime_local,
                   birth_place, created_at, updated_at
            FROM user_persons WHERE user_id = ? ORDER BY created_at ASC
        """, (user_id,)).fetchall()
        castings = db.execute("""
            SELECT id, method, subject_person_key, question, verdict, created_at
            FROM user_castings WHERE user_id = ?
            ORDER BY created_at DESC LIMIT 30
        """, (user_id,)).fetchall()
        castings_total = db.execute(
            "SELECT COUNT(*) FROM user_castings WHERE user_id = ?", (user_id,)
        ).fetchone()[0]
    finally:
        db.close()

    person_keys = [p[1] for p in persons]
    cache_paths = _user_cache_paths(person_keys)
    cache_size_bytes = sum(_dir_size_bytes(p) for p in cache_paths)

    return {
        "status": "ok",
        "user": {
            "user_id": urow[0], "email": urow[1], "display_name": urow[2], "role": urow[3],
            "default_person_id": urow[4], "created_at": urow[5], "last_login_at": urow[6],
            "must_change_password": bool(urow[7]),
        },
        "persons": [
            {
                "id": p[0], "person_key": p[1], "name": p[2], "relationship": p[3],
                "gender": p[4], "birth_datetime_local": p[5],
                "birth_place": p[6], "created_at": p[7], "updated_at": p[8],
            }
            for p in persons
        ],
        "recent_castings": [
            {
                "id": c[0], "method": c[1], "subject_person_key": c[2],
                "question": c[3], "verdict": c[4], "created_at": c[5],
            }
            for c in castings
        ],
        "castings_total": castings_total,
        "cache_size_mb": round(cache_size_bytes / (1024 * 1024), 3),
        "cache_person_keys": person_keys,
    }


# ─── 4. PATCH user (role / reset pwd / display_name) ─────────────────────────

class AdminUpdateUserRequest(BaseModel):
    role: Optional[str] = None              # 'owner' | 'user'
    display_name: Optional[str] = None
    reset_password: Optional[bool] = None   # True → generate new temp pwd + must_change_password=1


@router.patch("/users/{user_id}")
def admin_update_user(user_id: int, req: AdminUpdateUserRequest, request: Request) -> dict:
    actor = require_owner(request)
    if user_id == actor["user_id"] and req.role and req.role != "owner":
        raise HTTPException(400, "Bạn không thể tự hạ vai trò chính mình. Nhờ owner khác làm.")

    db = _connect()
    try:
        urow = db.execute("SELECT email, role FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not urow:
            raise HTTPException(404, "User not found")
        target_email, old_role = urow

        updates = []
        params = []
        details = {}

        if req.role and req.role in ("owner", "user") and req.role != old_role:
            updates.append("role=?")
            params.append(req.role)
            details["role"] = {"from": old_role, "to": req.role}

        if req.display_name:
            new_name = req.display_name.strip()
            if len(new_name) >= 2:
                updates.append("display_name=?")
                params.append(new_name)
                details["display_name"] = new_name

        temp_password = None
        if req.reset_password:
            temp_password = secrets.token_urlsafe(9)  # ~12 chars
            pw_hash, salt = _hash_password(temp_password)
            updates.append("password_hash=?")
            updates.append("password_salt=?")
            updates.append("must_change_password=?")
            params.extend([pw_hash, salt, 1])
            # Also kill all sessions of this user
            db.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
            details["reset_password"] = True

        if not updates:
            return {"status": "ok", "updated": 0, "message": "Không có thay đổi nào"}

        params.append(user_id)
        db.execute(f"UPDATE users SET {', '.join(updates)} WHERE user_id=?", params)
        db.commit()
    finally:
        db.close()

    # Audit
    action = "admin_reset_pwd" if temp_password else "admin_update_user"
    _record_audit(action, user_id=user_id, actor_user_id=actor["user_id"],
                  target_email=target_email, request=request, details=details)

    response = {"status": "ok", "updated": len(updates)}
    if temp_password:
        response["temp_password"] = temp_password
        response["message"] = "Mật khẩu tạm thời được tạo. User phải đổi ngay khi login."
    return response


# ─── 5. DELETE user ──────────────────────────────────────────────────────────

@router.delete("/users/{user_id}")
def admin_delete_user(user_id: int, request: Request) -> dict:
    actor = require_owner(request)
    if user_id == actor["user_id"]:
        raise HTTPException(400, "Không thể tự xoá tài khoản chính mình.")

    db = _connect()
    try:
        urow = db.execute("SELECT email, role FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not urow:
            raise HTTPException(404, "User not found")
        target_email, role = urow
        if role == "owner":
            # Make sure ≥1 owner remains
            owners_left = db.execute("SELECT COUNT(*) FROM users WHERE role='owner'").fetchone()[0]
            if owners_left <= 1:
                raise HTTPException(400, "Không thể xoá owner cuối cùng.")

        # Collect person_keys to also clear analysis_cache
        person_keys = [r[0] for r in db.execute(
            "SELECT person_key FROM user_persons WHERE user_id=?", (user_id,)
        ).fetchall()]

        db.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        # FK CASCADE deletes sessions, user_persons, user_castings, user_favorites automatically
        db.commit()
    finally:
        db.close()

    # Clean cache dirs (best-effort)
    import shutil
    for pk in person_keys:
        p = CACHE_ROOT / pk
        if p.exists() and pk not in ("_founder",):  # never wipe founder cache
            try:
                shutil.rmtree(p)
            except Exception as e:
                logger.warning(f"failed to wipe cache {p}: {e}")

    _record_audit("admin_delete_user", actor_user_id=actor["user_id"],
                  target_email=target_email, request=request,
                  details={"person_keys_wiped": person_keys})
    return {"status": "ok", "deleted_user_id": user_id, "person_keys_wiped": person_keys}


# ─── 6. Audit log ────────────────────────────────────────────────────────────

@router.get("/audit-log")
def admin_audit_log(
    request: Request,
    action: str = "",
    user_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    require_owner(request)
    where = "WHERE 1=1"
    params: list = []
    if action:
        where += " AND action=?"
        params.append(action)
    if user_id is not None:
        where += " AND (user_id=? OR actor_user_id=?)"
        params.extend([user_id, user_id])

    db = _connect()
    try:
        total = db.execute(f"SELECT COUNT(*) FROM audit_log {where}", params).fetchone()[0]
        rows = db.execute(f"""
            SELECT id, user_id, actor_user_id, action, target_email,
                   ip_address, user_agent, details_json, created_at
            FROM audit_log {where}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset]).fetchall()
    finally:
        db.close()

    return {
        "status": "ok",
        "total": total,
        "limit": limit,
        "offset": offset,
        "entries": [
            {
                "id": r[0], "user_id": r[1], "actor_user_id": r[2], "action": r[3],
                "target_email": r[4], "ip_address": r[5],
                "user_agent": (r[6] or "")[:80],
                "details": json.loads(r[7]) if r[7] else None,
                "created_at": r[8],
            }
            for r in rows
        ],
    }


# ─── 7. CSV export ───────────────────────────────────────────────────────────

@router.get("/export-csv")
def admin_export_csv(request: Request):
    require_owner(request)
    db = _connect()
    try:
        rows = db.execute("""
            SELECT u.user_id, u.email, u.display_name, u.role,
                   u.created_at, u.last_login_at,
                   COALESCE(c.cnt, 0) AS castings,
                   COALESCE(p.cnt, 0) AS persons
            FROM users u
            LEFT JOIN (SELECT user_id, COUNT(*) cnt FROM user_castings GROUP BY user_id) c ON c.user_id=u.user_id
            LEFT JOIN (SELECT user_id, COUNT(*) cnt FROM user_persons GROUP BY user_id) p ON p.user_id=u.user_id
            ORDER BY u.user_id
        """).fetchall()
    finally:
        db.close()

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["user_id", "email", "display_name", "role",
                "created_at", "last_login_at", "castings", "persons"])
    for r in rows:
        w.writerow([
            r[0], r[1], r[2], r[3],
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r[4])) if r[4] else "",
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r[5])) if r[5] else "",
            r[6], r[7],
        ])
    buf.seek(0)
    filename = f"yi-users-{time.strftime('%Y%m%d-%H%M%S')}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
