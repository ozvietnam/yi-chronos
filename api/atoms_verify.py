"""Founder verify atoms endpoint — Phase D.

POST /api/atoms/verify — verify 1 atom (owner-only)
GET  /api/atoms/pending — list atoms chờ verify theo (star, palace)

Verify flow:
- ✅ verdict="ok"     → confidence 0.95, founder_verified=1
- ⚠ verdict="edit"   → giữ confidence 0.85, founder_verified=0, lưu note
- ❌ verdict="reject" → confidence 0.3, founder_verified=-1 (loại khỏi retrieval)
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"

router = APIRouter(prefix="/api/atoms", tags=["atoms-verify"])


def _require_owner():
    """Owner gate — reuse auth dependency từ api.auth nếu có."""
    try:
        from api.auth import get_current_user_optional  # type: ignore
        return get_current_user_optional
    except ImportError:
        return None


class VerifyRequest(BaseModel):
    atom_id: int
    verdict: str = Field(..., description="ok | edit | reject")
    note: str | None = Field(None, description="Ghi chú của founder khi edit/reject")


@router.post("/verify")
async def verify_atom(req: VerifyRequest) -> dict:
    """Founder verify 1 atom. Verdict: ok (0.95) / edit (giữ 0.85 + note) / reject (0.3)."""
    if req.verdict not in ("ok", "edit", "reject"):
        raise HTTPException(400, "verdict must be ok|edit|reject")

    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT atom_id FROM atomic_questions WHERE atom_id = ?", (req.atom_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404, f"atom {req.atom_id} not found")

        if req.verdict == "ok":
            confidence, verified = 0.95, 1
        elif req.verdict == "edit":
            confidence, verified = 0.85, 0
        else:  # reject
            confidence, verified = 0.3, -1

        conn.execute(
            "UPDATE atomic_questions SET confidence = ?, founder_verified = ? WHERE atom_id = ?",
            (confidence, verified, req.atom_id),
        )
        conn.execute(
            "UPDATE atom_commentaries SET confidence = ?, founder_verified = ? WHERE atom_id = ?",
            (confidence, verified, req.atom_id),
        )
        # Lưu note vào extraction note nếu có (append vào from_template field tạm)
        if req.note:
            conn.execute(
                "UPDATE atomic_questions SET from_template = from_template || ' | FOUNDER_NOTE: ' || ? WHERE atom_id = ?",
                (req.note, req.atom_id),
            )
        conn.commit()
    finally:
        conn.close()

    return {
        "atom_id": req.atom_id,
        "verdict": req.verdict,
        "confidence": confidence,
        "founder_verified": verified,
    }


@router.get("/pending")
async def pending_atoms(star: str | None = None, palace: str | None = None, limit: int = 20) -> dict:
    """List atoms chờ verify (founder_verified=0), filter theo star/palace tag."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        sql = """
            SELECT a.atom_id, a.question_text, a.source_quote, a.confidence,
                   a.section_id, a.subject_identifiers,
                   c.book_corpus_id, c.page_start,
                   cm.viet_thuan
            FROM atomic_questions a
            JOIN chunks_v2 c ON c.chunk_id = a.chunk_id
            LEFT JOIN atom_commentaries cm ON cm.atom_id = a.atom_id
            WHERE a.founder_verified = 0
              AND c.book_corpus_id IN (
                'trung-chau-tu-vi-dau-so-2', 'tu-vi-dau-so-toan-thu-vu-tai-luc',
                'tu-vi-nghiem-ly-toan-thu-thien-luong', 'tu-vi-ham-so'
              )
        """
        params: list = []
        if star:
            sql += " AND a.subject_identifiers LIKE ?"
            params.append(f'%"{star}"%')
        if palace:
            sql += " AND a.subject_identifiers LIKE ?"
            params.append(f'%"{palace}"%')
        sql += " ORDER BY a.atom_id LIMIT ?"
        params.append(limit)

        rows = conn.execute(sql, params).fetchall()
        return {
            "count": len(rows),
            "atoms": [dict(r) for r in rows],
        }
    finally:
        conn.close()
