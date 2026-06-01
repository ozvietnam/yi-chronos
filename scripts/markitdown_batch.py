#!/usr/bin/env python3
"""MarkItDown batch — extract text-layer 11 sách Việt fast path.

Pipeline: PDF (có text-layer) → MarkItDown → markdown sạch.
Không LLM, chỉ pure parsing → ~5-20s/sách.

Usage:
  python3 scripts/markitdown_batch.py

Output: data/restored_books/<book_id>/content.md
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# (book_id, pdf_path, ưu tiên Tổ sư/kinh điển)
BOOKS = [
    # ⭐⭐ Kinh điển lớn
    ("tu-thu-binh-giai", "thư viện sách/Tứ Thư Bình Giải.pdf"),
    ("tu-vi-dau-so-toan-thu-vn", "thư viện sách/Tu Vi dau so toan thu.pdf"),
    ("tam-thien-dich-so", "thư viện sách/Tam Thiên Dịch Số.pdf"),
    ("sach-tu-vi-vo-long", "thư viện sách/Sach Tu Vi vo long.pdf"),
    # ⭐ Kinh điển trung
    ("khong-minh-than-toan-384-que", "thư viện sách/KhongMinhThanToan 384Que.pdf"),
    ("hoang-lich", "thư viện sách/Hoàng lịch.pdf"),
    ("ha-do-trong-van-minh-dai-viet", "thư viện sách/Hà đồ trong văn minh đại việt.pdf"),
    ("dich-hoc-tinh-hoa-nguyen-duy-can", "thư viện sách/Dịch học tinh hoa Nguyễn Duy Cần.pdf"),
    ("chua-benh-theo-chu-dich", "thư viện sách/Chữa bệnh theo chu dịch.pdf"),
    # Chuyên đề
    ("lap-va-giai-tu-vi", "thư viện sách/Lap-va-giai-tu-vi.pdf"),
    ("lien-hoa-don", "thư viện sách/LIENHOADON.pdf"),
]


def main():
    from markitdown import MarkItDown
    md = MarkItDown()
    out_root = ROOT / "data" / "restored_books"

    print(f"📚 MarkItDown batch — {len(BOOKS)} sách Việt text-layer")
    print(f"📂 Output: {out_root}")
    print()

    total_start = time.time()
    summary = []

    for i, (book_id, pdf_rel) in enumerate(BOOKS, 1):
        pdf = ROOT / pdf_rel
        if not pdf.exists():
            print(f"[{i}/{len(BOOKS)}] ❌ MISSING: {pdf_rel}")
            summary.append({"book_id": book_id, "status": "missing", "pdf": pdf_rel})
            continue

        book_dir = out_root / book_id
        book_dir.mkdir(parents=True, exist_ok=True)
        out_md = book_dir / "content.md"

        print(f"[{i}/{len(BOOKS)}] {book_id}  ({pdf.stat().st_size/1024/1024:.1f}MB)")
        t0 = time.time()
        try:
            result = md.convert(str(pdf))
            content = result.text_content or ""
            out_md.write_text(content, encoding="utf-8")
            elapsed = time.time() - t0
            chars = len(content)
            # Sanity check
            quality = "✅"
            if chars < 1000:
                quality = "⚠️ THIN"
            elif chars < 100:
                quality = "❌ EMPTY"

            print(f"   {quality} {elapsed:.1f}s, {chars:,} chars → {out_md.relative_to(ROOT)}")

            manifest = {
                "book_id": book_id,
                "source_pdf": str(pdf_rel),
                "extractor": "markitdown",
                "elapsed_seconds": round(elapsed, 1),
                "chars": chars,
                "ts": time.time(),
            }
            (book_dir / "manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            summary.append({"book_id": book_id, "status": "ok", "chars": chars, "seconds": round(elapsed,1)})
        except Exception as e:
            print(f"   ❌ ERROR: {type(e).__name__}: {str(e)[:200]}")
            summary.append({"book_id": book_id, "status": "error", "error": str(e)[:300]})

    total_elapsed = time.time() - total_start
    print()
    print("═" * 70)
    print(f"DONE — {total_elapsed:.0f}s total ({total_elapsed/60:.1f}m)")
    ok = [s for s in summary if s.get("status") == "ok"]
    print(f"✅ Success: {len(ok)}/{len(BOOKS)}")
    print(f"📝 Total chars: {sum(s.get('chars',0) for s in ok):,}")
    print("═" * 70)
    for s in summary:
        if s.get("status") == "ok":
            print(f"  ✅ {s['book_id']:<40} {s['chars']:>10,} chars  {s['seconds']:>5}s")
        else:
            print(f"  ❌ {s['book_id']:<40} {s.get('error', s.get('status','?'))[:60]}")

    # Save summary
    summary_path = ROOT / "data" / "restored_books" / "markitdown_batch_summary.json"
    summary_path.write_text(json.dumps({
        "total_seconds": round(total_elapsed, 1),
        "books": summary,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSummary: {summary_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
