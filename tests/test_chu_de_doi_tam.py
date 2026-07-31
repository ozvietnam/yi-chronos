"""ĐỌC THEO CHỦ ĐỀ — dời tâm (Anh 2026-07-31).

Điểm cốt: cung chủ đề làm TÂM thì phải đọc CHÒM THẬT của nó (tam phương tứ chính tính từ
chính cung đó), không phải danh sách cung chọn tay. Bug cũ: sự nghiệp lấy Thiên Di — vốn là
đối cung của MỆNH, không thuộc chòm Quan Lộc.
"""
from __future__ import annotations

from engine.tu_vi.chu_de import CHU_DE, doc_doi_tam, doi_tam_source_text
from engine.tu_vi.from_birth import cast_la_so_from_birth


def _founder():
    return cast_la_so_from_birth(birth_datetime_local="1988-06-05T23:30:00", gender="nam")


def _idx(la_so, ten):
    return next(p["branch_index"] for p in la_so["palaces"] if p["name"] == ten)


def test_chom_dung_hinh_hoc_tu_cung_tam():
    """Chòm phải tính TỪ CUNG TÂM: đối cung = +6, tam hợp = ±4 so với cung tâm."""
    ls = _founder()
    b = doc_doi_tam(ls, "su_nghiep")
    assert b["available"] and b["cung_tam"] == "Quan Lộc"
    tam_i = _idx(ls, "Quan Lộc")
    for h in b["tam"]["hoi_chieu"]:
        hi = _idx(ls, h["cung"])
        d = (hi - tam_i) % 12
        assert d in (4, 6, 8), f"{h['cung']} lệch {d} — không thuộc chòm cung tâm"
    # đối cung của Quan Lộc là Phu Thê (KHÔNG phải Thiên Di = đối cung của Mệnh)
    doi = [h["cung"] for h in b["tam"]["hoi_chieu"] if "đối cung" in h["quan_he"]]
    assert doi == ["Phu Thê"]


def test_moi_chu_de_co_tam_va_chom():
    ls = _founder()
    for slug in CHU_DE:
        b = doc_doi_tam(ls, slug)
        assert b["available"], slug
        assert b["tam"]["co_du_lieu"], slug
        assert len(b["tam"]["hoi_chieu"]) == 3, slug      # 1 đối cung + 2 tam hợp
        assert b["cung_tam"] not in {h["cung"] for h in b["tam"]["hoi_chieu"]}


def test_phu_tro_khong_lap_cung_trong_chom():
    ls = _founder()
    b = doc_doi_tam(ls, "su_nghiep")
    trong_chom = {h["cung"] for h in b["tam"]["hoi_chieu"]} | {b["cung_tam"]}
    assert not (trong_chom & {p["cung"] for p in b["phu_tro"]})


def test_vo_chinh_dieu_muon_sao_cung_xung():
    """Cung tâm Vô Chính Diệu → mượn sao cung xung (cổ pháp), có cờ báo."""
    ls = _founder()
    b = doc_doi_tam(ls, "su_nghiep")           # Quan Lộc (Dậu) của founder là VCĐ
    t = b["tam"]
    assert t["sao"], "phải mượn được sao"
    assert t["sao_muon_xung"] is True


def test_source_text_grounded_va_paradigm():
    """Có kho → phải DẪN NGUỒN; không có kho (worktree) → phải nói rõ CHƯA CÓ NGUỒN,
    tuyệt đối không tự chế nội dung (quote-or-silence)."""
    from engine.tu_vi import van_han as vh

    ls = _founder()
    blk = doc_doi_tam(ls, "su_nghiep")
    src = doi_tam_source_text(blk)
    assert "LẤY CUNG Quan Lộc LÀM TÂM" in src
    assert "tam phương tứ chính" in src
    assert "KHÔNG tiên tri" in src              # paradigm guard (Iron #4/#6/#8)
    if vh._db() is not None and blk["tam"]["sao_nguon"]:
        assert "nguồn:" in src                  # kho sẵn → trích sách
    else:
        assert "CHƯA CÓ NGUỒN" in src           # thiếu kho → im lặng, không bịa


def test_suc_khoe_co_luu_y_khong_chan_doan():
    """Iron #9 — sức khoẻ chỉ quan-sát, không chẩn đoán y tế."""
    b = doc_doi_tam(_founder(), "suc_khoe")
    assert b["luu_y"] and "KHÔNG phải chẩn đoán" in b["luu_y"]
    assert b["cung_tam"] == "Tật Ách"


def test_chu_de_la_khong_ho_tro():
    b = doc_doi_tam(_founder(), "xo_so")
    assert b["available"] is False and b["reason"] == "chu_de_khong_ho_tro"
