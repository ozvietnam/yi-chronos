"""P6 (issue #61) — hybrid FTS+vector+lan-cạnh vào Council. Test khoá hành vi.

Trọng tâm: (1) graceful degrade = đường PROD (không LM Studio → FTS thuần, không rỗng);
(2) cạnh lan CHỈ dùng loại MẠNH (bỏ 'nói-về' 87% nhiễu); (3) hybrid không crash.
"""
from engine.atomization.retriever import ChunkAtomRetriever


def _r(embedder=None):
    return ChunkAtomRetriever(embedder=embedder)


def test_strong_rels_khong_gom_noi_ve():
    """Cạnh lan phải LOẠI 'nói-về' (92.677 = 87% nhiễu chủ-đề-lỏng)."""
    assert "nói-về" not in ChunkAtomRetriever._STRONG_RELS
    assert "làm-rõ-sao" in ChunkAtomRetriever._STRONG_RELS


def test_degrade_ve_fts_khi_embed_tat():
    """PROD path: embedder trả None → hybrid == FTS thuần, KHÔNG rỗng (không giết council)."""
    r = _r(embedder=lambda q: None)          # ép embed fail
    assert r.search_atom_vec("Vũ Khúc", limit=5) == []   # vector rỗng
    hy = r.search_atom_hybrid("Vũ Khúc Phá Quân", limit=5)
    fts = r.search_atom_fts("Vũ Khúc Phá Quân", limit=5)
    assert hy, "degrade phải trả FTS, không được rỗng"
    assert {a.atom_id for a in hy} == {a.atom_id for a in fts}


def test_hybrid_khong_crash_va_atom_id_hop_le():
    """Hybrid chạy (dù embed on/off) → mọi atom_id > 0, không lỗi."""
    r = _r()
    hy = r.search_atom_hybrid("Thiên Tướng ở Mệnh", limit=6)
    assert isinstance(hy, list)
    for a in hy:
        assert a.atom_id > 0
        assert a.atom_query == "Thiên Tướng ở Mệnh"


def test_expand_chi_lan_canh_manh():
    """expand_via_relations nhận seed hợp lệ → trả list (có thể rỗng), không crash;
    seed rỗng → rỗng."""
    r = _r()
    assert r.expand_via_relations([], "x") == []
    fts = r.search_atom_fts("Vũ Khúc", limit=3)
    if fts:
        exp = r.expand_via_relations([a.atom_id for a in fts], "Vũ Khúc", limit=4)
        assert isinstance(exp, list)
        seed_ids = {a.atom_id for a in fts}
        assert all(a.atom_id not in seed_ids for a in exp)  # không lặp seed
