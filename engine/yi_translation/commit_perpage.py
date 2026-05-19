"""commit_perpage — Merge per-page extraction vào wiki SQLite.

KHÁC commit_to_wiki.py (chunk-level):
- passages: granularity = 1 trang (page_start = page_end = pn), không phải chapter
- concepts: aggregate qua tất cả pages → dedupe vs existing
- micro_cases: insert nhiều hơn, granular hơn
- quotes: 1 bảng MỚI → ghi vào passages.raw_text như "quote: ..."

DEDUP STRATEGY:
- Concept UNIQUE(canonical_zh, canonical_vi):
  * Nếu có exist trong DB từ chunk-level 3D → MERGE mentioned_in_passages, giữ short_note dài nhất
  * Nếu mới → INSERT
- Methods UNIQUE(name_zh, author_id):
  * Existing → skip (đã có)
  * New → insert
- Passages: per-page rows (page_start=page_end=pn) — sẽ co-exist với chapter passages của 3D
- Cases: insert mới (no UNIQUE constraint → cẩn thận avoid full duplicate)

USAGE:
    python3 -m engine.yi_translation.commit_perpage
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import time
import unicodedata
from pathlib import Path

WIKI_DB = Path("/Users/ozvietnamdesktop/Desktop/yi/data/yi_wiki/wiki.sqlite3")
STAGING = Path("/Users/ozvietnamdesktop/Desktop/yi/data/_logs/extract-tq-perpage.json")
CORPUS_ID = "thieu-khang-tiet-tq"


def _norm_vi(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFC", s).strip()
    s = " ".join(s.replace("-", " ").replace("–", " ").replace("—", " ").split())
    return s.lower()


def _norm_zh(s: str) -> str:
    if not s:
        return ""
    return unicodedata.normalize("NFC", s).strip()


def commit_perpage_passages(con: sqlite3.Connection, pages: list[dict], *, author_id: int, corpus_id: str) -> dict:
    """Insert page-level passages. Idempotent on (corpus_id, page_start, page_end, topic)."""
    cur = con.cursor()
    stats = {"inserted": 0, "skipped": 0}
    for p in pages:
        r = p.get("result")
        if not r or not r.get("summary_3line"):
            continue
        pn = p["page"]
        topic = (r.get("summary_3line") or "")[:200]
        # Use page number as both start and end → distinguish from chapter passages
        existing = cur.execute(
            "SELECT passage_id FROM passages WHERE corpus_id=? AND page_start=? AND page_end=? AND topic=?",
            (corpus_id, pn, pn, topic),
        ).fetchone()
        if existing:
            stats["skipped"] += 1
            continue
        # Build raw_text: concat key quotes if any
        quotes = r.get("quotes") or []
        raw_text = "\n".join(f"« {q} »" for q in quotes[:3])
        # concepts_mentioned: list of canonical_vi from this page
        concepts_mentioned = [c.get("canonical_vi") for c in (r.get("concepts") or []) if c.get("canonical_vi")]
        cur.execute("""
            INSERT INTO passages
            (author_id, corpus_id, page_start, page_end, raw_text, topic, summary_50w,
             concepts_mentioned, related_passages, is_canonical, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            author_id,
            corpus_id,
            pn,
            pn,
            raw_text[:1500],
            topic,
            (r.get("summary_3line") or "")[:500],
            json.dumps(concepts_mentioned, ensure_ascii=False),
            "[]",
            1,
            int(time.time()),
        ))
        stats["inserted"] += 1
    return stats


def commit_perpage_methods(con: sqlite3.Connection, pages: list[dict], *, author_id: int, corpus_id: str) -> dict:
    cur = con.cursor()
    stats = {"inserted": 0, "skipped_dup": 0, "skipped_empty": 0}
    # Dedupe in-batch
    seen_in_batch: set[tuple[str, int]] = set()
    for p in pages:
        r = p.get("result")
        if not r:
            continue
        pn = p["page"]
        page_label = f"{corpus_id}:p{pn}"
        for m in r.get("methods") or []:
            name_vi = (m.get("name_vi") or "").strip()
            name_zh = _norm_zh(m.get("name_zh") or "")
            steps = m.get("procedure_steps") or []
            if not name_vi or not steps:
                stats["skipped_empty"] += 1
                continue
            if name_zh:
                existing = cur.execute(
                    "SELECT method_id FROM methods WHERE name_zh=? AND author_id=?",
                    (name_zh, author_id),
                ).fetchone()
                if existing or (name_zh, author_id) in seen_in_batch:
                    stats["skipped_dup"] += 1
                    continue
            try:
                cur.execute("""
                    INSERT INTO methods
                    (author_id, name_vi, name_zh, domain, inputs_required, procedure_steps,
                     output_format, source_passages, derived_from, case_studies,
                     confidence_baseline, notes, created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    author_id,
                    name_vi[:200],
                    name_zh[:200] if name_zh else None,
                    (m.get("domain") or "khác")[:50],
                    "[]",
                    json.dumps(steps, ensure_ascii=False),
                    "",
                    json.dumps([page_label], ensure_ascii=False),
                    "",
                    "[]",
                    0.0,
                    f"Per-page extraction Quyển 3, {page_label}",
                    int(time.time()),
                ))
                stats["inserted"] += 1
                if name_zh:
                    seen_in_batch.add((name_zh, author_id))
            except sqlite3.IntegrityError:
                stats["skipped_dup"] += 1
    return stats


def commit_perpage_concepts(con: sqlite3.Connection, pages: list[dict], *, corpus_id: str) -> dict:
    """Aggregate concepts across all pages, then merge with existing wiki."""
    cur = con.cursor()
    stats = {"inserted": 0, "merged_existing": 0, "merged_in_batch": 0, "skipped_empty": 0}

    # 1. Aggregate concepts across all pages by normalized key
    agg: dict[tuple[str, str], dict] = {}
    for p in pages:
        r = p.get("result")
        if not r:
            continue
        pn = p["page"]
        for c in r.get("concepts") or []:
            vi = (c.get("canonical_vi") or "").strip()
            zh = (c.get("canonical_zh") or "").strip()
            if not vi:
                stats["skipped_empty"] += 1
                continue
            key = (_norm_vi(vi), _norm_zh(zh))
            if key not in agg:
                agg[key] = {
                    "canonical_vi": vi,
                    "canonical_zh": zh,
                    "aliases": set(c.get("aliases") or []),
                    "short_note": (c.get("short_note") or "").strip(),
                    "first_seen_page": pn,
                    "mentioned_in_pages": [pn],
                }
            else:
                e = agg[key]
                stats["merged_in_batch"] += 1
                if len(vi) > len(e["canonical_vi"]):
                    e["canonical_vi"] = vi
                if zh and not e["canonical_zh"]:
                    e["canonical_zh"] = zh
                for a in (c.get("aliases") or []):
                    e["aliases"].add(a)
                note = (c.get("short_note") or "").strip()
                if len(note) > len(e["short_note"]):
                    e["short_note"] = note
                e["mentioned_in_pages"].append(pn)
                e["first_seen_page"] = min(e["first_seen_page"], pn)

    # 2. Commit aggregated concepts (merge with existing)
    for key, e in agg.items():
        existing = cur.execute(
            "SELECT concept_id, aliases, mentioned_in_passages, short_note "
            "FROM concept_index WHERE canonical_zh=? AND canonical_vi=?",
            (e["canonical_zh"], e["canonical_vi"]),
        ).fetchone()

        new_mentions_for_corpus = [f"{corpus_id}:p{pn}" for pn in sorted(set(e["mentioned_in_pages"]))]

        if existing:
            old_id, old_aliases, old_mentions, old_note = existing
            try:
                old_al = set(json.loads(old_aliases) if old_aliases else [])
            except Exception:
                old_al = set()
            try:
                old_m = json.loads(old_mentions) if old_mentions else []
            except Exception:
                old_m = []
            merged_aliases = old_al | e["aliases"]
            new_mentions = list(dict.fromkeys(list(old_m) + new_mentions_for_corpus))
            new_note = old_note if len(old_note or "") >= len(e["short_note"]) else e["short_note"]
            cur.execute(
                "UPDATE concept_index SET aliases=?, mentioned_in_passages=?, short_note=? WHERE concept_id=?",
                (
                    json.dumps(sorted(merged_aliases), ensure_ascii=False),
                    json.dumps(new_mentions, ensure_ascii=False),
                    new_note,
                    old_id,
                ),
            )
            stats["merged_existing"] += 1
        else:
            try:
                cur.execute("""
                    INSERT INTO concept_index
                    (canonical_vi, canonical_zh, aliases, mentioned_in_passages,
                     short_note, first_seen_corpus, first_seen_page, created_at)
                    VALUES (?,?,?,?,?,?,?,?)
                """, (
                    e["canonical_vi"][:200],
                    e["canonical_zh"][:200] if e["canonical_zh"] else None,
                    json.dumps(sorted(e["aliases"]), ensure_ascii=False) if e["aliases"] else "[]",
                    json.dumps(new_mentions_for_corpus, ensure_ascii=False),
                    e["short_note"][:500],
                    corpus_id,
                    e["first_seen_page"],
                    int(time.time()),
                ))
                stats["inserted"] += 1
            except sqlite3.IntegrityError:
                stats["merged_existing"] += 1
    return stats


def commit_perpage_cases(con: sqlite3.Connection, pages: list[dict], *, corpus_id: str) -> dict:
    cur = con.cursor()
    stats = {"inserted": 0, "skipped_empty": 0, "skipped_dup": 0}
    # Default method_id = Quan mai chiêm quyết
    default_row = cur.execute(
        "SELECT method_id FROM methods WHERE name_zh='觀梅占訣' OR name_vi='Quan mai chiêm quyết' LIMIT 1"
    ).fetchone()
    default_method_id = default_row[0] if default_row else 1

    # In-batch dedupe key: (event normalized + source page)
    seen: set[str] = set()
    for p in pages:
        r = p.get("result")
        if not r:
            continue
        pn = p["page"]
        page_label = f"{corpus_id}:p{pn}"
        for cs in r.get("micro_cases") or []:
            event = (cs.get("historical_event") or "").strip()
            if not event:
                stats["skipped_empty"] += 1
                continue
            dedupe_key = f"{_norm_vi(event[:100])}|{page_label}"
            if dedupe_key in seen:
                stats["skipped_dup"] += 1
                continue
            seen.add(dedupe_key)
            cur.execute("""
                INSERT INTO case_studies
                (method_id, historical_event, inputs_recorded, output_predicted,
                 output_actual, accuracy_score, source_book, created_at)
                VALUES (?,?,?,?,?,?,?,?)
            """, (
                default_method_id,
                event[:500],
                (cs.get("inputs") or cs.get("inputs_recorded") or "")[:500],
                (cs.get("predicted") or cs.get("output_predicted") or "")[:500],
                (cs.get("actual") or cs.get("output_actual") or "")[:500],
                0.0,
                page_label,
                int(time.time()),
            ))
            stats["inserted"] += 1
    return stats


def commit_all(staging_path: Path = STAGING, *, db_path: Path = WIKI_DB,
               corpus_id: str = CORPUS_ID) -> dict:
    state = json.loads(staging_path.read_text())
    pages = state.get("pages", [])
    if not pages:
        return {"error": "empty staging"}

    con = sqlite3.connect(db_path)
    try:
        # Lookup author + work
        cur = con.cursor()
        row = cur.execute("SELECT author_id FROM authors WHERE name_zh='邵雍'").fetchone()
        if not row:
            return {"error": "Thiệu Ung không có trong authors"}
        author_id = row[0]
        row = cur.execute("SELECT work_id FROM works WHERE corpus_id=?", (corpus_id,)).fetchone()
        if not row:
            return {"error": f"Work với corpus_id={corpus_id} không có"}
        work_id = row[0]

        print(f"📚 Commit per-page → author_id={author_id} (Thiệu Ung), work_id={work_id}")
        print(f"   Pages to process: {len(pages)}")
        print()

        results = {
            "passages": commit_perpage_passages(con, pages, author_id=author_id, corpus_id=corpus_id),
            "methods": commit_perpage_methods(con, pages, author_id=author_id, corpus_id=corpus_id),
            "concepts": commit_perpage_concepts(con, pages, corpus_id=corpus_id),
            "cases": commit_perpage_cases(con, pages, corpus_id=corpus_id),
        }
        con.commit()
        return results
    finally:
        con.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", default=str(STAGING))
    args = ap.parse_args()
    results = commit_all(Path(args.staging))
    print(json.dumps(results, indent=2, ensure_ascii=False))
