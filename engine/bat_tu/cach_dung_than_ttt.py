"""Cách Dụng Thần — Trích Thiên Tủy paradigm (Chương 21-22).

Phân biệt với engine `cach_cuc.py` (10 cách phổ thông Tử Bình):
- Đây tập trung vào **DỤNG THẦN** theo paradigm Trích Thiên Tủy:
  - 5 cách Quan Sát (Sát dụng Ấn / Thực Thần chế Sát / Hợp Quan lưu Sát / Quan Sát hỗn tạp / Chế Sát quá mức)
  - 5 cách Thương Quan (Thương Quan dụng Ấn / Tài / Kiếp / Thương / Quan)
  - 8 patterns "Thương Quan kiến Quan" nuanced

Paradigm CỐT (Nhậm Thiết Tiều Ch.21):
> "Quan Sát hỗn tạp, phú quý nhiều. Quan sát đương lệnh, nhật chủ cần
>  phải tọa ân thụ, tất khí quan sát được lưu thông."

Khác Thiệu Vĩ Hoa: KHÔNG sợ Quan Sát hỗn tạp khi đủ điều kiện.

Paradigm Thương Quan (Ch.22):
> "Thương Quan có Tài, đều có thể gặp Quan.
>  Thương Quan mà không có Tài, đều không nên gặp Quan."

⚠️ Iron Rule #4+6: Output là paradigm pattern, không predict tĩnh.
"""

from __future__ import annotations


# ─── 8 patterns "Thương Quan kiến Quan" (Ch.22) ─────────────────────────────
# Khi Trụ có Thương Quan + gặp Quan (lưu niên/đại vận hoặc trong Tứ Trụ):
# 4 patterns OK + 4 patterns HUNG

THUONG_QUAN_KIEN_QUAN_PATTERNS = [
    {
        "name": "Thân nhược + Thương Quan vượng + CÓ Ấn",
        "verdict": "ok",
        "reason": "Ấn khắc chế Thương Quan + sinh thân → Quan đến không phá",
    },
    {
        "name": "Thân vượng + Thương Quan vượng + CÓ Tài (KHÔNG Quan trong Tứ Trụ)",
        "verdict": "ok",
        "reason": "Thương Quan sinh Tài, Tài sinh Quan — chuỗi tự nhiên",
    },
    {
        "name": "Thương Quan vượng + Tài khinh + CÓ Tỉ Kiếp",
        "verdict": "ok",
        "reason": "Tỉ Kiếp trợ Thân + cùng sinh Thương Quan → có thể gặp Quan",
    },
    {
        "name": "Nhật Chủ vượng + Thương Quan khinh + KHÔNG Ấn",
        "verdict": "ok",
        "reason": "Thương Quan nhẹ + Ấn không khắc Thương Quan → Quan đến OK",
    },
    {
        "name": "Thương Quan vượng + KHÔNG Tài + gặp Quan",
        "verdict": "hung",
        "reason": "Không có Tài chuyển hóa → Thương Quan trực tiếp khắc Quan = ĐẠI HỌA",
    },
    {
        "name": "Thương Quan vượng + Thân nhược + gặp Quan",
        "verdict": "hung",
        "reason": "Thân đã yếu, Thương Quan tiết khí, Quan đến khắc thân → hung",
    },
    {
        "name": "Thương Quan nhược + Tài khinh + gặp Quan",
        "verdict": "hung",
        "reason": "Thiếu cả Tài + Thương Quan → không có buffer khi Quan đến",
    },
    {
        "name": "Thương Quan nhược + CÓ Ấn + gặp Quan",
        "verdict": "hung",
        "reason": "Ấn đã khắc Thương Quan suy, gặp Quan thêm khắc thân → suy thêm",
    },
]


def classify_thuong_quan_kien_quan(state: dict) -> dict | None:
    """Phân loại pattern khi Tứ Trụ có cấu trúc Thương Quan + Quan.

    Args:
        state: bat_tu state with ngu_hanh.counts + day_master_assessment + thap_than_distribution

    Returns: dict {pattern, verdict, reason, narrative} or None
    """
    distrib = state.get("thap_than_distribution", {})
    if not isinstance(distrib, dict):
        return None

    # Structure: {visible: {tt: n}, hidden: {tt: n}}
    visible = distrib.get("visible", {}) if isinstance(distrib.get("visible"), dict) else {}
    hidden = distrib.get("hidden", {}) if isinstance(distrib.get("hidden"), dict) else {}

    # Get counts of each Thập Thần (visible weight 1.0, hidden 0.5)
    def cnt(tt: str) -> float:
        v = float(visible.get(tt, 0) or 0)
        h = float(hidden.get(tt, 0) or 0)
        return v + 0.5 * h

    tquan = cnt("Thương Quan")
    thuc = cnt("Thực Thần")
    quan = cnt("Chính Quan")
    sat = cnt("Thất Sát")
    tai = cnt("Chính Tài") + cnt("Thiên Tài")
    an = cnt("Chính Ấn") + cnt("Thiên Ấn") + cnt("Kiêu Thần")
    tikiep = cnt("Tỉ Kiên") + cnt("Tỉ Kiếp") + cnt("Kiếp Tài")

    # Need both Thương Quan AND Quan present
    if tquan < 0.5 or (quan + sat) < 0.5:
        return None

    # Get strength
    strength = state.get("ngu_hanh", {}).get("day_master_assessment", {}).get("strength_tag", "")
    day_strong = strength in ("strong", "very_strong")
    day_weak = strength in ("weak", "very_weak")

    # Classify
    tq_vuong = tquan >= 2
    tq_khinh = tquan < 2

    if day_weak and tq_vuong and an >= 1:
        pattern = THUONG_QUAN_KIEN_QUAN_PATTERNS[0]
    elif day_strong and tq_vuong and tai >= 1.5:
        pattern = THUONG_QUAN_KIEN_QUAN_PATTERNS[1]
    elif tq_vuong and tai < 1.5 and tikiep >= 1:
        pattern = THUONG_QUAN_KIEN_QUAN_PATTERNS[2]
    elif day_strong and tq_khinh and an < 1:
        pattern = THUONG_QUAN_KIEN_QUAN_PATTERNS[3]
    elif tq_vuong and tai < 1:
        pattern = THUONG_QUAN_KIEN_QUAN_PATTERNS[4]  # HUNG
    elif tq_vuong and day_weak:
        pattern = THUONG_QUAN_KIEN_QUAN_PATTERNS[5]  # HUNG
    elif tq_khinh and tai < 1:
        pattern = THUONG_QUAN_KIEN_QUAN_PATTERNS[6]  # HUNG
    elif tq_khinh and an >= 1:
        pattern = THUONG_QUAN_KIEN_QUAN_PATTERNS[7]  # HUNG
    else:
        return None

    return {
        "pattern_name": pattern["name"],
        "verdict": pattern["verdict"],
        "reason": pattern["reason"],
        "counts": {
            "thuong_quan": round(tquan, 1),
            "quan_sat": round(quan + sat, 1),
            "tai": round(tai, 1),
            "an": round(an, 1),
            "ti_kiep": round(tikiep, 1),
        },
        "narrative": (
            f"**Thương Quan kiến Quan — pattern: {pattern['name']}** "
            f"→ verdict: {pattern['verdict'].upper()}\n\n"
            f"Lý do: {pattern['reason']}\n\n"
            f"Quote Trích Thiên Tủy Ch.22: _'Thương Quan có Tài, đều có thể gặp Quan. "
            f"Thương Quan mà không có Tài, đều không nên gặp Quan.'_"
        ),
        "source": "Trích Thiên Tủy bình chú — Nhậm Thiết Tiều, Chương 22 Thương Quan, tr.85-86",
    }


# ─── 5 cách Quan Sát (Ch.21) ───────────────────────────────────────────────
QUAN_SAT_CACH = [
    {
        "id": "sat_dung_an",
        "name": "Sát dụng Ấn cách (殺用印格)",
        "essence": "Sát mạnh + Nhật chủ nhược → Ấn hóa Sát sinh thân",
        "favorable_vận": "Ấn vận / Tỉ Kiếp vận",
        "ky_vận": "Tài vận (khắc Ấn) / Thực Thương vận (khắc Sát phá hóa)",
    },
    {
        "id": "thuc_than_che_sat",
        "name": "Thực Thần chế Sát cách (食神制殺格)",
        "essence": "Thân vượng + Sát mạnh → Thực Thần khắc Sát",
        "favorable_vận": "Thực Thương vận / Ấn vận (khi Thực Thương quá vượng)",
        "ky_vận": "Ấn vận sớm (chế Thực Thương) / Tài vận (sinh Sát)",
    },
    {
        "id": "hop_quan_luu_sat",
        "name": "Hợp Quan lưu Sát cách (合官留殺格)",
        "essence": "Quan Sát hỗn tạp → dùng can hợp khử Quan giữ Sát (thuần thanh)",
        "favorable_vận": "Vận theo Sát (Ấn / Thực Thương / Tài tùy thân)",
        "ky_vận": "Vận làm Quan tái xuất → hỗn tạp lại",
    },
    {
        "id": "quan_sat_hon_tap",
        "name": "Quan Sát hỗn tạp cách (官殺混雜格)",
        "essence": "Quan + Sát cùng có → Nhật chủ phải tọa Ấn để lưu thông",
        "favorable_vận": "Ấn vận / Tỉ Kiếp khi thân nhược",
        "ky_vận": "Tài vận khắc Ấn → mất buffer",
    },
    {
        "id": "che_sat_qua_muc",
        "name": "Chế Sát quá mức cách (制殺太過格)",
        "essence": "Thực Thương quá nhiều khắc Sát hết → cần Tài cứu Sát",
        "favorable_vận": "Tài vận (sinh Sát) / Ấn vận (chế Thực Thương)",
        "ky_vận": "Thực Thương vận thêm",
    },
]


# ─── 5 cách Thương Quan (Ch.22) ────────────────────────────────────────────
THUONG_QUAN_CACH = [
    {
        "id": "thuong_quan_dung_an",
        "name": "Thương Quan dụng Ấn cách (傷官用印格 / Thương Quan Bội Ấn)",
        "essence": "Thân nhược + Thương Quan vượng → Ấn khắc chế Thương Quan + sinh thân",
        "favorable_vận": "Ấn vận / Quan vận (sinh Ấn)",
        "ky_vận": "Tài vận (khắc Ấn) / Thực Thương vận",
        "paradigm": "'Thương Quan Bội Ấn — tinh hoa phát tiết, thông minh đại quý'",
    },
    {
        "id": "thuong_quan_dung_tai",
        "name": "Thương Quan dụng Tài cách (傷官生財格)",
        "essence": "Thân vượng + Thương Quan vượng → Tài hóa Thương Quan thành lộc",
        "favorable_vận": "Tài vận / Thực Thương vận (sinh Tài)",
        "ky_vận": "Ấn vận (khắc Thương Quan + chế Tài chậm) / Tỉ Kiếp đoạt Tài",
    },
    {
        "id": "thuong_quan_dung_kiep",
        "name": "Thương Quan dụng Kiếp cách (傷官用劫格)",
        "essence": "Thân nhược + Thương Quan vượng + KHÔNG Ấn → dùng Tỉ Kiếp trợ thân",
        "favorable_vận": "Tỉ Kiếp vận / Ấn vận",
        "ky_vận": "Tài vận / Quan vận",
    },
    {
        "id": "thuong_quan_dung_thuong",
        "name": "Thương Quan dụng Thương cách (傷官用傷格)",
        "essence": "Thân vượng + Thương Quan khinh → dùng thêm Thương Quan để tiết khí",
        "favorable_vận": "Thực Thương vận / Tài vận",
        "ky_vận": "Ấn vận (khắc Thương Quan)",
    },
    {
        "id": "gia_thuong_quan",
        "name": "Giả Thương Quan cách (假傷官格)",
        "essence": "Tướng có Thương Quan nhưng thực không thuần — phức tạp, tùy ngữ cảnh",
        "favorable_vận": "Tùy biến hóa Tứ Trụ",
        "ky_vận": "Tùy",
    },
]


def list_quan_sat_cach() -> list[dict]:
    """Return 5 cách Quan Sát theo Trích Thiên Tủy Ch.21."""
    return QUAN_SAT_CACH


def list_thuong_quan_cach() -> list[dict]:
    """Return 5 cách Thương Quan theo Trích Thiên Tủy Ch.22."""
    return THUONG_QUAN_CACH
