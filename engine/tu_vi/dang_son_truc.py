"""Trục Đằng Sơn — view phái sinh: 4 trợ-tinh (cực dương) ↔ 4 hoại-tinh (cực âm).

Paradigm: 《Tử Vi Hoàn Toàn Khoa Học》— Đằng Sơn, Ch.24-25 (journal
docs/design/tu-vi-dang-son-FULL-vong-18-p328-348.md). Luật "toàn-không":
Hình-Riêu-Không-Kiếp là PHẢN ĐỀ phương-vị BẮT BUỘC của Tả-Hữu-Xương-Khúc. Đọc lá số
mà chỉ thấy cực dương (trợ-tinh) là đọc LỆCH; phải soi cả cực âm (hoại-tinh) để cân
âm-dương.

Module này KHÔNG đặt lại sao — chỉ ĐỌC vị trí đã an trong `la_so` (tránh trùng sao,
bug từng dính 2026-06-13). 8 sao đã hiện diện sẵn trong engine, ở các nhóm:
    - Tả Phù / Hữu Bật / Văn Xương / Văn Khúc → la_so["phu_tinh"]
    - Thiên Hình                              → la_so["sao_le"]["Thiên Hình"]
    - Thiên Riêu (天姚, engine key "Thiên Diêu") → la_so["sao_q2"]["Thiên Diêu"]
    - Địa Không / Địa Kiếp                     → la_so["sat_tinh"]

⚠️ Iron Rule #4/#6 + #8 (đọc đồng dạng, KHÔNG predict cát/hung): view chỉ nêu CẤU TRÚC
— sao nào tới tam-phương-tứ-chính của cung target, cực nào đang trội. Không phán hên/xui.
"""

from __future__ import annotations

from .an_sao import BRANCHES_TVI

# 4 trợ-tinh (cực dương) — đã ở la_so["phu_tinh"]
TRO_TINH: tuple[str, ...] = ("Tả Phù", "Hữu Bật", "Văn Xương", "Văn Khúc")

# 4 hoại-tinh (cực âm) — tên hiển thị theo Đằng Sơn
HOAI_TINH: tuple[str, ...] = ("Thiên Hình", "Thiên Riêu", "Địa Không", "Địa Kiếp")

# Tên-hiển-thị → (nhóm nguồn trong la_so, key gốc trong nhóm đó)
_SOURCE: dict[str, tuple[str, str]] = {
    "Tả Phù":     ("phu_tinh", "Tả Phù"),
    "Hữu Bật":    ("phu_tinh", "Hữu Bật"),
    "Văn Xương":  ("phu_tinh", "Văn Xương"),
    "Văn Khúc":   ("phu_tinh", "Văn Khúc"),
    "Thiên Hình": ("sao_le",   "Thiên Hình"),
    "Thiên Riêu": ("sao_q2",   "Thiên Diêu"),   # 天姚 — engine an dưới tên "Thiên Diêu"
    "Địa Không":  ("sat_tinh", "Địa Không"),
    "Địa Kiếp":   ("sat_tinh", "Địa Kiếp"),
}


def _fix(x: int) -> int:
    return ((x % 12) + 12) % 12


def _tam_phuong_tu_chinh(menh_index: int) -> list[int]:
    """Tam-phương-tứ-chính của 1 cung: đồng cung + xung (đối) + 2 tam-hợp.

    Thứ tự trả về: [đồng cung, xung chiếu, tam-hợp 1, tam-hợp 2].
    """
    m = _fix(menh_index)
    return [m, _fix(m + 6), _fix(m + 4), _fix(m + 8)]


def _chieu(star_index: int | None, target_index: int) -> str:
    """Phân loại quan hệ phương-vị của 1 sao với cung target."""
    if star_index is None:
        return "không tới"
    s = _fix(star_index)
    t = _fix(target_index)
    if s == t:
        return "đồng cung"
    if s == _fix(t + 6):
        return "xung chiếu"
    if s in (_fix(t + 4), _fix(t + 8)):
        return "tam hợp chiếu"
    return "không tới"


def _palace_name(la_so: dict, branch_index: int) -> str:
    for p in la_so.get("palaces", []):
        if p.get("branch_index") == branch_index:
            return p.get("name", "")
    return ""


def _star_entry(la_so: dict, display_name: str, target_index: int) -> dict:
    src_key, engine_key = _SOURCE[display_name]
    idx = la_so.get(src_key, {}).get(engine_key)
    entry = {
        "branch_index": idx,
        "branch": BRANCHES_TVI[idx] if isinstance(idx, int) and 0 <= idx < 12 else "",
        "palace": _palace_name(la_so, idx) if isinstance(idx, int) else "",
        "chieu": _chieu(idx, target_index),
    }
    if engine_key != display_name:
        entry["engine_key"] = engine_key      # con trỏ tra cứu chéo (Thiên Riêu→Thiên Diêu)
    return entry


_MO_TA = {
    "tĩnh": "Trên trục Đằng Sơn, không trợ-tinh lẫn hoại-tinh nào tới "
            "tam-phương-tứ-chính cung {palace} — trục này TĨNH tại đây.",
    "thiên dương": "Trục Đằng Sơn nghiêng DƯƠNG: chỉ có trợ-tinh ({tro}) tới cung "
                   "{palace}, vắng cực âm — đọc dễ LỆCH về thuận lợi nếu không soi thêm hoại.",
    "thiên âm": "Trục Đằng Sơn nghiêng ÂM: chỉ có hoại-tinh ({hoai}) tới cung "
                "{palace}, vắng cực dương — cấu trúc thiên về thử thách/kỷ luật trên trục này.",
    "lưỡng cực giao": "Trục Đằng Sơn LƯỠNG CỰC: cả trợ-tinh ({tro}) lẫn hoại-tinh ({hoai}) "
                      "cùng tới cung {palace} — âm-dương giao, đọc phải cân cả hai cực.",
}


def build_dang_son_truc(la_so: dict, target_palace_index: int | None = None) -> dict:
    """Dựng view Trục Đằng Sơn cho 1 cung (mặc định: cung Mệnh).

    Args:
        la_so: output của cast_la_so (cần phu_tinh / sat_tinh / sao_q2 / sao_le /
               palaces / menh_index).
        target_palace_index: branch index cung muốn soi. None → cung Mệnh.

    Returns: dict gồm target, tam_phuong_tu_chinh, tro_tinh (4), hoai_tinh (4),
        can_bang {the, tro_toi_target, hoai_toi_target, mo_ta}. Tất cả JSON-safe.
    """
    target = _fix(target_palace_index if target_palace_index is not None
                  else la_so["menh_index"])

    tro = {name: _star_entry(la_so, name, target) for name in TRO_TINH}
    hoai = {name: _star_entry(la_so, name, target) for name in HOAI_TINH}

    tro_toi = [name for name in TRO_TINH if tro[name]["chieu"] != "không tới"]
    hoai_toi = [name for name in HOAI_TINH if hoai[name]["chieu"] != "không tới"]

    if tro_toi and hoai_toi:
        the = "lưỡng cực giao"
    elif tro_toi:
        the = "thiên dương"
    elif hoai_toi:
        the = "thiên âm"
    else:
        the = "tĩnh"

    palace = _palace_name(la_so, target) or BRANCHES_TVI[target]
    mo_ta = _MO_TA[the].format(
        palace=palace,
        tro=", ".join(tro_toi) or "—",
        hoai=", ".join(hoai_toi) or "—",
    )

    return {
        "paradigm": "Trục Đằng Sơn — luật toàn-không (Tử Vi Hoàn Toàn Khoa Học, Ch.24-25)",
        "target": {
            "palace": palace,
            "branch_index": target,
            "branch": BRANCHES_TVI[target],
        },
        "tam_phuong_tu_chinh": _tam_phuong_tu_chinh(target),
        "tro_tinh": tro,
        "hoai_tinh": hoai,
        "can_bang": {
            "the": the,
            "tro_toi_target": tro_toi,
            "hoai_toi_target": hoai_toi,
            "mo_ta": mo_ta,
        },
    }
