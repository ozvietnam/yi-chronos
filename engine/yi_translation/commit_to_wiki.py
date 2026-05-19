"""commit_to_wiki — Commit staging JSON từ extract_to_wiki.py vào wiki SQLite.

DEDUP STRATEGY:
- concept_index: UNIQUE(canonical_zh, canonical_vi). Nếu trùng → merge `mentioned_in_passages`
  + giữ `short_note` dài nhất + extend `aliases`.
- passages: insert mới với corpus_id + page_start + page_end.
  Nếu (corpus_id, page_start, page_end, topic) trùng → skip (idempotent).
- methods: UNIQUE(name_zh, author_id). Nếu trùng → skip (đã có).
- case_studies: insert mới, FK method_id (lookup theo name_zh; nếu không match thì FK NULL hoặc skip).

USAGE:
    python3 -m engine.yi_translation.commit_to_wiki \\
        --staging data/_logs/extract-tq-staging.json \\
        --corpus thieu-khang-tiet-tq \\
        --work-id 6 \\
        --author-id <Thiệu Khang Tiết>
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import time
import unicodedata
from pathlib import Path

WIKI_DB = Path("/Users/ozvietnamdesktop/Desktop/yi/data/yi_wiki/wiki.sqlite3")


def _norm_vi(s: str) -> str:
    """Normalize Vietnamese: strip whitespace + collapse internal spaces + lowercase for dedup key.
    Giữ dấu (NFC compose). KHÔNG bỏ dấu vì "Thể Dụng" ≠ "The Dung"."""
    if not s:
        return ""
    s = unicodedata.normalize("NFC", s).strip()
    # Collapse multiple spaces, hyphens, ndashes
    s = " ".join(s.replace("-", " ").replace("–", " ").replace("—", " ").split())
    return s.lower()


def _norm_zh(s: str) -> str:
    if not s:
        return ""
    return unicodedata.normalize("NFC", s).strip()


def lookup_author_id(con: sqlite3.Connection, name_zh: str = "邵雍") -> int | None:
    cur = con.cursor()
    row = cur.execute("SELECT author_id FROM authors WHERE name_zh = ?", (name_zh,)).fetchone()
    return row[0] if row else None


def lookup_work_id(con: sqlite3.Connection, corpus_id: str) -> int | None:
    cur = con.cursor()
    row = cur.execute("SELECT work_id FROM works WHERE corpus_id = ?", (corpus_id,)).fetchone()
    return row[0] if row else None


def commit_passages(con: sqlite3.Connection, chapters: list[dict], *, author_id: int, corpus_id: str) -> dict:
    cur = con.cursor()
    stats = {"inserted": 0, "skipped": 0}
    for ch in chapters:
        r = ch.get("result")
        if not r or not r.get("passage"):
            continue
        p = r["passage"]
        topic = (p.get("topic") or "")[:200]
        # Idempotent check
        existing = cur.execute(
            "SELECT passage_id FROM passages WHERE corpus_id=? AND page_start=? AND page_end=? AND topic=?",
            (corpus_id, ch["start_page"], ch["end_page"], topic),
        ).fetchone()
        if existing:
            stats["skipped"] += 1
            continue
        cur.execute("""
            INSERT INTO passages
            (author_id, corpus_id, page_start, page_end, raw_text, topic, summary_50w,
             concepts_mentioned, related_passages, is_canonical, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            author_id,
            corpus_id,
            ch["start_page"],
            ch["end_page"],
            p.get("raw_text_quote", "")[:1000],
            topic,
            p.get("summary_50w", "")[:500],
            json.dumps(p.get("concepts_mentioned", []), ensure_ascii=False),
            "[]",
            1,
            int(time.time()),
        ))
        stats["inserted"] += 1
    return stats


def commit_methods(con: sqlite3.Connection, chapters: list[dict], *, author_id: int, corpus_id: str) -> dict:
    cur = con.cursor()
    stats = {"inserted": 0, "skipped_dup": 0, "skipped_empty": 0}
    seen_in_batch = set()  # (name_zh, author_id) already inserted in this batch
    for ch in chapters:
        r = ch.get("result")
        if not r:
            continue
        page_label = f"{corpus_id}:p{ch['start_page']}-{ch['end_page']}"
        for m in r.get("methods", []):
            name_vi = (m.get("name_vi") or "").strip()
            name_zh = _norm_zh(m.get("name_zh", "") or "")
            if not name_vi:
                stats["skipped_empty"] += 1
                continue
            # Existing check (DB-level UNIQUE on name_zh+author_id)
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
                    json.dumps(m.get("inputs_required", []), ensure_ascii=False) if m.get("inputs_required") else "[]",
                    json.dumps(m.get("procedure_steps", []), ensure_ascii=False),
                    "",
                    json.dumps([page_label], ensure_ascii=False),
                    "",
                    "[]",
                    0.0,
                    f"Trích từ Quyển 3 (图解梅花易数), {page_label}",
                    int(time.time()),
                ))
                stats["inserted"] += 1
                if name_zh:
                    seen_in_batch.add((name_zh, author_id))
            except sqlite3.IntegrityError:
                stats["skipped_dup"] += 1
    return stats


def commit_concepts(con: sqlite3.Connection, chapters: list[dict], *, corpus_id: str) -> dict:
    """Merge concepts với existing rows. Dedup on _norm_vi(canonical_vi) + _norm_zh(canonical_zh)."""
    cur = con.cursor()
    stats = {"inserted": 0, "merged": 0, "skipped_empty": 0}

    # 1. Aggregate concepts across all chapters by normalized key
    agg: dict[tuple[str, str], dict] = {}
    for ch in chapters:
        r = ch.get("result")
        if not r:
            continue
        page = ch["start_page"]
        page_label = f"p{ch['start_page']}-{ch['end_page']}"
        for c in r.get("concepts", []):
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
                    "first_seen_page": page,
                    "mentioned_in_passages": [page_label],
                }
            else:
                e = agg[key]
                # Take longer canonical forms
                if len(vi) > len(e["canonical_vi"]):
                    e["canonical_vi"] = vi
                if zh and not e["canonical_zh"]:
                    e["canonical_zh"] = zh
                for a in (c.get("aliases") or []):
                    e["aliases"].add(a)
                note = (c.get("short_note") or "").strip()
                if len(note) > len(e["short_note"]):
                    e["short_note"] = note
                e["mentioned_in_passages"].append(page_label)
                e["first_seen_page"] = min(e["first_seen_page"], page)

    # 2. Commit each aggregated concept
    for key, e in agg.items():
        # Check existing in DB
        existing = cur.execute(
            "SELECT concept_id, aliases, mentioned_in_passages, short_note FROM concept_index "
            "WHERE canonical_zh=? AND canonical_vi=?",
            (e["canonical_zh"], e["canonical_vi"]),
        ).fetchone()
        if existing:
            # Merge — keep richer data
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
            # Add new corpus-page tags
            new_mentions = list(old_m) + [f"{corpus_id}:{m}" for m in e["mentioned_in_passages"]]
            new_mentions = list(dict.fromkeys(new_mentions))  # dedupe preserving order
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
            stats["merged"] += 1
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
                    json.dumps([f"{corpus_id}:{m}" for m in e["mentioned_in_passages"]], ensure_ascii=False),
                    e["short_note"][:500],
                    corpus_id,
                    e["first_seen_page"],
                    int(time.time()),
                ))
                stats["inserted"] += 1
            except sqlite3.IntegrityError:
                stats["merged"] += 1
    return stats


def commit_cases(con: sqlite3.Connection, chapters: list[dict], *, corpus_id: str) -> dict:
    """Commit case_studies. FK method_id: lookup by procedure relevance, fallback to 1st method
    of Thiệu Khang Tiết (existing 'Quan mai chiêm quyết')."""
    cur = con.cursor()
    stats = {"inserted": 0, "skipped_empty": 0}
    # Default method_id: Quan mai chiêm quyết (method_id=5 thường) — or first method by Thiệu Ung
    default_row = cur.execute(
        "SELECT method_id FROM methods WHERE name_zh='觀梅占訣' OR name_vi='Quan mai chiêm quyết' LIMIT 1"
    ).fetchone()
    default_method_id = default_row[0] if default_row else 1

    for ch in chapters:
        r = ch.get("result")
        if not r:
            continue
        page_label = f"{corpus_id}:p{ch['start_page']}-{ch['end_page']}"
        for cs in r.get("case_studies", []):
            event = (cs.get("historical_event") or "").strip()
            if not event:
                stats["skipped_empty"] += 1
                continue
            cur.execute("""
                INSERT INTO case_studies
                (method_id, historical_event, inputs_recorded, output_predicted,
                 output_actual, accuracy_score, source_book, created_at)
                VALUES (?,?,?,?,?,?,?,?)
            """, (
                default_method_id,
                event[:500],
                (cs.get("inputs_recorded") or "")[:500],
                (cs.get("output_predicted") or "")[:500],
                (cs.get("output_actual") or "")[:500],
                0.0,
                page_label,
                int(time.time()),
            ))
            stats["inserted"] += 1
    return stats


def commit_all(staging_path: str | Path, *, corpus_id: str = "thieu-khang-tiet-tq",
               db_path: Path = WIKI_DB) -> dict:
    state = json.loads(Path(staging_path).read_text())
    chapters = state.get("chapters", [])
    if not chapters:
        return {"error": "empty staging"}

    con = sqlite3.connect(db_path)
    try:
        author_id = lookup_author_id(con, "邵雍")
        if not author_id:
            return {"error": "Thiệu Ung (邵雍) không có trong authors. Cần seed_master trước."}
        work_id = lookup_work_id(con, corpus_id)
        if not work_id:
            return {"error": f"Work với corpus_id={corpus_id} không có trong works."}

        print(f"📚 Commit vào author_id={author_id} (Thiệu Ung), work_id={work_id} ({corpus_id})")
        print()
        results = {
            "passages": commit_passages(con, chapters, author_id=author_id, corpus_id=corpus_id),
            "methods": commit_methods(con, chapters, author_id=author_id, corpus_id=corpus_id),
            "concepts": commit_concepts(con, chapters, corpus_id=corpus_id),
            "case_studies": commit_cases(con, chapters, corpus_id=corpus_id),
        }
        con.commit()
        return results
    finally:
        con.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", default="/Users/ozvietnamdesktop/Desktop/yi/data/_logs/extract-tq-staging.json")
    ap.add_argument("--corpus", default="thieu-khang-tiet-tq")
    args = ap.parse_args()
    results = commit_all(args.staging, corpus_id=args.corpus)
    print(json.dumps(results, indent=2, ensure_ascii=False))
