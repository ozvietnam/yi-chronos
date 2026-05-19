"""Import Q1 Tử Vi (545 cách cục + 320 concepts) vào yi_wiki schema.

Tables target:
    concept_index    — 320 concepts (canonical_vi, short_note, first_seen_corpus)
    passages         — 545 cách cục (mỗi cách = 1 passage of Phú Thái Vi)
    authors          — đảm bảo "Trần Đoàn" có author_id (Hi Di tiên sinh)

Idempotent: re-run sẽ INSERT OR IGNORE (UNIQUE constraint trên canonical_zh+vi).
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
WIKI_DB = ROOT / "data/yi_wiki/wiki.sqlite3"
Q1_MASTER = ROOT / "data/yi_publishing/q1_tuvi/master"
CORPUS_ID = "tuvidauso-zh-q1"  # Different from Q2's "tuvidauso-zh"

AUTHOR_NAME_VI = "Trần Đoàn"
AUTHOR_NAME_ZH = "陳摶"
AUTHOR_TITLE = "Hi Di tiên sinh — tác giả Tử Vi Đẩu Số Toàn Thư (thế kỷ X)"


def ensure_author(db: sqlite3.Connection) -> int:
    """Return author_id, creating if missing."""
    row = db.execute(
        "SELECT author_id FROM authors WHERE name_vi = ?", (AUTHOR_NAME_VI,)
    ).fetchone()
    if row:
        return row[0]
    now = int(time.time())
    cur = db.execute("""
        INSERT INTO authors
            (name_vi, name_zh, tier_in_lineage, era,
             birth_year, death_year, worldview_school,
             bio_summary, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        AUTHOR_NAME_VI, AUTHOR_NAME_ZH,
        1,                                  # tier 1 (founder of Tử Vi school)
        "Tống (北宋)",
        872, 989,
        "tu_vi_dau_so",
        "Hi Di tiên sinh — đạo sĩ Hoa Sơn, tổ sư Tử Vi Đẩu Số. Tác giả Tử Vi Đẩu Số Toàn Thư (sau được Phan Hy Doãn biên soạn, Dương Nhất Vũ hiệu duyệt).",
        now,
    ))
    return cur.lastrowid


def import_concepts(db: sqlite3.Connection) -> dict:
    """Import 320 concepts từ concepts_index.json. Returns counts."""
    src = json.loads((Q1_MASTER / "concepts_index.json").read_text())
    now = int(time.time())
    inserted = 0
    skipped = 0
    for term, entry in src.items():
        canonical_vi = term.strip()
        # No Han char in concepts_index by default — use NULL
        canonical_zh = None
        short_note = entry.get("definition", "")[:280]
        kind = entry.get("kind", "?")
        # Prefix short_note with [kind]
        short_note = f"[{kind}] {short_note}"
        first_page = entry.get("first_page", 0)
        try:
            db.execute("""
                INSERT INTO concept_index
                    (canonical_vi, canonical_zh, short_note,
                     first_seen_corpus, first_seen_page, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (canonical_vi, canonical_zh, short_note, CORPUS_ID, first_page, now))
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1
    db.commit()
    return {"inserted": inserted, "skipped": skipped, "total_source": len(src)}


def import_cach_cuc(db: sqlite3.Connection, author_id: int) -> dict:
    """Import 545 cách cục as passages. Each cách = 1 passage.

    Schema mapping:
        passages.raw_text          = bằng chứng text (Hán-Việt nguyên văn)
        passages.summary_50w       = y_nghia (tiếng Việt)
        passages.topic             = ten cách + [cap_do]
        passages.concepts_mentioned = JSON list của concepts mentioned in this cách
        passages.page_start/end    = first source page
        passages.is_canonical      = 1 (Phú Thái Vi là canonical)
    """
    src = json.loads((Q1_MASTER / "cach_cuc_index.json").read_text())
    now = int(time.time())
    inserted = 0
    for ten, entry in src.items():
        bang_chung = ""
        sources = entry.get("sources", [])
        if sources:
            bang_chung = sources[0].get("bang_chung", "")
        page_start = sources[0]["page"] if sources else 0
        page_end = sources[-1]["page"] if sources else page_start

        topic = f"{ten} [{entry.get('cap_do', '?')}]"
        summary = entry.get("y_nghia", "")[:280]
        # Detect concepts in name + dieu_kien
        from engine.tu_vi.cach_cuc_dict import CHINH_TINH, PHU_SAT_TINH, HOA
        ALL_STARS = CHINH_TINH + PHU_SAT_TINH + HOA
        text_to_scan = ten + " " + entry.get("dieu_kien", "") + " " + bang_chung
        mentioned = sorted({s for s in ALL_STARS if s.lower() in text_to_scan.lower()})

        # Check duplicate by topic + page_start (no unique constraint, so manual)
        existing = db.execute(
            "SELECT passage_id FROM passages WHERE topic = ? AND page_start = ? AND corpus_id = ?",
            (topic, page_start, CORPUS_ID),
        ).fetchone()
        if existing:
            continue
        db.execute("""
            INSERT INTO passages
                (author_id, corpus_id, page_start, page_end, raw_text,
                 topic, summary_50w, concepts_mentioned, is_canonical, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            author_id, CORPUS_ID, page_start, page_end,
            bang_chung or ten, topic, summary,
            json.dumps(mentioned, ensure_ascii=False),
            now,
        ))
        inserted += 1
    db.commit()
    return {"inserted": inserted, "total_source": len(src)}


def main():
    if not WIKI_DB.exists():
        print(f"❌ Wiki DB not found: {WIKI_DB}", file=sys.stderr)
        sys.exit(1)

    # Backup before mutating
    import shutil
    backup = WIKI_DB.parent / f"wiki.sqlite3.before-q1-{time.strftime('%Y%m%d-%H%M%S')}.bak"
    shutil.copy(WIKI_DB, backup)
    print(f"📦 Backup: {backup.name}")

    db = sqlite3.connect(WIKI_DB)
    try:
        author_id = ensure_author(db)
        print(f"✓ Author 'Trần Đoàn' = author_id={author_id}")

        c_result = import_concepts(db)
        print(f"✓ Concepts: inserted={c_result['inserted']}, skipped={c_result['skipped']}, source={c_result['total_source']}")

        p_result = import_cach_cuc(db, author_id)
        print(f"✓ Passages (cách cục): inserted={p_result['inserted']}, source={p_result['total_source']}")

        # Final stats
        total_concepts = db.execute("SELECT COUNT(*) FROM concept_index").fetchone()[0]
        total_passages = db.execute("SELECT COUNT(*) FROM passages").fetchone()[0]
        q1_concepts = db.execute(
            "SELECT COUNT(*) FROM concept_index WHERE first_seen_corpus = ?", (CORPUS_ID,)
        ).fetchone()[0]
        q1_passages = db.execute(
            "SELECT COUNT(*) FROM passages WHERE corpus_id = ?", (CORPUS_ID,)
        ).fetchone()[0]
        print(f"\n═══ FINAL ═══")
        print(f"  concept_index total: {total_concepts} (Q1 added: {q1_concepts})")
        print(f"  passages total:      {total_passages} (Q1 added: {q1_passages})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
