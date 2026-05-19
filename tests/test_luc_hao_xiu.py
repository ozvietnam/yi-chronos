"""Tests for engine.luc_hao.twentyeight_xiu — 28-tú mapping."""

from __future__ import annotations

import pytest

from engine.luc_hao.twentyeight_xiu import (
    Mansion,
    all_mansions,
    mansion_by_name,
    primary_xiu_dict,
    primary_xiu_for_hexagram,
)


def test_all_mansions_count_is_28():
    assert len(all_mansions()) == 28


def test_all_mansions_have_unique_names():
    names_vi = {m.name_vi for m in all_mansions()}
    names_cn = {m.name_cn for m in all_mansions()}
    assert len(names_vi) == 28
    assert len(names_cn) == 28


def test_four_quadrants_have_seven_mansions_each():
    counts = {"Đông": 0, "Bắc": 0, "Tây": 0, "Nam": 0}
    for m in all_mansions():
        counts[m.quadrant] += 1
    assert counts == {"Đông": 7, "Bắc": 7, "Tây": 7, "Nam": 7}


def test_known_mansion_metadata():
    """Spot-check canonical entries."""
    giac = mansion_by_name("Giác")
    assert giac.index == 0
    assert giac.name_cn == "角"
    assert giac.quadrant == "Đông"
    assert giac.spirit == "Thanh Long"

    sam = mansion_by_name("Sâm")
    assert sam.quadrant == "Tây"
    assert sam.spirit == "Bạch Hổ"

    chan = mansion_by_name("Chẩn")
    assert chan.index == 27   # last in canonical order
    assert chan.quadrant == "Nam"


def test_mansion_by_name_rejects_unknown():
    with pytest.raises(ValueError):
        mansion_by_name("NotAMansion")


def test_primary_xiu_returns_Mansion():
    m = primary_xiu_for_hexagram(1)
    assert isinstance(m, Mansion)


def test_primary_xiu_covers_all_64_hexagrams():
    """Every King-Wen 1..64 must yield a mansion without error."""
    for kw in range(1, 65):
        m = primary_xiu_for_hexagram(kw)
        assert isinstance(m, Mansion)


def test_primary_xiu_dict_shape():
    d = primary_xiu_dict(1)
    assert set(d.keys()) == {
        "index", "name_vi", "name_cn", "quadrant", "spirit", "element_7yao", "animal",
    }


def test_primary_xiu_rejects_out_of_range():
    with pytest.raises(ValueError):
        primary_xiu_for_hexagram(0)
    with pytest.raises(ValueError):
        primary_xiu_for_hexagram(65)


def test_primary_xiu_kw1_anchors_at_sam():
    """Convention: hexagram 1 (Càn / Kiền) → mansion 參 (Sâm)."""
    m = primary_xiu_for_hexagram(1)
    assert m.name_vi == "Sâm"


def test_primary_xiu_distribution_is_balanced():
    """64 hexagrams ÷ 28 mansions ≈ 2.28 — each mansion should rule 2 or 3 hexagrams."""
    counts = {m.name_vi: 0 for m in all_mansions()}
    for kw in range(1, 65):
        m = primary_xiu_for_hexagram(kw)
        counts[m.name_vi] += 1
    # Distribution: 8 mansions × 3 hex + 20 mansions × 2 hex = 24 + 40 = 64.
    for count in counts.values():
        assert 2 <= count <= 3


def test_jingfang_scaffold_includes_xiu_when_king_wen_passed():
    from engine.luc_hao.jingfang import build_jingfang_scaffold

    s = build_jingfang_scaffold("111111", king_wen_index=1)
    d = s.to_dict()
    assert d["primary_xiu"] is not None
    assert d["primary_xiu"]["name_vi"] == "Sâm"


def test_jingfang_scaffold_omits_xiu_when_no_king_wen():
    from engine.luc_hao.jingfang import build_jingfang_scaffold

    s = build_jingfang_scaffold("111111")
    assert s.to_dict()["primary_xiu"] is None
