#!/usr/bin/env python3
"""Tag-fix atoms untagged — detect star/palace từ question + source_quote.

Atoms không có star/palace tag không vào được CUNG_SAO_TO_SECTION mapping
→ không retrieve được theo lá số. Script này detect bằng pattern matching
(re-use STAR_PATTERNS từ ingest_q1_q3_legacy) rồi MERGE vào subject_identifiers
(không ghi đè tags sẵn có).

Usage:
  python3 scripts/tag_fix_untagged_atoms.py [--dry-run]
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"

sys.path.insert(0, str(PROJECT_ROOT))
from scripts.ingest_q1_q3_legacy import STAR_PATTERNS, PALACE_PATTERNS  # noqa: E402

CORPORA = (
    "trung-chau-tu-vi-dau-so-2",
    "tu-vi-dau-so-toan-thu-vu-tai-luc",
    "tu-vi-nghiem-ly-toan-thu-thien-luong",
    "tu-vi-ham-so",
    "tu-vi-dau-so-toan-thu-zh",
)


def detect(text: str) -> tuple[list[str], list[str]]:
    stars = [c for c, pats in STAR_PATTERNS.items() if any(p in text for p in pats)]
    # Biệt danh / viết tắt qua wiki — "một fact nhiều tên gọi" (Anh chốt 2026-06-11)
    from engine.tu_vi.star_aliases import detect_stars
    for s in detect_stars(text):
        if s not in stars:
            stars.append(s)
    palaces = [c for c, pats in PALACE_PATTERNS.items() if any(p in text for p in pats)]
    return stars, palaces


def main():
    dry = "--dry-run" in sys.argv
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    qs = ",".join("?" * len(CORPORA))
    rows = conn.execute(f"""
        SELECT a.atom_id, a.question_text, a.source_quote, a.subject_identifiers
        FROM atomic_questions a
        JOIN chunks_v2 c ON c.chunk_id = a.chunk_id
        WHERE c.book_corpus_id IN ({qs})
          AND a.founder_verified >= 0
    """, CORPORA).fetchall()

    fixed = skipped_has = skipped_nodetect = 0
    for r in rows:
        subj = {}
        try:
            subj = json.loads(r["subject_identifiers"] or "{}")
        except json.JSONDecodeError:
            subj = {}

        has_star = bool(subj.get("star"))
        has_palace = bool(subj.get("palace"))
        if has_star and has_palace:
            skipped_has += 1
            continue

        text = f"{r['question_text'] or ''} {r['source_quote'] or ''}"
        stars, palaces = detect(text)

        changed = False
        if not has_star and stars:
            subj["star"] = sorted(set((subj.get("star") or []) + stars))
            changed = True
        if not has_palace and palaces:
            subj["palace"] = sorted(set((subj.get("palace") or []) + palaces))
            changed = True

        if not changed:
            skipped_nodetect += 1
            continue

        fixed += 1
        if not dry:
            conn.execute(
                "UPDATE atomic_questions SET subject_identifiers = ? WHERE atom_id = ?",
                (json.dumps(subj, ensure_ascii=False), r["atom_id"]),
            )

    if not dry:
        conn.commit()
    conn.close()

    print(f"Scanned:           {len(rows)}")
    print(f"Fixed (tag added): {fixed}")
    print(f"Already tagged:    {skipped_has}")
    print(f"No detect:         {skipped_nodetect}  (atoms thuần paradigm/khái niệm — OK)")
    if dry:
        print("[DRY RUN — chưa ghi DB]")


if __name__ == "__main__":
    main()
