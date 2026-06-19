"""KIỂM hình học Bát Quái Lăn (八卦滚) — toán quẻ ĐÚNG (đối chiếu tài liệu founder).

Tài liệu founder mô tả đúng khái niệm nhưng VÍ DỤ tính quẻ có lỗi đếm hào.
Các test này khoá toán ĐÚNG (và ghi rõ chỗ tài liệu sai).
"""
from core.hexagram import compose_hexagram_binary as C
from engine.thiet_ban.bat_quai_lan import (
    ho_quai, dao_quai, bien_hao, ten_que, roll_8, base_que_from_bat_tu,
    so_tu_co_ban, quai_trung_so_tu_tru,
)


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


def test_base_que_birth_only():
    """Quẻ cơ bản từ giờ sinh (太玄 mod-8) — verify được, không lỗi."""
    bq = base_que_from_bat_tu("1988-06-05T23:30")
    assert len(bq["binary"]) == 6 and bq["ten"]
