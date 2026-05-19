"""Run layout detection trên 5 trang đầu Q3 source PDF.

Output:
    data/yi_publishing_test/p001-layout.json ... p005-layout.json
    data/yi_publishing_test/p001-overlay.png ... p005-overlay.png
    data/yi_publishing_test/SUMMARY.md
"""
from __future__ import annotations
import logging
import sys
import time
from pathlib import Path
from collections import Counter

logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(message)s')

# Suppress noisy HF logs
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.yi_publishing.layout_detector_pymupdf import detect_page
from engine.yi_publishing.visualize import make_overlay_png

SRC = "/Users/ozvietnamdesktop/Desktop/yi/thư viện sách/thieukhangtiet/图解梅花易数.pdf"
OUT_DIR = Path("data/yi_publishing_test")
OUT_DIR.mkdir(parents=True, exist_ok=True)

PAGES = [1, 2, 3, 4, 5]

print(f"=== Layout detection — 5 trang đầu Q3 source ===")
print(f"Source: {SRC}")
print(f"Output: {OUT_DIR}/")
print(f"Pages: {PAGES}\n")

results = []
for page_num in PAGES:
    print(f"\n--- Page {page_num} ---")
    t0 = time.time()
    try:
        layout = detect_page(
            pdf_path=SRC,
            page_num=page_num,
            book_id="thieu-khang-tiet-tq",
            page_image=f"pages/p{page_num:04d}.png",
        )
        elapsed = time.time() - t0

        # Save JSON
        json_path = OUT_DIR / f"p{page_num:03d}-layout.json"
        layout.save(json_path)

        # Save overlay PNG
        png_path = OUT_DIR / f"p{page_num:03d}-overlay.png"
        try:
            make_overlay_png(SRC, layout, png_path, dpi=120)
            png_ok = True
        except Exception as e:
            print(f"  Overlay error: {e}")
            png_ok = False

        # Stats
        types = Counter(r.type.value for r in layout.regions)
        print(f"  Regions: {len(layout.regions)} | Template: {layout.layout_template}")
        print(f"  Types: {dict(types)}")
        print(f"  Confidence: {layout.layout_confidence.value} ({layout.layout_confidence_score:.2f})")
        print(f"  JSON: {json_path.name} ({json_path.stat().st_size} bytes)")
        if png_ok:
            print(f"  Overlay: {png_path.name} ({png_path.stat().st_size//1024} KB)")
        print(f"  Time: {elapsed:.1f}s")

        results.append({
            'page': page_num,
            'regions': len(layout.regions),
            'types': dict(types),
            'template': layout.layout_template,
            'confidence': layout.layout_confidence.value,
            'score': layout.layout_confidence_score,
            'elapsed': elapsed,
            'json': str(json_path),
            'png': str(png_path) if png_ok else None,
        })
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        results.append({'page': page_num, 'error': str(e)})

# Summary
print(f"\n\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"{'Page':<6} {'Regions':<10} {'Template':<15} {'Conf':<8} {'Time':<8}")
for r in results:
    if 'error' in r:
        print(f"{r['page']:<6} ERROR: {r['error'][:60]}")
    else:
        print(f"{r['page']:<6} {r['regions']:<10} {r['template']:<15} "
              f"{r['confidence']:<8} {r['elapsed']:.1f}s")

# Write summary markdown
import json as jsonlib
with open(OUT_DIR / "SUMMARY.md", "w") as f:
    f.write("# Layout Detection — 5 trang đầu Q3\n\n")
    f.write(f"**Engine:** unstructured.partition_pdf (hi_res, chi_sim+eng)\n")
    f.write(f"**Source:** `{SRC}`\n\n")
    f.write("## Per-page results\n\n")
    f.write("| Page | Regions | Template | Confidence | Time | JSON | Overlay |\n")
    f.write("|------|---------|----------|------------|------|------|---------|\n")
    for r in results:
        if 'error' in r:
            f.write(f"| {r['page']} | ERROR | — | — | — | — | — |\n")
        else:
            json_link = f"`p{r['page']:03d}-layout.json`"
            png_link = f"`p{r['page']:03d}-overlay.png`" if r['png'] else "—"
            f.write(f"| {r['page']} | {r['regions']} | {r['template']} | "
                    f"{r['confidence']} ({r['score']:.2f}) | {r['elapsed']:.1f}s | "
                    f"{json_link} | {png_link} |\n")
    f.write("\n## Region types per page\n\n")
    for r in results:
        if 'error' not in r:
            f.write(f"**Page {r['page']}:** {r['types']}\n\n")

print(f"\nSummary: {OUT_DIR}/SUMMARY.md")
print(f"All files:")
for p in sorted(OUT_DIR.iterdir()):
    print(f"  {p.name} ({p.stat().st_size//1024 if p.stat().st_size>1024 else p.stat().st_size} {'KB' if p.stat().st_size>1024 else 'B'})")
