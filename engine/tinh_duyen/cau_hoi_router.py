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
    cpt = out.get("cung_phu_the_tuvi") or {}
    if not cpt:
        return ""
    parts = []
    branch = cpt.get("phu_the_branch")
    chinh = cpt.get("chinh_tinh") or []
    if branch:
        muon = " (mượn sao đối cung)" if cpt.get("muon_sao_doi_cung") else ""
        parts.append(f"Cung Phu Thê tại {branch}{muon}"
                     + (f", chính tinh: {', '.join(chinh)}." if chinh else "."))
    luan = cpt.get("chinh_tinh_luan") or []
    for item in luan[:2]:
        tc = item.get("tinh_chat_phoi_ngau")
        if tc:
            parts.append(f"{item.get('sao')}: {tc}")
    if cpt.get("dao_hoa"):
        parts.append(f"Đào hoa toạ Phu Thê: {', '.join(cpt['dao_hoa'])}.")
    parts.append("Đọc cấu trúc này như kiểu khí chất bạn đời cộng hưởng — vận hành tốt "
                 "nhất khi được ý thức, KHÔNG phán tốt/xấu cứng.")
    return " ".join(p for p in parts if p)


def _ans_dinh_thoi(out: dict) -> str:
    dt = out.get("dinh_thoi") or {}
    if not dt:
        return ""
    parts = []
    kh = dt.get("nam_kich_hoat") or []
    gg = dt.get("nam_can_giu_gin") or []
    if kh:
        khoang = "; ".join(
            f"vận {x.get('branch')} (tuổi {x.get('start_age')}-{x.get('end_age')})"
            for x in kh[:2]
        )
        parts.append(f"Cửa sổ khí duyên được KÍCH HOẠT: {khoang}.")
    if gg:
        khoang = "; ".join(
            f"vận {x.get('branch')} (tuổi {x.get('start_age')}-{x.get('end_age')})"
            for x in gg[:2]
        )
        parts.append(f"Giai đoạn cần GIỮ GÌN/chăm sóc quan hệ: {khoang}.")
    if not parts:
        parts.append("Trên cấu trúc hiện tại chưa nổi cửa sổ kích hoạt rõ ở tầm đại vận; "
                     "đọc theo 'năm khí được kích hoạt', KHÔNG phải tiên tri năm cứng.")
    else:
        parts.append("Đây là 'năm khí được kích hoạt / năm cần giữ gìn', KHÔNG phải "
                     "lời tiên tri (Iron Rule #4/#6).")
    return " ".join(parts)


def _ans_personality(out: dict) -> str:
    p = out.get("personality") or {}
    profiles = p.get("profiles") or []
    parts = []
    for it in profiles[:2]:
        kc = it.get("khi_chat")
        cy = it.get("cach_yeu")
        seg = it.get("sao", "")
        if kc:
            seg += f" — khí chất: {kc}"
        if cy:
            seg += f"; cách yêu: {cy}"
        if seg:
            parts.append(seg)
    if not parts:
        return ("Cung Mệnh vô chính diệu / chưa đủ dữ liệu khẩu vị — đọc tính cách qua "
                "đối chiếu Thập Thần Bát Tự (xem mục personality).")
    parts.append("Đọc làm NGUYÊN LIỆU để em chủ động xử lý (mệnh là động từ).")
    return " ".join(parts)


def _ans_batu_hon_nhan(out: dict) -> str:
    b = out.get("batu_hon_nhan") or {}
    if not b:
        return ""
    parts = []
    tt_luan = b.get("trang_thai_luan")
    if isinstance(tt_luan, dict):
        mo_ta = tt_luan.get("y_nghia") or tt_luan.get("mo_ta") or ""
        if mo_ta:
            parts.append(f"Trạng thái 官杀 (sao chồng): {mo_ta}")
    png = b.get("phoi_ngau_cung_luan")
    if isinstance(png, dict):
        y = png.get("y_nghia") or png.get("mo_ta")
        if y:
            parts.append(f"Cung phối ngẫu (日支 {b.get('nhat_chi')}): {y}")
    elif isinstance(png, str):
        parts.append(f"Cung phối ngẫu ({b.get('nhat_chi')}): {png}")
    if not parts:
        parts.append("Đọc lực ngũ hành 官杀 + 日支 như cấu trúc khí hôn nhân, KHÔNG verdict.")
    return " ".join(parts)


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
    ('… → bước cung TỬ TỨC' / 'NÔ BỘC' / 'TÀI BẠCH')."""
    qt = out.get("quy_trinh_day_du") or {}
    tu_vi = (qt.get("tu_vi_12_buoc") or {}).get("buoc") or []
    # Tìm cung con trong chi_tiet (uppercase VN).
    cung_can = None
    for cung in ("TỬ TỨC", "NÔ BỘC", "TÀI BẠCH", "TỬ TỨC"):
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
    luan = target.get("luan") or ""
    ten = target.get("ten_buoc") or ""
    seg = (f"{ten}: " if ten else "") + luan
    seg += (" Đọc cấu trúc cung này như 'duyên/tín hiệu cần để ý', KHÔNG phán có/không "
            "hay số cứng (giọng nhẹ, gợi y học/chuyên môn khi cần).")
    return seg


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

    counter = [0]
    results: list[dict] = []
    for q in cau_hoi_list:
        tra_loi = _build_answer(q, out)
        tra_loi = _shorten(tra_loi)
        # Hàng rào cứng defense-in-depth (text tự ráp cũng phải qua _scrub).
        scrubbed = _scrub(tra_loi)
        if scrubbed != tra_loi:
            counter[0] += 1
        tra_loi = scrubbed

        results.append({
            "cau_hoi": q.get("cau_hoi"),
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
