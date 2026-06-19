"""KIỂM 考刻 乾坤流度数法 — đối chiếu cặp kiểm sách 图解 tr.2197."""
from engine.thiet_ban.kao_khac import (
    cast_que_kao_khac, phu_mau_hao, kao_khac_cha_me, doi_chieu_luc_than,
    LUU_DO_CAN, LUU_DO_KHON,
)


def test_cast_que_kao_khac_giap_ty():
    """甲子 → 河洛: 甲6,子(1,6); lẻ{1}=1→坎(上), chẵn{6,6}=12→2→坤(dưới) = 水地比."""
    binary, odd, even = cast_que_kao_khac("Giáp", "Tý")
    assert binary == "010000" and odd == 1 and even == 12   # 坎上坤下 = Tỷ


def test_phu_mau_hao_ty_cua_bi():
    """水地比 (坤宫土) → 父母爻 = hào 2 (乙巳, 巳火 sinh thổ)."""
    assert phu_mau_hao("010000") == "Tỵ"


def test_luu_do_arithmetic_va_cap_kiem():
    """流度 密数 (图解 tr.4611-4661): 乾=9003+i×50, 坤=9605+i×50."""
    assert LUU_DO_CAN["Tý"] == 9003 and LUU_DO_CAN["Ngọ"] == 9303
    assert LUU_DO_CAN["Tỵ"] == 9253                 # cặp kiểm: 乾宫[巳]=9253
    assert LUU_DO_KHON["Tỵ"] == 9855                # cặp kiểm: 坤宫[巳]=9855
    assert LUU_DO_KHON["Hợi"] == 10155              # 坤宫[亥]=10155 (母命猪年 ✓ DB)


def test_kao_khac_cha_me_khop_sach():
    """Trọn phép: 年柱甲子 → 父母爻巳 → cha 乾宫9253 (sinh tiêu 蛇/Rắn)."""
    r = kao_khac_cha_me("Giáp", "Tý")
    assert r["que"] == "Tỷ" and r["phu_mau_chi"] == "Tỵ"
    assert r["cha"]["mat_so"] == 9253 and "蛇" in r["cha"]["sinh_tieu"]
    assert r["me"]["mat_so"] == 9855


def test_doi_chieu_luc_than_khop():
    """Gia đạo: cha sinh năm Tỵ (rắn) → KHỚP 乾宫流度 sơ khắc."""
    r = doi_chieu_luc_than("Giáp", "Tý", cha_chi="Tỵ")
    assert r["ket_qua"] == "khớp" and any("CHA" in k for k in r["khop"])


def test_doi_chieu_luc_than_lech():
    """Cha KHÁC sinh tiêu sơ-khắc → báo cần dò khắc (考刻 sâu), không bịa khớp."""
    r = doi_chieu_luc_than("Giáp", "Tý", cha_chi="Tý", me_chi="Sửu")
    assert r["ket_qua"] == "lệch sơ-khắc"


def test_kao_khac_from_birth_founder():
    """考刻 từ giờ sinh lá Anh (1988-06-05T23:30) → 年柱 戊辰 → cha/mẹ tuổi 龙."""
    from engine.thiet_ban.kao_khac import kao_khac_from_birth
    r = kao_khac_from_birth("1988-06-05T23:30")
    assert r["nam_tru"] == "Mậu Thìn" and r["phu_mau_chi"] == "Thìn"
    assert "龙" in r["cha"]["dieu_van_chuan"]


def test_kao_khac_from_birth_doi_chieu():
    """Cấp sinh tiêu cha = Thìn (rồng) → KHỚP sơ-khắc; cha = Tý → lệch."""
    from engine.thiet_ban.kao_khac import kao_khac_from_birth
    assert kao_khac_from_birth("1988-06-05T23:30", cha_chi="Thìn")["ket_qua"] == "khớp"
    assert kao_khac_from_birth("1988-06-05T23:30", cha_chi="Tý")["ket_qua"] == "lệch sơ-khắc"
