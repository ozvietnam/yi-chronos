#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_semantic_edges_obsidian.py — THÊM CẠNH NGỮ-NGHĨA (semantic edges) vào đồ thị
Obsidian đã dựng bởi build_obsidian_graph.py.

Khác build_obsidian_graph.py (xoá + dựng lại toàn bộ OUT): script NÀY là
POST-PROCESSOR — chỉ THÊM 1 mục '## 🔗 Gần nghĩa' vào CUỐI mỗi note khái niệm
ĐÃ TỒN TẠI, KHÔNG đụng phần cấu trúc (frontmatter, body, các **edge:** cũ).

Quan hệ ngữ-nghĩa = nomic embedding (LM Studio :1234) → cosine top-5.
  • Nguồn vector: bảng concept_vec (vec0, FLOAT[768]) trong wiki.sqlite3.
    TÁI DÙNG embedding có sẵn; CHỈ embed concept nào còn THIẾU (idempotent).
  • Top-5 concept gần nghĩa nhất / concept (loại chính nó).

AN TOÀN:
  • CHỈ link tới note ĐÃ TỒN TẠI trên đĩa (đọc ground-truth filename).
  • KHÔNG trùng link cấu trúc đã có (parse các **edge:** sẵn trong note).
  • Idempotent: chạy lại thay nguyên mục '## 🔗 Gần nghĩa' (regex), không nhân đôi.
  • Embedder lỗi → THOÁT SẠCH (exit code 0, không sửa file nào).

Usage:
  .venv/bin/python3 scripts/add_semantic_edges_obsidian.py [--topk 5] [--limit N] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
DB = ROOT / "data/yi_wiki/wiki.sqlite3"
OUT = ROOT / "thư viện sách/🧠 Mạng Tri Thức YI"
F_CONCEPT = OUT / "03 · Khái niệm"

sys.path.insert(0, str(ROOT))

# Reuse the EXACT sanitizer the graph builder used → titles match 1:1.
from scripts.build_obsidian_graph import safe_name  # noqa: E402
from engine.yi_wiki.embeddings import embed_texts, is_available, EMBED_DIM  # noqa: E402

SECTION_HEADER = "## 🔗 Gần nghĩa"
# Match an existing section so re-runs replace (not append) → idempotent.
# Section runs from the header to the next '## ' header or EOF.
_SECTION_RE = re.compile(
    r"\n*## 🔗 Gần nghĩa\b.*?(?=\n## |\Z)", re.DOTALL
)
# Pull every [[target]] already present (structure edges) to avoid duplicating.
_WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+?)(?:\|[^\]]*)?\]\]")


def load_vec_db() -> sqlite3.Connection | None:
    try:
        import sqlite_vec
    except Exception:
        return None
    db = sqlite3.connect(str(DB))
    db.row_factory = sqlite3.Row
    try:
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)
        db.execute("SELECT vec_version()").fetchone()
    except Exception:
        db.close()
        return None
    return db


def ensure_concept_vec(db: sqlite3.Connection):
    db.execute(
        f"CREATE VIRTUAL TABLE IF NOT EXISTS concept_vec "
        f"USING vec0(concept_id INTEGER PRIMARY KEY, embedding FLOAT[{EMBED_DIM}])"
    )


def backfill_concept_embeddings(db: sqlite3.Connection, batch: int = 64) -> int:
    """Embed concepts (canonical_vi + short_note) NOT yet in concept_vec. Idempotent."""
    rows = db.execute(
        "SELECT c.concept_id, c.canonical_vi, c.short_note "
        "FROM concept_index c LEFT JOIN concept_vec v ON v.concept_id = c.concept_id "
        "WHERE v.concept_id IS NULL AND c.canonical_vi != '' ORDER BY c.concept_id"
    ).fetchall()
    done = 0
    for i in range(0, len(rows), batch):
        chunk = rows[i:i + batch]
        texts = []
        for r in chunk:
            note = (r["short_note"] or "").strip()
            t = r["canonical_vi"] + (("\n" + note) if note else "")
            texts.append(t[:2000])
        vecs = embed_texts(texts)
        if not vecs:
            # embedder died mid-run → stop cleanly, keep what we have
            break
        for r, vec in zip(chunk, vecs):
            db.execute(
                "INSERT OR REPLACE INTO concept_vec(concept_id, embedding) VALUES (?, ?)",
                (r["concept_id"], json.dumps(vec)),
            )
        db.commit()
        done += len(chunk)
    return done


def build_note_index() -> dict[str, Path]:
    """Real on-disk stem (case-EXACT) -> path. Keyed by casefold too so we always
    recover the TRUE filename casing (macOS FS is case-insensitive; Path.exists()
    on a mis-cased name lies — we must read the actual stem from iterdir)."""
    idx: dict[str, Path] = {}
    for p in F_CONCEPT.rglob("*.md"):
        idx[p.stem] = p
        idx.setdefault("\x00cf\x00" + p.stem.casefold(), p)  # casefold fallback key
    return idx


def resolve_concept_note(
    concept_id: int, school: str, canonical_vi: str, note_index: dict[str, Path]
) -> Path | None:
    """Map a concept to its ACTUAL note file (case-exact path from disk), mirroring
    build_obsidian_graph's title rule: base = safe_name(canonical_vi); on
    case-insensitive FS collision the builder suffixed ' (id<concept_id>)'."""
    base = safe_name(canonical_vi)
    disamb = f"{base} (id{concept_id})"
    # Prefer exact-cased disk stem; else casefold-recovered real path.
    for key in (base, disamb):
        if key in note_index:
            return note_index[key]
        cf = note_index.get("\x00cf\x00" + key.casefold())
        if cf is not None:
            return cf
    return None


def existing_links(text: str) -> set[str]:
    """All wikilink targets already in the note BODY (structure edges)."""
    # Strip any prior semantic section first so its links don't count as "existing".
    body = _SECTION_RE.sub("", text)
    return {safe_name(m.group(1).strip()) for m in _WIKILINK_RE.finditer(body)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--limit", type=int, default=None, help="cap concepts processed (debug)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not OUT.exists():
        print(json.dumps({"status": "no_graph", "msg": "Chưa dựng đồ thị (chạy build_obsidian_graph.py trước)."}, ensure_ascii=False))
        return 0

    # ── Embedder gate: lỗi → thoát sạch, KHÔNG phá đồ thị cấu trúc. ──
    if not is_available():
        print(json.dumps({"status": "no_embedder", "concepts_embedded": 0, "edges_added": 0,
                          "msg": "LM Studio embedder không phản hồi — bỏ qua sạch sẽ."}, ensure_ascii=False))
        return 0

    db = load_vec_db()
    if db is None:
        print(json.dumps({"status": "no_sqlite_vec", "concepts_embedded": 0, "edges_added": 0}, ensure_ascii=False))
        return 0

    ensure_concept_vec(db)
    embedded = backfill_concept_embeddings(db)

    # All concepts (id, school, vi) — to map id → note.
    concepts = db.execute(
        "SELECT concept_id, canonical_vi, short_note, school FROM concept_index "
        "WHERE canonical_vi != '' ORDER BY concept_id"
    ).fetchall()
    note_index = build_note_index()

    # concept_id → ground-truth note title (stem) + path; and reverse for KNN target titles.
    id_to_path: dict[int, Path] = {}
    id_to_title: dict[int, str] = {}
    for r in concepts:
        p = resolve_concept_note(r["concept_id"], r["school"], r["canonical_vi"], note_index)
        if p is not None:
            id_to_path[r["concept_id"]] = p
            id_to_title[r["concept_id"]] = p.stem

    processed = list(id_to_path.items())
    if args.limit:
        processed = processed[: args.limit]

    edges_added = 0
    notes_touched = 0
    example = None
    k = args.topk

    for cid, path in processed:
        emb = db.execute("SELECT embedding FROM concept_vec WHERE concept_id=?", (cid,)).fetchone()
        if emb is None:
            continue
        # KNN: ask for k+1 to drop self.
        rows = db.execute(
            "SELECT concept_id, distance FROM concept_vec "
            "WHERE embedding MATCH ? AND k = ? ORDER BY distance",
            (emb["embedding"], k + 1),
        ).fetchall()

        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        already = existing_links(text)
        self_title = id_to_title.get(cid)

        neigh_titles: list[str] = []
        seen = set()
        for nr in rows:
            ncid = nr["concept_id"]
            if ncid == cid:
                continue
            ntitle = id_to_title.get(ncid)
            if not ntitle:
                continue  # neighbor has no existing note → skip (link only to existing)
            if ntitle == self_title:
                continue  # different concept_id collapsed to same note → no self-link
            if ntitle in already:
                continue  # already linked structurally → don't duplicate
            if ntitle in seen:
                continue
            seen.add(ntitle)
            neigh_titles.append(ntitle)
            if len(neigh_titles) >= k:
                break

        # Build the section. Always strip any previous one (idempotent).
        stripped = _SECTION_RE.sub("", text).rstrip()
        if neigh_titles:
            section = "\n\n" + SECTION_HEADER + "\n" + " · ".join(f"[[{t}]]" for t in neigh_titles) + "\n"
            new_text = stripped + section
        else:
            # nothing to link → just ensure no stale section remains
            new_text = stripped + "\n"

        if new_text != text:
            if not args.dry_run:
                path.write_text(new_text, encoding="utf-8")
            notes_touched += 1
        edges_added += len(neigh_titles)

        if example is None and len(neigh_titles) >= 1:
            example = {"concept": self_title, "gan_nghia": neigh_titles}

    db.close()
    result = {
        "status": "ok",
        "concepts_embedded_this_run": embedded,
        "concepts_with_note": len(id_to_path),
        "notes_touched": notes_touched,
        "semantic_edges_added": edges_added,
        "topk": k,
        "dry_run": args.dry_run,
        "vi_du": example,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
