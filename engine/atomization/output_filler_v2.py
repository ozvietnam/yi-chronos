"""OutputFiller v2 — render 3-Layer cho lá số bất kỳ.

3-Layer paradigm (Anh chốt):
- Lớp 1: **Chuyện về anh** — narrative cá nhân hóa
- Lớp 2: **Vì sao** — paradigm warnings explain
- Lớp 3: **Sách cổ nói** — citation 4 hệ phái có agree/disagree

Output: dict structured để render UI hoặc compose LLM prompt.
Em CHƯA wire LLM call ở v2 vì test text-only trước.

Built 2026-06-10 Phase B.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.tu_vi.cross_school import (
    luan_sao_cung, luan_to_hop_cung, detect_paradigm_warnings, SCHOOL_NAMES
)
from engine.tu_vi.viet_names import vi_star, vi_chi, vi_can, vi_palace


def render_per_palace(palace: str, stars: list[str]) -> dict:
    """Render 1 cung với 14 chính tinh có thể có."""
    cross_views = {}
    for star in stars:
        cv = luan_sao_cung(star, palace, limit_per_school=3)
        cross_views[star] = cv
    return {
        "palace": palace,
        "stars": stars,
        "cross_views": cross_views,
    }


def render_3_layer(la_so: dict) -> dict:
    """Main entry — render 3-Layer cho cả lá số.

    Args:
        la_so: dict (xem schema trong cross_school.detect_paradigm_warnings)

    Returns:
        {
          "lop_1_chuyen_ve_anh": text (narrative tổng)
          "lop_2_vi_sao": text (paradigm explain)
          "lop_3_sach_co": dict (per palace cross-school)
          "warnings": list (paradigm warnings)
          "metadata": {...}
        }
    """
    # Paradigm warnings
    warnings = detect_paradigm_warnings(la_so)

    # Render per palace
    per_palace = {}
    for palace, stars in (la_so.get("chinh_tinh_per_palace") or {}).items():
        if stars:
            per_palace[palace] = render_per_palace(palace, stars)

    # Tổ hợp cung (việc D — tam phương tứ chính / giáp / mượn sao).
    # Chỉ tính cho key là 12 chi (key chức năng menh/tai_bach không có vị trí vòng).
    from engine.tu_vi.paradigm.to_hop_cung import CHI_RING
    ct = la_so.get("chinh_tinh_per_palace") or {}
    to_hop_per_palace = {}
    for chi in CHI_RING:
        if chi not in per_palace:
            continue
        try:
            to_hop_per_palace[chi] = luan_to_hop_cung(chi, ct)
        except Exception:
            continue  # tổ hợp là lớp bổ sung — lỗi không được chặn render chính

    # Compose lớp 1 (narrative tổng — simple template)
    bac_tuoi_w = next((w for w in warnings if w["type"] == "bac_tuoi"), None)
    nhan_cung_warnings = [w for w in warnings if w["type"] == "nhan_cung"]
    tam_hop_w = next((w for w in warnings if w["type"] == "tam_hop_loc"), None)
    ba_vong_w = next((w for w in warnings if w["type"] == "ba_vong"), None)

    lop_1 = f"""## Chuyện về anh

Anh sinh năm {vi_can(la_so['can'])} {vi_chi(la_so['chi'])} — {bac_tuoi_w['msg'] if bac_tuoi_w else ''}.

{tam_hop_w['msg'] if tam_hop_w else ''}

{ba_vong_w['msg'] if ba_vong_w else ''}
""".strip()

    # Compose lớp 2
    lop_2_parts = ["## Vì sao\n"]
    if nhan_cung_warnings:
        lop_2_parts.append(
            f"⚠ **Cảnh báo Nhân Cung** — Trần Đoàn dạy có {len(nhan_cung_warnings)} chính tinh trong lá số anh rơi vào 'đất thất vị':\n"
        )
        for w in nhan_cung_warnings:
            lop_2_parts.append(f"- **{vi_star(w['star'])}** ở **{vi_chi(w['palace'])}** — khả năng tốt giảm 80%")
    else:
        lop_2_parts.append("✓ Không có chính tinh nào rơi vào Nhân Cung.")
    lop_2 = "\n".join(lop_2_parts)

    # Compose lớp 3 (per palace cross-school + tổ hợp cung)
    lop_3 = {
        "per_palace": per_palace,
        "to_hop_per_palace": to_hop_per_palace,
        "schools_summary": {
            sc_code: SCHOOL_NAMES[sc_code]
            for sc_code in SCHOOL_NAMES
        }
    }

    return {
        "lop_1_chuyen_ve_anh": lop_1,
        "lop_2_vi_sao": lop_2,
        "lop_3_sach_co": lop_3,
        "warnings": warnings,
        "metadata": {
            "atoms_pulled": sum(
                v["cross_views"][s]["total_atoms"]
                for v in per_palace.values()
                for s in v["stars"]
            ),
            "to_hop_atoms": sum(v["total_atoms"] for v in to_hop_per_palace.values()),
            "schools_count": 4,
        }
    }


if __name__ == "__main__":
    import json

    # E2E test với lá số founder
    la_so_founder = {
        "can": "mau",
        "chi": "thin",
        "menh_palace": "ty",
        "than_palace": "than",
        "cuc": "thuy_nhi_cuc",
        "gender": "M",
        "chinh_tinh_per_palace": {
            "ty": ["thien_dong"],          # Cung Mệnh
            "than": ["vu_khuc"],            # Cung Thân
            "thin": ["tu_vi"],
            "hoi": ["thien_co"],
            "dau": ["thai_am"],
        }
    }

    out = render_3_layer(la_so_founder)
    print("===== OUTPUT FILLER V2 — FOUNDER TEST =====\n")
    print(out["lop_1_chuyen_ve_anh"])
    print()
    print(out["lop_2_vi_sao"])
    print()
    print(f"--- Metadata ---")
    print(f"Atoms pulled: {out['metadata']['atoms_pulled']}")
    print(f"Schools: {out['metadata']['schools_count']}")
    print()
    print(f"--- Per palace cross-school view ---")
    for p, data in out["lop_3_sach_co"]["per_palace"].items():
        for s, cv in data["cross_views"].items():
            print(f"  {s} × {p}: {cv['total_atoms']} atoms ({len(cv['schools_present'])} schools)")
            for sc, atoms in cv["schools"].items():
                if atoms:
                    sample = atoms[0]
                    quote = (sample["source_quote"] or "")[:80]
                    print(f"    [{sc}] {quote}...")
