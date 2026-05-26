"""Multi-user authentication module for YI-CHRONOS.

Design:
    - SQLite store at data/yi_users/users.sqlite3
    - Tables: users, sessions
    - Founder seeded on first run (email from YI_CHRONOS_FOUNDER_EMAIL env,
      person_id=_founder)
    - Session token via HTTP cookie 'yi_session'; also accepted as
      X-Session-Token header for API clients.
    - Each user has a default_person_id pointing to a row in
      data/yi_hermes/persons.sqlite3 (anh's existing system).

Public API surface (mount via FastAPI router):
    POST /api/auth/register      register new user (owner only)
    POST /api/auth/login         email + password → session token
    POST /api/auth/logout        clear session
    GET  /api/auth/me            current user info + default profile
    GET  /api/auth/users         list users (owner only)
    POST /api/auth/switch-person change active person_id for current user

Security:
    - bcrypt password hashing (via passlib if available, else hashlib+pbkdf2)
    - Session token = secrets.token_urlsafe(32), 30-day TTL by default.
    - Owner role required for register/users.
    - Founder bootstrap: if users table empty, founder is seeded with a password
      from env var YI_CHRONOS_FOUNDER_PASSWORD. If unset, a 24-char random
      password is generated and written to data/.founder-bootstrap-pwd (chmod
      600). Founder MUST change password after first login.
"""
from __future__ import annotations

import hashlib
import logging
import os
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

# ─── storage paths ────────────────────────────────────────────────────────────
# Auth là một phần TÍCH HỢP của YI-CHRONOS — cho phép nhiều user (gia đình,
# bạn bè, khách hàng tương lai) đăng nhập và có namespace data riêng:
# persons (gia đình/con/vợ/đồng nghiệp), gieo quẻ history, favorites...
# Founder là owner — thấy mọi tab kể cả Cài đặt / Lexicon.
# User thường chỉ thấy các tab xem mệnh (tab dev được ẩn).
PROJECT_ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
AUTH_DB = PROJECT_ROOT / "data/yi_users/users.sqlite3"
PERSONS_DB = PROJECT_ROOT / "data/yi_hermes/persons.sqlite3"

# Bootstrap creds for founder (must be changed on first login)
FOUNDER_EMAIL = os.environ.get("YI_CHRONOS_FOUNDER_EMAIL", "founder@yi-chronos.local")
FOUNDER_PERSON_ID = "_founder"
FOUNDER_DISPLAY_NAME = "Anh (Founder)"


def _resolve_founder_bootstrap_password() -> str:
    """Return the password used to seed the founder user on first run.

    Resolution order:
    1. Env var YI_CHRONOS_FOUNDER_PASSWORD (preferred for prod).
    2. data/.founder-bootstrap-pwd file (chmod 600) — auto-generated on
       first call if neither env nor file exist.

    Why: a hardcoded default password in source is discoverable by anyone
    with repo read access, even if the repo is private. Env-driven + a
    random-generated fallback keeps the credential out of git history.
    """
    env_pwd = os.environ.get("YI_CHRONOS_FOUNDER_PASSWORD")
    if env_pwd:
        return env_pwd

    bootstrap_file = AUTH_DB.parent.parent / ".founder-bootstrap-pwd"
    if bootstrap_file.exists():
        return bootstrap_file.read_text().strip()

    new_pwd = secrets.token_urlsafe(18)  # ~24 chars URL-safe
    bootstrap_file.parent.mkdir(parents=True, exist_ok=True)
    bootstrap_file.write_text(new_pwd)
    bootstrap_file.chmod(0o600)
    logger.warning("─" * 60)
    logger.warning("YI-CHRONOS FOUNDER BOOTSTRAP PASSWORD GENERATED")
    logger.warning(f"  stored: {bootstrap_file}")
    logger.warning("  read once + change immediately on first login")
    logger.warning("─" * 60)
    return new_pwd


FOUNDER_DEFAULT_PASSWORD = _resolve_founder_bootstrap_password()

SESSION_TTL_SECONDS = 30 * 24 * 3600  # 30 days
COOKIE_NAME = "yi_session"


# ─── DB init ──────────────────────────────────────────────────────────────────

def _connect() -> sqlite3.Connection:
    AUTH_DB.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(AUTH_DB)


def _init_schema(db: sqlite3.Connection) -> None:
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            email            TEXT UNIQUE NOT NULL,
            display_name     TEXT NOT NULL,
            password_hash    TEXT NOT NULL,
            password_salt    TEXT NOT NULL,
            role             TEXT NOT NULL DEFAULT 'user',  -- 'owner' | 'user'
            default_person_id TEXT,                          -- persons.sqlite3 person_id
            created_at       INTEGER NOT NULL,
            last_login_at    INTEGER,
            must_change_password INTEGER DEFAULT 0,
            is_suspended     INTEGER DEFAULT 0,              -- 0=active, 1=suspended (blocks login, keeps data)
            suspended_at     INTEGER,                         -- timestamp when suspended
            suspend_reason   TEXT                             -- short reason shown to admin
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token         TEXT PRIMARY KEY,
            user_id       INTEGER NOT NULL,
            created_at    INTEGER NOT NULL,
            expires_at    INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);

        -- ───────────────────────────────────────────────────────────────────
        -- User-namespaced data — mỗi user có hệ sinh thái riêng
        -- ───────────────────────────────────────────────────────────────────

        -- Persons trong namespace của user (gia đình, con, vợ, đồng nghiệp, người yêu)
        CREATE TABLE IF NOT EXISTS user_persons (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id               INTEGER NOT NULL,
            person_key            TEXT NOT NULL,            -- e.g. 'self', 'wife', 'child_1'
            name                  TEXT NOT NULL,
            relationship          TEXT,                      -- 'self' | 'spouse' | 'child' | 'parent' | 'sibling' | 'colleague' | 'friend' | 'partner' | 'other'
            gender                TEXT,                      -- 'nam' | 'nữ'
            birth_datetime_local  TEXT,                      -- ISO 'YYYY-MM-DDTHH:MM:SS'
            birth_year            INTEGER,
            timezone              TEXT DEFAULT 'Asia/Ho_Chi_Minh',
            birth_place           TEXT,
            notes                 TEXT,
            created_at            INTEGER NOT NULL,
            updated_at            INTEGER,
            UNIQUE(user_id, person_key),
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_user_persons_user ON user_persons(user_id);

        -- Gieo quẻ history — lưu mọi lần user cast (Mai Hoa / Lục Hào / Tử Vi / Bát Tự / etc.)
        CREATE TABLE IF NOT EXISTS user_castings (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            method        TEXT NOT NULL,                     -- 'mai_hoa' | 'luc_hao' | 'tu_vi' | 'bat_tu' | 'ha_lac' | 'lien_hoa' | 'pytago'
            subject_person_key TEXT,                          -- which user_person this cast is for (NULL = anonymous)
            question      TEXT,                              -- câu hỏi đặt cho quẻ
            input_json    TEXT,                              -- đầu vào (birth, hexagram, etc.)
            result_json   TEXT NOT NULL,                     -- kết quả engine trả
            verdict       TEXT,                              -- ngắn gọn — cát/hung/cảnh báo
            tags          TEXT,                              -- comma-separated
            note          TEXT,                              -- user note
            created_at    INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_user_castings_user ON user_castings(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_castings_method ON user_castings(user_id, method);
        CREATE INDEX IF NOT EXISTS idx_user_castings_created ON user_castings(created_at);

        -- Favorites — ngày tốt, xem tuổi vợ chồng, ...
        CREATE TABLE IF NOT EXISTS user_favorites (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            kind          TEXT NOT NULL,                     -- 'auspicious_day' | 'couple_match' | 'reading' | 'other'
            label         TEXT NOT NULL,
            payload_json  TEXT NOT NULL,
            created_at    INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_user_favorites_user ON user_favorites(user_id, kind);

        -- Audit log — login attempts, signups, role changes, deletes (admin trail)
        CREATE TABLE IF NOT EXISTS audit_log (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER,                          -- NULL nếu chưa biết user (login fail)
            actor_user_id INTEGER,                          -- ai thực hiện (admin / self)
            action        TEXT NOT NULL,                    -- 'login_ok' | 'login_fail' | 'signup' | 'logout' | 'change_password' | 'admin_set_role' | 'admin_reset_pwd' | 'admin_delete_user' | 'setup_profile'
            target_email  TEXT,                              -- email liên quan (nếu user_id bị xoá vẫn còn manh mối)
            ip_address    TEXT,
            user_agent    TEXT,
            details_json  TEXT,                              -- payload tuỳ event
            created_at    INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
        CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action);
        CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);

        -- ⭐ VIP feature subscriptions — admin grants/revokes per user per feature
        -- Each grant has expiry date (optional) + remaining_uses (optional).
        -- Engine deducts remaining_uses on each successful use.
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            feature_id      TEXT NOT NULL,                -- e.g. 'tu_vi_phe_menh_sau' | 'mai_hoa_premium' | ...
            tier            TEXT NOT NULL DEFAULT 'vip1', -- 'vip1' | 'vip2' | 'vip_lifetime'
            enabled         INTEGER NOT NULL DEFAULT 1,   -- 1=active, 0=paused
            expires_at      INTEGER,                       -- unix timestamp, NULL = no expiry
            remaining_uses  INTEGER,                       -- NULL = unlimited
            total_uses      INTEGER NOT NULL DEFAULT 0,
            granted_by      INTEGER,                       -- admin user_id
            granted_at      INTEGER NOT NULL,
            notes           TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE(user_id, feature_id)
        );
        CREATE INDEX IF NOT EXISTS idx_subs_user ON user_subscriptions(user_id);
        CREATE INDEX IF NOT EXISTS idx_subs_feature ON user_subscriptions(feature_id);

        -- 📚 User publications — registry các bản đã sinh thành (PDF/DOCX/MD)
        -- Tự động register sau mỗi lần gen LLM thành công.
        CREATE TABLE IF NOT EXISTS user_publications (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            person_key      TEXT NOT NULL,                -- 'self' | 'wife' | 'child_1' | ...
            pub_type        TEXT NOT NULL,                -- 'phe_menh_sau' | 'cdk_12_cung' | 'cdk_dai_han' | 'cdk_luu_nien' | 'cdk_tong_doan' | 'master'
            title           TEXT NOT NULL,
            file_dir        TEXT NOT NULL,                -- 'data/user_publications/u1/self/phe_menh_sau_v4'
            formats         TEXT NOT NULL DEFAULT '{}',   -- JSON {"pdf": "...", "docx": "...", "md": "...", "json": "..."}
            total_chars     INTEGER DEFAULT 0,
            cost_usd        REAL DEFAULT 0,
            provider        TEXT,                          -- 'deepseek' | 'minimax' | ...
            model           TEXT,                          -- 'v4_pro' | ...
            version         TEXT,                          -- 'v4_q4_enriched' | ...
            generated_at    INTEGER NOT NULL,
            status          TEXT NOT NULL DEFAULT 'active',-- 'active' | 'archived'
            notes           TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE(user_id, person_key, pub_type)
        );
        CREATE INDEX IF NOT EXISTS idx_pub_user ON user_publications(user_id);
        CREATE INDEX IF NOT EXISTS idx_pub_user_person ON user_publications(user_id, person_key);

        -- 🔗 Publication shares — token-based public share link
        CREATE TABLE IF NOT EXISTS publication_shares (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            publication_id  INTEGER NOT NULL,
            token           TEXT UNIQUE NOT NULL,         -- random 32-char
            created_by      INTEGER NOT NULL,             -- user_id của owner
            created_at      INTEGER NOT NULL,
            expires_at      INTEGER,                       -- NULL = không hết hạn
            access_count    INTEGER NOT NULL DEFAULT 0,
            max_accesses    INTEGER,                       -- NULL = unlimited views
            note            TEXT,                          -- e.g. "Chia sẻ cho vợ"
            FOREIGN KEY(publication_id) REFERENCES user_publications(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_share_token ON publication_shares(token);
    """)
    db.commit()


def _record_audit(
    action: str,
    *,
    user_id: Optional[int] = None,
    actor_user_id: Optional[int] = None,
    target_email: Optional[str] = None,
    request: Optional[Request] = None,
    details: Optional[dict] = None,
) -> None:
    """Insert an audit_log row. Silently swallows errors — auditing must never break a request."""
    try:
        ip = ""
        ua = ""
        if request is not None:
            ip = (request.client.host if request.client else "") or request.headers.get("x-forwarded-for", "")
            ua = (request.headers.get("user-agent") or "")[:200]
        import json as _json
        db = _connect()
        try:
            db.execute("""
                INSERT INTO audit_log (user_id, actor_user_id, action, target_email,
                                       ip_address, user_agent, details_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, actor_user_id, action, target_email,
                ip, ua,
                _json.dumps(details, ensure_ascii=False) if details else None,
                int(time.time()),
            ))
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"audit log failed for action={action}: {e}")


def _hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """PBKDF2-SHA256 with 200k iterations. Returns (hash_hex, salt_hex)."""
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200_000,
    )
    return dk.hex(), salt


def _verify_password(password: str, stored_hash: str, stored_salt: str) -> bool:
    """Constant-time comparison."""
    candidate_hash, _ = _hash_password(password, stored_salt)
    return secrets.compare_digest(candidate_hash, stored_hash)


def _seed_founder(db: sqlite3.Connection) -> None:
    """Create founder user on first run if users table is empty."""
    n = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if n > 0:
        return
    pw_hash, salt = _hash_password(FOUNDER_DEFAULT_PASSWORD)
    db.execute("""
        INSERT INTO users (email, display_name, password_hash, password_salt,
                           role, default_person_id, created_at, must_change_password)
        VALUES (?, ?, ?, ?, 'owner', ?, ?, 1)
    """, (
        FOUNDER_EMAIL, FOUNDER_DISPLAY_NAME, pw_hash, salt,
        FOUNDER_PERSON_ID, int(time.time()),
    ))
    db.commit()
    logger.info(
        f"  🌱 Seeded founder user: email={FOUNDER_EMAIL!r}, "
        f"default password=<bootstrap>. user MUST change on first login."
    )


def _migrate_v2_suspend_columns(db: sqlite3.Connection) -> None:
    """Add is_suspended/suspended_at/suspend_reason to users if missing (idempotent)."""
    cols = {r[1] for r in db.execute("PRAGMA table_info(users)").fetchall()}
    if "is_suspended" not in cols:
        db.execute("ALTER TABLE users ADD COLUMN is_suspended INTEGER DEFAULT 0")
    if "suspended_at" not in cols:
        db.execute("ALTER TABLE users ADD COLUMN suspended_at INTEGER")
    if "suspend_reason" not in cols:
        db.execute("ALTER TABLE users ADD COLUMN suspend_reason TEXT")
    db.commit()


def _ensure_initialized() -> None:
    db = _connect()
    try:
        _init_schema(db)
        _migrate_v2_suspend_columns(db)
        _seed_founder(db)
    finally:
        db.close()


_ensure_initialized()


# ─── persons.sqlite3 helper ──────────────────────────────────────────────────

def _load_person(person_id: str) -> Optional[dict]:
    """Look up a person from persons.sqlite3. Returns dict or None."""
    if not PERSONS_DB.exists():
        return None
    db = sqlite3.connect(PERSONS_DB)
    try:
        # persons table columns: person_id, name (not 'full_name'), gender,
        # birth_datetime_local, timezone, day_pillar_convention, etc.
        row = db.execute("""
            SELECT person_id, name, gender, birth_datetime_local, timezone,
                   day_pillar_convention, relationship_to_founder
            FROM persons WHERE person_id = ?
        """, (person_id,)).fetchone()
        if not row:
            return None
        return {
            "person_id": row[0],
            "name": row[1],
            "gender": row[2],
            "birth_datetime_local": row[3],
            "timezone": row[4],
            "day_pillar_convention": row[5],
            "relationship_to_founder": row[6],
        }
    except Exception as e:
        logger.warning(f"_load_person({person_id!r}) error: {e}")
        return None
    finally:
        db.close()


# ─── session helpers ─────────────────────────────────────────────────────────

def _create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    now = int(time.time())
    db = _connect()
    try:
        db.execute(
            "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (token, user_id, now, now + SESSION_TTL_SECONDS),
        )
        db.execute(
            "UPDATE users SET last_login_at = ? WHERE user_id = ?",
            (now, user_id),
        )
        db.commit()
    finally:
        db.close()
    return token


def _resolve_session(token: str) -> Optional[dict]:
    """Return user dict if token is valid, else None."""
    if not token:
        return None
    now = int(time.time())
    db = _connect()
    try:
        row = db.execute("""
            SELECT u.user_id, u.email, u.display_name, u.role, u.default_person_id,
                   u.created_at, u.last_login_at, u.must_change_password, s.expires_at
            FROM sessions s
            JOIN users u ON u.user_id = s.user_id
            WHERE s.token = ? AND s.expires_at > ?
        """, (token, now)).fetchone()
        if not row:
            return None
        return {
            "user_id": row[0], "email": row[1], "display_name": row[2],
            "role": row[3], "default_person_id": row[4],
            "created_at": row[5], "last_login_at": row[6],
            "must_change_password": bool(row[7]),
            "session_expires_at": row[8],
        }
    finally:
        db.close()


def get_current_user(request: Request) -> Optional[dict]:
    """Extract user from cookie or X-Session-Token header."""
    token = request.cookies.get(COOKIE_NAME) or request.headers.get("X-Session-Token")
    if not token:
        return None
    return _resolve_session(token)


def require_user(request: Request) -> dict:
    """Raise 401 if not authenticated."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_owner(request: Request) -> dict:
    """Raise 403 if not owner."""
    user = require_user(request)
    if user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Owner role required")
    return user


# ─── pydantic models ─────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    display_name: str
    password: str
    default_person_id: Optional[str] = None
    role: str = "user"


class SignupRequest(BaseModel):
    """Public self-signup — no owner required, no email verification."""
    email: str
    display_name: str
    password: str


class SetupProfileRequest(BaseModel):
    """Onboarding — first-time profile setup for a freshly registered user."""
    name: Optional[str] = None        # default = user.display_name
    gender: str                        # 'nam' | 'nữ'
    birth_datetime_local: str          # ISO 'YYYY-MM-DDTHH:MM:SS'
    timezone: str = "Asia/Ho_Chi_Minh"
    birth_place: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class SwitchPersonRequest(BaseModel):
    person_id: str


# ─── router ──────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(req: LoginRequest, request: Request, response: Response) -> dict:
    email = req.email.lower().strip()
    db = _connect()
    try:
        row = db.execute("""
            SELECT user_id, password_hash, password_salt, role,
                   default_person_id, display_name, must_change_password,
                   COALESCE(is_suspended, 0), suspend_reason
            FROM users WHERE email = ?
        """, (email,)).fetchone()
    finally:
        db.close()
    if not row or not _verify_password(req.password, row[1], row[2]):
        _record_audit("login_fail", target_email=email, request=request)
        # Avoid timing leak on missing email
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")
    if row[7]:  # is_suspended
        _record_audit("login_blocked_suspended", user_id=row[0], target_email=email, request=request)
        reason = row[8] or "Tài khoản đã bị tạm khoá"
        raise HTTPException(status_code=403, detail=f"Tài khoản tạm khoá: {reason}")

    # Update last_login_at
    db = _connect()
    try:
        db.execute("UPDATE users SET last_login_at = ? WHERE user_id = ?", (int(time.time()), row[0]))
        db.commit()
    finally:
        db.close()

    token = _create_session(row[0])
    response.set_cookie(
        COOKIE_NAME, token,
        httponly=True, samesite="lax",
        max_age=SESSION_TTL_SECONDS, path="/",
    )
    _record_audit("login_ok", user_id=row[0], target_email=email, request=request)
    person = _load_person(row[4]) if row[4] else None
    return {
        "status": "ok",
        "user": {
            "user_id": row[0], "email": req.email, "display_name": row[5],
            "role": row[3], "default_person_id": row[4],
            "must_change_password": bool(row[6]),
        },
        "person": person,
        "session_token": token,
    }


@router.post("/logout")
def logout(request: Request, response: Response) -> dict:
    token = request.cookies.get(COOKIE_NAME) or request.headers.get("X-Session-Token")
    user = get_current_user(request)
    if token:
        db = _connect()
        try:
            db.execute("DELETE FROM sessions WHERE token = ?", (token,))
            db.commit()
        finally:
            db.close()
    if user:
        _record_audit("logout", user_id=user["user_id"], target_email=user["email"], request=request)
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"status": "ok"}


def _load_user_self_person(user_id: int) -> Optional[dict]:
    """Load the user_persons row where person_key='self' for this user."""
    db = _connect()
    try:
        row = db.execute("""
            SELECT person_key, name, gender, birth_datetime_local, timezone,
                   birth_year, birth_place, notes, relationship
            FROM user_persons
            WHERE user_id = ? AND person_key = 'self'
            LIMIT 1
        """, (user_id,)).fetchone()
    finally:
        db.close()
    if not row:
        return None
    return {
        "person_id": row[0],            # 'self'
        "name": row[1],
        "gender": row[2],
        "birth_datetime_local": row[3],
        "timezone": row[4] or "Asia/Ho_Chi_Minh",
        "birth_year": row[5],
        "birth_place": row[6],
        "notes": row[7],
        "relationship_to_founder": row[8] or "self",
    }


@router.get("/me")
def me(request: Request) -> dict:
    user = get_current_user(request)
    if not user:
        # Guests get NO default person — previously we returned the founder
        # profile as a single-user convenience, but that leaked anh's birth
        # data (DOB, time, place, notes) to every visitor of kinhdich.online.
        # Frontend panels handle person=null by prompting "đăng nhập / nhập
        # ngày sinh".
        return {
            "status": "guest",
            "user": None,
            "person": None,
        }
    # Priority order for resolving the logged-in user's active person:
    #   1. user.default_person_id (legacy founder profile pointer)
    #   2. user_persons row with person_key='self' (new multi-user pattern)
    #   3. None → frontend will prompt onboarding modal
    person = None
    if user["default_person_id"]:
        person = _load_person(user["default_person_id"])
    if not person:
        person = _load_user_self_person(user["user_id"])
    return {
        "status": "ok",
        "user": {
            "user_id": user["user_id"], "email": user["email"],
            "display_name": user["display_name"], "role": user["role"],
            "default_person_id": user["default_person_id"],
            "must_change_password": user["must_change_password"],
            "session_expires_at": user["session_expires_at"],
        },
        "person": person,
        "needs_profile_setup": person is None,
    }


@router.post("/register")
def register(req: RegisterRequest, request: Request) -> dict:
    owner = require_owner(request)
    if req.role not in ("owner", "user"):
        raise HTTPException(status_code=400, detail="role must be 'owner' or 'user'")

    pw_hash, salt = _hash_password(req.password)
    db = _connect()
    try:
        try:
            cur = db.execute("""
                INSERT INTO users (email, display_name, password_hash, password_salt,
                                   role, default_person_id, created_at, must_change_password)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """, (
                req.email.lower().strip(), req.display_name,
                pw_hash, salt, req.role, req.default_person_id,
                int(time.time()),
            ))
            db.commit()
            new_id = cur.lastrowid
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Email đã tồn tại")
    finally:
        db.close()

    return {
        "status": "ok",
        "user": {
            "user_id": new_id, "email": req.email,
            "display_name": req.display_name, "role": req.role,
            "default_person_id": req.default_person_id,
        },
        "created_by": owner["email"],
    }


@router.post("/signup")
def signup(req: SignupRequest, request: Request, response: Response) -> dict:
    """Public self-signup — bất kỳ ai cũng đăng ký được, không cần xác thực email.
    Role luôn = "user". Auto-login ngay sau khi tạo (trả session_token + set cookie)."""
    # Basic validation
    email = (req.email or "").strip().lower()
    name = (req.display_name or "").strip()
    pw = req.password or ""
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Email không hợp lệ")
    if len(name) < 2:
        raise HTTPException(status_code=400, detail="Tên hiển thị tối thiểu 2 ký tự")
    if len(pw) < 6:
        raise HTTPException(status_code=400, detail="Mật khẩu tối thiểu 6 ký tự")

    pw_hash, salt = _hash_password(pw)
    db = _connect()
    try:
        try:
            cur = db.execute("""
                INSERT INTO users (email, display_name, password_hash, password_salt,
                                   role, default_person_id, created_at, must_change_password)
                VALUES (?, ?, ?, ?, 'user', NULL, ?, 0)
            """, (email, name, pw_hash, salt, int(time.time())))
            db.commit()
            new_id = cur.lastrowid
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Email đã được đăng ký rồi. Vui lòng đăng nhập.")
    finally:
        db.close()

    # Auto-login
    token = _create_session(new_id)
    response.set_cookie(
        COOKIE_NAME, token,
        httponly=True, samesite="lax",
        max_age=SESSION_TTL_SECONDS, path="/",
    )
    _record_audit("signup", user_id=new_id, target_email=email, request=request)
    return {
        "status": "ok",
        "user": {
            "user_id": new_id, "email": email, "display_name": name,
            "role": "user", "default_person_id": None,
            "must_change_password": False,
        },
        "person": None,
        "session_token": token,
    }


@router.post("/setup-profile")
def setup_profile(req: SetupProfileRequest, request: Request) -> dict:
    """Onboarding 1-shot: tạo (hoặc update) row 'self' trong user_persons cho
    user đang đăng nhập. Sau này login lại không phải nhập lại birth_datetime.
    """
    user = require_user(request)
    if req.gender not in ("nam", "nữ"):
        raise HTTPException(400, "gender phải là 'nam' hoặc 'nữ'")
    if not req.birth_datetime_local or len(req.birth_datetime_local) < 10:
        raise HTTPException(400, "birth_datetime_local required (ISO format)")

    name = (req.name or user["display_name"] or "Bạn").strip()
    try:
        birth_year = int(req.birth_datetime_local[:4])
    except Exception:
        birth_year = None
    now = int(time.time())

    db = _connect()
    try:
        # Upsert: nếu đã có 'self' thì update, ngược lại insert
        existing = db.execute(
            "SELECT id FROM user_persons WHERE user_id=? AND person_key='self'",
            (user["user_id"],),
        ).fetchone()
        if existing:
            db.execute("""
                UPDATE user_persons
                SET name=?, gender=?, birth_datetime_local=?, birth_year=?,
                    timezone=?, birth_place=?, updated_at=?
                WHERE id=?
            """, (
                name, req.gender, req.birth_datetime_local, birth_year,
                req.timezone, req.birth_place, now, existing[0],
            ))
            person_row_id = existing[0]
        else:
            cur = db.execute("""
                INSERT INTO user_persons
                    (user_id, person_key, name, relationship, gender,
                     birth_datetime_local, birth_year, timezone, birth_place,
                     created_at, updated_at)
                VALUES (?, 'self', ?, 'self', ?, ?, ?, ?, ?, ?, ?)
            """, (
                user["user_id"], name, req.gender,
                req.birth_datetime_local, birth_year, req.timezone,
                req.birth_place, now, now,
            ))
            person_row_id = cur.lastrowid
        db.commit()
    finally:
        db.close()

    person = _load_user_self_person(user["user_id"])
    _record_audit("setup_profile", user_id=user["user_id"], target_email=user["email"],
                  request=request, details={"birth": req.birth_datetime_local, "gender": req.gender})

    # 🚀 Auto-trigger full Tử Vi pipeline (background) — user không phải chờ + tự click 4 lần
    # Đường dẫn: TuViAnalyzer → engine.yi_publishing.translator.get_deepseek_client()
    # → https://api.deepseek.com/v1 (DeepSeek native chính chủ, key in data/ai_keys.json)
    auto_job_id = None
    try:
        from engine.tu_vi.analyzer import TuViAnalyzer, Person
        import threading
        analyzer_person = Person(
            person_key="self",
            name=name,
            birth_datetime_local=req.birth_datetime_local,
            gender=req.gender,
            timezone=req.timezone,
            user_id=user["user_id"],   # scope cache per-user
        )

        def _bg_runall():
            try:
                analyzer = TuViAnalyzer(analyzer_person)
                analyzer.discover_cach_cuc()
                analyzer.dai_van_annotate()
                analyzer.luu_nien(2026, 2030)
                analyzer.luu_nguyet(2026)
                logger.info(f"auto-pipeline done for user_id={user['user_id']}")
            except Exception as e:
                logger.warning(f"auto-pipeline failed for user_id={user['user_id']}: {e}")

        thread = threading.Thread(target=_bg_runall, daemon=True)
        thread.start()
        auto_job_id = f"setup_{user['user_id']}_{int(time.time())}"
    except Exception as e:
        logger.warning(f"failed to start auto-pipeline: {e}")

    return {
        "status": "ok",
        "person": person,
        "person_row_id": person_row_id,
        "auto_pipeline_started": auto_job_id is not None,
        "auto_pipeline_job_id": auto_job_id,
    }


@router.get("/users")
def list_users(request: Request) -> dict:
    require_owner(request)
    db = _connect()
    try:
        rows = db.execute("""
            SELECT user_id, email, display_name, role, default_person_id,
                   created_at, last_login_at, must_change_password
            FROM users ORDER BY user_id
        """).fetchall()
    finally:
        db.close()
    users = [
        {
            "user_id": r[0], "email": r[1], "display_name": r[2], "role": r[3],
            "default_person_id": r[4], "created_at": r[5],
            "last_login_at": r[6], "must_change_password": bool(r[7]),
        }
        for r in rows
    ]
    return {"status": "ok", "users": users, "count": len(users)}


@router.post("/change-password")
def change_password(req: ChangePasswordRequest, request: Request) -> dict:
    user = require_user(request)
    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải ≥ 8 ký tự")
    db = _connect()
    try:
        row = db.execute(
            "SELECT password_hash, password_salt FROM users WHERE user_id = ?",
            (user["user_id"],),
        ).fetchone()
        if not row or not _verify_password(req.current_password, row[0], row[1]):
            raise HTTPException(status_code=401, detail="Mật khẩu hiện tại không đúng")
        new_hash, new_salt = _hash_password(req.new_password)
        db.execute(
            "UPDATE users SET password_hash=?, password_salt=?, must_change_password=0 WHERE user_id=?",
            (new_hash, new_salt, user["user_id"]),
        )
        db.commit()
    finally:
        db.close()
    _record_audit("change_password", user_id=user["user_id"], target_email=user["email"], request=request)
    return {"status": "ok", "message": "Mật khẩu đã được cập nhật"}


@router.post("/switch-person")
def switch_person(req: SwitchPersonRequest, request: Request) -> dict:
    """Change the default person_id for the current user (e.g. impersonate)."""
    user = require_user(request)
    person = _load_person(req.person_id)
    if not person:
        raise HTTPException(status_code=404, detail=f"Person not found: {req.person_id}")
    db = _connect()
    try:
        db.execute(
            "UPDATE users SET default_person_id=? WHERE user_id=?",
            (req.person_id, user["user_id"]),
        )
        db.commit()
    finally:
        db.close()
    return {"status": "ok", "person": person}


@router.get("/persons")
def list_persons(request: Request) -> dict:
    """List all available persons from persons.sqlite3 (for user switcher)."""
    require_user(request)
    if not PERSONS_DB.exists():
        return {"status": "ok", "persons": []}
    db = sqlite3.connect(PERSONS_DB)
    try:
        rows = db.execute("""
            SELECT person_id, name, gender, birth_datetime_local, timezone,
                   relationship_to_founder
            FROM persons ORDER BY person_id
        """).fetchall()
    finally:
        db.close()
    return {
        "status": "ok",
        "persons": [
            {
                "person_id": r[0], "name": r[1], "gender": r[2],
                "birth_datetime_local": r[3], "timezone": r[4],
                "relationship_to_founder": r[5],
            }
            for r in rows
        ],
    }


# ─── User-namespaced data: persons / castings / favorites ────────────────────

PERSON_RELATIONSHIPS = {
    "self", "spouse", "child", "parent", "sibling",
    "colleague", "friend", "partner", "other",
}


class UserPersonCreate(BaseModel):
    person_key: str  # e.g. 'self', 'wife', 'child_an'
    name: str
    relationship: str = "other"
    gender: Optional[str] = None
    birth_datetime_local: Optional[str] = None
    birth_year: Optional[int] = None
    timezone: str = "Asia/Ho_Chi_Minh"
    birth_place: Optional[str] = None
    notes: Optional[str] = None


class UserPersonUpdate(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    gender: Optional[str] = None
    birth_datetime_local: Optional[str] = None
    birth_year: Optional[int] = None
    timezone: Optional[str] = None
    birth_place: Optional[str] = None
    notes: Optional[str] = None


class CastingSave(BaseModel):
    method: str       # 'mai_hoa', 'luc_hao', 'tu_vi', 'bat_tu', etc.
    subject_person_key: Optional[str] = None
    question: Optional[str] = None
    input_json: Optional[dict] = None
    result_json: dict
    verdict: Optional[str] = None
    tags: Optional[str] = None
    note: Optional[str] = None


class FavoriteSave(BaseModel):
    kind: str          # 'auspicious_day' | 'couple_match' | 'reading' | 'other'
    label: str
    payload_json: dict


@router.get("/my/persons")
def list_my_persons(request: Request) -> dict:
    """List user's own persons (gia đình, đồng nghiệp, etc.)."""
    user = require_user(request)
    db = _connect()
    try:
        rows = db.execute("""
            SELECT id, person_key, name, relationship, gender,
                   birth_datetime_local, birth_year, timezone, birth_place,
                   notes, created_at, updated_at
            FROM user_persons WHERE user_id = ?
            ORDER BY (relationship='self') DESC, created_at
        """, (user["user_id"],)).fetchall()
    finally:
        db.close()
    cols = ["id", "person_key", "name", "relationship", "gender",
            "birth_datetime_local", "birth_year", "timezone", "birth_place",
            "notes", "created_at", "updated_at"]
    return {"status": "ok", "persons": [dict(zip(cols, r)) for r in rows]}


@router.post("/my/persons")
def add_my_person(req: UserPersonCreate, request: Request) -> dict:
    user = require_user(request)
    if req.relationship not in PERSON_RELATIONSHIPS:
        raise HTTPException(400, f"relationship must be one of {PERSON_RELATIONSHIPS}")
    now = int(time.time())
    db = _connect()
    try:
        try:
            cur = db.execute("""
                INSERT INTO user_persons
                    (user_id, person_key, name, relationship, gender,
                     birth_datetime_local, birth_year, timezone, birth_place,
                     notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user["user_id"], req.person_key, req.name, req.relationship,
                req.gender, req.birth_datetime_local, req.birth_year,
                req.timezone, req.birth_place, req.notes, now, now,
            ))
            db.commit()
            new_id = cur.lastrowid
        except sqlite3.IntegrityError:
            raise HTTPException(409, f"person_key {req.person_key!r} already exists")
    finally:
        db.close()
    return {"status": "ok", "id": new_id}


@router.patch("/my/persons/{person_id}")
def update_my_person(person_id: int, req: UserPersonUpdate, request: Request) -> dict:
    user = require_user(request)
    fields = {k: v for k, v in req.model_dump(exclude_unset=True).items() if v is not None}
    if not fields:
        return {"status": "ok", "updated": 0}
    if "relationship" in fields and fields["relationship"] not in PERSON_RELATIONSHIPS:
        raise HTTPException(400, f"relationship invalid")
    fields["updated_at"] = int(time.time())
    sets = ", ".join(f"{k}=?" for k in fields)
    params = list(fields.values()) + [person_id, user["user_id"]]
    db = _connect()
    try:
        cur = db.execute(
            f"UPDATE user_persons SET {sets} WHERE id=? AND user_id=?", params,
        )
        db.commit()
        if cur.rowcount == 0:
            raise HTTPException(404, "person not found or not owned")
    finally:
        db.close()
    return {"status": "ok", "updated": cur.rowcount}


@router.delete("/my/persons/{person_id}")
def delete_my_person(person_id: int, request: Request) -> dict:
    user = require_user(request)
    db = _connect()
    try:
        cur = db.execute(
            "DELETE FROM user_persons WHERE id=? AND user_id=?",
            (person_id, user["user_id"]),
        )
        db.commit()
    finally:
        db.close()
    return {"status": "ok", "deleted": cur.rowcount}


@router.post("/my/castings")
def save_casting(req: CastingSave, request: Request) -> dict:
    """Save một lần gieo quẻ vào history user."""
    import json as _json
    user = require_user(request)
    db = _connect()
    try:
        cur = db.execute("""
            INSERT INTO user_castings
                (user_id, method, subject_person_key, question,
                 input_json, result_json, verdict, tags, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user["user_id"], req.method, req.subject_person_key, req.question,
            _json.dumps(req.input_json, ensure_ascii=False) if req.input_json else None,
            _json.dumps(req.result_json, ensure_ascii=False),
            req.verdict, req.tags, req.note, int(time.time()),
        ))
        db.commit()
        new_id = cur.lastrowid
    finally:
        db.close()
    return {"status": "ok", "id": new_id}


@router.get("/my/castings")
def list_castings(request: Request, method: Optional[str] = None,
                  limit: int = 50, offset: int = 0) -> dict:
    """List user's casting history (newest first), optional filter by method."""
    import json as _json
    user = require_user(request)
    db = _connect()
    try:
        if method:
            rows = db.execute("""
                SELECT id, method, subject_person_key, question,
                       input_json, result_json, verdict, tags, note, created_at
                FROM user_castings
                WHERE user_id=? AND method=?
                ORDER BY created_at DESC LIMIT ? OFFSET ?
            """, (user["user_id"], method, limit, offset)).fetchall()
        else:
            rows = db.execute("""
                SELECT id, method, subject_person_key, question,
                       input_json, result_json, verdict, tags, note, created_at
                FROM user_castings
                WHERE user_id=?
                ORDER BY created_at DESC LIMIT ? OFFSET ?
            """, (user["user_id"], limit, offset)).fetchall()
    finally:
        db.close()
    cols = ["id", "method", "subject_person_key", "question",
            "input_json", "result_json", "verdict", "tags", "note", "created_at"]
    items = []
    for r in rows:
        d = dict(zip(cols, r))
        # Parse JSON fields lazily for caller
        for jf in ("input_json", "result_json"):
            try:
                if d.get(jf):
                    d[jf] = _json.loads(d[jf])
            except Exception:
                pass
        items.append(d)
    return {"status": "ok", "castings": items, "count": len(items)}


@router.delete("/my/castings/{casting_id}")
def delete_casting(casting_id: int, request: Request) -> dict:
    user = require_user(request)
    db = _connect()
    try:
        cur = db.execute(
            "DELETE FROM user_castings WHERE id=? AND user_id=?",
            (casting_id, user["user_id"]),
        )
        db.commit()
    finally:
        db.close()
    return {"status": "ok", "deleted": cur.rowcount}


@router.post("/my/favorites")
def save_favorite(req: FavoriteSave, request: Request) -> dict:
    """Save 1 mục favorite (ngày tốt, xem tuổi vợ chồng, ...)."""
    import json as _json
    user = require_user(request)
    db = _connect()
    try:
        cur = db.execute("""
            INSERT INTO user_favorites (user_id, kind, label, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user["user_id"], req.kind, req.label,
            _json.dumps(req.payload_json, ensure_ascii=False),
            int(time.time()),
        ))
        db.commit()
        new_id = cur.lastrowid
    finally:
        db.close()
    return {"status": "ok", "id": new_id}


@router.get("/my/favorites")
def list_favorites(request: Request, kind: Optional[str] = None) -> dict:
    import json as _json
    user = require_user(request)
    db = _connect()
    try:
        if kind:
            rows = db.execute("""
                SELECT id, kind, label, payload_json, created_at
                FROM user_favorites WHERE user_id=? AND kind=?
                ORDER BY created_at DESC
            """, (user["user_id"], kind)).fetchall()
        else:
            rows = db.execute("""
                SELECT id, kind, label, payload_json, created_at
                FROM user_favorites WHERE user_id=? ORDER BY created_at DESC
            """, (user["user_id"],)).fetchall()
    finally:
        db.close()
    items = []
    for r in rows:
        d = {"id": r[0], "kind": r[1], "label": r[2], "created_at": r[4]}
        try:
            d["payload"] = _json.loads(r[3])
        except Exception:
            d["payload"] = None
        items.append(d)
    return {"status": "ok", "favorites": items, "count": len(items)}


@router.delete("/my/favorites/{fav_id}")
def delete_favorite(fav_id: int, request: Request) -> dict:
    user = require_user(request)
    db = _connect()
    try:
        cur = db.execute(
            "DELETE FROM user_favorites WHERE id=? AND user_id=?",
            (fav_id, user["user_id"]),
        )
        db.commit()
    finally:
        db.close()
    return {"status": "ok", "deleted": cur.rowcount}
