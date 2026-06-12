#!/usr/bin/env python3
"""Ingest MỘT vòng đọc sâu (20 trang) vào wiki — đi cùng skill doc-sau-20-trang.

Mỗi vòng: 1 chunk (text 20 trang) + atoms em đúc kết (file JSON) → wiki.sqlite3.
Idempotent theo (corpus, from_page, to_page): chạy lại sẽ thay vòng đó.

Atoms file format (mảng):
[
  {"q": "câu hỏi", "quote": "trích nguyên văn / đúc kết", "subj": {"chu_de": ["ngu_hanh"], ...},
   "cat": "adnh_nen_tang", "confidence": 0.85}
]

Usage:
  .venv/bin/python3 scripts/ingest_reading_round.py \
    --corpus hoc-thuyet-am-duong-ngu-hanh \
    --book-dir data/restored_books/hoc-thuyet-am-duong-ngu-hanh-le-van-suu \
    --author "Lê Văn Sửu" --tier 3 \
    --from-page 1 --to-page 20 \
    --atoms /tmp/vong1_atoms.json
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/yi_wiki/wiki.sqlite3"
EXTRACTED_BY = "doc-sau-20-trang"


def pages_text(content_md: Path, from_page: int, to_page: int) -> str:
    """Cắt text các trang [from_page, to_page] theo marker <!-- page N -->."""
    raw = content_md.read_text(encoding="utf-8")
    parts = re.split(r"<!-- page (\d+) -->", raw)
    # parts: [preamble, num, text, num, text...]
    out = []
    for i in range(1, len(parts), 2):
        num = int(parts[i])
        if from_page <= num <= to_page:
            out.append(f"[trang {num}]\n{parts[i + 1].strip()}")
    return "\n\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--book-dir", required=True)
    ap.add_argument("--author", required=True)
    ap.add_argument("--tier", type=int, default=3)
    ap.add_argument("--from-page", type=int, required=True)
    ap.add_argument("--to-page", type=int, required=True)
    ap.add_argument("--atoms", required=True, help="file JSON atoms đúc kết")
    ap.add_argument("--summary", default="", help="1 dòng tóm vòng (cho chunk.summary)")
    args = ap.parse_args()

    book_dir = ROOT / args.book_dir
    text = pages_text(book_dir / "content.md", args.from_page, args.to_page)
    if len(text) < 500:
        raise SystemExit(f"Text vòng quá ngắn ({len(text)} chars) — kiểm tra page markers.")
    atoms = json.loads(Path(args.atoms).read_text(encoding="utf-8"))
    if not isinstance(atoms, list) or not atoms:
        raise SystemExit("File atoms rỗng / sai định dạng.")

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Author (idempotent)
    row = cur.execute("SELECT author_id FROM authors WHERE name_vi=?", (args.author,)).fetchone()
    if row:
        author_id = row["author_id"]
    else:
        cur.execute(
            "INSERT INTO authors (name_vi, tier_in_lineage, era, created_at) VALUES (?,?,?,?)",
            (args.author, args.tier, "hiện đại VN", int(time.time())),
        )
        author_id = cur.lastrowid
        print(f"✅ Thêm author '{args.author}' (id={author_id})")

    # Thay vòng cũ nếu có (idempotent)
    old = cur.execute(
        "SELECT chunk_id FROM chunks_v2 WHERE book_corpus_id=? AND page_start=? AND page_end=?",
        (args.corpus, args.from_page, args.to_page),
    ).fetchall()
    if old:
        ids = [r["chunk_id"] for r in old]
        qs = ",".join("?" * len(ids))
        cur.execute(f"DELETE FROM atomic_questions WHERE chunk_id IN ({qs})", ids)
        cur.execute(f"DELETE FROM chunks_v2 WHERE chunk_id IN ({qs})", ids)
        print(f"♻️  Thay vòng cũ ({len(ids)} chunk)")

    cur.execute(
        """INSERT INTO chunks_v2 (book_corpus_id, author_id, page_start, page_end,
           section_path, text, summary, metadata_json, created_at)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (args.corpus, author_id, args.from_page, args.to_page,
         f"vong-p{args.from_page:03d}-p{args.to_page:03d}", text,
         args.summary or f"Vòng đọc sâu p{args.from_page}-{args.to_page}",
         json.dumps({"reading_discipline": "doc-sau-20-trang"}, ensure_ascii=False),
         int(time.time())),
    )
    chunk_id = cur.lastrowid

    n = 0
    for a in atoms:
        cur.execute(
            """INSERT INTO atomic_questions
               (chunk_id, question_text, question_lang, from_category,
                subject_identifiers, source_quote, confidence, extracted_by, section_id)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (chunk_id, a["q"], "vi", a.get("cat", "doc_sau"),
             json.dumps(a.get("subj", {}), ensure_ascii=False),
             (a.get("quote") or "")[:2000],
             a.get("confidence", 0.85), EXTRACTED_BY, "doc_sau_vong"),
        )
        n += 1
    conn.commit()
    total = cur.execute(
        "SELECT COUNT(*) FROM atomic_questions a JOIN chunks_v2 c ON c.chunk_id=a.chunk_id WHERE c.book_corpus_id=?",
        (args.corpus,),
    ).fetchone()[0]
    conn.close()
    print(f"✅ Vòng p{args.from_page}-{args.to_page}: 1 chunk ({len(text):,} chars) + {n} atoms "
          f"(corpus {args.corpus} tổng: {total} atoms)")


if __name__ == "__main__":
    main()
