"""Tests cho engine.tinh_duyen.read_tinh_duyen (nữ mệnh, deterministic)."""

from __future__ import annotations

import json

import pytest

from engine.tinh_duyen import read_tinh_duyen
from engine.tinh_duyen.reading import METHOD_ID, _has_forbidden, _scrub

# Danh sách CẤM (verdict) — KHÔNG được xuất hiện trong OUTPUT (Iron Rule #4/#6/#8,
# CLAUDE.md). 'cô quả/cô đơn/cô độc' KHÔNG nằm đây vì hợp lệ trong câu biện chính.
FORBIDDEN_VERDICTS = [
    "khắc chồng", "sát chồng", "sát phu", "khắc phu", "mưu hại",
    "làm gái", "hạ tiện", "dâm xướng", "dâm tiện", "dâm đãng",
    "kỹ nữ", "làm thiếp", "làm lẽ", "khắc tử", "hình khắc tử",
    "hình phu", "đắc thê tài", "thê hiền",
]

# 5 lá NỮ trải tuổi 13-44 (gồm 2009-05-10 Thất Sát + 1985-11-02 Liêm Phá).
FEMALE_CHARTS = [
    "2009-05-10T08:00",   # ~17, Mệnh có Thất Sát
    "1985-11-02T10:00",   # ~41, Liêm Phá
    "2000-03-15T14:30",   # ~26
    "1995-07-07T06:00",   # ~31
    "1988-06-05T23:30",   # ~38
]

# (birth, as_of_year, expected_age_approx, expected_stage_id)
CASES = [
    ("2009-05-10T08:00", 2026, 17, "rung-dong-dau"),       # ~17 -> chặng cấp 3
    ("2000-03-15T14:30", 2026, 26, "chon-ban-doi"),        # ~26
    ("1990-08-20T10:30", 2026, 36, "lam-lai-tai-hop"),     # ~36
]

REQUIRED_KEYS = {
    "method_id", "input", "stage", "personality", "cung_phu_the_tuvi",
    "batu_hon_nhan", "song_phai_reconcile", "cach_cuc", "dinh_thoi",
    "base_12_khia_canh", "paradigm_ok", "sources", "_disclaimer",
}


@pytest.mark.parametrize("birth,as_of,age,stage_id", CASES)
def test_basic_structure(birth, as_of, age, stage_id):
    res = read_tinh_duyen(birth, gender="nữ", as_of_year=as_of)

    # Đủ khóa.
    assert REQUIRED_KEYS.issubset(res.keys()), \
        f"thiếu khóa: {REQUIRED_KEYS - set(res.keys())}"

    assert res["method_id"] == METHOD_ID == "tinh_duyen_nu_menh_v1"

    # Tuổi tính đúng (cho phép ±1 do sinh nhật).
    assert abs(res["input"]["tuoi"] - age) <= 1
    assert abs(res["stage"]["tuoi"] - age) <= 1

    # Stage khớp tuổi.
    assert res["stage"]["stage_id"] == stage_id
    assert res["stage"]["tuoi_min"] <= res["stage"]["tuoi"] <= res["stage"]["tuoi_max"]

    # personality.menh_chinh_tinh là list (có thể rỗng nếu vô chính diệu).
    assert isinstance(res["personality"]["menh_chinh_tinh"], list)

    # cách cục là list.
    assert isinstance(res["cach_cuc"], list)

    # paradigm_ok True.
    assert res["paradigm_ok"] is True

    # reconcile có 8 chủ đề.
    assert len(res["song_phai_reconcile"]) == 8

    # base 12 khía cạnh.
    assert len(res["base_12_khia_canh"]) == 12

    # cung phu the có branch.
    assert res["cung_phu_the_tuvi"]["phu_the_branch"]

    # batu hôn nhân: có đếm 官杀.
    assert "tong_quan_sat" in res["batu_hon_nhan"]["quan_sat_count"]

    # sources không rỗng.
    assert res["sources"]


def test_personality_menh_chinh_tinh_matches_la_so():
    """menh_chinh_tinh trong output phải khớp chính tinh tại cung Mệnh của lá số."""
    from engine.tu_vi.from_birth import cast_la_so_from_birth

    birth = "1990-08-20T10:30"
    la = cast_la_so_from_birth(birth_datetime_local=birth, gender="nữ")
    expected = sorted(s for s, i in la["chinh_tinh"].items() if i == la["menh_index"])

    res = read_tinh_duyen(birth, gender="nữ", as_of_year=2026)
    assert sorted(res["personality"]["menh_chinh_tinh"]) == expected


def test_different_age_different_stage():
    """Hai lá tuổi khác nhau -> stage khác nhau."""
    young = read_tinh_duyen("2009-05-10T08:00", gender="nữ", as_of_year=2026)
    older = read_tinh_duyen("1990-08-20T10:30", gender="nữ", as_of_year=2026)
    assert young["stage"]["stage_id"] != older["stage"]["stage_id"]


def test_no_crash_all_cases():
    """Không lá nào crash; cách cục luôn là list; dinh_thoi có khóa mong đợi."""
    for birth, as_of, _, _ in CASES:
        res = read_tinh_duyen(birth, gender="nữ", as_of_year=as_of)
        assert isinstance(res["cach_cuc"], list)
        assert "nam_kich_hoat" in res["dinh_thoi"]
        assert "nam_can_giu_gin" in res["dinh_thoi"]
        # disclaimer paradigm.
        assert "KHÔNG bói" in res["_disclaimer"]
