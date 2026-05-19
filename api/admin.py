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


def _user_cache_paths(person_keys: list[str], user_id: Optional[int] = None) -> list[Path]:
    """Return analysis_cache directories owned by this user.

    With per-user namespace (u{id}/{person_key}), we look under u{id}/ first,
    falling back to legacy unscoped paths for founder backward compat.
    """
    paths: list[Path] = []
    if user_id is not None:
        user_dir = CACHE_ROOT / f"u{user_id}"
        if user_dir.exists():
            paths.append(user_dir)
    for pk in person_keys:
        legacy = CACHE_ROOT / pk
        if legacy.exists() and legacy not in paths:
            paths.append(legacy)
    return paths


def _user_total_cost(user_id: int, person_keys: list[str]) -> tuple[float, int]:
    """Sum cost_usd across all analysis_cache files for this user.

    Returns: (total_cost_usd, files_scanned).
    """
    total = 0.0
    scanned = 0
    seen_files: set[Path] = set()
    for base in _user_cache_paths(person_keys, user_id):
        for jf in base.rglob("*.json"):
            if jf in seen_files:
                continue
            seen_files.add(jf)
            try:
                with jf.open() as f:
                    d = json.load(f)
                if isinstance(d, dict) and "cost_usd" in d:
                    total += float(d["cost_usd"] or 0)
                    scanned += 1
            except Exception:
                pass
    return round(total, 6), scanned


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

        kpis["suspended_users"] = db.execute(
            "SELECT COUNT(*) FROM users WHERE COALESCE(is_suspended,0)=1"
        ).fetchone()[0]

        # Top users by # castings (proxy for engagement)
        top_users = db.execute("""
            SELECT u.user_id, u.email, u.display_name, u.role,
                   COALESCE(c.cnt, 0) AS castings_count,
                   COALESCE(p.cnt, 0) AS persons_count,
                   u.created_at, u.last_login_at,
                   COALESCE(u.is_suspended, 0)
            FROM users u
            LEFT JOIN (SELECT user_id, COUNT(*) cnt FROM user_castings GROUP BY user_id) c ON c.user_id=u.user_id
            LEFT JOIN (SELECT user_id, COUNT(*) cnt FROM user_persons GROUP BY user_id) p ON p.user_id=u.user_id
            ORDER BY castings_count DESC, persons_count DESC
            LIMIT 10
        """).fetchall()
        # Compute cost per top user (capped to 10 to limit disk scan)
        top_user_persons = {}
        for r in top_users:
            person_keys = [
                pk[0] for pk in db.execute(
                    "SELECT person_key FROM user_persons WHERE user_id=?", (r[0],)
                ).fetchall()
            ]
            top_user_persons[r[0]] = person_keys
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
                "is_suspended": bool(r[8]),
                "total_cost_usd": _user_total_cost(r[0], top_user_persons.get(r[0], []))[0],
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
    status: str = "",                # 'active' | 'suspended' | 'inactive_30d'
    birth_year: Optional[int] = None,
    sort: str = "created_at_desc",
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Paginated list with per-user stats. Supports search + filters."""
    require_owner(request)
    where = "WHERE 1=1"
    params: list = []
    if search:
        where += " AND (u.email LIKE ? OR u.display_name LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if role and role in ("owner", "user"):
        where += " AND u.role = ?"
        params.append(role)
    if status == "suspended":
        where += " AND COALESCE(u.is_suspended,0)=1"
    elif status == "active":
        where += " AND COALESCE(u.is_suspended,0)=0"
    elif status == "inactive_30d":
        cutoff = int(time.time()) - 30 * 86400
        where += " AND (u.last_login_at IS NULL OR u.last_login_at < ?)"
        params.append(cutoff)
    if birth_year is not None:
        # JOIN user_persons where person_key='self' to filter by user's own birth year
        where += " AND EXISTS (SELECT 1 FROM user_persons up WHERE up.user_id=u.user_id AND up.person_key='self' AND up.birth_year=?)"
        params.append(birth_year)

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
                   COALESCE(p.cnt, 0) AS persons_count,
                   COALESCE(u.is_suspended, 0),
                   u.suspended_at, u.suspend_reason
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
                "is_suspended": bool(r[10]),
                "suspended_at": r[11], "suspend_reason": r[12],
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
                   created_at, last_login_at, must_change_password,
                   COALESCE(is_suspended, 0), suspended_at, suspend_reason
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
    cache_paths = _user_cache_paths(person_keys, user_id)
    cache_size_bytes = sum(_dir_size_bytes(p) for p in cache_paths)
    total_cost, cost_files_scanned = _user_total_cost(user_id, person_keys)

    return {
        "status": "ok",
        "user": {
            "user_id": urow[0], "email": urow[1], "display_name": urow[2], "role": urow[3],
            "default_person_id": urow[4], "created_at": urow[5], "last_login_at": urow[6],
            "must_change_password": bool(urow[7]),
            "is_suspended": bool(urow[8]),
            "suspended_at": urow[9], "suspend_reason": urow[10],
        },
        "total_cost_usd": total_cost,
        "cost_files_scanned": cost_files_scanned,
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
        "cache_paths": [str(p.relative_to(CACHE_ROOT.parent)) for p in cache_paths],
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

# ─── 8. Suspend / Unsuspend ──────────────────────────────────────────────────

class SuspendRequest(BaseModel):
    is_suspended: bool
    reason: Optional[str] = None


@router.post("/users/{user_id}/suspend")
def admin_suspend_user(user_id: int, req: SuspendRequest, request: Request) -> dict:
    actor = require_owner(request)
    if user_id == actor["user_id"]:
        raise HTTPException(400, "Không thể tự khoá chính mình.")

    db = _connect()
    try:
        urow = db.execute("SELECT email, role FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not urow:
            raise HTTPException(404, "User not found")
        if urow[1] == "owner" and req.is_suspended:
            owners_left = db.execute(
                "SELECT COUNT(*) FROM users WHERE role='owner' AND COALESCE(is_suspended,0)=0"
            ).fetchone()[0]
            if owners_left <= 1:
                raise HTTPException(400, "Không thể khoá owner cuối cùng đang active.")

        now = int(time.time()) if req.is_suspended else None
        db.execute("""
            UPDATE users SET is_suspended=?, suspended_at=?, suspend_reason=?
            WHERE user_id=?
        """, (1 if req.is_suspended else 0, now, req.reason if req.is_suspended else None, user_id))
        # Kill active sessions when suspending
        if req.is_suspended:
            db.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
        db.commit()
    finally:
        db.close()

    action = "admin_suspend" if req.is_suspended else "admin_unsuspend"
    _record_audit(action, user_id=user_id, actor_user_id=actor["user_id"],
                  target_email=urow[0], request=request,
                  details={"reason": req.reason} if req.reason else None)
    return {"status": "ok", "user_id": user_id, "is_suspended": req.is_suspended}


# ─── 9. Force re-run pipeline (admin impersonate) ───────────────────────────

@router.post("/users/{user_id}/rerun-pipeline")
def admin_rerun_pipeline(user_id: int, request: Request) -> dict:
    """Trigger background full pipeline cho user. Owner ấn khi user báo lỗi / cần refresh."""
    actor = require_owner(request)
    db = _connect()
    try:
        urow = db.execute("SELECT email, display_name FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not urow:
            raise HTTPException(404, "User not found")
        target_email = urow[0]
        prow = db.execute("""
            SELECT name, gender, birth_datetime_local, timezone
            FROM user_persons WHERE user_id=? AND person_key='self'
        """, (user_id,)).fetchone()
    finally:
        db.close()

    if not prow:
        raise HTTPException(400, f"User chưa setup profile (no person_key='self')")

    from engine.tu_vi.analyzer import TuViAnalyzer, Person
    import threading

    person = Person(
        person_key="self", name=prow[0],
        gender=prow[1] or "nam",
        birth_datetime_local=prow[2] or "",
        timezone=prow[3] or "Asia/Ho_Chi_Minh",
        user_id=user_id,
    )

    def _bg():
        try:
            an = TuViAnalyzer(person, force=True)
            an.discover_cach_cuc()
            an.dai_van_annotate()
            an.luu_nien(2026, 2030)
            an.luu_nguyet(2026)
            logger.info(f"admin rerun-pipeline done for user_id={user_id}")
        except Exception as e:
            logger.warning(f"admin rerun-pipeline failed for user_id={user_id}: {e}")

    threading.Thread(target=_bg, daemon=True).start()
    _record_audit("admin_rerun_pipeline", user_id=user_id, actor_user_id=actor["user_id"],
                  target_email=target_email, request=request)
    return {"status": "queued", "user_id": user_id, "person_key": "self"}


# ─── 10. Clear cache cho 1 user ─────────────────────────────────────────────

@router.delete("/users/{user_id}/cache")
def admin_clear_cache(user_id: int, request: Request) -> dict:
    """Xoá toàn bộ analysis_cache của 1 user (giải phóng disk hoặc force re-run)."""
    actor = require_owner(request)
    db = _connect()
    try:
        urow = db.execute("SELECT email FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not urow:
            raise HTTPException(404, "User not found")
        target_email = urow[0]
        person_keys = [r[0] for r in db.execute(
            "SELECT person_key FROM user_persons WHERE user_id=?", (user_id,)
        ).fetchall()]
    finally:
        db.close()

    import shutil
    deleted: list[str] = []
    user_dir = CACHE_ROOT / f"u{user_id}"
    if user_dir.exists():
        try:
            shutil.rmtree(user_dir)
            deleted.append(f"u{user_id}/")
        except Exception as e:
            logger.warning(f"failed to wipe {user_dir}: {e}")

    _record_audit("admin_clear_cache", user_id=user_id, actor_user_id=actor["user_id"],
                  target_email=target_email, request=request,
                  details={"deleted_paths": deleted, "person_keys": person_keys})
    return {"status": "ok", "deleted_paths": deleted}


# ─── 11. View user's PDF (admin impersonate) ────────────────────────────────

@router.get("/users/{user_id}/report-pdf")
def admin_view_user_pdf(user_id: int, request: Request):
    """Owner-only: tải PDF báo cáo lá số của 1 user bất kỳ.
    Hữu ích khi user báo lỗi và owner muốn verify giúp."""
    actor = require_owner(request)
    db = _connect()
    try:
        urow = db.execute("SELECT email FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not urow:
            raise HTTPException(404, "User not found")
        target_email = urow[0]
    finally:
        db.close()

    from fastapi.responses import FileResponse
    from engine.tu_vi.report_pdf import generate_pdf
    try:
        pdf_path = generate_pdf("self", user_id=user_id)
    except Exception as e:
        raise HTTPException(500, f"PDF gen failed: {e}")

    _record_audit("admin_view_pdf", user_id=user_id, actor_user_id=actor["user_id"],
                  target_email=target_email, request=request)
    return FileResponse(str(pdf_path), media_type="application/pdf",
                        filename=f"admin-bao-cao-uid{user_id}.pdf")


# ─── 12. Bulk action ─────────────────────────────────────────────────────────

class BulkActionRequest(BaseModel):
    user_ids: list[int]
    action: str  # 'delete' | 'suspend' | 'unsuspend' | 'reset_password' | 'clear_cache'
    reason: Optional[str] = None


@router.post("/users/bulk")
def admin_bulk_action(req: BulkActionRequest, request: Request) -> dict:
    actor = require_owner(request)
    if req.action not in ("delete", "suspend", "unsuspend", "reset_password", "clear_cache"):
        raise HTTPException(400, f"Unknown action: {req.action}")
    if actor["user_id"] in req.user_ids:
        raise HTTPException(400, "Không thể bulk-action lên chính mình.")

    results: list[dict] = []
    for uid in req.user_ids:
        try:
            if req.action == "delete":
                # Reuse single-delete logic
                r = admin_delete_user(uid, request)
                results.append({"user_id": uid, "status": "ok", "detail": r})
            elif req.action == "suspend":
                r = admin_suspend_user(uid, SuspendRequest(is_suspended=True, reason=req.reason), request)
                results.append({"user_id": uid, "status": "ok"})
            elif req.action == "unsuspend":
                r = admin_suspend_user(uid, SuspendRequest(is_suspended=False), request)
                results.append({"user_id": uid, "status": "ok"})
            elif req.action == "reset_password":
                r = admin_update_user(uid, AdminUpdateUserRequest(reset_password=True), request)
                results.append({"user_id": uid, "status": "ok", "temp_password": r.get("temp_password")})
            elif req.action == "clear_cache":
                r = admin_clear_cache(uid, request)
                results.append({"user_id": uid, "status": "ok", "deleted": r.get("deleted_paths", [])})
        except HTTPException as e:
            results.append({"user_id": uid, "status": "error", "detail": e.detail})
        except Exception as e:
            results.append({"user_id": uid, "status": "error", "detail": str(e)})

    _record_audit("admin_bulk_action", actor_user_id=actor["user_id"], request=request,
                  details={"action": req.action, "count": len(req.user_ids), "results": results})
    return {"status": "ok", "action": req.action, "results": results}


# ─── 13. Cost summary (whole system) ────────────────────────────────────────

@router.get("/costs")
def admin_costs(request: Request) -> dict:
    """Tổng chi phí DeepSeek toàn hệ thống, breakdown theo user."""
    require_owner(request)
    db = _connect()
    try:
        users = db.execute("""
            SELECT u.user_id, u.email, u.display_name
            FROM users u ORDER BY u.user_id
        """).fetchall()
        breakdown = []
        total_cost = 0.0
        total_files = 0
        for u in users:
            uid = u[0]
            person_keys = [r[0] for r in db.execute(
                "SELECT person_key FROM user_persons WHERE user_id=?", (uid,)
            ).fetchall()]
            cost, files = _user_total_cost(uid, person_keys)
            if cost > 0:
                breakdown.append({
                    "user_id": uid, "email": u[1], "display_name": u[2],
                    "cost_usd": cost, "files_count": files,
                })
                total_cost += cost
                total_files += files
        breakdown.sort(key=lambda x: x["cost_usd"], reverse=True)
    finally:
        db.close()
    return {
        "status": "ok",
        "total_cost_usd": round(total_cost, 4),
        "total_files_scanned": total_files,
        "breakdown": breakdown,
    }


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
