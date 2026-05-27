#!/usr/bin/env python3
"""Seed 64 quẻ Kinh Dịch (deep files) vào wiki SQLite.

Pipeline:
1. Tạo work "Kinh Dịch Trọn Bộ" (Ngô Tất Tố, corpus=kinh-dich-tron-bo-ngo-tat-to)
2. Tạo 64 passages (1/quẻ) chứa body markdown làm raw_text
3. Extract concepts:
   - Tên quẻ (canonical_vi=Kiền, canonical_zh=乾) — 64 concepts
   - Routing keys (slug → canonical_vi readable) — ~300 concepts
   - Key phrases trong blockquotes (Trình Di, Chu Hy citations) — extract Hán terms
4. Link concepts ↔ passages qua concepts_mentioned + mentioned_in_passages
"""
from __future__ import annotations

import re
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.yi_wiki.luan_sau_kinhdich import list_hexagrams, get_hexagram

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "yi_wiki" / "wiki.sqlite3"
NGO_TAT_TO_AUTHOR_ID = 11
TRINH_DI_AUTHOR_ID = 6
CHU_HY_AUTHOR_ID = 5
CORPUS_ID = "kinh-dich-tron-bo-ngo-tat-to"


def _backup_db() -> None:
    """Backup DB trước khi seed."""
    import shutil
    ts = time.strftime("%Y%m%d-%H%M%S")
    bak = DB_PATH.parent / f"wiki.sqlite3.before-kinh-dich-{ts}.bak"
    shutil.copy(DB_PATH, bak)
    print(f"[backup] {bak.name}")


def _ensure_work(conn: sqlite3.Connection) -> int:
    """Tạo work 'Kinh Dịch Trọn Bộ' nếu chưa có. Return work_id."""
    cur = conn.execute(
        "SELECT work_id FROM works WHERE corpus_id = ?", (CORPUS_ID,)
    )
    row = cur.fetchone()
    if row:
        print(f"[work] exists work_id={row[0]}")
        return row[0]
    now = int(time.time())
    cur = conn.execute(
        """INSERT INTO works
           (author_id, title_vi, title_zh, year_composed, role, corpus_id, is_canonical, notes, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (NGO_TAT_TO_AUTHOR_ID, "Kinh Dịch Trọn Bộ", "周易", None, "translation",
         CORPUS_ID, 1,
         "Bản dịch Ngô Tất Tố. 64 quẻ đã deep với Trình Di Truyện + Bản nghĩa Chu Hy + Tiên Nho.",
         now),
    )
    work_id = cur.lastrowid
    print(f"[work] created work_id={work_id}")
    return work_id


def _seed_passages(conn: sqlite3.Connection) -> dict:
    """Tạo 64 passages (1/quẻ). Return {hexagram_number: passage_id}."""
    items = list_hexagrams()
    pid_map = {}
    now = int(time.time())
    for h in items:
        # Get full body
        detail = get_hexagram(str(h["number"]))
        if not detail:
            continue
        # Check exists
        cur = conn.execute(
            """SELECT passage_id FROM passages
               WHERE corpus_id = ? AND page_start = ? AND topic = ?""",
            (CORPUS_ID, h["number"], f"Quẻ {h['number']} — {h['name_vi']}"),
        )
        row = cur.fetchone()
        if row:
            pid_map[h["number"]] = row[0]
            continue
        topic = f"Quẻ {h['number']} — {h['name_vi']}"
        summary = h["description"][:200] if h["description"] else f"Quẻ {h['name_vi']} ({h['name_zh']}) — {h['upper']}/{h['lower']}"
        # Use number as both page_start and page_end (hexagram number as ID)
        cur = conn.execute(
            """INSERT INTO passages
               (author_id, corpus_id, page_start, page_end, raw_text, topic, summary_50w,
                concepts_mentioned, related_passages, is_canonical, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (NGO_TAT_TO_AUTHOR_ID, CORPUS_ID, h["number"], h["number"],
             detail["body_markdown"], topic, summary, "", "", 1, now),
        )
        pid_map[h["number"]] = cur.lastrowid
    print(f"[passages] seeded {len(pid_map)} passages")
    return pid_map


def _normalize_routing_key(key: str) -> str:
    """Convert routing-key slug → human-readable canonical_vi.

    vd: 'tien-canh-tam-nhat-hau-canh-tam-nhat' → 'Tiên canh tam nhật hậu canh tam nhật'
    """
    s = key.replace("-", " ").strip()
    # Capitalize first letter of each word for readability
    return " ".join(w.capitalize() if i == 0 else w for i, w in enumerate(s.split()))


def _extract_key_phrases_from_body(body: str) -> list[tuple[str, str]]:
    """Extract Hán nguyên văn + dịch âm từ blockquote markdown.

    Heuristic: tìm pattern '> 字字字, 字字字.' (Hán pure) + tiếp theo `> _dịch âm._`
    """
    out = []
    lines = body.split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i].strip()
        # Pattern: line starts with `> ` + nội dung CJK
        if ln.startswith("> ") and not ln.startswith("> _") and not ln.startswith("> >"):
            content = ln[2:].strip()
            # Check if mostly Hán (>= 50% CJK chars in content)
            if content and len(content) <= 120:
                cjk_count = sum(1 for ch in content if "一" <= ch <= "鿿")
                if cjk_count >= 3 and cjk_count / max(len(content), 1) >= 0.3:
                    # Find next dịch âm line
                    han = content
                    am = ""
                    for j in range(i + 1, min(i + 4, len(lines))):
                        jln = lines[j].strip()
                        if jln.startswith("> _") and jln.endswith("_"):
                            am = jln[3:-1].strip()
                            break
                    if han and am:
                        out.append((han, am))
        i += 1
    return out


def _seed_concepts(conn: sqlite3.Connection, work_id: int, pid_map: dict) -> None:
    """Extract + insert concepts từ 64 quẻ."""
    items = list_hexagrams()
    now = int(time.time())
    seen_canonical: set[tuple[str, str]] = set()
    inserted = 0
    skipped = 0

    for h in items:
        detail = get_hexagram(str(h["number"]))
        if not detail:
            continue
        passage_id = pid_map.get(h["number"])

        # === 1. Tên quẻ ===
        canonical_vi = h["name_vi"]
        canonical_zh = h["name_zh"]
        key = (canonical_zh, canonical_vi)
        if key not in seen_canonical:
            seen_canonical.add(key)
            short_note = (h["description"] or "")[:200]
            try:
                conn.execute(
                    """INSERT INTO concept_index
                       (canonical_vi, canonical_zh, aliases, mentioned_in_passages,
                        short_note, first_seen_corpus, first_seen_page, created_at,
                        category, corpora, school)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (canonical_vi, canonical_zh, "", str(passage_id), short_note,
                     CORPUS_ID, h["number"], now, "que",
                     CORPUS_ID, "kinh-dich"),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                # Already exists — update mentioned_in_passages
                conn.execute(
                    """UPDATE concept_index
                       SET mentioned_in_passages = COALESCE(mentioned_in_passages, '') || ',' || ?
                       WHERE canonical_zh = ? AND canonical_vi = ?""",
                    (str(passage_id), canonical_zh, canonical_vi),
                )
                skipped += 1

        # === 2. Routing keys ===
        for rk in (detail.get("routing_keys") or []):
            cvi = _normalize_routing_key(rk)
            if not cvi:
                continue
            key = ("", cvi)
            if key in seen_canonical:
                continue
            seen_canonical.add(key)
            try:
                conn.execute(
                    """INSERT INTO concept_index
                       (canonical_vi, canonical_zh, aliases, mentioned_in_passages,
                        short_note, first_seen_corpus, first_seen_page, created_at,
                        category, corpora, school)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (cvi, "", rk, str(passage_id),
                     f"Tâm pháp/routing key cho quẻ {h['number']} {h['name_vi']}",
                     CORPUS_ID, h["number"], now, "tam_phap",
                     CORPUS_ID, "kinh-dich"),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                skipped += 1

        # === 3. Hán phrases từ blockquotes (Lời Kinh + 6 hào) ===
        phrases = _extract_key_phrases_from_body(detail["body_markdown"])
        for han, am in phrases[:6]:  # cap 6 per quẻ
            # Truncate Han to keep canonical_zh reasonable
            han_short = han.split(".")[0].strip()[:80] if han else ""
            am_short = am.split(".")[0].strip()[:120] if am else ""
            if not han_short or not am_short:
                continue
            key = (han_short, am_short)
            if key in seen_canonical:
                continue
            seen_canonical.add(key)
            try:
                conn.execute(
                    """INSERT INTO concept_index
                       (canonical_vi, canonical_zh, aliases, mentioned_in_passages,
                        short_note, first_seen_corpus, first_seen_page, created_at,
                        category, corpora, school)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (am_short, han_short, "", str(passage_id),
                     f"Hán văn từ quẻ {h['number']} {h['name_vi']} (Lời Kinh + 6 hào)",
                     CORPUS_ID, h["number"], now, "phrase",
                     CORPUS_ID, "kinh-dich"),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                skipped += 1

    print(f"[concepts] inserted={inserted}, skipped (dup)={skipped}")


def main() -> None:
    if not DB_PATH.exists():
        print(f"DB not found: {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    _backup_db()

    conn = sqlite3.connect(str(DB_PATH))
    try:
        work_id = _ensure_work(conn)
        pid_map = _seed_passages(conn)
        _seed_concepts(conn, work_id, pid_map)
        conn.commit()

        # Stats
        cur = conn.execute(
            "SELECT COUNT(*) FROM passages WHERE corpus_id = ?", (CORPUS_ID,)
        )
        n_pass = cur.fetchone()[0]
        cur = conn.execute(
            "SELECT COUNT(*) FROM concept_index WHERE first_seen_corpus = ?", (CORPUS_ID,)
        )
        n_concept = cur.fetchone()[0]
        cur = conn.execute(
            "SELECT category, COUNT(*) FROM concept_index WHERE first_seen_corpus = ? GROUP BY category",
            (CORPUS_ID,),
        )
        breakdown = cur.fetchall()
        print()
        print("=== Kinh Dịch wiki seed DONE ===")
        print(f"  passages: {n_pass}")
        print(f"  concepts total: {n_concept}")
        for cat, n in breakdown:
            print(f"    {cat}: {n}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
