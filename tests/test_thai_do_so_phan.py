"""(d) Engine hiện thực Phần II sách 《Tử Vi Tính Được》 — hồ sơ THÁI ĐỘ SỐ PHẬN.

Tính được cái TÍNH (thế đứng vận hành), KHÔNG predict (Iron #4/#6/#8). Embedding 14
chính tinh vào không-gian-thái-độ 3 trục chính (Định–Biến, Thụ–Tác, Nội–Ngoại) +
trục 4 (Cá-nhân–Siêu) cho Tả/Hữu. Tất định + đọc-đồng-dạng.
"""
from __future__ import annotations

import engine.tu_vi.thai_do_so_phan as M

_14 = ["tu_vi", "thien_co", "thai_duong", "vu_khuc", "thien_dong", "liem_trinh",
       "thien_phu", "thai_am", "tham_lang", "cu_mon", "thien_tuong", "thien_luong",
       "that_sat", "pha_quan"]


def test_du_14_chinh_tinh_co_vector():
    for s in _14:
        assert s in M.STARS, f"thiếu vector sao {s}"
        v = M.STARS[s]
        assert {"dinh_bien", "thu_tac", "noi_ngoai"} <= set(v)
        for ax in ("dinh_bien", "thu_tac", "noi_ngoai"):
            assert -1.0 <= v[ax] <= 1.0


def test_vu_khuc_doi_cuc_cu_mon():
    """Kiểm chứng nội tại Phần II: Vũ Khúc (Định-Tác-Nội) đối cực Cự Môn (Biến-Thụ-Ngoại)."""
    vk, cm = M.STARS["vu_khuc"], M.STARS["cu_mon"]
    assert vk["dinh_bien"] > 0 > cm["dinh_bien"]
    assert vk["thu_tac"] > 0 > cm["thu_tac"]
    assert vk["noi_ngoai"] > 0 > cm["noi_ngoai"]


def test_ho_so_tat_dinh_va_co_cau_truc():
    chart = {"menh": ["vu_khuc"], "quan_loc": ["thien_phu"]}
    r1 = M.ho_so_thai_do(chart)
    r2 = M.ho_so_thai_do(chart)
    assert r1 == r2, "phải tất định (cùng input → cùng output)"
    assert {"profile", "dominant", "paradigm"} <= set(r1)
    # Vũ Khúc + Thiên Phủ đều "Định" → trục dinh_bien dương
    assert r1["profile"]["dinh_bien"] > 0


def test_menh_trong_so_cao_hon_cung_phu():
    a = M.ho_so_thai_do({"menh": ["pha_quan"], "no_boc": ["thien_phu"]})
    b = M.ho_so_thai_do({"menh": ["thien_phu"], "no_boc": ["pha_quan"]})
    # Phá Quân (Biến cực) ở Mệnh → a "Biến" hơn b rõ rệt
    assert a["profile"]["dinh_bien"] < b["profile"]["dinh_bien"]


def test_paradigm_khong_predict():
    import engine.hermes_guard as g
    r = M.ho_so_thai_do({"menh": ["pha_quan"]})
    text = (r.get("dominant", "") + " " + r.get("paradigm", ""))
    assert not g.paradigm_violations(text), "output KHÔNG được mang giọng tiên tri"


def test_lazy_empty_chart_khong_no():
    r = M.ho_so_thai_do({})
    assert "profile" in r  # rỗng → profile 0, không ném
