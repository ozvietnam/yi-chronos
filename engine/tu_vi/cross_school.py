"""Cross-school orchestrator — luận giải sao×cung qua 4 hệ phái độc lập.

4 hệ phái:
- **Trung Châu** (Vương Đình Chỉ Q2) — `school_code = "trung_chau"`
- **Trần Đoàn** (Toàn Thư - Vũ Tài Lục) — `school_code = "tran_doan"`
- **Thiên Lương** (Nghiệm Lý Toàn Thư) — `school_code = "thien_luong"`
- **Hàm Số** (Nguyễn Phát Lộc 1972) — `school_code = "ham_so"`

Logic: pull atoms từ mapping → group by school → detect agree/disagree.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"

SCHOOL_MAP = {
    "trung-chau-tu-vi-dau-so-2": "trung_chau",
    "tu-vi-dau-so-toan-thu-vu-tai-luc": "tran_doan",
    "tu-vi-nghiem-ly-toan-thu-thien-luong": "thien_luong",
    "tu-vi-ham-so": "ham_so",
    "tu-vi-dau-so-toan-thu-zh": "tran_doan_zh",  # bản dịch Trung Q1 Phú + Q3 sao×cung
}

SCHOOL_NAMES = {
    "trung_chau":    "Trung Châu (Vương Đình Chỉ)",
    "tran_doan":     "Trần Đoàn (Toàn Thư — Vũ Tài Lục)",
    "tran_doan_zh":  "Trần Đoàn (TVDSTT bản dịch Trung — Q1 Phú + Q3)",
    "thien_luong":   "Cụ Thiên Lương (Nghiệm Lý)",
    "ham_so":        "Hàm Số (Nguyễn Phát Lộc)",
}


def _fetch_atom_details(conn: sqlite3.Connection, atom_ids: list[int]) -> list[dict]:
    if not atom_ids:
        return []
    qs = ",".join("?" * len(atom_ids))
    rows = conn.execute(f"""
        SELECT
            a.atom_id, a.question_text, a.source_quote, a.confidence,
            a.founder_verified, a.section_id,
            c.book_corpus_id, c.page_start,
            cm.han_viet_explain, cm.viet_thuan, cm.nguyen_ly,
            cm.vi_du_doi_song, cm.iron_rule_warning
        FROM atomic_questions a
        JOIN chunks_v2 c ON c.chunk_id = a.chunk_id
        LEFT JOIN atom_commentaries cm ON cm.atom_id = a.atom_id
        WHERE a.atom_id IN ({qs})
    """, atom_ids).fetchall()
    return [dict(r) for r in rows]


def luan_sao_cung(star: str, palace: str, limit_per_school: int = 5) -> dict:
    """Luận giải sao × cung qua 4 hệ phái.

    Returns dict:
      {
        "star": str,
        "palace": str,
        "schools": {
          "trung_chau": [atom_dicts...],
          "tran_doan": [...],
          "thien_luong": [...],
          "ham_so": [...]
        },
        "agree_count": int (atoms cùng nói),
        "schools_present": list[str]
      }
    """
    from .cung_sao_mapping import normalize_star, normalize_palace, build_mapping

    s = normalize_star(star)
    p = normalize_palace(palace)

    mapping, _ = build_mapping()
    items = mapping.get((s, p), [])

    # Group atom_ids by school
    by_school: dict[str, list[int]] = {sc: [] for sc in SCHOOL_NAMES}
    for item in items:
        school_code = SCHOOL_MAP.get(item["school"])
        if school_code:
            by_school[school_code].append(item["atom_id"])

    # Truncate to limit_per_school (theo confidence)
    for sc in by_school:
        by_school[sc] = sorted(by_school[sc])[:limit_per_school]

    # Fetch atom details
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    schools_atoms = {}
    for sc, ids in by_school.items():
        schools_atoms[sc] = _fetch_atom_details(conn, ids)
    conn.close()

    return {
        "star": s,
        "palace": p,
        "schools": schools_atoms,
        "schools_present": [sc for sc, atoms in schools_atoms.items() if atoms],
        "total_atoms": sum(len(a) for a in schools_atoms.values()),
    }


# ── Retrieval v2: atoms tổ hợp cung (tam phương / hội chiếu / giáp / mượn sao) ──
# Cache module-level: ~1.2k atoms relation-tagged, load 1 lần rồi filter Python.
_RELATION_ATOMS_CACHE: list[dict] | None = None

RELATION_NAMES_VI = {
    "tam_phuong": "Tam phương tứ chính",
    "tam_hop": "Tam hợp",
    "hoi_chieu": "Hội chiếu",
    "xung_chieu": "Xung chiếu / đối cung",
    "giap": "Giáp cung",
    "muon_sao": "Mượn sao an cung",
}


def _load_relation_atoms() -> list[dict]:
    global _RELATION_ATOMS_CACHE
    if _RELATION_ATOMS_CACHE is not None:
        return _RELATION_ATOMS_CACHE
    import json
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT a.atom_id, a.subject_identifiers, a.confidence,
               c.book_corpus_id
        FROM atomic_questions a
        JOIN chunks_v2 c ON c.chunk_id = a.chunk_id
        WHERE a.subject_identifiers LIKE '%"relation"%'
          AND a.founder_verified >= 0
    """).fetchall()
    conn.close()
    out = []
    for r in rows:
        try:
            subj = json.loads(r["subject_identifiers"] or "{}")
        except json.JSONDecodeError:
            continue
        school = SCHOOL_MAP.get(r["book_corpus_id"])
        if not school:
            continue
        out.append({
            "atom_id": r["atom_id"],
            "stars": set(subj.get("star") or []),
            "relations": subj.get("relation") or [],
            "school": school,
            "confidence": r["confidence"],
        })
    _RELATION_ATOMS_CACHE = out
    return out


def luan_to_hop_cung(chi: str, chinh_tinh_per_palace: dict[str, list[str]],
                     limit_per_school: int = 3) -> dict:
    """Luận tổ hợp cung: pull atoms quan hệ cung-cung KHỚP với sao hội chiếu
    thật của lá số (việc D — chống 'luận đoán máy móc' theo Trung Châu).

    Match rule: atom relation-tagged + tag ≥2 sao + toàn bộ sao của atom
    nằm trong tập sao hội chiếu của tứ chính (tức tổ hợp đó lá số CÓ thật).
    Atoms giáp: sao atom ⊆ (sao cung + sao 2 cung giáp).
    """
    from .paradigm import to_hop_cung as compute_to_hop

    th = compute_to_hop(chi, chinh_tinh_per_palace)
    hoi_chieu_set = set(th["hoi_chieu_stars"])
    giap_set = set(chinh_tinh_per_palace.get(chi) or [])
    for c in th["giap"]["cungs"]:
        giap_set |= set(th["giap"]["stars_per_cung"].get(c) or [])

    by_school: dict[str, list[dict]] = {sc: [] for sc in SCHOOL_NAMES}
    for atom in _load_relation_atoms():
        if len(atom["stars"]) < 2:
            continue  # combo phải ≥2 sao — atom 1 sao đã có ở lớp sao×cung
        rels = set(atom["relations"])
        if rels & {"tam_phuong", "tam_hop", "hoi_chieu", "xung_chieu", "muon_sao"}:
            if atom["stars"] <= hoi_chieu_set:
                by_school[atom["school"]].append(atom)
                continue
        if "giap" in rels and atom["stars"] <= giap_set:
            by_school[atom["school"]].append(atom)

    # Fetch details, sort confidence cao trước
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    schools_atoms: dict[str, list[dict]] = {}
    for sc, atoms in by_school.items():
        atoms.sort(key=lambda a: -(a["confidence"] or 0))
        ids = [a["atom_id"] for a in atoms[:limit_per_school]]
        details = _fetch_atom_details(conn, ids)
        # Gắn relations vào detail để UI hiển thị loại quan hệ
        rel_by_id = {a["atom_id"]: a["relations"] for a in atoms}
        for d in details:
            d["relations"] = rel_by_id.get(d["atom_id"], [])
        schools_atoms[sc] = details
    conn.close()

    return {
        "cung": chi,
        "to_hop": th,
        "schools": schools_atoms,
        "schools_present": [sc for sc, a in schools_atoms.items() if a],
        "total_atoms": sum(len(a) for a in schools_atoms.values()),
    }


def detect_paradigm_warnings(la_so: dict) -> list[dict]:
    """Run paradigm engine + return list warnings.

    la_so: dict {
      "can": "mau", "chi": "thin",  # năm sinh
      "menh_palace": "ty",          # cung Mệnh (chi)
      "than_palace": "than",        # cung Thân
      "chinh_tinh_per_palace": {     # 12 cung × chính tinh
        "ty": ["thien_phu"], ...
      },
      "gender": "M"|"F",
    }

    Returns: [{type, severity, msg, citation, ...}]
    """
    from .paradigm import (
        is_nhan_cung, bac_tuoi, tam_hop_loc_ton, ba_vong_lon
    )

    warnings = []

    # 1. Bậc tuổi
    bac, name, cit = bac_tuoi(la_so["can"], la_so["chi"])
    warnings.append({
        "type": "bac_tuoi",
        "severity": "info" if bac in (1, 2) else "warning" if bac in (3, 4) else "danger",
        "msg": f"Bậc tuổi {bac}: {name}",
        "citation": cit,
    })

    # 2. Tam hợp Lộc Tồn
    huong, msg, cit = tam_hop_loc_ton(la_so["can"], la_so["chi"])
    warnings.append({
        "type": "tam_hop_loc",
        "severity": "info" if huong else "neutral",
        "msg": msg,
        "citation": cit,
    })

    # 3. Nhân Cung check ALL chính tinh trong lá số
    for palace, stars in (la_so.get("chinh_tinh_per_palace") or {}).items():
        for star in stars:
            hit, info_msg = is_nhan_cung(star, palace)
            if hit:
                warnings.append({
                    "type": "nhan_cung",
                    "severity": "warning",
                    "msg": info_msg,
                    "star": star,
                    "palace": palace,
                })

    # 4. 3 vòng lớn overview
    from .viet_names import vi_chi
    cuc = la_so.get("cuc", "thuy_nhi_cuc")
    vong = ba_vong_lon(la_so["can"], la_so["chi"], cuc, la_so.get("gender", "M"))
    warnings.append({
        "type": "ba_vong",
        "severity": "info",
        "msg": f"3 vòng lớn — Lộc Tồn tại {vi_chi(vong['loc_ton']['vi_tri'])}, "
               f"Thái Tuế tại {vi_chi(vong['thai_tue']['vi_tri'])}",
        "citation": vong["citation"],
        "detail": vong,
    })

    return warnings
