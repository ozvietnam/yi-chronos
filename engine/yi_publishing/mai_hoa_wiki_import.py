"""Import Mai Hoa Q1+Q2 (methods + concepts) vào yi_wiki schema.

Author: Thiệu Khang Tiết — tier_in_lineage=1 (đã có author_id)
Corpus: mai-hoa-dich-so-q1q2
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
WIKI_DB = ROOT / "data/yi_wiki/wiki.sqlite3"
MASTER = ROOT / "data/yi_publishing/mai_hoa_thamnhuan/master"
CORPUS_ID = "mai-hoa-dich-so-q1q2"

AUTHOR_NAME_VI = "Thiệu Khang Tiết"


def get_author_id(db: sqlite3.Connection) -> int:
    row = db.execute("SELECT author_id FROM authors WHERE name_vi = ?", (AUTHOR_NAME_VI,)).fetchone()
    if row:
        return row[0]
    # Create
    cur = db.execute("""
        INSERT INTO authors (name_vi, name_zh, tier_in_lineage, era, birth_year, death_year,
                              worldview_school, bio_summary, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (AUTHOR_NAME_VI, "邵雍", 1, "Tống", 1011, 1077,
          "mai_hoa_dich_so",
          "Thiệu Khang Tiết — nhà đại triết học và đại dịch học đời Tống, tác giả Mai Hoa Dịch Số.",
          int(time.time())))
    return cur.lastrowid


def import_concepts(db, author_id):
    src = json.loads((MASTER / "concepts_index.json").read_text())
    now = int(time.time())
    inserted = skipped = 0
    for term, entry in src.items():
        canonical_vi = term.strip()
        kind = entry.get("kind", "?")
        short_note = f"[{kind}] {entry.get('definition','')[:280]}"
        first_page = entry.get("first_page", 0)
        try:
            db.execute("""
                INSERT INTO concept_index
                    (canonical_vi, canonical_zh, short_note, first_seen_corpus, first_seen_page, created_at)
                VALUES (?, NULL, ?, ?, ?, ?)
            """, (canonical_vi, short_note, CORPUS_ID, first_page, now))
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1
    db.commit()
    return {"inserted": inserted, "skipped": skipped, "total": len(src)}


def import_methods(db, author_id):
    """Import methods as passages (mỗi method = 1 passage)."""
    src = json.loads((MASTER / "methods_index.json").read_text())
    now = int(time.time())
    inserted = 0
    for ten, entry in src.items():
        pages = entry.get("pages", [entry.get("first_page", 0)])
        page_start = min(pages) if pages else 0
        page_end = max(pages) if pages else page_start
        topic = f"{ten} [{entry.get('linh_vuc', '?')}]"
        raw = entry.get("quy_tac", "") or ten
        summary = entry.get("y_nghia", "")[:280]
        existing = db.execute(
            "SELECT passage_id FROM passages WHERE topic=? AND page_start=? AND corpus_id=?",
            (topic, page_start, CORPUS_ID),
        ).fetchone()
        if existing:
            continue
        db.execute("""
            INSERT INTO passages
                (author_id, corpus_id, page_start, page_end, raw_text,
                 topic, summary_50w, is_canonical, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (author_id, CORPUS_ID, page_start, page_end, raw, topic, summary, now))
        inserted += 1
    db.commit()
    return {"inserted": inserted, "total": len(src)}


def main():
    if not WIKI_DB.exists():
        print(f"❌ Wiki DB not found", file=sys.stderr)
        sys.exit(1)
    backup = WIKI_DB.parent / f"wiki.sqlite3.before-mh-{time.strftime('%Y%m%d-%H%M%S')}.bak"
    shutil.copy(WIKI_DB, backup)
    print(f"📦 Backup: {backup.name}")

    db = sqlite3.connect(WIKI_DB)
    try:
        aid = get_author_id(db)
        print(f"✓ Author 'Thiệu Khang Tiết' = author_id={aid}")
        c = import_concepts(db, aid)
        print(f"✓ Concepts: inserted={c['inserted']}, skipped={c['skipped']}, total_source={c['total']}")
        p = import_methods(db, aid)
        print(f"✓ Methods (as passages): inserted={p['inserted']}, total_source={p['total']}")
        total_c = db.execute("SELECT COUNT(*) FROM concept_index").fetchone()[0]
        total_p = db.execute("SELECT COUNT(*) FROM passages").fetchone()[0]
        print(f"\n═══ Wiki FINAL ═══")
        print(f"  concepts: {total_c}")
        print(f"  passages: {total_p}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
