"""KIỂM engine lập số Thiết Bản (phái 五音/十二辟卦) — clean-room, đối chiếu tham chiếu.

Cặp kiểm: ví dụ README repo xaminxan/tiebanshenshu (kiểm chéo, repo không LICENSE
→ chỉ dùng làm cặp-kiểm số học; verse dùng DB của ta, đã xác nhận cùng kho).
"""
from engine.thiet_ban.lap_so import lap_thiet_ban_so, tra_dieu_van, NAP_AM, _nhat_menh, _ngu_am


def test_birth_only_1924():
    """Sinh 1924-06-15 16:00 nam — CHỈ giờ sinh (đã bỏ giờ hỏi). 先天命数 11."""
    r = lap_thiet_ban_so("1924-06-15T16:00", "nam")
    assert r["bat_tu_sinh"] == "甲子 庚午 乙丑 甲申"
    assert r["tien_thien_menh_so"] == 11        # birth-only, ổn định
    assert r["ngu_am_so"] == 2 and r["ngu_am"] == "徵"


def test_co_dinh_theo_gio_sinh():
    """KHÔNG còn tham số giờ hỏi: cùng giờ sinh → CÙNG kết quả (THỂ cố định)."""
    a = lap_thiet_ban_so("1988-06-05T23:30", "nam")
    b = lap_thiet_ban_so("1988-06-05T23:30", "nam")
    assert a["ban_menh_so"] == b["ban_menh_so"]
    assert a["thap_nhi_tich_quai"] == b["thap_nhi_tich_quai"]


def test_tien_thien_cong_thuc():
    """先天命数 = tháng + 3 − giờ-chi-số (≤0 → +12). Giờ Thân(9): 5+3−9=−1→11."""
    r = lap_thiet_ban_so("1924-06-15T16:00", "nam")
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


def test_tich_quai_co():
    """辟卦 tra được từ 本命数 birth-only (lá founder 本命802 → 观)."""
    r = lap_thiet_ban_so("1988-06-05T23:30", "nam")
    assert r["ban_menh_so"] == 802
    assert r["thap_nhi_tich_quai"] == "观"


def test_co_che_dieu_van_co_ngu_nghia():
    """基数+序数+秘数 → điều văn DB ta, ĐÚNG NGỮ NGHĨA (复初刻先天2):
    兄弟 offset 2530 → 410+350+2530=3290 → verse VỀ anh em."""
    assert (tra_dieu_van(3290) or {}).get("zh") == "兄弟三人数中注定"
    assert "仁慈" in (tra_dieu_van(1796) or {}).get("zh", "")  # 性格 1036


def test_full_chain_birth_only_co_dieu_van():
    """Lá founder (birth-only) rơi 辟卦 观 có 秘数 → 本命条文 thật từ DB."""
    r = lap_thiet_ban_so("1988-06-05T23:30", "nam")
    assert r["ban_menh_dieu_van"] is not None
    sos = [m["so"] for m in r["ban_menh_dieu_van"]["muc"]]
    assert all(s >= 1000 for s in sos)
    assert any(m["dieu_van"] for m in r["ban_menh_dieu_van"]["muc"])
