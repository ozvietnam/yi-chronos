"""Tests cho engine.tinh_duyen.tuvi_process.doc_tuvi_12_buoc.

3 lá NỮ thật, kiểm: đủ 12 bước, không crash, mỗi bước đủ contract field,
paradigm đọc-đồng-dạng (không câu predict), mức độ ảnh hưởng gán đúng theo doc #1.
"""
from __future__ import annotations

import pytest

from engine.tu_vi.from_birth import cast_la_so_from_birth
from engine.tinh_duyen.tuvi_process import (
    doc_tuvi_12_buoc,
    doc_tuvi_12_buoc_from_birth,
    TRUC_TIEP,
    GIAN_TIEP,
    TIEM_AN,
)

# 3 lá số NỮ (giờ sinh dương lịch, true-solar adjust trong engine)
_BIRTHS = [
    "1988-06-05T23:30",   # cùng ngày founder, đọc as nữ
    "1995-03-12T08:15",
    "2000-11-20T14:45",
]

_REQUIRED_KEYS = {"ten_buoc", "sao_chinh", "du_lieu", "luan",
                  "_nguon", "muc_do_anh_huong"}
_VALID_MUC_DO = {TRUC_TIEP, GIAN_TIEP, TIEM_AN}

# Mức ảnh hưởng kỳ vọng theo doc #1 (thứ tự bước 1..12).
_EXPECTED_MUC_DO = [
    TRUC_TIEP,  # 1 Phu Thê
    GIAN_TIEP,  # 2 tam chiếu
    GIAN_TIEP,  # 3 Quan Lộc xung
    GIAN_TIEP,  # 4 stub đôi
    GIAN_TIEP,  # 5 đại vận
    TIEM_AN,    # 6 lưu niên
    GIAN_TIEP,  # 7 Tử Tức
    TIEM_AN,    # 8 Điền Trạch
    TIEM_AN,    # 9 Nô Bộc
    TIEM_AN,    # 10 Tật Ách
    TIEM_AN,    # 11 Tài Bạch
    GIAN_TIEP,  # 12 Mệnh
]


@pytest.fixture(params=_BIRTHS)
def la_so_nu(request):
    return cast_la_so_from_birth(
        birth_datetime_local=request.param, gender="nữ",
    )


def test_du_12_buoc_khong_crash(la_so_nu):
    res = doc_tuvi_12_buoc(la_so_nu, gender="nữ", as_of_year=2026)
    assert res["method_id"] == "tinh_duyen_tuvi_12_buoc_v1"
    assert len(res["buoc"]) == 12


def test_moi_buoc_du_contract(la_so_nu):
    res = doc_tuvi_12_buoc(la_so_nu, gender="nữ")
    for i, b in enumerate(res["buoc"], 1):
        assert _REQUIRED_KEYS <= set(b.keys()), f"bước {i} thiếu field"
        assert b["muc_do_anh_huong"] in _VALID_MUC_DO
        assert isinstance(b["luan"], str) and len(b["luan"]) > 10
        assert isinstance(b["du_lieu"], dict)
        assert b["_nguon"], f"bước {i} thiếu _nguon"


def test_muc_do_anh_huong_gan_dung(la_so_nu):
    res = doc_tuvi_12_buoc(la_so_nu, gender="nữ")
    got = [b["muc_do_anh_huong"] for b in res["buoc"]]
    assert got == _EXPECTED_MUC_DO


def test_buoc_1_la_phu_the_truc_tiep(la_so_nu):
    res = doc_tuvi_12_buoc(la_so_nu, gender="nữ")
    b1 = res["buoc"][0]
    assert "Phu Thê" in b1["ten_buoc"]
    assert b1["muc_do_anh_huong"] == TRUC_TIEP
    assert "chi" in b1["du_lieu"]


def test_buoc_9_no_boc_nguoi_thu_ba(la_so_nu):
    res = doc_tuvi_12_buoc(la_so_nu, gender="nữ")
    b9 = res["buoc"][8]
    assert "Nô Bộc" in b9["ten_buoc"]
    assert "THỨ BA" in b9["ten_buoc"].upper() or "thứ ba" in b9["luan"].lower()


def test_buoc_4_la_stub(la_so_nu):
    res = doc_tuvi_12_buoc(la_so_nu, gender="nữ")
    b4 = res["buoc"][3]
    assert "STUB" in b4["ten_buoc"].upper()
    assert b4["du_lieu"].get("trang_thai") == "chua_co_la_so_doi"


def test_paradigm_khong_boi(la_so_nu):
    """KHÔNG xuất hiện câu predict cứng (Iron Rule #4/#6/#8)."""
    res = doc_tuvi_12_buoc(la_so_nu, gender="nữ")
    blob = " ".join(b["luan"] for b in res["buoc"]).lower()
    for cam in ("sẽ ly hôn", "chắc chắn", "số phải", "định mệnh là"):
        assert cam not in blob, f"phát hiện câu bói cấm: {cam}"
    assert "động từ" in res["paradigm"] or "đồng dạng" in res["paradigm"]


def test_from_birth_helper():
    res = doc_tuvi_12_buoc_from_birth(
        birth_datetime_local="1995-03-12T08:15", gender="nữ", as_of_year=2026,
    )
    assert len(res["buoc"]) == 12
    assert "la_so" in res
    assert res["la_so"]["gender"] == "nữ"
