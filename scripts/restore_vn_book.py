#!/usr/bin/env python3
"""Phục chế sách Việt môn Đông phương (Tứ Trụ, Tử Vi, Bát Tự).

Pipeline:
  PDF scan → pdf2image → Tesseract VN OCR → Gemma 4 cleanup → markdown

Yêu cầu:
  - tesseract + ngôn ngữ vie installed
  - poppler installed (pdf2image dependency)
  - LM Studio chạy localhost:1234 với gemma-4-e4b loaded

Usage:
  python3 scripts/restore_vn_book.py \
    --pdf "thư viện sách/Du Bao Theo Tu Binh.pdf" \
    --book-id du-bao-theo-tu-binh \
    --start 1 --end 424 \
    [--concurrency 3] [--dpi 200]

Output:
  data/restored_books/<book_id>/
    pages/p001.md, p002.md, ...  (per-page markdown đã cleanup)
    pages/p001.raw.txt           (raw Tesseract output)
    content.md                   (concat full book)
    manifest.json                (per-page metadata: timing, char counts, errors)
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


SYS_PROMPT = """Bạn là biên tập viên sách Đông phương học (Tử Vi, Bát Tự, Tứ Trụ, Mai Hoa, Kinh Dịch).

Nhiệm vụ: NHẬN bản OCR Tesseract thô tiếng Việt, TRẢ về MARKDOWN sạch để xuất bản.

QUY TẮC TUYỆT ĐỐI:
1. STRIP toàn bộ watermark, số trang đơn lẻ, header/footer lặp lại ("chan X tru Y.pdf", "BAT TU", v.v.)
2. SỬA typo OCR rõ ràng:
   - "kìm" / "kĩm" → "kim"
   - "hoả" → "hỏa"
   - "thuỷ" → "thủy"
   - dấu thanh nhầm vị trí (vd: "vịêc" → "việc")
   - chữ Việt thiếu dấu (nếu rõ ngữ cảnh)
3. GIỮ NGUYÊN văn — KHÔNG diễn lại, KHÔNG thêm nghĩa, KHÔNG dịch
4. THUẬT NGỮ Đông phương phải CHUẨN CHÍNH TẢ:
   - Ngũ Hành (Mộc, Hỏa, Thổ, Kim, Thủy)
   - Thiên Can (Giáp, Ất, Bính, Đinh, Mậu, Kỷ, Canh, Tân, Nhâm, Quý)
   - Địa Chi (Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi)
   - Tứ Trụ, Bát Tự, Nhật Chủ, Đại Vận, Tiểu Hạn, Lưu Niên
   - Tử Vi, Thiên Phủ, Vũ Khúc, Liêm Trinh, Thái Dương, Thái Âm, Tham Lang, Cự Môn, Thiên Tướng, Thiên Lương, Thất Sát, Phá Quân
   - Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ
   - Tả Phụ, Hữu Bật, Văn Xương, Văn Khúc
   - 12 cung: Mệnh, Phụ Mẫu, Phúc Đức, Điền Trạch, Quan Lộc, Nô Bộc, Thiên Di, Tật Ách, Tài Bạch, Tử Tức, Phu Thê, Huynh Đệ
5. REFLOW đoạn — line OCR bị xuống dòng giữa câu thì nối lại
6. DIAGRAM noise (chữ trong vòng tròn ngũ hành đọc loạn) → thay bằng `[Sơ đồ X]`
7. BẢNG (table) → giữ ở dạng markdown table nếu detect được
8. HEADERS markdown:
   - `## Tiêu đề chương lớn` (cấp 2)
   - `### Tiêu đề mục` (cấp 3)
   - `**Tên hành/chính tinh in đậm**` cho danh sách
9. Output CHỈ markdown sạch — KHÔNG comment, KHÔNG meta như "Đây là bản cleanup..."
10. Nếu trang TRỐNG hoặc chỉ có 1-2 dòng vô nghĩa → output `<!-- trang trống -->`
"""


def pdf_to_pngs(pdf_path: Path, out_dir: Path, start: int, end: int, dpi: int = 200) -> list[Path]:
    """Convert PDF pages to PNGs. Returns list of png paths in order."""
    from pdf2image import convert_from_path
    out_dir.mkdir(parents=True, exist_ok=True)
    pages = convert_from_path(
        str(pdf_path),
        dpi=dpi,
        first_page=start,
        last_page=end,
        output_folder=str(out_dir),
        output_file="p",
        fmt="png",
        paths_only=True,
    )
    return [Path(p) for p in pages]


def tesseract_ocr(png_path: Path, lang: str = "vie") -> str:
    """Run Tesseract OCR on a PNG. macOS bug workaround: cd into dir."""
    cwd = png_path.parent
    rel = png_path.name
    out_base = png_path.with_suffix("")  # /tmp/x/p0001-022
    try:
        subprocess.run(
            ["tesseract", rel, str(out_base.name), "-l", lang, "--psm", "6"],
            cwd=cwd,
            check=True,
            capture_output=True,
            timeout=60,
        )
        txt_path = out_base.with_suffix(".txt")
        if txt_path.exists():
            return txt_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  Tesseract error on {png_path.name}: {e}", file=sys.stderr)
    return ""


def gemma_cleanup(raw_ocr: str, client, model: str, page_num: int) -> tuple[str, float]:
    """Send raw OCR to Gemma → cleaned markdown. Returns (markdown, elapsed_s)."""
    if not raw_ocr.strip() or len(raw_ocr.strip()) < 30:
        return "<!-- trang trống -->", 0.0
    t0 = time.time()
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYS_PROMPT},
                {"role": "user", "content": f"OCR thô trang {page_num}:\n\n{raw_ocr}\n\n→ Markdown sạch:"},
            ],
            temperature=0.1,
            max_tokens=3000,
            timeout=180,
        )
        return (r.choices[0].message.content or "").strip(), time.time() - t0
    except Exception as e:
        return f"<!-- ERROR cleanup p{page_num}: {e} -->\n\n{raw_ocr}", time.time() - t0


def process_page(idx: int, png_path: Path, page_num: int, out_dir: Path, client, model: str) -> dict:
    """Process 1 page: Tesseract → Gemma cleanup → write markdown."""
    t0 = time.time()
    raw = tesseract_ocr(png_path)
    t_ocr = time.time() - t0

    raw_path = out_dir / f"p{page_num:04d}.raw.txt"
    raw_path.write_text(raw, encoding="utf-8")

    cleaned, t_clean = gemma_cleanup(raw, client, model, page_num)
    md_path = out_dir / f"p{page_num:04d}.md"
    md_path.write_text(f"<!-- page {page_num} -->\n\n{cleaned}\n", encoding="utf-8")

    return {
        "page": page_num,
        "ocr_seconds": round(t_ocr, 2),
        "cleanup_seconds": round(t_clean, 2),
        "raw_chars": len(raw),
        "cleaned_chars": len(cleaned),
        "md_path": str(md_path.relative_to(out_dir.parent.parent)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True, help="Path to source PDF")
    ap.add_argument("--book-id", required=True, help="Slug for output folder")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=10)
    ap.add_argument("--concurrency", type=int, default=2,
                    help="Concurrent Gemma cleanups (LM Studio handles 1 at time well)")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--lm-url", default="http://localhost:1234/v1")
    ap.add_argument("--model", default="google/gemma-4-e4b")
    ap.add_argument("--out-root", default="data/restored_books")
    args = ap.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        sys.exit(f"PDF not found: {pdf_path}")

    book_dir = ROOT / args.out_root / args.book_id
    pages_dir = book_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    tmp_png_dir = Path(f"/tmp/restore-{args.book_id}")
    tmp_png_dir.mkdir(parents=True, exist_ok=True)

    from openai import OpenAI
    client = OpenAI(base_url=args.lm_url, api_key="lm-studio")

    print(f"📖 Book: {args.book_id}")
    print(f"📄 Pages: {args.start}-{args.end} ({args.end-args.start+1} pages)")
    print(f"🤖 Model: {args.model}")
    print(f"⚡ Concurrency: {args.concurrency}")
    print(f"📂 Output: {book_dir}")
    print()

    print("Stage 1: Extract PNGs...")
    t0 = time.time()
    png_paths = pdf_to_pngs(pdf_path, tmp_png_dir, args.start, args.end, args.dpi)
    print(f"  ✓ {len(png_paths)} PNGs in {time.time()-t0:.1f}s")
    print()

    print("Stage 2: OCR + Gemma cleanup (parallel)...")
    t_batch_start = time.time()
    results = []
    page_nums = list(range(args.start, args.start + len(png_paths)))

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futures = {
            ex.submit(process_page, i, png_paths[i], page_nums[i], pages_dir, client, args.model): page_nums[i]
            for i in range(len(png_paths))
        }
        for fut in concurrent.futures.as_completed(futures):
            pn = futures[fut]
            try:
                r = fut.result()
                results.append(r)
                elapsed_total = time.time() - t_batch_start
                done = len(results)
                rate = done / elapsed_total if elapsed_total > 0 else 0
                eta = (len(png_paths) - done) / rate if rate > 0 else 0
                print(f"  ✓ p{pn:04d}: OCR={r['ocr_seconds']}s, cleanup={r['cleanup_seconds']}s, "
                      f"{r['raw_chars']}→{r['cleaned_chars']} chars  "
                      f"[{done}/{len(png_paths)} done, ETA {eta/60:.1f}m]")
            except Exception as e:
                print(f"  ✗ p{pn:04d} FAIL: {e}")
                results.append({"page": pn, "error": str(e)})

    total_elapsed = time.time() - t_batch_start
    print()
    print(f"Stage 3: Compile content.md...")
    results.sort(key=lambda r: r.get("page", 0))
    content = [f"# {args.book_id}\n\n_Phục chế từ {pdf_path.name}, p{args.start}-{args.end}_\n\n---\n"]
    for r in results:
        if r.get("error"):
            continue
        md_path = pages_dir / f"p{r['page']:04d}.md"
        if md_path.exists():
            content.append(md_path.read_text(encoding="utf-8"))
            content.append("\n\n---\n\n")
    (book_dir / "content.md").write_text("\n".join(content), encoding="utf-8")
    print(f"  ✓ content.md written")

    manifest = {
        "book_id": args.book_id,
        "source_pdf": str(pdf_path),
        "page_range": [args.start, args.end],
        "total_pages": len(png_paths),
        "total_seconds": round(total_elapsed, 1),
        "model": args.model,
        "dpi": args.dpi,
        "concurrency": args.concurrency,
        "pages": results,
    }
    (book_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ manifest.json written")
    print()
    print(f"✅ DONE in {total_elapsed/60:.1f} min ({total_elapsed/len(png_paths):.1f}s/page avg)")
    print(f"   Total chars: {sum(r.get('cleaned_chars',0) for r in results):,}")

    # Cleanup tmp PNGs (keep small footprint)
    if args.end - args.start > 10:
        shutil.rmtree(tmp_png_dir, ignore_errors=True)
        print(f"   Cleaned tmp PNGs")


if __name__ == "__main__":
    main()
