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
}

SCHOOL_NAMES = {
    "trung_chau":   "Trung Châu (Vương Đình Chỉ)",
    "tran_doan":    "Trần Đoàn (Toàn Thư)",
    "thien_luong":  "Cụ Thiên Lương (Nghiệm Lý)",
    "ham_so":       "Hàm Số (Nguyễn Phát Lộc)",
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
    cuc = la_so.get("cuc", "thuy_nhi_cuc")
    vong = ba_vong_lon(la_so["can"], la_so["chi"], cuc, la_so.get("gender", "M"))
    warnings.append({
        "type": "ba_vong",
        "severity": "info",
        "msg": f"3 vòng lớn — Lộc Tồn tại {vong['loc_ton']['vi_tri']}, "
               f"Thái Tuế tại {vong['thai_tue']['vi_tri']}",
        "citation": vong["citation"],
        "detail": vong,
    })

    return warnings
