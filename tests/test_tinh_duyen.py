"""Tests cho engine.tinh_duyen.read_tinh_duyen (nữ mệnh, deterministic)."""

from __future__ import annotations

import json

import pytest

from engine.tinh_duyen import read_tinh_duyen
from engine.tinh_duyen.reading import (
    METHOD_ID,
    _FORBIDDEN_CONDEMNATION,
    _has_forbidden,
    _in_prohibition_frame,
    _scrub,
)

# TẦNG (a) — KẾT ÁN ĐẠO ĐỨC vô giá trị phân tích: KHÔNG được xuất hiện như verdict
# (chỉ hợp lệ khi nằm trong KHUNG BIỆN-CHÍNH 'không phải số làm lẽ…'). Iron Rule
# #4/#6/#8 + CLAUDE.md. ('khắc phu/khắc chồng/sát phu' KHÔNG còn ở đây — chúng là
# KHÁI NIỆM PHÂN TÍCH Tử Bình 伤官见官, chỉ cấm khi phán-vào-người.)
FORBIDDEN_CONDEMNATION = [
    "làm gái", "dâm xướng", "dâm tiện", "dâm đãng", "kỹ nữ",
    "làm thiếp", "làm lẽ", "hạ tiện", "mưu hại", "đắc thê tài", "thê hiền",
]

# Lời-PHÁN-VÀO-NGƯỜI (verdict định mệnh hướng thẳng chủ thể) — TUYỆT ĐỐI cấm,
# kể cả khi dùng khái niệm phân tích 'khắc chồng/cô quả' với chủ-ngữ-người + giọng phán.
FORBIDDEN_PERSON_VERDICTS = [
    "em sẽ khắc chồng", "số cô quả", "chắc chắn ly hôn", "mệnh em là khắc chồng",
    "sẽ không lấy được chồng",
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
    # KEY MỚI: chẩn đoán cấp độ thử thách (giữ mọi key cũ).
    "chan_doan_cap_do",
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


# --------------------------------------------------------------------------- #
# HÀNG RÀO CỨNG — paradigm (Iron Rule #4/#6/#8, CLAUDE.md CẤM TUYỆT ĐỐI)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("birth", FEMALE_CHARTS)
def test_no_condemnation_verdict_in_output(birth):
    """Cụm KẾT ÁN đạo đức (làm gái/dâm/làm lẽ/hạ tiện…) chỉ được phép xuất hiện khi
    nằm trong KHUNG BIỆN-CHÍNH (bác bỏ); KHÔNG bao giờ là verdict trần."""
    res = read_tinh_duyen(birth, gender="nữ", as_of_year=2026)

    def walk(o):
        if isinstance(o, str):
            yield o
        elif isinstance(o, dict):
            for v in o.values():
                yield from walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                yield from walk(v)

    for s in walk(res):
        low = s.lower()
        cond = [w for w in FORBIDDEN_CONDEMNATION if w in low]
        if cond:
            assert _in_prohibition_frame(low), \
                f"{birth}: kết án TRẦN (không biện-chính): {cond} | {s[:120]}"


@pytest.mark.parametrize("birth", FEMALE_CHARTS)
def test_no_person_directed_verdict_in_output(birth):
    """Lời-PHÁN-VÀO-NGƯỜI ('em sẽ khắc chồng', 'số cô quả') TUYỆT ĐỐI không lọt output
    DƯỚI DẠNG VERDICT TRẦN. Cho phép khi nằm trong khung BIỆN-CHÍNH (bác bỏ định kiến —
    Iron Rule #5 tiếc dê tiếc lễ), nhưng KHÔNG được phán trần vào chủ thể."""
    res = read_tinh_duyen(birth, gender="nữ", as_of_year=2026)

    def walk(o):
        if isinstance(o, str):
            yield o
        elif isinstance(o, dict):
            for v in o.values():
                yield from walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                yield from walk(v)

    for s in walk(res):
        low = s.lower()
        hits = [w for w in FORBIDDEN_PERSON_VERDICTS if w in low]
        if hits:
            assert _in_prohibition_frame(low), \
                f"{birth}: verdict phán-vào-người TRẦN: {hits} | {s[:120]}"


@pytest.mark.parametrize("birth", FEMALE_CHARTS)
def test_thuong_quan_step_preserved(birth):
    """REGRESSION (bug cũ): bước Thương Quan KHÔNG bị scrub xoá trắng — phải còn
    ten_buoc + luận THẬT (gọi tên cấu trúc khắc Quan như khái niệm phân tích)."""
    res = read_tinh_duyen(birth, gender="nữ", as_of_year=2026)
    b3 = res["quy_trinh_day_du"]["bat_tu_10_buoc"]["buoc"][2]
    # Tên bước phải là ngôn ngữ phân tích trung tính, KHÔNG bị thay placeholder.
    assert b3["ten_buoc"].startswith("3."), f"{birth}: bước 3 sai nhãn"
    assert "Thương Quan" in b3["ten_buoc"]
    assert "đã được lược" not in b3["ten_buoc"], f"{birth}: bước 3 bị scrub xoá trắng!"
    # Luận phải còn nội dung phân tích thật (không phải placeholder).
    assert "đã được lược" not in b3["luan"], f"{birth}: luận bước 3 bị scrub!"
    assert "Thương Quan" in b3["luan"]


@pytest.mark.parametrize("birth", FEMALE_CHARTS)
def test_stage_not_none_for_marriageable_ages(birth):
    """Tuổi 13-44 PHẢI ra một stage cụ thể (KHÔNG None)."""
    res = read_tinh_duyen(birth, gender="nữ", as_of_year=2026)
    age = res["input"]["tuoi"]
    if 13 <= age <= 44:
        assert res["stage"]["stage_id"] is not None, \
            f"{birth} (tuổi {age}): stage_id None — regression!"
        assert res["stage"]["stage_id"], f"{birth}: stage_id rỗng"
        assert res["stage"]["tuoi_min"] <= age <= res["stage"]["tuoi_max"]


def test_stage_2009_05_10_is_rung_dong_dau():
    """REGRESSION cụ thể: lá nữ 2009-05-10 (tuổi ~17) -> 'rung-dong-dau', KHÔNG None."""
    res = read_tinh_duyen("2009-05-10T08:00", gender="nữ", as_of_year=2026)
    assert res["stage"]["stage_id"] == "rung-dong-dau"


@pytest.mark.parametrize("birth", FEMALE_CHARTS)
def test_cach_cuc_surfaces_bien_chinh(birth):
    """Mỗi mục cách cục surface PHẢI có field 'bien_chinh' (đọc đồng dạng)
    không rỗng — KHÔNG surface raw han_tu/y_nghia_duyen thô."""
    res = read_tinh_duyen(birth, gender="nữ", as_of_year=2026)
    for c in res["cach_cuc"]:
        assert "bien_chinh" in c, f"{birth}/{c.get('ten_cach')}: thiếu 'bien_chinh'"
        assert c["bien_chinh"], f"{birth}/{c.get('ten_cach')}: 'bien_chinh' rỗng"
        # KHÔNG còn surface raw thô.
        assert "han_tu" not in c
        assert "y_nghia_goc_tham_khao" not in c


@pytest.mark.parametrize("birth", FEMALE_CHARTS)
def test_no_male_gender_cach_in_female_output(birth):
    """Mục cách cục gioi_tinh='nam' bị LOẠI khỏi output nữ mệnh."""
    res = read_tinh_duyen(birth, gender="nữ", as_of_year=2026)
    nams = [c["ten_cach"] for c in res["cach_cuc"] if c.get("gioi_tinh") == "nam"]
    assert nams == [], f"{birth}: lọt cách góc nhìn nam: {nams}"


def test_scrub_blocks_person_directed_verdict():
    """_scrub thay string PHÁN-VÀO-NGƯỜI bằng bản trung tính (chủ-ngữ-người + giọng phán)."""
    dirty = "Em sẽ khắc chồng, chắc chắn cô quả."
    out = _scrub(dirty)
    assert out != dirty
    assert "đã được lược" in out
    assert _has_forbidden(dirty) is True


def test_scrub_blocks_condemnation_word():
    """_scrub LUÔN chặn kết án đạo đức trần (không có khung biện-chính)."""
    dirty = "Nữ mệnh này làm lẽ, hạ tiện."
    assert _has_forbidden(dirty) is True
    assert _scrub(dirty) != dirty


def test_scrub_keeps_analytic_concept():
    """KHÁI NIỆM PHÂN TÍCH ('Thương Quan khắc Quan', 'khắc phu' trung tính) KHÔNG bị scrub.

    Đây là CORE của fix: 'khắc phu/khắc chồng' khi là khái niệm phân tích (không
    chủ-ngữ-người, không giọng phán) phải GIỮ NGUYÊN để luận thật."""
    concept = ("Thương Quan khắc Quan (伤官见官) — với nữ mệnh là khí khắc phu, "
               "cấu trúc cần chế hóa qua Ấn/Tài.")
    assert _has_forbidden(concept) is False
    assert _scrub(concept) == concept


def test_scrub_keeps_bien_chinh_frame():
    """Khung BIỆN-CHÍNH bác bỏ verdict (Iron Rule #5) KHÔNG bị scrub tự huỷ."""
    bien = "Cổ cho là 'số làm lẽ' nhưng KHÔNG phải số làm lẽ — nay là sống chung không cưới."
    assert _in_prohibition_frame(bien.lower()) is True
    assert _scrub(bien) == bien

    clean = "Cấu trúc khí này độc lập, vận hành tốt khi theo nghề chuyên chú."
    assert _scrub(clean) == clean
    assert _has_forbidden(clean) is False


@pytest.mark.parametrize("birth", FEMALE_CHARTS)
def test_scrub_caution_count_present(birth):
    """Output có cờ caution scrub_caution_count (int >= 0)."""
    res = read_tinh_duyen(birth, gender="nữ", as_of_year=2026)
    assert "scrub_caution_count" in res
    assert isinstance(res["scrub_caution_count"], int)
    assert res["scrub_caution_count"] >= 0


@pytest.mark.parametrize("birth", FEMALE_CHARTS)
def test_sources_all_six_named(birth):
    """_collect_sources in nguồn THẬT cho cả 6 file (mỗi entry có ': <nguồn>')."""
    res = read_tinh_duyen(birth, gender="nữ", as_of_year=2026)
    srcs = res["sources"]
    assert len(srcs) == 6
    for s in srcs:
        assert ": " in s, f"{birth}: nguồn thiếu nội dung thật -> {s!r}"
