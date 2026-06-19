"""Test khoá luật 起数 ĐỌC ĐÚNG BẢN GỐC + engine luận lá số con cái.

Nguồn luật: 《邵康节说易·铁板神数》Càn Tập, origin.pdf tr.9-10 (đọc thẳng scan, 2026-06-18).
Bản gốc IN CHỈNH TỀ — cái "mờ" cũ là lỗi pipeline MinerU, không phải sách.
"""
from engine.thiet_ban.khoi_so import (
    DIA_CHI_QUAI, HA_LAC_CAN, HA_LAC_CHI, NGU_HO_DON, NHAT_CHU_QUAI,
    an_than_menh, phoi_tru,
)
from engine.tu_vi.gia_dao import _doc_cung_tre, _doi_chieu_bo_me, luan_la_so_con


# ════════ 起数 — luật đọc đúng bản gốc ════════
def test_dia_chi_quai_la_7can_8doai():
    """Bản gốc chép '七艮八兑九离' — KHÔNG phải chuẩn 7兑8艮. Khoá đúng bản."""
    assert DIA_CHI_QUAI["Sửu"] == ("Cấn", 7)
    assert DIA_CHI_QUAI["Thân"] == ("Đoài", 8)
    assert DIA_CHI_QUAI["Ngọ"] == ("Ly", 9)
    assert DIA_CHI_QUAI["Tý"] == ("Khảm", 1)


def test_ha_lac_phoi_so():
    """河洛配数: 甲己子午9, 乙庚丑未8, 丙辛寅申7, 丁壬卯酉6, 戊癸辰戌5, 巳亥4."""
    assert HA_LAC_CAN["Giáp"] == 9 and HA_LAC_CAN["Kỷ"] == 9
    assert HA_LAC_CAN["Mậu"] == 5 and HA_LAC_CAN["Quý"] == 5
    assert HA_LAC_CHI["Tý"] == 9 and HA_LAC_CHI["Ngọ"] == 9
    assert HA_LAC_CHI["Tỵ"] == 4 and HA_LAC_CHI["Hợi"] == 4


def test_ngu_ho_don():
    """五虎遁 khởi tháng Giêng theo can năm."""
    assert NGU_HO_DON["Giáp"] == "Bính" and NGU_HO_DON["Kỷ"] == "Bính"
    assert NGU_HO_DON["Đinh"] == "Nhâm" and NGU_HO_DON["Nhâm"] == "Nhâm"


def test_nhat_chu_quai():
    assert NHAT_CHU_QUAI["Hợi"] == "Khảm" and NHAT_CHU_QUAI["Tý"] == "Khảm"
    assert NHAT_CHU_QUAI["Mão"] == "Càn" and NHAT_CHU_QUAI["Dậu"] == "Càn"


def test_an_than_menh_gio_ty():
    """安身命: giờ Tý → Mệnh = Thân = cung tháng (nghịch/thuận 0 bước)."""
    r = an_than_menh(5, "Tý")
    assert r["menh_chi"] == r["than_chi"] == r["month_palace_chi"] == "Ngọ"


def test_an_than_menh_nghich_thuan():
    """Giờ khác Tý: Mệnh nghịch, Thân thuận từ cung tháng."""
    r = an_than_menh(1, "Mão")  # tháng Giêng = Dần; giờ Mão (h=3)
    assert r["month_palace_chi"] == "Dần"
    assert r["menh_chi"] == "Hợi"   # Dần lùi 3 = Hợi
    assert r["than_chi"] == "Tỵ"    # Dần tiến 3 = Tỵ


def test_phoi_tru_shape():
    out = phoi_tru("Giáp", "Tý")
    assert out["can_quai"] == "Càn" and out["chi_quai"] == "Khảm"
    assert out["ha_lac_can_so"] == 9 and out["chi_hado_so"] == 6


# ════════ Luận lá số con — engine thuần (không cần sxtwl) ════════
def _fake_ls():
    """la_so_input tối giản: chính tinh theo cung chức năng + fn_to_chi."""
    return {
        "chinh_tinh_per_palace": {
            "menh": ["that_sat"], "phu_mau": ["thien_co"],
            "phuc_duc": ["tu_vi"], "tat_ach": ["thien_tuong"],
            "quan_loc": ["van_khong_co"],  # sao lạ → lọc ra → coi như vô chính diệu
        },
        "phu_tinh_per_palace": {"menh": ["van_xuong"]},
        "fn_to_chi": {"menh": "ty", "phu_mau": "suu", "phuc_duc": "dan",
                      "tat_ach": "mao", "huynh_de": "thin", "quan_loc": "ti"},
    }


def test_doc_cung_tre_co_sao():
    c = _doc_cung_tre(_fake_ls(), "menh")
    assert c["vo_chinh_dieu"] is False
    assert "Thất Sát" in c["chinh_tinh"]
    assert c["khi_chat"] and c["nuoi"]


def test_doc_cung_tre_vo_chinh_dieu():
    c = _doc_cung_tre(_fake_ls(), "huynh_de")  # không có sao → vô chính diệu
    assert c["vo_chinh_dieu"] is True
    assert "môi trường" in c["nuoi"]


def test_doi_chieu_bo_me_sinh_va_khac():
    # con cần Thủy: Bố Kim (Kim sinh Thủy) = nguồn nuôi; Mẹ Thổ (Thổ khắc Thủy) = khắc nhẹ
    out = _doi_chieu_bo_me(["Thủy"], "Hỏa",
                           [{"vai": "Bố", "hanh": "Kim"}, {"vai": "Mẹ", "hanh": "Thổ"}])
    assert out["con_can"] == "Thủy"
    rel = {x["vai"]: x["quan_he"] for x in out["doi_chieu"]}
    assert rel["Bố"] == "sinh con"
    assert rel["Mẹ"] == "khắc nhẹ"


def test_luan_la_so_con_shape():
    out = luan_la_so_con(_fake_ls(), {}, parents=[{"vai": "Bố", "hanh": "Mộc"}])
    assert len(out["cung"]) == 6
    assert "paradigm" in out and "không phán" in out["paradigm"].lower()
    assert out["van_tinh"] and out["van_tinh"]["co_van_tinh"]  # Văn Xương ở Mệnh
    # child_pillars rỗng → bat_tu chỉ có note, không có truong_bo_me
    assert "note" in out["bat_tu"]
    assert "truong_bo_me" not in out
