#!/usr/bin/env python3
"""Bịt 3 lỗ rò precision retrieval (Anh giao 2026-06-13).

Lỗi gốc: tag sao theo "có NHẮC trong text" → atom về Thiên Phủ lọt ô Thiên Tướng,
case-study lá số người khác + atom nữ-mệnh trộn vào lá số nam. ~35% atoms cung
Mệnh lạc.

Bồi 3 field vào subject_identifiers (KHÔNG xoá tag cũ):
- star_primary: sao CHỦ NGỮ — sao xuất hiện trong question_text (cái atomizer
  chắt lọc "atom này hỏi VỀ gì"). Fallback: sao sớm nhất trong source_quote.
- is_case_study: 1 nếu là ví dụ lá số cụ thể (lá số + can-chi + nam/nữ + ngày/giờ).
- gender: "F" | "M" | None — atom chỉ đúng cho 1 giới.

Usage: python3 scripts/enrich_atom_precision.py [--dry-run]
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
sys.path.insert(0, str(PROJECT_ROOT))

from engine.tu_vi.star_aliases import alias_to_stars  # noqa: E402

CORPORA = (
    "trung-chau-tu-vi-dau-so-2", "tu-vi-dau-so-toan-thu-vu-tai-luc",
    "tu-vi-nghiem-ly-toan-thu-thien-luong", "tu-vi-ham-so",
    "tu-vi-dau-so-toan-thu-zh", "tuvi-bon-ba-tiktok",
)

# Case-study: lá số ví dụ cụ thể (can-chi + giới + ngày/giờ)
_CASE_RE = re.compile(
    r"(lá số|mệnh tạo|đương số này|ví dụ).{0,40}"
    r"(âm nam|âm nữ|dương nam|dương nữ|" +
    r"(giáp|ất|bính|đinh|mậu|kỷ|canh|tân|nhâm|quý)\s"
    r"(tý|sửu|dần|mão|thìn|tỵ|tị|ngọ|mùi|thân|dậu|tuất|hợi))",
    re.IGNORECASE,
)
_CASE_RE2 = re.compile(
    r"(âm nam|âm nữ|dương nam|dương nữ).{0,30}(ngày|giờ|tháng)\s*\d",
    re.IGNORECASE,
)

# Giới tính
_FEMALE = ["đàn bà", "phụ nữ", "nữ mệnh", "nữ nhân", "con gái", "người nữ", "gái"]
_MALE_ONLY = ["nam mệnh", "đàn ông", "con trai", "nam nhân", "người nam"]

# Lỗ #4: atom gắn "Mệnh ở/cư/tại <chi>" = mệnh người cụ thể ở chi đó
_CHI_VI = {"tý": "ty", "tí": "ty", "sửu": "suu", "dần": "dan", "mão": "mao",
           "thìn": "thin", "tỵ": "ti", "tị": "ti", "ngọ": "ngo", "mùi": "mui",
           "thân": "than", "dậu": "dau", "tuất": "tuat", "hợi": "hoi"}
_MENH_CHI_RE = re.compile(
    r"[Mm]ệnh\s+(?:ở|cư|tại|an|đóng(?:\s+(?:ở|tại))?)\s+"
    r"(Tý|Tí|Sửu|Dần|Mão|Thìn|Tỵ|Tị|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi)\b")


def detect_menh_chi_ref(text: str) -> str | None:
    m = _MENH_CHI_RE.search(text)
    return _CHI_VI.get(m.group(1).lower()) if m else None


# Lỗ #6: atom combo nhiều sao — khớp ở phạm vi nào?
_SCOPE_TUCHINH = ["triều", "hội", "chiếu", "củng", "hiệp", "giáp", "tam hợp", "tam phương"]


def detect_combo_scope(question: str) -> str:
    """Combo nhiều sao khớp ở: 'same' (đồng cung) hay 'tuchinh' (hội chiếu)."""
    q = (question or "").lower()
    return "tuchinh" if any(w in q for w in _SCOPE_TUCHINH) else "same"


def detect_primary_stars(question: str, quote: str) -> list[str]:
    """Sao chủ ngữ: ưu tiên sao trong question_text (chủ đề atomizer chắt lọc).

    Trả list canonical, theo thứ tự xuất hiện. Rỗng → fallback quote.
    """
    table = alias_to_stars()
    # Chỉ dùng alias là TÊN SAO (loại cụm cách cục dài) để tránh nhiễu
    def _scan(text: str) -> list[str]:
        hits = []  # (vị trí, canonical)
        for alias, stars in table.items():
            pos = text.find(alias)
            if pos >= 0:
                for s in stars:
                    hits.append((pos, s))
        hits.sort()
        out = []
        for _, s in hits:
            if s not in out:
                out.append(s)
        return out

    # CHỈ lấy sao trong question (chủ đề atomizer chắt lọc). KHÔNG fallback quote
    # — fallback kéo lại sao nhắc-kèm = nguồn rác. Question rỗng sao → trả [] →
    # atom xếp "yếu", chỉ dùng khi cung thiếu atom mạnh.
    return _scan(question or "")[:3]


def detect_gender(text: str) -> str | None:
    t = text.lower()
    has_f = any(w in t for w in _FEMALE)
    has_m = any(w in t for w in _MALE_ONLY)
    if has_f and not has_m:
        return "F"
    if has_m and not has_f:
        return "M"
    return None


def main():
    dry = "--dry-run" in sys.argv
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    qs = ",".join("?" * len(CORPORA))
    rows = conn.execute(f"""
        SELECT a.atom_id, a.question_text, a.source_quote, a.subject_identifiers
        FROM atomic_questions a JOIN chunks_v2 c ON c.chunk_id = a.chunk_id
        WHERE c.book_corpus_id IN ({qs}) AND a.founder_verified >= 0
    """, CORPORA).fetchall()

    n_prim = n_case = n_gender = n_menhref = n_combo = 0
    for r in rows:
        try:
            subj = json.loads(r["subject_identifiers"] or "{}")
        except json.JSONDecodeError:
            continue
        q = r["question_text"] or ""
        sq = r["source_quote"] or ""
        changed = False

        prim = detect_primary_stars(q, sq)
        if prim:
            if subj.get("star_primary") != prim:
                subj["star_primary"] = prim
                n_prim += 1
                changed = True
        elif "star_primary" in subj:
            # question rỗng sao → xoá primary cũ (từ lần fallback) → atom xếp yếu
            del subj["star_primary"]
            changed = True

        is_case = 1 if (_CASE_RE.search(q + " " + sq) or _CASE_RE2.search(q + " " + sq)) else 0
        if is_case and subj.get("is_case_study") != 1:
            subj["is_case_study"] = 1
            n_case += 1
            changed = True

        g = detect_gender(q + " " + sq)
        if g and subj.get("gender") != g:
            subj["gender"] = g
            n_gender += 1
            changed = True

        mref = detect_menh_chi_ref(q + " " + sq)
        if mref and subj.get("menh_chi_ref") != mref:
            subj["menh_chi_ref"] = mref
            n_menhref += 1
            changed = True

        # Lỗ #6: combo scope cho atom có ≥2 sao chủ ngữ
        prim_now = subj.get("star_primary") or []
        if len(prim_now) >= 2:
            scope = detect_combo_scope(q)
            if subj.get("combo_scope") != scope:
                subj["combo_scope"] = scope
                n_combo += 1
                changed = True
        elif "combo_scope" in subj:
            del subj["combo_scope"]
            changed = True

        if changed and not dry:
            conn.execute(
                "UPDATE atomic_questions SET subject_identifiers = ? WHERE atom_id = ?",
                (json.dumps(subj, ensure_ascii=False), r["atom_id"]),
            )

    if not dry:
        conn.commit()
    conn.close()
    print(f"Scanned: {len(rows)}")
    print(f"  star_primary gắn: {n_prim}")
    print(f"  is_case_study=1:  {n_case}")
    print(f"  gender (F/M):     {n_gender}")
    print(f"  menh_chi_ref:     {n_menhref}")
    print(f"  combo_scope:      {n_combo}")
    if dry:
        print("[DRY RUN]")


if __name__ == "__main__":
    main()
