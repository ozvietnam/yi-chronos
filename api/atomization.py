"""API endpoints cho atomization — PIKE-RAG inspired.

Endpoints:
- POST /api/atomization/decompose — Algorithm 1 wrap engine v3/v4
- GET  /api/atomization/atom/search — FTS5 search atomic_questions
- GET  /api/atomization/atom/{atom_id} — fetch full atom + chunk
- GET  /api/atomization/stats — DB stats (chunks, atoms, classifications)
- POST /api/atomization/verify/{atom_id} — founder verify atom (1=correct, -1=wrong)
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"

router = APIRouter(prefix="/api/atomization", tags=["atomization"])


# ─── Schemas ─────────────────────────────────────────────────────
class DecomposeRequest(BaseModel):
    query: str
    la_so: dict[str, Any] | None = None
    school: str | None = None
    max_iter: int = Field(default=5, ge=1, le=10)


class DecomposeResponse(BaseModel):
    query: str
    answer: str | None
    rationale: str | None
    citations: list[dict]
    n_atoms_chosen: int
    trajectory: list[dict]
    duration_sec: float
    total_tokens: int
    error: str | None = None


class AtomSummary(BaseModel):
    atom_id: int
    question: str
    source_book: str
    page_start: int
    page_end: int
    from_category: str | None
    subject_identifiers: dict
    confidence: float
    founder_verified: int


class StatsResponse(BaseModel):
    n_chunks: int
    n_classifications: int
    n_atomic_questions: int
    n_extraction_runs: int
    by_book: dict[str, int]
    by_archetype: dict[str, int]
    by_format: dict[str, int]
    founder_verified_count: int
    founder_rejected_count: int


# ─── Helpers ─────────────────────────────────────────────────────
def _open_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ─── Endpoints ───────────────────────────────────────────────────
@router.post("/decompose", response_model=DecomposeResponse)
def decompose(req: DecomposeRequest) -> DecomposeResponse:
    """Algorithm 1 — wrap engine v3/v4 via retriever + LLM orchestration."""
    # Lazy import to avoid startup overhead
    from engine.atomization.decomposer import KnowledgeAwareDecomposer

    decomposer = KnowledgeAwareDecomposer(max_iter=req.max_iter)
    result = decomposer.decompose(
        user_query=req.query, la_so=req.la_so, school=req.school,
    )
    return DecomposeResponse(
        query=result.user_query,
        answer=result.answer,
        rationale=result.rationale,
        citations=result.citations,
        n_atoms_chosen=len(result.chosen_atoms),
        trajectory=result.trajectory,
        duration_sec=result.duration_sec,
        total_tokens=result.total_tokens,
        error=result.error,
    )


@router.get("/atom/search", response_model=list[AtomSummary])
def atom_search(
    q: str = Query(..., description="search query"),
    limit: int = Query(default=20, ge=1, le=100),
    school: str | None = Query(default=None, description="filter by book/school"),
) -> list[AtomSummary]:
    """FTS5 search atomic_questions."""
    from engine.atomization.retriever import ChunkAtomRetriever

    retriever = ChunkAtomRetriever()
    hits = retriever.search_atom_fts(q, limit=limit, school=school)
    return [
        AtomSummary(
            atom_id=h.atom_id,
            question=h.atom_question,
            source_book=h.source_book,
            page_start=h.page_start,
            page_end=h.page_end,
            from_category=h.from_category,
            subject_identifiers=h.subject_identifiers,
            confidence=h.confidence,
            founder_verified=h.founder_verified,
        )
        for h in hits
    ]


@router.get("/atom/{atom_id}")
def atom_detail(atom_id: int) -> dict:
    """Fetch full atom + linked chunk + classification."""
    conn = _open_db()
    try:
        row = conn.execute(
            """SELECT aq.*, c.text as chunk_text, c.book_corpus_id, c.page_start, c.page_end,
                      cc.is_chu_the, cc.is_cong_thuc, cc.is_luan_giai, cc.is_to_hop, cc.is_kinh_nghiem,
                      cc.format_style, cc.knowledge_categories_json
               FROM atomic_questions aq
               JOIN chunks_v2 c ON c.chunk_id = aq.chunk_id
               LEFT JOIN chunk_classifications cc ON cc.cc_id = aq.cc_id
               WHERE aq.atom_id = ?""",
            (atom_id,),
        ).fetchone()
        if not row:
            raise HTTPException(404, f"Atom {atom_id} not found")
        d = dict(row)
        # Parse JSON fields
        for k in ("subject_identifiers", "knowledge_categories_json"):
            if d.get(k):
                try:
                    d[k] = json.loads(d[k])
                except json.JSONDecodeError:
                    pass
        return d
    finally:
        conn.close()


@router.get("/stats", response_model=StatsResponse)
def stats() -> StatsResponse:
    """DB stats for atomization tables."""
    conn = _open_db()
    try:
        n_chunks = conn.execute("SELECT COUNT(*) FROM chunks_v2").fetchone()[0]
        n_cc = conn.execute("SELECT COUNT(*) FROM chunk_classifications").fetchone()[0]
        n_atoms = conn.execute("SELECT COUNT(*) FROM atomic_questions").fetchone()[0]
        n_runs = conn.execute("SELECT COUNT(*) FROM extraction_runs").fetchone()[0]

        by_book = dict(conn.execute(
            "SELECT book_corpus_id, COUNT(*) FROM chunks_v2 GROUP BY book_corpus_id"
        ).fetchall())
        by_archetype = {
            "chu_the": conn.execute("SELECT COUNT(*) FROM chunk_classifications WHERE is_chu_the=1").fetchone()[0],
            "cong_thuc": conn.execute("SELECT COUNT(*) FROM chunk_classifications WHERE is_cong_thuc=1").fetchone()[0],
            "luan_giai": conn.execute("SELECT COUNT(*) FROM chunk_classifications WHERE is_luan_giai=1").fetchone()[0],
            "to_hop": conn.execute("SELECT COUNT(*) FROM chunk_classifications WHERE is_to_hop=1").fetchone()[0],
            "kinh_nghiem": conn.execute("SELECT COUNT(*) FROM chunk_classifications WHERE is_kinh_nghiem=1").fetchone()[0],
        }
        by_format = dict(conn.execute(
            "SELECT COALESCE(format_style, '(unknown)'), COUNT(*) FROM chunk_classifications GROUP BY format_style"
        ).fetchall())
        n_verified = conn.execute("SELECT COUNT(*) FROM atomic_questions WHERE founder_verified=1").fetchone()[0]
        n_rejected = conn.execute("SELECT COUNT(*) FROM atomic_questions WHERE founder_verified=-1").fetchone()[0]

        return StatsResponse(
            n_chunks=n_chunks,
            n_classifications=n_cc,
            n_atomic_questions=n_atoms,
            n_extraction_runs=n_runs,
            by_book=by_book,
            by_archetype=by_archetype,
            by_format=by_format,
            founder_verified_count=n_verified,
            founder_rejected_count=n_rejected,
        )
    finally:
        conn.close()


@router.post("/verify/{atom_id}")
def verify_atom(atom_id: int, verdict: int = Query(..., ge=-1, le=1)) -> dict:
    """Founder verify atom. verdict: 1=correct, -1=wrong, 0=reset."""
    conn = _open_db()
    try:
        cur = conn.execute(
            "UPDATE atomic_questions SET founder_verified=?, confidence=? WHERE atom_id=?",
            (verdict, 0.98 if verdict == 1 else (0.0 if verdict == -1 else 0.85), atom_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(404, f"Atom {atom_id} not found")
        conn.commit()
        return {"atom_id": atom_id, "verdict": verdict, "updated": True}
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════
# WORKBENCH endpoints — section-aware research project
# Theo nguyên tắc anh đặt 2026-06-09: từng section, không nhảy
# ═══════════════════════════════════════════════════════════════════

class SectionSummary(BaseModel):
    id: str
    title: str
    page_start: int
    page_end: int
    n_pages: int
    stars: list[str] = []
    palaces: list[str] = []
    # Progress
    n_chunks: int = 0
    n_classifications: int = 0
    n_atoms: int = 0
    n_commentaries: int = 0
    n_verified: int = 0
    n_rejected: int = 0
    status: str = "todo"  # 'todo' | 'in_progress' | 'done' | 'verified'


def _parse_manifest(book: str) -> list[dict]:
    """Inline parser cho manifest.yaml."""
    import re
    path = PROJECT_ROOT / "data" / "restored_books" / book / "manifest.yaml"
    if not path.exists():
        return []
    RE_ID = re.compile(r'^\s*-\s*id:\s*"([^"]+)"\s*$')
    RE_FIELD = re.compile(r'^\s*(\w+):\s*(.*)$')

    sections = []
    current: dict = {}
    in_sec = False
    for line in path.read_text(encoding="utf-8").split("\n"):
        if line.strip() == "sections:":
            in_sec = True
            continue
        if not in_sec:
            continue
        m_id = RE_ID.match(line)
        if m_id:
            if current:
                sections.append(current)
            current = {"id": m_id.group(1)}
            continue
        if not current:
            continue
        m = RE_FIELD.match(line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if key == "id":
                continue
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            elif val.startswith("[") and val.endswith("]"):
                val = re.findall(r'"([^"]*)"', val)
            elif val.isdigit():
                val = int(val)
            current[key] = val
    if current:
        sections.append(current)
    return sections


@router.get("/books")
def list_books() -> list[dict]:
    """List restored_books có manifest.yaml."""
    base = PROJECT_ROOT / "data" / "restored_books"
    out = []
    for book_dir in base.iterdir():
        if not book_dir.is_dir():
            continue
        manifest = book_dir / "manifest.yaml"
        if not manifest.exists():
            continue
        sections = _parse_manifest(book_dir.name)
        # Count atoms
        conn = _open_db()
        try:
            n_atoms = conn.execute(
                "SELECT COUNT(*) FROM atomic_questions aq "
                "JOIN chunks_v2 c ON c.chunk_id=aq.chunk_id "
                "WHERE c.book_corpus_id=?", (book_dir.name,)
            ).fetchone()[0]
            n_chunks = conn.execute(
                "SELECT COUNT(*) FROM chunks_v2 WHERE book_corpus_id=?", (book_dir.name,)
            ).fetchone()[0]
        finally:
            conn.close()
        out.append({
            "book": book_dir.name,
            "n_sections": len(sections),
            "n_chunks": n_chunks,
            "n_atoms": n_atoms,
        })
    return out


@router.get("/books/{book}/sections", response_model=list[SectionSummary])
def list_sections(book: str) -> list[SectionSummary]:
    """List all sections of book + progress stats."""
    sections = _parse_manifest(book)
    if not sections:
        raise HTTPException(404, f"Book {book} not found or no manifest")

    conn = _open_db()
    try:
        out = []
        for s in sections:
            sid = s["id"]
            # Count via section_id tag
            n_chunks = conn.execute(
                "SELECT COUNT(*) FROM chunks_v2 WHERE book_corpus_id=? AND section_id=?",
                (book, sid),
            ).fetchone()[0]
            n_cls = conn.execute(
                "SELECT COUNT(*) FROM chunk_classifications cc "
                "JOIN chunks_v2 c ON c.chunk_id=cc.chunk_id "
                "WHERE c.book_corpus_id=? AND c.section_id=?",
                (book, sid),
            ).fetchone()[0]
            n_atoms = conn.execute(
                "SELECT COUNT(*) FROM atomic_questions WHERE section_id=?",
                (sid,),
            ).fetchone()[0]
            n_commentaries = conn.execute(
                "SELECT COUNT(*) FROM atom_commentaries ac "
                "JOIN atomic_questions aq ON aq.atom_id=ac.atom_id "
                "WHERE aq.section_id=?",
                (sid,),
            ).fetchone()[0]
            n_verified = conn.execute(
                "SELECT COUNT(*) FROM atomic_questions WHERE section_id=? AND founder_verified=1",
                (sid,),
            ).fetchone()[0]
            n_rejected = conn.execute(
                "SELECT COUNT(*) FROM atomic_questions WHERE section_id=? AND founder_verified=-1",
                (sid,),
            ).fetchone()[0]

            # Determine status
            if n_chunks == 0:
                status = "todo"
            elif n_cls < n_chunks:
                status = "in_progress"
            elif n_verified > 0 and n_verified + n_rejected >= n_atoms * 0.8:
                status = "verified"
            else:
                status = "done"

            out.append(SectionSummary(
                id=sid,
                title=s.get("title", ""),
                page_start=int(s.get("page_start", 0)),
                page_end=int(s.get("page_end", 0)),
                n_pages=int(s.get("n_pages", 0)),
                stars=s.get("stars", []) if isinstance(s.get("stars"), list) else [],
                palaces=s.get("palaces", []) if isinstance(s.get("palaces"), list) else [],
                n_chunks=n_chunks,
                n_classifications=n_cls,
                n_atoms=n_atoms,
                n_commentaries=n_commentaries,
                n_verified=n_verified,
                n_rejected=n_rejected,
                status=status,
            ))
        return out
    finally:
        conn.close()


@router.get("/books/{book}/sections/{section_id}/atoms")
def section_atoms(book: str, section_id: str, include_chunk: bool = False) -> list[dict]:
    """All atoms in section with details for review."""
    conn = _open_db()
    try:
        rows = conn.execute("""
            SELECT aq.atom_id, aq.question_text, aq.from_category, aq.from_template,
                   aq.subject_identifiers, aq.source_quote,
                   aq.confidence, aq.founder_verified,
                   c.page_start, c.text as chunk_text, c.chunk_id,
                   cc.format_style, cc.is_chu_the, cc.is_cong_thuc,
                   cc.is_luan_giai, cc.is_to_hop, cc.is_kinh_nghiem,
                   ac.viet_thuan, ac.vi_du_doi_song, ac.iron_rule_warning
            FROM atomic_questions aq
            JOIN chunks_v2 c ON c.chunk_id = aq.chunk_id
            LEFT JOIN chunk_classifications cc ON cc.cc_id = aq.cc_id
            LEFT JOIN atom_commentaries ac ON ac.atom_id = aq.atom_id
            WHERE aq.section_id = ? AND c.book_corpus_id = ?
            ORDER BY c.page_start, aq.atom_id
        """, (section_id, book)).fetchall()

        out = []
        for r in rows:
            d = dict(r)
            try:
                d["subject_identifiers"] = json.loads(d["subject_identifiers"] or "{}")
            except json.JSONDecodeError:
                pass
            if not include_chunk:
                # truncate for list view
                d["chunk_text"] = (d["chunk_text"] or "")[:300] + "..." if len(d["chunk_text"] or "") > 300 else d["chunk_text"]
            out.append(d)
        return out
    finally:
        conn.close()


@router.post("/verify-bulk")
def verify_bulk(atom_ids: list[int], verdict: int = Query(..., ge=-1, le=1)) -> dict:
    """Bulk verify. atom_ids: list. verdict: 1=correct, -1=wrong, 0=reset."""
    conn = _open_db()
    try:
        conf = 0.98 if verdict == 1 else (0.0 if verdict == -1 else 0.85)
        placeholders = ",".join("?" * len(atom_ids))
        cur = conn.execute(
            f"UPDATE atomic_questions SET founder_verified=?, confidence=? WHERE atom_id IN ({placeholders})",
            [verdict, conf] + list(atom_ids),
        )
        conn.commit()
        return {"updated": cur.rowcount, "verdict": verdict}
    finally:
        conn.close()


@router.get("/quota")
def quota_status() -> dict:
    """Check LLM provider quota status (from recent extraction_runs)."""
    conn = _open_db()
    try:
        # Recent token usage by provider
        rows = conn.execute("""
            SELECT llm_provider, llm_model,
                   SUM(prompt_tokens) as prompt_tok,
                   SUM(completion_tokens) as completion_tok,
                   COUNT(*) as n_calls,
                   MAX(started_at) as last_call
            FROM extraction_runs
            WHERE started_at > strftime('%s','now') - 18000  -- 5h window
            GROUP BY llm_provider, llm_model
        """).fetchall()
        # Recent fails
        n_fail_429 = conn.execute("""
            SELECT COUNT(*) FROM extraction_runs
            WHERE status='failed' AND error_message LIKE '%429%'
              AND started_at > strftime('%s','now') - 3600
        """).fetchone()[0]
        return {
            "providers_5h_window": [dict(r) for r in rows],
            "recent_429_fails_1h": n_fail_429,
        }
    finally:
        conn.close()
