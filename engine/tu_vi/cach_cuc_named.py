"""Cách cục CÓ TÊN RIÊNG — match rule-based + pull atoms theo tag cach_cuc.

Từ truy quét thuật ngữ 2026-06-11 (Anh duyệt): 38 cách cục có tên trong sách
(Phiếm thủy đào hoa, Thạch trung ẩn ngọc, Hỏa Tham, Lộc Mã giao trì...).
- 18 cách có match_rule rõ → máy tự phát hiện trong lá số
- Còn lại match_rule=null → chỉ tra atoms khi user search (điều kiện cần
  sao vòng phụ chưa truyền, hoặc đa phái định nghĩa lệch nhau)

Khác cach_cuc_dict (545 cách match mờ theo overlap sao): lớp này match
CHÍNH XÁC điều kiện sao × chi × tứ hóa.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# Volume mount /opt/yi-chronos/data shadows data/ trong container → fallback
# embedded_data/ (Dockerfile COPY data/tu_vi/ → embedded_data/tu_vi/)
_CANDIDATES = [
    PROJECT_ROOT / "data" / "tu_vi" / "cach_cuc_named.json",
    PROJECT_ROOT / "embedded_data" / "tu_vi" / "cach_cuc_named.json",
]
DATA_PATH = next((p for p in _CANDIDATES if p.exists()), _CANDIDATES[0])
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"

CHI_RING = ["ty", "suu", "dan", "mao", "thin", "ti",
            "ngo", "mui", "than", "dau", "tuat", "hoi"]

_DATA: list[dict] | None = None


def load_named_cach_cucs() -> list[dict]:
    global _DATA
    if _DATA is None:
        _DATA = json.loads(DATA_PATH.read_text())["cach_cucs"]
    return _DATA


def _star_chis(star: str, all_stars: dict[str, list[str]]) -> list[str]:
    """Các chi mà sao đang tọa (all_stars: chi → list sao, CHỈ key 12 chi)."""
    return [chi for chi in CHI_RING if star in (all_stars.get(chi) or [])]


def _eval_condition(cond: dict, ctx: dict) -> bool:
    """ctx: {all_stars: {chi: [sao]}, menh_chi, tu_hoa: [{hoa, star}], hoa_chis: {hoa: chi}}"""
    t = cond["type"]
    all_stars = ctx["all_stars"]

    if t == "star_at_chi":
        return bool(set(_star_chis(cond["star"], all_stars)) & set(cond["chi_in"]))

    if t == "same_palace":
        sets = [set(_star_chis(s, all_stars)) for s in cond["stars"]]
        if any(not s for s in sets):
            return False
        common = set.intersection(*sets)
        return bool(common)

    if t == "same_palace_any":
        base_chis = set(_star_chis(cond["star"], all_stars))
        if not base_chis:
            return False
        for other in cond["any_of"]:
            if base_chis & set(_star_chis(other, all_stars)):
                return True
        return False

    if t == "same_or_opposite":
        a, b = cond["stars"]
        ca = set(_star_chis(a, all_stars))
        cb = set(_star_chis(b, all_stars))
        if not ca or not cb:
            return False
        if ca & cb:
            return True
        opposite_of_a = {CHI_RING[(CHI_RING.index(c) + 6) % 12] for c in ca}
        return bool(opposite_of_a & cb)

    if t == "menh_has":
        menh = ctx.get("menh_chi")
        return menh is not None and cond["star"] in (all_stars.get(menh) or [])

    if t == "menh_chi_in":
        return ctx.get("menh_chi") in cond["chi_in"]

    if t == "hoa_any":
        for th in ctx.get("tu_hoa") or []:
            if th.get("star") == cond["star"] and th.get("hoa") in cond["hoa_in"]:
                return True
        return False

    if t == "tuan_triet_at_chi":
        # Tuần hoặc Triệt án ngữ tại 1 trong các chi
        tt = set(ctx.get("tuan_chi") or []) | set(ctx.get("triet_chi") or [])
        return bool(tt & set(cond["chi_in"]))

    if t == "tuan_triet_at_star":
        # Sao bị Tuần/Triệt án ngữ (cung sao đó nằm trong vùng tuần/triệt)
        tt = set(ctx.get("tuan_chi") or []) | set(ctx.get("triet_chi") or [])
        return bool(set(_star_chis(cond["star"], all_stars)) & tt)

    if t == "menh_vo_chinh_dieu":
        menh = ctx.get("menh_chi")
        if menh is None:
            return False
        chinh = ctx.get("chinh_tinh") or {}
        return not (chinh.get(menh) or [])

    if t == "stars_in_menh_tu_chinh":
        # Tất cả các sao đều nằm trong tứ chính (tam phương + xung) của cung Mệnh
        menh = ctx.get("menh_chi")
        if menh is None:
            return False
        from .paradigm.to_hop_cung import tam_phuong_tu_chinh
        tu_chinh = set(tam_phuong_tu_chinh(menh)["tu_chinh"])
        for s in cond["stars"]:
            if not (set(_star_chis(s, all_stars)) & tu_chinh):
                return False
        return True

    if t == "star_level":
        # Trạng thái miếu-hãm của sao tại vị trí thật
        from .cross_school import _mieu_ham_level
        chis = _star_chis(cond["star"], all_stars)
        if not chis:
            return False
        lv = _mieu_ham_level(cond["star"], chis[0])
        return lv in cond["level_in"]

    if t == "star_tu_chinh_has_any":
        # Tứ chính của cung sao X chứa ít nhất 1 sao trong any_of
        from .paradigm.to_hop_cung import tam_phuong_tu_chinh
        for chi in _star_chis(cond["star"], all_stars):
            tu_chinh = set(tam_phuong_tu_chinh(chi)["tu_chinh"])
            for other in cond["any_of"]:
                if set(_star_chis(other, all_stars)) & tu_chinh:
                    return True
        return False

    if t == "star_tu_chinh_lacks_all":
        # Tứ chính của cung sao X KHÔNG chứa sao nào trong all_of (Tại Dã Cô Quân)
        from .paradigm.to_hop_cung import tam_phuong_tu_chinh
        chis = _star_chis(cond["star"], all_stars)
        if not chis:
            return False
        tu_chinh = set(tam_phuong_tu_chinh(chis[0])["tu_chinh"])
        for other in cond["all_of"]:
            if set(_star_chis(other, all_stars)) & tu_chinh:
                return False
        return True

    if t == "hoa_all_in_tu_chinh_of_star":
        # TẤT CẢ các hóa trong hoa_in đóng trong tứ chính của cung sao X
        from .paradigm.to_hop_cung import tam_phuong_tu_chinh
        chis = _star_chis(cond["star"], all_stars)
        if not chis:
            return False
        tu_chinh = set(tam_phuong_tu_chinh(chis[0])["tu_chinh"])
        hoa_chi = {th["hoa"]: th.get("palace_chi") for th in ctx.get("tu_hoa") or []}
        return all(hoa_chi.get(h) in tu_chinh for h in cond["hoa_in"])

    if t == "giap_2_ben":
        # Sao X bị kẹp: 1 cung kề có sao nhóm A, cung kề KIA có sao nhóm B
        # (Hình kỵ giáp ấn / Tài ấm giáp ấn). Nhóm hỗ trợ "__hoa_ky__" =
        # cung kề là nơi đóng của sao hóa Kỵ năm sinh.
        from .paradigm.to_hop_cung import giap_cung
        hoa_ky_chi = next((th.get("palace_chi") for th in ctx.get("tu_hoa") or []
                           if th.get("hoa") == "hoa_ky"), None)

        def _side_has(chi: str, group: list[str]) -> bool:
            for g in group:
                if g == "__hoa_ky__":
                    if chi == hoa_ky_chi:
                        return True
                elif g in (all_stars.get(chi) or []):
                    return True
            return False

        for chi in _star_chis(cond["star"], all_stars):
            left, right = giap_cung(chi)
            if (_side_has(left, cond["ben_a"]) and _side_has(right, cond["ben_b"])) or \
               (_side_has(right, cond["ben_a"]) and _side_has(left, cond["ben_b"])):
                return True
        return False

    if t == "tam_hoa_lien_chau":
        chis = []
        for th in ctx.get("tu_hoa") or []:
            if th.get("hoa") in ("hoa_loc", "hoa_quyen", "hoa_khoa") and th.get("palace_chi"):
                chis.append(CHI_RING.index(th["palace_chi"]))
        if len(set(chis)) != 3:
            return False
        chis = sorted(set(chis))
        # 3 cung liền kề (kể cả vòng qua Hợi-Tý)
        spans = [chis[2] - chis[0], 12 - chis[2] + chis[1], 12 - chis[1] + chis[0]]
        return min(spans) == 2

    return False  # condition type lạ → không match (an toàn)


def match_named_cach_cucs(la_so_input: dict) -> list[dict]:
    """Match cách cục có tên với lá số.

    la_so_input cần: chinh_tinh_per_palace + phu_tinh_per_palace (key 12 chi),
    menh_palace, tu_hoa (list {hoa, star, palace_chi}).
    """
    # Gộp chính tinh + phụ tinh + vòng sao theo chi (bỏ key chức năng)
    all_stars: dict[str, list[str]] = {}
    for src in ("chinh_tinh_per_palace", "phu_tinh_per_palace", "vong_sao_per_palace"):
        for k, stars in (la_so_input.get(src) or {}).items():
            if k in CHI_RING:
                all_stars.setdefault(k, []).extend(stars)

    chinh_tinh_chi = {
        k: v for k, v in (la_so_input.get("chinh_tinh_per_palace") or {}).items()
        if k in CHI_RING
    }
    ctx = {
        "all_stars": all_stars,
        "chinh_tinh": chinh_tinh_chi,
        "menh_chi": la_so_input.get("menh_palace"),
        "tu_hoa": la_so_input.get("tu_hoa") or [],
        "tuan_chi": la_so_input.get("tuan_chi") or [],
        "triet_chi": la_so_input.get("triet_chi") or [],
    }

    matched = []
    for cc in load_named_cach_cucs():
        rule = cc.get("match_rule")
        if not rule:
            continue
        try:
            if all(_eval_condition(c, ctx) for c in rule):
                matched.append(cc)
        except Exception:
            continue
    return matched


def atoms_for_cach_cuc(slug: str, aliases: list[str], limit_per_school: int = 2) -> dict:
    """Pull atoms về cách cục: ưu tiên tag cach_cuc, bù bằng tên trong text."""
    from .cross_school import SCHOOL_MAP, SCHOOL_NAMES, _fetch_atom_details

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Tag trước, text sau
    name_conds = " OR ".join(
        ["a.subject_identifiers LIKE ?"] +
        ["a.question_text LIKE ?" for _ in aliases] +
        ["a.source_quote LIKE ?" for _ in aliases]
    )
    params = [f'%cach_cuc%{slug}%'] + [f"%{a}%" for a in aliases] * 2
    rows = conn.execute(f"""
        SELECT a.atom_id, c.book_corpus_id, a.confidence
        FROM atomic_questions a JOIN chunks_v2 c ON c.chunk_id = a.chunk_id
        WHERE ({name_conds}) AND a.founder_verified >= 0
        ORDER BY a.confidence DESC LIMIT 40
    """, params).fetchall()

    by_school: dict[str, list[int]] = {}
    for r in rows:
        sc = SCHOOL_MAP.get(r["book_corpus_id"])
        if sc and len(by_school.setdefault(sc, [])) < limit_per_school:
            by_school[sc].append(r["atom_id"])

    schools_atoms = {}
    for sc, ids in by_school.items():
        schools_atoms[sc] = _fetch_atom_details(conn, ids)
    conn.close()
    return {
        "schools": schools_atoms,
        "total_atoms": sum(len(v) for v in schools_atoms.values()),
    }
