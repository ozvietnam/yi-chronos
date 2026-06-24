"""Tests cho engine.tinh_duyen.batu_process — 10 BƯỚC tình duyên Bát Tự (nữ mệnh).

Kiểm 3 lá NỮ khác nhau, mỗi lá phải đủ 10 bước có schema chuẩn + grounded _nguon
+ tuân paradigm (KHÔNG bói, KHÔNG phán định mệnh).
"""
from __future__ import annotations

import pytest

from engine.bat_tu.cast import cast_bat_tu
from engine.tinh_duyen.batu_process import METHOD_ID, doc_batu_10_buoc

# 3 lá NỮ MỆNH (ngày sinh khác nhau để phủ nhiều cấu trúc 官杀/伤官).
_BIRTHS = [
    ("1988-06-05T23:30", 2026),   # Nhâm Thìn — thân nhược, 官杀 vượng
    ("1990-03-08T14:00", 2026),   # lá khác
    ("1995-11-20T07:15", 2026),   # lá thứ 3
]

_MUC_DO_HOP_LE = {"truc_tiep", "gian_tiep", "tiem_an"}

# Cụm verdict TUYỆT ĐỐI cấm xuất hiện trong luận (paradigm Iron Rule #4/#6/#8).
_FORBIDDEN = (
    "sẽ ly hôn", "chắc chắn ly", "số khắc chồng", "số góa", "số cô quả",
    "sẽ giàu", "sẽ nghèo", "định mệnh đã định",
)


@pytest.fixture(params=_BIRTHS, ids=["la1_nham_thin", "la2", "la3"])
def nu_state(request):
    birth, _year = request.param
    return cast_bat_tu(
        birth_datetime_local=birth,
        timezone="Asia/Ho_Chi_Minh",
        gender="nữ",
    ), request.param[1]


@pytest.fixture
def result(nu_state):
    state, year = nu_state
    return doc_batu_10_buoc(state, gender="nữ", as_of_year=year)


# --------------------------------------------------------------------------- #
def test_method_id(result):
    assert result["method_id"] == METHOD_ID


def test_co_du_10_buoc(result):
    assert len(result["buoc"]) == 10


def test_thu_tu_10_buoc_dung(result):
    """10 bước đúng thứ tự 1→10 theo nhãn 'ten_buoc'."""
    for i, b in enumerate(result["buoc"], start=1):
        assert b["ten_buoc"].startswith(f"{i}."), f"Bước {i} sai nhãn: {b['ten_buoc']}"


def test_moi_buoc_dung_schema(result):
    """Mỗi bước phải có {ten_buoc, du_lieu, luan, muc_do_anh_huong, _nguon}."""
    for b in result["buoc"]:
        assert set(b) >= {"ten_buoc", "du_lieu", "luan", "muc_do_anh_huong", "_nguon"}
        assert isinstance(b["du_lieu"], dict)
        assert isinstance(b["luan"], str) and b["luan"].strip()
        assert b["muc_do_anh_huong"] in _MUC_DO_HOP_LE


def test_moi_buoc_co_nguon_grounded(result):
    """Mỗi bước phải GROUND ít nhất 1 nguồn (_nguon non-empty) — không bịa."""
    for b in result["buoc"]:
        assert isinstance(b["_nguon"], list)
        assert len(b["_nguon"]) >= 1, f"Bước {b['ten_buoc']} thiếu nguồn"
        assert all(isinstance(n, str) and n.strip() for n in b["_nguon"])


def test_du_3_muc_do_anh_huong(result):
    """Toàn bộ 10 bước phải phủ đủ 3 loại mức độ ảnh hưởng."""
    seen = {b["muc_do_anh_huong"] for b in result["buoc"]}
    assert seen == _MUC_DO_HOP_LE, f"Thiếu mức độ: {_MUC_DO_HOP_LE - seen}"


def test_buoc1_la_truc_tiep_quan_sat(result):
    """Bước 1 (Nhật chủ + Phu Thê tinh) phải là ảnh hưởng TRỰC TIẾP."""
    assert result["buoc"][0]["muc_do_anh_huong"] == "truc_tiep"
    assert "nhat_chu" in result["buoc"][0]["du_lieu"]


def test_buoc3_thuong_quan_co_lo_tang(result):
    """Bước 3 phải có cấu trúc lộ/tàng cho Thương Quan."""
    du = result["buoc"][2]["du_lieu"]
    assert "lo" in du and "tang" in du and "thuong_quan" in du


def test_buoc8_ngu_hanh_thieu_co_hanh_chong_con(result):
    """Bước 8 phải suy ra hành chồng (官杀) + hành con (Thực Thương) theo Nhật chủ."""
    du = result["buoc"][7]["du_lieu"]
    assert du["hanh_chong"] and du["hanh_con"]
    assert du["hanh_chong"] != du["hanh_con"]


def test_paradigm_khong_boi(result):
    """KHÔNG cụm phán định mệnh / tiên tri nào lọt vào LUẬN của các bước.

    (Disclaimer cố ý TRÍCH các cụm cấm để CẤM chúng — nên không quét disclaimer.)
    """
    blob = " ".join(b["luan"] for b in result["buoc"]).lower()
    for bad in _FORBIDDEN:
        assert bad not in blob, f"Lọt verdict cấm: {bad!r}"


def test_disclaimer_la_paradigm_guard(result):
    """Disclaimer phải nêu rõ KHÔNG bói + mệnh là động từ (Iron Rule #8)."""
    d = result["_disclaimer"].lower()
    assert "không bói" in d and "động từ" in d


def test_cross_grounding_co_mat(result):
    assert "cross_grounding" in result
    assert set(result["cross_grounding"]) >= {"nu_menh", "hon_nhan", "luc_than_phu_tu"}


def test_input_co_nhat_chu_nhat_chi(result):
    inp = result["input"]
    assert inp["nhat_chu"] and inp["nhat_chi"]
