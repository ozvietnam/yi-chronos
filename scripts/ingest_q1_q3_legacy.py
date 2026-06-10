#!/usr/bin/env python3
"""Ingest Q1 Phú Thái Vi (64 passages) + Q3 sao×cung lines (1418 lines)
từ bản dịch tuvidauso-zh vào atom store.

School: tran_doan_zh (TVDSTT bản dịch Trung — phân biệt với bản Vũ Tài Lục).
Đây chính là nguồn nuôi hệ cung_reading cũ — giờ hợp nhất vào atom store
để OutputFiller v2 dùng được (việc A Anh chốt 2026-06-10).

Q3 lines: data/yi_publishing/translations/tuvidauso-zh/p0142-p0198/r*.json
Q1 phú:   _phu_thai_vi_layer3.json

Atom mapping:
- question     = generated từ hanviet (luận về sao/cung gì)
- source_quote = hanviet (cổ văn dịch âm — giữ nguyên)
- viet_thuan   = luangiai
- vi_du_doi_song = giaithichdande (nếu có — Q1 only)
- tags         = star:* + palace:* detect từ text
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
TRANSL_ROOT = PROJECT_ROOT / "data" / "yi_publishing" / "translations" / "tuvidauso-zh"

BOOK_CORPUS = "tu-vi-dau-so-toan-thu-zh"  # bản dịch Trung — corpus riêng

# Sao names → canonical (để build tags)
STAR_PATTERNS = {
    "tu_vi": ["Tử Vi", "Tử Vy"],
    "thien_co": ["Thiên Cơ"],
    "thai_duong": ["Thái Dương", "Nhật"],
    "vu_khuc": ["Vũ Khúc"],
    "thien_dong": ["Thiên Đồng"],
    "liem_trinh": ["Liêm Trinh"],
    "thien_phu": ["Thiên Phủ"],
    "thai_am": ["Thái Âm", "Nguyệt"],
    "tham_lang": ["Tham Lang"],
    "cu_mon": ["Cự Môn"],
    "thien_tuong": ["Thiên Tướng"],
    "thien_luong": ["Thiên Lương"],
    "that_sat": ["Thất Sát"],
    "pha_quan": ["Phá Quân"],
    "van_xuong": ["Văn Xương"],
    "van_khuc": ["Văn Khúc"],
    "loc_ton": ["Lộc Tồn"],
    "kinh_duong": ["Kình Dương"],
    "da_la": ["Đà La"],
    "hoa_tinh": ["Hỏa Tinh"],
    "linh_tinh": ["Linh Tinh"],
    "thien_khoi": ["Thiên Khôi"],
    "thien_viet": ["Thiên Việt"],
    "ta_phu": ["Tả Phụ", "Tả Phù"],
    "huu_bat": ["Hữu Bật"],
    "hoa_loc": ["Hóa Lộc"],
    "hoa_quyen": ["Hóa Quyền"],
    "hoa_khoa": ["Hóa Khoa"],
    "hoa_ky": ["Hóa Kỵ", "Hóa Kị"],
}

PALACE_PATTERNS = {
    "menh": ["Mệnh", "mệnh cung", "tại Mệnh", "thủ Mệnh"],
    "huynh_de": ["Huynh Đệ", "huynh đệ"],
    "phu_the": ["Phu Thê", "cung Thê", "cung Phu"],
    "tu_tuc": ["Tử Tức", "Tử Nữ"],
    "tai_bach": ["Tài Bạch"],
    "tat_ach": ["Tật Ách"],
    "thien_di": ["Thiên Di"],
    "no_boc": ["Nô Bộc"],
    "quan_loc": ["Quan Lộc"],
    "dien_trach": ["Điền Trạch"],
    "phuc_duc": ["Phúc Đức"],
    "phu_mau": ["Phụ Mẫu"],
}


def detect_tags(text: str) -> list[str]:
    tags = []
    for canon, pats in STAR_PATTERNS.items():
        if any(p in text for p in pats):
            tags.append(f"star:{canon}")
    for canon, pats in PALACE_PATTERNS.items():
        if any(p in text for p in pats):
            tags.append(f"palace:{canon}")
    return tags


def load_q1_passages() -> list[dict]:
    data = json.loads((TRANSL_ROOT / "_phu_thai_vi_layer3.json").read_text())
    out = []
    for i, p in enumerate(data.get("passages", []), 1):
        hanviet = (p.get("hanviet") or "").strip()
        luangiai = (p.get("luangiai") or "").strip()
        if not hanviet or not luangiai or len(hanviet) < 10:
            continue
        tags = detect_tags(hanviet + " " + luangiai)
        out.append({
            "question_id": f"tdzh.Q1.P{i:03d}",
            "question": f"Phú Thái Vi nói gì: \"{hanviet[:60]}...\"?",
            "answer_atom": luangiai,
            "source_quote": hanviet,
            "source_page": int(p.get("page") or 16),
            "section_id": "tdzh.Q1-phu-thai-vi",
            "tags": tags + ["genre:phu", "school:tran_doan_zh"],
            "commentary": {
                "han_viet_explain": None,
                "viet_thuan": luangiai,
                "nguyen_ly": None,
                "vi_du_doi_song": (p.get("giaithichdande") or "").strip() or None,
                "iron_rule_warning": None,
            },
            "confidence": 0.85,
            "extracted_by": "legacy-q1q3-ingest",
        })
    return out


def load_q3_lines() -> list[dict]:
    """Q3 lines p0142-p0198 — format per cung_reading._load_q3_lines."""
    out = []
    idx = 0
    for pn in range(142, 199):
        pdir = TRANSL_ROOT / f"p{pn:04d}"
        if not pdir.is_dir():
            continue
        for jf in sorted(pdir.glob("r*.json")):
            try:
                d = json.loads(jf.read_text())
            except Exception:
                continue
            lines = d.get("lines") or {}
            # Format: {"lines": {"r001-l001": {"text_vi": hanviet, "text_vi_luangiai": ...}}}
            for line_id, line in (lines.items() if isinstance(lines, dict) else []):
                if not isinstance(line, dict):
                    continue
                hanviet = (line.get("text_vi") or line.get("hanviet") or "").strip()
                luangiai = (line.get("text_vi_luangiai") or line.get("luangiai") or "").strip()
                if not hanviet or not luangiai or len(hanviet) < 12:
                    continue
                idx += 1
                tags = detect_tags(hanviet + " " + luangiai)
                # Q3 = sao×cung điều văn — chỉ giữ lines có ít nhất 1 star tag
                if not any(t.startswith("star:") for t in tags):
                    continue
                out.append({
                    "question_id": f"tdzh.Q3.L{idx:04d}",
                    "question": f"Q3 TVDSTT luận: \"{hanviet[:60]}...\"?",
                    "answer_atom": luangiai,
                    "source_quote": hanviet,
                    "source_page": pn,
                    "section_id": "tdzh.Q3-sao-cung",
                    "tags": tags + ["genre:dieu_van", "school:tran_doan_zh"],
                    "commentary": {
                        "han_viet_explain": None,
                        "viet_thuan": luangiai,
                        "nguyen_ly": None,
                        "vi_du_doi_song": None,
                        "iron_rule_warning": None,
                    },
                    "confidence": 0.85,
                    "extracted_by": "legacy-q1q3-ingest",
                })
    return out


def main():
    dry = "--dry-run" in sys.argv

    q1 = load_q1_passages()
    q3 = load_q3_lines()
    print(f"Q1 Phú Thái Vi: {len(q1)} atoms")
    print(f"Q3 sao×cung:    {len(q3)} atoms")

    # Stats tags
    with_star = sum(1 for a in q1 + q3 if any(t.startswith("star:") for t in a["tags"]))
    with_palace = sum(1 for a in q1 + q3 if any(t.startswith("palace:") for t in a["tags"]))
    print(f"Atoms có star tag: {with_star} | có palace tag: {with_palace}")

    if dry:
        print("\n[DRY RUN] Sample atom:")
        print(json.dumps((q1 + q3)[0], ensure_ascii=False, indent=1)[:800])
        return

    # Write draft JSON rồi dùng ingest_atomize_v3
    draft_dir = PROJECT_ROOT / "data" / "atomize_v2_drafts" / "toan-thu-zh-legacy"
    draft_dir.mkdir(parents=True, exist_ok=True)

    for section_id, atoms, fname in [
        ("tdzh.Q1-phu-thai-vi", q1, "tdzh.Q1-phu-thai-vi.json"),
        ("tdzh.Q3-sao-cung", q3, "tdzh.Q3-sao-cung.json"),
    ]:
        payload = {
            "book_corpus_id": BOOK_CORPUS,
            "section_id": section_id,
            "section_title": section_id,
            "pages": sorted(set(a["source_page"] for a in atoms)),
            "atoms": atoms,
        }
        (draft_dir / fname).write_text(json.dumps(payload, ensure_ascii=False, indent=1))
        print(f"✅ Wrote {fname}: {len(atoms)} atoms")

    print("\nNext: python3 scripts/ingest_atomize_v3.py data/atomize_v2_drafts/toan-thu-zh-legacy/")


if __name__ == "__main__":
    main()
