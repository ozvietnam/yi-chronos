#!/usr/bin/env python3
"""OCR 8 sách CHƯA làm sạch — anh phát hiện trong audit 2026-06-02.

Pipeline: MarkItDown text-layer extract → fallback flag nếu chars < 1000
(sách scan ảnh cần Tesseract VN + qwen-vl, sẽ chạy sau).

8 sách target:
1. Kinh Dich Tron Bo - Ngo Tat To (CỐT — quẻ Dịch)
2. Học Thuyết Âm Dương Ngũ Hành - Lê Văn Sửu (CỐT — triết học gốc)
3. Trung Chau tu vi dau so 2 (Trung Châu phái Tử Vi)
4. DON TOAN THAN DIEU
5. phong-thuy-tam-quai-trach
6. Lac thu cuu tinh phong thuy nha o
7. 12 con giap theo lich van nien
8. chon viec theo lich am
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# 8 sách MISSING — đã verify gap
BOOKS = [
    ("kinh-dich-tron-bo-ngo-tat-to", "thư viện sách/Kinh Dich Tron Bo - Ngo Tat To.pdf", "⭐⭐ CỐT"),
    ("hoc-thuyet-am-duong-ngu-hanh-le-van-suu", "thư viện sách/Học Thuyết Âm Dương Ngũ Hành - Lê Văn Sửu.pdf", "⭐⭐ Triết học gốc"),
    ("trung-chau-tu-vi-dau-so-2", "thư viện sách/Trung Chau tu vi dau so 2.pdf", "⭐ Trung Châu phái"),
    ("don-toan-than-dieu", "thư viện sách/DON TOAN THAN DIEU.pdf", "?"),
    ("phong-thuy-tam-quai-trach", "thư viện sách/phong-thuy-tam-quai-trach.pdf", "Phong thủy 8 quái"),
    ("lac-thu-cuu-tinh-phong-thuy-nha-o", "thư viện sách/Lac thu cuu tinh phong thuy nha o.pdf", "Lạc Thư cửu tinh"),
    ("12-con-giap-theo-lich-van-nien", "thư viện sách/12 con giap theo lich van nien.pdf", "Lịch vạn niên"),
    ("chon-viec-theo-lich-am", "thư viện sách/chon viec theo lich am.pdf", "Chọn việc lịch âm"),
]


def main():
    from markitdown import MarkItDown
    md = MarkItDown()
    out_root = ROOT / "data" / "restored_books"
    print(f"📚 MarkItDown extract 8 sách thiếu")
    print()

    summary = []
    total_start = time.time()

    for i, (book_id, pdf_rel, note) in enumerate(BOOKS, 1):
        pdf = ROOT / pdf_rel
        if not pdf.exists():
            print(f"[{i}/8] ❌ MISSING PDF: {pdf_rel}")
            summary.append({"book_id": book_id, "status": "pdf_missing", "pdf": pdf_rel})
            continue

        book_dir = out_root / book_id
        book_dir.mkdir(parents=True, exist_ok=True)
        out_md = book_dir / "content.md"

        size_mb = pdf.stat().st_size / 1024 / 1024
        print(f"[{i}/8] {book_id}  ({size_mb:.1f}MB) {note}")
        t0 = time.time()

        try:
            result = md.convert(str(pdf))
            content = result.text_content or ""
            out_md.write_text(content, encoding="utf-8")
            elapsed = time.time() - t0
            chars = len(content)

            quality = "✅"
            needs_ocr = False
            if chars < 1000:
                quality = "⚠️ THIN — cần OCR ảnh sau"
                needs_ocr = True
            elif chars < 10000:
                quality = "🟡 SHORT"

            print(f"   {quality} {elapsed:.1f}s, {chars:,} chars")

            manifest = {
                "book_id": book_id,
                "source_pdf": pdf_rel,
                "note": note,
                "extractor": "markitdown",
                "elapsed_seconds": round(elapsed, 1),
                "chars": chars,
                "needs_ocr_image": needs_ocr,
                "ts": time.time(),
            }
            (book_dir / "manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            summary.append({"book_id": book_id, "status": "ok", "chars": chars, "needs_ocr": needs_ocr})
        except Exception as e:
            elapsed = time.time() - t0
            print(f"   ❌ FAILED: {str(e)[:150]}")
            summary.append({"book_id": book_id, "status": "error", "error": str(e)[:200]})

    total_elapsed = time.time() - total_start
    print()
    print(f"━━━ DONE in {total_elapsed:.1f}s ━━━")
    print(f"OK: {sum(1 for s in summary if s['status']=='ok')}")
    print(f"Need image OCR: {sum(1 for s in summary if s.get('needs_ocr'))}")
    print(f"Error: {sum(1 for s in summary if s['status']=='error')}")

    (out_root / "ocr_8_missing_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
