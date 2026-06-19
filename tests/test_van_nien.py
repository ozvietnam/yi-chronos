"""KIỂM 大运取数法 + 流年取数法 — đối chiếu cặp kiểm sách 图解 tr.103."""
from engine.thiet_ban.van_nien import (
    basic_so, _van_dieu_van, year_can_chi, dai_van_thu_so, luu_nien_thu_so,
)


def test_basic_so_khop_4343():
    """基本数 = 月干(千)日干(百)时干(十)年干(个) (大运取数诀): 月甲4·日戊3·时甲4·年癸3 = 4343."""
    assert basic_so("Giáp", "Mậu", "Giáp", "Quý") == 4343


def test_van_dieu_van_cong_thuc():
    """base 4343, 大运 乙卯 (乙=4, 卯=3,8) → 4343+4000+3=8346, +8=8351."""
    assert _van_dieu_van(4343, "Ất", "Mão") == [8346, 8351]


def test_year_can_chi():
    assert year_can_chi(1984) == ("Giáp", "Tý")
    assert year_can_chi(1988) == ("Mậu", "Thìn")


def test_dai_van_from_birth():
    r = dai_van_thu_so("1988-06-05T23:30", "nam")
    assert r["basic_so"] > 0 and len(r["dai_van"]) == 8
    assert all(len(v["dieu_van"]) == 2 for v in r["dai_van"])


def test_luu_nien_from_birth():
    r = luu_nien_thu_so("1988-06-05T23:30", 1, 10)
    assert r["basic_so"] > 0 and len(r["luu_nien"]) == 10
    assert all(1 <= x["dieu_van"][0]["so"] <= 13000 for x in r["luu_nien"])
