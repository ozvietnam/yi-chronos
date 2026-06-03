"""Tests for engine.bat_tu.hon_nhan + engine.bat_tu.su_nghiep.

Verifies paradigm tone, founder chart specifics, structural completeness.
"""
from __future__ import annotations

import pytest

from engine.bat_tu import analyze_hon_nhan, analyze_su_nghiep, cast_bat_tu


@pytest.fixture
def founder_state():
    return cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )


# ─── Hôn Nhân tests ─────────────────────────────────────────────────────────


@pytest.fixture
def founder_hon_nhan(founder_state):
    return analyze_hon_nhan(founder_state)


def test_hn_method_id(founder_hon_nhan):
    assert founder_hon_nhan["method_id"] == "bat_tu_hon_nhan_v1"


def test_hn_paradigm_guard(founder_hon_nhan):
    """Paradigm guard explicitly says KHÔNG dự đoán."""
    guard = founder_hon_nhan["paradigm_guard"]
    assert "KHÔNG dự đoán" in guard
    # Other narrative sections (NOT paradigm_guard, which intentionally contains
    # negated predict phrases like "không dự đoán anh sẽ X") shouldn't predict.
    narrative_text = (
        founder_hon_nhan["overall"]["narrative"]
        + " " + founder_hon_nhan["closing"]
        + " " + founder_hon_nhan["cung_phoi"]["trait_narrative"]
    ).lower()
    forbidden = ["chắc chắn lấy", "chắc chắn ly hôn", "chắc chắn cưới"]
    for f in forbidden:
        assert f not in narrative_text


def test_hn_all_sections(founder_hon_nhan):
    required = [
        "method_id", "paradigm_guard", "gender",
        "cung_phoi", "partner_star", "warnings",
        "special_stars", "timing_suggestions", "overall", "closing",
    ]
    for k in required:
        assert k in founder_hon_nhan


def test_hn_founder_cung_phoi_is_thin(founder_hon_nhan):
    """Founder Trụ Ngày = Nhâm Thìn → Cung Phối = Thìn."""
    cp = founder_hon_nhan["cung_phoi"]
    assert cp["branch"] == "Thìn"
    assert cp["branch_element"] == "thổ"


def test_hn_founder_cung_phoi_no_luc_xung(founder_hon_nhan):
    """Cung Phối Thìn (Trụ Ngày) trùng chi Thìn (Trụ Năm) → KHÔNG lục xung
    (chart đã sửa: Thìn không xung Thìn, khác với Tuất ⚔ Thìn cũ)."""
    interactions = founder_hon_nhan["cung_phoi"]["interactions_with_other_pillars"]
    types = [i["type"] for i in interactions]
    assert "lục xung" not in types


def test_hn_founder_tai_tinh_count(founder_hon_nhan):
    """Founder is nam → Tài tinh check. Main star = Chính Tài (Đinh tàng Ngọ)."""
    ps = founder_hon_nhan["partner_star"]
    assert ps["gender"] == "nam"
    assert ps["main_star"] == "Chính Tài"
    assert ps["total_count"] >= 1


def test_hn_founder_has_warnings(founder_hon_nhan):
    """Founder has Tài + Kiếp Tài → "Kiếp Tài đoạt Tài" warning."""
    warning_names = {w["name"] for w in founder_hon_nhan["warnings"]}
    assert "Kiếp Tài đoạt Tài" in warning_names or "Tài tinh quá vượng" in warning_names


def test_hn_no_predict_phrases(founder_hon_nhan):
    import json
    text = json.dumps(founder_hon_nhan, ensure_ascii=False).lower()
    forbidden = ["sẽ lấy được", "chắc chắn ly hôn", "chắc chắn cưới"]
    for f in forbidden:
        assert f not in text


def test_hn_invalid_state_rejected():
    with pytest.raises(ValueError, match="tu_tru"):
        analyze_hon_nhan({})


def test_hn_female_uses_quan_tinh():
    """Phụ nữ should look at Quan tinh, not Tài."""
    state = cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nữ",
    )
    hn = analyze_hon_nhan(state)
    ps = hn["partner_star"]
    assert ps["gender"] == "nữ"
    assert ps["main_star"] == "Chính Quan"
    assert ps["secondary_star"] == "Thất Sát"


# ─── Sự Nghiệp tests ────────────────────────────────────────────────────────


@pytest.fixture
def founder_su_nghiep(founder_state):
    return analyze_su_nghiep(founder_state)


def test_sn_method_id(founder_su_nghiep):
    assert founder_su_nghiep["method_id"] == "bat_tu_su_nghiep_v1"


def test_sn_paradigm_guard(founder_su_nghiep):
    guard = founder_su_nghiep["paradigm_guard"]
    assert "KHÔNG dự đoán" in guard


def test_sn_all_sections(founder_su_nghiep):
    required = [
        "method_id", "paradigm_guard", "cach_cuc_summary",
        "career_patterns", "dominant_thap_than_styles",
        "recommendations", "avoid", "timing_by_dai_van", "closing",
    ]
    for k in required:
        assert k in founder_su_nghiep


def test_sn_founder_cach_cuc_is_chinh_tai(founder_su_nghiep):
    """Founder's cách cục = Chính Tài."""
    assert "Chính Tài" in founder_su_nghiep["cach_cuc_summary"]["name"]
    assert founder_su_nghiep["cach_cuc_summary"]["career_style"]


def test_sn_founder_has_patterns(founder_su_nghiep):
    """Founder must detect multiple patterns (Quan Ấn tương sinh, Thực Thương sinh Tài, Tỷ Kiếp trợ thân)."""
    assert len(founder_su_nghiep["career_patterns"]) >= 2
    names = {p["name"] for p in founder_su_nghiep["career_patterns"]}
    # At least one of these should be detected
    expected_one_of = {"Quan Ấn tương sinh", "Thực Thương sinh Tài", "Tỷ Kiếp trợ thân"}
    assert names & expected_one_of


def test_sn_dung_than_recommendations(founder_su_nghiep):
    """Dụng = Thủy → industries should be thủy-related."""
    rec = founder_su_nghiep["recommendations"]["by_dung_than"]
    assert rec["element"] == "thủy"
    assert len(rec["industries"]) >= 3


def test_sn_avoid_tho(founder_su_nghiep):
    """Kỵ = Thổ → avoid list should be thổ-related (đất đai, nông nghiệp, vật liệu)."""
    avoid = founder_su_nghiep["avoid"]
    cats = [i["category"] for i in avoid["from_ky_than"]]
    # Look for Thổ industries
    assert any(
        "Bất động sản" in c or "Nông nghiệp" in c or "Đá" in c or "Vải vóc" in c
        for c in cats
    )


def test_sn_timing_dai_van(founder_su_nghiep):
    """Each cycle should have a verdict + mark."""
    cycles = founder_su_nghiep["timing_by_dai_van"]
    assert len(cycles) >= 4
    for c in cycles:
        assert c["verdict"] in {"thuận lợi", "thử thách", "tích lũy", "hỗn tạp", "trung"}
        assert c["mark"] in {"✦", "⚠", "✧", "⚖", "·"}


def test_sn_no_predict(founder_su_nghiep):
    """Forbidden predict phrases must not appear in narratives (excluding paradigm_guard
    which intentionally cites negated forms like "KHÔNG dự đoán anh sẽ thành công nghề X")."""
    narrative_text = (
        founder_su_nghiep["cach_cuc_summary"]["narrative"]
        + " " + founder_su_nghiep["closing"]
        + " " + " ".join(p["narrative"] for p in founder_su_nghiep["career_patterns"])
    ).lower()
    forbidden = ["chắc chắn giàu", "chắc chắn thành công", "chắc chắn nghèo"]
    for f in forbidden:
        assert f not in narrative_text


def test_sn_invalid_state_rejected():
    with pytest.raises(ValueError, match="tu_tru"):
        analyze_su_nghiep({})


# ─── Edge cases ─────────────────────────────────────────────────────────────


def test_both_engines_work_for_different_birth():
    """Engines should handle various birth times without crashing."""
    state = cast_bat_tu(
        birth_datetime_local="1995-12-15T08:00",
        timezone="Asia/Ho_Chi_Minh",
        gender="nữ",
    )
    hn = analyze_hon_nhan(state)
    sn = analyze_su_nghiep(state)
    assert hn["method_id"]
    assert sn["method_id"]
    assert hn["cung_phoi"]["branch"]
    assert sn["cach_cuc_summary"]["name"]
