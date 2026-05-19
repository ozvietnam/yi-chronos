"""Run vision-based layout detection trên 5 trang đầu Q3 source PDF.

Pipeline:
    1. Render PDF page → PNG (200 DPI)
    2. qwen2.5vl detect regions → JSON
    3. Save layout JSON + overlay PNG
"""
from __future__ import annotations
import logging
import sys
import time
from pathlib import Path
from collections import Counter

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logging.getLogger("urllib3").setLevel(logging.ERROR)

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.yi_publishing.layout_detector_vision import detect_page_vision
from engine.yi_publishing.visualize import render_page_to_image, draw_overlay

SRC = "/Users/ozvietnamdesktop/Desktop/yi/thư viện sách/thieukhangtiet/图解梅花易数.pdf"
OUT_DIR = Path("data/yi_publishing_test_vision")
OUT_DIR.mkdir(parents=True, exist_ok=True)

PAGES = [1, 2, 3, 4, 5]

print(f"=== Vision Layout — 5 trang đầu Q3 ===")
print(f"Engine: qwen2.5vl:7b (local Ollama)")
print(f"Source: {SRC}")
print(f"Output: {OUT_DIR}/\n")

import fitz
doc = fitz.open(SRC)

results = []
for page_num in PAGES:
    print(f"\n--- Page {page_num} ---")
    t0 = time.time()
    try:
        # Render page → PNG (200 DPI for vision quality)
        page = doc[page_num - 1]
        pdf_width, pdf_height = page.rect.width, page.rect.height

        img_path = OUT_DIR / f"p{page_num:03d}-source.png"
        page_img = render_page_to_image(SRC, page_num, dpi=150)
        page_img.save(img_path, "PNG", optimize=True)
        print(f"  Source PNG: {img_path.name} ({img_path.stat().st_size//1024} KB, "
              f"{page_img.width}x{page_img.height})")

        # Detect layout via qwen-vl
        layout = detect_page_vision(
            image_path=img_path,
            page_num=page_num,
            book_id="thieu-khang-tiet-tq",
            page_width=pdf_width,
            page_height=pdf_height,
        )

        # Save JSON
        json_path = OUT_DIR / f"p{page_num:03d}-layout.json"
        layout.save(json_path)

        # Overlay
        overlay_path = OUT_DIR / f"p{page_num:03d}-overlay.png"
        overlay = draw_overlay(page_img, layout)
        overlay.save(overlay_path, "PNG", optimize=True)

        elapsed = time.time() - t0
        types = Counter(r.type.value for r in layout.regions)
        print(f"  Regions: {len(layout.regions)} | Template: {layout.layout_template}")
        print(f"  Types: {dict(types)}")
        for r in layout.regions[:8]:
            desc = r.image_description or ""
            print(f"    #{r.reading_order} [{r.type.value:15s}] "
                  f"bbox=({r.bbox[0]:.0f},{r.bbox[1]:.0f},{r.bbox[2]:.0f},{r.bbox[3]:.0f}) "
                  f"{desc[:50]}")
        print(f"  Overlay: {overlay_path.name}")
        print(f"  Time: {elapsed:.1f}s")

        results.append({
            'page': page_num,
            'regions': len(layout.regions),
            'types': dict(types),
            'template': layout.layout_template,
            'elapsed': elapsed,
        })
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        results.append({'page': page_num, 'error': str(e)})

doc.close()

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"{'Page':<6} {'Regions':<10} {'Template':<15} {'Time':<8}")
for r in results:
    if 'error' in r:
        print(f"{r['page']:<6} ERROR: {r['error'][:60]}")
    else:
        print(f"{r['page']:<6} {r['regions']:<10} {r['template']:<15} {r['elapsed']:.1f}s")
print(f"\nFiles: {OUT_DIR}/")
for p in sorted(OUT_DIR.iterdir()):
    sz = p.stat().st_size
    print(f"  {p.name} ({sz//1024 if sz>1024 else sz} {'KB' if sz>1024 else 'B'})")
