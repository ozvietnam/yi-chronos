"""Probe MarkItDown capabilities trên thư viện sách."""
from markitdown import MarkItDown
import time
import subprocess
from pathlib import Path

md = MarkItDown()
print(f"MarkItDown initialized")
print()

# Test 1: Scanned PDF
scanned_pdf = "/Users/ozvietnamdesktop/Desktop/yi/thư viện sách/Kinh Dich Tron Bo - Ngo Tat To.pdf"
print("=== Test 1: Scanned PDF (no text layer expected) ===")
t0 = time.time()
try:
    result = md.convert(scanned_pdf)
    dt = time.time() - t0
    text = (result.text_content or "").strip()
    print(f"  Duration: {dt:.1f}s")
    print(f"  Text length: {len(text)} chars")
    if text:
        print(f"  Preview (200 chars): \"{text[:200]}\"")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {str(e)[:200]}")
print()

# Test 2: Find PDFs có text layer
print("=== Test 2: Probe text layer cross thư viện ===")
lib = Path("/Users/ozvietnamdesktop/Desktop/yi/thư viện sách")
all_pdfs = sorted(lib.glob("*.pdf"))
text_pdfs = []
for pdf in all_pdfs:
    try:
        r = subprocess.run(
            ["pdftotext", "-l", "3", str(pdf), "-"],
            capture_output=True, text=True, timeout=10,
        )
        text_chars = len(r.stdout.strip())
        if text_chars > 200:
            text_pdfs.append((pdf, text_chars))
    except Exception:
        pass
text_pdfs.sort(key=lambda x: -x[1])
print(f"  Total PDFs: {len(all_pdfs)}")
print(f"  Có text layer: {len(text_pdfs)}")
print()
print("  Top 5 có nhiều text:")
for p, l in text_pdfs[:5]:
    print(f"    {l:6d} chars/3pg  {p.name[:55]}")

if text_pdfs:
    p = text_pdfs[0][0]
    print()
    print(f"  MarkItDown trên: {p.name[:55]}")
    t0 = time.time()
    try:
        result = md.convert(str(p))
        dt = time.time() - t0
        text = (result.text_content or "").strip()
        print(f"    Duration: {dt:.1f}s")
        print(f"    Text length: {len(text)} chars")
        print(f"    Preview (500 chars):")
        for line in text[:500].splitlines()[:10]:
            print(f"      | {line[:90]}")
    except Exception as e:
        print(f"    ERROR: {type(e).__name__}: {str(e)[:200]}")
