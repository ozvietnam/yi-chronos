"""CUNG_SAO_TO_SECTION mapping — autogen từ DB atoms tags.

Pull atoms từ atomic_questions, parse `subject_identifiers` JSON (mapping
sao/palace từ tag), group by (sao, palace, school) → return list atom_ids.

Used by OutputFiller v2 để pull atoms relevant cho (sao × cung) trong lá số.

Built 2026-06-10 Phase A2.
"""
from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"

# Canonical name mappings (Vietnamese → canonical kebab)
PALACE_CANON = {
    "menh": "menh", "thân": "than", "than": "than",
    "phu_mau": "phu_mau", "phụ_mẫu": "phu_mau",
    "phuc_duc": "phuc_duc", "phúc_đức": "phuc_duc",
    "dien_trach": "dien_trach", "điền_trạch": "dien_trach",
    "quan_loc": "quan_loc", "quan_lộc": "quan_loc",
    "no_boc": "no_boc",
    "thien_di": "thien_di", "thiên_di": "thien_di",
    "tat_ach": "tat_ach", "tật_ách": "tat_ach",
    "tai_bach": "tai_bach", "tài_bạch": "tai_bach",
    "tu_tuc": "tu_tuc",
    "phu_the": "phu_the", "phu_thê": "phu_the",
    "huynh_de": "huynh_de", "huynh_đệ": "huynh_de",
}

STAR_CANON_PREFIX = "star:"
PALACE_CANON_PREFIX = "palace:"


def parse_tags(subject_json: str | None) -> dict:
    if not subject_json:
        return {}
    try:
        return json.loads(subject_json)
    except (json.JSONDecodeError, TypeError):
        return {}


def normalize_palace(p: str) -> str:
    p_norm = p.lower().strip().replace(" ", "_").replace("-", "_")
    return PALACE_CANON.get(p_norm, p_norm)


def normalize_star(s: str) -> str:
    return s.lower().strip().replace(" ", "_").replace("-", "_")


# Cache module-level — mapping gọi ~50 lần/request (mỗi sao × cung 1 lần),
# query DB 1 lần là đủ. Re-ingest atoms thì restart API (hoặc gọi invalidate).
_MAPPING_CACHE: tuple | None = None


def invalidate_mapping_cache():
    global _MAPPING_CACHE
    _MAPPING_CACHE = None


def build_mapping() -> dict:
    """Build mapping: (star, palace) → list[(school, atom_id, section_id, confidence)].

    Returns dict[tuple[star, palace], list[dict]]. Cached module-level.
    """
    global _MAPPING_CACHE
    if _MAPPING_CACHE is not None:
        return _MAPPING_CACHE
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            a.atom_id, a.section_id, a.subject_identifiers, a.confidence, a.founder_verified,
            c.book_corpus_id as school
        FROM atomic_questions a
        JOIN chunks_v2 c ON c.chunk_id = a.chunk_id
        WHERE c.book_corpus_id IN (
            'trung-chau-tu-vi-dau-so-2',
            'tu-vi-dau-so-toan-thu-vu-tai-luc',
            'tu-vi-nghiem-ly-toan-thu-thien-luong',
            'tu-vi-ham-so',
            'tu-vi-dau-so-toan-thu-zh',
            'tuvi-bon-ba-tiktok'
        )
        AND (a.extracted_by LIKE 'sub-agent%' OR a.extracted_by = 'legacy-q1q3-ingest')
    """).fetchall()

    conn.close()

    mapping: dict[tuple[str, str], list[dict]] = defaultdict(list)
    untagged = 0

    for r in rows:
        subj = parse_tags(r["subject_identifiers"])
        # PRECISION (2026-06-13): khóa mapping theo SAO CHỦ NGỮ (star_primary).
        # primary có → atom MẠNH (sao đứng chủ đề câu). primary rỗng → dùng star
        # broad nhưng đánh dấu YẾU (chỉ dùng khi cung thiếu atom mạnh).
        primary = subj.get("star_primary")
        if primary:
            stars, is_weak = primary, 0
        else:
            stars, is_weak = (subj.get("star", []) or subj.get("sao", [])), 1
        palaces = subj.get("palace", []) or subj.get("cung", [])

        if not stars or not palaces:
            untagged += 1
            continue

        is_case = subj.get("is_case_study", 0) or subj.get("is_boilerplate", 0)
        gender = subj.get("gender")  # "F" | "M" | None
        menh_ref = subj.get("menh_chi_ref")  # mệnh người khác ở chi này
        # Lỗ #6: combo nhiều sao chỉ khớp khi lá số đủ sao (same/tuchinh)
        combo_need = [normalize_star(x) for x in primary] if (primary and len(primary) >= 2) else None
        combo_scope = subj.get("combo_scope")
        pos_chi = subj.get("pos_chi")  # atom neo vị trí chi cụ thể
        phu_only = subj.get("primary_phu_only", 0)  # chủ-thể toàn phụ tinh
        for star in stars:
            for palace in palaces:
                s = normalize_star(star)
                p = normalize_palace(palace)
                mapping[(s, p)].append({
                    "atom_id": r["atom_id"],
                    "section_id": r["section_id"],
                    "school": r["school"],
                    "confidence": r["confidence"],
                    "founder_verified": r["founder_verified"],
                    "is_case_study": is_case,
                    "gender": gender,
                    "menh_chi_ref": menh_ref,
                    "is_weak": is_weak,
                    "combo_need": combo_need,
                    "combo_scope": combo_scope,
                    "pos_chi": pos_chi,
                    "phu_only": phu_only,
                })

    _MAPPING_CACHE = (dict(mapping), untagged)
    return _MAPPING_CACHE


def get_atoms_for(star: str, palace: str) -> list[dict]:
    """Get atoms for (star, palace) combo, sorted by founder_verified desc + confidence desc."""
    s = normalize_star(star)
    p = normalize_palace(palace)
    mapping, _ = build_mapping()  # cached in production
    items = mapping.get((s, p), [])
    return sorted(items, key=lambda x: (-x["founder_verified"], -x["confidence"]))


if __name__ == "__main__":
    # Generate full mapping + summary
    mapping, untagged = build_mapping()
    print(f"Total mappings: {len(mapping)}")
    print(f"Atoms untagged (no star/palace tag): {untagged}")
    print()
    print("Top 20 (star, palace) combos by atom count:")
    sorted_combos = sorted(mapping.items(), key=lambda x: -len(x[1]))[:20]
    for (s, p), atoms in sorted_combos:
        schools = set(a["school"] for a in atoms)
        print(f"  {s:20s} × {p:15s} = {len(atoms):3d} atoms ({len(schools)} schools)")

    # Save mapping JSON for OutputFiller v2
    out_path = PROJECT_ROOT / "data" / "tu_vi_cung_sao_mapping.json"
    save_data = {
        f"{s}__{p}": atoms
        for (s, p), atoms in mapping.items()
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "mappings": save_data,
            "stats": {
                "total_combos": len(mapping),
                "untagged_atoms": untagged,
                "total_atoms_mapped": sum(len(v) for v in mapping.values()),
            }
        }, f, ensure_ascii=False, indent=2)
    print()
    print(f"✅ Saved mapping to {out_path}")
