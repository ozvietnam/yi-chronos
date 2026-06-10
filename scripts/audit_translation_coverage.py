#!/usr/bin/env python3
"""Audit translation coverage for a yi_publishing book.

Replicates api/main.py page_layout logic (middle.json + index-block patch)
to count, per page, how many source lines exist vs how many have stored
translations. Outputs a list of pages needing (re)translation.

Usage:
    python3 scripts/audit_translation_coverage.py <book_id> [--json OUT]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MINERU_ROOT = PROJECT_ROOT / "data" / "yi_publishing_mineru"
TRANSLATIONS_ROOT = PROJECT_ROOT / "data" / "yi_publishing" / "translations"

TEXT_TYPES = ("text", "title", "list", "table", "index")


def find_middle_json(book_id: str) -> Path | None:
    book_dir = MINERU_ROOT / book_id
    if not book_dir.exists():
        return None
    hits = sorted(book_dir.rglob("*_middle.json"))
    return hits[0] if hits else None


def build_lines(block: dict) -> list[str]:
    """Return line_ids that page_layout would emit for this block (1 region)."""
    out = []
    for idx, line in enumerate(block.get("lines", []), start=1):
        spans = line.get("spans", [])
        text = "".join(s.get("content", "") for s in spans).strip()
        if not text and block.get("type") not in ("image", "table"):
            continue
        out.append((f"l{idx:03d}", text))
    return out


def audit(book_id: str) -> dict:
    middle_path = find_middle_json(book_id)
    if not middle_path:
        raise SystemExit(f"middle.json not found for {book_id}")
    middle = json.loads(middle_path.read_text())
    pdf_info = middle.get("pdf_info", [])

    pages_report = []
    total_lines = 0
    total_translated = 0

    for page_idx, page in enumerate(pdf_info):
        page_num = page_idx + 1
        blocks = page.get("para_blocks", page.get("preproc_blocks", []))
        preproc = page.get("preproc_blocks") or []
        for b in blocks:
            if not b.get("lines") and b.get("lines_deleted"):
                for pb in preproc:
                    if pb.get("bbox") == b.get("bbox") or pb.get("index") == b.get("index"):
                        if pb.get("lines"):
                            b["lines"] = pb["lines"]
                            break

        trans_dir = TRANSLATIONS_ROOT / book_id / f"p{page_num:04d}"

        page_lines = 0
        page_translated = 0
        for ridx, block in enumerate(blocks, start=1):
            region_id = f"r{ridx:03d}"
            if block.get("type") not in TEXT_TYPES:
                continue
            lines = build_lines(block)
            if not lines:
                continue
            stored = {}
            tp = trans_dir / f"{region_id}.json"
            if tp.exists():
                try:
                    stored = json.loads(tp.read_text()).get("lines", {})
                except Exception:
                    stored = {}
            for lsuffix, _text in lines:
                line_id = f"{region_id}-{lsuffix}"
                page_lines += 1
                entry = stored.get(line_id) or {}
                if (entry.get("text_vi") or "").strip():
                    page_translated += 1

        total_lines += page_lines
        total_translated += page_translated
        if page_lines > 0:
            pages_report.append({
                "page": page_num,
                "lines": page_lines,
                "translated": page_translated,
                "missing": page_lines - page_translated,
            })

    needs_work = [p for p in pages_report if p["missing"] > 0]
    return {
        "book_id": book_id,
        "pages_total": len(pdf_info),
        "pages_with_text": len(pages_report),
        "total_lines": total_lines,
        "total_translated": total_translated,
        "total_missing": total_lines - total_translated,
        "pages_needing_work": needs_work,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("book_id")
    ap.add_argument("--json", dest="json_out", default=None)
    args = ap.parse_args()

    rep = audit(args.book_id)
    print(f"book: {rep['book_id']}")
    print(f"pages: {rep['pages_total']} | pages with text: {rep['pages_with_text']}")
    pct = 100.0 * rep["total_translated"] / rep["total_lines"] if rep["total_lines"] else 0
    print(f"lines: {rep['total_translated']}/{rep['total_lines']} translated ({pct:.1f}%)")
    print(f"missing lines: {rep['total_missing']} across {len(rep['pages_needing_work'])} pages")
    nw = rep["pages_needing_work"]
    if nw:
        preview = ", ".join(str(p["page"]) for p in nw[:40])
        print(f"pages needing work (first 40): {preview}")
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(rep, ensure_ascii=False, indent=1))
        print(f"wrote {args.json_out}")


if __name__ == "__main__":
    main()
