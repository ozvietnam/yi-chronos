"""Danh Sĩ Kiểm Chứng — 11 case study Hà Lạc đã kiểm chứng (Xuân Cang p420-583).

Paradigm Xuân Cang Phần Ba:
> Cấu trúc Hà Lạc ứng nghiệm với MỌI người trên trái đất, đặc biệt với nhà
> văn vì nhà văn KHÔNG bao giờ giấu được mình. Khí chất, mệnh vận, tính
> cách văn chương phơi bày ra trên trang giấy. Văn chương 1 người = bản sao
> hành trình số phận.

Module này load 11 chân dung danh sĩ Việt Nam (Tản Đà → Xuân Cang) với cấu
trúc Hà Lạc đầy đủ + paradigm + tác phẩm + sự kiện kiểm chứng, để LLM phê
mệnh sâu CITE được dữ liệu thật khi luận giải Hà Lạc cho user mới.

Iron rules:
1. KHÔNG dùng để predict.
2. Chỉ ĐỒNG DẠNG cross-reference: "Cấu trúc anh gần với X (Xuân Cang). Paradigm X là Y."
3. 11 danh sĩ là DỮ LIỆU lịch sử, KHÔNG phải fortune-telling reference.

Reference: Bát Tự Hà Lạc & Quỹ Đạo Đời Người (Xuân Cang) p420-583.
Seed: data/seeds/danh_si_ha_lac.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_SEED_PATH = Path(__file__).resolve().parents[2] / "data" / "seeds" / "danh_si_ha_lac.json"

_CACHE: dict | None = None


def load_danh_si_seed() -> dict:
    """Load 11 chân dung từ seed JSON (cached)."""
    global _CACHE
    if _CACHE is None:
        with open(_SEED_PATH, encoding="utf-8") as f:
            _CACHE = json.load(f)
    return _CACHE


def list_danh_si() -> list[dict]:
    """Danh sách 11 danh sĩ."""
    return load_danh_si_seed()["danh_si"]


def get_danh_si(danh_si_id: str) -> dict | None:
    """Lấy 1 chân dung theo id (vd: 'tan_da', 'to_hoai')."""
    for d in list_danh_si():
        if d["id"] == danh_si_id:
            return d
    return None


def find_by_tien_thien(que_tien_thien: str) -> list[dict]:
    """Tìm các danh sĩ có cùng quẻ Tiên Thiên với user."""
    return [
        d for d in list_danh_si()
        if d.get("cau_truc_ha_lac", {}).get("tien_thien", "").strip() == que_tien_thien.strip()
    ]


def find_by_hau_thien(que_hau_thien: str) -> list[dict]:
    """Tìm các danh sĩ có cùng quẻ Hậu Thiên với user."""
    return [
        d for d in list_danh_si()
        if d.get("cau_truc_ha_lac", {}).get("hau_thien", "").strip() == que_hau_thien.strip()
    ]


def find_similar_structure(que_tien_thien: str, que_hau_thien: str) -> list[dict]:
    """Tìm danh sĩ có cấu trúc Hà Lạc TƯƠNG ĐỒNG (cùng cả Tiên + Hậu Thiên).

    Trường hợp đặc biệt: Trần Đăng Khoa + Nguyễn Hiến Lê đều có
    `Phong Địa Quán` + `Địa Thiên Thái` — KHÁC Hóa Công → KHÁC kết quả.
    """
    matches_tien = find_by_tien_thien(que_tien_thien)
    return [d for d in matches_tien
            if d.get("cau_truc_ha_lac", {}).get("hau_thien", "").strip() == que_hau_thien.strip()]


def get_paradigm_patterns() -> list[dict]:
    """8 paradigm pattern vĩ mô em ngộ qua 11 chân dung."""
    return load_danh_si_seed().get("paradigm_cross_references", [])


def build_llm_context(que_tien_thien: str, que_hau_thien: str) -> str:
    """Build context string để inject vào prompt LLM khi phê mệnh sâu.

    Tìm danh sĩ có cấu trúc gần user → trả về paradigm + tác phẩm + sự kiện
    cho LLM cite trong luận giải.
    """
    matches = find_similar_structure(que_tien_thien, que_hau_thien)
    if not matches:
        # Fallback: chỉ match Tiên Thiên
        matches = find_by_tien_thien(que_tien_thien)
        if not matches:
            return ""

    parts = []
    parts.append("=== DANH SĨ HÀ LẠC ĐÃ KIỂM CHỨNG (Xuân Cang Phần Ba) ===")
    parts.append("")
    for d in matches[:3]:  # top 3
        parts.append(f"**{d['ten_that']}** ({d.get('but_danh', '—')}) [{d['nam_sinh']}{'-' + str(d['nam_mat']) if 'nam_mat' in d else '-'}]")
        ct = d.get("cau_truc_ha_lac", {})
        parts.append(f"  Tiên Thiên: {ct.get('tien_thien', '?')} | Hậu Thiên: {ct.get('hau_thien', '?')}")
        parts.append(f"  Paradigm CỐT: {d.get('paradigm_cot', '?')}")
        parts.append(f"  Tác phẩm: {', '.join(d.get('tac_pham_tieu_bieu', [])[:3])}")
        if d.get("phat_hien_dat"):
            parts.append(f"  Phát hiện đắt:")
            for p in d["phat_hien_dat"][:3]:
                parts.append(f"    • {p}")
        if d.get("loi_canh_bao"):
            parts.append(f"  ⚠ Cảnh báo: {d['loi_canh_bao']}")
        if d.get("loi_an_tam"):
            parts.append(f"  🌸 An tâm: {d['loi_an_tam']}")
        parts.append("")

    parts.append("⚠ KHÔNG predict — chỉ ĐỒNG DẠNG cross-reference.")
    return "\n".join(parts)


__all__ = [
    "load_danh_si_seed",
    "list_danh_si",
    "get_danh_si",
    "find_by_tien_thien",
    "find_by_hau_thien",
    "find_similar_structure",
    "get_paradigm_patterns",
    "build_llm_context",
]
