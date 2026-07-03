"""Thân cư — engine.tu_vi.than_cu. Đọc Thân đóng cung nào → nghĩa GROUNDED có nguồn.

Kỷ luật quote-or-silence (Iron #9): CHỈ trả atom đã duyệt + nguồn; vị trí không có
nguồn → chua_co_nguon (KHÔNG bịa). Vị trí phải ĐÚNG (than_index) + nghĩa KHÔNG lẫn chéo.
"""
from engine.tu_vi.than_cu import doc_than_cu, _retrieve, _PALACE_KEY
from engine.tu_vi.from_birth import cast_la_so_from_birth


def test_founder_than_cu_menh_grounded():
    """Founder: Thân đồng cung Mệnh (Tỵ) → có nghĩa đã duyệt + nguồn."""
    r = cast_la_so_from_birth(birth_datetime_local="1988-06-05T23:30:00", gender="nam")
    tc = doc_than_cu(r)
    assert tc["available"] is True
    assert tc["than_cung"] == "Mệnh" and tc["than_branch"] == "Tỵ"
    assert tc["menh_than_dong_cung"] is True
    assert tc["chua_co_nguon"] is False
    assert tc["y_nghia"], "phải có ít nhất 1 nghĩa grounded"
    for y in tc["y_nghia"]:
        assert y["text"] and y["source"]           # mỗi nghĩa PHẢI kèm nguồn


def test_than_cu_dung_vi_tri_theo_than_index():
    """Thân đóng cung nào là theo than_index — không cứng ở Mệnh."""
    r = cast_la_so_from_birth(birth_datetime_local="1988-06-05T23:30:00", gender="nam")
    r2 = dict(r)
    # ép Thân sang cung Quan Lộc (tìm branch_index của Quan Lộc)
    quan = next(p for p in r["palaces"] if p["name"] == "Quan Lộc")
    r2["than_index"] = quan["branch_index"]
    tc = doc_than_cu(r2)
    assert tc["than_cung"] == "Quan Lộc"
    assert tc["menh_than_dong_cung"] is False


def test_sau_vi_tri_deu_co_nghia_va_khong_lan_cheo():
    """6 vị trí Thân cư đều kéo được nghĩa, và nghĩa KHÁC nhau (không nhiễm chéo)."""
    texts = {}
    for p in _PALACE_KEY:
        ys = _retrieve(p, 1)
        assert ys, f"Thân cư {p} phải có nghĩa grounded"
        texts[p] = ys[0]["text"]
    # Mệnh vs Quan Lộc vs Thiên Di phải khác nhau (chống bug khớp source_quote nhiễu chéo)
    assert texts["Mệnh"] != texts["Quan Lộc"]
    assert texts["Quan Lộc"] != texts["Thiên Di"]
    assert len(set(texts.values())) >= 5          # gần như toàn bộ phân biệt


def test_quote_or_silence_vi_tri_khong_phai_than_cu():
    """Cung KHÔNG thuộc 6 vị trí Thân cư (vd Điền Trạch) → không có key → [] (không bịa)."""
    assert _retrieve("Điền Trạch", 2) == []
    assert _retrieve("Tật Ách", 2) == []


def test_loc_chat_luong_khong_lot_mau_sai_hay_asr_tho():
    """6 vị trí: KHÔNG lọt atom META (Mẫu SAI — dạy tránh nói) hay bản ASR thô ('số N…')."""
    for p in _PALACE_KEY:
        for y in _retrieve(p, 3):
            t = y["text"].strip().lower()
            assert not t.startswith("mẫu sai"), f"{p}: lọt Mẫu SAI"
            assert "mẫu sai" not in t[:40], f"{p}: lọt Mẫu SAI"
            assert not t.startswith("số "), f"{p}: lọt ASR thô"
