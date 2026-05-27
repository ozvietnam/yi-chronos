"""Tests for engine.bat_tu.luan_giai — synthesizer engine.

Verifies paradigm tone is preserved, all sections present, founder chart works.
"""
from __future__ import annotations

import pytest

from engine.bat_tu import cast_bat_tu, compose_luan_giai


@pytest.fixture
def founder_state():
    """Founder's authoritative chart: 1988-06-05 23:30 ICT, nam."""
    return cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )


@pytest.fixture
def founder_luan(founder_state):
    return compose_luan_giai(founder_state, current_age=38)


# ─── Structure tests ────────────────────────────────────────────────────────


def test_all_sections_present(founder_luan):
    """All 16 sections of luận giải must be present."""
    required = [
        "method_id", "source_ref", "paradigm_guard",
        "overview", "cuong_do_nhat_chu", "ngu_hanh_balance",
        "cach_cuc_luan", "dung_than_luan", "thap_than_pattern",
        "favorable_combinations", "warnings", "thong_quan",
        "truong_sinh_luan", "than_sat_highlights",
        "dai_van_current", "bo_huong", "closing",
    ]
    for key in required:
        assert key in founder_luan, f"Missing section: {key}"


def test_method_id(founder_luan):
    assert founder_luan["method_id"] == "bat_tu_luan_giai_v1"


def test_source_ref_cites_thieu_vi_hoa(founder_luan):
    assert "Thiệu Vĩ Hoa" in founder_luan["source_ref"]
    assert "Trần Viên" in founder_luan["source_ref"]


# ─── Paradigm tone tests ────────────────────────────────────────────────────


def test_paradigm_guard_no_predict(founder_luan):
    """Paradigm guard must explicitly say KHÔNG predict."""
    guard = founder_luan["paradigm_guard"]
    assert "KHÔNG predict" in guard
    assert "tri mệnh" in guard.lower() or "Tri mệnh" in guard


def test_overview_tone(founder_luan):
    """Overview must NOT predict success/failure."""
    text = founder_luan["overview"]
    # Should mention cấu trúc khí, not predict outcome
    assert "cấu trúc khí" in text or "cấu trúc khí bẩm sinh" in text
    assert "KHÔNG dự đoán" in text or "không dự đoán" in text.lower()
    # Forbidden predict words
    forbidden = ["sẽ giàu", "sẽ nghèo", "sẽ thành công", "sẽ thất bại"]
    for f in forbidden:
        assert f not in text.lower(), f"Forbidden predict phrase: {f}"


def test_closing_paradigm(founder_luan):
    """Closing must emphasize tri mệnh + Bổ, not prediction."""
    closing = founder_luan["closing"]
    assert "Bổ" in closing or "BỔ" in closing
    assert "tri mệnh" in closing.lower() or "Tri mệnh" in closing
    assert "cố kết" in closing  # Mệnh cố kết
    assert "lưu biến" in closing  # Vận lưu biến


# ─── Founder-specific content tests ─────────────────────────────────────────


def test_founder_day_master(founder_state):
    """Founder's Day Master must be Giáp (Mộc)."""
    dm = founder_state["tu_tru"]["day_master"]
    assert dm["stem"] == "Giáp"
    assert dm["element"] == "mộc"


def test_founder_pillars(founder_state):
    """Founder's pillars must match authoritative chart."""
    pillars = founder_state["tu_tru"]["pillars"]
    assert pillars["year"]["stem"] == "Mậu" and pillars["year"]["branch"] == "Thìn"
    assert pillars["month"]["stem"] == "Đinh" and pillars["month"]["branch"] == "Tỵ"
    assert pillars["day"]["stem"] == "Giáp" and pillars["day"]["branch"] == "Tuất"
    assert pillars["hour"]["stem"] == "Giáp" and pillars["hour"]["branch"] == "Tý"


def test_founder_cach_cuc(founder_luan):
    """Founder lands in Thực Thần cách (recognized classical pattern)."""
    cc = founder_luan["cach_cuc_luan"]
    assert cc["present"]
    assert "Thực Thần" in cc["name"]


def test_founder_dung_than(founder_luan):
    """Founder's Dụng Thần = Mộc (Day Master support, since nhược)."""
    dt = founder_luan["dung_than_luan"]
    assert dt["dung"] == "mộc"


def test_founder_favorable_combinations(founder_luan):
    """Founder's chart has Thực Thần chế Sát (Thực + Sát detected)."""
    names = {fc["name"] for fc in founder_luan["favorable_combinations"]}
    assert "Thực Thần chế Sát" in names


def test_founder_warnings_present(founder_luan):
    """Founder's chart has warnings (Day Master nhược + Tài + Quan)."""
    assert len(founder_luan["warnings"]) > 0


def test_founder_dai_van_age_38(founder_luan):
    """At age 38, founder's Đại Vận should be detected."""
    dv = founder_luan["dai_van_current"]
    assert dv.get("current_cycle") is not None
    cycle = dv["current_cycle"]
    assert cycle["start_age"] <= 38 <= cycle["end_age"]


# ─── Bổ Hướng tests ─────────────────────────────────────────────────────────


def test_bo_huong_has_recommend(founder_luan):
    bh = founder_luan["bo_huong"]
    assert "recommend" in bh
    assert "dung" in bh["recommend"]
    rec = bh["recommend"]["dung"]
    assert "nghe_nghiep" in rec and len(rec["nghe_nghiep"]) > 0
    assert "mau_sac" in rec and len(rec["mau_sac"]) > 0
    assert "phuong_vi" in rec and len(rec["phuong_vi"]) > 0
    assert "am_thuc" in rec and len(rec["am_thuc"]) > 0


def test_bo_huong_tranh_for_ky_than(founder_luan):
    """Tránh section must mention Kỵ Thần explicitly."""
    bh = founder_luan["bo_huong"]
    assert bh["tranh"] is not None
    # Kim is Kỵ for founder
    assert bh["tranh"]["element"] == "kim"


# ─── Thap Thần pattern tests ────────────────────────────────────────────────


def test_thap_than_dominant_top_3(founder_luan):
    """Dominant Thập Thần should be at most top 3 by weighted count."""
    tt = founder_luan["thap_than_pattern"]
    assert len(tt["dominant"]) <= 3
    assert len(tt["profiles"]) <= 3


def test_thap_than_profiles_have_both_polarities(founder_luan):
    """Each dominant Thần profile must have tích_cực + tiêu_cực (balanced reading)."""
    for p in founder_luan["thap_than_pattern"]["profiles"]:
        assert p["tich_cuc"]
        assert p["tieu_cuc"]


# ─── Edge cases ─────────────────────────────────────────────────────────────


def test_no_current_age_falls_back_gracefully():
    """Without current_age, dai_van_current should still return a narrative."""
    state = cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    luan = compose_luan_giai(state, current_age=None)
    assert luan["dai_van_current"]["current_cycle"] is None
    assert luan["dai_van_current"]["narrative"]


def test_compose_requires_tu_tru():
    """compose_luan_giai must reject invalid input."""
    with pytest.raises(ValueError, match="tu_tru"):
        compose_luan_giai({}, current_age=30)
