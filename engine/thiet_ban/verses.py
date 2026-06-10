"""Verses — tra cứu điều văn Thiết Bản từ tabular_verses.

Mọi hàm trả dict/list JSON-serializable. Read-only — không ghi DB.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
CORPUS = "thiet-ban-than-so"

VOLUMES = ["子集", "丑集", "寅集", "卯集", "辰集", "巳集",
           "午集", "未集", "申集", "酉集", "戌集", "亥集"]
RE_CJK = re.compile(r"[一-鿿]")


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_dict(r: sqlite3.Row) -> dict:
    return {
        "seq_no": r["seq_no"],
        "volume": r["volume"],
        "zh": r["zh"],
        "vi": r["vi"],
        "age_marks": r["age_marks_raw"],
        "confidence": r["seq_confidence"],
        "page_pdf": r["page_pdf"],
    }


def get_verse(seq_no: int) -> dict | None:
    """Tra 1 điều theo số tuyệt đối (1001..12990)."""
    conn = _conn()
    r = conn.execute(
        """SELECT * FROM tabular_verses
           WHERE book_corpus_id=? AND seq_no=? ORDER BY verse_id LIMIT 1""",
        (CORPUS, seq_no)).fetchone()
    conn.close()
    return _row_to_dict(r) if r else None


def get_range(start: int, end: int, limit: int = 50) -> list[dict]:
    """Tra dải điều [start..end] (giới hạn 50/lần)."""
    end = min(end, start + limit - 1)
    conn = _conn()
    rows = conn.execute(
        """SELECT * FROM tabular_verses
           WHERE book_corpus_id=? AND seq_no BETWEEN ? AND ?
           ORDER BY seq_no""", (CORPUS, start, end)).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def search(q: str, limit: int = 20) -> dict:
    """Tìm điều văn: chữ Hán → LIKE trên zh (FTS5 unicode61 không tách CJK);
    tiếng Việt → FTS trên vi."""
    q = (q or "").strip()
    if not q:
        return {"query": q, "mode": "empty", "results": []}
    conn = _conn()
    if RE_CJK.search(q):
        mode = "zh-like"
        rows = conn.execute(
            """SELECT * FROM tabular_verses
               WHERE book_corpus_id=? AND zh LIKE ?
               ORDER BY seq_no LIMIT ?""",
            (CORPUS, f"%{q}%", limit)).fetchall()
    else:
        mode = "vi-fts"
        # escape FTS specials, match từng từ
        safe = " ".join(re.sub(r'["\'\^\*\(\)]', " ", q).split())
        rows = conn.execute(
            """SELECT tv.* FROM tabular_verses_fts f
               JOIN tabular_verses tv ON tv.verse_id = f.rowid
               WHERE tabular_verses_fts MATCH ? AND tv.book_corpus_id=?
               ORDER BY rank LIMIT ?""",
            (safe, CORPUS, limit)).fetchall()
    conn.close()
    return {"query": q, "mode": mode, "results": [_row_to_dict(r) for r in rows]}


def get_volume(tap: str, offset: int = 0, limit: int = 50) -> dict:
    """Liệt kê điều văn 1 tập (子集..亥集), phân trang."""
    conn = _conn()
    total = conn.execute(
        "SELECT COUNT(*) FROM tabular_verses WHERE book_corpus_id=? AND volume=?",
        (CORPUS, tap)).fetchone()[0]
    rows = conn.execute(
        """SELECT * FROM tabular_verses WHERE book_corpus_id=? AND volume=?
           ORDER BY seq_no LIMIT ? OFFSET ?""",
        (CORPUS, tap, limit, offset)).fetchall()
    conn.close()
    return {"volume": tap, "total": total, "offset": offset,
            "results": [_row_to_dict(r) for r in rows]}


def stats() -> dict:
    conn = _conn()
    total, with_vi = conn.execute(
        """SELECT COUNT(*), SUM(CASE WHEN vi IS NOT NULL AND vi != '' THEN 1 ELSE 0 END)
           FROM tabular_verses WHERE book_corpus_id=?""", (CORPUS,)).fetchone()
    by_conf = dict(conn.execute(
        """SELECT seq_confidence, COUNT(*) FROM tabular_verses
           WHERE book_corpus_id=? GROUP BY 1""", (CORPUS,)).fetchall())
    by_vol = dict(conn.execute(
        """SELECT COALESCE(volume,'?'), COUNT(*) FROM tabular_verses
           WHERE book_corpus_id=? GROUP BY 1 ORDER BY MIN(seq_no)""",
        (CORPUS,)).fetchall())
    lo, hi = conn.execute(
        "SELECT MIN(seq_no), MAX(seq_no) FROM tabular_verses WHERE book_corpus_id=?",
        (CORPUS,)).fetchone()
    conn.close()
    return {"total": total, "with_vi": with_vi, "seq_range": [lo, hi],
            "by_confidence": by_conf, "by_volume": by_vol, "volumes": VOLUMES}
