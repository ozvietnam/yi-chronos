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


# ─────────────────────────────────────────────────────────────
# GAP-1 (M1-A2): nối atom_commentaries (luận giải SÂU) vào council
# ─────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _WIKI_DB.exists(), reason="cần wiki.sqlite3 (integration)")
def test_retriever_attaches_commentary():
    """search_atom_fts gắn luận giải sâu (commentary) khi atom CÓ — không chỉ trích thô."""
    from engine.atomization.retriever import ChunkAtomRetriever

    r = ChunkAtomRetriever(_WIKI_DB)
    hits = r.search_atom_fts("Tử Vi cách cục phái Trung Châu hộ giá", limit=20)
    assert hits, "không có hit nào để kiểm"
    with_comm = [h for h in hits if h.commentary]
    assert with_comm, "không atom nào kèm luận giải sâu — JOIN atom_commentaries hỏng"
    # commentary phải chứa ít nhất 1 field giàu, không rỗng
    for h in with_comm:
        assert isinstance(h.commentary, dict) and h.commentary
        assert any(
            (h.commentary.get(k) or "")
            for k in ("viet_thuan", "nguyen_ly", "han_viet_explain",
                      "vi_du_doi_song", "cross_school_notes", "iron_rule_warning")
        ), f"commentary atom {h.atom_id} rỗng — phải lọc field rỗng"


@pytest.mark.skipif(not _WIKI_DB.exists(), reason="cần wiki.sqlite3 (integration)")
def test_expert_context_contains_deep_commentary():
    """build_expert_context giờ chứa LUẬN GIẢI SÂU (Việt thuần / Nguyên lý) — luận sâu,
    không chỉ trích thô. Vẫn không rỗng."""
    block = build_expert_context("Tử Vi cách cục phái Trung Châu hộ giá", "tu_vi")
    assert block, "council rỗng"
    assert "TRI THỨC SÂU" in block
    # Phải có ÍT NHẤT 1 nhãn lớp luận giải sâu (chứng tỏ commentary đã được bơm)
    assert any(label in block for label in (
        "Việt thuần:", "Nguyên lý:", "Đối chiếu phái:", "Hán-Việt cốt:",
    )), "expert context KHÔNG có luận giải sâu — vẫn chỉ trích thô"
    # Header phản ánh có luận giải đã thẩm
    assert "LUẬN GIẢI SÂU" in block


def test_commentary_rejected_minus1_excluded(tmp_path):
    """Commentary founder_verified = -1 KHÔNG được rò vào context (Iron #9), nhưng
    atom vẫn ra với trích thô. Dựng DB tối thiểu để kiểm tất định."""
    import sqlite3

    from engine.atomization.retriever import ChunkAtomRetriever

    db = tmp_path / "mini.sqlite3"
    conn = sqlite3.connect(str(db))
    conn.executescript(
        """
        CREATE TABLE chunks_v2 (
            chunk_id INTEGER PRIMARY KEY, text TEXT, book_corpus_id TEXT,
            page_start INTEGER, page_end INTEGER, atom_q_str TEXT
        );
        CREATE TABLE atomic_questions (
            atom_id INTEGER PRIMARY KEY, question_text TEXT, chunk_id INTEGER,
            subject_identifiers TEXT, from_category TEXT, source_quote TEXT,
            confidence REAL, founder_verified INTEGER, cc_id INTEGER
        );
        CREATE TABLE chunk_classifications (
            cc_id INTEGER PRIMARY KEY, is_chu_the INTEGER, is_cong_thuc INTEGER,
            is_luan_giai INTEGER, is_to_hop INTEGER, is_kinh_nghiem INTEGER,
            format_style TEXT
        );
        CREATE TABLE atom_commentaries (
            commentary_id INTEGER PRIMARY KEY, atom_id INTEGER UNIQUE,
            han_viet_explain TEXT, viet_thuan TEXT, nguyen_ly TEXT,
            vi_du_doi_song TEXT, cross_school_notes TEXT, iron_rule_warning TEXT,
            extracted_by TEXT, confidence REAL, founder_verified INTEGER
        );
        CREATE VIRTUAL TABLE atomic_questions_fts USING fts5(question_text);
        """
    )
    # 2 atom đều khớp FTS 'tuvi'; atom 1 commentary OK, atom 2 commentary bị bác (-1)
    conn.execute("INSERT INTO chunks_v2 VALUES (1,'chunk text','tuvi-book',1,1,'')")
    conn.execute(
        "INSERT INTO atomic_questions VALUES "
        "(1,'tuvi cau hoi mot',1,'{}','cat','TRICH THO MOT',0.9,0,NULL),"
        "(2,'tuvi cau hoi hai',1,'{}','cat','TRICH THO HAI',0.9,0,NULL)"
    )
    conn.execute(
        "INSERT INTO atom_commentaries "
        "(atom_id,viet_thuan,founder_verified) VALUES "
        "(1,'LUAN GIAI SAU DA THAM',0),"
        "(2,'LUAN GIAI BI BAC KHONG DUOC RO',-1)"
    )
    conn.execute("INSERT INTO atomic_questions_fts(rowid,question_text) VALUES (1,'tuvi cau hoi mot'),(2,'tuvi cau hoi hai')")
    conn.commit()
    conn.close()

    r = ChunkAtomRetriever(db)
    hits = {h.atom_id: h for h in r.search_atom_fts("tuvi", limit=10)}
    assert set(hits) == {1, 2}, "cả 2 atom phải ra (atom không bị bác)"
    # atom 1: có luận giải sâu
    assert hits[1].commentary and hits[1].commentary.get("viet_thuan") == "LUAN GIAI SAU DA THAM"
    # atom 2: commentary -1 → bị loại, atom vẫn ra với trích thô
    assert hits[2].commentary is None, "commentary -1 bị rò vào retrieval"
    assert hits[2].source_quote == "TRICH THO HAI"


# ─────────────────────────────────────────────────────────────
# P1 (2026-07-01): quota 2-pass — commentary phải LỌT vào block
# ─────────────────────────────────────────────────────────────

def _mini_db(tmp_path):
    """DB tối thiểu: 3 atom khớp FTS 'tuvi'; chỉ atom 3 (rank thấp nhất) có commentary."""
    import sqlite3
    db = tmp_path / "mini2.sqlite3"
    conn = sqlite3.connect(str(db))
    conn.executescript(
        """
        CREATE TABLE chunks_v2 (
            chunk_id INTEGER PRIMARY KEY, text TEXT, book_corpus_id TEXT,
            page_start INTEGER, page_end INTEGER, atom_q_str TEXT
        );
        CREATE TABLE atomic_questions (
            atom_id INTEGER PRIMARY KEY, question_text TEXT, chunk_id INTEGER,
            subject_identifiers TEXT, from_category TEXT, source_quote TEXT,
            confidence REAL, founder_verified INTEGER, cc_id INTEGER
        );
        CREATE TABLE chunk_classifications (
            cc_id INTEGER PRIMARY KEY, is_chu_the INTEGER, is_cong_thuc INTEGER,
            is_luan_giai INTEGER, is_to_hop INTEGER, is_kinh_nghiem INTEGER,
            format_style TEXT
        );
        CREATE TABLE atom_commentaries (
            commentary_id INTEGER PRIMARY KEY, atom_id INTEGER UNIQUE,
            han_viet_explain TEXT, viet_thuan TEXT, nguyen_ly TEXT,
            vi_du_doi_song TEXT, cross_school_notes TEXT, iron_rule_warning TEXT,
            extracted_by TEXT, confidence REAL, founder_verified INTEGER
        );
        CREATE VIRTUAL TABLE atomic_questions_fts USING fts5(question_text);
        """
    )
    conn.execute("INSERT INTO chunks_v2 VALUES (1,'chunk','tuvi-book',1,1,'')")
    conn.execute(
        "INSERT INTO atomic_questions VALUES "
        "(1,'tuvi tuvi tuvi cau mot',1,'{}','cat','QUOTE MOT',0.9,0,NULL),"
        "(2,'tuvi tuvi tuvi cau hai',1,'{}','cat','QUOTE HAI',0.9,0,NULL),"
        "(3,'tuvi cau ba',1,'{}','cat','QUOTE BA',0.9,0,NULL)"
    )
    conn.execute(
        "INSERT INTO atom_commentaries (atom_id,viet_thuan,founder_verified) "
        "VALUES (3,'LUAN SAU CUA BA',0)"
    )
    conn.execute(
        "INSERT INTO atomic_questions_fts(rowid,question_text) VALUES "
        "(1,'tuvi tuvi tuvi cau mot'),(2,'tuvi tuvi tuvi cau hai'),(3,'tuvi cau ba')"
    )
    conn.commit()
    conn.close()
    return db


def test_require_commentary_filter(tmp_path):
    """require_commentary=True chỉ trả atom CÓ luận sâu (pass 2 của quota)."""
    from engine.atomization.retriever import ChunkAtomRetriever
    r = ChunkAtomRetriever(_mini_db(tmp_path))
    hits = r.search_atom_fts("tuvi", limit=10, require_commentary=True)
    assert [h.atom_id for h in hits] == [3], "phải chỉ ra atom có commentary"
    assert hits[0].commentary.get("viet_thuan") == "LUAN SAU CUA BA"


def test_fmt_shows_atom_question(tmp_path):
    """Fix bug field name: block phải chứa CÂU HỎI atom (trước đọc question_text → mất)."""
    from engine.ai.expert_context import _fmt
    from engine.atomization.retriever import ChunkAtomRetriever
    r = ChunkAtomRetriever(_mini_db(tmp_path))
    hits = r.search_atom_fts("tuvi", limit=10)
    body = _fmt(hits, limit=3)
    assert "tuvi" in body and "cau" in body, f"câu hỏi atom mất khỏi block: {body!r}"
    assert not any(ln.strip() == "-" for ln in body.splitlines()), "dòng '-' trần = bug field name quay lại"


@pytest.mark.skipif(not _WIKI_DB.exists(), reason="cần wiki.sqlite3 (integration)")
def test_expert_context_quota_pulls_commentary():
    """Query mà top-k thường KHÔNG dính commentary (baseline đo 2026-07-01: 'hôn nhân
    phu thê' → 0/12) — sau quota 2-pass block PHẢI có nhãn luận sâu."""
    block = build_expert_context("hôn nhân phu thê", "tu_vi")
    assert block, "context rỗng"
    assert any(label in block for label in (
        "Việt thuần:", "Nguyên lý:", "Hán-Việt cốt:", "Ví dụ đời sống:",
    )), "quota 2-pass không kéo được commentary vào block"
