"""Backfill embeddings cho atomic_questions → atom_vec (sqlite-vec).

Mirror pattern của WikiStore.backfill_embeddings (passages → passages_vec):
- embed_texts (LM Studio nomic 768-dim) qua engine.yi_wiki.embeddings
- INSERT OR REPLACE vào atom_vec (vec0)
- idempotent: chỉ embed atom CHƯA có vector (LEFT JOIN atom_vec)
- batch 64, retry nhẹ mỗi batch

Text số hoá mỗi atom = question_text + source_quote (+ viet_thuan nếu có
commentary chưa bị bác). busy_timeout=30000.

LƯU Ý dim: atom_vec gốc tạo FLOAT[1536] (kế hoạch OpenAI cũ) nhưng RỖNG; embedder
thực tế = nomic 768-dim (giống passages_vec). Script tự sửa atom_vec về đúng
EMBED_DIM nếu lệch (chỉ khi bảng rỗng — an toàn).

Usage:
  .venv/bin/python3 scripts/backfill_atom_embeddings.py [--limit N] [--with-concepts]
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import sqlite_vec  # noqa: E402

from engine.yi_wiki.embeddings import (  # noqa: E402
    EMBED_DIM,
    embed_one,
    embed_texts,
    is_available,
)

DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
BATCH = 64
MAX_RETRY = 3


def _open(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA busy_timeout=30000")
    conn.row_factory = sqlite3.Row
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn


def _vec_dim(conn: sqlite3.Connection, table: str) -> int | None:
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE name=?", (table,)
    ).fetchone()
    if not row or not row["sql"]:
        return None
    import re

    m = re.search(r"FLOAT\[(\d+)\]", row["sql"])
    return int(m.group(1)) if m else None


def ensure_vec_table(conn: sqlite3.Connection, table: str, id_col: str) -> None:
    """Tạo bảng vec0 nếu chưa có. Nếu đã có nhưng SAI dim và RỖNG → drop+recreate
    về đúng EMBED_DIM (an toàn vì rỗng). Nếu sai dim mà CÓ dữ liệu → raise."""
    dim = _vec_dim(conn, table)
    if dim is None:
        conn.execute(
            f"CREATE VIRTUAL TABLE {table} USING vec0("
            f"{id_col} INTEGER PRIMARY KEY, embedding FLOAT[{EMBED_DIM}])"
        )
        conn.commit()
        return
    if dim != EMBED_DIM:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        if cnt > 0:
            raise SystemExit(
                f"❌ {table} dim={dim} ≠ EMBED_DIM={EMBED_DIM} nhưng có {cnt} dòng. "
                "Không tự drop bảng có dữ liệu — cần xử lý tay."
            )
        print(f"   ⚠ {table} dim={dim} ≠ {EMBED_DIM}, rỗng → recreate về {EMBED_DIM}")
        conn.execute(f"DROP TABLE {table}")
        conn.execute(
            f"CREATE VIRTUAL TABLE {table} USING vec0("
            f"{id_col} INTEGER PRIMARY KEY, embedding FLOAT[{EMBED_DIM}])"
        )
        conn.commit()


def _embed_with_retry(texts: list[str]) -> list[list[float]] | None:
    for attempt in range(1, MAX_RETRY + 1):
        vecs = embed_texts(texts)
        if vecs:
            return vecs
        if attempt < MAX_RETRY:
            time.sleep(1.5 * attempt)
    return None


def backfill_atoms(conn: sqlite3.Connection, limit: int | None) -> dict:
    ensure_vec_table(conn, "atom_vec", "atom_id")
    # Gom text mỗi atom: question_text + source_quote + viet_thuan (commentary chưa bác).
    sql = """
        SELECT aq.atom_id,
               aq.question_text,
               aq.source_quote,
               ac.viet_thuan
        FROM atomic_questions aq
        LEFT JOIN atom_vec v ON v.atom_id = aq.atom_id
        LEFT JOIN atom_commentaries ac
               ON ac.atom_id = aq.atom_id AND ac.founder_verified >= 0
        WHERE v.atom_id IS NULL
          AND aq.question_text IS NOT NULL AND aq.question_text != ''
        ORDER BY aq.atom_id
    """
    if limit:
        sql += f" LIMIT {int(limit)}"
    todo = conn.execute(sql).fetchall()
    total = len(todo)
    print(f"   📐 atom_vec dim={_vec_dim(conn, 'atom_vec')} · cần embed: {total}")

    done = 0
    failed_batches = 0
    for i in range(0, total, BATCH):
        chunk = todo[i:i + BATCH]
        texts = []
        for r in chunk:
            parts = [r["question_text"] or ""]
            if r["source_quote"]:
                parts.append(r["source_quote"])
            if r["viet_thuan"]:
                parts.append(r["viet_thuan"])
            texts.append(" \n".join(p for p in parts if p)[:2000])
        vecs = _embed_with_retry(texts)
        if not vecs or len(vecs) != len(chunk):
            failed_batches += 1
            print(f"   ⚠ batch {i//BATCH} fail (embedder) — skip")
            continue
        for row, vec in zip(chunk, vecs):
            conn.execute(
                "INSERT OR REPLACE INTO atom_vec(atom_id, embedding) VALUES (?, ?)",
                (row["atom_id"], json.dumps(vec)),
            )
        conn.commit()
        done += len(chunk)
        if (i // BATCH) % 20 == 0:
            print(f"      … {done}/{total}")
    return {"total_todo": total, "embedded": done, "failed_batches": failed_batches}


def backfill_concepts(conn: sqlite3.Connection, limit: int | None) -> dict:
    """Optional: embed concept_index vào concept_vec (canonical_vi + zh + short_note)."""
    ensure_vec_table(conn, "concept_vec", "concept_id")
    sql = """
        SELECT c.concept_id, c.canonical_vi, c.canonical_zh, c.short_note
        FROM concept_index c
        LEFT JOIN concept_vec v ON v.concept_id = c.concept_id
        WHERE v.concept_id IS NULL
          AND c.canonical_vi IS NOT NULL AND c.canonical_vi != ''
        ORDER BY c.concept_id
    """
    if limit:
        sql += f" LIMIT {int(limit)}"
    todo = conn.execute(sql).fetchall()
    total = len(todo)
    print(f"   📐 concept_vec dim={_vec_dim(conn, 'concept_vec')} · cần embed: {total}")
    done = 0
    for i in range(0, total, BATCH):
        chunk = todo[i:i + BATCH]
        texts = [
            " \n".join(
                p for p in (r["canonical_vi"], r["canonical_zh"], r["short_note"]) if p
            )[:2000]
            for r in chunk
        ]
        vecs = _embed_with_retry(texts)
        if not vecs or len(vecs) != len(chunk):
            print(f"   ⚠ concept batch {i//BATCH} fail — skip")
            continue
        for row, vec in zip(chunk, vecs):
            conn.execute(
                "INSERT OR REPLACE INTO concept_vec(concept_id, embedding) VALUES (?, ?)",
                (row["concept_id"], json.dumps(vec)),
            )
        conn.commit()
        done += len(chunk)
    return {"total_todo": total, "embedded": done}


def verify(conn: sqlite3.Connection) -> dict:
    out = {}
    out["atom_vec_count"] = conn.execute("SELECT COUNT(*) FROM atom_vec").fetchone()[0]
    out["atomic_questions_count"] = conn.execute(
        "SELECT COUNT(*) FROM atomic_questions"
    ).fetchone()[0]
    try:
        out["concept_vec_count"] = conn.execute(
            "SELECT COUNT(*) FROM concept_vec"
        ).fetchone()[0]
    except sqlite3.Error:
        out["concept_vec_count"] = None

    # Semantic search demo: 1 câu mệnh
    q = "Người này có tài hùng biện, ăn nói giỏi không?"
    qvec = embed_one(q)
    sample = []
    if qvec is not None and out["atom_vec_count"] > 0:
        rows = conn.execute(
            """SELECT v.atom_id, v.distance, aq.question_text, aq.source_quote
               FROM atom_vec v
               JOIN atomic_questions aq ON aq.atom_id = v.atom_id
               WHERE v.embedding MATCH ? AND k = 5
               ORDER BY v.distance""",
            (json.dumps(qvec),),
        ).fetchall()
        for r in rows:
            sample.append({
                "atom_id": r["atom_id"],
                "distance": round(r["distance"], 4),
                "question": (r["question_text"] or "")[:90],
            })
    out["semantic_query"] = q
    out["semantic_sample"] = sample
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--with-concepts", action="store_true")
    args = ap.parse_args()

    if not is_available():
        raise SystemExit("❌ Embedder không phản hồi (LM Studio :1234). Bật rồi chạy lại.")

    conn = _open(DB_PATH)
    try:
        print("▶ Backfill atom_vec (atomic_questions)…")
        a = backfill_atoms(conn, args.limit)
        print("  →", a)
        if args.with_concepts:
            print("▶ Backfill concept_vec (concept_index)…")
            c = backfill_concepts(conn, args.limit)
            print("  →", c)
        print("▶ Verify…")
        v = verify(conn)
        print(json.dumps(v, ensure_ascii=False, indent=2))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
