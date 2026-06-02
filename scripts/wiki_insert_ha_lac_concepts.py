#!/usr/bin/env python3
"""Bổ sung wiki concepts Hà Lạc với LUẬN GIẢI TƯỜNG MINH.

Paradigm Anh (2026-06-02): "Có gì hay bổ sung vào wiki sau luận giải cho tường minh."

Module này:
1. Add Xuân Cang vào authors
2. Add work "Bát Tự Hà Lạc và Quỹ Đạo Đời Người" (1995)
3. Insert concepts cho 33 quẻ đã thâm nhuần với luận giải tường minh
4. Insert paradigm cross-links (FOUNDER_*)
"""

from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI_PATH = ROOT / "data" / "yi_wiki" / "wiki.sqlite3"

sys.path.insert(0, str(ROOT))
from engine.ha_lac.thoi_que import THOI_QUE_TABLE, QUAI_ALIASES  # noqa: E402
from engine.ha_lac.paradigm_quy_chieu import (  # noqa: E402
    PARADIGM_CASES,
    IRON_RULE_CROSS_LINK,
)


def main():
    if not WIKI_PATH.exists():
        print(f"❌ Wiki DB không tồn tại: {WIKI_PATH}")
        return 1

    # Backup before
    backup = WIKI_PATH.parent / f"wiki.sqlite3.before-luan-giai-sau-{int(time.time())}.bak"
    import shutil
    shutil.copy(WIKI_PATH, backup)
    print(f"✓ Backup: {backup.name}")

    conn = sqlite3.connect(WIKI_PATH)
    cur = conn.cursor()
    now = int(time.time())
    corpus_id = "bat-tu-ha-lac-xuan-cang"

    # ── 1. Add Xuân Cang as author ──
    cur.execute("SELECT author_id FROM authors WHERE name_vi LIKE '%Xuân Cang%'")
    row = cur.fetchone()
    if not row:
        cur.execute(
            "INSERT INTO authors (name_vi, name_zh, tier_in_lineage, era, "
            "worldview_school, bio_summary, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "Xuân Cang",
                "春耕",
                2,  # kế thừa Học Năng
                "viet-nam-hien-dai",
                "ha-lac-viet-nam",
                "Nhà Hà Lạc Lý Số Việt Nam, kế thừa Học Năng. Sách 'Bát Tự Hà Lạc "
                "& Quỹ Đạo Đời Người' (1995, 608 trang) — bộ sách Hà Lạc tiếng Việt "
                "đầy đủ nhất, kết hợp Học Năng + Nguyễn Hiến Lê + Phan Bội Châu phụ chú.",
                now,
            ),
        )
        xuan_cang_id = cur.lastrowid
        print(f"✓ Added Xuân Cang: author_id={xuan_cang_id}")
    else:
        xuan_cang_id = row[0]
        print(f"· Xuân Cang đã có: author_id={xuan_cang_id}")

    # ── 2. Add work "Bát Tự Hà Lạc & Quỹ Đạo Đời Người" ──
    cur.execute(
        "SELECT work_id FROM works WHERE title_vi LIKE '%Quỹ Đạo Đời Người%'"
    )
    row = cur.fetchone()
    if not row:
        cur.execute(
            "INSERT INTO works (author_id, title_vi, title_zh, year_composed, "
            "role, corpus_id, is_canonical, notes, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                xuan_cang_id,
                "Bát Tự Hà Lạc và Quỹ Đạo Đời Người",
                "八字河洛 - 人生軌道",
                1995,
                "author",
                corpus_id,
                1,
                "Sách chính cho engine ha_lac/ vòng 1-12 (2026-06-01..02). "
                "608 trang. Phần I: lý thuyết. Phần II: 64 quẻ × 6 hào (384 hào). "
                "Phần III: chân dung nhà văn soi chiếu. Em đọc kỹ p1-235 + jump Tiết (p389).",
                now,
            ),
        )
        work_id = cur.lastrowid
        print(f"✓ Added work: work_id={work_id}")
    else:
        work_id = row[0]
        print(f"· Work đã có: work_id={work_id}")

    # ── 3. Insert concepts cho 33 quẻ ──
    inserted_quae = 0
    skipped_quae = 0
    for quai_name, paradigm in THOI_QUE_TABLE.items():
        canonical_vi = f"Quẻ Hà Lạc — {quai_name}"

        # Check existed
        cur.execute(
            "SELECT concept_id FROM concept_index WHERE canonical_vi = ? AND first_seen_corpus = ?",
            (canonical_vi, corpus_id),
        )
        if cur.fetchone():
            skipped_quae += 1
            continue

        # Build short_note (luận giải tường minh, multi-paragraph)
        parts = [
            f"**{paradigm['ban_chat']}**",
            f"**Nên thế nào**: {paradigm['nen_the_nao']}",
        ]
        if "tuong" in paradigm:
            parts.append(f"**Tượng quẻ**: {paradigm['tuong']}")

        # Inject key paradigm/rule/case_study
        for k, v in paradigm.items():
            if k.startswith(("key_paradigm", "key_rule", "case_study", "cross_link", "thien_co_dat_si")):
                parts.append(v)

        short_note = "\n\n".join(parts)[:4000]  # cap để tránh quá lớn

        aliases = json.dumps([quai_name, paradigm.get("paradigm_keyword", "")], ensure_ascii=False)

        cur.execute(
            "INSERT INTO concept_index (canonical_vi, canonical_zh, aliases, "
            "short_note, first_seen_corpus, category, school, corpora, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                canonical_vi,
                None,
                aliases,
                short_note,
                corpus_id,
                "hà-lạc-quẻ",
                "ha-lac-xuan-cang",
                json.dumps([corpus_id], ensure_ascii=False),
                now,
            ),
        )
        inserted_quae += 1

    print(f"✓ Inserted {inserted_quae} quẻ concepts (skipped {skipped_quae} existing)")

    # ── 4. Insert IRON RULE cross-link concepts ──
    inserted_ir = 0
    for key, content in IRON_RULE_CROSS_LINK.items():
        canonical_vi = f"Iron Rule cross-link — {key}"
        cur.execute(
            "SELECT concept_id FROM concept_index WHERE canonical_vi = ?",
            (canonical_vi,),
        )
        if cur.fetchone():
            continue
        cur.execute(
            "INSERT INTO concept_index (canonical_vi, aliases, short_note, "
            "first_seen_corpus, category, school, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                canonical_vi,
                json.dumps([key], ensure_ascii=False),
                content,
                corpus_id,
                "iron-rule-cross-link",
                "ha-lac-xuan-cang",
                now,
            ),
        )
        inserted_ir += 1
    print(f"✓ Inserted {inserted_ir} Iron Rule cross-link concepts")

    # ── 5. Insert PARADIGM CASES (case study sử/đời sống) ──
    inserted_cases = 0
    for (que, hao), cases in PARADIGM_CASES.items():
        for c in cases:
            actor = c["actor"]
            canonical_vi = f"Case study Hà Lạc — {que} hào {hao or 'tổng'} — {actor}"
            cur.execute(
                "SELECT concept_id FROM concept_index WHERE canonical_vi = ?",
                (canonical_vi,),
            )
            if cur.fetchone():
                continue
            short = (
                f"**Bối cảnh**: {c['situation']}\n\n"
                f"**Bài học paradigm**: {c['paradigm_lesson']}\n\n"
                f"_Nguồn: {c['source']}_"
            )
            cur.execute(
                "INSERT INTO concept_index (canonical_vi, aliases, short_note, "
                "first_seen_corpus, category, school, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    canonical_vi,
                    json.dumps([actor, que], ensure_ascii=False),
                    short,
                    corpus_id,
                    "hà-lạc-case-study",
                    "ha-lac-xuan-cang",
                    now,
                ),
            )
            inserted_cases += 1
    print(f"✓ Inserted {inserted_cases} case study concepts")

    conn.commit()
    conn.close()

    print()
    print(f"🎯 Total Hà Lạc Xuân Cang concepts: {inserted_quae + inserted_ir + inserted_cases}")
    print(f"   Backup at: {backup.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
