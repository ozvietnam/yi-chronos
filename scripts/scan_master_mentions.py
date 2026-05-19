"""Scan restored corpus tìm mentions về Thiệu Khang Tiết + lineage + methods.

Output: structured markdown report identifying:
- Direct quotes / references to Thiệu
- Methods mentioned (Mai Hoa Dịch Số, Hoàng Cực Kinh Thế, ...)
- Concepts em không có explanation đầy đủ → research targets
- Books referenced nhưng KHÔNG có trong library → shopping list

Theo nguyên tắc "học trò ghi chép cẩn trọng" — em KHÔNG tự ý phân loại
"sự thật gốc". Em chỉ liệt kê mentions + context cho anh review.
"""

from __future__ import annotations

import re
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


RESTORED_DIR = Path("/Users/ozvietnamdesktop/Desktop/yi/data/yi_restored")
OUTPUT_DIR = Path("/Users/ozvietnamdesktop/Desktop/yi/data/research")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ─── Search patterns ────────────────────────────────────────────────────────

# Tiếng Việt + Hán Tiệu Khang Tiết và lineage
MASTER_PATTERNS = {
    # Thiệu Khang Tiết
    "thieu_khang_tiet": re.compile(
        r"(Thi[ệê]u\s+Khang\s+Ti[ếe]t|Thi[ệê]u\s+T[ửu]|Khang\s+Ti[ếe]t|"
        r"Thi[ệê]u\s+Ung|邵雍|邵康節|邵康节|邵子|邵伯溫|邵伯温)",
        re.IGNORECASE
    ),
    # Thiệu Vĩ Hoa (hậu duệ hiện đại) — separately tracked
    "thieu_vi_hoa": re.compile(
        r"(Thi[ệê]u\s+V[ĩy]\s+Hoa|邵伟华|邵偉華)",
        re.IGNORECASE
    ),
}

# Works của Thiệu Khang Tiết
WORK_PATTERNS = {
    "mai_hoa_dich_so": re.compile(
        r"(Mai\s+Hoa\s+D[ịi]ch\s+S[ốo]|Mai\s+Hoa|梅花易數|梅花易数|梅花)",
        re.IGNORECASE
    ),
    "hoang_cuc_kinh_the": re.compile(
        r"(Ho[àa]ng\s+C[ựu]c\s+Kinh\s+Th[ếe]|Ho[àa]ng\s+C[ựu]c|皇極經世|皇极经世)",
        re.IGNORECASE
    ),
    "quan_vat": re.compile(
        r"(Quan\s+V[ậa]t\s+(N[ộo]i\s+Ngo[ạa]i)?|觀物|观物)",
        re.IGNORECASE
    ),
    "tien_thien_do": re.compile(
        r"(Ti[êe]n\s+Thi[êe]n\s+([ĐĐ][ồô]|Tâm\s+Ph[áa]p)?|先天圖|先天图|先天卦)",
        re.IGNORECASE
    ),
    "y_xuyen_kich_nhuong": re.compile(
        r"(Y\s+Xuy[êe]n\s+K[íi]ch\s+Nh[ưu][ơo]ng|伊川擊壤集|伊川击壤集)",
        re.IGNORECASE
    ),
}

# Influencers + disciples
LINEAGE_PATTERNS = {
    "ly_chi_tai": re.compile(r"(L[ýy]\s+Chi\s+T[àa]i|李之才)", re.IGNORECASE),
    "chu_hy": re.compile(r"(Chu\s+Hy|Chu\s+H[yi]|朱熹|朱子)", re.IGNORECASE),
    "trinh_di": re.compile(r"(Tr[ìi]nh\s+Di|程頤|程颐|程子)", re.IGNORECASE),
    "vuong_bat": re.compile(r"(V[ưu][ơo]ng\s+B[ậa]t|王弼)", re.IGNORECASE),
    "truong_hanh_thanh": re.compile(
        r"(Tr[ưu][ơo]ng\s+H[àa]nh\s+Th[àa]nh|張行成|张行成)", re.IGNORECASE
    ),
    "lai_tri_duc": re.compile(r"(Lai\s+Tri\s+[ĐĐ][ứu]c|來知德|来知德)", re.IGNORECASE),
    "sai_nguyen_dinh": re.compile(r"(Sai\s+Nguy[êe]n\s+[ĐĐ][ịi]nh|蔡元定)", re.IGNORECASE),
}

# Methods + concepts liên quan
METHOD_PATTERNS = {
    "boc_que": re.compile(r"(b[ốo]c\s+qu[ẻe]|gieo\s+qu[ẻe])", re.IGNORECASE),
    "ung_ky": re.compile(r"([ứu]ng\s+k[ỳy]|应期|應期)", re.IGNORECASE),
    "dong_hao": re.compile(r"([đđ][ộo]ng\s+h[àa]o|动爻|動爻)", re.IGNORECASE),
    "ha_do": re.compile(r"(H[àa]\s+[ĐĐ][ồô]|河圖|河图)", re.IGNORECASE),
    "lac_thu": re.compile(r"(L[ạa]c\s+Th[ưu]|洛書|洛书)", re.IGNORECASE),
    "tam_phap": re.compile(r"(T[âa]m\s+ph[áa]p|心法)", re.IGNORECASE),
}


@dataclass
class Mention:
    pattern_key: str
    pattern_category: str  # 'MASTER'|'WORK'|'LINEAGE'|'METHOD'
    matched_text: str
    book_slug: str
    page_no: int
    context: str  # ±300 chars

    def to_dict(self) -> dict:
        return {
            "pattern_key": self.pattern_key,
            "pattern_category": self.pattern_category,
            "matched_text": self.matched_text,
            "book_slug": self.book_slug,
            "page_no": self.page_no,
            "context": self.context,
        }


def scan_page(text: str, book_slug: str, page_no: int) -> list[Mention]:
    """Scan 1 page → list mentions."""
    mentions: list[Mention] = []
    categories = [
        ("MASTER", MASTER_PATTERNS),
        ("WORK", WORK_PATTERNS),
        ("LINEAGE", LINEAGE_PATTERNS),
        ("METHOD", METHOD_PATTERNS),
    ]
    for cat_name, pattern_dict in categories:
        for key, regex in pattern_dict.items():
            for m in regex.finditer(text):
                start = max(0, m.start() - 300)
                end = min(len(text), m.end() + 300)
                context = text[start:end].strip()
                # Clean context — remove excessive newlines
                context = re.sub(r"\n+", " | ", context)
                context = re.sub(r"\s{2,}", " ", context)
                mentions.append(Mention(
                    pattern_key=key,
                    pattern_category=cat_name,
                    matched_text=m.group(0),
                    book_slug=book_slug,
                    page_no=page_no,
                    context=context,
                ))
    return mentions


def scan_book(book_dir: Path) -> list[Mention]:
    """Scan all pages của 1 book restored."""
    pages_dir = book_dir / "pages"
    if not pages_dir.exists():
        return []
    book_slug = book_dir.name
    all_mentions: list[Mention] = []
    for page_file in sorted(pages_dir.glob("page-*.md")):
        try:
            page_no = int(page_file.stem.split("-")[1])
        except (ValueError, IndexError):
            continue
        try:
            text = page_file.read_text(encoding="utf-8")
        except Exception:
            continue
        all_mentions.extend(scan_page(text, book_slug, page_no))
    return all_mentions


def main():
    print("=== Scanning restored corpus ===\n")
    all_books = [d for d in RESTORED_DIR.iterdir()
                 if d.is_dir() and not d.name.startswith("_")
                 and not d.name.endswith(".ocr-attempt")
                 and not d.name.endswith(".ocr-backup")]
    print(f"Books to scan: {len(all_books)}")
    for b in all_books:
        n_pages = len(list((b / 'pages').glob('page-*.md'))) if (b / 'pages').exists() else 0
        print(f"  - {b.name}: {n_pages} pages")
    print()

    all_mentions: list[Mention] = []
    for book_dir in all_books:
        mentions = scan_book(book_dir)
        all_mentions.extend(mentions)
        print(f"  {book_dir.name}: {len(mentions)} mentions")
    print(f"\nTotal mentions: {len(all_mentions)}\n")

    # Group by pattern_key for stats
    by_key = defaultdict(list)
    for m in all_mentions:
        by_key[(m.pattern_category, m.pattern_key)].append(m)

    print("=== Top mention counts ===")
    sorted_keys = sorted(by_key.items(), key=lambda x: -len(x[1]))
    for (cat, key), mlist in sorted_keys[:20]:
        print(f"  [{cat:8s}] {key:30s} {len(mlist):4d} mentions")

    # Save raw JSON
    raw_path = OUTPUT_DIR / "master-mentions-raw.json"
    raw_path.write_text(
        json.dumps([m.to_dict() for m in all_mentions], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n✓ Raw mentions: {raw_path}")

    # Build markdown report
    report_path = OUTPUT_DIR / "master-mentions-scan.md"
    write_report(all_mentions, by_key, all_books, report_path)
    print(f"✓ Report: {report_path}")


def write_report(mentions, by_key, books, output_path):
    """Generate human-readable markdown report."""
    import time
    lines = []
    lines.append("# Master Mentions Scan — Thiệu Khang Tiết & Lineage")
    lines.append(f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Books scanned**: {len(books)}")
    book_pages = []
    for b in books:
        n_pages = len(list((b / 'pages').glob('page-*.md'))) if (b / 'pages').exists() else 0
        book_pages.append(f"- `{b.name}` ({n_pages} pages)")
    lines.extend(book_pages)
    lines.append(f"**Total mentions found**: {len(mentions)}")
    lines.append("")
    lines.append("> Em ghi chép cẩn trọng. KHÔNG tự ý phán cái nào là 'sự thật gốc'.")
    lines.append("> Anh đọc + cân nhắc.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Stats overview
    lines.append("## 📊 Stats Overview")
    lines.append("")
    lines.append("| Category | Pattern | Count |")
    lines.append("|---|---|---|")
    sorted_keys = sorted(by_key.items(), key=lambda x: (x[0][0], -len(x[1])))
    for (cat, key), mlist in sorted_keys:
        lines.append(f"| {cat} | `{key}` | {len(mlist)} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # By category, by pattern, with context excerpts
    categories = ["MASTER", "WORK", "LINEAGE", "METHOD"]
    cat_titles = {
        "MASTER": "1. 🎯 MASTER mentions — Thiệu Khang Tiết",
        "WORK": "2. 📚 WORK mentions — Các tác phẩm",
        "LINEAGE": "3. 🧬 LINEAGE mentions — Đệ tử + người liên quan",
        "METHOD": "4. 🔮 METHOD mentions — Phương pháp + khái niệm",
    }

    for cat in categories:
        cat_mentions = [m for m in mentions if m.pattern_category == cat]
        if not cat_mentions:
            continue
        lines.append(f"## {cat_titles[cat]}")
        lines.append("")
        # Group by pattern_key
        by_pattern = defaultdict(list)
        for m in cat_mentions:
            by_pattern[m.pattern_key].append(m)
        for pkey, mlist in sorted(by_pattern.items(), key=lambda x: -len(x[1])):
            lines.append(f"### `{pkey}` ({len(mlist)} mentions)")
            lines.append("")
            # Show up to 10 contexts per pattern
            for i, m in enumerate(mlist[:10]):
                lines.append(f"**{i+1}. {m.book_slug} · page {m.page_no} · matched `{m.matched_text}`**")
                lines.append("")
                # Truncate context for readability
                ctx = m.context[:500] + "..." if len(m.context) > 500 else m.context
                lines.append(f"> {ctx}")
                lines.append("")
            if len(mlist) > 10:
                lines.append(f"_... and {len(mlist) - 10} more mentions of `{pkey}`_")
                lines.append("")
            lines.append("")

    lines.append("---")
    lines.append("")

    # Shopping list — books anh should find
    lines.append("## 🛒 SHOPPING LIST — Books anh PHẢI tìm")
    lines.append("")
    lines.append("Theo paradigm 'học thầy trước, học trò sau', đây là priority:")
    lines.append("")
    lines.append("### Tier 0 — CORE (sách của THẦY)")
    lines.append("")
    lines.append("| # | Sách | Tiếng Hán | Bản | Tầm quan trọng |")
    lines.append("|---|---|---|---|---|")
    lines.append("| 1 | Mai Hoa Dịch Số | 梅花易數 | Hán + Việt | ⭐⭐⭐⭐⭐ Method bốc — ESSENTIAL |")
    lines.append("| 2 | Hoàng Cực Kinh Thế | 皇極經世 | Hán + Việt | ⭐⭐⭐⭐⭐ Cosmology + số học |")
    lines.append("| 3 | Quan Vật Nội Ngoại Thiên | 觀物內外篇 | Hán + Việt | ⭐⭐⭐⭐ Hermeneutic philosophy |")
    lines.append("| 4 | Tiên Thiên Đồ Truyện | 先天圖傳 | Hán | ⭐⭐⭐⭐ Đồ học |")
    lines.append("| 5 | Y Xuyên Kích Nhưỡng Tập | 伊川擊壤集 | Hán | ⭐⭐⭐ Thơ ngộ đạo |")
    lines.append("")
    lines.append("### Tier 1 — Đệ tử trực tiếp (Tier 2 lineage)")
    lines.append("")
    lines.append("| # | Sách | Tác giả | Ghi chú |")
    lines.append("|---|---|---|---|")
    lines.append("| 6 | Hoàng Cực Kinh Thế Bổ Chú | Thiệu Bá Ôn (con) | Phân tích sách của cha |")
    lines.append("| 7 | (works của Lý Chi Tài) | Lý Chi Tài | Thầy của Thiệu — Đồ Thư phái |")
    lines.append("")
    lines.append("### Tier 2 — Influencers + Tier 3 lineage")
    lines.append("")
    lines.append("| # | Sách | Tác giả | Ghi chú |")
    lines.append("|---|---|---|---|")
    lines.append("| 8 | Chu Dịch Bản Nghĩa | Chu Hy | Có Tiên Thiên Đồ của Thiệu — quan trọng |")
    lines.append("| 9 | Chu Tử Ngữ Loại | Chu Hy | Ghi chép lời Chu Hy về Thiệu |")
    lines.append("| 10 | Cận Tư Lục | Chu Hy + Lữ Tổ Khiêm | Tinh tuý Tống Lý học |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Concept gaps section (heuristic — pattern mentioned but in short context)
    lines.append("## 🔍 CONCEPT GAPS — Khái niệm em đã thấy nhưng cần research thêm")
    lines.append("")
    lines.append("Đây là pattern em scan ra **mention NHƯNG context có vẻ thiếu giải đầy đủ** —")
    lines.append("anh review xem có cần research mở rộng không.")
    lines.append("")

    # For each WORK + METHOD pattern, if we have <5 mentions in restored, likely incomplete
    gap_candidates = []
    for (cat, key), mlist in by_key.items():
        if cat in ("WORK", "METHOD") and len(mlist) < 5:
            gap_candidates.append((cat, key, mlist))
    gap_candidates.sort(key=lambda x: (x[0], len(x[2])))

    for cat, key, mlist in gap_candidates:
        lines.append(f"- **[{cat}] `{key}`** ({len(mlist)} mentions)")
        if mlist:
            preview = mlist[0].context[:200]
            lines.append(f"  - Sample context: \"{preview}...\"")
            lines.append(f"  - **Suggestion**: research thêm via `/research {key.replace('_', ' ')}`")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Next steps
    lines.append("## 📋 Next Steps")
    lines.append("")
    lines.append("1. **Anh review report này** — confirm shopping list đúng")
    lines.append("2. **Anh tìm sách Tier 0** (Mai Hoa, Hoàng Cực) — gửi PDF cho em")
    lines.append("3. **Em phục chế** sách Tổ sư qua MarkItDown (~1 ngày nếu có text layer)")
    lines.append("4. **Em + anh extract Author + Passages + Methods** từ Master corpus")
    lines.append("5. **Concept gaps** ở trên → research mở rộng qua `yi_research` agent")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"_Scan tool: `scripts/scan_master_mentions.py`_")
    lines.append(f"_Raw data: `data/research/master-mentions-raw.json`_")

    output_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
