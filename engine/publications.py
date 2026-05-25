"""User publications — registry các bản đã sinh thành cho từng user.

Storage layout:
    data/user_publications/u{user_id}/{person_key}/{pub_type}/
        ├── data.json    ← raw LLM output
        ├── output.md    ← rendered markdown
        ├── output.docx  ← Word
        ├── output.pdf   ← PDF (optional, generated on-demand)
        └── meta.json    ← metadata
"""
from __future__ import annotations

import json
import secrets
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PUB_ROOT = PROJECT_ROOT / "data/user_publications"
AUTH_DB = PROJECT_ROOT / "data/yi_users/users.sqlite3"


# ─── Pub type catalog (single source of truth) ────────────────────────────────
PUB_TYPES = {
    "phe_menh_sau": {
        "title": "Phê mệnh sâu — Tử Vi (V4 Q4 enriched)",
        "engine_call": "TuViAnalyzer.phe_menh_sau",
        "approx_chars": 44000,
    },
    "cdk_12_cung": {
        "title": "Chiếu Đởm Kinh — 12 cung Việt thuần",
        "engine_call": "luan_toan_bo_cung",
        "approx_chars": 19000,
    },
    "cdk_dai_han": {
        "title": "Chiếu Đởm Kinh — Đại Hạn 8 vòng 80 năm",
        "engine_call": "luan_dai_han_8_vong",
        "approx_chars": 11400,
    },
    "cdk_luu_nien": {
        "title": "Chiếu Đởm Kinh — Lưu Niên 10 năm",
        "engine_call": "luan_luu_nien_10_nam",
        "approx_chars": 17000,
    },
    "cdk_tong_doan": {
        "title": "Chiếu Đởm Kinh — Tổng đoán cuộc đời",
        "engine_call": "tong_doan_ca_doi",
        "approx_chars": 7900,
    },
    "master": {
        "title": "MASTER — Bộ Tổng Đoán Mệnh Hoàn Chỉnh",
        "engine_call": "build_master",
        "approx_chars": 126000,
    },
}


def _db():
    return sqlite3.connect(AUTH_DB)


def pub_dir(user_id: int, person_key: str, pub_type: str) -> Path:
    """Get directory path for a publication."""
    safe_pk = "".join(c for c in person_key if c.isalnum() or c in "_-")
    return PUB_ROOT / f"u{user_id}" / safe_pk / pub_type


def register_publication(
    *,
    user_id: int,
    person_key: str,
    pub_type: str,
    files_relpath: dict,        # {"json": "data.json", "md": "output.md", "docx": "output.docx", "pdf": "output.pdf"}
    total_chars: int = 0,
    cost_usd: float = 0,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    version: Optional[str] = None,
    notes: Optional[str] = None,
) -> dict:
    """Register (or upsert) a publication."""
    if pub_type not in PUB_TYPES:
        return {"ok": False, "error": f"unknown pub_type: {pub_type}"}

    title = PUB_TYPES[pub_type]["title"]
    d = pub_dir(user_id, person_key, pub_type)
    file_dir_rel = str(d.relative_to(PROJECT_ROOT))
    formats_json = json.dumps(files_relpath, ensure_ascii=False)
    now = int(time.time())

    db = _db()
    try:
        existing = db.execute(
            "SELECT id FROM user_publications WHERE user_id=? AND person_key=? AND pub_type=?",
            (user_id, person_key, pub_type),
        ).fetchone()
        if existing:
            db.execute(
                """UPDATE user_publications SET
                   title=?, file_dir=?, formats=?, total_chars=?, cost_usd=?,
                   provider=?, model=?, version=?, generated_at=?, status='active', notes=?
                   WHERE id=?""",
                (title, file_dir_rel, formats_json, total_chars, cost_usd,
                 provider, model, version, now, notes, existing[0]),
            )
            pub_id = existing[0]
            action = "updated"
        else:
            cur = db.execute(
                """INSERT INTO user_publications
                   (user_id, person_key, pub_type, title, file_dir, formats,
                    total_chars, cost_usd, provider, model, version, generated_at, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, person_key, pub_type, title, file_dir_rel, formats_json,
                 total_chars, cost_usd, provider, model, version, now, notes),
            )
            pub_id = cur.lastrowid
            action = "created"
        db.commit()
        return {"ok": True, "id": pub_id, "action": action, "file_dir": file_dir_rel}
    finally:
        db.close()


def list_publications(user_id: int, *, person_key: Optional[str] = None) -> list[dict]:
    """List publications for a user (optionally filtered by person_key)."""
    db = _db()
    try:
        if person_key:
            rows = db.execute(
                """SELECT id, person_key, pub_type, title, file_dir, formats, total_chars,
                          cost_usd, provider, model, version, generated_at, status, notes
                   FROM user_publications
                   WHERE user_id = ? AND person_key = ? AND status = 'active'
                   ORDER BY generated_at DESC""",
                (user_id, person_key),
            ).fetchall()
        else:
            rows = db.execute(
                """SELECT id, person_key, pub_type, title, file_dir, formats, total_chars,
                          cost_usd, provider, model, version, generated_at, status, notes
                   FROM user_publications
                   WHERE user_id = ? AND status = 'active'
                   ORDER BY generated_at DESC""",
                (user_id,),
            ).fetchall()
        return [
            {
                "id": r[0], "person_key": r[1], "pub_type": r[2], "title": r[3],
                "file_dir": r[4], "formats": json.loads(r[5] or "{}"),
                "total_chars": r[6], "cost_usd": r[7],
                "provider": r[8], "model": r[9], "version": r[10],
                "generated_at": r[11], "status": r[12], "notes": r[13],
            }
            for r in rows
        ]
    finally:
        db.close()


def get_publication(pub_id: int) -> Optional[dict]:
    db = _db()
    try:
        row = db.execute(
            """SELECT id, user_id, person_key, pub_type, title, file_dir, formats,
                      total_chars, cost_usd, provider, model, version, generated_at, status, notes
               FROM user_publications WHERE id = ?""",
            (pub_id,),
        ).fetchone()
        if not row:
            return None
        return {
            "id": row[0], "user_id": row[1], "person_key": row[2], "pub_type": row[3],
            "title": row[4], "file_dir": row[5], "formats": json.loads(row[6] or "{}"),
            "total_chars": row[7], "cost_usd": row[8],
            "provider": row[9], "model": row[10], "version": row[11],
            "generated_at": row[12], "status": row[13], "notes": row[14],
        }
    finally:
        db.close()


def archive_publication(pub_id: int, user_id: int) -> dict:
    """Mark publication as archived (still in DB, files preserved)."""
    db = _db()
    try:
        row = db.execute("SELECT user_id FROM user_publications WHERE id=?", (pub_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "not_found"}
        if row[0] != user_id:
            return {"ok": False, "error": "permission_denied"}
        db.execute("UPDATE user_publications SET status='archived' WHERE id=?", (pub_id,))
        db.commit()
        return {"ok": True}
    finally:
        db.close()


def user_stats(user_id: int) -> dict:
    """Aggregate stats for user dashboard."""
    db = _db()
    try:
        row = db.execute(
            """SELECT COUNT(*), SUM(total_chars), SUM(cost_usd),
                      COUNT(DISTINCT person_key), MAX(generated_at)
               FROM user_publications WHERE user_id = ? AND status = 'active'""",
            (user_id,),
        ).fetchone()
        return {
            "publication_count": row[0] or 0,
            "total_chars": row[1] or 0,
            "total_cost_usd": round(row[2] or 0, 4),
            "person_count": row[3] or 0,
            "latest_at": row[4],
        }
    finally:
        db.close()


# ─── Share tokens ────────────────────────────────────────────────────────────

def create_share_token(
    pub_id: int,
    user_id: int,
    *,
    expires_at: Optional[int] = None,
    max_accesses: Optional[int] = None,
    note: Optional[str] = None,
) -> dict:
    """Generate random share token for a publication."""
    db = _db()
    try:
        # Verify owner
        row = db.execute("SELECT user_id FROM user_publications WHERE id=?", (pub_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "publication_not_found"}
        if row[0] != user_id:
            return {"ok": False, "error": "permission_denied"}
        token = secrets.token_urlsafe(24)
        now = int(time.time())
        db.execute(
            """INSERT INTO publication_shares
               (publication_id, token, created_by, created_at, expires_at, max_accesses, note)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (pub_id, token, user_id, now, expires_at, max_accesses, note),
        )
        db.commit()
        return {"ok": True, "token": token, "share_url": f"/share/{token}"}
    finally:
        db.close()


def resolve_share_token(token: str) -> Optional[dict]:
    """Resolve a share token to publication. Returns None if invalid/expired/over-quota."""
    db = _db()
    try:
        row = db.execute(
            """SELECT s.id, s.publication_id, s.expires_at, s.access_count, s.max_accesses,
                      p.user_id, p.person_key, p.pub_type, p.title, p.file_dir, p.formats
               FROM publication_shares s
               JOIN user_publications p ON p.id = s.publication_id
               WHERE s.token = ? AND p.status = 'active'""",
            (token,),
        ).fetchone()
        if not row:
            return None
        share_id, pub_id, expires_at, access_count, max_accesses = row[0], row[1], row[2], row[3], row[4]
        now = int(time.time())
        if expires_at and now > expires_at:
            return {"_expired": True}
        if max_accesses is not None and access_count >= max_accesses:
            return {"_quota_exceeded": True}
        # Increment counter
        db.execute("UPDATE publication_shares SET access_count = access_count + 1 WHERE id = ?", (share_id,))
        db.commit()
        return {
            "publication_id": pub_id,
            "user_id": row[5], "person_key": row[6], "pub_type": row[7],
            "title": row[8], "file_dir": row[9], "formats": json.loads(row[10] or "{}"),
            "share_id": share_id, "access_count": access_count + 1,
        }
    finally:
        db.close()


def list_user_shares(user_id: int) -> list[dict]:
    db = _db()
    try:
        rows = db.execute(
            """SELECT s.id, s.publication_id, s.token, s.created_at, s.expires_at,
                      s.access_count, s.max_accesses, s.note, p.title, p.pub_type, p.person_key
               FROM publication_shares s
               JOIN user_publications p ON p.id = s.publication_id
               WHERE s.created_by = ?
               ORDER BY s.created_at DESC""",
            (user_id,),
        ).fetchall()
        return [
            {
                "id": r[0], "publication_id": r[1], "token": r[2],
                "created_at": r[3], "expires_at": r[4],
                "access_count": r[5], "max_accesses": r[6], "note": r[7],
                "pub_title": r[8], "pub_type": r[9], "person_key": r[10],
                "share_url": f"/share/{r[2]}",
            }
            for r in rows
        ]
    finally:
        db.close()


def revoke_share(share_id: int, user_id: int) -> dict:
    db = _db()
    try:
        row = db.execute("SELECT created_by FROM publication_shares WHERE id=?", (share_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "not_found"}
        if row[0] != user_id:
            return {"ok": False, "error": "permission_denied"}
        db.execute("DELETE FROM publication_shares WHERE id=?", (share_id,))
        db.commit()
        return {"ok": True}
    finally:
        db.close()


# ─── File helpers ────────────────────────────────────────────────────────────

def save_artifacts(
    user_id: int,
    person_key: str,
    pub_type: str,
    *,
    data_json: Optional[dict] = None,
    markdown: Optional[str] = None,
    docx_source_md: Optional[Path] = None,
) -> dict:
    """Save artifacts to publication directory and return files_relpath dict."""
    d = pub_dir(user_id, person_key, pub_type)
    d.mkdir(parents=True, exist_ok=True)
    out = {}
    if data_json is not None:
        p = d / "data.json"
        p.write_text(json.dumps(data_json, ensure_ascii=False, indent=2), encoding="utf-8")
        out["json"] = "data.json"
    if markdown is not None:
        p = d / "output.md"
        p.write_text(markdown, encoding="utf-8")
        out["md"] = "output.md"
    # Try DOCX via pandoc
    md_for_docx = d / "output.md" if markdown else docx_source_md
    if md_for_docx and md_for_docx.exists():
        docx_p = d / "output.docx"
        result = subprocess.run(
            ["pandoc", str(md_for_docx), "-o", str(docx_p),
             "--from", "markdown+pipe_tables+blank_before_blockquote",
             "--to", "docx", "--standalone"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            out["docx"] = "output.docx"
    return out
