"""KIỂM engine lập số Thiết Bản (phái 五音/十二辟卦) — clean-room, đối chiếu tham chiếu.

Cặp kiểm: ví dụ README repo xaminxan/tiebanshenshu (kiểm chéo, repo không LICENSE
→ chỉ dùng làm cặp-kiểm số học; verse dùng DB của ta, đã xác nhận cùng kho).
"""
from engine.thiet_ban.lap_so import lap_thiet_ban_so, NAP_AM, _nhat_menh, _ngu_am


def test_readme_example_1924():
    """Sinh 1924-06-15 16:00 nam, hỏi 2025-04-20 10:00 → 先天11 · 五音2 · 本命344."""
    r = lap_thiet_ban_so("1924-06-15T16:00", "nam", "2025-04-20T10:00")
    assert r["bat_tu_sinh"] == "甲子 庚午 乙丑 甲申"
    assert r["tien_thien_menh_so"] == 11
    assert r["ngu_am_so"] == 2 and r["ngu_am"] == "徵"
    assert r["nhat_menh"] == 4 and r["thoi_van"] == 3
    assert r["khao_khac"] == "初刻"
    assert r["ban_menh_so"] == 344
    assert r["hau_thien_menh_so"] == 3


def test_tien_thien_cong_thuc():
    """先天命数 = tháng + 3 − giờ-chi-số (≤0 → +12). Giờ Thân(9): 5+3−9=−1→11."""
    r = lap_thiet_ban_so("1924-06-15T16:00", "nam", "2025-04-20T10:00")
    assert r["tien_thien_menh_so"] == 11


def test_nap_am_60_day_du():
    assert len(NAP_AM) == 60
    assert NAP_AM["甲子"] == "金" and NAP_AM["乙丑"] == "金"
    assert NAP_AM["戊辰"] == "木" and NAP_AM["庚午"] == "土"


def test_nhat_menh_khop_bang_14_5():
    """日命 ((can+nạp-âm) mod5)+1: 金×甲=4, 水×甲=1, 土×甲=5."""
    assert _nhat_menh("金", "甲") == 4
    assert _nhat_menh("水", "甲") == 1
    assert _nhat_menh("土", "甲") == 5
    assert _nhat_menh("金", "己") == 4


def test_ngu_am_phoi():
    """五音 cong=11, can năm 甲 (nhóm 甲己) → 徵(2)."""
    am, so = _ngu_am(11, "甲")
    assert am == "徵" and so == 2
