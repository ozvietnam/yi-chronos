"""Test lớp trình bày dùng chung build_display (web + AppChat).

Kiểm: ra {meta, sections}; cap_do (KILLER) lên đầu; section rỗng bị BỎ;
gender nam → title 'vợ' + phoi_ngau 'vợ'; nữ → 'chồng'; ẨN internal
(base_12_khia_canh, scrub_caution_count) khỏi display.
"""
from __future__ import annotations

import json
import re

from engine.tinh_duyen.display import _strip_han, build_display
from engine.tinh_duyen.reading import read_tinh_duyen

# Dải Hán [一-鿿] — tom_tat KHÔNG được chứa ký tự nào trong dải này.
_HAN_RE = re.compile(r"[一-鿿]")


def _han_in(obj) -> list[str]:
    """List ký tự Hán tìm thấy trong obj (đệ quy qua str/list/dict)."""
    blob = json.dumps(obj, ensure_ascii=False) if obj is not None else ""
    return _HAN_RE.findall(blob)

# Lá có Mệnh chính tinh (Liêm Trinh) + cách cục + cau_hoi_tuoi → sections đầy đủ.
_BIRTH = "1990-08-20T14:00"


def _read(gender: str) -> dict:
    return read_tinh_duyen(birth_datetime_local=_BIRTH, gender=gender)


def _ids(display: dict) -> list[str]:
    return [s["id"] for s in display["sections"]]


# ── 1) ra meta + sections ────────────────────────────────────────────────────
def test_build_display_co_meta_va_sections():
    d = build_display(_read("nữ"), "nữ")
    assert "meta" in d and "sections" in d
    assert isinstance(d["sections"], list) and d["sections"]
    m = d["meta"]
    for k in ("title", "gender", "phoi_ngau", "tuoi", "stage_id",
              "disclaimer", "method_id", "paradigm_ok"):
        assert k in m, f"meta thiếu key {k}"
    # mỗi section có id + kind.
    for s in d["sections"]:
        assert s.get("id") and s.get("kind")


# ── 2) cap_do KILLER lên đầu ─────────────────────────────────────────────────
def test_cap_do_len_dau():
    d = build_display(_read("nữ"), "nữ")
    first = d["sections"][0]
    assert first["id"] == "cap_do" and first["kind"] == "cap_do"
    data = first["data"]
    assert data["max"] == 5
    assert 1 <= data["cap_do"] <= 5


# ── 3) section rỗng bị BỎ ─────────────────────────────────────────────────────
def test_section_rong_bi_bo():
    # reading tối thiểu: KHÔNG có cap_do/cau_hoi/cung_phu_the/song_phai/dinh_thoi/
    # cach_cuc/quy_trinh/sources → chỉ còn các section CTA luôn-hiện.
    minimal = {
        "method_id": "tinh_duyen_nu_menh_v1",
        "input": {"gender": "nữ", "tuoi": 30},
        "stage": {"stage_id": "x", "tuoi": 30},
        "chan_doan_cap_do": {},
        "cau_hoi_tuoi": [],
        "cung_phu_the_tuvi": {},
        "song_phai_reconcile": [],
        "dinh_thoi": {},
        "cach_cuc": [],
        "quy_trinh_day_du": {},
        "sources": [],
        "paradigm_ok": True,
        "_disclaimer": "đọc đồng dạng",
    }
    d = build_display(minimal, "nữ")
    ids = _ids(d)
    # Các section data-driven RỖNG phải biến mất.
    for gone in ("cap_do", "hoi_dap", "cung_phu_the", "song_phai",
                 "dinh_thoi", "cach_cuc", "luan_chi_tiet", "nguon"):
        assert gone not in ids, f"section rỗng '{gone}' phải bị bỏ"
    # CTA (không cần data) vẫn còn.
    for keep in ("loi_thay", "phac_hoa", "gieo_que"):
        assert keep in ids


def test_cach_cuc_xuat_hien_khi_co_data():
    # Lá thật CÓ cách cục 'Liêm Trinh hãm địa' → section cach_cuc hiện.
    d = build_display(_read("nữ"), "nữ")
    cc = [s for s in d["sections"] if s["id"] == "cach_cuc"]
    assert cc, "lá có cách cục phải hiện section cach_cuc"
    assert cc[0]["kind"] == "list" and cc[0]["items"]
    assert "tone" in cc[0]["items"][0]


# ── 4) gender-aware: nam → 'vợ', nữ → 'chồng' ────────────────────────────────
def test_gender_nam_title_va_phoi_ngau_vo():
    d = build_display(_read("nam"), "nam")
    assert d["meta"]["phoi_ngau"] == "vợ"
    assert "vợ" in d["meta"]["title"]
    assert d["meta"]["gender"] == "nam"
    cpt = [s for s in d["sections"] if s["id"] == "cung_phu_the"]
    if cpt:
        assert "vợ" in cpt[0]["title"]
    phac = [s for s in d["sections"] if s["id"] == "phac_hoa"][0]
    assert "vợ" in phac["title"]


def test_gender_nu_title_va_phoi_ngau_chong():
    d = build_display(_read("nữ"), "nữ")
    assert d["meta"]["phoi_ngau"] == "chồng"
    assert "chồng" in d["meta"]["title"]
    assert d["meta"]["gender"] == "nữ"
    cpt = [s for s in d["sections"] if s["id"] == "cung_phu_the"]
    if cpt:
        assert "chồng" in cpt[0]["title"]


def test_gender_suy_tu_input_khi_param_rong():
    # gender rỗng → suy từ reading_output['input']['gender'].
    d = build_display(_read("nam"), "")
    assert d["meta"]["phoi_ngau"] == "vợ"


# ── 5) ẨN internal: base_12 / scrub không còn trong display ───────────────────
def test_an_internal_khong_con_base12_scrub():
    d = build_display(_read("nữ"), "nữ")
    blob = json.dumps(d, ensure_ascii=False)
    assert "base_12_khia_canh" not in blob
    assert "scrub_caution_count" not in blob
    # sections không chứa base_12 / scrub key.
    assert "base_12_khia_canh" not in d
    assert "scrub_caution_count" not in d


def test_sections_la_json_thuan_render_duoc():
    # AppChat: sections phải serialise JSON được (không HTML, không object lạ).
    import re
    d = build_display(_read("nữ"), "nữ")
    s = json.dumps(d, ensure_ascii=False)
    # Quét CHẶT thẻ HTML thật (mở/đóng) — KHÔNG dùng OR yếu (dễ pass sai).
    html_tags = re.findall(r"</?[a-zA-Z][^>]*>", s)
    assert not html_tags, f"display KHÔNG được chứa thẻ HTML, thấy: {html_tags[:5]}"
    round_trip = json.loads(s)
    assert round_trip["meta"]["phoi_ngau"] == "chồng"
    # Mỗi section phải có kind hợp lệ + payload render được (data/items/content/action).
    valid_kinds = {"cap_do", "qa", "prose_list", "pairs", "timeline", "list",
                   "collapsible", "narration", "cta", "cta_gieo_que", "refs"}
    for sec in round_trip["sections"]:
        assert sec["kind"] in valid_kinds, f"kind lạ: {sec['kind']}"
        has_payload = any(k in sec for k in
                          ("data", "items", "content", "action", "fetch_action"))
        assert has_payload, f"section {sec['id']} thiếu payload render"


# ── 6) _strip_han: xoá Hán + dọn ngoặc rỗng ──────────────────────────────────
def test_strip_han_xoa_han_va_don_ngoac_rong():
    # Hán trong ngoặc → cả ngoặc rỗng bị dọn.
    assert _strip_han("khí chất ưu nhã (气质优雅)") == "khí chất ưu nhã"
    # Hán trần (không ngoặc) → biến mất, space gọn.
    out = _strip_han("năm Hồng Loan 红鸾 đến cung")
    assert "红" not in out and "鸾" not in out
    assert "  " not in out  # không còn double-space
    # Ngoặc vuông Hán → dọn sạch.
    assert "刑" not in _strip_han("sợ [刑忌夹印] đè")
    # Non-str giữ nguyên.
    assert _strip_han(5) == 5
    assert _strip_han(None) is None
    assert _strip_han(True) is True
    # List/dict đệ quy.
    assert _strip_han(["a 中", {"x": "b 文"}]) == ["a", {"x": "b"}]


# ── 7) tom_tat của MỌI section: 0 ký tự Hán ──────────────────────────────────
def test_tom_tat_moi_section_0_han():
    d = build_display(_read("nữ"), "nữ")
    assert d["meta"]["co_can_cu"] is True
    for s in d["sections"]:
        han = _han_in(s.get("tom_tat"))
        assert not han, f"section {s['id']}: tom_tat còn Hán {han[:5]}"
        # Mỗi section PHẢI có 3 field mới (giữ field cũ song song).
        assert "tom_tat" in s
        assert "can_cu" in s
        assert "mac_dinh_an" in s


def test_tom_tat_0_han_nam_menh():
    # Gender nam cũng phải sạch Hán.
    d = build_display(_read("nam"), "nam")
    for s in d["sections"]:
        assert not _han_in(s.get("tom_tat")), f"{s['id']} nam menh còn Hán"


# ── 8) can_cu chứa phần KỸ THUẬT (Hán) khi section có ─────────────────────────
def test_cung_phu_the_tach_tom_tat_va_can_cu():
    d = build_display(_read("nữ"), "nữ")
    cpt = [s for s in d["sections"] if s["id"] == "cung_phu_the"]
    assert cpt, "lá có cung Phu Thê"
    sec = cpt[0]
    # tom_tat: câu nghĩa plain, 0 Hán.
    assert not _han_in(sec["tom_tat"])
    assert sec["tom_tat"] and sec["tom_tat"][0]["noi_dung"]
    # can_cu: 'TênSao (Hán)' + chứa Hán kỹ thuật.
    assert sec["can_cu"]
    blob = json.dumps(sec["can_cu"], ensure_ascii=False)
    assert _HAN_RE.search(blob), "can_cu cung_phu_the phải còn tên sao Hán kỹ thuật"
    assert sec["mac_dinh_an"] is False


def test_song_phai_tach_tom_tat_va_can_cu():
    d = build_display(_read("nữ"), "nữ")
    sp = [s for s in d["sections"] if s["id"] == "song_phai"]
    assert sp, "lá có song phái reconcile"
    sec = sp[0]
    assert not _han_in(sec["tom_tat"])
    # tom_tat: 'hai phái hội tụ/dị biệt' + ket_luan plain.
    t0 = sec["tom_tat"][0]
    assert "hai phái" in t0["ket_luan"]
    assert t0["trang_thai"] in ("hội tụ", "dị biệt")
    # can_cu: cơ chế tu_vi/bat_tu (chứa Hán).
    assert sec["can_cu"] and "tu_vi" in sec["can_cu"][0]


# ── 9) luan_chi_tiet + nguon: mac_dinh_an=True (cả section là căn cứ) ─────────
def test_luan_chi_tiet_va_nguon_mac_dinh_an():
    d = build_display(_read("nữ"), "nữ")
    by_id = {s["id"]: s for s in d["sections"]}
    if "luan_chi_tiet" in by_id:
        assert by_id["luan_chi_tiet"]["mac_dinh_an"] is True
        assert by_id["luan_chi_tiet"]["tom_tat"] is None
        assert by_id["luan_chi_tiet"]["can_cu"] is not None
    if "nguon" in by_id:
        assert by_id["nguon"]["mac_dinh_an"] is True
        assert by_id["nguon"]["can_cu"]


# ── 10) gender giữ đúng sau khi tách (chồng/vợ) ──────────────────────────────
def test_gender_giu_dung_sau_khi_tach():
    dn = build_display(_read("nữ"), "nữ")
    assert "chồng" in dn["meta"]["title"]
    cpt = [s for s in dn["sections"] if s["id"] == "cung_phu_the"]
    if cpt:
        assert "chồng" in cpt[0]["title"]
    dm = build_display(_read("nam"), "nam")
    assert "vợ" in dm["meta"]["title"]


# ── 11) field cũ GIỮ NGUYÊN (không vỡ contract) ──────────────────────────────
def test_giu_field_cu_khong_vo_contract():
    d = build_display(_read("nữ"), "nữ")
    by_id = {s["id"]: s for s in d["sections"]}
    # cap_do vẫn có data; cung_phu_the/song_phai vẫn có items.
    assert "data" in by_id["cap_do"]
    if "cung_phu_the" in by_id:
        assert "items" in by_id["cung_phu_the"]
    if "song_phai" in by_id:
        assert "items" in by_id["song_phai"]
