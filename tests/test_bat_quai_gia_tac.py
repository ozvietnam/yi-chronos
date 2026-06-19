"""KIỂM 八卦加则法 — đối chiếu cặp kiểm sách 图解 tr.1600-1700.

Ví dụ: 男 癸未 庚申 丁未 丙午 → 年柱 地山谦 → 2472; 月柱 雷天大壮 → 3384.
"""
from engine.thiet_ban.bat_quai_gia_tac import (
    gia_tac_mot_que, bat_quai_gia_tac_tu_tru, bat_quai_gia_tac,
)


def test_gia_tac_nam_tru_khop_2472():
    """癸未 → 坤(干癸)上 艮(支未)下 = 地山谦, tổng 480 → 2×1000+480−8 = 2472."""
    r = gia_tac_mot_que("Quý", "Mùi")
    assert r["que"] == "Khiêm" and r["tong"] == 480 and r["so"] == 2472


def test_gia_tac_nguyet_tru_khop_3384():
    """庚申 → 震(干庚)上 乾(支申)下 = 雷天大壮, tổng 390 → 3×1000+390−6 = 3384."""
    r = gia_tac_mot_que("Canh", "Thân")
    assert r["que"] == "Đại Tráng" and r["tong"] == 390 and r["so"] == 3384


def test_gia_tac_tu_tru_4_que():
    """Trọn tứ trụ ví dụ → 4 quẻ, năm 2472 + tháng 3384 (cặp kiểm 2/2)."""
    pillars = {"year": ("Quý", "Mùi"), "month": ("Canh", "Thân"),
               "day": ("Đinh", "Mùi"), "hour": ("Bính", "Ngọ")}
    rows = bat_quai_gia_tac_tu_tru(pillars)
    assert len(rows) == 4
    assert rows[0]["so"] == 2472 and rows[1]["so"] == 3384
    assert all(1 <= r["so"] <= 13000 for r in rows)


def test_gia_tac_from_birth():
    """Từ giờ sinh — 4 quẻ + tra điều văn (tất định)."""
    r = bat_quai_gia_tac("1988-06-05T23:30")
    assert len(r["quai"]) == 4 and all(q["so"] for q in r["quai"])


def test_phu_mau_sinh_tieu():
    """父母生肖化卦取数 (tr.4253): 父支→上卦, 母支→下卦 → 八卦加则 (lõi đã validate)."""
    from engine.thiet_ban.bat_quai_gia_tac import phu_mau_sinh_tieu
    r = phu_mau_sinh_tieu("Mùi", "Thân")     # 未→艮(上), 申→乾(下) = 山天大畜
    assert r["upper"] == "Cấn" and r["lower"] == "Càn" and 1 <= r["so"] <= 13000
