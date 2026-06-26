"""Test tín hiệu cung Phu Thê (đào hoa / độc thân cộng dồn / duyên xa) — kênh #3 P2."""
from engine.tu_vi.phu_the_signals import read_phu_the_signals, CAVEAT


def _lsi(*, menh="ty", phu_the="ngo", thien_di="ty_", than=None,
         pt_chinh=None, pt_phu=None, menh_phu=None, tuan=None, triet=None, tu_hoa=None):
    # chi hợp lệ: dùng ty/suu/dan... ; 'ty_' chỉ placeholder để khác
    fn = {"menh": menh, "phu_the": phu_the, "thien_di": thien_di}
    return {
        "chinh_tinh_per_palace": {phu_the: pt_chinh or []},
        "phu_tinh_per_palace": {phu_the: pt_phu or [], menh: menh_phu or []},
        "vong_sao_per_palace": {},
        "fn_to_chi": fn, "menh_palace": menh, "than_palace": than,
        "tuan_chi": tuan or [], "triet_chi": triet or [], "tu_hoa": tu_hoa or [],
    }


def test_caveat_va_khong_phan_nhan_pham():
    r = read_phu_the_signals(_lsi())
    assert r["caveat"] == CAVEAT
    assert "không phán" in r["caveat"].lower() and "định mệnh" in r["caveat"].lower()


def test_dao_hoa_field_detected():
    """Phu Thê có chính tinh đào hoa + đào-hồng phụ → trường đào hoa, KHÔNG nói ngoại tình."""
    r = read_phu_the_signals(_lsi(pt_chinh=["liem_trinh", "tham_lang"],
                                  pt_phu=["dai_hao", "hong_loan"]))
    dh = r["dao_hoa_field"]
    assert dh and dh["muc"] == "mạnh"
    assert "không phải dấu hiệu phản bội" in dh["mo_ta"].lower()
    assert "hanh_dong" in dh


def test_dao_hoa_none_khi_khong_co():
    r = read_phu_the_signals(_lsi(pt_chinh=["thai_duong"], pt_phu=[]))
    assert r["dao_hoa_field"] is None


def test_doc_than_cong_don_3_yeu_to():
    """Cô Thần (Mệnh) + Tuần (Phu Thê) + Hóa Kỵ (Thiên Di) → 3 yếu tố, mức khá rõ."""
    r = read_phu_the_signals(_lsi(
        menh="ty", phu_the="ngo", thien_di="dan",
        menh_phu=["co_than"], tuan=["ngo"],
        tu_hoa=[{"hoa": "hoa_ky", "palace_fn": "thien_di"}]))
    dt = r["doc_than_risk"]
    assert dt["so_yeu_to"] == 3 and "khá rõ" in dt["muc"]


def test_doc_than_1_yeu_to_nhe():
    r = read_phu_the_signals(_lsi(phu_the="ngo", triet=["ngo"]))
    dt = r["doc_than_risk"]
    assert dt["so_yeu_to"] == 1 and "nhẹ" in dt["muc"]
    assert "ế" not in dt["muc"]  # KHÔNG dùng từ "ế"


def test_duyen_xa_than_cu_thien_di():
    r = read_phu_the_signals(_lsi(thien_di="dan", than="dan"))
    assert r["duyen_xa"] and "phương xa" in r["duyen_xa"]["mo_ta"]


def test_duyen_xa_none_khi_than_khac():
    r = read_phu_the_signals(_lsi(thien_di="dan", than="ty"))
    assert r["duyen_xa"] is None


def test_founder_real_chart():
    from engine.tu_vi.from_birth import cast_la_so_from_birth
    from engine.tu_vi.la_so_input_builder import build_la_so_input
    ls = cast_la_so_from_birth(birth_datetime_local="1988-06-05T23:30:00",
                               timezone="Asia/Ho_Chi_Minh", gender="nam")
    lsi = build_la_so_input(ls, "nam", birth_year=1988, now_year=2026)
    r = read_phu_the_signals(lsi)
    assert r["phu_the_chi"] == "mao"  # Phu Thê founder tại Mão
    assert r["doc_than_risk"]["so_yeu_to"] >= 0  # không crash
    assert r["caveat"]
