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


def render_per_palace(palace: str, stars: list[str],
                      phu_tinh: list[str] | None = None,
                      chi: str | None = None, gender: str | None = None,
                      same_stars: set | None = None,
                      tu_chinh_stars: set | None = None) -> dict:
    """Render 1 cung: chính tinh (3 atoms/hệ phái) + phụ tinh/Tứ Hóa (2 atoms/hệ phái).

    chi = vị trí địa chi thật của cung → đối chiếu miếu-hãm (Việc 2).
    gender = giới user → lọc atom khác giới (precision 2026-06-13).
    same_stars/tu_chinh_stars = sao đồng cung / hội chiếu → lọc atom combo (lỗ #6).
    """
    cross_views = {}
    for star in stars:
        cv = luan_sao_cung(star, palace, limit_per_school=3, chi=chi, gender=gender,
                           same_stars=same_stars, tu_chinh_stars=tu_chinh_stars)
        cross_views[star] = cv
    phu_views = {}
    for star in (phu_tinh or []):
        cv = luan_sao_cung(star, palace, limit_per_school=2, chi=chi, gender=gender,
                           same_stars=same_stars, tu_chinh_stars=tu_chinh_stars)
        if cv["total_atoms"]:
            phu_views[star] = cv
    return {
        "palace": palace,
        "stars": stars,
        "phu_tinh": list(phu_views.keys()),
        "cross_views": cross_views,
        "phu_tinh_views": phu_views,
    }


# Việc 2 — lọc điều kiện miếu-hãm: sách nói "nhập miếu thì X / hãm thì Y",
# phải đối chiếu trạng thái sao THẬT của lá số. KHÔNG xóa atom (giữ đủ 2 vế
# bám sách) — chỉ annotate khớp/lệch + đẩy atom lệch điều kiện xuống cuối.
_MIEU_WORDS = ("nhập miếu", "miếu địa", "miếu vượng", "tại miếu", "đắc địa", "vượng địa")
_HAM_WORDS = ("hãm địa", "lạc hãm", "bị hãm", "cư hãm", "gặp hãm")
_GOOD_LEVELS = ("miếu", "vượng", "đắc")
_BAD_LEVELS = ("hãm", "lạc")


def _build_star_levels(chinh_tinh_per_palace: dict) -> dict[str, dict]:
    """Map sao → {level, palace_chi} từ vị trí chi thật (bảng chỉ phủ 14 chính tinh)."""
    from engine.tu_vi.mieu_vuong_ham import level_at
    from engine.tu_vi.viet_names import vi_star, vi_chi
    from engine.tu_vi.paradigm.to_hop_cung import CHI_RING

    chi_set = set(CHI_RING)
    out: dict[str, dict] = {}
    for chi, stars in (chinh_tinh_per_palace or {}).items():
        if chi not in chi_set:
            continue
        for s in stars:
            lv = level_at(vi_star(s), vi_chi(chi))
            if lv:
                out[s] = {"level": lv, "palace_chi": chi}
    return out


def _annotate_mieu_ham(per_palace: dict, star_levels: dict) -> int:
    """Gắn cờ điều kiện miếu-hãm vào atoms. Returns số atom LỆCH điều kiện."""
    lech = 0
    for v in per_palace.values():
        for star, cv in (v.get("cross_views") or {}).items():
            info = star_levels.get(star)
            if not info:
                continue
            lv = info["level"]
            cv["mieu_ham"] = lv
            is_good = any(g in lv for g in _GOOD_LEVELS)
            is_bad = any(b in lv for b in _BAD_LEVELS)
            if not (is_good or is_bad):
                continue  # bình — không đủ căn cứ phán khớp/lệch
            for atoms in (cv.get("schools") or {}).values():
                for a in atoms:
                    text = f"{a.get('question_text', '')} {a.get('source_quote', '')}".lower()
                    cond = ("mieu" if any(w in text for w in _MIEU_WORDS)
                            else "ham" if any(w in text for w in _HAM_WORDS) else None)
                    if cond is None:
                        continue
                    khop = (cond == "mieu") == is_good
                    a["dieu_kien"] = cond
                    a["dieu_kien_khop"] = khop
                    if not khop:
                        lech += 1
                        a["dieu_kien_note"] = (
                            f"Sách nói điều kiện {'nhập miếu/đắc' if cond == 'mieu' else 'hãm địa'} "
                            f"— sao trong lá số này đang {lv}"
                        )
                atoms.sort(key=lambda a: a.get("dieu_kien_khop") is False)
    return lech


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

    # Render per palace (chính tinh + phụ tinh/sát tinh/Tứ Hóa cùng cung)
    # fn_to_chi: cung chức năng → chi thật, để đối chiếu miếu-hãm
    from engine.tu_vi.paradigm.to_hop_cung import CHI_RING as _CHI_RING
    fn_to_chi = la_so.get("fn_to_chi") or {}
    phu_map = la_so.get("phu_tinh_per_palace") or {}

    def _chi_of(palace: str) -> str | None:
        return palace if palace in _CHI_RING else fn_to_chi.get(palace)

    # Sao đồng cung + hội chiếu của mỗi chi → lọc atom combo (lỗ #6)
    from engine.tu_vi.paradigm.to_hop_cung import to_hop_cung as _to_hop
    ct_chi = {k: v for k, v in (la_so.get("chinh_tinh_per_palace") or {}).items() if k in _CHI_RING}
    for k, v in (phu_map or {}).items():
        if k in _CHI_RING:
            ct_chi.setdefault(k, [])
            ct_chi[k] = list(ct_chi[k]) + list(v)

    def _star_sets(palace: str):
        chi = _chi_of(palace)
        if not chi:
            return None, None
        same = set(ct_chi.get(chi) or [])
        try:
            tc = set(_to_hop(chi, ct_chi)["hoi_chieu_stars"])
        except Exception:
            tc = same
        return same, tc

    gender = la_so.get("gender")  # "M" | "F"
    per_palace = {}
    for palace, stars in (la_so.get("chinh_tinh_per_palace") or {}).items():
        if stars:
            same, tc = _star_sets(palace)
            per_palace[palace] = render_per_palace(
                palace, stars, phu_map.get(palace), chi=_chi_of(palace), gender=gender,
                same_stars=same, tu_chinh_stars=tc)
    # Cung chỉ có phụ tinh (vô chính diệu) vẫn render phần phụ tinh
    for palace, pstars in phu_map.items():
        if palace not in per_palace and pstars:
            same, tc = _star_sets(palace)
            per_palace[palace] = render_per_palace(
                palace, [], pstars, chi=_chi_of(palace), gender=gender,
                same_stars=same, tu_chinh_stars=tc)

    # Việc 2 — đối chiếu miếu-hãm: annotate atoms khớp/lệch điều kiện
    star_levels = _build_star_levels(la_so.get("chinh_tinh_per_palace") or {})
    lech_count = _annotate_mieu_ham(per_palace, star_levels)

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

    # Việc 3 — đại vận hiện tại (BIẾN): cung vận = "Mệnh của 10 năm" → pull atoms
    # sao tọa cung vận luận như Mệnh + đối chiếu miếu-hãm tại cung vận.
    # Phú Thái Vi: "Cẩu hoặc bất sát kỳ cơ, cánh vong kỳ biến, tắc số chi tạo hóa viễn hĩ."
    dai_van_view = None
    dv = la_so.get("dai_van_hien_tai")
    if dv:
        from engine.tu_vi.mieu_vuong_ham import level_at
        from engine.tu_vi.viet_names import vi_star as _vs, vi_chi as _vc
        from engine.tu_vi.paradigm.to_hop_cung import muon_sao as _muon_sao
        # Cung vận vô chính diệu → mượn sao đối cung (phép tá tinh, việc B)
        van_stars = list(dv.get("stars") or [])
        muon_info = None
        if not van_stars:
            m = _muon_sao(dv["chi"], la_so.get("chinh_tinh_per_palace") or {})
            if m["vo_chinh_dieu"] and m["stars"]:
                van_stars = m["stars"]
                muon_info = m
        dv = {**dv, "stars": van_stars, "muon_sao": muon_info}
        van_views = {}
        for star in van_stars:
            cv = luan_sao_cung(star, "menh", limit_per_school=2)
            if cv["total_atoms"]:
                lv = level_at(_vs(star), _vc(dv["chi"]))
                if lv:
                    cv["mieu_ham"] = lv
                van_views[star] = cv
        dai_van_view = {
            **dv,
            "cross_views": van_views,
            "total_atoms": sum(cv["total_atoms"] for cv in van_views.values()),
            "vo_chinh_dieu": muon_info is not None,
            "citation": ("Phú Thái Vi: 'quên biến hóa thì tạo hóa của số vuột mất' — "
                         "cung đại vận luận như Mệnh tạm trong 10 năm; "
                         "'Chư tinh cát phùng hung dã cát, chư tinh hung phùng cát dã hung'"),
        }

    # Cách cục CÓ TÊN RIÊNG (truy quét thuật ngữ 2026-06-11) — match rule chính xác
    cach_cuc_named = []
    try:
        from engine.tu_vi.cach_cuc_named import match_named_cach_cucs, atoms_for_cach_cuc
        for cc in match_named_cach_cucs(la_so):
            atoms = atoms_for_cach_cuc(cc["slug"], cc["aliases"])
            cach_cuc_named.append({
                "slug": cc["slug"], "ten": cc["ten"], "loai": cc["loai"],
                "dieu_kien": cc["dieu_kien"], "aliases": cc["aliases"],
                **atoms,
            })
    except Exception:
        pass  # lớp bổ sung — không chặn render chính

    # Bộ phụ tinh + THẾ (đồng/giáp/hội/xung chiếu) cho 12 cung — Anh chốt 2026-06-13
    bo_phu_tinh_per_palace = {}
    try:
        from engine.tu_vi.bo_phu_tinh import luan_bo_phu_tinh, build_all_stars, atoms_for_bo, BO_PHU_TINH
        _all_stars = build_all_stars(la_so)
        _bo_map = {b[0]: (b[1], b[2]) for b in BO_PHU_TINH}
        menh_chi = la_so.get("menh_palace")
        for chi in _CHI_RING:
            bos = luan_bo_phu_tinh(chi, _all_stars)
            if not bos:
                continue
            # Pull atoms cho cung Mệnh (để feed narrative + hiển thị sâu)
            if chi == menh_chi:
                for bo in bos[:5]:
                    a, b = _bo_map[bo["slug"]]
                    bo.update(atoms_for_bo(a, b))
            bo_phu_tinh_per_palace[chi] = bos
    except Exception:
        pass

    # Compose lớp 3 (per palace cross-school + tổ hợp cung)
    lop_3 = {
        "per_palace": per_palace,
        "to_hop_per_palace": to_hop_per_palace,
        "cach_cuc_named": cach_cuc_named,
        "bo_phu_tinh_per_palace": bo_phu_tinh_per_palace,
        "dai_van_hien_tai": dai_van_view,
        "schools_summary": {
            sc_code: SCHOOL_NAMES[sc_code]
            for sc_code in SCHOOL_NAMES
        }
    }

    return {
        "lop_1_chuyen_ve_anh": lop_1,
        "lop_2_vi_sao": lop_2,
        "lop_3_sach_co": lop_3,
        "star_levels": star_levels,
        "warnings": warnings,
        "metadata": {
            "atoms_pulled": sum(
                v["cross_views"][s]["total_atoms"]
                for v in per_palace.values()
                for s in v["stars"]
            ),
            "to_hop_atoms": sum(v["total_atoms"] for v in to_hop_per_palace.values()),
            "dieu_kien_lech_atoms": lech_count,
            "phu_tinh_atoms": sum(
                cv["total_atoms"]
                for v in per_palace.values()
                for cv in v.get("phu_tinh_views", {}).values()
            ),
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
