"""Phụ Lục Tiết khí + Bảng tra Hà Lạc (Xuân Cang p580-608).

Module load:
- 24 tiết khí (Lập Xuân → Đại Hàn) với mã ngày dương lịch + tháng âm + địa chi
- Lưu ý giờ sinh VN (5 thời kỳ múi giờ khác nhau 1945-nay) — CRITICAL cho engine
- Bảng Hóa Công theo tiết khí (mùa sinh → quẻ Hóa Công)
- Bảng Mệnh × Quẻ (paradigm ứng xử khi Mệnh Ngũ Hành gặp Quẻ Tiên Thiên)
- 8 quẻ quần chúng thích + 3 quẻ quần chúng ghét
- 21 hào đáng vị + 14 hào không đáng vị

Reference: Bát Tự Hà Lạc & Quỹ Đạo Đời Người (Xuân Cang) p580-608.
Seed: data/seeds/ha_lac_phu_luc_tiet_khi.json

⚠ Iron Rule: KHÔNG dùng để predict cát/hung. Chỉ paradigm + lookup.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

_SEED_PATH = Path(__file__).resolve().parents[2] / "data" / "seeds" / "ha_lac_phu_luc_tiet_khi.json"
_CACHE: dict | None = None


def _load() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_SEED_PATH, encoding="utf-8") as f:
            _CACHE = json.load(f)
    return _CACHE


def get_24_tiet_khi() -> list[dict]:
    """24 tiết khí với ngày dương lịch + tháng âm + địa chi."""
    return _load()["tiet_khi_24"]


def adjust_gio_sinh_vn(dt: datetime) -> tuple[str, str]:
    """Điều chỉnh giờ sinh VN theo 5 thời kỳ múi giờ khác nhau.

    Returns: (gio_ty_range, ghi_chu) — vd: ("23-01h", "Toàn quốc thống nhất UTC+7")

    CRITICAL: Engine PHẢI gọi hàm này TRƯỚC khi cast Hà Lạc.
    """
    data = _load()["luu_y_gio_sinh_viet_nam"]["thoi_ky"]
    for tk in data:
        try:
            start = datetime.strptime(tk["tu_ngay"], "%d-%m-%Y")
        except ValueError:
            continue
        end_str = tk["den_ngay"]
        if end_str == "nay":
            end = datetime(2099, 12, 31)
        else:
            try:
                end = datetime.strptime(end_str, "%d-%m-%Y")
            except ValueError:
                continue
        if start <= dt <= end:
            return tk["gio_ty"], tk["ghi_chu"]
    # Default trước 1945 = giờ TQ chuẩn
    return "23-01h", "Trước 1945 — giờ TQ truyền thống"


def get_hoa_cong_by_season(tiet_khi: str) -> dict | None:
    """Lấy quẻ Hóa Công theo mùa sinh (sau Đông Chí / Xuân Phân / Hạ Chí / Thu Phân).

    Args:
        tiet_khi: "Đông Chí" | "Xuân Phân" | "Hạ Chí" | "Thu Phân" | mùa sinh

    Returns dict: {sinh_sau, sinh_truoc, que_hoa_cong, y_nghia}
    """
    data = _load()["hoa_cong_theo_tiet_khi"]["bang"]
    for row in data:
        if row["sinh_sau"] in tiet_khi or row["sinh_truoc"] in tiet_khi:
            return row
    return None


def get_menh_x_que_paradigm(menh: str, que: str) -> str | None:
    """Tra paradigm khi Mệnh Ngũ Hành GẶP Quẻ Tiên Thiên.

    Args:
        menh: "Kim" | "Mộc" | "Thủy" | "Hỏa" | "Thổ"
        que: 1 trong 8 quẻ đơn: Càn/Khảm/Cấn/Chấn/Tốn/Ly/Khôn/Đoài

    Returns: Lời paradigm (vd: "Phú quý", "Hãm mắc kẹt")
    """
    menh_key = f"menh_{menh.lower().replace('ộ', 'o').replace('ỏ', 'o').replace('ủ', 'u').replace('ổ', 'o')}"
    # Normalize: Mộc→moc, Hỏa→hoa, Thủy→thuy, Thổ→tho, Kim→kim
    mapping = {"kim": "menh_kim", "mộc": "menh_moc", "thủy": "menh_thuy",
               "hỏa": "menh_hoa", "thổ": "menh_tho",
               "moc": "menh_moc", "thuy": "menh_thuy", "hoa": "menh_hoa", "tho": "menh_tho"}
    key = mapping.get(menh.lower(), menh_key)
    data = _load().get("menh_x_que_paradigm", {})
    menh_data = data.get(key)
    if not menh_data:
        return None
    return menh_data.get("que", {}).get(que)


def is_que_thich(que: str, hao: int) -> dict | None:
    """Check quẻ + hào có trong 8 quẻ quần chúng THÍCH."""
    for row in _load()["8_que_quan_chung_thich"]:
        if row["que"] == que and row["hao"] == hao:
            return row
    return None


def is_que_ghet(que: str, hao: int) -> dict | None:
    """Check quẻ + hào có trong 3 quẻ quần chúng GHÉT."""
    for row in _load()["3_que_quan_chung_ghet"]:
        if row["que"] == que and row["hao"] == hao:
            return row
    return None


def is_hao_dang_vi(que: str, hao: int) -> bool | None:
    """Check hào có ĐÁNG VỊ không (dương ở vị dương, âm ở vị âm)."""
    data = _load()["hao_dang_vi"]
    for row in data["21_hao_dang_vi_tieu_bieu"]:
        if row["que"] == que and row["hao"] == hao:
            return True
    for row in data["14_hao_khong_dang_vi_tieu_bieu"]:
        if row["que"] == que and row["hao"] == hao:
            return False
    return None  # Không có trong bảng reference


def build_phu_luc_context(menh: str | None, hoa_cong_que: str | None) -> str:
    """Build context string để inject vào LLM phê mệnh sâu."""
    parts = []
    parts.append("=== PHỤ LỤC HÀ LẠC (Xuân Cang p580-608) ===")

    if hoa_cong_que:
        parts.append(f"\n**Hóa Công**: {hoa_cong_que}")
        season = get_hoa_cong_by_season(hoa_cong_que)
        if season:
            parts.append(f"  Mùa sinh: sau {season['sinh_sau']} trước {season['sinh_truoc']}")
            parts.append(f"  Ý nghĩa: {season['y_nghia']}")

    if menh:
        parts.append(f"\n**Mệnh Ngũ Hành**: {menh}")
        for que in ["Càn", "Khảm", "Cấn", "Chấn", "Tốn", "Ly", "Khôn", "Đoài"]:
            p = get_menh_x_que_paradigm(menh, que)
            if p:
                parts.append(f"  • Gặp {que}: {p}")

    parts.append("\n⚠ Iron Rule: paradigm chứ KHÔNG predict.")
    return "\n".join(parts)


__all__ = [
    "get_24_tiet_khi",
    "adjust_gio_sinh_vn",
    "get_hoa_cong_by_season",
    "get_menh_x_que_paradigm",
    "is_que_thich",
    "is_que_ghet",
    "is_hao_dang_vi",
    "build_phu_luc_context",
]
