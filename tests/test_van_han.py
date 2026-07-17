"""Vận hạn GROUNDED — engine.tu_vi.van_han. Xương tất định + Thể-Dụng + Tứ Hóa rọi cung
+ nội dung sao CHỈ từ founder_verified=1 (quote-or-silence). 0 LLM ở tầng engine.
"""
from engine.tu_vi.from_birth import cast_la_so_from_birth
from engine.tu_vi import van_han as vh
from engine.tu_vi.an_sao import BRANCHES_TVI


def _founder():
    return cast_la_so_from_birth(birth_datetime_local="1988-06-05T23:30:00", gender="nam")


def test_dai_van_block_the_dung_va_tu_hoa():
    r = _founder()
    d = vh.dai_van_block(r, 4)
    assert d["available"] and d["tang"] == "dai_van"
    assert d["khoang_tuoi"] == [35, 44]           # verify khớp lá số founder
    assert d["cung_the"] and d["vi_tri"] in BRANCHES_TVI
    # Tứ Hóa đại vận: đủ 4 hóa, mỗi hóa rọi 1 cung
    hoa = {h["hoa"] for h in d["tu_hoa_van"]}
    assert hoa == {"Lộc", "Quyền", "Khoa", "Kỵ"}
    assert d["nguyen_tac"]["nguon"]               # nguyên tắc Thể-Dụng có nguồn


def test_vo_chinh_dieu_muon_sao_xung():
    """Cung vận Vô Chính Diệu → mượn sao cung xung (đối diện +6)."""
    r = _founder()
    d = vh.dai_van_block(r, 4)                     # founder c4 = Thân, Vô Chính Diệu
    if d["sao_muon_xung"]:
        assert d["sao"], "mượn xung phải có sao"
        assert "xung" in d["dien_giai_the_dung"].lower()


def test_luu_nien_luu_nguyet_tuan_deterministic():
    r = _founder()
    n = vh.luu_nien_block(r, 2026)
    assert n["year_can_chi"] == "Bính Ngọ" and n["vi_tri"] == "Ngọ"   # 2026 = Bính Ngọ
    g = vh.luu_nguyet_block(r, 2026, 9)
    assert g["tang"] == "luu_nguyet" and g["month"] == 9
    # lưu nguyệt Mệnh khởi Đẩu Quân lưu niên (chi năm) + thuận (month-1)
    expect = BRANCHES_TVI[(BRANCHES_TVI.index("Ngọ") + 8) % 12]
    assert g["vi_tri"] == expect
    t = vh.tuan_block(r, 2026, 9, 3)
    assert t["tuan"] == 3 and "Hạ tuần" in t["tuan_label"]
    # tuần dịch thuận từ lưu nguyệt Mệnh
    assert t["vi_tri"] == BRANCHES_TVI[(BRANCHES_TVI.index(g["vi_tri"]) + 2) % 12]


def test_grounded_chi_lay_founder_verified_1():
    """Nội dung sao PHẢI có nguồn (từ fv=1); rỗng thì chua_co_nguon=True (không bịa)."""
    r = _founder()
    for blk in [vh.dai_van_block(r, 4), vh.luu_nien_block(r, 2026),
                vh.luu_nguyet_block(r, 2026, 9), vh.tuan_block(r, 2026, 9, 1)]:
        for s in blk["sao_nguon"]:
            assert s["dich"] and s["nguon"] and s["sao"]     # mỗi trích có nguồn
        assert blk["chua_co_nguon"] == (len(blk["sao_nguon"]) == 0)


def test_overview_skeleton_tat_dinh():
    """Overview 12 đại vận + N năm — skeleton tất định (0 LLM), khớp lá số founder."""
    r = _founder()
    dv = vh.dai_van_overview(r)
    assert len(dv["cycles"]) == len(r["dai_van"])
    assert dv["cycles"][0]["start_age"] == r["dai_van"][0]["start_age"]
    for c in dv["cycles"]:
        assert c["cung_the"] and c["branch"] in BRANCHES_TVI
    ln = vh.luu_nien_overview(r, 2026, 2030)
    assert len(ln["years"]) == 5
    assert ln["years"][0]["year"] == 2026 and ln["years"][0]["year_can_chi"] == "Bính Ngọ"
    for y in ln["years"]:
        assert y["cung_the"]


def test_luu_nhat_block_lich_am_va_tu_hoa_ngay():
    """Lưu Nhật: solar→âm (sxtwl) + lưu nhật Mệnh = lưu nguyệt Mệnh + (ngày âm-1) thuận,
    Tứ Hóa theo CAN NGÀY. Có nguồn cổ pháp 'lưu nguyệt khởi mùng một'."""
    r = _founder()
    b = vh.luu_nhat_block(r, 2026, 9, 15)
    assert b["available"] and b["tang"] == "luu_nhat"
    assert 1 <= b["lunar_day"] <= 30 and b["day_can"]
    assert b["vi_tri"] in BRANCHES_TVI and b["cung_the"]
    assert {h["hoa"] for h in b["tu_hoa_van"]} == {"Lộc", "Quyền", "Khoa", "Kỵ"}
    assert "vi mô" in b["luu_y_vi_mo"].lower()
    # dispatch
    assert vh.build_block(r, "luu_nhat", year=2026, month=9, day=15)["vi_tri"] == b["vi_tri"]


def test_cung_van_rules_grounded_list():
    """#3: nguyên tắc đọc-cung-theo-vận = LIST CÓ NGUỒN (từ van_han_nguon atomize + duyệt,
    fallback seed hardcoded). Mỗi rule kèm nguồn; cung chưa trích → [] (quote-or-silence)."""
    r = _founder()
    from engine.tu_vi.van_han import _CUNG_VAN_NGHIA, _the_dung_block, _cung_van_rules
    for cung, v in _CUNG_VAN_NGHIA.items():
        assert v["rule"] and v["nguon"]                 # seed hardcoded có nguồn
    seen_some = False
    for bi in range(12):
        blk = _the_dung_block(r, bi, "Đại Vận")
        cvr = blk.get("cung_van_rules")
        assert isinstance(cvr, list)
        for x in cvr:                                   # mỗi rule PHẢI có nguồn
            assert x["rule"] and x["nguon"]
        if cvr:
            seen_some = True
    assert seen_some
    # tang filter: rule 'all' hoặc khớp tang; không lẫn tầng khác
    for x in _cung_van_rules("Tật Ách", "luu_nien"):
        assert x["tang"] in ("all", "luu_nien")


def test_tam_phuong_tu_chinh_hoi_chieu():
    """Cổ pháp 'còn phải xem lục xung tam hợp chiếu': mỗi block có hoi_chieu = đối cung
    (xung +6) + 2 cung tam hợp (±4), KHÔNG đọc cung lẻ."""
    r = _founder()
    for blk in [vh.dai_van_block(r, 4), vh.luu_nien_block(r, 2026),
                vh.luu_nguyet_block(r, 2026, 9), vh.tuan_block(r, 2026, 9, 2)]:
        hc = blk["hoi_chieu"]
        assert len(hc) == 3
        i = BRANCHES_TVI.index(blk["vi_tri"])
        offs = sorted((BRANCHES_TVI.index(h["vi_tri"]) - i) % 12 for h in hc)
        assert offs == [4, 6, 8]                     # 2 tam hợp + 1 xung
        assert any("xung" in h["quan_he"] for h in hc)
        for h in hc:
            assert h["cung"] and isinstance(h["sao"], list)


def test_luu_nguyet_overview_va_thang_nhuan():
    """#2 overview 12 tháng tất định + #3 tháng nhuận đúng (sxtwl quét ngày)."""
    r = _founder()
    o = vh.luu_nguyet_overview(r, 2025)
    assert len(o["months"]) == 12
    assert o["months"][0]["month"] == 1 and o["months"][0]["cung_the"]
    # 2025 (Ất Tỵ) có tháng nhuận 6; 2026/2027 không
    assert vh._leap_month_of(2025) == 6
    assert vh._leap_month_of(2026) == 0 and vh._leap_month_of(2027) == 0
    assert vh._leap_month_of(2028) == 5
    assert o["thang_nhuan"] == 6 and o["thang_nhuan_note"]
    # block năm không nhuận → note rỗng (không cảnh báo bừa)
    assert vh.luu_nguyet_block(r, 2026, 6)["thang_nhuan_note"] == ""


def test_long_tang_bao_tram_dai_van():
    """Luận năm/tháng LỒNG trong Đại Vận bao trùm (cổ pháp lấy đại hạn làm chủ) + sao
    hội chiếu có nội dung nguồn. Nâng chất luận nguyệt/niên vận."""
    p = {"birth_datetime_local": "1988-06-05T23:30:00", "gender": "nam"}
    for tang, kw in [("luu_nien", {"year": 2030}), ("luu_nguyet", {"year": 2030, "month": 5})]:
        r = vh.van_han_luan(p, tang, want_llm=False, **kw)
        bt = r["block"].get("bao_tram_dai_van")
        assert bt and bt["cung"] and bt["khoang_tuoi"]         # có đại vận bao trùm
        assert bt["khoang_tuoi"][0] <= 43 <= bt["khoang_tuoi"][1]   # 2030 ~ tuổi 43
        assert "BỐI CẢNH — Đại Vận bao trùm" in r["source_text"]
        # ≥1 cung hội chiếu có nội dung nguồn (đọc cả chòm)
        assert any(h["sao_nguon"] for h in r["block"]["hoi_chieu"])


def test_month_out_of_range():
    r = _founder()
    import pytest
    with pytest.raises(ValueError):
        vh.luu_nguyet_block(r, 2026, 13)
    with pytest.raises(ValueError):
        vh.tuan_block(r, 2026, 9, 4)
