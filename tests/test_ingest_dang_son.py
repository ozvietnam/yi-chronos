"""Test wiki-ingest corpus Đằng Sơn (40 vòng → concepts)."""
from __future__ import annotations

from engine.yi_wiki.ingest_dang_son import extract_concepts, _glob_journals


def test_globs_40_journals():
    assert len(_glob_journals()) == 40   # 20 Tập 1 + 20 Tập 2


def test_extract_concepts_shape_and_volume():
    cs = extract_concepts()
    assert len(cs) >= 200                # 40 vòng PHASE B → corpus đáng kể
    for c in cs:
        assert isinstance(c["canonical_vi"], str) and len(c["canonical_vi"]) >= 2
        assert isinstance(c["short_note"], str)
        assert isinstance(c["first_seen_page"], int)
        assert isinstance(c["sources"], list) and c["sources"]


def test_known_concepts_present():
    canon = {c["canonical_vi"].lower() for c in extract_concepts()}
    # vài concept cột mốc xuyên 40 vòng
    assert any("đào-mã-cái-sát" in k for k in canon)
    assert any("tuyệt-xứ-phùng-sinh" in k or "tuyệt-xứ" in k for k in canon)
    assert any("tuần" in k and "triệt" in k for k in canon)
