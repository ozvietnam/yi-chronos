"""Gieo Duyên (H4 / lớp G) — hàm thuần xác định cho tính năng Tử Vi & Gieo Duyên.

Phục vụ spec `prvchat/.../2026-06-14-tuvi-gieoduyen-profile-matching-spec.md`:

- **G1** `profile_derived`     — nạp âm + cung mệnh Bát Trạch (cụm A)
- **G2** `compatible_years`    — tuổi (năm sinh) hợp với user (cụm B)
- **G3** `marriage_years`      — năm dương lịch tốt để kết hôn (cụm C)
- **G4** `compat_key`/`compat_batch` — chấm điểm so khớp hàng loạt theo compatKey (cụm D)

KHÔNG cần LLM, KHÔNG cần DB — tái dùng bảng đã verify của `engine/bat_tu`
(nạp âm, lục/tam hợp, lục xung/hại/hình, 5 hợp can, sinh-khắc ngũ hành).

Paradigm (Iron Rule #6/#8 — đọc đồng dạng, KHÔNG tiên tri): điểm số/sao là
**chỉ dấu cấu trúc tương hợp**, không phải phán "số phận". Mọi output mang
`paradigm_guard`; client diễn đạt lại giọng mặt tiền (Q1 — 2 chế độ).
"""
from __future__ import annotations

from .compatibility import (
    HOP_CAN,
    NAP_AM_MAP,
    NAP_AM_NAMES,
    _element_relation,
)
from .constants import (
    EARTHLY_BRANCHES,
    ELEMENT_CONTROLS,
    ELEMENT_GENERATES,
    HEAVENLY_STEMS,
    STEM_ELEMENT,
)
from .luu_nien import LUC_HAI, LUC_HOP, LUC_XUNG, TAM_HINH_GROUPS, TAM_HOP

PARADIGM_GUARD = (
    "Đọc đồng dạng, KHÔNG tiên tri (Iron Rule #6/#8). Con số/sao là chỉ dấu cấu "
    "trúc tương hợp giữa hai bên, không phải bản án số phận. Mệnh là động từ — "
    "tương hợp tốt nghĩa là 'dễ cùng vận hành', không phải 'chắc chắn hạnh phúc'."
)


# ─── Can-Chi từ năm ──────────────────────────────────────────────────────────

def year_to_can_chi(year: int) -> tuple[str, str, str]:
    """Năm dương → (Can, Chi, 'Can Chi'). Mốc: 1984 = Giáp Tý."""
    stem = HEAVENLY_STEMS[(year - 4) % 10]
    branch = EARTHLY_BRANCHES[(year - 4) % 12]
    return stem, branch, f"{stem} {branch}"


def nap_am_for_year(year: int) -> dict:
    """Nạp âm trụ Năm → {element, name, can_chi}."""
    stem, branch, cc = year_to_can_chi(year)
    return {
        "element": NAP_AM_MAP.get((stem, branch), "unknown"),
        "name": NAP_AM_NAMES.get((stem, branch), "Unknown"),
        "can_chi": cc,
    }


# ─── Cung mệnh Bát Trạch (cung phi) ──────────────────────────────────────────

# Số cung Lạc thư → (quái, hành, Đông/Tây tứ mệnh). Cung 5 được chuyển hướng.
_QUAI_BY_CUNG: dict[int, tuple[str, str, str]] = {
    1: ("Khảm", "thủy", "dong"),
    2: ("Khôn", "thổ", "tay"),
    3: ("Chấn", "mộc", "dong"),
    4: ("Tốn", "mộc", "dong"),
    6: ("Càn", "kim", "tay"),
    7: ("Đoài", "kim", "tay"),
    8: ("Cấn", "thổ", "tay"),
    9: ("Ly", "hỏa", "dong"),
}
_GROUP_LABEL = {"dong": "Đông Tứ Mệnh", "tay": "Tây Tứ Mệnh"}


def _digit_root(n: int) -> int:
    """Cộng dồn chữ số về 1 chữ số (1..9); 0 → 9."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n or 9


def _wrap_1_9(n: int) -> int:
    while n > 9:
        n -= 9
    while n < 1:
        n += 9
    return n


def cung_phi(year: int, gender: str) -> dict:
    """Cung mệnh Bát Trạch từ năm sinh + giới tính.

    Công thức cổ điển (Lạc thư), có nhánh thế kỷ:
      - Nam: TK20 `11 - s` · TK21 `9 - s`  → cung 5 = Khôn(2)
      - Nữ:  TK20 `s + 4`  · TK21 `s + 6`  → cung 5 = Cấn(8)
    với `s` = digit-root của năm. Đã kiểm: 1984/1990/2000 cả nam-nữ.
    """
    s = _digit_root(year)
    is_female = str(gender).strip().lower() in {"nữ", "nu", "female", "f"}
    if year >= 2000:
        cung = (s + 6) if is_female else (9 - s)
    else:
        cung = (s + 4) if is_female else (11 - s)
    cung = _wrap_1_9(cung)
    if cung == 5:
        cung = 8 if is_female else 2
    quai, element, group = _QUAI_BY_CUNG[cung]
    return {
        "cung_number": cung,
        "quai": quai,
        "element": element,
        "menh_group": group,
        "menh_group_label": _GROUP_LABEL[group],
        "label": f"{quai} ({_GROUP_LABEL[group]})",
    }


def profile_derived(year: int, gender: str) -> dict:
    """G1 — suy diễn hồ sơ tĩnh cụm A: nạp âm + cung mệnh Bát Trạch."""
    return {
        "nap_am": nap_am_for_year(year),
        "cung_menh": cung_phi(year, gender),
        "paradigm_guard": PARADIGM_GUARD,
    }


# ─── Chấm điểm quan hệ 2 chi + nạp âm (lõi dùng chung G2/G3/G4) ───────────────

def _branch_relations(b1: str, b2: str) -> list[dict]:
    """Quan hệ 2 địa chi → list {type, points, note}. Điểm + = hợp, - = xung."""
    pair = frozenset([b1, b2])
    out: list[dict] = []
    if pair in LUC_HOP:
        out.append({"type": "lục hợp", "points": 3,
                    "note": f"{b1}+{b2} lục hợp ({LUC_HOP[pair].title()})"})
    for el, group in TAM_HOP.items():
        if b1 in group and b2 in group and b1 != b2:
            out.append({"type": "tam hợp", "points": 2,
                        "note": f"{b1}+{b2} bán hợp {el.title()} cục"})
            break
    if pair in LUC_XUNG:
        out.append({"type": "lục xung", "points": -3, "note": f"{b1}⚔{b2} lục xung"})
    if pair in LUC_HAI:
        out.append({"type": "lục hại", "points": -2, "note": f"{b1}✗{b2} lục hại"})
    for group in TAM_HINH_GROUPS:
        if b1 in group and b2 in group and b1 != b2:
            out.append({"type": "tương hình", "points": -2, "note": f"{b1}⚖{b2} tương hình"})
            break
    if b1 == b2:
        out.append({"type": "đồng chi", "points": 1, "note": f"Cùng chi {b1} — đồng khí"})
    return out


def _nap_am_points(el_a: str, el_b: str) -> tuple[int, str]:
    """Điểm quan hệ nạp âm 2 bên."""
    rel = _element_relation(el_a, el_b)
    if rel["polarity"] == "lành":
        return 2, rel["narrative"]
    if rel["type"] == "tỷ hòa":
        return 1, rel["narrative"]
    if rel["polarity"] == "căng":
        return -1, rel["narrative"]
    return 0, rel["narrative"]


def _grade(score: int) -> str:
    if score >= 5:
        return "Rất hợp"
    if score >= 3:
        return "Hợp"
    if score >= 1:
        return "Hòa hợp"
    if score >= 0:
        return "Bình thường"
    return "Thử thách"


def _percent_stars(score: int) -> tuple[int, int]:
    """Map điểm thô → phần trăm (5..99) + sao (1..5) cho hiển thị mặt tiền."""
    percent = max(5, min(99, 50 + score * 8))
    stars = max(1, min(5, round(percent / 20)))
    return percent, stars


# ─── G2: tuổi hợp ────────────────────────────────────────────────────────────

def compatible_years(year: int, gender: str | None = None,
                     span: int = 10, top: int = 6) -> list[dict]:
    """Năm sinh (can-chi) hợp với user, trong dải ±span, xếp hạng giảm dần."""
    _, anchor_branch, _ = year_to_can_chi(year)
    anchor_na = nap_am_for_year(year)["element"]
    items: list[dict] = []
    for cand in range(year - span, year + span + 1):
        if cand == year:
            continue
        c_stem, c_branch, c_cc = year_to_can_chi(cand)
        rels = _branch_relations(anchor_branch, c_branch)
        score = sum(r["points"] for r in rels)
        na_pts, na_note = _nap_am_points(anchor_na, nap_am_for_year(cand)["element"])
        score += na_pts
        if score <= 0:
            continue
        notes = [r["note"] for r in rels if r["points"] > 0] or [na_note]
        items.append({
            "year": cand,
            "can_chi": c_cc,
            "age_gap": year - cand,
            "score": score,
            "grade": _grade(score),
            "reason": "; ".join(notes) + ".",
        })
    items.sort(key=lambda it: (it["score"], -abs(it["age_gap"])), reverse=True)
    return items[:top]


# ─── G3: tuổi kết hôn ────────────────────────────────────────────────────────

def marriage_years(birth_datetime_local: str, gender: str,
                   timezone: str = "Asia/Ho_Chi_Minh",
                   from_year: int | None = None, count: int = 3,
                   scan: int = 6) -> list[dict]:
    """Năm dương lịch tốt để kết hôn — quét lưu niên, tránh xung Thái Tuế.

    Chấm theo quan hệ chi năm lưu niên với (a) chi Cung Phối = chi trụ Ngày và
    (b) chi trụ Năm bản mệnh (Thái Tuế). Hàm thuần, không LLM.
    """
    from datetime import datetime as _dt

    from .tu_tru import extract_tu_tru

    tt = extract_tu_tru(birth_datetime_local, timezone)
    pillars = tt["pillars"]
    day_branch = pillars["day"]["branch"]
    year_branch = pillars["year"]["branch"]

    if from_year is None:
        try:
            from_year = _dt.fromisoformat(birth_datetime_local).year + 25
        except ValueError:
            from_year = 2026

    items: list[dict] = []
    for cand in range(from_year, from_year + scan):
        _, ln_branch, ln_cc = year_to_can_chi(cand)
        notes: list[str] = []
        score = 0
        # Cung Phối (chi ngày)
        for r in _branch_relations(day_branch, ln_branch):
            score += r["points"]
            if r["points"] > 0:
                notes.append(f"Cung Phối {r['note']}")
            elif r["type"] == "lục xung":
                notes.append(f"Cung Phối {r['note']} (biến động)")
        # Tránh xung Thái Tuế (chi năm bản mệnh)
        if frozenset([year_branch, ln_branch]) in LUC_XUNG:
            score -= 3
            notes.append(f"Xung Thái Tuế ({year_branch}⚔{ln_branch}) — nên tránh")
        elif frozenset([year_branch, ln_branch]) in LUC_HOP:
            score += 2
            notes.append(f"Hợp Thái Tuế ({year_branch}+{ln_branch})")
        items.append({
            "year": cand,
            "can_chi": ln_cc,
            "score": score,
            "grade": _grade(score),
            "reason": ("; ".join(notes) + "." if notes
                       else "Năm trung hòa, không xung không hợp nổi bật."),
        })
    # Chọn năm tốt nhất; ổn định thứ tự theo điểm rồi theo năm gần trước.
    items.sort(key=lambda it: (it["score"], -it["year"]), reverse=True)
    chosen = [it for it in items if it["score"] > 0][:count]
    if not chosen:                      # không năm nào dương → trả năm đỡ xung nhất
        chosen = items[:1]
    return chosen


# ─── G4: compatKey + compat-batch ────────────────────────────────────────────

def compat_key(year: int, day_master: str | None = None) -> dict:
    """Khóa chấm điểm rẻ cho 1 người (lưu sẵn vào datingProfiles).

    Tối thiểu = can-chi năm + nạp âm; tùy chọn nhật chủ (Day Master) để chấm
    sâu hơn (5 hợp can / sinh-khắc). KHÔNG cần giờ sinh.
    """
    stem, branch, cc = year_to_can_chi(year)
    key = {
        "year": year,
        "year_can_chi": cc,
        "year_branch": branch,
        "nap_am_element": nap_am_for_year(year)["element"],
    }
    if day_master:
        key["day_master"] = day_master
    return key


def _pair_score(a: dict, b: dict) -> tuple[int, list[str]]:
    """Điểm + highlight giữa 2 compatKey."""
    notes: list[str] = []
    score = 0
    rels = _branch_relations(a["year_branch"], b["year_branch"])
    score += sum(r["points"] for r in rels)
    notes += [r["note"] for r in rels if r["points"] > 0]
    na_pts, na_note = _nap_am_points(a["nap_am_element"], b["nap_am_element"])
    score += na_pts
    if na_pts > 0:
        notes.append(na_note)
    # Nhật chủ (nếu cả 2 có)
    dm_a, dm_b = a.get("day_master"), b.get("day_master")
    if dm_a and dm_b:
        if frozenset([dm_a, dm_b]) in HOP_CAN:
            score += 3
            notes.append(f"Nhật chủ {dm_a}+{dm_b} hợp can (tâm hợp ý)")
        else:
            ea, eb = STEM_ELEMENT.get(dm_a), STEM_ELEMENT.get(dm_b)
            if ea and eb:
                if ELEMENT_GENERATES.get(ea) == eb or ELEMENT_GENERATES.get(eb) == ea:
                    score += 1
                    notes.append(f"Nhật chủ tương sinh ({ea.title()}–{eb.title()})")
                elif ELEMENT_CONTROLS.get(ea) == eb or ELEMENT_CONTROLS.get(eb) == ea:
                    score -= 1
    return score, notes


def compat_batch(anchor: dict, candidates: list[dict]) -> list[dict]:
    """G4 — chấm 1 anchor với N ứng viên trong 1 lời gọi (cụm D).

    Mỗi candidate là compat_key(...) kèm `id`. Trả list xếp hạng giảm dần với
    percent + sao + highlight cho card gợi ý bạn đời.
    """
    out: list[dict] = []
    for cand in candidates:
        score, notes = _pair_score(anchor, cand)
        percent, stars = _percent_stars(score)
        out.append({
            "id": cand.get("id"),
            "score": score,
            "percent": percent,
            "stars": stars,
            "grade": _grade(score),
            "highlight": ("; ".join(notes) + "." if notes
                          else "Cấu trúc khí hai bên độc lập, không nổi bật."),
        })
    out.sort(key=lambda r: r["score"], reverse=True)
    return out
