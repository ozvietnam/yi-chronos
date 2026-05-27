"""Tests for engine.bat_tu.suc_khoe — health + Trung y cross-ref."""
from __future__ import annotations

import pytest

from engine.bat_tu import analyze_suc_khoe, cast_bat_tu


@pytest.fixture
def founder_state():
    return cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )


@pytest.fixture
def founder_sk(founder_state):
    return analyze_suc_khoe(founder_state)


def test_method_id(founder_sk):
    assert founder_sk["method_id"] == "bat_tu_suc_khoe_v1"


def test_paradigm_no_predict(founder_sk):
    assert "KHÔNG dự đoán" in founder_sk["paradigm_guard"]


def test_all_sections(founder_sk):
    required = [
        "method_id", "source_ref", "paradigm_guard",
        "imbalance", "tang_phu_warnings", "constitution",
        "dai_van_health_warnings", "dietary", "lifestyle_narrative",
        "ngu_hanh_table", "closing",
    ]
    for k in required:
        assert k in founder_sk


def test_founder_imbalance_detected(founder_sk):
    """Founder has Thổ excess + Kim deficient."""
    imb = founder_sk["imbalance"]
    excess_els = {e["element"] for e in imb["excess"]}
    deficient_els = {d["element"] for d in imb["deficient"]}
    assert "thổ" in excess_els
    assert "kim" in deficient_els


def test_founder_tang_phu_warnings_present(founder_sk):
    """Must produce warnings for thổ + kim."""
    warnings = founder_sk["tang_phu_warnings"]
    assert len(warnings) >= 2
    tangs = {w["tang"] for w in warnings}
    assert "Tỳ" in tangs  # Thổ excess
    assert "Phế" in tangs  # Kim deficient


def test_founder_constitution_mộc_nhược(founder_sk):
    """Day Master Mộc, nhược."""
    c = founder_sk["constitution"]
    assert c["element"] == "mộc"
    assert c["tag"] == "weak"
    assert c["primary_tang"] == "Can"


def test_founder_dai_van_warnings_kim(founder_sk):
    """Đại Vận Canh Thân + Tân Dậu (Kim = Kỵ) → cảnh báo Phế."""
    warnings = founder_sk["dai_van_health_warnings"]
    assert len(warnings) >= 1
    for w in warnings:
        assert w["ky_element"] == "kim"
        assert w["tang_at_risk"] == "Phế"


def test_founder_dietary_dung_moc(founder_sk):
    """Dụng Thần Mộc → diet xanh chua."""
    d = founder_sk["dietary"]["by_dung_than"]
    assert d["element"] == "mộc"
    assert "chua" in d["vi"]
    assert len(d["thuc_pham"]) >= 3


def test_founder_lifestyle_present(founder_sk):
    assert founder_sk["lifestyle_narrative"]
    assert len(founder_sk["lifestyle_narrative"]) > 30


def test_ngu_hanh_table_5_elements(founder_sk):
    """Full 5 elements table."""
    table = founder_sk["ngu_hanh_table"]
    assert len(table) == 5
    els = {row["element"] for row in table}
    assert els == {"mộc", "hỏa", "thổ", "kim", "thủy"}
    for row in table:
        assert row["tang"]
        assert row["phu"]


def test_other_chart_works():
    state = cast_bat_tu(
        birth_datetime_local="1995-08-15T14:00",
        timezone="Asia/Ho_Chi_Minh",
        gender="nữ",
    )
    sk = analyze_suc_khoe(state)
    assert sk["method_id"]


def test_invalid_state_rejected():
    with pytest.raises(ValueError, match="tu_tru"):
        analyze_suc_khoe({})
