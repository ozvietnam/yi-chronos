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

# JARGON cần ĐẨY KHỎI tom_tat (xuống can_cu): tom_tat = THUẦN nghĩa, người Việt
# KHÔNG biết tử vi đọc vẫn hiểu. can_cu được PHÉP chứa (dành người tò mò trace).
# (a) tên sao · (b) thập thần · (c) lý-thuật / can-chi.
_JARGON = [
    # (a) tên sao
    "Tử Vi", "Thiên Phủ", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng",
    "Liêm Trinh", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng", "Thiên Lương",
    "Thất Sát", "Phá Quân", "Đào Hoa", "Hồng Loan", "Thiên Hỉ", "Thiên Hỷ",
    "Thiên Diêu", "Cô Thần", "Quả Tú", "Kình Dương", "Đà La", "Hỏa Tinh",
    "Linh Tinh", "Địa Không", "Địa Kiếp", "Không Kiếp", "Thiên Mã", "Văn Xương",
    "Văn Khúc", "Tả Phù", "Hữu Bật",
    # (b) thập thần
    "Chính Quan", "Thiên Quan", "Thương Quan", "Thực Thần", "Chính Tài",
    "Thiên Tài", "Chính Ấn", "Thiên Ấn", "Tỷ Kiên", "Kiếp Tài", "Tỷ Kiếp",
    "Quan Sát", "官杀", "财",
    # (c) lý-thuật / can-chi
    "đại vận", "lưu niên", "tiểu hạn", "hãm", "miếu", "vượng địa", "đắc địa",
    "ấn tinh", "cung Phu Thê", "cung Mệnh", "nhật chủ", "hóa Lộc", "hóa Quyền",
    "hóa Khoa", "hóa Kỵ", "Tuần", "Triệt",
]


def _han_in(obj) -> list[str]:
    """List ký tự Hán tìm thấy trong obj (đệ quy qua str/list/dict)."""
    blob = json.dumps(obj, ensure_ascii=False) if obj is not None else ""
    return _HAN_RE.findall(blob)


def _jargon_in(obj) -> list[str]:
    """List token JARGON (tên sao / thập thần / lý-thuật) tìm thấy trong obj.

    tom_tat phải SẠCH list này (THUẦN nghĩa đời thường). can_cu được phép chứa."""
    blob = json.dumps(obj, ensure_ascii=False) if obj is not None else ""
    return [j for j in _JARGON if j in blob]

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


def test_cach_cuc_tom_tat_thuan_can_cu_giu_ten_cach():
    # tom_tat = _plain_vi(bien_chinh) (bỏ tên cách-Hán + Tỵ/Hợi hãm + tên sao).
    # can_cu = {ten_cach, han_tu, _nguon} (giữ cho người tò mò).
    d = build_display(_read("nữ"), "nữ")
    sec = [s for s in d["sections"] if s["id"] == "cach_cuc"][0]
    assert sec["tom_tat"], "cach_cuc phải có tom_tat thuần"
    assert not _han_in(sec["tom_tat"])
    assert not _jargon_in(sec["tom_tat"]), "tom_tat cach_cuc phải sạch jargon"
    t0 = sec["tom_tat"][0]
    assert "noi_dung" in t0 and "tone" in t0
    assert "ten" not in t0  # tên cách kỹ thuật KHÔNG ở tom_tat
    # can_cu: tên cách gốc (có thể chứa 'hãm', tên sao) + han_tu + _nguon.
    assert sec["can_cu"]
    c0 = sec["can_cu"][0]
    for k in ("ten_cach", "han_tu", "_nguon"):
        assert k in c0, f"can_cu cach_cuc thiếu {k}"


def test_plain_vi_thuan_nghia():
    from engine.tinh_duyen.display import _plain_vi
    # đại vận → giai đoạn; lưu niên → năm.
    out = _plain_vi("vận này theo đại vận và lưu niên")
    assert "đại vận" not in out and "lưu niên" not in out
    assert "giai đoạn" in out and "năm" in out
    # bỏ tên sao + chữ Hán; mệnh đề rỗng dọn sạch.
    out2 = _plain_vi("Liêm Trinh (廉貞) ở Tỵ hãm")
    assert not _HAN_RE.search(out2)
    assert "Liêm Trinh" not in out2 and "Tỵ" not in out2 and "hãm" not in out2
    # 'năm Hồng Loan tới' → nghĩa đời thường.
    out3 = _plain_vi("năm Hồng Loan tới")
    assert "Hồng Loan" not in out3
    assert "vui" in out3 or "duyên" in out3
    # Non-str giữ nguyên; đệ quy list/dict.
    assert _plain_vi(5) == 5 and _plain_vi(None) is None
    rec = _plain_vi({"a": "đại vận", "b": ["lưu niên"]})
    assert "đại vận" not in rec["a"] and "lưu niên" not in rec["b"][0]


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


# ── 7) tom_tat của MỌI section: 0 Hán + 0 JARGON (THUẦN nghĩa đời thường) ─────
def test_tom_tat_moi_section_thuan_nghia():
    """tom_tat = THUẦN nghĩa: KHÔNG Hán, KHÔNG tên sao / thập thần / lý-thuật.
    Người Việt không biết tử vi đọc vẫn hiểu. Jargon đẩy xuống can_cu."""
    d = build_display(_read("nữ"), "nữ")
    assert d["meta"]["co_can_cu"] is True
    for s in d["sections"]:
        han = _han_in(s.get("tom_tat"))
        assert not han, f"section {s['id']}: tom_tat còn Hán {han[:5]}"
        jargon = _jargon_in(s.get("tom_tat"))
        assert not jargon, f"section {s['id']}: tom_tat còn JARGON {jargon}"
        # Mỗi section PHẢI có 3 field mới (giữ field cũ song song).
        assert "tom_tat" in s
        assert "can_cu" in s
        assert "mac_dinh_an" in s


def test_tom_tat_thuan_nghia_nam_menh():
    # Gender nam cũng phải THUẦN: 0 Hán + 0 jargon.
    d = build_display(_read("nam"), "nam")
    for s in d["sections"]:
        assert not _han_in(s.get("tom_tat")), f"{s['id']} nam menh còn Hán"
        jargon = _jargon_in(s.get("tom_tat"))
        assert not jargon, f"{s['id']} nam menh tom_tat còn JARGON {jargon}"


# ── 7b) REGRESSION quét ĐA-LÁ: tom_tat 0 jargon + 0 toán-tử/ngoặc mồ côi ──────
# Lý do: glossary is_jargon CŨ bỏ sót một số thuật ngữ người-thường KHÔNG hiểu
# ('Phu Thê' trần, 'chính tinh', 'lưu Kình', 'cương khắc', 'gặp sát',
# 'thuộc hạ cách'), test cũ chỉ quét theo is_jargon → false pass. Đồng thời các
# nhóm dao_hoa/sat_tinh/tu_hoa TRƯỚC ĐÂY thiếu nghia_thuan → fallback _plain_vi
# để lại toán tử treo ('+ →') / ngoặc rỗng nơi tên sao bị xoá. Test này quét
# ĐỆ QUY mọi tom_tat trên NHIỀU lá × 2 giới để bắt residue đó.
_LAYPERSON_LEAK = [
    # thuật ngữ tử vi người Việt thường KHÔNG hiểu (ngoài is_jargon cũ).
    "Phu Thê", "chính tinh", "chính diệu", "lưu Kình", "lưu Đà",
    "cương khắc", "cương liệt", "sát cương", "sát hỏa", "sát âm",
    "gặp sát", "hội sát", "thuộc hạ cách", "hạ cách", "thượng cách",
    "đồng cung", "đồng độ", "đồng triền", "hội chiếu", "tam phương",
]
# Lá đa dạng: có/không chính tinh, sát tinh, đào hoa, tứ hóa nhập Phu.
_BIRTHS_SCAN = [
    "1990-08-20T14:00", "1988-06-05T23:30", "1995-03-10T08:00",
    "1992-11-25T17:00", "1985-01-01T06:00", "2000-07-07T12:00",
    "1978-12-31T20:00", "1993-04-18T03:00",
]


def _walk_strings(obj):
    """Yield mọi chuỗi (đệ quy) trong obj."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _walk_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _walk_strings(v)


def test_tom_tat_da_la_khong_jargon_nguoi_thuong():
    """Quét ĐA-LÁ × 2 giới: tom_tat mọi section 0 chữ Hán, 0 jargon is_jargon,
    0 thuật-ngữ-người-thường-không-hiểu, KHÔNG toán tử/ngoặc mồ côi do xoá sao."""
    # Toán tử MỒ CÔI = '+'/'→' mất toán-hạng do xoá tên sao: hai toán tử liền nhau
    # ('+ →'), toán tử ngay trước dấu đóng ngoặc/nháy ('+)'/"+'"), hay cuối chuỗi.
    # KHÔNG bắt '+'/'→' hợp lệ giữa hai cụm từ thật ("rèn + chọn", "'có nên' → Mai Hoa").
    op_re = re.compile(
        r"[+→]\s*[+→]"                 # hai toán tử liền nhau
        r"|[+→]\s*[\)\）\]】」'\"]"     # toán tử ngay trước dấu đóng
        r"|[\(\（\[【「]\s*[+→]"        # toán tử ngay sau dấu mở
        r"|[+→]\s*$"                    # toán tử cuối chuỗi
    )
    lead_paren_re = re.compile(r"^\s*[\(\（]")                          # ngoặc dẫn mồ côi
    for birth in _BIRTHS_SCAN:
        for g in ("nữ", "nam"):
            d = build_display(
                read_tinh_duyen(birth_datetime_local=birth, gender=g), g)
            for s in d["sections"]:
                tt = s.get("tom_tat")
                tag = f"{birth}/{g}/{s['id']}"
                # (a) 0 Hán + 0 jargon is_jargon (giữ kiểm cũ).
                assert not _han_in(tt), f"{tag}: tom_tat còn Hán"
                assert not _jargon_in(tt), f"{tag}: tom_tat còn JARGON is_jargon"
                # (b) 0 thuật-ngữ người-thường-không-hiểu.
                blob = json.dumps(tt, ensure_ascii=False) if tt else ""
                leak = [t for t in _LAYPERSON_LEAK if t in blob]
                assert not leak, f"{tag}: tom_tat rò thuật ngữ người-thường: {leak}"
                # (c) Không toán-tử treo + không ngoặc dẫn mồ côi (nơi tên sao bị
                #     xoá để lại '+ →' / '(gloss)' lủng lẳng).
                for txt in _walk_strings(tt):
                    assert not op_re.search(txt), \
                        f"{tag}: toán tử treo trong tom_tat: {txt!r}"
                    assert not lead_paren_re.match(txt), \
                        f"{tag}: ngoặc dẫn mồ côi trong tom_tat: {txt!r}"


# ── 8) can_cu chứa phần KỸ THUẬT (Hán) khi section có ─────────────────────────
def test_cung_phu_the_tach_tom_tat_va_can_cu():
    d = build_display(_read("nữ"), "nữ")
    cpt = [s for s in d["sections"] if s["id"] == "cung_phu_the"]
    assert cpt, "lá có cung Phu Thê"
    sec = cpt[0]
    # tom_tat: câu nghĩa THUẦN (nghia_thuan) — 0 Hán, 0 jargon, KHÔNG tên sao.
    assert not _han_in(sec["tom_tat"])
    assert not _jargon_in(sec["tom_tat"]), "tom_tat cung_phu_the phải sạch jargon"
    assert sec["tom_tat"] and sec["tom_tat"][0]["noi_dung"]
    # tom_tat KHÔNG còn field 'ten' (tên sao đã đẩy xuống can_cu).
    assert "ten" not in sec["tom_tat"][0]
    # can_cu: 'TênSao (Hán)' + noi_dung gốc kỹ thuật + cat_hung + dieu_can_chu_y.
    assert sec["can_cu"]
    c0 = sec["can_cu"][0]
    for k in ("ten", "noi_dung", "cat_hung", "dieu_can_chu_y"):
        assert k in c0, f"can_cu cung_phu_the thiếu {k}"
    blob = json.dumps(sec["can_cu"], ensure_ascii=False)
    assert _HAN_RE.search(blob), "can_cu cung_phu_the phải còn tên sao Hán kỹ thuật"
    assert sec["mac_dinh_an"] is False


def test_song_phai_tach_tom_tat_va_can_cu():
    d = build_display(_read("nữ"), "nữ")
    sp = [s for s in d["sections"] if s["id"] == "song_phai"]
    assert sp, "lá có song phái reconcile"
    sec = sp[0]
    assert not _han_in(sec["tom_tat"])
    assert not _jargon_in(sec["tom_tat"]), "tom_tat song_phai phải sạch jargon"
    # tom_tat = {chu_de, trang_thai, ket_luan _plain_vi}: kết luận thuần đời thường.
    t0 = sec["tom_tat"][0]
    assert "chu_de" in t0 and "ket_luan" in t0
    assert t0["trang_thai"] in ("hội tụ", "dị biệt")
    assert "hai phái" in t0["ket_luan"]
    # can_cu: cơ chế tu_vi/bat_tu GIỮ NGUYÊN (chứa Hán).
    assert sec["can_cu"] and "tu_vi" in sec["can_cu"][0]
    assert _HAN_RE.search(json.dumps(sec["can_cu"], ensure_ascii=False))


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


# ── 10b) lo_trinh user-facing THUẦN — không con trỏ internal, không jargon ────
def test_tom_tat_lo_trinh_thuan_nghia():
    """cap_do.lo_trinh trong tom_tat phải THUẦN nghĩa (Iron Rule tầng NGHĨA THUẦN):
    KHÔNG chú dẫn nội bộ 'xem key.dotted', KHÔNG thập-thần jargon (Thương Quan,
    Thực Thần, Cự Môn...), KHÔNG chữ Hán. Nội dung thật vẫn còn (không xoá quá tay).
    Lưu ý: lo_trinh nay tự-chứa nội dung plain → không còn con trỏ 'xem X' trong
    data (đã thay bằng hành vi đời thường); _strip_internal_ref vẫn được phủ bởi
    test_strip_internal_ref_truc_tiep bên dưới."""
    d = build_display(_read("nữ"), "nữ")
    cap = [s for s in d["sections"] if s["id"] == "cap_do"][0]
    tom_blob = json.dumps(cap["tom_tat"], ensure_ascii=False)
    leak = re.findall(r"xem\s+[a-z_]+(?:\.[a-z0-9_]+)+", tom_blob)
    assert not leak, f"tom_tat rò con trỏ internal: {leak}"
    # KHÔNG jargon thập-thần / sao trong lo_trinh user-facing.
    jargon = ["Thương Quan", "Thực Thần", "Quan Sát", "Chính Quan",
              "Cô Thần", "Quả Tú", "Cự Môn", "hóa Kỵ", "王亭之"]
    lo_blob = json.dumps(cap["tom_tat"]["lo_trinh"], ensure_ascii=False)
    found = [j for j in jargon if j in lo_blob]
    assert not found, f"lo_trinh tom_tat còn jargon: {found}"
    assert not re.search(r"[一-鿿]", lo_blob), "lo_trinh tom_tat còn chữ Hán"
    # lo_trinh tom_tat vẫn còn nội dung thật (không bị xoá quá tay).
    assert cap["tom_tat"]["lo_trinh"]
    assert "Hạ cái tôi" in cap["tom_tat"]["lo_trinh"][0]


def test_strip_internal_ref_truc_tiep():
    from engine.tinh_duyen.display import _strip_internal_ref
    # Sau ' — ' (cuối câu).
    assert _strip_internal_ref(
        "chuyển sang Thực Thần — xem lo_trinh_ren.thuong_quan_sang_thuc_than."
    ) == "chuyển sang Thực Thần."
    # Trong ngoặc, có dấu phẩy trước.
    assert _strip_internal_ref(
        "Cự Môn (khéo lời, xem lo_trinh_ren.cu_mon_sang_kheo_loi)."
    ) == "Cự Môn (khéo lời)."
    # Không có con trỏ → trả NGUYÊN (identity, không đụng).
    plain = "câu thuần Việt không có ref"
    assert _strip_internal_ref(plain) is plain
    # Non-str / đệ quy.
    assert _strip_internal_ref(5) == 5
    assert _strip_internal_ref(None) is None
    assert _strip_internal_ref(["a xem x.y", {"k": "b xem m.n.o"}]) == ["a", {"k": "b"}]


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
