"""Tầng narrative Ngũ Uẩn — trường phái Tử Vi Bôn Ba (hiện đại VN).

Khung phân tích: mỗi chính tinh / cung soi qua 5 lớp Ngũ Uẩn (Phật học):
  Sắc  — biểu hiện ra bên ngoài (thân, thần thái, tác phong)
  Thọ  — cảm xúc, vui buồn sướng khổ đặc trưng
  Tưởng — lăng kính diễn giải, câu hỏi vô thức thường trực
  Hành — kiểu phản ứng, thói quen hành động
  Thức — niềm tin gốc sâu nhất + nỗi sợ gốc

Nguồn dữ liệu: ``data/yi_wiki/tuvibonba_ngu_uan.json`` (build bởi
``scripts/tuvibonba_import.py`` từ corpus 98 video Tử Vi Bôn Ba).

Đạo đức luận giải (Iron Rule #4/#6/#8 + Tử Vi Bôn Ba):
  - Lá số là BẢN ĐỒ, không phải bản án. Sao không tốt không xấu —
    miếu/hãm chỉ là ĐỘ KHÓ của bài học.
  - Luận đoán nào khiến người đọc sợ hãi và tê liệt hành động là luận
    đoán SAI, dù đúng sách đến đâu.
  - Chỉ nói điều người đọc có thể can thiệp được.
"""
from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Volume mount /opt/yi-chronos/data shadows data/ trong Docker — embedded first
_CANDIDATES = [
    ROOT / "embedded_data/yi_wiki/tuvibonba_ngu_uan.json",
    ROOT / "data/yi_wiki/tuvibonba_ngu_uan.json",
]

SCHOOL_LABEL = "Tử Vi Bôn Ba — quán chiếu Ngũ Uẩn"

UAN_KEYS = ["sac", "tho", "tuong", "hanh", "thuc"]
UAN_LABELS = {
    "sac": "Sắc — biểu hiện ra ngoài",
    "tho": "Thọ — cảm xúc",
    "tuong": "Tưởng — cách nhìn cuộc đời",
    "hanh": "Hành — phản ứng & thói quen",
    "thuc": "Thức — niềm tin sâu nhất",
}

# Lời nhắc paradigm gắn cuối mỗi khối luận giải (xoay vòng theo cung để đỡ lặp).
PARADIGM_REMINDERS = [
    "Lá số mô tả xu hướng vận hành, không phán kết cục — kết quả nằm ở những lựa chọn lặp lại hàng ngày.",
    "Sao không tốt không xấu: mỗi sao là một dạng lực sống — dùng đúng thành năng lực, dùng sai thành phá hoại.",
    "Miếu hay hãm chỉ là độ khó của bài học; trạng thái nào cũng có người vượt qua được bài của mình.",
    "Vận hạn không tạo ra biến cố — nó làm lộ điểm yếu tồn tại sẵn trong cách sống, để mình kịp điều chỉnh.",
    "Biết cấu trúc thì mới tạo ra tương lai; bản đồ chỉ có ích khi chính mình cầm lái.",
]


def _strip_accents(s: str) -> str:
    nfkd = unicodedata.normalize("NFD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _canon(s: str) -> str:
    """'Thiên Cơ' → 'thien_co' — khóa tra cứu không dấu."""
    return _strip_accents(s).lower().strip().replace(" ", "_").replace("-", "_")


@lru_cache(maxsize=1)
def _load_dataset() -> dict | None:
    for p in _CANDIDATES:
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return None
    return None


def invalidate_cache() -> None:
    _load_dataset.cache_clear()
    _index.cache_clear()


@lru_cache(maxsize=1)
def _index() -> dict:
    """Index dataset: by_star / by_palace / nguyen_ly / quan_diem / ung_dung."""
    ds = _load_dataset()
    idx = {"by_star": {}, "by_palace": {}, "nguyen_ly": {}, "quan_diem": {},
           "ung_dung": {}, "meo_sao_o_dau": {}}
    if not ds:
        return idx
    for rec in ds.get("records", []):
        t = rec.get("type")
        if t == "chinh_tinh" and rec.get("sao"):
            idx["by_star"][_canon(rec["sao"])] = rec
        elif t == "cung" and rec.get("cung"):
            idx["by_palace"][_canon(rec["cung"])] = rec
        elif t == "nguyen_ly" and rec.get("ten"):
            idx["nguyen_ly"][rec["ten"]] = rec
        elif t == "quan_diem" and rec.get("ten"):
            idx["quan_diem"][rec["ten"]] = rec
        elif t == "ung_dung" and rec.get("ten"):
            idx["ung_dung"][rec["ten"]] = rec
    # Mẹo "sao X đóng đâu thì nơi đó..." — items của record mẹo nhìn nhanh
    for ten, rec in idx["nguyen_ly"].items():
        if "Mẹo nhìn nhanh" in ten:
            for item in rec.get("items") or []:
                name = item.get("ten") or ""
                if name:
                    idx["meo_sao_o_dau"][_canon(name)] = item.get("noi_dung") or ""
    return idx


def dataset_available() -> bool:
    return bool(_index()["by_star"])


def get_star_profile(star_vi: str) -> dict | None:
    """Profile Ngũ Uẩn của một chính tinh (tên tiếng Việt, vd 'Thiên Cơ').

    Cung không có chính tinh → dùng 'Vô Chính Diệu'.
    """
    return _index()["by_star"].get(_canon(star_vi))


def get_palace_profile(palace_vi: str) -> dict | None:
    """Profile Ngũ Uẩn của một cung (vd 'Phúc Đức')."""
    return _index()["by_palace"].get(_canon(palace_vi))


def get_nguyen_ly(ten_substr: str) -> dict | None:
    """Tìm record nguyên lý theo tên gần đúng (substring, không dấu)."""
    needle = _canon(ten_substr)
    for ten, rec in _index()["nguyen_ly"].items():
        if needle in _canon(ten):
            return rec
    return None


def sao_o_dau_thi(star_vi: str) -> str | None:
    """Câu 'sao X đóng ở đâu thì nơi đó là nơi ta...' từ mẹo nhìn nhanh."""
    hit = _index()["meo_sao_o_dau"].get(_canon(star_vi))
    if hit:
        return hit
    rec = get_star_profile(star_vi)
    if rec:
        return rec.get("sao_o_dau_thi")
    return None


# ─── Ngôn ngữ "độ khó bài học" thay cho tốt/xấu ──────────────────────────────

DO_KHO_WORDING = {
    "favorable": "bối cảnh thuận — lực sao và bối cảnh cùng chiều, bài học dễ vào đà",
    "mixed": "bối cảnh pha trộn — có đà thuận lẫn điểm phải rèn, kết quả tùy cách dùng lực",
    "challenging": "bài học có độ khó cao — lực vẫn nguyên đó nhưng đòi tay lái vững và nhịp chậm hơn",
    "empty": "bối cảnh mở (Vô Chính Diệu) — linh hoạt, khó đoán, đổi theo môi trường; cần một niềm tin đủ lớn để theo lâu một con đường",
}


def do_kho_label(polarity_tag: str) -> str:
    return DO_KHO_WORDING.get(polarity_tag, DO_KHO_WORDING["mixed"])


def _first_sentences(text: str | None, n: int = 2) -> str:
    """Lấy n câu đầu của một đoạn (để ghép văn liền mạch, tránh quá dài)."""
    if not text:
        return ""
    parts = [p.strip() for p in text.replace("…", ".").split(".") if p.strip()]
    return (". ".join(parts[:n]) + ".") if parts else ""


def _uan_of(rec: dict, key: str) -> dict:
    """Lấy uẩn `key` từ record chinh_tinh — chấp nhận cả dạng str lẫn dict."""
    u = (rec.get("ngu_uan") or {}).get(key)
    if u is None:
        return {}
    if isinstance(u, str):
        return {"mo_ta": u}
    return u


def compose_palace_ngu_uan(
    palace_name: str,
    chinh_stars: list[str],
    hoa_attachments: list[dict] | None = None,
    mieu_ham_levels: dict[str, str] | None = None,
    polarity_tag: str = "mixed",
    reminder_seed: int = 0,
) -> dict | None:
    """Khối diễn giải Ngũ Uẩn cho 1 cung trong lá số.

    Args:
        palace_name: tên cung tiếng Việt ('Mệnh', 'Phu Thê', ...).
        chinh_stars: chính tinh tại cung (tên tiếng Việt); [] = Vô Chính Diệu.
        hoa_attachments: [{star, hoa, label}] tứ hóa đóng tại cung.
        mieu_ham_levels: {star_vi: 'miếu'/'vượng'/'đắc'/'bình'/'lạc'/'hãm'}.
        polarity_tag: tag độ khó đã tính ở interpretation.
        reminder_seed: số để xoay vòng lời nhắc paradigm (vd index cung).

    Returns None nếu dataset chưa có (web fallback về reading cũ).
    """
    if not dataset_available():
        return None

    hoa_attachments = hoa_attachments or []
    mieu_ham_levels = mieu_ham_levels or {}
    palace_rec = get_palace_profile(palace_name)

    star_names = list(chinh_stars) or ["Vô Chính Diệu"]
    star_recs: list[tuple[str, dict | None]] = [
        (s, get_star_profile(s)) for s in star_names
    ]

    # ── Bối cảnh (định nghĩa lại cung) ──
    boi_canh = None
    cau_hoi = None
    if palace_rec:
        boi_canh = palace_rec.get("dinh_nghia_lai")
        cau_hoi = palace_rec.get("cau_hoi_tu_van")

    # ── Sao định vị trong bối cảnh ──
    sao_dinh_vi = []
    for s, rec in star_recs:
        level = mieu_ham_levels.get(s)
        hoa = next((h["hoa"] for h in hoa_attachments if h.get("star") == s), None)
        sao_dinh_vi.append({
            "sao": s,
            "tom_gon": (rec or {}).get("tom_gon") or [],
            "dinh_vi": (rec or {}).get("menh_de_dinh_vi"),
            "o_dau_thi": sao_o_dau_thi(s),
            "mieu_ham": level,
            "hoa": hoa,
        })

    # ── 5 uẩn: bối cảnh cung + lực của từng sao ──
    ngu_uan_doc = []
    for key in UAN_KEYS:
        pieces = []
        if palace_rec:
            p_uan = (palace_rec.get("ngu_uan") or {}).get(key)
            if isinstance(p_uan, dict):
                p_uan = p_uan.get("mo_ta")
            if p_uan:
                pieces.append(_first_sentences(p_uan, 2))
        for s, rec in star_recs:
            if not rec:
                continue
            u = _uan_of(rec, key)
            mo_ta = u.get("mo_ta")
            if mo_ta:
                label = f"{s}: " if len(star_recs) > 1 else ""
                pieces.append(f"{label}{_first_sentences(mo_ta, 3)}")
        if pieces:
            ngu_uan_doc.append({
                "key": key,
                "label": UAN_LABELS[key],
                "text": " ".join(pieces),
            })

    # ── Khi thuận / khi lệch (cả hai mặt — người đọc tự chọn cách dùng lực) ──
    thuan_parts, lech_parts = [], []
    for s, rec in star_recs:
        if not rec:
            continue
        for key in UAN_KEYS:
            u = _uan_of(rec, key)
            if u.get("khi_manh"):
                thuan_parts.append(u["khi_manh"])
            if u.get("khi_lech"):
                lech_parts.append(u["khi_lech"])
    # Tứ hóa nghiêng cán cân diễn đạt (không đổi dữ kiện, chỉ thêm ghi chú)
    hoa_notes = []
    for h in hoa_attachments:
        if h.get("hoa") == "Kỵ":
            hoa_notes.append(
                f"{h['star']} Hóa Kỵ: giai đoạn này mặt 'khi lệch' dễ bị kích hoạt hơn — "
                "đây là tín hiệu để chậm lại và soi kỹ, không phải án phạt."
            )
        elif h.get("hoa") in ("Lộc", "Quyền", "Khoa"):
            hoa_notes.append(
                f"{h['star']} Hóa {h['hoa']}: dòng lực đang được tiếp thêm — "
                "thuận đà nhưng đừng để thành chủ quan."
            )

    thuan = " ".join(_first_sentences(t, 1) for t in thuan_parts[:3]) or None
    lech = " ".join(_first_sentences(t, 1) for t in lech_parts[:3]) or None

    # ── Cần gì để phát huy ──
    can_phat_huy = [
        rec["can_de_phat_huy"] for _, rec in star_recs
        if rec and rec.get("can_de_phat_huy")
    ]

    reminder = PARADIGM_REMINDERS[reminder_seed % len(PARADIGM_REMINDERS)]

    return {
        "available": True,
        "school": SCHOOL_LABEL,
        "do_kho": do_kho_label(polarity_tag),
        "boi_canh": boi_canh,
        "sao_dinh_vi": sao_dinh_vi,
        "ngu_uan": ngu_uan_doc,
        "thuan": thuan,
        "lech": lech,
        "hoa_notes": hoa_notes,
        "can_de_phat_huy": can_phat_huy,
        "cau_hoi_tu_soi": cau_hoi,
        "nhac_paradigm": reminder,
    }


def compose_main_reading_v2(
    palace_name: str,
    chinh_stars: list[str],
    ngu_uan_block: dict | None,
    polarity_tag: str,
) -> str | None:
    """Đoạn văn mở đầu giàu ngữ nghĩa cho main_reading (thay template cũ).

    Trả None nếu thiếu dữ liệu (caller giữ template cũ làm fallback).
    """
    if not ngu_uan_block:
        return None
    parts: list[str] = []
    if ngu_uan_block.get("boi_canh"):
        parts.append(f"Cung {palace_name} — {_first_sentences(ngu_uan_block['boi_canh'], 2)}")
    for sv in ngu_uan_block.get("sao_dinh_vi", [])[:2]:
        seg = []
        if sv.get("dinh_vi"):
            seg.append(f"{sv['sao']}: {_first_sentences(sv['dinh_vi'], 1)}")
        if sv.get("o_dau_thi"):
            seg.append(_first_sentences(sv["o_dau_thi"], 1))
        if sv.get("mieu_ham"):
            seg.append(f"Tại đây sao ở thế {sv['mieu_ham']} — độ khó của bài học, không phải lời khen chê.")
        if seg:
            parts.append(" ".join(seg))
    parts.append(f"Tổng thể: {do_kho_label(polarity_tag)}.")
    if ngu_uan_block.get("cau_hoi_tu_soi"):
        parts.append(_first_sentences(ngu_uan_block["cau_hoi_tu_soi"], 1))
    return " ".join(p for p in parts if p).strip() or None
