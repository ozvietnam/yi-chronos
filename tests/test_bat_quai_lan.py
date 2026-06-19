"""KIỂM hình học Bát Quái Lăn (八卦滚) — toán quẻ ĐÚNG (đối chiếu tài liệu founder).

Tài liệu founder mô tả đúng khái niệm nhưng VÍ DỤ tính quẻ có lỗi đếm hào.
Các test này khoá toán ĐÚNG (và ghi rõ chỗ tài liệu sai).
"""
from core.hexagram import compose_hexagram_binary as C
from engine.thiet_ban.bat_quai_lan import (
    ho_quai, dao_quai, bien_hao, ten_que, roll_8,
    so_tu_co_ban, quai_trung_so_tu_tru, roll_bat_quai_lan, nguyen_cua_nam,
)


def test_roll_8_khop_vi_du_sach():
    """八卦滚 (图解 tr.97-98): 女 2006 → 地天泰(4410), 年số 57 (下元) →
    8 quẻ = 归妹·大壮·既济·夬·无妄·随·解·兑 (khớp 8/8)."""
    r = roll_8(C("Khôn", "Càn"), 4410, 57)   # 地天泰
    tens = [q["ten"] for q in r["tam_quai"]]
    assert tens == ["Quy Muội", "Đại Tráng", "Ký Tế", "Quải",
                    "Vô Vọng", "Tùy", "Giải", "Đoài"]


def test_nguyen_cua_nam():
    assert nguyen_cua_nam(2006) == "下元" and nguyen_cua_nam(1988) == "下元"
    assert nguyen_cua_nam(1950) == "中元" and nguyen_cua_nam(1900) == "上元"


def test_roll_bat_quai_lan_birth():
    """Trọn 八卦滚 từ giờ sinh → 8 quẻ + base + năm-số (tất định)."""
    r = roll_bat_quai_lan("1988-06-05T23:30", "nam")
    assert len(r["tam_quai"]) == 8 and r["base"]["base_seq"] > 0
    assert r["nguyen"] == "下元"


def test_so_tu_co_ban_4410():
    """八卦基本配数表 (图解 tr.96): 水火既济 = 坎2880+离1530 = 4410; 地天泰 = 坤3960+乾450 = 4410."""
    assert so_tu_co_ban(C("Khảm", "Ly")) == 4410
    assert so_tu_co_ban(C("Khôn", "Càn")) == 4410


def test_quai_trung_khop_cap_kiem_sach():
    """卦中取数法 (图解 tr.95): nam 己丑乙亥癸卯乙卯 → 7198, 7157, 9356, 9363 (khớp 4/4)."""
    pillars = {"year": ("Kỷ", "Sửu"), "month": ("Ất", "Hợi"),
               "day": ("Quý", "Mão"), "hour": ("Ất", "Mão")}
    sos = [r["so"] for r in quai_trung_so_tu_tru(pillars)]
    assert sos == [7198, 7157, 9356, 9363]

BI = C("Càn", "Khôn")  # 天地否


def test_ho_quai_bi_la_tiem():
    """互(天地否) = 风山渐 — tài liệu ĐÚNG ở bước này."""
    assert ten_que(BI) == "Bĩ"
    assert ten_que(ho_quai(BI)) == "Tiệm"


def test_ho_quai_tiem_la_vi_te_KHONG_phai_khue():
    """互(风山渐) = 火水未济 (Vị Tế) — TÀI LIỆU SAI khi nói 火泽睽."""
    tiem = ho_quai(BI)
    assert ten_que(ho_quai(tiem)) == "Vị Tế"


def test_bien_hao_tiem_la_dong_nhan():
    """Biến 风山渐 sơ+tứ (dư 9 = [1,4]) = 天火同人."""
    tiem = ho_quai(BI)
    assert ten_que(bien_hao(tiem, [1, 4])) == "Đồng Nhân"


def test_ho_quai_dong_nhan_la_cau_KHONG_phai_su():
    """互(天火同人) = 天风姤 (Cấu) — TÀI LIỆU SAI khi nói 地水师."""
    dn = bien_hao(ho_quai(BI), [1, 4])
    assert ten_que(ho_quai(dn)) == "Cấu"


def test_dao_quai_tiem_la_co():
    """倒(风山渐) = 山风蛊 (Cổ)."""
    assert ten_que(dao_quai(ho_quai(BI))) == "Cổ"


def test_roll_8_ra_8_que():
    r = roll_8(BI, 4410, 88)
    assert len(r["tam_quai"]) == 8
    assert all(len(q["binary"]) == 6 for q in r["tam_quai"])


def test_base_que_bat_quai_lan_birth():
    """Quẻ cơ bản 八卦滚 từ giờ sinh (后天 lẻ/chẵn) — verify shape."""
    from engine.thiet_ban.bat_quai_lan import base_que_bat_quai_lan
    bq = base_que_bat_quai_lan("1988-06-05T23:30")
    assert len(bq["binary"]) == 6 and bq["ten"] and bq["base_seq"] > 0


def test_dieu_van_48_cong_thuc_khop_cap_kiem():
    """八卦滚 求条文数 (图解 tr.98): công thức + 序数 khớp cặp kiểm 归妹 → 3142 thật."""
    from engine.thiet_ban.bat_quai_lan import dieu_van_48_tu_3he, GUI_MEI_KIEM, seri_so
    from engine.thiet_ban.lap_so import tra_dieu_van
    assert seri_so(C("Chấn", "Đoài")) == 42        # 归妹 震上兑下 序数=42
    sos = dieu_van_48_tu_3he([GUI_MEI_KIEM])
    assert sos == [4287, 4231, 8742, 8731, 3142, 3187]
    assert "水尽山穷" in (tra_dieu_van(3142, prefer_tujie=True) or {}).get("zh", "")
