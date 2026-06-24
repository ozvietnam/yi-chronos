"""Test lớp trình bày dùng chung build_display (web + AppChat).

Kiểm: ra {meta, sections}; cap_do (KILLER) lên đầu; section rỗng bị BỎ;
gender nam → title 'vợ' + phoi_ngau 'vợ'; nữ → 'chồng'; ẨN internal
(base_12_khia_canh, scrub_caution_count) khỏi display.
"""
from __future__ import annotations

import json

from engine.tinh_duyen.display import build_display
from engine.tinh_duyen.reading import read_tinh_duyen

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
