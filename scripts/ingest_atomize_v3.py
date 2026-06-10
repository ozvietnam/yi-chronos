#!/usr/bin/env python3
"""Ingest atoms v3 — generic theo book_corpus_id từ JSON file.

JSON format:
{
  "book_corpus_id": "tu-vi-dau-so-toan-thu-vu-tai-luc",
  "section_id": "tdts.S1",
  "section_title": "...",
  "pages": [1, 2, ..., 20],
  "atoms": [
    {
      "question_id": "tdts.S1.Q01",
      "question": "...",
      "answer_atom": "...",
      "source_quote": "...",
      "source_page": 5,
      "section_id": "tdts.S1",
      "tags": [...],
      "commentary": {...},
      "confidence": 0.85,
      "extracted_by": "sub-agent-bam-sach"
    }
  ]
}

Usage:
  python3 scripts/ingest_atomize_v3.py data/atomize_v2_drafts/toan-thu-tran-doan/
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"


def find_or_create_chunk(conn: sqlite3.Connection, book_corpus: str, page: int, section_id: str) -> int:
    cur = conn.execute(
        """
        SELECT chunk_id FROM chunks_v2
        WHERE book_corpus_id = ? AND page_start <= ? AND page_end >= ?
        ORDER BY chunk_id ASC LIMIT 1
        """,
        (book_corpus, page, page),
    )
    row = cur.fetchone()
    if row:
        return int(row[0])

    md_path = PROJECT_ROOT / "data" / "restored_books" / book_corpus / "pages" / f"p{page:04d}.md"
    text = md_path.read_text(encoding="utf-8") if md_path.exists() else f"<!-- page {page} -->"
    cur = conn.execute(
        """
        INSERT INTO chunks_v2
            (book_corpus_id, page_start, page_end, section_path, section_id, text, is_canonical)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        """,
        (book_corpus, page, page, f"§{section_id}", section_id, text),
    )
    return int(cur.lastrowid)


def ingest_atom(conn: sqlite3.Connection, atom: dict, section_id: str, book_corpus: str) -> int | None:
    page = int(atom.get("source_page") or 0)
    if not page:
        return None

    quote = (atom.get("source_quote") or "").strip()
    cur = conn.execute(
        """
        SELECT a.atom_id FROM atomic_questions a
        JOIN chunks_v2 c ON c.chunk_id = a.chunk_id
        WHERE c.book_corpus_id = ?
          AND a.section_id = ?
          AND a.source_quote = ?
        LIMIT 1
        """,
        (book_corpus, section_id, quote),
    )
    existing = cur.fetchone()
    if existing:
        return None

    chunk_id = find_or_create_chunk(conn, book_corpus, page, section_id)

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


def ingest_file(conn: sqlite3.Connection, json_path: Path) -> tuple[int, int, str]:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    book_corpus = data.get("book_corpus_id")
    if not book_corpus:
        return 0, 0, "no book_corpus_id"
    section_id = data.get("section_id") or ""
    atoms = data.get("atoms") or []
    print(f"\n📥 {json_path.name} — book={book_corpus} section={section_id} — {len(atoms)} atoms")

    inserted = skipped = 0
    for atom in atoms:
        aid = ingest_atom(conn, atom, atom.get("section_id") or section_id, book_corpus)
        if aid:
            inserted += 1
        else:
            skipped += 1
    return inserted, skipped, book_corpus


def main():
    if len(sys.argv) < 2:
        print("Usage: ingest_atomize_v3.py <drafts_dir_or_file>")
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
    book_corpus_seen = set()
    try:
        for f in files:
            try:
                ins, sk, bc = ingest_file(conn, f)
                total_in += ins
                total_skip += sk
                if bc:
                    book_corpus_seen.add(bc)
                conn.commit()
                print(f"  ✅ inserted={ins}  skipped={sk}")
            except Exception as e:
                conn.rollback()
                print(f"  ❌ {f.name}: {e}")
    finally:
        try:
            conn.execute("INSERT INTO atomic_questions_fts(atomic_questions_fts) VALUES('rebuild')")
            conn.execute("INSERT INTO atom_commentaries_fts(atom_commentaries_fts) VALUES('rebuild')")
            conn.commit()
            print("\n🔁 FTS rebuilt")
        except Exception as e:
            print(f"\n⚠ FTS rebuild failed: {e}")
        conn.close()

    print(f"\n🎯 TỔNG: inserted={total_in}  skipped={total_skip}  books={sorted(book_corpus_seen)}")


if __name__ == "__main__":
    main()
