"""Lục Thân (六親) — family relations analysis from Bát Tự chart.

Lục Thân = 6 quan hệ thân thuộc: Cha + Mẹ + Anh chị em + Vợ/Chồng + Con cái.
Phân tích qua Thập Thần + vị trí trụ + cường độ.

Paradigm (Iron Rule #4+6): KHÔNG dự đoán "anh sẽ mất cha năm X". Đọc cấu trúc
khí liên quan đến Lục Thân → mô tả quan hệ + ảnh hưởng hai chiều.

Lục Thân map (cổ điển Tử Bình):

| Quan hệ | Nam | Nữ |
|---|---|---|
| Cha | Thiên Tài | Thiên Tài |
| Mẹ | Chính Ấn | Chính Ấn |
| Anh chị em | Tỷ Kiên + Kiếp Tài | Tỷ Kiên + Kiếp Tài |
| Vợ chính | Chính Tài | — |
| Vợ lẽ / tình cảm thứ | Thiên Tài | — |
| Chồng | — | Chính Quan |
| Tình cảm mạnh / kẻ cường | — | Thất Sát |
| Con trai | Thất Sát | Thực Thần |
| Con gái | Chính Quan | Thương Quan |

Vị trí trụ (cổ điển):
- Trụ Năm: tổ tiên + cha mẹ (sơ ấu)
- Trụ Tháng: cha mẹ (chính) + anh chị em
- Trụ Ngày: bản thân + vợ/chồng (chi)
- Trụ Giờ: con cái

Algorithm:
1. Identify Thập Thần positions cho mỗi Lục Thân category
2. Strength + Vị trí + interactions
3. Specific patterns: Cha mất sớm, Mẹ quý hiển, ...
4. Quan hệ + ảnh hưởng narrative
"""

from __future__ import annotations

from .constants import PILLAR_DOMAIN
from .thap_than import thap_than_of


# ─── Lục Thân mapping (gender-aware) ────────────────────────────────────────

LUC_THAN_MAP_NAM: dict[str, list[str]] = {
    "Cha": ["Thiên Tài"],
    "Mẹ": ["Chính Ấn"],
    "Anh chị em": ["Tỷ Kiên", "Kiếp Tài"],
    "Vợ chính": ["Chính Tài"],
    "Vợ lẽ / tình cảm phụ": ["Thiên Tài"],
    "Con trai": ["Thất Sát"],
    "Con gái": ["Chính Quan"],
}

LUC_THAN_MAP_NU: dict[str, list[str]] = {
    "Cha": ["Thiên Tài"],
    "Mẹ": ["Chính Ấn"],
    "Anh chị em": ["Tỷ Kiên", "Kiếp Tài"],
    "Chồng": ["Chính Quan"],
    "Tình cảm phụ / kẻ cường": ["Thất Sát"],
    "Con trai": ["Thực Thần"],
    "Con gái": ["Thương Quan"],
}

# Vị trí trụ (theo cổ điển)
PILLAR_RELATIONS: dict[str, dict] = {
    "year": {
        "label": "Trụ Năm",
        "represents": ["tổ tiên", "cha mẹ (sơ ấu)", "vận 0-15 tuổi"],
    },
    "month": {
        "label": "Trụ Tháng",
        "represents": ["cha mẹ (chính)", "anh chị em", "vận 16-30 tuổi"],
    },
    "day": {
        "label": "Trụ Ngày",
        "represents": ["bản thân (can)", "vợ/chồng (chi)", "vận 31-45 tuổi"],
    },
    "hour": {
        "label": "Trụ Giờ",
        "represents": ["con cái", "hậu vận 46+ tuổi"],
    },
}


# Tính chất từng Lục Thân (when Thập Thần is present + strong)
LUC_THAN_TRAITS: dict[str, dict] = {
    "Cha": {
        "strong": "Cha là Tài tinh — bố vững vàng, có tài chính, ảnh hưởng tích cực. "
                  "Khi Thiên Tài vượng + ở Trụ Năm: cha bản thân có khí lực mạnh.",
        "weak": "Thiên Tài nhược / vắng: ít gắn kết cha hoặc cha không ảnh hưởng lớn. "
                "Cha có thể mất sớm, đi xa, hoặc tình cảm nhạt.",
        "afflicted": "Thiên Tài bị khắc (vd Tỷ/Kiếp đoạt) → cha gặp khó khăn, sức khỏe, tài chính.",
    },
    "Mẹ": {
        "strong": "Mẹ là Chính Ấn — mẹ nuôi dưỡng, học vấn từ mẹ, gắn kết tinh thần. "
                  "Ấn vượng + ở Trụ Tháng: mẹ đóng vai trò chính dìu dắt.",
        "weak": "Chính Ấn nhược / vắng: ít sinh khí từ mẹ, hoặc mẹ ít ảnh hưởng. "
                "Có thể mẹ mất sớm, đi xa, hoặc tinh thần xa cách.",
        "afflicted": "Chính Ấn bị Tài đoạt (Chính Tài khắc Chính Ấn) → "
                     "Tài → Ấn xung đột: vợ ↔ mẹ khó hòa, hoặc tiền tài làm xa mẹ.",
    },
    "Anh chị em": {
        "strong": "Tỷ Kiên / Kiếp Tài là anh chị em — có người đồng hành cùng vai. "
                  "Nhiều Tỷ Kiếp: gia đình đông anh chị em, đối tác bạn bè nhiều.",
        "weak": "Tỷ Kiếp ít / vắng: ít anh chị em hoặc ít gắn kết. Cô độc hơn.",
        "afflicted": "Kiếp Tài quá mạnh: anh chị em tranh tài, đoạt vợ/chồng, cướp đoạt.",
    },
    "Vợ chính": {
        "strong": "Chính Tài là vợ chính — vợ ổn định, biết chăm nom tài chính. "
                  "Chính Tài ở Trụ Ngày chi: vợ hợp tính nết bản thân.",
        "weak": "Chính Tài nhược: hôn nhân muộn, hoặc vợ ít có sức ảnh hưởng. "
                "Day Master nhược + Tài vượng: không gánh nổi → vợ áp đảo.",
        "afflicted": "Chính Tài bị Kiếp Tài đoạt: vợ bị kẻ khác cướp, hoặc hôn nhân đổ vỡ.",
    },
    "Vợ lẽ / tình cảm phụ": {
        "strong": "Thiên Tài là tình cảm phụ + đào hoa — có sức hút phụ nữ.",
        "weak": "Thiên Tài nhược: ít tình cảm bên ngoài, hoặc đào hoa nhẹ.",
        "afflicted": "Thiên Tài + Kiếp Tài: tình cảm phụ vướng bí mật, scandal.",
    },
    "Chồng": {
        "strong": "Chính Quan là chồng — chồng chính danh, có chức tước, đáng tin. "
                  "Chính Quan ở Trụ Ngày chi: chồng hợp tính nết, gắn kết.",
        "weak": "Chính Quan nhược: hôn nhân muộn, hoặc chồng ít có sức ảnh hưởng.",
        "afflicted": "Chính Quan + Thương Quan: 'Thương Quan kiến Quan' → khắc chồng, "
                     "hôn nhân biến động, ly hôn nguy cơ.",
    },
    "Tình cảm phụ / kẻ cường": {
        "strong": "Thất Sát mạnh: dễ vướng đối tượng cường, áp lực, hấp dẫn nguy hiểm.",
        "weak": "Thất Sát yếu: tình cảm phụ ít. Nếu thân vượng, Sát cũng không ảnh hưởng nhiều.",
        "afflicted": "Thất Sát quá mạnh + không có chế hóa: kẻ áp đảo, mối nguy hiểm.",
    },
    "Con trai": {
        "strong": "Con trai ở vị trí Thực Thần (Nữ) / Thất Sát (Nam) tại Trụ Giờ. "
                  "Nếu mạnh: con trai có tài + sức.",
        "weak": "Vắng mặt / yếu: ít con trai, hoặc xa cách.",
        "afflicted": "Bị khắc / hỗn tạp: con trai gặp khó khăn, hoặc quan hệ xa cách.",
    },
    "Con gái": {
        "strong": "Con gái ở vị trí Thương Quan (Nữ) / Chính Quan (Nam). "
                  "Nếu mạnh: con gái thông minh, có tài năng.",
        "weak": "Vắng mặt / yếu: ít con gái, hoặc xa cách.",
        "afflicted": "Bị khắc: con gái gặp khó khăn về sức khỏe / hôn nhân.",
    },
}


# ─── Helpers ────────────────────────────────────────────────────────────────


def _find_thap_than_positions(pillars: dict, day_master: str,
                                 target_thap_than: list[str]) -> list[dict]:
    """Tìm tất cả positions của 1 (hoặc nhiều) Thập Thần loại."""
    out = []
    for pos in ("year", "month", "day", "hour"):
        p = pillars[pos]
        # Visible stem (skip day's own stem)
        if pos != "day":
            stem_tt = thap_than_of(day_master, p["stem"])
            if stem_tt in target_thap_than:
                out.append({
                    "pillar": pos,
                    "pillar_vi": p.get("position_vi"),
                    "type": "visible_stem",
                    "stem": p["stem"],
                    "thap_than": stem_tt,
                })
        # Hidden stems
        for hs in p["hidden_stems"]:
            if hs == day_master and pos == "day":
                continue
            tt = thap_than_of(day_master, hs)
            if tt in target_thap_than:
                out.append({
                    "pillar": pos,
                    "pillar_vi": p.get("position_vi"),
                    "type": "hidden_stem",
                    "stem": hs,
                    "branch": p["branch"],
                    "thap_than": tt,
                })
    return out


def _assess_luc_than_strength(positions: list[dict],
                                 thap_than_dist: dict,
                                 target_thap_than: list[str]) -> str:
    """Assess strength: strong / weak / afflicted / absent."""
    if not positions:
        return "absent"
    visible = thap_than_dist.get("visible", {})
    hidden = thap_than_dist.get("hidden", {})
    total_count = sum(visible.get(tt, 0) + hidden.get(tt, 0) for tt in target_thap_than)
    visible_count = sum(visible.get(tt, 0) for tt in target_thap_than)
    if visible_count >= 1 and total_count >= 2:
        return "strong"
    elif total_count >= 1:
        return "moderate"
    return "weak"


def _detect_afflictions(luc_than_name: str, thap_than_dist: dict,
                          dm_tag: str) -> list[str]:
    """Detect specific afflictions cho 1 quan hệ."""
    visible = thap_than_dist.get("visible", {})
    hidden = thap_than_dist.get("hidden", {})
    has = lambda tt: visible.get(tt, 0) + hidden.get(tt, 0) > 0
    out = []
    # "Mẹ" Chính Ấn bị Chính Tài đoạt
    if luc_than_name == "Mẹ" and has("Chính Ấn") and has("Chính Tài"):
        out.append("Chính Tài đoạt Chính Ấn → Tài ↔ Ấn xung đột: vợ-mẹ khó hòa.")
    # "Vợ chính" / "Chồng" bị khắc
    if luc_than_name == "Vợ chính" and has("Chính Tài") and has("Kiếp Tài"):
        out.append("Kiếp Tài đoạt Chính Tài → vợ bị cản trở / hôn nhân biến động.")
    if luc_than_name == "Chồng" and has("Chính Quan") and has("Thương Quan"):
        out.append("Thương Quan kiến Chính Quan → khắc chồng (Nữ), nhất là khi Day Master nhược.")
    # Sát quá mạnh
    if luc_than_name == "Tình cảm phụ / kẻ cường":
        sat_count = visible.get("Thất Sát", 0) + hidden.get("Thất Sát", 0)
        if sat_count >= 2 and not has("Thực Thần") and not has("Chính Ấn") and not has("Thiên Ấn"):
            out.append("Thất Sát mạnh + không có chế hóa: cần đề phòng quan hệ nguy hiểm.")
    return out


def _analyze_one_relation(name: str, target_thap_than: list[str],
                            pillars: dict, day_master: str,
                            thap_than_dist: dict, dm_tag: str) -> dict:
    """Phân tích 1 quan hệ Lục Thân."""
    positions = _find_thap_than_positions(pillars, day_master, target_thap_than)
    strength = _assess_luc_than_strength(positions, thap_than_dist, target_thap_than)
    afflictions = _detect_afflictions(name, thap_than_dist, dm_tag)
    traits = LUC_THAN_TRAITS.get(name, {})

    # Compose narrative
    if strength == "absent":
        narrative = (
            f"**{name}** ({', '.join(target_thap_than)}): VẮNG MẶT trong lá số. "
            f"{traits.get('weak', '')}"
        )
    elif strength == "strong":
        narrative = (
            f"**{name}** ({', '.join(target_thap_than)}): MẠNH ({len(positions)} vị trí). "
            f"{traits.get('strong', '')}"
        )
    elif strength == "moderate":
        narrative = (
            f"**{name}** ({', '.join(target_thap_than)}): TRUNG BÌNH "
            f"({len(positions)} vị trí, đa số ẩn). {traits.get('strong', '')[:100]}..."
        )
    else:
        narrative = (
            f"**{name}** ({', '.join(target_thap_than)}): YẾU. {traits.get('weak', '')}"
        )
    if afflictions:
        narrative += f" Cảnh báo: {' | '.join(afflictions)}"

    return {
        "name": name,
        "target_thap_than": target_thap_than,
        "positions": positions,
        "strength": strength,
        "afflictions": afflictions,
        "narrative": narrative,
    }


# ─── Public API ─────────────────────────────────────────────────────────────


METHOD_ID = "bat_tu_luc_than_v1"
SOURCE_REF = "Thiệu Vĩ Hoa Q. 5-6 + Tử Bình Chân Thuyên về Lục Thân."


def analyze_luc_than(bat_tu_state: dict) -> dict:
    """Phân tích Lục Thân chi tiết: Cha + Mẹ + Anh chị em + Vợ/Chồng + Con cái.

    Args:
        bat_tu_state: Output of `cast_bat_tu(...)`.

    Returns:
        Dict structured by relation.
    """
    if "tu_tru" not in bat_tu_state:
        raise ValueError("bat_tu_state must contain 'tu_tru' key")

    gender = bat_tu_state.get("gender", "nam")
    pillars = bat_tu_state["tu_tru"]["pillars"]
    day_master = bat_tu_state["tu_tru"]["day_master"]["stem"]
    thap_than_dist = bat_tu_state.get("thap_than_distribution", {})
    dm_tag = bat_tu_state["ngu_hanh"]["day_master_assessment"]["strength_tag"]

    luc_than_map = LUC_THAN_MAP_NAM if gender == "nam" else LUC_THAN_MAP_NU

    relations = []
    for name, target_tt in luc_than_map.items():
        relations.append(_analyze_one_relation(
            name, target_tt, pillars, day_master, thap_than_dist, dm_tag
        ))

    # Pillar overview
    pillar_overview = []
    for pos, info in PILLAR_RELATIONS.items():
        p = pillars[pos]
        pillar_overview.append({
            "pillar": pos,
            "label": info["label"],
            "stem": p["stem"],
            "branch": p["branch"],
            "represents": info["represents"],
        })

    return {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "paradigm_guard": (
            "Lục Thân KHÔNG dự đoán \"anh sẽ mất X năm Y\". "
            "Đọc cấu trúc khí Thập Thần liên quan → mô tả quan hệ + xu hướng ảnh hưởng. "
            "Quan hệ là dòng chảy động — phụ thuộc thực hành có ý thức của cả 2 bên."
        ),
        "gender": gender,
        "pillar_overview": pillar_overview,
        "relations": relations,
        "closing": (
            "Lục Thân (6 thân) cho thấy cấu trúc gia đình tiềm ẩn. "
            "Nhưng chất lượng quan hệ phụ thuộc CHÚ TÂM + CHĂM SÓC + GIAO TIẾP có ý thức. "
            "Bát Tự chỉ cho bản đồ — đi đường là do mình."
        ),
    }
