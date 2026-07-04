"""Vòng sao / phụ tinh — roster đầy đủ cho Thư viện Tử Vi (B4, Anh chốt 2026-07-03).

Nguồn = kho `sao_noi_dung` lớp 'def', CHỈ dòng đã DUYỆT ĐỐI KHÁNG (founder_verified=1):
quote gốc chứng minh có trong sách (provenance) + bản dịch không bịa ý (LLM đối kháng
qwen3-30b local). Pipeline: scripts/verify_sao_noi_dung.py.

Loại 14 chính tinh (đã có hồ sơ sâu ở ChinhTinhLibraryPanel) → panel này chỉ phụ/vòng
sao: vòng Bác Sĩ, vòng Thái Tuế (Tang Môn/Bạch Hổ…), lục sát (Kình/Đà/Hỏa/Linh/Không/
Kiếp), Lộc Tồn, Thiên Mã, Tứ Hóa, cát/hung tinh lẻ…

Iron #9 quote-or-silence: chỉ hiện cái đã duyệt + NGUỒN đích danh. Không có → không hiện.
"""
from __future__ import annotations

import sqlite3
from functools import lru_cache
from pathlib import Path

_WIKI_DB = "data/yi_wiki/wiki.sqlite3"

CHINH_TINH = frozenset({
    "Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh",
    "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng", "Thiên Lương",
    "Thất Sát", "Phá Quân",
})

# nguon_book (id kho) → nhãn nguồn thân thiện (attribution minh bạch).
_BOOK_LABEL = {
    "trung-chau-tu-vi-dau-so-2": "Trung Châu Tử Vi Đẩu Số",
    "tu-vi-dau-so-toan-thu-vu-tai-luc": "Tử Vi Đẩu Số Toàn Thư (Vũ Tài Lục)",
    "tu-vi-ham-so": "Tử Vi Hàm Số",
    "tuvifull-tu-vi-dau-so-tuong-te": "Tử Vi Đẩu Số Tường Tế",
    "tuvi-toan-thu-lht-zh": "Tử Vi Đẩu Số Toàn Thư (bản Hán)",
    "tuvifull-trung-chau-phai-tu-vi-dau-so-dao-tao-sau-giao-trinh-ha-conve": "Trung Châu phái (giáo trình)",
    "tuvifull-luan-giai-cac-chinh-tinh": "Luận giải các chính tinh",
    "tu-vi-nghiem-ly-toan-thu-thien-luong": "Nghiệm Lý Toàn Thư (Thiên Lương)",
    "tuvi-dao-tang-zh": "Tử Vi Đạo Tạng (Hán)",
    "tuvifull-tuvidausotoanthu-ban-full-dich": "Tử Vi Đẩu Số Toàn Thư (bản dịch)",
    "can-chi-thong-luan": "Can Chi Thống Luận",
}

_DISCLAIMER = (
    "Vòng sao/phụ tinh là 'gia vị' — chỉ có nghĩa đầy đủ khi ghép với chính tinh trên "
    "cung. Nội dung dưới đây đã qua duyệt đối kháng (quote có trong sách + dịch không "
    "bịa ý), kèm nguồn đích danh; phần chưa đủ nguồn để trống, KHÔNG suy đoán."
)


def _book_label(b: str) -> str:
    return _BOOK_LABEL.get(b, (b or "").replace("tuvifull-", "").replace("-", " "))


@lru_cache(maxsize=1)
def _db() -> "sqlite3.Connection | None":
    p = Path(_WIKI_DB)
    if not p.exists():
        return None
    try:
        return sqlite3.connect(f"file:{p}?mode=ro", uri=True, check_same_thread=False)
    except Exception:
        return None


def _words(s: str) -> set:
    import re
    return set(re.sub(r"[^\w\s]", " ", (s or "").lower()).split())


def _dedup_add(bucket: list, seen: list, dich: str, quote: str, book: str, cap: int, *, cung: str | None = None) -> bool:
    """Thêm 1 trích vào bucket nếu chưa TRÙNG nội dung (overlap>0.6) và chưa đầy cap."""
    if len(bucket) >= cap:
        return False
    w = _words(dich)
    if any(len(w & ws) / max(1, min(len(w), len(ws))) > 0.6 for ws in seen):
        return False
    seen.append(w)
    item = {"dich": dich, "quote_goc": (quote or "").strip(), "nguon": _book_label(book)}
    if cung is not None:
        item["cung"] = cung
    bucket.append(item)
    return True


def list_vong_sao(*, per_star: int = 4, per_star_cung: int = 16, per_star_ket_hop: int = 6) -> dict:
    """Roster phụ/vòng sao có nội dung ĐÃ DUYỆT, gộp 3 lớp: def (định nghĩa chung),
    cung (nghĩa theo TỪNG cung an — cột `cung`), ket_hop (nghĩa khi kết hợp sao khác).
    Mỗi lớp dedup theo overlap nội dung (>0.6 coi là trùng) + cap riêng."""
    conn = _db()
    if conn is None:
        return {"stars": [], "total": 0, "disclaimer": _DISCLAIMER}
    try:
        rows = conn.execute(
            """SELECT sao_vi, sao_zh, lop, cung, quote_goc, dich_thuan_viet, nguon_book
               FROM sao_noi_dung
               WHERE lop IN ('def', 'cung', 'ket_hop') AND founder_verified=1
               ORDER BY sao_vi, lop, length(dich_thuan_viet) DESC""",
        ).fetchall()
    except Exception:
        return {"stars": [], "total": 0, "disclaimer": _DISCLAIMER}

    by_sao: dict[str, dict] = {}
    seen_words: dict[str, dict[str, list]] = {}
    for sao_vi, sao_zh, lop, cung, quote, dich, book in rows:
        if sao_vi in CHINH_TINH:                 # chính tinh có panel riêng → bỏ khỏi vòng sao
            continue
        dich = (dich or "").strip()
        if not dich:
            continue
        entry = by_sao.setdefault(sao_vi, {
            "sao_vi": sao_vi, "sao_zh": sao_zh or "",
            "items": [], "cung_items": [], "ket_hop_items": [],
        })
        seen = seen_words.setdefault(sao_vi, {"def": [], "cung": [], "ket_hop": []})
        if lop == "def":
            _dedup_add(entry["items"], seen["def"], dich, quote, book, per_star)
        elif lop == "cung":
            _dedup_add(entry["cung_items"], seen["cung"], dich, quote, book, per_star_cung, cung=cung)
        elif lop == "ket_hop":
            _dedup_add(entry["ket_hop_items"], seen["ket_hop"], dich, quote, book, per_star_ket_hop)

    stars = [s for s in by_sao.values() if s["items"] or s["cung_items"] or s["ket_hop_items"]]
    stars.sort(key=lambda s: s["sao_vi"])
    return {
        "stars": stars,
        "total": len(stars),
        "disclaimer": _DISCLAIMER,
    }
