#!/usr/bin/env python3
"""C2a — Seed P0 `sao_noi_dung` gaps từ quote CÓ TRONG SÁCH (2026-07-27).

Chỉ insert dòng đã kiểm provenance shingle ≥ 0.85 với chunks_v2 / content.md.
KHÔNG bịa per-cung khi sách im. Idempotent theo (sao_vi, lop, cung, quote_goc).

Dùng:
  .venv/bin/python3 scripts/seed_c2a_p0_sao_noi_dung.py           # dry-run
  .venv/bin/python3 scripts/seed_c2a_p0_sao_noi_dung.py --commit  # ghi DB
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/yi_wiki/wiki.sqlite3"
RESTORED = ROOT / "data/restored_books"
PROV_THRESH = 0.85

_VN = "àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ"
_KEEP = re.compile(r"[^0-9a-z" + _VN + r"一-鿿]")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", (s or "").lower())
    return _KEEP.sub("", s)


def shingle_cov(quote: str, hay: str, k: int = 8, step: int = 3) -> float:
    q = norm(quote)
    h = hay
    if not q or not h:
        return 0.0
    sh = [q[i : i + k] for i in range(0, max(0, len(q) - k + 1), step)] or [q]
    if not sh:
        return 0.0
    hit = sum(1 for s in sh if s in h)
    return hit / len(sh)


def book_haystack(db: sqlite3.Connection, book: str) -> str:
    parts = [r[0] or "" for r in db.execute(
        "SELECT text FROM chunks_v2 WHERE book_corpus_id=?", (book,))]
    blob = norm(" ".join(parts))
    if len(blob) >= 5000:
        return blob
    p = RESTORED / book / "content.md"
    if p.exists():
        return norm(p.read_text(encoding="utf-8", errors="ignore"))
    return blob


# (sao_vi, sao_zh, lop, cung|None, quote_goc, dich_thuan_viet, nguon_book, nguon_loc)
# quote_goc = đoạn gần nguyên văn sách (VI) để provenance; dich = bản sạch cho engine.
ROWS: list[tuple] = [
    (
        "Văn Tinh", "文星", "def", None,
        "Đây là sao văn học, có nhiều ý nghĩa liên quan đến học hành, cụ thể là: "
        "Sự thông minh. Tính hiếu học. Khả năng học vấn. Khả năng thành danh sĩ. "
        "Đi với các sao văn học khác như Khoa, Xương Khúc, Khôi Việt, Nhật, Nguyệt sáng sủa "
        "thì trình độ thông minh và học vấn càng cao thêm, có nhiều khoa bản hơn.",
        "Lưu Niên Văn Tinh (engine gọi tắt Văn Tinh) là sao văn học: thông minh, hiếu học, "
        "học vấn, thành danh sĩ. Hội Khoa / Xương Khúc / Khôi Việt / Nhật Nguyệt sáng thì "
        "học lực và khoa bản càng mạnh.",
        "tu-vi-ham-so", "content.md p.191 · mục LƯU NIÊN VĂN TINH §1",
    ),
    (
        "Văn Tinh", "文星", "cung", "Mệnh",
        "Ở Mệnh, Thân, Quan Lưu Niên Văn Tinh đồng nghĩa. Nếu không gặp sao xấu thì học hành, "
        "công danh tiến đạt. Không thấy nói đến vị trí hãm địa của sao này. Tuy nhiên, vì là "
        "sao chủ về học hành nên đóng ở các cung Thân, Mệnh, Quan thì thích hợp hơn cả. "
        "Nói khác đi, nếu Lưu Niên Văn Tinh đóng ở các cung Tật Ách, Tài chắc chắn sẽ không "
        "có chỗ dụng, khác nào như bị lạc hãm.",
        "Văn Tinh (Lưu Niên) ở Mệnh đồng nghĩa với khi ở Thân / Quan: không gặp sao xấu thì "
        "học hành, công danh tiến đạt. Sách không nêu hãm địa riêng; chỗ dụng hợp nhất là "
        "Mệnh–Thân–Quan (Tật/Tài coi như không chỗ dụng).",
        "tu-vi-ham-so", "content.md p.191 · mục LƯU NIÊN VĂN TINH §2",
    ),
    (
        "Lưu Hà", "流霞", "cung", "Mệnh",
        "Lưu Hà chỉ bệnh máu loãng, dễ bị băng huyết đối với phụ nữ. Nữ mệnh có Lưu Hà ở Mệnh "
        "hay ở Tật rất dễ bị làm băng lúc sinh đẻ.",
        "Lưu Hà ở Mệnh (hoặc Tật): với nữ mệnh, sách Hàm Số gắn với máu loãng / dễ băng huyết "
        "khi sinh — chỉ là lớp bệnh lý trong sách, không phải đoán bệnh thay y tế.",
        "tu-vi-ham-so", "content.md p.190 · Lưu Hà · ý nghĩa bệnh lý",
    ),
    (
        "Thiên Hỉ", "天喜", "cung", "Mệnh",
        "Thiên Hỉ Hồng Loan nhập Mệnh cung. Nghĩa là: Mệnh có Thiên Hỉ, Hồng Loan: Làm việc gì "
        "cũng dễ trót lọt, con người tài hoa. Sao Thiên Hỉ tiền nhân ta coi nó chủ về dung mạo "
        "tuấn mỹ hoặc là con người rất có duyên. Sao Thiên Hỉ chủ mừng vui. Thiên Hỉ thủ mệnh "
        "miệng cười có duyên.",
        "Thiên Hỉ thủ Mệnh (cùng mạch Hồng Loan nhập Mệnh trong phú tiền nhân / Vũ Tài Lục): "
        "chủ mừng vui, duyên dáng; phú gắn với việc dễ thông, tài hoa — đọc cấu trúc, không đoán sự kiện.",
        "tu-vi-dau-so-toan-thu-vu-tai-luc", "content.md p.62–63 · Hồng Loan–Thiên Hỉ",
    ),
    (
        "Ân Quang", "恩光", "cung", "Phụ Mẫu",
        "Vốn là phúc tinh, Quang Quý ở cung nào cũng đẹp, đem phúc lại cho cung đó. Vì vậy, "
        "Quang Quý không có vị trí Hãm Địa.",
        "Ân Quang thuộc bộ Quang Quý: sách Hàm Số ghi Quang Quý ở cung nào cũng đẹp, đem phúc "
        "cho cung đó (không hãm địa). Ở Phụ Mẫu → lớp phúc/che chở soi quan hệ trên–dưới/cha mẹ "
        "theo nghĩa động từ, không phán số phận.",
        "tu-vi-ham-so", "content.md p.148 · Ý nghĩa Quang Quý ở các cung",
    ),
    (
        "Thiên Quý", "天贵", "cung", "Điền Trạch",
        "Vốn là phúc tinh, Quang Quý ở cung nào cũng đẹp, đem phúc lại cho cung đó. Vì vậy, "
        "Quang Quý không có vị trí Hãm Địa.",
        "Thiên Quý thuộc bộ Quang Quý: ở cung nào cũng đẹp, đem phúc cho cung đó. Ở Điền Trạch "
        "→ phúc tinh soi miền nhà cửa/đất đai (không bịa họa thất cụ thể).",
        "tu-vi-ham-so", "content.md p.148 · Ý nghĩa Quang Quý ở các cung",
    ),
    (
        "Quan Phù", "官符", "cung", "Phúc Đức",
        "Thành thử, Quan Phù báo hiệu cho nghiệp chướng của việc báo oán, thù dai nếu tọa thủ "
        "ở Phúc Đức, Mệnh, Thân.",
        "Quan Phù tọa thủ Phúc Đức (cùng Mệnh/Thân theo Hàm Số): báo lớp nghiệp báo oán / thù dai "
        "trong cấu trúc phúc–nghiệp — quan sát cách vận hành, không đoán kiện tụng đóng.",
        "tu-vi-ham-so", "content.md p.197 · Quan Phù",
    ),
    # Thiên Lương — định nghĩa Lưu Niên Văn Tinh (bổ sung def, đa phái)
    (
        "Văn Tinh", "文星", "def", None,
        "Còn Lưu Niên Văn Tinh là anh em kết nghĩa với Lộc Tồn.",
        "Phái Thiên Lương: Lưu Niên Văn Tinh là 'anh em kết nghĩa' với Lộc Tồn — cùng nhóm "
        "Lộc do Thiên Can xếp (cùng Hóa Lộc, Thiên Trù).",
        "tu-vi-nghiem-ly-toan-thu-thien-luong", "content.md ~p.16–17 · bốn thứ Lộc",
    ),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true")
    args = ap.parse_args()

    db = sqlite3.connect(DB)
    hay: dict[str, str] = {}
    today = date.today().isoformat()
    ok, skip, fail = [], [], []

    for row in ROWS:
        sao, zh, lop, cung, quote, dich, book, loc = row
        if book not in hay:
            hay[book] = book_haystack(db, book)
        cov = shingle_cov(quote, hay[book])
        if cov < PROV_THRESH:
            fail.append((sao, lop, cung, cov, book))
            continue

        # Đã có cùng quote (kể cả fv=-1 cũ) → skip; nếu fv=-1 khác quote thì vẫn insert mới
        exists = db.execute(
            "SELECT id, founder_verified FROM sao_noi_dung "
            "WHERE sao_vi=? AND lop=? AND ifnull(cung,'')=? AND quote_goc=?",
            (sao, lop, cung or "", quote),
        ).fetchone()
        if exists:
            skip.append((exists[0], sao, lop, cung, exists[1]))
            continue

        # Tránh trùng dich đã duyệt cùng ô
        dup = db.execute(
            "SELECT id FROM sao_noi_dung WHERE sao_vi=? AND lop=? AND ifnull(cung,'')=? "
            "AND founder_verified=1 AND dich_thuan_viet=?",
            (sao, lop, cung or "", dich),
        ).fetchone()
        if dup:
            skip.append((dup[0], sao, lop, cung, "dup-dich"))
            continue

        ok.append((sao, zh, lop, cung, quote, dich, book, loc, cov))

    print(f"provenance OK: {len(ok)}  skip: {len(skip)}  FAIL: {len(fail)}")
    for s, lop, cung, cov, book in fail:
        print(f"  FAIL cov={cov:.2f} {s} {lop} {cung} @ {book}")
    for item in skip:
        print(f"  skip {item}")

    if not args.commit:
        print("\nDRY-RUN — sẽ insert:")
        for r in ok:
            print(f"  + {r[0]} {r[2]} {r[3]} cov={r[8]:.2f} ← {r[6]}")
        print("Chạy lại với --commit để ghi.")
        return 1 if fail else 0

    cur = db.cursor()
    for sao, zh, lop, cung, quote, dich, book, loc, cov in ok:
        cur.execute(
            """INSERT INTO sao_noi_dung
               (sao_vi, sao_zh, concept_id, lop, cung, quote_goc, ngon_ngu,
                dich_thuan_viet, nguon_book, nguon_loc, founder_verified, created_at)
               VALUES (?,?,NULL,?,?,?,?,?,?,?,?,?)""",
            (sao, zh, lop, cung, quote, "vi", dich, book, loc, 1, today),
        )
        print(f"  INSERT id={cur.lastrowid} {sao} {lop} {cung} cov={cov:.2f}")
    db.commit()
    db.close()
    print(f"Committed {len(ok)} rows → {DB}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
