#!/usr/bin/env python3
"""Ingest atoms từ JSON drafts (sub-agent output) vào DB.

Pattern: data/atomize_v2_drafts/cung-menh/5.1.X-*.json
Format JSON:
{
  "section_id": "5.1.6",
  "section_title": "...",
  "pages": [521, 522, ...],
  "atoms": [
    {
      "question_id": "tcq2-5.1.6-Q01",
      "question": "...",
      "answer_atom": "...",
      "source_quote": "...",
      "source_page": 521,
      "section_id": "5.1.6",
      "tags": [...],
      "commentary": {...},
      "confidence": 0.85,
      "extracted_by": "sub-agent-bam-sach"
    }
  ]
}

Usage:
  python3 scripts/ingest_atomize_v2.py data/atomize_v2_drafts/cung-menh/
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
BOOK_CORPUS = "trung-chau-tu-vi-dau-so-2"


def find_or_create_chunk(conn: sqlite3.Connection, page: int, section_id: str) -> int:
    """Tìm chunk_id của page X — nếu chưa có, tạo placeholder chunk page-as-chunk."""
    cur = conn.execute(
        """
        SELECT chunk_id FROM chunks_v2
        WHERE book_corpus_id = ? AND page_start <= ? AND page_end >= ?
        ORDER BY chunk_id ASC LIMIT 1
        """,
        (BOOK_CORPUS, page, page),
    )
    row = cur.fetchone()
    if row:
        return int(row[0])

    # Create page-as-chunk
    md_path = PROJECT_ROOT / "data" / "restored_books" / BOOK_CORPUS / "pages" / f"p{page:04d}.md"
    text = md_path.read_text(encoding="utf-8") if md_path.exists() else f"<!-- page {page} -->"
    cur = conn.execute(
        """
        INSERT INTO chunks_v2
            (book_corpus_id, page_start, page_end, section_path, section_id, text, is_canonical)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        """,
        (BOOK_CORPUS, page, page, f"§{section_id}", section_id, text),
    )
    return int(cur.lastrowid)


def ingest_atom(conn: sqlite3.Connection, atom: dict, section_id: str) -> int | None:
    """Insert 1 atom + commentary. Return atom_id or None if skipped."""
    page = int(atom.get("source_page") or 0)
    if not page:
        print(f"  ⚠ skip atom no page: {atom.get('question_id')}")
        return None

    # Duplicate check: same section + same source_quote first 100 chars
    quote = (atom.get("source_quote") or "").strip()
    cur = conn.execute(
        """
        SELECT atom_id FROM atomic_questions
        WHERE section_id = ?
          AND source_quote = ?
        LIMIT 1
        """,
        (section_id, quote),
    )
    existing = cur.fetchone()
    if existing:
        print(f"  ↩ dup, skip: {atom.get('question_id')} (existing atom_id={existing[0]})")
        return None

    chunk_id = find_or_create_chunk(conn, page, section_id)

    # Build subject_identifiers from tags
    tags = atom.get("tags") or []
    subj = {}
    for tag in tags:
        if ":" in tag:
            k, v = tag.split(":", 1)
            subj.setdefault(k, []).append(v)
    subj_json = json.dumps(subj, ensure_ascii=False)

    cur = conn.execute(
        """
        INSERT INTO atomic_questions
            (chunk_id, question_text, question_lang, from_category, from_template,
             subject_identifiers, source_quote, confidence, founder_verified,
             extracted_by, section_id)
        VALUES (?, ?, 'vi', ?, ?, ?, ?, ?, 0, ?, ?)
        """,
        (
            chunk_id,
            atom.get("question") or "",
            "tuvi_sao_cung",
            atom.get("question_id") or "",
            subj_json,
            quote,
            float(atom.get("confidence") or 0.85),
            atom.get("extracted_by") or "sub-agent-bam-sach",
            section_id,
        ),
    )
    atom_id = int(cur.lastrowid)

    # Insert commentary
    com = atom.get("commentary") or {}
    conn.execute(
        """
        INSERT INTO atom_commentaries
            (atom_id, han_viet_explain, viet_thuan, nguyen_ly, vi_du_doi_song,
             iron_rule_warning, extracted_by, confidence, founder_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (
            atom_id,
            com.get("han_viet_explain"),
            com.get("viet_thuan") or atom.get("answer_atom"),
            com.get("nguyen_ly"),
            com.get("vi_du_doi_song"),
            com.get("iron_rule_warning"),
            atom.get("extracted_by") or "sub-agent-bam-sach",
            float(atom.get("confidence") or 0.85),
        ),
    )

    return atom_id


def ingest_file(conn: sqlite3.Connection, json_path: Path) -> tuple[int, int]:
    """Return (inserted, skipped)."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    section_id = data.get("section_id") or ""
    atoms = data.get("atoms") or []
    print(f"\n📥 {json_path.name} — section {section_id} — {len(atoms)} atoms")

    inserted = skipped = 0
    for atom in atoms:
        aid = ingest_atom(conn, atom, atom.get("section_id") or section_id)
        if aid:
            inserted += 1
        else:
            skipped += 1
    return inserted, skipped


def main():
    if len(sys.argv) < 2:
        print("Usage: ingest_atomize_v2.py <drafts_dir_or_file>")
        sys.exit(1)

    target = Path(sys.argv[1])
    if target.is_dir():
        files = sorted(target.glob("*.json"))
    else:
        files = [target]

    if not files:
        print(f"⚠ no JSON files in {target}")
        sys.exit(0)

    conn = sqlite3.connect(DB_PATH)
    total_in = total_skip = 0
    try:
        for f in files:
            try:
                ins, sk = ingest_file(conn, f)
                total_in += ins
                total_skip += sk
                conn.commit()
                print(f"  ✅ inserted={ins}  skipped={sk}")
            except Exception as e:
                conn.rollback()
                print(f"  ❌ {f.name}: {e}")
    finally:
        # FTS rebuild
        try:
            conn.execute("INSERT INTO atomic_questions_fts(atomic_questions_fts) VALUES('rebuild')")
            conn.execute("INSERT INTO atom_commentaries_fts(atom_commentaries_fts) VALUES('rebuild')")
            conn.commit()
            print("\n🔁 FTS rebuilt")
        except Exception as e:
            print(f"\n⚠ FTS rebuild failed: {e}")
        conn.close()

    print(f"\n🎯 TỔNG: inserted={total_in}  skipped={total_skip}")


if __name__ == "__main__":
    main()
