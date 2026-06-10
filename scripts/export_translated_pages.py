#!/usr/bin/env python3
"""Export translated book pages → data/restored_books/<corpus_id>/pages/pNNNN.md

Source: API page_layout (middle.json structure + per-line translations merged).
Output format matches trung-chau-tu-vi-dau-so-2 pages: `<!-- page N -->` + VI text.

- Skips regions: image (no text), page furniture is naturally absent from para_blocks
- Lines without translation are emitted as `[⚠ chưa dịch] <ZH>` so atomizer never
  silently loses content.
- title regions become `### <text>` headings.

Usage:
    python3 scripts/export_translated_pages.py <book_id> <corpus_id> [--pages 1-50]
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = PROJECT_ROOT / "data" / "restored_books"
BASE = "http://localhost:8001"
TEXT_TYPES = ("text", "title", "list", "table", "index", "table_caption", "figure_caption")


def fetch_page(token: str, book_id: str, page: int) -> dict:
    req = urllib.request.Request(
        f"{BASE}/api/yi-publishing/pages/{book_id}/{page}",
        headers={"X-Session-Token": token},
    )
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def page_to_markdown(page_num: int, layout: dict) -> tuple[str, int, int]:
    """Return (markdown, n_lines, n_untranslated)."""
    parts = [f"<!-- page {page_num} -->", ""]
    n_lines = 0
    n_miss = 0
    for reg in layout.get("regions", []):
        rtype = reg.get("type")
        if rtype not in TEXT_TYPES:
            continue
        buf = []
        for ln in reg.get("lines", []):
            src = (ln.get("source_text") or "").strip()
            if not src:
                continue
            n_lines += 1
            vi = ((ln.get("translation") or {}).get("text_vi") or "").strip()
            if vi:
                buf.append(vi)
            else:
                n_miss += 1
                buf.append(f"[⚠ chưa dịch] {src}")
        if not buf:
            continue
        if rtype == "title":
            parts.append(f"### {' '.join(buf)}")
        elif rtype == "index":
            # Thiết Bản điều văn — one line per entry, keep separate lines
            parts.extend(buf)
        else:
            parts.append(" ".join(buf) if rtype == "table" else "\n".join(buf))
        parts.append("")
    return "\n".join(parts).rstrip() + "\n", n_lines, n_miss


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("book_id")
    ap.add_argument("corpus_id")
    ap.add_argument("--pages", default=None, help="vd 1-50; default = all")
    ap.add_argument("--token-file", default="/tmp/yi_owner_token")
    args = ap.parse_args()

    token = open(args.token_file).read().strip()

    # Determine total pages from page 1 response error or probe
    first = fetch_page(token, args.book_id, 1)
    if first.get("status") != "ok":
        sys.exit(f"cannot fetch page 1: {first.get('message')}")
    total = first.get("total_pages") or 0
    if not total:
        # probe via error message fallback
        probe = fetch_page(token, args.book_id, 999999)
        msg = probe.get("message", "")
        import re
        m = re.search(r"1-(\d+)", msg)
        total = int(m.group(1)) if m else 0
    if not total:
        sys.exit("cannot determine total pages")

    if args.pages:
        a, b = args.pages.split("-")
        rng = range(int(a), min(int(b), total) + 1)
    else:
        rng = range(1, total + 1)

    out_dir = OUT_ROOT / args.corpus_id / "pages"
    out_dir.mkdir(parents=True, exist_ok=True)

    tot_lines = 0
    tot_miss = 0
    written = 0
    for p in rng:
        layout = fetch_page(token, args.book_id, p) if p != 1 else first
        if layout.get("status") != "ok":
            print(f"p{p:04d} SKIP: {layout.get('message')}", flush=True)
            continue
        md, n_lines, n_miss = page_to_markdown(p, layout)
        if n_lines == 0:
            continue  # image-only / blank page → no md file
        (out_dir / f"p{p:04d}.md").write_text(md, encoding="utf-8")
        written += 1
        tot_lines += n_lines
        tot_miss += n_miss
        if p % 100 == 0:
            print(f"...p{p:04d} ({written} files)", flush=True)

    manifest = {
        "corpus_id": args.corpus_id,
        "source_book_id": args.book_id,
        "source": "yi_publishing translations (per-line VI) + MinerU middle.json",
        "pages_written": written,
        "lines": tot_lines,
        "untranslated_lines": tot_miss,
    }
    (OUT_ROOT / args.corpus_id / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1)
    )
    print(f"DONE: {written} pages, {tot_lines} lines, {tot_miss} untranslated → {out_dir}")


if __name__ == "__main__":
    main()
