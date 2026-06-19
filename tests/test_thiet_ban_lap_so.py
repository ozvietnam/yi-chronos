"""KIỂM engine lập số Thiết Bản (phái 五音/十二辟卦) — clean-room, đối chiếu tham chiếu.

Cặp kiểm: ví dụ README repo xaminxan/tiebanshenshu (kiểm chéo, repo không LICENSE
→ chỉ dùng làm cặp-kiểm số học; verse dùng DB của ta, đã xác nhận cùng kho).
"""
from engine.thiet_ban.lap_so import (
    lap_thiet_ban_so, tra_dieu_van, tra_luu_nien, luu_nien_chain,
    NAP_AM, _nhat_menh, _ngu_am,
)


def test_luu_nien_lookup_khop_anchor():
    """流年 (字母,岁)→条文: 福|1 tuổi → 1141+992 = 2133 → DB 并蒂双莲."""
    r = tra_luu_nien("福", 1)
    assert r["so"] == 2133
    assert "并蒂双莲" in (r["dieu_van"] or "")


def test_luu_nien_chain_letter_walk():
    """Letter-walk đầy đủ (validate VÀNG: 108/108 chữ cái khớp engine repo tieban).
    Lá founder: 先天6 后天8 初刻, tam-hợp 申子辰, khởi 3, age1 → chữ 桃 #2408."""
    r = luu_nien_chain("1988-06-05T23:30", "nam", max_age=108)
    assert r["tien_thien_menh_so"] == 6 and r["hau_thien_menh_so"] == 8
    assert r["nhom_tam_hop"] == "申子辰" and r["khoi_dau_so"] == 3
    a1 = r["luu_nien"][0]
    assert a1["thanh"] == "五" and a1["marker"] == "水" and a1["chu_cai"] == "桃" and a1["so"] == 2408
    # phủ điều văn cao
    assert sum(1 for x in r["luu_nien"] if x["so"]) >= 100


def test_luu_nien_tuoi_nhung_khop():
    """Tự-kiểm: tuổi tính ra KHỚP tuổi GHI trong điều văn.
    Đa bản: 图解 ghi tuổi ở CỘT (（1）), DB cũ nhét vào câu (一岁) — chấp nhận cả hai."""
    CN = {1: "一", 28: "二十八"}
    r = luu_nien_chain("1988-06-05T23:30", "nam", max_age=30)
    rows = {x["tuoi"]: x for x in r["luu_nien"]}

    def khop_tuoi(x, n):
        blob = (x.get("dieu_van") or "") + (x.get("age_marks") or "")
        return str(n) in blob or CN[n] in blob

    assert khop_tuoi(rows[1], 1)
    assert khop_tuoi(rows[28], 28)


def test_luu_nien_co_dinh_theo_sinh():
    """流年 TẤT ĐỊNH theo giờ sinh — cùng input, cùng kết quả."""
    a = luu_nien_chain("1990-03-20T08:00", "nữ", max_age=20)
    b = luu_nien_chain("1990-03-20T08:00", "nữ", max_age=20)
    assert [x["so"] for x in a["luu_nien"]] == [x["so"] for x in b["luu_nien"]]


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
    import re
    _strip = lambda s: re.sub(r"[，。、；！？\s]", "", s or "")  # noqa: E731
    assert _strip((tra_dieu_van(3290) or {}).get("zh")) == "兄弟三人数中注定"
    assert "仁慈" in (tra_dieu_van(1796) or {}).get("zh", "")  # 性格 1036 (图解 trống→DB)


def test_full_chain_birth_only_co_dieu_van():
    """Lá founder (birth-only) rơi 辟卦 观 có 秘数 → 本命条文 thật từ DB."""
    r = lap_thiet_ban_so("1988-06-05T23:30", "nam")
    assert r["ban_menh_dieu_van"] is not None
    sos = [m["so"] for m in r["ban_menh_dieu_van"]["muc"]]
    assert all(s >= 1000 for s in sos)
    assert any(m["dieu_van"] for m in r["ban_menh_dieu_van"]["muc"])
