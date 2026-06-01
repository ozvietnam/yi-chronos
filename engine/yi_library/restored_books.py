"""Restored Books library — đọc các sách Việt đã phục chế qua OCR/MarkItDown.

Pipeline upstream:
- scripts/restore_vn_book.py — Tesseract + Gemma cho PDF scan
- scripts/markitdown_batch.py — MarkItDown cho PDF có text-layer

Output structure:
  data/restored_books/<book_id>/
    content.md              (full concatenated markdown)
    manifest.json           (book_id, source_pdf, total_pages, ...)
    pages/p001.md, p001.raw.txt, ...  (per-page, optional — không vào image)

Production VPS: volume mount có thể shadow data/. Fallback embedded_data/restored_books/
được COPY vào image qua Dockerfile.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _resolve_library_root() -> Path:
    """Resolve restored_books folder. Prefer mounted data/, fallback embedded_data/."""
    primary = _PROJECT_ROOT / "data" / "restored_books"
    # Heuristic: nếu có ít nhất 1 manifest.json hoặc 1 content.md
    if primary.exists() and any(primary.glob("*/manifest.json")) or any(primary.glob("*/content.md")):
        return primary
    embedded = _PROJECT_ROOT / "embedded_data" / "restored_books"
    if embedded.exists():
        return embedded
    return primary


# Display labels — known book_id → human title (Tiếng Việt)
# Nếu book_id không có ở đây, fallback dùng book_id slug → titlecase.
BOOK_TITLES = {
    # Đêm 30/5 + sáng 31/5 batch
    "du-doan-tu-tru-thieu-vy-hoa": "Dự đoán theo Tứ Trụ — Thiệu Vỹ Hoa (bản đẹp)",
    "tu-xem-van-menh-theo-tu-tru": "Tự xem vận mệnh theo Tứ Trụ",
    "nguyen-ly-chon-ngay-theo-bat-tu-ha-lac": "Nguyên lý chọn ngày theo Bát Tự Hà Lạc",
    "chu-dich-du-doan-cac-vi-du-co-giai-thieu-vi-hoa": "Chu Dịch Dự Đoán Các Ví Dụ Có Giải — Thiệu Vĩ Hoa",
    "du-bao-theo-tu-binh": "Dự Báo Theo Tử Bình",
    "chu-dich-voi-du-doan-hoc": "Chu Dịch với Dự Đoán Học",
    # Stage A MarkItDown
    "tu-thu-binh-giai": "Tứ Thư Bình Giải",
    "tu-vi-dau-so-toan-thu-vn": "Tử Vi Đẩu Số Toàn Thư (VN — Vũ Tài Lục)",
    "tam-thien-dich-so": "Tam Thiên Dịch Số",
    "sach-tu-vi-vo-long": "Sách Tử Vi Vô Lông",
    "khong-minh-than-toan-384-que": "Khổng Minh Thần Toán — 384 Quẻ",
    "hoang-lich": "Hoàng Lịch",
    "ha-do-trong-van-minh-dai-viet": "Hà Đồ trong Văn Minh Đại Việt",
    "dich-hoc-tinh-hoa-nguyen-duy-can": "Dịch Học Tinh Hoa — Nguyễn Duy Cần",
    "chua-benh-theo-chu-dich": "Chữa Bệnh Theo Chu Dịch",
    "lap-va-giai-tu-vi": "Lập và Giải Tử Vi",
    "lien-hoa-don": "Liên Hoa Đốn",
    # Đêm 1 (queued)
    "trich-thien-tuy-binh-chu-nham-thiet-tieu": "Trích Thiên Tủy Bình Chú — Nhậm Thiết Tiều",
    "thien-nhan-hoc-co-dai-trich-thien-tuy": "Thiên Nhân Học Cổ Đại — Trích Thiên Tủy",
    "tu-vi-dau-so-toan-thu-vu-tai-luc": "Tử Vi Đẩu Số Toàn Thư — Vũ Tài Lục (OCR)",
    "tu-vi-nghiem-ly-toan-thu-thien-luong": "Tử Vi Nghiệm Lý Toàn Thư — Thiên Lương",
    "tang-san-boc-dich": "Tăng San Bốc Dịch",
    "tu-vi-ham-so": "Tử Vi Hàm Số",
    "boc-phe-chinh-tong": "Bốc Phệ Chính Tông",
    "bat-tu-ha-lac-va-quy-dao-doi-nguoi": "Bát Tự Hà Lạc và Quỹ Đạo Đời Người",
}

# Categories — for grouping in UI
BOOK_CATEGORIES = {
    "tu-thu-binh-giai": "Kinh Điển",
    "khong-minh-than-toan-384-que": "Bốc Phệ",
    "tang-san-boc-dich": "Bốc Phệ",
    "boc-phe-chinh-tong": "Bốc Phệ",
    "du-doan-tu-tru-thieu-vy-hoa": "Tứ Trụ — Bát Tự",
    "tu-xem-van-menh-theo-tu-tru": "Tứ Trụ — Bát Tự",
    "nguyen-ly-chon-ngay-theo-bat-tu-ha-lac": "Tứ Trụ — Bát Tự",
    "du-bao-theo-tu-binh": "Tứ Trụ — Bát Tự",
    "bat-tu-ha-lac-va-quy-dao-doi-nguoi": "Tứ Trụ — Bát Tự",
    "trich-thien-tuy-binh-chu-nham-thiet-tieu": "Tứ Trụ — Bát Tự",
    "thien-nhan-hoc-co-dai-trich-thien-tuy": "Tứ Trụ — Bát Tự",
    "tu-vi-dau-so-toan-thu-vn": "Tử Vi Đẩu Số",
    "tu-vi-dau-so-toan-thu-vu-tai-luc": "Tử Vi Đẩu Số",
    "tu-vi-nghiem-ly-toan-thu-thien-luong": "Tử Vi Đẩu Số",
    "tu-vi-ham-so": "Tử Vi Đẩu Số",
    "sach-tu-vi-vo-long": "Tử Vi Đẩu Số",
    "lap-va-giai-tu-vi": "Tử Vi Đẩu Số",
    "chu-dich-du-doan-cac-vi-du-co-giai-thieu-vi-hoa": "Chu Dịch — Dự Đoán",
    "chu-dich-voi-du-doan-hoc": "Chu Dịch — Dự Đoán",
    "dich-hoc-tinh-hoa-nguyen-duy-can": "Chu Dịch — Dự Đoán",
    "ha-do-trong-van-minh-dai-viet": "Chu Dịch — Dự Đoán",
    "tam-thien-dich-so": "Dịch Số",
    "lien-hoa-don": "Chuyên Đề",
    "chua-benh-theo-chu-dich": "Chuyên Đề",
    "hoang-lich": "Lịch — Phong Thuỷ",
}


def _slug_to_title(slug: str) -> str:
    parts = slug.replace("_", "-").split("-")
    return " ".join(p.capitalize() for p in parts)


def list_books() -> list[dict[str, Any]]:
    """List all restored books with metadata."""
    root = _resolve_library_root()
    if not root.exists():
        return []
    books = []
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        content = d / "content.md"
        if not content.exists():
            continue
        bid = d.name
        manifest_path = d / "manifest.json"
        manifest: dict[str, Any] = {}
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:
                manifest = {}
        chars = content.stat().st_size
        # Pages — from manifest hoặc count h2 headers
        if manifest.get("pages"):
            pages = manifest.get("total_pages") or len(manifest["pages"])
        elif manifest.get("page_range"):
            pages = manifest["page_range"][1] - manifest["page_range"][0] + 1
        else:
            # MarkItDown: no per-page split — estimate by char count / 2500
            pages = max(1, chars // 2500)
        books.append({
            "book_id": bid,
            "title": BOOK_TITLES.get(bid) or _slug_to_title(bid),
            "category": BOOK_CATEGORIES.get(bid) or "Khác",
            "source_pdf": manifest.get("source_pdf", ""),
            "extractor": manifest.get("extractor") or ("ocr+gemma" if manifest.get("model") else "markitdown"),
            "model": manifest.get("model", ""),
            "total_pages": pages,
            "chars": chars,
            "has_pages_split": (d / "pages").exists(),
            "restored_at": manifest.get("ts") or 0,
        })
    return books


def get_book_content(book_id: str, page: int | None = None) -> dict[str, Any]:
    """Get full content of a book, or just 1 page if specified."""
    root = _resolve_library_root()
    book_dir = root / book_id
    if not book_dir.exists():
        return {"status": "not_found", "reason": f"Book {book_id} not in library"}
    content_path = book_dir / "content.md"
    if not content_path.exists():
        return {"status": "not_found", "reason": f"No content.md for {book_id}"}

    if page:
        # Try per-page file
        pages_dir = book_dir / "pages"
        page_path = pages_dir / f"p{page:04d}.md"
        if page_path.exists():
            return {
                "status": "ok",
                "book_id": book_id,
                "title": BOOK_TITLES.get(book_id) or _slug_to_title(book_id),
                "page": page,
                "content_md": page_path.read_text(encoding="utf-8"),
            }
        return {"status": "not_found", "reason": f"Page {page} not split for {book_id}"}

    content = content_path.read_text(encoding="utf-8")
    return {
        "status": "ok",
        "book_id": book_id,
        "title": BOOK_TITLES.get(book_id) or _slug_to_title(book_id),
        "category": BOOK_CATEGORIES.get(book_id) or "Khác",
        "content_md": content,
        "chars": len(content),
    }


def search_books(query: str, max_results: int = 50) -> list[dict[str, Any]]:
    """Full-text search across all books. Returns snippets with context."""
    if not query or len(query.strip()) < 2:
        return []
    q = query.strip().lower()
    root = _resolve_library_root()
    results = []
    for book in list_books():
        bid = book["book_id"]
        content_path = root / bid / "content.md"
        if not content_path.exists():
            continue
        text = content_path.read_text(encoding="utf-8")
        text_lower = text.lower()
        idx = 0
        hits_for_book = 0
        while True:
            pos = text_lower.find(q, idx)
            if pos < 0:
                break
            start = max(0, pos - 100)
            end = min(len(text), pos + len(q) + 150)
            snippet = text[start:end].replace("\n", " ")
            results.append({
                "book_id": bid,
                "title": book["title"],
                "category": book["category"],
                "snippet": ("..." if start > 0 else "") + snippet + ("..." if end < len(text) else ""),
                "offset": pos,
            })
            idx = pos + len(q)
            hits_for_book += 1
            if hits_for_book >= 3:  # max 3 hits per book to avoid flooding
                break
            if len(results) >= max_results:
                break
        if len(results) >= max_results:
            break
    return results
