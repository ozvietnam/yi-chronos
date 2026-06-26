"""cau_hoi_router — TRẢ LỜI các câu hỏi tình duyên TOP theo nhóm tuổi.

tra_loi_cau_hoi_tuoi(reading_output, age, gender='nữ') -> list[dict]

Mỗi nhóm tuổi (cau_hoi_tuoi.json) có bộ câu hỏi TOP. Hàm này:
  1. Chọn nhóm tuổi từ `age`.
  2. Với mỗi câu, ĐỊNH TUYẾN tới section CÓ SẴN trong reading_output (read_tinh_duyen)
     và RÚT GỌN câu trả lời TỪ section đó — KHÔNG bịa luận mới.
  3. Câu QUYẾT ĐỊNH nhị nguyên (can_gieo_que) → KHÔNG chốt từ lá số, trả lời gợi
     'gieo quẻ Mai Hoa' (paradigm Iron Rule #4).
  4. Câu cần lá số người kia (can_la_so_doi) → gợi 'dùng so-sánh-duyên'.

PARADIGM: KHÔNG bói, KHÔNG phán có/không (Iron #4/#6/#8). Câu 'có khắc chồng?'
trả QUA chan_doan_cap_do (cấp + lộ trình, constructive), KHÔNG verdict.

Engine DETERMINISTIC, KHÔNG gọi LLM. Mọi text rút ra ĐÃ đi qua _scrub trong
read_tinh_duyen; hàm này áp _scrub LẦN NỮA lên text tự ráp (defense-in-depth).
"""

from __future__ import annotations

from typing import Optional

from . import gender_lens as GL
from . import knowledge_loader as kb

# Trần ký tự cho câu trả lời rút gọn (giữ gọn cho UI).
_MAX_LEN = 320

# Ánh xạ nhóm tuổi (key trong cau_hoi_tuoi.json) -> (min, max).
# Lấy động từ JSON (key dạng "16-20"), nhưng giữ hàm parse an toàn.
def _parse_range(key: str) -> tuple[int, int]:
    lo, _, hi = key.partition("-")
    try:
        return int(lo), int(hi)
    except ValueError:
        return 0, 999


def _pick_nhom_tuoi(age: int) -> tuple[str, dict]:
    """Chọn nhóm tuổi khớp `age`. Ngoài biên -> clamp vào nhóm đầu/cuối."""
    nhom = kb.get("cau_hoi_tuoi")["nhom_tuoi"]
    # Sắp theo lo để clamp đúng.
    items = sorted(nhom.items(), key=lambda kv: _parse_range(kv[0])[0])
    for key, block in items:
        lo, hi = _parse_range(key)
        if lo <= age <= hi:
            return key, block
    # Ngoài biên.
    first_key, first_block = items[0]
    last_key, last_block = items[-1]
    if age < _parse_range(first_key)[0]:
        return first_key, first_block
    return last_key, last_block


def _shorten(text: str) -> str:
    """Rút gọn 1 đoạn về <= _MAX_LEN ký tự, cắt ở ranh giới câu/từ."""
    text = " ".join((text or "").split())
    if len(text) <= _MAX_LEN:
        return text
    cut = text[:_MAX_LEN]
    # Ưu tiên cắt ở dấu câu gần cuối, fallback ở khoảng trắng.
    for sep in (". ", "; ", ", ", " "):
        idx = cut.rfind(sep)
        if idx >= _MAX_LEN * 0.6:
            return cut[: idx + (0 if sep == " " else 1)].rstrip() + "…"
    return cut.rstrip() + "…"


# --------------------------------------------------------------------------- #
# Trích câu trả lời TỪ section reading_output (KHÔNG bịa)
# --------------------------------------------------------------------------- #
def _ans_chan_doan_cap_do(out: dict) -> str:
    cc = out.get("chan_doan_cap_do") or {}
    if not cc:
        return ""
    muc = cc.get("muc_do_thu_thach")
    ten = cc.get("ten_cap")
    doi = cc.get("do_thay_doi_duoc")
    lo_trinh = cc.get("lo_trinh") or []
    parts = []
    if muc:
        parts.append(f"Mức độ thử thách của cấu trúc duyên: {muc}"
                     + (f" ({ten})" if ten else "") + ".")
    if doi:
        parts.append(f"Khả năng chuyển hoá bằng rèn/chọn: {doi}.")
    if lo_trinh:
        parts.append("Lộ trình: " + "; ".join(str(x) for x in lo_trinh[:2]) + ".")
    parts.append("Đây là ĐỘ KHÓ của nguyên liệu trời ban (TÍNH), KHÔNG phải bản án — "
                 "mệnh là việc XỬ LÝ tính (Iron Rule #8).")
    return " ".join(parts)


def _ans_cung_phu_the(out: dict) -> str:
    """BUG3 — ráp câu BỎ QUA field rỗng + KHÔNG prefix tên-sao-trần (jargon) lên
    body, vì khi _plain_vi strip tên sao sẽ để lại ':' / '=' mồ côi
    ('Tham Lang: …' → ': …'). Body 'tinh_chat_phoi_ngau' đã tự chứa chủ ngữ, không
    cần nhãn tên sao. Cũng KHÔNG ghép 'Cung Phu Thê tại Tý, chính tinh: Tham Lang'
    (tên cung + tên sao đều là jargon → _plain_vi strip để lại 'Cung … tại ,:.:')."""
    cpt = out.get("cung_phu_the_tuvi") or {}
    if not cpt:
        return ""
    parts = []
    # GROUND vào branch THẬT của lá số (router chỉ _scrub → giữ 'Tỵ'; còn ở display
    # _plain_vi strip 'tại Tỵ' → 'an.' SẠCH, không để orphan ',:.:' nhờ
    # _ORPHAN_LOCATIVE_VERB_RE). Dùng 1 CÂU RIÊNG dạng 'an tại <chi>.' — KHÔNG ghép
    # tên cung + tên sao vào cùng cụm (cái đó mới sinh orphan). 'an tại' là locative
    # → khi strip object chỉ rụng locative, vế nghĩa phía sau còn nguyên.
    branch = (cpt.get("phu_the_branch") or "").strip()
    if branch:
        parts.append(f"Cung bạn đời của em an tại {branch}.")
    # Mở bằng câu THUẦN nghĩa, KHÔNG nhồi tên cung/chi/sao (jargon) vào — tránh
    # orphan ',:.:' sau khi _plain_vi strip. 'mượn sao đối cung' giữ vì là nghĩa.
    if cpt.get("muon_sao_doi_cung"):
        parts.append("Cung bạn đời mượn khí từ cung đối diện.")
    luan = cpt.get("chinh_tinh_luan") or []
    for item in luan[:2]:
        tc = (item.get("tinh_chat_phoi_ngau") or "").strip()
        if tc:
            parts.append(tc)
    dao = [s for s in (cpt.get("dao_hoa") or []) if (s or "").strip()]
    if dao:
        parts.append(f"Có sao đào hoa toạ cung bạn đời: {', '.join(dao)}.")
    parts.append("Đọc cấu trúc này như kiểu khí chất bạn đời cộng hưởng — vận hành tốt "
                 "nhất khi được ý thức, KHÔNG phán tốt/xấu cứng.")
    return " ".join(p for p in parts if p and p.strip())


def _fmt_van(x: dict) -> str:
    return f"vận {x.get('branch')} (tuổi {x.get('start_age')}-{x.get('end_age')})"


def _ans_dinh_thoi(out: dict) -> str:
    """BUG1 — trả lời 'năm nào cưới được?' ƯU TIÊN cửa sổ ĐANG/SẮP TỚI (end_age >=
    tuổi hiện tại). Nếu cửa sổ duyên chính đã trôi qua → nói TRUNG THỰC ('đã mở
    quanh tuổi X') + trỏ giai đoạn kế, KHÔNG phán 'cưới lúc 2-11'. Giữ paradigm:
    năm khí kích hoạt, KHÔNG tiên tri năm cứng (Iron Rule #4/#6)."""
    dt = out.get("dinh_thoi") or {}
    if not dt:
        return ""
    parts = []
    sap_toi = dt.get("cua_so_kich_hoat_sap_toi") or []
    da_qua = dt.get("cua_so_kich_hoat_da_qua") or []
    gg = dt.get("nam_can_giu_gin") or []

    if sap_toi:
        # Có cửa sổ phía trước (đang/sắp) → đó là câu trả lời chính.
        khoang = "; ".join(_fmt_van(x) for x in sap_toi[:2])
        parts.append(f"Cửa sổ khí duyên ĐANG/SẮP được KÍCH HOẠT: {khoang}.")
    elif da_qua:
        # Cửa sổ duyên CHÍNH đã trôi qua → nói thật, trỏ giai đoạn tới (không bịa
        # 'cưới lúc 2-11' — đó là vận tuổi thơ đã qua).
        khoang = "; ".join(_fmt_van(x) for x in da_qua[:2])
        parts.append(
            f"Cửa sổ khí duyên nổi rõ ở tầm đại vận đã MỞ QUANH {khoang} — giai đoạn "
            "đó đã qua. Ở tầm đại vận phía trước chưa nổi thêm cửa sổ kích hoạt rõ; "
            "giai đoạn TỚI duyên do em CHỦ ĐỘNG vun đắp (đào hoa lưu niên năm-tháng "
            "soi kỹ hơn khi cần) — KHÔNG có 'năm cưới định sẵn'."
        )
    else:
        parts.append("Ở tầm đại vận chưa nổi cửa sổ kích hoạt rõ; đọc theo 'năm khí "
                     "được kích hoạt', duyên do em chủ động vun đắp, KHÔNG phải tiên tri "
                     "năm cứng.")

    # Giai đoạn giữ gìn: chỉ nêu cái ĐANG/SẮP (bỏ cái đã qua cho gọn, đỡ rối).
    gg_sap = [x for x in gg if not x.get("da_qua")]
    if gg_sap:
        khoang = "; ".join(_fmt_van(x) for x in gg_sap[:2])
        parts.append(f"Giai đoạn cần GIỮ GÌN/chăm sóc quan hệ: {khoang}.")

    parts.append("Đây là 'năm khí được kích hoạt / năm cần giữ gìn', KHÔNG phải "
                 "lời tiên tri (Iron Rule #4/#6).")
    return " ".join(parts)


def _ans_personality(out: dict) -> str:
    """BUG4 — câu trả lời TÍNH CÁCH user-facing phải SẠCH jargon (như Tử Vi).

    'cach_yeu' là field đã DIỄN ĐẠT đời thường (cách yêu/cách thể hiện) — DÙNG làm
    nội dung chính. 'khi_chat' là chân-dung-sao DÀY jargon (Nam/Bắc Đẩu đệ X tinh,
    hóa khí vi…, hành âm-dương) → KHÔNG nhồi vào dap (nó tụt thẳng vào tom_tat, để
    lại rác sau khi scrub). Chỉ fallback khi tuyệt nhiên không có cach_yeu, và khi
    đó vẫn để _plain_vi (display) scrub jargon. KHÔNG prefix tên sao (jargon)."""
    p = out.get("personality") or {}
    profiles = p.get("profiles") or []
    parts = []
    for it in profiles[:2]:
        cy = (it.get("cach_yeu") or "").strip()
        if cy:
            parts.append(cy)
        else:
            # Không có cách-yêu sạch → fallback khí-chất (display._plain_vi sẽ scrub).
            kc = (it.get("khi_chat") or "").strip()
            if kc:
                parts.append(kc)
    if not parts:
        return ("Cung Mệnh vô chính diệu / chưa đủ dữ liệu khẩu vị — đọc tính cách qua "
                "đối chiếu Thập Thần Bát Tự (xem mục personality).")
    parts.append("Đọc làm NGUYÊN LIỆU để em chủ động xử lý (mệnh là động từ).")
    return " ".join(parts)


def _ans_batu_hon_nhan(out: dict) -> str:
    """BUG3 — ráp BỎ field rỗng + KHÔNG nhồi nhãn jargon ('官杀 (sao chồng):',
    '日支 Ngọ:') vào trước body. Body 'y_nghia' đã tự đủ nghĩa; nhãn jargon sau khi
    _plain_vi strip Hán/can-chi sẽ để lại '(): ' mồ côi."""
    b = out.get("batu_hon_nhan") or {}
    if not b:
        return ""
    parts = []
    tt_luan = b.get("trang_thai_luan")
    if isinstance(tt_luan, dict):
        mo_ta = (tt_luan.get("y_nghia") or tt_luan.get("mo_ta") or "").strip()
        if mo_ta:
            parts.append(mo_ta)
    png = b.get("phoi_ngau_cung_luan")
    y = ""
    if isinstance(png, dict):
        y = (png.get("y_nghia") or png.get("mo_ta") or "").strip()
    elif isinstance(png, str):
        y = png.strip()
    if y:
        parts.append(y)
    if not parts:
        parts.append("Đọc lực ngũ hành 官杀 + 日支 như cấu trúc khí hôn nhân, KHÔNG verdict.")
    return " ".join(p for p in parts if p and p.strip())


def _ans_song_phai_reconcile(out: dict) -> str:
    rec = out.get("song_phai_reconcile") or []
    if not rec:
        return ""
    parts = []
    for cd in rec[:2]:
        ten = cd.get("chu_de")
        hoi_tu = cd.get("khi_HOI_TU")
        if ten and hoi_tu:
            parts.append(f"{ten}: {hoi_tu}")
    parts.append("So đôi đọc bổ khuyết/cộng hưởng giữa hai cấu trúc, KHÔNG chấm điểm hợp/không.")
    return " ".join(parts)


def _ans_quy_trinh(out: dict, chi_tiet: str) -> str:
    """Rút từ quy_trinh_day_du theo bước cung con nêu trong section_nguon_chi_tiet
    ('… → bước cung PHU THÊ' / 'TỬ TỨC' / 'NÔ BỘC' / 'TÀI BẠCH')."""
    qt = out.get("quy_trinh_day_du") or {}
    tu_vi = (qt.get("tu_vi_12_buoc") or {}).get("buoc") or []
    # Tìm cung con trong chi_tiet (uppercase VN).
    cung_can = None
    for cung in ("PHU THÊ", "TỬ TỨC", "NÔ BỘC", "TÀI BẠCH"):
        if cung in (chi_tiet or "").upper():
            cung_can = cung.title()
            break
    target = None
    if cung_can:
        for b in tu_vi:
            ten = (b.get("ten_buoc") or "")
            if cung_can.lower() in ten.lower() or cung_can.replace(" ", "").lower() in ten.replace(" ", "").lower():
                target = b
                break
    if target is None:
        # fallback: tổng hợp kim tự tháp.
        tong = (qt.get("tong_hop_kim_tu_thap") or "").strip()
        if tong:
            return tong
        return ""
    # BUG3 — KHÔNG prefix 'ten_buoc' (chứa số thứ tự + tên cung-Hán '7. Cung Tử Tức
    # (子女宫) — …') vào trước luan: sau _plain_vi strip Hán/tên-cung sẽ để lại '7. — …:'
    # mồ côi. luan đã tự nêu cung; chỉ trả luan + đuôi paradigm.
    luan = (target.get("luan") or "").strip()
    if not luan:
        return ""
    return (luan + " Đọc cấu trúc cung này như 'duyên/tín hiệu cần để ý', KHÔNG phán "
            "có/không hay số cứng (giọng nhẹ, gợi y học/chuyên môn khi cần).")


# Bộ trích theo section_nguon.
_SECTION_EXTRACTORS = {
    "chan_doan_cap_do": _ans_chan_doan_cap_do,
    "cung_phu_the_tuvi": _ans_cung_phu_the,
    "dinh_thoi": _ans_dinh_thoi,
    "personality": _ans_personality,
    "batu_hon_nhan": _ans_batu_hon_nhan,
    "song_phai_reconcile": _ans_song_phai_reconcile,
}

# Câu QUYẾT ĐỊNH cần gieo quẻ Mai Hoa — trả lời cố định (paradigm).
_GIEO_QUE_PREFIX = (
    "Câu này nên gieo quẻ Mai Hoa quyết định: "
)
_LA_SO_DOI_MSG = (
    "Cần lá số người kia (dùng so-sánh-duyên) — chưa có thì đọc tham khảo cung Phu Thê "
    "của chính em (kiểu người hợp khí chất), KHÔNG chốt hợp/không."
)


def _he_tra_loi(q: dict) -> str:
    """Hệ trả lời (engine) cho câu — map he_chinh -> nhãn dễ đọc."""
    he = (q.get("he_chinh") or "").strip()
    if q.get("can_gieo_que"):
        return "mai_hoa"
    return {"tu_vi": "tu_vi", "bat_tu": "bat_tu", "kinh_dich": "mai_hoa"}.get(he, he or "tu_vi")


def _do_tin(q: dict, tra_loi: str, out: dict) -> str:
    """Độ tin của câu trả lời (cao/trung/thấp)."""
    if q.get("can_gieo_que") or q.get("can_la_so_doi"):
        # Quyết định/cần lá số đôi: engine KHÔNG chốt → độ tin của 'câu trả lời' thấp
        # (vì là lời gợi gieo quẻ / cần thêm dữ liệu).
        return "thấp"
    if (out.get("input") or {}).get("gio_sinh_thieu"):
        # Thiếu giờ sinh → cung phụ thuộc giờ kém tin.
        if q.get("section_nguon") in ("cung_phu_the_tuvi", "dinh_thoi", "quy_trinh_day_du"):
            return "trung"
    return "cao" if tra_loi else "thấp"


def _build_answer(q: dict, out: dict) -> str:
    """Rút câu trả lời cho 1 câu hỏi từ reading_output (đã paradigm-safe)."""
    # 1) Câu QUYẾT ĐỊNH nhị nguyên -> gieo quẻ Mai Hoa.
    if q.get("can_gieo_que"):
        note = q.get("paradigm_note") or (
            "câu hỏi quyết định/nhị nguyên — KHÔNG chốt từ lá số; quẻ soi tâm, em tự quyết."
        )
        return _GIEO_QUE_PREFIX + note

    # 2) Câu cần lá số người kia (và không phải quyết định) -> so-sánh-duyên.
    if q.get("can_la_so_doi"):
        return _LA_SO_DOI_MSG

    # 3) Rút từ section thật.
    section = q.get("section_nguon")
    if section == "quy_trinh_day_du":
        ans = _ans_quy_trinh(out, q.get("section_nguon_chi_tiet") or "")
    else:
        extractor = _SECTION_EXTRACTORS.get(section)
        ans = extractor(out) if extractor else ""

    if not ans:
        # Section không có data / không nhận dạng -> trả lời an toàn (không bịa).
        ans = ("Chưa đủ dữ liệu trên lá số để rút câu trả lời cho mục này — "
               "xem trực tiếp section liên quan trong báo cáo, KHÔNG suy đoán thêm.")
    return ans


def tra_loi_cau_hoi_tuoi(
    reading_output: dict,
    age: Optional[int] = None,
    gender: str = "nữ",
) -> list[dict]:
    """Trả list câu hỏi TOP theo nhóm tuổi + câu trả lời rút từ reading_output.

    Args:
        reading_output: dict trả từ read_tinh_duyen (đã paradigm-safe).
        age: tuổi. None -> lấy reading_output['input']['tuoi'] / stage.tuoi.
        gender: giới (engine cho nữ mệnh).

    Returns:
        list[{cau_hoi, he_tra_loi, tra_loi, can_gieo_que, can_la_so_doi, do_tin,
              section_nguon, tan_suat}].
    """
    # Import lazy để tránh vòng tròn import (reading.py import module này ở top-level).
    from .reading import _scrub

    out = reading_output or {}
    if age is None:
        age = (out.get("input") or {}).get("tuoi")
        if age is None:
            age = (out.get("stage") or {}).get("tuoi")
    age = int(age or 0)

    _key, block = _pick_nhom_tuoi(age)
    cau_hoi_list = block.get("cau_hoi") or []

    # cau_hoi_tuoi.json viết THUẦN NỮ (lấy chồng/khắc chồng/chồng ngoại tình…). Với NAM,
    # transform câu hỏi + câu trả lời qua gender_lens (lấy vợ/khắc thê/vợ ngoại tình…).
    # KHÔNG bao giờ phán 'tái hôn/khắc chồng' kiểu nữ cho nam — apply_gender đảo hết.
    is_male = GL.is_male(gender)

    counter = [0]
    results: list[dict] = []
    for q in cau_hoi_list:
        tra_loi = _build_answer(q, out)
        # NAM: đảo từ-vựng giới TRƯỚC khi rút gọn/scrub (lấy chồng→lấy vợ…).
        if is_male:
            tra_loi = GL.apply_gender(tra_loi, "nam")
        tra_loi = _shorten(tra_loi)
        # Hàng rào cứng defense-in-depth (text tự ráp cũng phải qua _scrub).
        scrubbed = _scrub(tra_loi)
        if scrubbed != tra_loi:
            counter[0] += 1
        tra_loi = scrubbed

        # Câu hỏi của user cũng đảo giới (NAM hỏi 'lấy vợ', không 'lấy chồng').
        cau_hoi_txt = q.get("cau_hoi")
        if is_male:
            cau_hoi_txt = GL.apply_gender(cau_hoi_txt, "nam")

        results.append({
            "cau_hoi": cau_hoi_txt,
            "he_tra_loi": _he_tra_loi(q),
            "tra_loi": tra_loi,
            "can_gieo_que": bool(q.get("can_gieo_que")),
            "can_la_so_doi": bool(q.get("can_la_so_doi")),
            "do_tin": _do_tin(q, tra_loi, out),
            "section_nguon": q.get("section_nguon"),
            "tan_suat": q.get("tan_suat"),
        })
    # Gắn cờ caution lên item đầu? Không — giữ contract là list thuần.
    return results


__all__ = ["tra_loi_cau_hoi_tuoi"]
