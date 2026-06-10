#!/usr/bin/env python3
"""Chuẩn hóa tag quan hệ cung-cung trong atoms — việc D phần 1.

Sub-agents ghi tag tự do (tam_hop / cung_tam_hop / doi_cung / cung_doi /
muon_sao / giap...) mỗi người 1 kiểu → không query được. Script này detect
từ CẢ tag cũ + keyword trong question/quote, ghi field chuẩn:
    subject_identifiers["relation"] = ["tam_phuong"|"tam_hop"|"hoi_chieu"|
                                       "xung_chieu"|"giap"|"muon_sao", ...]

Lưu ý bẫy tiếng Việt: "giáp" trùng can Giáp (tuổi Giáp, Giáp Kỷ...) →
chỉ match cụm cụ thể (giáp cung, cung giáp, giáp Mệnh, Hình Kỵ giáp...).

Usage: python3 scripts/normalize_relation_tags.py [--dry-run]
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"

CORPORA = (
    "trung-chau-tu-vi-dau-so-2",
    "tu-vi-dau-so-toan-thu-vu-tai-luc",
    "tu-vi-nghiem-ly-toan-thu-thien-luong",
    "tu-vi-ham-so",
    "tu-vi-dau-so-toan-thu-zh",
)

# relation → list cụm keyword (lowercase, match substring)
KEYWORD_RULES: dict[str, list[str]] = {
    "tam_phuong": ["tam phương tứ chính", "tam phương"],
    "tam_hop": ["tam hợp"],
    "hoi_chieu": ["hội chiếu", "hội hợp", "tương hội"],
    "xung_chieu": ["xung chiếu", "đối cung", "cung xung"],
    # "giáp" phải là cụm cụ thể — tránh can Giáp / tuổi Giáp / Giáp Kỷ
    "giap": [
        "giáp cung", "cung giáp", "giáp mệnh", "giáp ấn",
        "hình kỵ giáp", "tài ấm giáp", "kẹp giữa", "bị kẹp",
        "giáp hai bên", "hai cung kề",
    ],
    "muon_sao": ["mượn sao", "tá tinh", "mượn từ đối cung", "vô chính diệu mượn"],
}

# Tag tự do cũ của sub-agents → relation chuẩn
LEGACY_KEY_RULES: dict[str, str] = {
    "tam_hop": "tam_hop",
    "cung_tam_hop": "tam_hop",
    "doi_cung": "xung_chieu",
    "cung_doi": "xung_chieu",
    "muon_sao": "muon_sao",
    "giap_cung": "giap",
    "cung_giap": "giap",
}


def detect_relations(question: str, quote: str, subj: dict) -> list[str]:
    text = f"{question} {quote}".lower()
    rels: set[str] = set()
    for rel, phrases in KEYWORD_RULES.items():
        if any(p in text for p in phrases):
            rels.add(rel)
    for key, rel in LEGACY_KEY_RULES.items():
        if subj.get(key):
            rels.add(rel)
    # vi_tri kiểu "tam phương tứ chính" trong tag cũ
    vi_tri = str(subj.get("vi_tri", "") or subj.get("cung", "")).lower()
    if "tam phương" in vi_tri:
        rels.add("tam_phuong")
    return sorted(rels)


def main():
    dry = "--dry-run" in sys.argv
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    qs = ",".join("?" * len(CORPORA))
    rows = conn.execute(f"""
        SELECT a.atom_id, a.question_text, a.source_quote, a.subject_identifiers
        FROM atomic_questions a
        JOIN chunks_v2 c ON c.chunk_id = a.chunk_id
        WHERE c.book_corpus_id IN ({qs})
          AND a.founder_verified >= 0
    """, CORPORA).fetchall()

    tagged = 0
    by_rel: dict[str, int] = {}
    for r in rows:
        try:
            subj = json.loads(r["subject_identifiers"] or "{}")
        except json.JSONDecodeError:
            subj = {}

        rels = detect_relations(r["question_text"] or "", r["source_quote"] or "", subj)
        if not rels:
            continue
        if subj.get("relation") == rels:
            continue  # đã chuẩn rồi
        subj["relation"] = rels
        tagged += 1
        for rel in rels:
            by_rel[rel] = by_rel.get(rel, 0) + 1
        if not dry:
            conn.execute(
                "UPDATE atomic_questions SET subject_identifiers = ? WHERE atom_id = ?",
                (json.dumps(subj, ensure_ascii=False), r["atom_id"]),
            )

    if not dry:
        conn.commit()
    conn.close()

    print(f"Scanned: {len(rows)}")
    print(f"Tagged relation: {tagged}")
    for rel, n in sorted(by_rel.items()):
        print(f"  {rel}: {n}")
    if dry:
        print("[DRY RUN — chưa ghi DB]")


if __name__ == "__main__":
    main()
