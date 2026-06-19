"""KIỂM 元会运世法 — đối chiếu cặp kiểm sách 图解 tr.99-100.

Ví dụ: 男 乙亥 丁亥 壬子 辛亥. 太玄: 乙8亥4 丁6亥4 壬6子9 辛7亥4.
"""
from engine.thiet_ban.nguyen_hoi_van_the import tinh_so, _dao, nguyen_hoi_van_the


def test_dao():
    assert _dao(15) == 51 and _dao(11) == 11 and _dao(18) == 81


def test_tinh_so_khop_cap_kiem_sach():
    """男 乙亥丁亥壬子辛亥 → 元会基本数1210, 运世5111, 基本数一9210, 基本数二1111,
    8 条文 [9810,9270,9217,9216] + [1711,1171,1118,1117] (图解 tr.99-100)."""
    s = tinh_so(8, 4, 6, 4, 6, 9, 7, 4)              # yc yz mc mz dc dz hc hz
    assert s["nguyen"] == 12 and s["hoi"] == 10 and s["van"] == 15 and s["the"] == 11
    assert s["nguyen_hoi_co_ban"] == 1210 and s["van_the_co_ban"] == 5111
    assert s["co_ban_mot"] == 9210 and s["co_ban_hai"] == 1111
    assert s["so_nguyen_hoi"] == [9810, 9270, 9217, 9216]
    assert s["so_van_the"] == [1711, 1171, 1118, 1117]


def test_gioi_han_13000():
    """基本数二 >13000 thì −12000: vt_co_ban 5111 + 年干8×1000 = 13111 → 1111."""
    s = tinh_so(8, 4, 6, 4, 6, 9, 7, 4)
    assert s["co_ban_hai"] == 1111                   # 13111 − 12000


def test_from_birth_tat_dinh():
    """Từ giờ sinh — tất định, có 8 条文 (4+4) + nối Nguyên-Hội-Vận-Thế."""
    r = nguyen_hoi_van_the("1988-06-05T23:30", "Asia/Ho_Chi_Minh")
    assert len(r["dieu_van_nguyen_hoi"]) == 4 and len(r["dieu_van_van_the"]) == 4
    assert all(1 <= x["so"] <= 13000 for x in r["dieu_van_nguyen_hoi"])
    assert r["nguyen_so"] and r["co_ban_mot"]
