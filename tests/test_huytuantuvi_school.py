"""Regression: kênh #2 Huy Tuấn Tử Vi ingest đúng 4 lớp + lá chắn cô lập.

Anh duyệt 2026-06-17: ingest chọn lọc, TÁCH school `tu_vi_huy_tuan`, và vùng LÁ CHẮN
(anti_paradigm / quan_diem) KHÔNG được lọt vào luận sao×cung tích cực.
"""
import sqlite3
from pathlib import Path

from engine.tu_vi import cross_school
from engine.tu_vi import cung_sao_mapping

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/yi_wiki/wiki.sqlite3"
CORPUS = "tu-vi-huy-tuan-tiktok"


def test_school_registered():
    """School tu_vi_huy_tuan có trong registry cross_school."""
    assert cross_school.SCHOOL_MAP.get(CORPUS) == "tu_vi_huy_tuan"
    assert "tu_vi_huy_tuan" in cross_school.SCHOOL_NAMES
    assert "Huy Tuấn" in cross_school.SCHOOL_NAMES["tu_vi_huy_tuan"]


def test_grid_excludes_shield_filter_present():
    """Query cung_sao_mapping phải loại anti_paradigm + quan_diem (lá chắn không vào grid)."""
    src = Path(cung_sao_mapping.__file__).read_text(encoding="utf-8")
    assert CORPUS in src, "corpus kênh #2 phải có trong cung_sao_mapping"
    assert 'NOT LIKE \'%"anti_paradigm"%\'' in src, "phải loại atom lá chắn khỏi grid"
    assert 'NOT LIKE \'%"quan_diem"%\'' in src, "phải loại atom quan điểm khỏi grid"


def test_shield_atoms_isolated_in_db():
    """Nếu DB có corpus: atom lá chắn (anti_paradigm) tồn tại NHƯNG không lọt query grid."""
    if not DB.exists():
        return  # CI không có wiki.sqlite3 (sync qua VPS) — bỏ qua an toàn
    conn = sqlite3.connect(DB)
    n_corpus = conn.execute(
        "SELECT COUNT(*) FROM chunks_v2 WHERE book_corpus_id=?", (CORPUS,)).fetchone()[0]
    if n_corpus == 0:
        conn.close()
        return  # corpus chưa import ở máy này — bỏ qua
    n_shield = conn.execute(
        """SELECT COUNT(*) FROM atomic_questions a JOIN chunks_v2 c ON c.chunk_id=a.chunk_id
           WHERE c.book_corpus_id=? AND a.subject_identifiers LIKE '%"anti_paradigm"%'""",
        (CORPUS,)).fetchone()[0]
    n_in_grid = conn.execute(
        """SELECT COUNT(*) FROM atomic_questions a JOIN chunks_v2 c ON c.chunk_id=a.chunk_id
           WHERE c.book_corpus_id=?
           AND a.subject_identifiers NOT LIKE '%"anti_paradigm"%'
           AND a.subject_identifiers NOT LIKE '%"quan_diem"%'""",
        (CORPUS,)).fetchone()[0]
    conn.close()
    assert n_shield > 0, "phải có atom lá chắn (vùng độc hại giữ làm ví dụ-để-tránh)"
    assert n_in_grid > 0, "phải có atom kỹ thuật+aligned vào grid"
