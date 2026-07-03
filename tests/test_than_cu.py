"""Thân cư — engine.tu_vi.than_cu. Đọc Thân đóng cung nào → nghĩa GROUNDED có nguồn.

Kỷ luật quote-or-silence (Iron #9): CHỈ trả atom đã duyệt + nguồn; vị trí không có
nguồn → chua_co_nguon (KHÔNG bịa). Vị trí phải ĐÚNG (than_index) + nghĩa KHÔNG lẫn chéo.
"""
from engine.tu_vi.than_cu import (
    doc_than_cu, doc_cuc, list_cuc, _retrieve, _PALACE_KEY, _CUC_ELEMENT,
)
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


def test_cuc_la_ngu_hanh_nen_grounded():
    """#2: Cục = ngũ hành nền. Founder Thổ Ngũ → hành Thổ + nature grounded (không rỗng)."""
    r = cast_la_so_from_birth(birth_datetime_local="1988-06-05T23:30:00", gender="nam")
    c = doc_cuc(r)
    assert c["available"] and c["element"] == "Thổ"
    assert c["nature"] and "ổn định" in c["nature"]
    assert "cổ thư" in c["source"] or "Ngũ hành" in c["source"]


def test_5_cuc_deu_co_nature():
    """Cả 5 cục (2..6) đều ra ngũ hành nền + nature không rỗng."""
    for cuc in _CUC_ELEMENT:
        c = doc_cuc({"cuc": cuc, "cuc_name": "X"})
        assert c["available"] and c["element"] and c["nature"]


def test_list_cuc_thu_vien_du_5_grounded():
    """B2 Thư viện: list_cuc() trả đủ 5 cục (2..6), mỗi cục có tên + hành + nature.

    Tầng 'chất người' để TRỐNG + chua_co_nguon=True (quote-or-silence, không bịa).
    """
    d = list_cuc()
    items = d["items"]
    assert len(items) == 5
    assert [i["cuc"] for i in items] == [2, 3, 4, 5, 6]
    names = [i["cuc_name"] for i in items]
    assert names == ["Thủy Nhị Cục", "Mộc Tam Cục", "Kim Tứ Cục",
                     "Thổ Ngũ Cục", "Hỏa Lục Cục"]
    for i in items:
        assert i["element"] and i["nature"] and i["element_key"]
        assert i["chat_nguoi"] == "" and i["chua_co_nguon"] is True  # không bịa
    assert d["vai_tro"] and "KHÔNG đoán" in d["vai_tro"]             # không predict
    assert "cổ thư" in d["source"] or "Ngũ hành" in d["source"]


def test_menh_than_axis_grounded():
    """#3: trục Mệnh→Thân có nguồn — 'Mệnh nửa đời trước, Thân nửa đời sau'."""
    r = cast_la_so_from_birth(birth_datetime_local="1988-06-05T23:30:00", gender="nam")
    ax = doc_than_cu(r)["menh_than_axis"]
    assert ax and ax["text"] and ax["source"]
    assert "nửa đời" in ax["text"]
    assert "Tuy nhiên" not in ax["text"]         # caveat đã cắt gọn


def test_loc_chat_luong_khong_lot_mau_sai_hay_asr_tho():
    """6 vị trí: KHÔNG lọt atom META (Mẫu SAI — dạy tránh nói) hay bản ASR thô ('số N…')."""
    for p in _PALACE_KEY:
        for y in _retrieve(p, 3):
            t = y["text"].strip().lower()
            assert not t.startswith("mẫu sai"), f"{p}: lọt Mẫu SAI"
            assert "mẫu sai" not in t[:40], f"{p}: lọt Mẫu SAI"
            assert not t.startswith("số "), f"{p}: lọt ASR thô"
