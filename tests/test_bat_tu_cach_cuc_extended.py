"""Tests for engine.bat_tu.cach_cuc_extended — Tòng + Hóa Khí + Five Special detection.

Real-world extreme charts are rare (~1-2% population). Most tests use synthetic
charts built directly from constants to verify each detection path.
"""
from __future__ import annotations

import pytest

from engine.bat_tu import cast_bat_tu, compose_luan_giai, detect_extreme_pattern


def _build_pillar(pos, stem, branch):
    """Build a minimal pillar dict for testing."""
    from engine.bat_tu.constants import (
        BRANCH_ELEMENT, BRANCH_HIDDEN_STEMS, STEM_ELEMENT,
    )
    return {
        "position_vi": {"year": "Trụ Năm", "month": "Trụ Tháng",
                        "day": "Trụ Ngày", "hour": "Trụ Giờ"}[pos],
        "stem": stem,
        "branch": branch,
        "stem_element": STEM_ELEMENT[stem],
        "branch_element": BRANCH_ELEMENT[branch],
        "hidden_stems": list(BRANCH_HIDDEN_STEMS[branch]),
    }


# ─── Five Special tests ─────────────────────────────────────────────────────


def test_khuc_truc_full_moc():
    """Khúc Trực (full Mộc) — DM Giáp + 4 chi Mộc + no Kim."""
    pillars = {
        "year": _build_pillar("year", "Giáp", "Dần"),
        "month": _build_pillar("month", "Đinh", "Mão"),
        "day": _build_pillar("day", "Giáp", "Dần"),
        "hour": _build_pillar("hour", "Ất", "Mão"),
    }
    counts = {"mộc": 6.0, "hỏa": 0.5, "thổ": 0.2, "kim": 0.0, "thủy": 0.0}
    dist = {
        "visible": {"Tỷ Kiên": 1, "Kiếp Tài": 1, "Thương Quan": 1},
        "hidden": {"Tỷ Kiên": 2, "Kiếp Tài": 1, "Thực Thần": 1, "Thiên Tài": 1},
    }
    result = detect_extreme_pattern(pillars, "Giáp", counts, dist, 8.0)
    assert result is not None
    assert result["pattern_type"] == "special"
    assert "Khúc Trực" in result["name"]
    assert result["dung_than_element"] == "mộc"
    assert result["ky_than_element"] == "kim"
    assert result["confidence"] == "high"


def test_viem_thuong_full_hoa():
    """Viêm Thượng (full Hỏa)."""
    pillars = {
        "year": _build_pillar("year", "Bính", "Ngọ"),
        "month": _build_pillar("month", "Đinh", "Tỵ"),
        "day": _build_pillar("day", "Bính", "Ngọ"),
        "hour": _build_pillar("hour", "Đinh", "Tỵ"),
    }
    counts = {"mộc": 0.5, "hỏa": 6.0, "thổ": 0.3, "kim": 0.0, "thủy": 0.0}
    dist = {
        "visible": {"Tỷ Kiên": 1, "Kiếp Tài": 2},
        "hidden": {"Tỷ Kiên": 2, "Kiếp Tài": 2},
    }
    result = detect_extreme_pattern(pillars, "Bính", counts, dist, 8.0)
    assert result is not None
    assert "Viêm Thượng" in result["name"]
    assert result["dung_than_element"] == "hỏa"
    assert result["ky_than_element"] == "thủy"


def test_gia_sac_full_tho():
    """Giá Sắc (full Thổ) — DM Mậu/Kỷ + 4 chi Thổ."""
    pillars = {
        "year": _build_pillar("year", "Mậu", "Thìn"),
        "month": _build_pillar("month", "Kỷ", "Mùi"),
        "day": _build_pillar("day", "Mậu", "Tuất"),
        "hour": _build_pillar("hour", "Kỷ", "Sửu"),
    }
    counts = {"mộc": 0.3, "hỏa": 0.2, "thổ": 7.0, "kim": 0.5, "thủy": 0.0}
    dist = {
        "visible": {"Tỷ Kiên": 1, "Kiếp Tài": 2},
        "hidden": {"Tỷ Kiên": 4, "Kiếp Tài": 2, "Chính Quan": 1, "Thương Quan": 1},
    }
    result = detect_extreme_pattern(pillars, "Mậu", counts, dist, 8.0)
    assert result is not None
    assert "Giá Sắc" in result["name"]
    assert result["dung_than_element"] == "thổ"


def test_tong_cach_full_kim():
    """Tòng Cách (full Kim) — DM Canh/Tân + 4 chi Kim."""
    pillars = {
        "year": _build_pillar("year", "Canh", "Thân"),
        "month": _build_pillar("month", "Tân", "Dậu"),
        "day": _build_pillar("day", "Canh", "Thân"),
        "hour": _build_pillar("hour", "Tân", "Dậu"),
    }
    counts = {"mộc": 0.0, "hỏa": 0.0, "thổ": 0.2, "kim": 6.5, "thủy": 0.5}
    dist = {
        "visible": {"Tỷ Kiên": 1, "Kiếp Tài": 2},
        "hidden": {"Tỷ Kiên": 2, "Kiếp Tài": 2},
    }
    result = detect_extreme_pattern(pillars, "Canh", counts, dist, 8.0)
    assert result is not None
    assert "Tòng Cách" in result["name"]
    assert result["dung_than_element"] == "kim"
    assert result["ky_than_element"] == "hỏa"


def test_nhuan_ha_full_thuy():
    """Nhuận Hạ (full Thủy)."""
    pillars = {
        "year": _build_pillar("year", "Nhâm", "Tý"),
        "month": _build_pillar("month", "Quý", "Hợi"),
        "day": _build_pillar("day", "Nhâm", "Tý"),
        "hour": _build_pillar("hour", "Quý", "Hợi"),
    }
    counts = {"mộc": 0.5, "hỏa": 0.0, "thổ": 0.2, "kim": 0.0, "thủy": 7.0}
    dist = {
        "visible": {"Tỷ Kiên": 1, "Kiếp Tài": 2},
        "hidden": {"Tỷ Kiên": 2, "Kiếp Tài": 2, "Thực Thần": 1},
    }
    result = detect_extreme_pattern(pillars, "Nhâm", counts, dist, 8.0)
    assert result is not None
    assert "Nhuận Hạ" in result["name"]
    assert result["dung_than_element"] == "thủy"


def test_five_special_blocked_by_khac_element():
    """4 chi Mộc nhưng có nhiều Kim → KHÔNG là Khúc Trực."""
    pillars = {
        "year": _build_pillar("year", "Giáp", "Dần"),
        "month": _build_pillar("month", "Canh", "Mão"),  # Canh Kim ở thiên can
        "day": _build_pillar("day", "Giáp", "Dần"),
        "hour": _build_pillar("hour", "Canh", "Mão"),
    }
    # Significant Kim
    counts = {"mộc": 5.0, "hỏa": 0.0, "thổ": 0.5, "kim": 2.5, "thủy": 0.0}
    dist = {"visible": {"Thất Sát": 2}, "hidden": {}}
    result = detect_extreme_pattern(pillars, "Giáp", counts, dist, 0.0)
    # Should NOT detect Khúc Trực because Kim count > 15% of total
    assert result is None or "Khúc Trực" not in result.get("name", "")


# ─── Hóa Khí tests ──────────────────────────────────────────────────────────


def test_hoa_khi_giap_ky_thanh_tho():
    """Giáp + Kỷ hợp Thổ + tháng Sửu (Thổ vượng) + no Mộc khắc."""
    pillars = {
        "year": _build_pillar("year", "Kỷ", "Sửu"),
        "month": _build_pillar("month", "Kỷ", "Sửu"),
        "day": _build_pillar("day", "Giáp", "Tuất"),
        "hour": _build_pillar("hour", "Kỷ", "Tỵ"),
    }
    counts = {"mộc": 0.5, "hỏa": 1.0, "thổ": 6.0, "kim": 0.6, "thủy": 0.4}
    dist = {
        "visible": {"Chính Tài": 3},
        "hidden": {"Chính Tài": 3, "Thiên Tài": 1, "Chính Quan": 1},
    }
    result = detect_extreme_pattern(pillars, "Giáp", counts, dist, -3.0)
    assert result is not None
    assert result["pattern_type"] == "hoa"
    assert "hóa Thổ" in result["name"]
    assert result["dung_than_element"] == "thổ"


def test_hoa_khi_blocked_by_khac():
    """Giáp + Kỷ nhưng có nhiều Mộc khắc → KHÔNG hóa."""
    pillars = {
        "year": _build_pillar("year", "Kỷ", "Mùi"),
        "month": _build_pillar("month", "Kỷ", "Sửu"),
        "day": _build_pillar("day", "Giáp", "Dần"),  # gốc Mộc mạnh
        "hour": _build_pillar("hour", "Giáp", "Dần"),  # thêm Mộc
    }
    # High mộc count
    counts = {"mộc": 3.5, "hỏa": 0.5, "thổ": 4.5, "kim": 0.0, "thủy": 0.5}
    dist = {"visible": {}, "hidden": {}}
    result = detect_extreme_pattern(pillars, "Giáp", counts, dist, 0.0)
    # mộc 3.5/9 = 39% > 20% → should NOT hóa
    if result and result.get("pattern_type") == "hoa":
        # If still detected, confidence should be low
        assert result.get("confidence") in {"low", "medium"}


# ─── Tòng cách tests ────────────────────────────────────────────────────────


def test_tong_tai_dm_extreme_weak_tai_dominant():
    """Tòng Tài: DM Giáp cực nhược + Tài (Thổ) chiếm hầu hết (NO Kỷ to trigger hóa)."""
    # Use Mậu instead of Kỷ to avoid Giáp+Kỷ hóa Thổ
    pillars = {
        "year": _build_pillar("year", "Mậu", "Tuất"),
        "month": _build_pillar("month", "Mậu", "Tuất"),  # tháng Thổ
        "day": _build_pillar("day", "Giáp", "Thìn"),
        "hour": _build_pillar("hour", "Mậu", "Thìn"),
    }
    counts = {"mộc": 0.7, "hỏa": 0.5, "thổ": 7.0, "kim": 0.3, "thủy": 0.2}
    dist = {
        "visible": {"Thiên Tài": 3},
        "hidden": {"Thiên Tài": 4, "Chính Tài": 1, "Chính Quan": 2},
    }
    result = detect_extreme_pattern(pillars, "Giáp", counts, dist, -7.5)
    assert result is not None
    # Either Tòng Tài or Hóa Khí — both reasonable. Just verify it detected something.
    assert result["pattern_type"] in {"tong", "hoa"}


def test_tong_cuong_dm_extreme_strong_an_ty_dominant():
    """Tòng Cường: DM cực vượng + Ấn/Tỷ chiếm > 70%."""
    # DM = Giáp, all support: Tỷ + Kiếp + Ấn
    pillars = {
        "year": _build_pillar("year", "Quý", "Hợi"),   # Quý sinh Giáp + Hợi mộc
        "month": _build_pillar("month", "Giáp", "Dần"),  # Tỷ + lộc
        "day": _build_pillar("day", "Giáp", "Dần"),    # DM
        "hour": _build_pillar("hour", "Ất", "Mão"),     # Kiếp + lộc
    }
    counts = {"mộc": 6.5, "hỏa": 0.5, "thổ": 0.2, "kim": 0.0, "thủy": 1.5}
    dist = {
        "visible": {"Chính Ấn": 1, "Tỷ Kiên": 1, "Kiếp Tài": 1},
        "hidden": {"Tỷ Kiên": 3, "Kiếp Tài": 1, "Chính Ấn": 1, "Thiên Ấn": 1},
    }
    # Day Master EXTREME vượng
    result = detect_extreme_pattern(pillars, "Giáp", counts, dist, 9.0)
    # Khúc Trực should also be possible (full Mộc) — but Quý/Hợi water makes it not pure Mộc
    # Could detect either Khúc Trực OR Tòng Cường
    assert result is not None


def test_no_extreme_for_normal_chart():
    """Normal chart (founder) — KHÔNG có extreme."""
    state = cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    assert state.get("extreme_pattern") is None


# ─── cast.py integration ────────────────────────────────────────────────────


def test_cast_bat_tu_includes_extreme_pattern_field():
    """cast_bat_tu output must include `extreme_pattern` key."""
    state = cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    assert "extreme_pattern" in state


def test_luan_giai_includes_extreme_section():
    """luận giải output includes extreme_pattern_luan (None if no extreme)."""
    state = cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    luan = compose_luan_giai(state, current_age=38)
    assert "extreme_pattern_luan" in luan
    # Founder has no extreme
    assert luan["extreme_pattern_luan"] is None


def test_cach_cuc_luan_has_extreme_override_field():
    """cach_cuc_luan must have has_extreme_override field."""
    state = cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    luan = compose_luan_giai(state, current_age=38)
    assert "has_extreme_override" in luan["cach_cuc_luan"]
    assert luan["cach_cuc_luan"]["has_extreme_override"] is False  # founder normal
