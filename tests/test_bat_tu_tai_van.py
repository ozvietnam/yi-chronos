"""Tests for engine.bat_tu.tai_van — Tài Vận analysis."""
from __future__ import annotations

import pytest

from engine.bat_tu import analyze_tai_van, cast_bat_tu


@pytest.fixture
def founder_state():
    return cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )


@pytest.fixture
def founder_tv(founder_state):
    return analyze_tai_van(founder_state)


# ─── Structure ──────────────────────────────────────────────────────────────


def test_method_id(founder_tv):
    assert founder_tv["method_id"] == "bat_tu_tai_van_v1"


def test_source_ref_cites_thieu_vi_hoa(founder_tv):
    assert "Thiệu Vĩ Hoa" in founder_tv["source_ref"]


def test_all_sections(founder_tv):
    required = [
        "method_id", "source_ref", "paradigm_guard",
        "tai_map", "dm_tai_balance", "patterns", "sources",
        "dai_van_tai_timing", "strategy", "closing",
    ]
    for key in required:
        assert key in founder_tv


def test_paradigm_no_predict(founder_tv):
    assert "KHÔNG dự đoán" in founder_tv["paradigm_guard"]


# ─── Founder-specific ───────────────────────────────────────────────────────


def test_founder_tai_map_chinh_tai(founder_tv):
    """Founder has 1 Chính Tài (Đinh hỏa, tàng Trụ Tháng Ngọ), no Thiên Tài."""
    tm = founder_tv["tai_map"]
    assert tm["total_chinh_tai"] == 1
    assert tm["total_thien_tai"] == 0


def test_founder_dm_tai_balance_warning(founder_tv):
    """Day Master Nhâm nhược → cần cứu thân trước khi gánh Tài."""
    balance = founder_tv["dm_tai_balance"]
    assert "nhược — Cần cứu thân trước" in balance["status"]


def test_founder_patterns_include_tai_quan(founder_tv):
    """Founder must detect Tài-Quan tương sinh pattern."""
    names = {p["name"] for p in founder_tv["patterns"]}
    assert "Tài-Quan tương sinh" in names


def test_founder_patterns_thuc_thuong_sinh_tai(founder_tv):
    """Founder also has Thực Thương + Tài → Thực Thương sinh Tài."""
    names = {p["name"] for p in founder_tv["patterns"]}
    assert "Thực Thương sinh Tài" in names


def test_founder_kiep_tai_warning(founder_tv):
    """Founder has Kiếp Tài + Tài → cảnh báo."""
    names = {p["name"] for p in founder_tv["patterns"]}
    assert "Kiếp Tài đoạt Tài" in names


def test_founder_sources_chinh_tai(founder_tv):
    """Founder's source is Chính Tài (only Chính Tài present, no Thiên)."""
    sources = founder_tv["sources"]
    types = [s["type"] for s in sources]
    assert "Chính Tài" in types


def test_founder_dai_van_timing_8_cycles(founder_tv):
    """Founder Đại Vận has 8 cycles → all should be evaluated."""
    timing = founder_tv["dai_van_tai_timing"]
    assert len(timing) == 8
    for c in timing:
        assert c["verdict"] in {"tài lộc kích hoạt", "tài lộc bình", "tài lộc yên"}
        assert c["mark"] in {"✦", "·", "○"}
        assert "score" in c


def test_founder_strategy_has_warnings(founder_tv):
    """Founder cấu hình Kiếp Tài đoạt Tài should produce warning strategy."""
    strategy = founder_tv["strategy"]
    assert len(strategy) >= 2
    # Should have at least one warning (⚠)
    warnings = [s for s in strategy if s.startswith("⚠")]
    assert len(warnings) >= 1


# ─── Other charts ───────────────────────────────────────────────────────────


def test_other_chart_works():
    state = cast_bat_tu(
        birth_datetime_local="1995-08-15T14:00",
        timezone="Asia/Ho_Chi_Minh",
        gender="nữ",
    )
    tv = analyze_tai_van(state)
    assert tv["method_id"]
    assert tv["tai_map"]["total_count"] >= 0


def test_invalid_state_rejected():
    with pytest.raises(ValueError, match="tu_tru"):
        analyze_tai_van({})


# ─── Patterns logic ─────────────────────────────────────────────────────────


def test_patterns_have_actionable(founder_tv):
    """Each pattern must include actionable advice."""
    for p in founder_tv["patterns"]:
        assert p.get("actionable")
        assert len(p["actionable"]) > 30


def test_no_predict_phrases(founder_tv):
    """Forbidden predict phrases must not appear (excl paradigm_guard)."""
    narrative_text = (
        founder_tv["dm_tai_balance"]["narrative"]
        + " " + founder_tv["closing"]
        + " " + " ".join(p["narrative"] for p in founder_tv["patterns"])
    ).lower()
    forbidden = ["chắc chắn giàu", "sẽ giàu năm", "chắc chắn phá sản"]
    for f in forbidden:
        assert f not in narrative_text
