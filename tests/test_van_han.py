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


def test_cung_van_nghia_grounded_hoac_none():
    """#3: nguyên tắc đọc-cung-theo-vận CÓ NGUỒN cho cung đã trích; cung chưa trích → None
    (quote-or-silence, không bịa)."""
    r = _founder()
    from engine.tu_vi.van_han import _CUNG_VAN_NGHIA, _the_dung_block
    from engine.tu_vi.an_sao import BRANCHES_TVI as B
    # mọi rule đã curate PHẢI có nguồn
    for cung, v in _CUNG_VAN_NGHIA.items():
        assert v["rule"] and v["nguon"]
    # block: cung có trong dict → cung_van_nghia có nguồn; ngoài dict → None
    seen_some = False
    for bi in range(12):
        blk = _the_dung_block(r, bi, "Test")
        cvn = blk.get("cung_van_nghia")
        if blk["cung_the"] in _CUNG_VAN_NGHIA:
            assert cvn and cvn["nguon"]
            seen_some = True
        else:
            assert cvn is None       # KHÔNG bịa cung chưa trích
    assert seen_some


def test_month_out_of_range():
    r = _founder()
    import pytest
    with pytest.raises(ValueError):
        vh.luu_nguyet_block(r, 2026, 13)
    with pytest.raises(ValueError):
        vh.tuan_block(r, 2026, 9, 4)
