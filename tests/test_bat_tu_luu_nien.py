"""Tests for engine.bat_tu.luu_nien — annual analysis."""
from __future__ import annotations

import pytest

from engine.bat_tu import analyze_luu_nien, cast_bat_tu
from engine.bat_tu.luu_nien import (
    compute_luu_nien_pillar_by_year,
    LUC_HOP,
    LUC_XUNG,
    TAM_HOP,
)


# ─── Lưu Niên pillar computation ────────────────────────────────────────────


@pytest.mark.parametrize("year,expected_stem,expected_branch", [
    (1984, "Giáp", "Tý"),      # anchor — Giáp Tý
    (1985, "Ất", "Sửu"),
    (1988, "Mậu", "Thìn"),     # founder year
    (2024, "Giáp", "Thìn"),
    (2025, "Ất", "Tỵ"),
    (2026, "Bính", "Ngọ"),
    (2027, "Đinh", "Mùi"),
    (2044, "Giáp", "Tý"),      # next 60-year cycle anchor
])
def test_pillar_formula(year, expected_stem, expected_branch):
    p = compute_luu_nien_pillar_by_year(year)
    assert p["stem"] == expected_stem
    assert p["branch"] == expected_branch


def test_pillar_includes_elements():
    p = compute_luu_nien_pillar_by_year(2026)
    assert p["stem_element"] == "hỏa"  # Bính = dương hỏa
    assert p["branch_element"] == "hỏa"  # Ngọ = dương hỏa


# ─── Founder analysis (year 2026) ───────────────────────────────────────────


@pytest.fixture
def founder_luu_2026():
    state = cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    return analyze_luu_nien(state, current_age=38, target_year=2026)


def test_founder_2026_is_binh_ngo(founder_luu_2026):
    """Year 2026 must be Bính Ngọ."""
    ln = founder_luu_2026["luu_nien"]
    assert ln["stem"] == "Bính"
    assert ln["branch"] == "Ngọ"
    assert ln["year_solar"] == 2026


def test_founder_2026_thap_than_is_thien_tai(founder_luu_2026):
    """Bính (dương hỏa) vs Day Master Nhâm (dương thủy) = Thiên Tài
    (thủy khắc hỏa, cùng tính dương → Thiên Tài)."""
    ln = founder_luu_2026["luu_nien"]
    assert ln["thap_than_vs_dm"] == "Thiên Tài"


def test_founder_2026_luu_xung_with_tru_gio(founder_luu_2026):
    """2026 Ngọ ⚔ founder's Trụ Giờ Tý = lục xung."""
    hour_inter = founder_luu_2026["vs_chart"]["vs_pillars"]["hour"]
    types = [ci["type"] for ci in hour_inter["chi_interactions"]]
    assert "lục xung" in types


def test_founder_2026_no_ban_hop_hoa(founder_luu_2026):
    """Chart sửa: Trụ Ngày = Thìn (không phải Tuất) → 2026 Ngọ KHÔNG tạo bán hợp Hỏa cục."""
    tam_hop = founder_luu_2026["vs_chart"]["tam_hop_detected"]
    found_hoa = [th for th in tam_hop if th["element"] == "hỏa"]
    assert len(found_hoa) == 0


def test_founder_2026_overall_verdict_trung_tinh(founder_luu_2026):
    """Bính Ngọ (Hỏa/Hỏa) vs Dụng Thủy / Kỵ Thổ → trung tính."""
    ov = founder_luu_2026["overall_verdict"]
    assert ov["verdict"] == "trung tính"
    assert not ov["matches_dung_than"]
    assert not ov["matches_ky_than"]


def test_founder_2026_dai_van_detected(founder_luu_2026):
    """Age 38 should detect Đại Vận Tân Dậu (30-39)."""
    dv = founder_luu_2026["vs_dai_van"]["current_dai_van"]
    assert dv is not None
    assert dv["stem"] == "Tân"
    assert dv["branch"] == "Dậu"


def test_founder_2026_12_months_complete(founder_luu_2026):
    """12 tháng Lưu Nguyệt must be 12 entries."""
    months = founder_luu_2026["luu_nguyet"]
    assert len(months) == 12
    # First month must start with Tiết Lập Xuân + chi Dần
    assert months[0]["branch"] == "Dần"
    assert months[0]["tiet_khi"] == "Lập Xuân"
    # Fifth month: Mang Chủng (Ngọ)
    assert months[4]["branch"] == "Ngọ"


def test_founder_2026_thuan_months(founder_luu_2026):
    """Some 'thuận' months must exist (Dụng = Thủy days)."""
    months = founder_luu_2026["luu_nguyet"]
    thuan_months = [m for m in months if m["verdict"] == "thuận"]
    assert len(thuan_months) >= 1


# ─── Paradigm tone ──────────────────────────────────────────────────────────


def test_paradigm_guard_no_predict(founder_luu_2026):
    guard = founder_luu_2026["paradigm_guard"]
    assert "KHÔNG dự đoán" in guard or "KHÔNG predict" in guard


def test_no_predict_phrases(founder_luu_2026):
    """No forbidden predict phrases in narrative."""
    import json
    text = json.dumps(founder_luu_2026, ensure_ascii=False)
    forbidden = ["sẽ giàu", "sẽ nghèo", "sẽ thành công", "sẽ thất bại"]
    for f in forbidden:
        assert f.lower() not in text.lower(), f"Found forbidden phrase: {f}"


# ─── Other years ────────────────────────────────────────────────────────────


def test_other_year_works():
    """Analyzing year 2030 should work too."""
    state = cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    luu = analyze_luu_nien(state, current_age=42, target_year=2030)
    assert luu["target_year"] == 2030
    # 2030 = Canh Tuất (formula check)
    p = compute_luu_nien_pillar_by_year(2030)
    assert p["stem"] == "Canh"
    assert p["branch"] == "Tuất"


def test_include_luu_nguyet_false():
    """Optional skip of 12 months."""
    state = cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    luu = analyze_luu_nien(state, current_age=38, target_year=2026, include_luu_nguyet=False)
    assert luu["luu_nguyet"] == []


# ─── Edge cases ─────────────────────────────────────────────────────────────


def test_no_current_age():
    """Without current_age, Đại Vận not detected, but core analysis still works."""
    state = cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    luu = analyze_luu_nien(state, current_age=None, target_year=2026)
    assert luu["vs_dai_van"]["current_dai_van"] is None
    # But Lưu Niên + verdict still computed
    assert luu["luu_nien"]["stem"] == "Bính"
    assert luu["overall_verdict"]["narrative"]


def test_invalid_state_rejected():
    with pytest.raises(ValueError, match="tu_tru"):
        analyze_luu_nien({}, current_age=38, target_year=2026)


# ─── Reference table consistency ────────────────────────────────────────────


def test_luc_hop_complete():
    """All 6 lục hợp pairs present."""
    assert len(LUC_HOP) == 6


def test_luc_xung_complete():
    """All 6 lục xung pairs present."""
    assert len(LUC_XUNG) == 6


def test_tam_hop_groups():
    """4 tam hợp cục — Thủy/Mộc/Hỏa/Kim (no Thổ)."""
    assert set(TAM_HOP.keys()) == {"thủy", "mộc", "hỏa", "kim"}
    for el, group in TAM_HOP.items():
        assert len(group) == 3
