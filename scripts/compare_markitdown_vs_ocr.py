"""So sánh MarkItDown vs qwen-vl OCR cho Kinh Dịch — chất lượng + tốc độ."""
from markitdown import MarkItDown
from pathlib import Path
import re

pdf = "/Users/ozvietnamdesktop/Desktop/yi/thư viện sách/Kinh Dich Tron Bo - Ngo Tat To.pdf"
md = MarkItDown()
result = md.convert(pdf)
text = result.text_content or ""

# Split into "pages" — pdfminer separates pages with form feed \f
pages = text.split("\f")
print(f"Total chars: {len(text):,}")
print(f"Pages detected: {len(pages)}")
print()

# Show sample pages — same as we already OCR'd to compare
for pn in [5, 10, 15, 20, 25, 30, 50, 100]:
    if pn < len(pages):
        page_text = pages[pn].strip()
        print(f"=== Page {pn} (MarkItDown, {len(page_text)} chars) ===")
        # Strip excess whitespace + tabs (pdf-text often has weird spacing)
        cleaned = re.sub(r"\s+", " ", page_text)
        print(cleaned[:400])
        print()

# Test: text quality — diacritics ratio, Han characters present
import collections
ascii_chars = sum(1 for c in text if c.isascii())
total_chars = len(text)
ratio_ascii = ascii_chars / total_chars if total_chars else 0
print(f"=== Quality metrics ===")
print(f"Total chars: {total_chars:,}")
print(f"ASCII ratio: {ratio_ascii:.1%} (low = lots of Vietnamese/Han)")

# Sample diacritic chars
diacritics = [c for c in "áàảãạâấầẩẫậăắằẳẵặéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ" if c in text]
print(f"Diacritics found: {len(diacritics)}/{67}")

# Han chars (CJK Unified Ideographs)
han_chars = sum(1 for c in text if 0x4E00 <= ord(c) <= 0x9FFF)
print(f"Han characters: {han_chars}")

# Watermark detection
watermark = text.count("thuviensach.vn") + text.count("Sachvui.Com")
print(f"Watermark occurrences: {watermark}")
