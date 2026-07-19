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
    """PROD path: embedder None → vector rỗng, nhưng hybrid = FTS seeds + LAN-CẠNH
    (không rỗng, và CHỨA TRỌN FTS — lan-cạnh chỉ thêm, không bỏ)."""
    r = _r(embedder=lambda q: None)          # ép embed fail
    assert r.search_atom_vec("Vũ Khúc", limit=5) == []   # vector rỗng
    hy = r.search_atom_hybrid("Vũ Khúc Phá Quân", limit=5)
    fts = r.search_atom_fts("Vũ Khúc Phá Quân", limit=5)
    assert hy, "degrade phải trả kết quả, không được rỗng"
    assert {a.atom_id for a in fts} <= {a.atom_id for a in hy}  # hybrid ⊇ FTS (thêm lan-cạnh)


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


def test_degrade_van_lan_canh_khong_embedder(monkeypatch):
    """FIX prod: khi KHÔNG có embedder (đường degrade), hybrid VẪN gọi lan-cạnh trên
    seed FTS — vì atom_relations không cần vector. Đây là điểm khiến 107k cạnh có giá
    trị TRÊN LIVE (trước đây đường degrade return thẳng FTS, bỏ qua cạnh)."""
    from types import SimpleNamespace
    r = _r(embedder=lambda q: None)                       # prod: không vector
    seeds = [SimpleNamespace(atom_id=1), SimpleNamespace(atom_id=2)]
    neighbor = [SimpleNamespace(atom_id=99)]
    monkeypatch.setattr(r, "search_atom_fts", lambda *a, **k: list(seeds))
    monkeypatch.setattr(r, "search_atom_vec", lambda *a, **k: [])
    seen = {}

    def fake_expand(ids, q, limit=4, school=None):
        seen["ids"] = list(ids)
        return list(neighbor)

    monkeypatch.setattr(r, "expand_via_relations", fake_expand)
    out = r.search_atom_hybrid("bất kỳ", limit=5)
    ids = {a.atom_id for a in out}
    assert {1, 2} <= ids, "phải giữ trọn seed FTS"
    assert 99 in ids, "phải THÊM atom lan-cạnh dù không có embedder (fix prod)"
    assert seen.get("ids"), "expand_via_relations phải được gọi trên đường degrade"


def test_conflict_rels_duoc_lan():
    """Iron Rule #3 (đa phái): cạnh PHẢN-BIỆN/CẢNH-BÁO phải được lan để council thấy
    counterpoint, không chỉ bằng chứng đồng thuận. Vẫn LOẠI nhiễu 'nói-về'."""
    for rel in ("đối-lập", "đối-lập-phái-khác", "cảnh-báo", "trai_nghia"):
        assert rel in ChunkAtomRetriever._STRONG_RELS, f"{rel} phải nằm trong _STRONG_RELS"
    assert "nói-về" not in ChunkAtomRetriever._STRONG_RELS
