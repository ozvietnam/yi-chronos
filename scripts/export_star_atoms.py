#!/usr/bin/env python3
"""Xuất atoms của 1 chính tinh ra JSON cho thợ viết luận giải sâu.

Lấy mẫu cân bằng: mỗi (cung × nguồn) tối đa N atoms theo founder_verified +
confidence; kèm nhóm atoms "mọi cung" (sao_o_dau_thi, tổng quan).

Usage: .venv/bin/python3 scripts/export_star_atoms.py thien_co /tmp/thien_co_atoms.json [N]
"""
from __future__ import annotations

import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/yi_wiki/wiki.sqlite3"

SCHOOL_LABEL = {
    "trung-chau-tu-vi-dau-so-2": "Trung Châu (Vương Đình Chỉ)",
    "tu-vi-dau-so-toan-thu-vu-tai-luc": "Trần Đoàn — Toàn Thư (Vũ Tài Lục dịch)",
    "tu-vi-dau-so-toan-thu-zh": "Trần Đoàn — Toàn Thư bản Trung (Q1 Phú + Q3 sao×cung)",
    "tu-vi-nghiem-ly-toan-thu-thien-luong": "Thiên Lương (Nghiệm Lý)",
    "tu-vi-ham-so": "Hàm Số (Nguyễn Phát Lộc)",
    "tuvi-bon-ba-tiktok": "Tử Vi Bôn Ba (hiện đại VN — Ngũ Uẩn)",
}


def main(star_slug: str, out_path: str, per_cell: int = 3) -> None:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT a.atom_id, a.question_text, a.source_quote, a.confidence,
                  a.founder_verified, a.subject_identifiers,
                  c.book_corpus_id, c.page_start
           FROM atomic_questions a JOIN chunks_v2 c ON c.chunk_id = a.chunk_id
           WHERE a.subject_identifiers LIKE ?""",
        (f'%"{star_slug}"%',),
    ).fetchall()
    conn.close()

    import unicodedata

    def canon(s: str) -> str:
        nfkd = unicodedata.normalize("NFD", str(s))
        s2 = "".join(c for c in nfkd if not unicodedata.combining(c))
        return s2.lower().strip().replace(" ", "_").replace("-", "_").replace("đ", "d")

    PALACE_12 = {"menh", "phu_mau", "phuc_duc", "dien_trach", "quan_loc", "no_boc",
                 "thien_di", "tat_ach", "tai_bach", "tu_tuc", "phu_the", "huynh_de", "than"}

    def as_list(v) -> list:
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return [x for x in v if isinstance(x, str)]

    buckets: dict[tuple, list] = defaultdict(list)
    for r in rows:
        try:
            subj = json.loads(r["subject_identifiers"] or "{}")
        except json.JSONDecodeError:
            continue
        stars = [canon(s) for s in as_list(subj.get("star")) + as_list(subj.get("sao"))]
        if star_slug not in stars:
            continue
        palaces_raw = as_list(subj.get("palace")) + as_list(subj.get("cung"))
        palaces = [canon(p) for p in palaces_raw]
        palaces = [p for p in palaces if p in PALACE_12]
        # atoms gắn đủ 12 cung = atoms "mọi cung" (vd "sao X ở đâu thì")
        if len(palaces) >= 12:
            key_palaces = ["__moi_cung__"]
        elif palaces:
            key_palaces = palaces
        else:
            key_palaces = ["__tong_quan__"]  # không tag cung chuẩn → nhóm tổng quan
        item = {
            "atom_id": r["atom_id"],
            "q": r["question_text"],
            "quote": (r["source_quote"] or "")[:900],
            "school": SCHOOL_LABEL.get(r["book_corpus_id"], r["book_corpus_id"]),
            "page": r["page_start"],
            "conf": r["confidence"],
            "fv": r["founder_verified"],
        }
        for p in key_palaces:
            buckets[(p, r["book_corpus_id"])].append(item)

    out: dict[str, list] = defaultdict(list)
    seen: set[int] = set()
    for (palace, _school), items in sorted(buckets.items()):
        items.sort(key=lambda x: (-(x["fv"] or 0), -(x["conf"] or 0)))
        for it in items[:per_cell]:
            if it["atom_id"] in seen and palace not in ("__moi_cung__", "__tong_quan__"):
                continue
            seen.add(it["atom_id"])
            out[palace].append(it)

    payload = {
        "star_slug": star_slug,
        "total_atoms_in_db": len(rows),
        "sampled": sum(len(v) for v in out.values()),
        "per_palace": dict(out),
    }
    Path(out_path).write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{star_slug}: {len(rows)} atoms trong DB → lấy mẫu {payload['sampled']} "
          f"({len(out)} nhóm cung) → {out_path}")


if __name__ == "__main__":
    slug = sys.argv[1]
    out = sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    main(slug, out, n)
