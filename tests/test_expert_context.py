"""RAG grounding cho council sage — bơm tri thức sâu trích sách vào prompt."""
from pathlib import Path

import pytest

from engine.ai.agents import _user_message_for_agent
from engine.ai.expert_context import build_expert_context

_WIKI_DB = Path("data/yi_wiki/wiki.sqlite3")


def test_empty_question_returns_blank():
    assert build_expert_context("", "tu_vi") == ""
    assert build_expert_context("   ", "tu_vi") == ""


def test_grounds_with_book_quotes_when_db_present():
    """Có wiki.sqlite3 → block có trích sách (>); không có DB → '' (best-effort, không vỡ)."""
    block = build_expert_context("Vận sự nghiệp công danh tài lộc của tôi thế nào?", "tu_vi")
    assert isinstance(block, str)
    if block:
        assert "TRI THỨC SÂU" in block and ">" in block


def test_user_message_injects_expert_context_and_cites():
    msg = _user_message_for_agent(
        question="Q", chart_data={"a": 1},
        expert_context="## TRI THỨC SÂU TỪ SÁCH\n- > trích nguyên văn")
    assert "TRI THỨC SÂU" in msg and "DẪN cụ thể" in msg


def test_user_message_without_expert_context_unchanged():
    msg = _user_message_for_agent(question="Q", chart_data={"a": 1})
    assert "TRI THỨC SÂU" not in msg
    assert "dựa CHỈ trên dữ liệu chart" in msg


def test_challenge_round_skips_expert_block():
    """Vòng phản biện (có challenges) → KHÔNG bơm expert (tập trung chất vấn)."""
    msg = _user_message_for_agent(
        question="Q", chart_data={"a": 1}, challenges="Phản biện X",
        expert_context="## TRI THỨC SÂU TỪ SÁCH\n- > trích")
    assert "CHẤT VẤN" in msg


# ─────────────────────────────────────────────────────────────
# Iron #9 / M0-C: CHẶN RÒ atom Anh đã bác (founder_verified = -1) vào council
# ─────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _WIKI_DB.exists(), reason="cần wiki.sqlite3 (integration)")
def test_rejected_atoms_excluded_but_unverified_still_retrieved():
    """search_atom_fts (đường council lấy atom): LOẠI -1, GIỮ 0 (và 1 nếu có).

    Bảo đảm 3 điều cùng lúc:
    - atom Anh đã bác (founder_verified = -1) KHÔNG còn trong kết quả retrieval
    - atom chưa duyệt (0) VẪN vào (nếu require dương → council rỗng vì 0 atom duyệt dương)
    - council KHÔNG rỗng (vẫn có atom để bơm)
    """
    import sqlite3

    from engine.atomization.retriever import ChunkAtomRetriever

    # Tiền đề: DB có atom -1 VÀ atom -1 đó FTS-matchable (nếu không, test vô nghĩa).
    conn = sqlite3.connect(str(_WIKI_DB))
    conn.row_factory = sqlite3.Row
    try:
        n_rejected = conn.execute(
            "SELECT COUNT(*) c FROM atomic_questions WHERE founder_verified = -1"
        ).fetchone()["c"]
        leakable = conn.execute(
            """SELECT aq.atom_id FROM atomic_questions_fts
               JOIN atomic_questions aq ON aq.atom_id = atomic_questions_fts.rowid
               WHERE atomic_questions_fts MATCH ? AND aq.founder_verified = -1""",
            ('"cô quân"',),
        ).fetchall()
    finally:
        conn.close()

    if n_rejected == 0 or not leakable:
        pytest.skip("DB hiện không có atom -1 FTS-matchable để kiểm rò")

    rejected_ids = {r["atom_id"] for r in leakable}

    r = ChunkAtomRetriever(_WIKI_DB)
    hits = r.search_atom_fts("cô quân Tử Vi cách cục", limit=50)

    # (1) Không atom -1 nào lọt
    assert all(h.founder_verified >= 0 for h in hits), "atom -1 vẫn lọt vào retrieval"
    hit_ids = {h.atom_id for h in hits}
    assert hit_ids.isdisjoint(rejected_ids), f"atom Anh bác bị rò: {hit_ids & rejected_ids}"

    # (2) atom chưa duyệt (0) vẫn vào → KHÔNG require dương
    assert any(h.founder_verified == 0 for h in hits), "atom chưa-duyệt (0) bị loại oan"

    # (3) council KHÔNG rỗng
    assert len(hits) > 0, "council rỗng — filter quá tay"


@pytest.mark.skipif(not _WIKI_DB.exists(), reason="cần wiki.sqlite3 (integration)")
def test_expert_context_nonempty_after_filter():
    """build_expert_context (đường thật council gọi) vẫn có trích sách sau khi lọc -1."""
    block = build_expert_context("cô quân Tử Vi cách cục đại hạn lưu niên", "tu_vi")
    assert isinstance(block, str)
    assert block, "council rỗng sau filter — KHÔNG được require verified-dương"
    assert "TRI THỨC SÂU" in block and ">" in block
