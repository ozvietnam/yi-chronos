#!/usr/bin/env python3
"""OCR sách "Học Thuyết Âm Dương Ngũ Hành - Lê Văn Sửu" (251 trang).

MarkItDown bị CID encoding hỏng → dùng Tesseract VN OCR ảnh.
Strategy: pdftoppm 300 DPI → png → tesseract -l vie → concat thành content.md.

Run: python3 scripts/ocr_le_van_suu.py [--max-pages N]
"""
from __future__ import annotations
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "thư viện sách" / "Học Thuyết Âm Dương Ngũ Hành - Lê Văn Sửu.pdf"
OUT_DIR = ROOT / "data" / "restored_books" / "hoc-thuyet-am-duong-ngu-hanh-le-van-suu"
TMP_DIR = ROOT / ".ocr_tmp_lvs"


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, **kw)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-pages", type=int, default=100,
                        help="Max pages to OCR (default 100 = phần lý luận cốt)")
    parser.add_argument("--start-page", type=int, default=1)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()

    if not PDF.exists():
        print(f"❌ PDF không tồn tại: {PDF}")
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    # Clean tmp
    for f in TMP_DIR.glob("*"):
        f.unlink()

    end = args.start_page + args.max_pages - 1
    print(f"📚 OCR sách Lê Văn Sửu — trang {args.start_page} → {end} ({args.max_pages} trang)")

    # Step 1: pdftoppm
    print(f"\n⏳ Step 1: pdftoppm convert PDF → PNG ({args.dpi} DPI)...")
    t0 = time.time()
    r = run([
        "pdftoppm", "-r", str(args.dpi), "-png",
        "-f", str(args.start_page), "-l", str(end),
        str(PDF), str(TMP_DIR / "page")
    ])
    if r.returncode != 0:
        print(f"❌ pdftoppm failed: {r.stderr[:200]}")
        return 1
    pngs = sorted(TMP_DIR.glob("page-*.png"))
    print(f"   ✅ {len(pngs)} pages in {time.time()-t0:.1f}s")

    # Step 2: OCR mỗi page (copy ra /tmp flat — tesseract issue với path có dấu)
    print(f"\n⏳ Step 2: Tesseract OCR tiếng Việt...")
    pages_text = []
    t0 = time.time()
    # Tesseract trên macOS có issue với /tmp/ → dùng cwd trong project
    work_dir = ROOT / ".ocr_work_lvs"
    work_dir.mkdir(exist_ok=True)
    for png in pngs:
        # Move png vào work_dir
        local_png = work_dir / png.name
        shutil.copy(png, local_png)
        out_base = png.stem
        # Run từ cwd=work_dir để tesseract đọc relative path
        r = subprocess.run(
            ["tesseract", png.name, out_base, "-l", "vie"],
            cwd=work_dir, capture_output=True,
        )
        txt_path = work_dir / f"{out_base}.txt"
        if txt_path.exists():
            text = txt_path.read_text(encoding="utf-8")
            page_num = int(png.stem.replace("page-", ""))
            pages_text.append((page_num, text))
            txt_path.unlink(missing_ok=True)
        local_png.unlink(missing_ok=True)
    print(f"   ✅ OCR {len(pages_text)} pages in {time.time()-t0:.1f}s")

    # Step 3: Combine
    print(f"\n⏳ Step 3: Combine + save content.md...")
    parts = []
    parts.append("# Học Thuyết Âm Dương Ngũ Hành — Lê Văn Sửu\n")
    parts.append(f"_(OCR Tesseract VN từ PDF, {args.max_pages} trang đầu — {args.dpi} DPI)_\n\n---\n")
    for num, text in pages_text:
        parts.append(f"\n<!-- page {num} -->\n")
        parts.append(text.strip())
        parts.append("\n")
    full = "\n".join(parts)
    out_md = OUT_DIR / "content.md"
    out_md.write_text(full, encoding="utf-8")
    print(f"   ✅ Saved: {out_md} ({len(full):,} chars)")

    # Update manifest
    import json
    manifest = {
        "book_id": "hoc-thuyet-am-duong-ngu-hanh-le-van-suu",
        "title": "Học Thuyết Âm Dương Ngũ Hành",
        "author": "Lê Văn Sửu",
        "source_pdf": str(PDF.relative_to(ROOT)),
        "extractor": "tesseract-vie-300dpi",
        "pages_total": 251,
        "pages_ocr": len(pages_text),
        "start_page": args.start_page,
        "end_page": end,
        "chars": len(full),
        "ts": time.time(),
    }
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"   ✅ Manifest updated")

    # Clean tmp
    shutil.rmtree(TMP_DIR, ignore_errors=True)
    shutil.rmtree(work_dir, ignore_errors=True)
    print(f"\n🎉 DONE!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
