"""Cast — định vị thời cuộc + trích dẫn tri thức từ kho atoms Hoàng Cực.

cast_hoang_cuc(year, with_atoms=True) → vị trí Nguyên-Hội-Vận-Thế
+ atoms liên quan (FTS trên kho 7.154 atoms đã đúc từ chính sách)
+ khung luận giải paradigm-safe (đọc đồng dạng — không predict).
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from . import METHOD_ID, SOURCE_REF
from .nguyen_hoi_van_the import locate_year

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
CORPUS = "hoang-cuc-kinh-the-thuong"


def _related_atoms(terms: list[str], limit: int = 6) -> list[dict]:
    """FTS atoms Hoàng Cực theo cụm thuật ngữ (vd 'hội Ngọ', 'nguyên hội vận thế')."""
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    seen: set[int] = set()
    out: list[dict] = []
    for term in terms:
        safe = " ".join(re.sub(r'["\'\^\*\(\)]', " ", term).split())
        if not safe:
            continue
        try:
            rows = conn.execute(
                """SELECT aq.atom_id, aq.question_text, aq.source_quote, c.page_start
                   FROM atomic_questions_fts f
                   JOIN atomic_questions aq ON aq.atom_id = f.rowid
                   JOIN chunks_v2 c ON c.chunk_id = aq.chunk_id
                   WHERE atomic_questions_fts MATCH ? AND c.book_corpus_id = ?
                   ORDER BY rank LIMIT ?""",
                (safe, CORPUS, limit)).fetchall()
        except sqlite3.OperationalError:
            continue
        for r in rows:
            if r["atom_id"] in seen:
                continue
            seen.add(r["atom_id"])
            out.append({
                "atom_id": r["atom_id"],
                "question": r["question_text"],
                "quote": (r["source_quote"] or "")[:200],
                "page": r["page_start"],
            })
        if len(out) >= limit:
            break
    conn.close()
    return out[:limit]


def cast_hoang_cuc(year: int, with_atoms: bool = True) -> dict:
    """Định vị thời cuộc cho 1 năm. Paradigm: quan-thời-trace-cấu-trúc, không predict."""
    loc = locate_year(year)
    result = {
        "method": METHOD_ID,
        "source": SOURCE_REF,
        "vi_tri": loc,
        "paradigm_note": (
            "Đọc đồng dạng (Iron Rule #4/#6): vị trí này phản chiếu CẤU TRÚC thời đoạn "
            "trong chu kỳ lớn — không phải lời đoán cát hung. "
            "Quan vật là quán cái LẼ của thời, đặt việc người vào dòng trời đất."
        ),
    }
    if with_atoms:
        hoi_chi = loc["hoi"]["chi"]
        result["atoms_lien_quan"] = _related_atoms([
            f"hội {hoi_chi}", "nguyên hội vận thế", "kinh thế", "vận thế",
        ])
    return result
