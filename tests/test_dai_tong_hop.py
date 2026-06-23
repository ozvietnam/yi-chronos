"""Test đại tổng hợp lá số — kết tinh 40 vòng đọc Đằng Sơn (founder anchor)."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.usefixtures("as_owner")

from engine.tu_vi import cast_la_so
from engine.tu_vi.dai_tong_hop import dai_tong_hop


@pytest.fixture
def founder_la_so():
    # Founder 1988-06-05 23:30 giờ Tý sớm → cast lunar 4/22 (lăn ngày 6/6), nam, Mậu Thìn.
    return cast_la_so(lunar_month=4, lunar_day=22, hour_branch="Tý",
                      year_stem="Mậu", year_branch="Thìn", gender="nam")


def test_co_snapshot_founder(founder_la_so):
    d = dai_tong_hop(founder_la_so)["co"]
    assert d["menh_branch"] == "Tỵ"
    assert d["cuc"] == 5
    assert d["menh_truong_sinh_stage"] == "Tuyệt"     # Mệnh tại Tuyệt = tuyệt-xứ-phùng-sinh
    assert "Thiên Tướng" in d["menh_stars"]


def test_the_dung_hau_thien_founder(founder_la_so):
    d = dai_tong_hop(founder_la_so)["the_dung_hau_thien"]
    assert d["the"]["sao"] == "Vũ Khúc"               # THỂ tiên thiên
    assert "Thiên Tướng" in d["dung"]["sao"]          # DỤNG diện mạo
    assert d["hau_thien"]["sao"] == "Văn Xương"       # hậu thiên = trục văn-học


def test_cua_tu_cluster_founder(founder_la_so):
    d = dai_tong_hop(founder_la_so)["cua_tu"]
    assert d["menh_branch"] == "Tỵ"
    # 4 sao cửa-tu hội tụ Mệnh: Thiên Tướng + Thiên Không + Thiếu Dương + Cô Thần
    assert set(d["stars_present"]) == {"Thiên Tướng", "Thiên Không", "Thiếu Dương", "Cô Thần"}
    assert d["count"] == 4


def test_tu_mo_tu_duong_founder(founder_la_so):
    d = dai_tong_hop(founder_la_so)["tu_mo_tu_duong"]
    assert d["is_tu_mo_year"] is True                 # năm Thìn = tứ mộ
    assert d["cua_khong_colocated_corner"] is True
    assert d["corner"] == "Tỵ"
    assert d["reading"] is not None


def test_tuan_triet_menh_thong_founder(founder_la_so):
    d = dai_tong_hop(founder_la_so)["tuan_triet"]
    assert d["menh_thong"] is True                    # Mệnh Tỵ ngoài cả Tuần (Tuất-Hợi) lẫn Triệt (Tý-Sửu)


def test_can_bang_trung_thuc_has_both(founder_la_so):
    d = dai_tong_hop(founder_la_so)["can_bang"]
    assert len(d["sang"]) >= 2                        # có tín hiệu sáng
    assert len(d["xau_nhe"]) >= 1                     # TRUNG THỰC nêu xấu-nhẹ (không tô hồng)
    # xấu-nhẹ phải gồm Khôi-Triệt (nhịp đứt-nối tài lộc)
    assert any("Khôi" in x and "Triệt" in x for x in d["xau_nhe"])


def test_disclaimer_present(founder_la_so):
    d = dai_tong_hop(founder_la_so)
    assert "KHÔNG PREDICT" in d["disclaimer"]
    assert "disposition" in d["disclaimer"]
