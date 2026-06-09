"""Section Detector — Auto-extract section boundaries từ restored book content.md.

Logic:
- Scan content.md, match `<!-- page N -->` markers
- Match `### X.Y[.Z]. Title` headers
- Compute page_start, page_end per section
- Output: manifest.yaml với structure 60 sections

Usage:
    python3 -m engine.atomization.section_detector --book trung-chau-tu-vi-dau-so-2
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Regex tested trên Trung Châu Q2 content
RE_PAGE = re.compile(r"<!--\s*page\s+(\d+)\s*-->")
RE_SECTION = re.compile(r"^#{2,5}\s+(\d+\.\d+(?:\.\d+)?)\.?\s+(.+?)\s*$")
RE_CHAPTER = re.compile(r"^##\s+(?:Chương\s+|Phần\s+)?(\d+)\.?\s+(.+?)\s*$")


def detect_sections(content_md_path: Path) -> list[dict[str, Any]]:
    """Walk content.md → extract section list with page boundaries."""
    text = content_md_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    current_page = 0
    sections: list[dict[str, Any]] = []

    for line_idx, line in enumerate(lines, 1):
        stripped = line.strip()

        # Update current_page
        m_page = RE_PAGE.search(stripped)
        if m_page:
            current_page = int(m_page.group(1))
            continue

        # Match section header
        m_sec = RE_SECTION.match(line)
        if m_sec:
            section_id = m_sec.group(1)
            title = m_sec.group(2).strip().rstrip("*").strip()
            sections.append({
                "id": section_id,
                "title": title,
                "page_start": current_page,
                "line_in_content": line_idx,
            })

    # Compute page_end: next section's page_start - 1, last section → current_page
    for i, s in enumerate(sections):
        if i + 1 < len(sections):
            next_page = sections[i + 1]["page_start"]
            s["page_end"] = next_page - 1 if next_page > s["page_start"] else s["page_start"]
        else:
            s["page_end"] = current_page

    return sections


def extract_star_palace(title: str) -> dict[str, Any]:
    """Naive extract star + palace from title.
    vd: 'Tử Vi độc tọa ở hai cung Tí hoặc Ngọ' → {star: 'Tử Vi', palaces: ['Tý', 'Ngọ']}
    """
    # Map palace name variants → canonical
    palace_canonical = {
        "Tí": "Tý", "Tý": "Tý",
        "Sửu": "Sửu",
        "Dần": "Dần",
        "Mão": "Mão",
        "Thìn": "Thìn",
        "Tị": "Tỵ", "Tỵ": "Tỵ",
        "Ngọ": "Ngọ",
        "Mùi": "Mùi",
        "Thân": "Thân",
        "Dậu": "Dậu",
        "Tuất": "Tuất",
        "Hợi": "Hợi",
    }

    # Detect palaces in title
    palaces = []
    for variant, canonical in palace_canonical.items():
        if variant in title:
            palaces.append(canonical)
    palaces = list(dict.fromkeys(palaces))  # dedupe preserve order

    # Detect star (14 chính tinh + double-star combos)
    chinh_tinh = [
        "Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng",
        "Liêm Trinh", "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn",
        "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân",
    ]
    stars_in_title = [s for s in chinh_tinh if s in title]

    return {
        "stars": stars_in_title,
        "palaces": palaces,
    }


def write_manifest(book: str, sections: list[dict[str, Any]], out_path: Path) -> None:
    """Write YAML manifest. Use plain string format (no PyYAML dep)."""
    lines = [
        f"# Auto-generated manifest for {book}",
        "# Edit ranh giới section nếu cần (anh có thể chỉnh manual)",
        "",
        f"book: {book}",
        f"total_sections: {len(sections)}",
        "",
        "sections:",
    ]
    for s in sections:
        sp_info = extract_star_palace(s["title"])
        lines.append(f'  - id: "{s["id"]}"')
        # Escape quotes in title
        title_esc = s["title"].replace('"', '\\"')
        lines.append(f'    title: "{title_esc}"')
        lines.append(f'    page_start: {s["page_start"]}')
        lines.append(f'    page_end: {s["page_end"]}')
        lines.append(f'    n_pages: {s["page_end"] - s["page_start"] + 1}')
        if sp_info["stars"]:
            stars_yaml = ", ".join(f'"{x}"' for x in sp_info["stars"])
            lines.append(f'    stars: [{stars_yaml}]')
        if sp_info["palaces"]:
            palaces_yaml = ", ".join(f'"{x}"' for x in sp_info["palaces"])
            lines.append(f'    palaces: [{palaces_yaml}]')
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Manifest written: {out_path}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--book", required=True, help="vd. trung-chau-tu-vi-dau-so-2")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    book_dir = PROJECT_ROOT / "data" / "restored_books" / args.book
    content_md = book_dir / "content.md"
    if not content_md.exists():
        sys.exit(f"❌ {content_md} not found")

    sections = detect_sections(content_md)
    print(f"🔍 Detected {len(sections)} sections in {args.book}")
    print(f"\n📋 Top 15 sections:")
    for s in sections[:15]:
        print(f"   {s['id']:>8}  p{s['page_start']:04d}-p{s['page_end']:04d}  "
              f"({s['page_end']-s['page_start']+1} pages)  {s['title'][:60]}")
    if len(sections) > 15:
        print(f"   ... and {len(sections)-15} more")

    if args.dry_run:
        return

    out_path = book_dir / "manifest.yaml"
    write_manifest(args.book, sections, out_path)


if __name__ == "__main__":
    main()
