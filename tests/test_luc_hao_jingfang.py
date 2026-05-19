"""Tests for engine.luc_hao.jingfang — 京房 scaffolding (Najia + Lục thân + 伏神).

Verified against canonical 火珠林 / 京房易 charts.
"""

from __future__ import annotations

import pytest

from engine.luc_hao.jingfang import (
    _build_palace_table,
    build_jingfang_scaffold,
    hidden_lines,
    luc_than_of,
    luc_than_per_yao,
    najia_of,
    palace_of,
    palace_pure_hexagram,
    shih_yao_position,
)


# ─── 1. Palace classifier ─────────────────────────────────────────────────────


def test_palace_table_covers_all_64_hexagrams():
    table = _build_palace_table()
    assert len(table) == 64
    binaries = {bin(i)[2:].zfill(6) for i in range(64)}
    assert set(table.keys()) == binaries


def test_palace_8_pure_hexagrams_are_position_0():
    """The 8 pure trigrams doubled must each be 本卦 (position 0) of their palace."""
    pure_cases = [
        ("111111", "Càn"),
        ("000000", "Khôn"),
        ("011011", "Đoài"),
        ("101101", "Ly"),
        ("001001", "Chấn"),
        ("110110", "Tốn"),
        ("010010", "Khảm"),
        ("100100", "Cấn"),
    ]
    for binary, trigram in pure_cases:
        palace_trigram, position, _ = palace_of(binary)
        assert palace_trigram == trigram, f"{binary} expected palace {trigram}, got {palace_trigram}"
        assert position == 0, f"{binary} should be position 0 (Bản cung)"


def test_palace_known_assignments():
    """Spot-check well-known hexagrams against the canonical 京房八宮卦."""
    cases = [
        # binary,   palace,  position 0..7
        ("010001", "Khảm",  2),   # 水雷屯 — 坎宮 二世
        ("111000", "Càn",   3),   # 天地否 — 乾宮 三世 (天/地)
        ("000111", "Khôn",  3),   # 地天泰 — 坤宮 三世 (地/天)
        ("101000", "Càn",   6),   # 火地晉 — 乾宮 遊魂
        ("101111", "Càn",   7),   # 火天大有 — 乾宮 歸魂
        ("111110", "Càn",   1),   # 天風姤 — 乾宮 一世
    ]
    for binary, expected_palace, expected_pos in cases:
        palace, pos, _ = palace_of(binary)
        assert palace == expected_palace, f"{binary}: expected {expected_palace}, got {palace}"
        assert pos == expected_pos, f"{binary}: expected pos {expected_pos}, got {pos}"


def test_palace_pure_hexagram_for_truan_is_khảm_for_khảm():
    """屯 → palace pure = 坎為水 = 010010."""
    assert palace_pure_hexagram("010001") == "010010"


# ─── 2. Najia ──────────────────────────────────────────────────────────────────


def test_najia_qian_pure_hexagram():
    """乾為天: inner 甲子,甲寅,甲辰 / outer 壬午,壬申,壬戌."""
    result = najia_of("111111")
    expected = [
        ("Giáp", "Tý"), ("Giáp", "Dần"), ("Giáp", "Thìn"),
        ("Nhâm", "Ngọ"), ("Nhâm", "Thân"), ("Nhâm", "Tuất"),
    ]
    assert result == expected


def test_najia_kun_pure_hexagram():
    """坤為地: inner 乙未,乙巳,乙卯 / outer 癸丑,癸亥,癸酉."""
    result = najia_of("000000")
    expected = [
        ("Ất", "Mùi"), ("Ất", "Tỵ"), ("Ất", "Mão"),
        ("Quý", "Sửu"), ("Quý", "Hợi"), ("Quý", "Dậu"),
    ]
    assert result == expected


def test_najia_truan_water_thunder():
    """水雷屯: lower Chấn (庚子,庚寅,庚辰), upper Khảm (戊申,戊戌,戊子)."""
    result = najia_of("010001")
    expected = [
        ("Canh", "Tý"), ("Canh", "Dần"), ("Canh", "Thìn"),
        ("Mậu", "Thân"), ("Mậu", "Tuất"), ("Mậu", "Tý"),
    ]
    assert result == expected


def test_najia_returns_6_pairs_for_all_64_hexagrams():
    for i in range(64):
        binary = bin(i)[2:].zfill(6)
        result = najia_of(binary)
        assert len(result) == 6
        for stem, branch in result:
            assert stem in ("Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ",
                            "Canh", "Tân", "Nhâm", "Quý")


# ─── 3. Lục thân ───────────────────────────────────────────────────────────────


def test_luc_than_classifier_rules():
    # Same element → Huynh Đệ
    assert luc_than_of("kim", "kim") == "Huynh Đệ"
    # yao 生 palace → Phụ Mẫu (yao là cha mẹ)
    assert luc_than_of("thổ", "kim") == "Phụ Mẫu"   # thổ sinh kim
    # palace 生 yao → Tử Tôn
    assert luc_than_of("thủy", "kim") == "Tử Tôn"    # kim sinh thủy
    # yao 尅 palace → Quan Quỷ
    assert luc_than_of("hỏa", "kim") == "Quan Quỷ"   # hỏa khắc kim
    # palace 尅 yao → Thê Tài
    assert luc_than_of("mộc", "kim") == "Thê Tài"    # kim khắc mộc


def test_luc_than_per_yao_qian():
    """乾為天 (palace=kim): expected lục thân bottom-up = Tử, Thê, Phụ, Quan, Huynh, Phụ."""
    yao = luc_than_per_yao("111111")
    assert [y["luc_than"] for y in yao] == [
        "Tử Tôn", "Thê Tài", "Phụ Mẫu", "Quan Quỷ", "Huynh Đệ", "Phụ Mẫu",
    ]


# ─── 4. 伏神 (Phục thần / hidden lines) — THE TARGET ──────────────────────────


def test_hidden_lines_qian_pure_has_none():
    """乾為天 has all 5 relations → no missing → no 伏神."""
    assert hidden_lines("111111") == []


def test_hidden_lines_truan_has_one_thetai():
    """水雷屯 (palace=Khảm thủy) missing Thê Tài → hidden = 戊午 from 坎為水 hào 3."""
    hidden = hidden_lines("010001")
    assert len(hidden) == 1
    h = hidden[0].to_dict()
    assert h["luc_than"] == "Thê Tài"
    assert h["stem"] == "Mậu"
    assert h["branch"] == "Ngọ"
    assert h["element"] == "hỏa"
    assert h["visible_yao_position"] == 3
    assert h["visible_yao_luc_than"] == "Quan Quỷ"


def test_hidden_lines_multi_missing_robust():
    """Verify the engine handles hexagrams with 2+ missing relations
    (upstream ichingshifa silently fails this case)."""
    # Pick a hexagram and check the engine doesn't crash on any 64 input.
    for i in range(64):
        binary = bin(i)[2:].zfill(6)
        hidden = hidden_lines(binary)
        # Each hidden must be a valid PhucThan instance.
        for h in hidden:
            assert h.luc_than in ("Huynh Đệ", "Phụ Mẫu", "Tử Tôn", "Thê Tài", "Quan Quỷ")
            assert 1 <= h.visible_yao_position <= 6


# ─── 5. 世/應 + 身 ─────────────────────────────────────────────────────────────


def test_shih_position_for_palace_positions():
    """8 palace positions map to expected 世 positions."""
    # 乾宮: 本卦 → 世 6
    assert shih_yao_position("111111") == 6
    # 乾宮 一世 (天風姤) → 世 1
    assert shih_yao_position("111110") == 1
    # 乾宮 遊魂 (火地晉) → 世 4
    assert shih_yao_position("101000") == 4
    # 乾宮 歸魂 (火天大有) → 世 3
    assert shih_yao_position("101111") == 3


# ─── 6. Top-level scaffold ─────────────────────────────────────────────────────


def test_build_scaffold_complete():
    s = build_jingfang_scaffold("010001")
    d = s.to_dict()
    assert d["binary"] == "010001"
    assert d["palace_trigram"] == "Khảm"
    assert d["palace_position_name"] == "Nhị thế"
    assert d["palace_element"] == "thủy"
    assert len(d["najia_per_yao"]) == 6
    assert d["shih_yao_position"] == 2
    assert d["ying_yao_position"] == 5
    assert d["shen_yao_position"] == 3
    assert len(d["hidden_lines"]) == 1


def test_build_scaffold_rejects_invalid():
    with pytest.raises(ValueError):
        build_jingfang_scaffold("12345")   # not 6-bit
    with pytest.raises(ValueError):
        build_jingfang_scaffold("123456")  # not binary


def test_build_scaffold_all_64_smoke():
    """Smoke: no hexagram raises during scaffold building."""
    for i in range(64):
        binary = bin(i)[2:].zfill(6)
        s = build_jingfang_scaffold(binary)
        assert s.binary == binary
