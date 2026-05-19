"""Publisher — render translated book to PDF (bản in cuối).

Reads:
  - MinerU layout: data/yi_publishing_mineru/{book_id}/auto|ocr/...
  - Translations: data/yi_publishing/translations/{book_id}/p{NNNN}/r{NNN}.json

Outputs:
  - data/published/{book_id}-v{N}.pdf
  - data/published/{book_id}-v{N}.html (intermediate)

Layout choices per page:
  * For each book page:
      - Heading with page number
      - Original scan image rendered next to (or before) Vietnamese
      - Vietnamese paragraphs, line-by-line preserved
      - Image regions inlined as figures
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

MINERU_ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi/data/yi_publishing_mineru")
TRANSLATIONS_ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi/data/yi_publishing/translations")
PUBLISHED_ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi/data/published")


# ----------------------------- loaders -----------------------------

def _resolve_book_dir(book_id: str) -> Path:
    """Find the auto/ or ocr/ subdir under MinerU output for a book."""
    book_dir = MINERU_ROOT / book_id
    for subname in ("auto", "ocr"):
        sub = book_dir / subname
        if (sub / f"{book_id}_middle.json").exists():
            return sub
    raise FileNotFoundError(f"No middle.json found under {book_dir}")


def _load_middle(book_id: str) -> dict:
    sub = _resolve_book_dir(book_id)
    return json.loads((sub / f"{book_id}_middle.json").read_text())


def _load_translations(book_id: str, page_num: int) -> dict[str, dict]:
    """Return {line_id: {text_vi, status, version, ...}} for a page."""
    tdir = TRANSLATIONS_ROOT / book_id / f"p{page_num:04d}"
    out: dict[str, dict] = {}
    if not tdir.exists():
        return out
    for f in tdir.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            for lid, info in (d.get("lines") or {}).items():
                out[lid] = info
        except Exception as e:
            logger.warning(f"Failed to load {f}: {e}")
    return out


def _block_lines(block: dict, region_id: str) -> list[dict]:
    """Same as API _build_lines_for_block."""
    out = []
    for idx, line in enumerate(block.get("lines", []), start=1):
        spans = line.get("spans", [])
        text = "".join(s.get("content", "") for s in spans).strip()
        if not text and block.get("type") not in ("image", "table"):
            continue
        out.append({
            "line_id": f"{region_id}-l{idx:03d}",
            "source_text": text,
            "bbox": line.get("bbox", [0, 0, 0, 0]),
        })
    return out


def _block_image_path(block: dict, book_sub: Path) -> Optional[Path]:
    """Find image file for image blocks."""
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            if span.get("type") == "image":
                ip = span.get("image_path")
                if ip:
                    candidate = book_sub / "images" / ip
                    if candidate.exists():
                        return candidate
                    # Some MinerU layouts store relative paths
                    candidate2 = book_sub / ip
                    if candidate2.exists():
                        return candidate2
    return None


# ----------------------------- HTML builder -----------------------------

HTML_TEMPLATE = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<style>
@page {{
  size: A5 portrait;
  margin: 18mm 16mm 22mm 16mm;
  @bottom-center {{ content: counter(page); font-family: serif; font-size: 9pt; color: #555; }}
}}
@page :first {{ margin: 0; }}
html {{
  /* Vietnamese-aware fonts FIRST. Songti SC for CJK fallback. */
  font-family: "Times New Roman", "Palatino", "Hoefler Text",
               "Baskerville", "Songti SC", "Noto Serif CJK SC", serif;
  font-size: 11pt;
  line-height: 1.6;
  color: #1a1410;
}}
body {{ margin: 0; }}
.cover {{
  page-break-after: always;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  background: linear-gradient(135deg, #faf8f3, #efe5d2);
  padding: 4rem 3rem;
}}
.cover .stamp {{
  font-size: 0.85rem;
  letter-spacing: 0.5em;
  color: #8b3a2a;
  margin-bottom: 1.2em;
  font-variant: small-caps;
}}
.cover .hanzi {{
  font-family: "Songti SC", "Noto Serif CJK SC", "STSong", serif;
  font-size: 2.4em;
  color: #4a1a1a;
  margin-bottom: 0.3em;
  letter-spacing: 0.15em;
}}
.cover h1 {{
  font-size: 2.0em;
  margin: 0.2em 0 0.8em 0;
  color: #6d2727;
  border-bottom: 2px solid #b8a890;
  padding-bottom: 0.4em;
  letter-spacing: 0.04em;
}}
.cover .author {{
  font-size: 1.1em;
  color: #555;
  margin-bottom: 0.4em;
}}
.cover .edition {{
  font-size: 0.85em;
  color: #777;
  margin-top: auto;
}}
.toc {{
  page-break-after: always;
  padding: 1rem 0;
}}
.toc h2 {{ border-bottom: 1px solid #c8b896; padding-bottom: 0.3em; color: #4a1a1a; }}
.toc-entry {{
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 0.15em 0;
  border-bottom: 1px dotted #d8c8a8;
  font-size: 0.92em;
}}
.toc-entry .title {{ flex: 1; }}
.toc-entry .pgnum {{ font-family: ui-monospace, monospace; color: #777; font-size: 0.85em; }}

.book-page {{
  page-break-after: always;
  padding-bottom: 0.5rem;
}}
.book-page .pg-head {{
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid #c8b896;
  padding-bottom: 0.4em;
  margin-bottom: 1em;
  font-size: 0.78em;
  color: #777;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}}
.book-page h1 {{
  font-size: 1.6em;
  text-align: center;
  color: #4a1a1a;
  margin: 0.3em 0 0.8em 0;
  border-bottom: 2px solid #b8a890;
  padding-bottom: 0.3em;
}}
.book-page h2 {{
  font-size: 1.2em;
  color: #6d2727;
  margin: 0.9em 0 0.4em 0;
}}
.book-page p {{
  margin: 0.5em 0;
  text-align: justify;
  text-indent: 1.3em;
}}
.book-page ul {{ margin: 0.5em 0; padding-left: 1.5em; }}
.book-page ul li {{ margin: 0.15em 0; }}
.book-page figure {{
  text-align: center;
  margin: 1.2em auto;
  page-break-inside: avoid;
}}
.book-page figure img {{
  max-width: 90%;
  max-height: 12cm;
  border: 1px solid #c8b896;
  background: #fff;
}}
.book-page figure figcaption {{
  font-size: 0.78em;
  color: #777;
  font-style: italic;
  margin-top: 0.3em;
}}
.untranslated {{ background: #fff3cd; color: #7a5a00; padding: 0 0.2em; }}
.toc-block {{
  background: #f8f3e9;
  border-left: 3px solid #b8a890;
  padding: 0.4em 0.7em;
  margin: 0.4em 0;
}}
.scan-thumb {{
  display: block;
  max-width: 75%;
  margin: 0.5em auto 1em auto;
  border: 1px solid #c8b896;
  page-break-inside: avoid;
}}
.imgcell {{ text-align: center; }}

/* 2-layer rendering: Hán-Việt + Luận giải */
.passage-block {{
  margin: 0.7em 0 1em 0;
  padding: 0.5em 0.7em;
  border-left: 3px solid #c8b896;
  background: #faf6ed;
  page-break-inside: avoid;
}}
.passage-hanviet {{
  font-style: italic;
  color: #6d4a2a;
  font-size: 0.92em;
  margin: 0 0 0.45em 0;
  line-height: 1.55;
  text-indent: 0;
  border-bottom: 1px dashed #c8b896;
  padding-bottom: 0.35em;
}}
.passage-hanviet::before {{
  content: "音 ";
  color: #b8a890;
  font-size: 0.85em;
  font-style: normal;
  font-weight: 600;
}}
.passage-luangiai {{
  margin: 0;
  color: #1a1410;
  font-size: 1em;
  line-height: 1.7;
  text-indent: 0;
}}
.passage-luangiai::before {{
  content: "義 ";
  color: #8b3a2a;
  font-size: 0.85em;
  font-weight: 600;
}}
</style>
</head>
<body>
{cover}
{toc}
{pages}
</body>
</html>
"""


# ----------------------------- per-page renderer -----------------------------

def _render_page(
    page_idx: int,
    page: dict,
    book_id: str,
    book_sub: Path,
    translations: dict[str, dict],
    include_scan: bool,
) -> str:
    """Render one source page as a section of HTML."""
    blocks = page.get("para_blocks") or page.get("preproc_blocks") or []
    preproc = page.get("preproc_blocks") or []

    parts = [
        f'<section class="book-page">',
        f'<div class="pg-head">'
        f'<span>Trang {page_idx} (gốc {page_idx})</span>'
        f'<span>{book_id}</span>'
        f'</div>',
    ]

    if include_scan:
        scan_path = book_sub / "page_images" / f"{page_idx:04d}.png"
        if not scan_path.exists():
            # MinerU uses different naming: 0_image.png in page_images dir
            candidates = list((book_sub / "page_images").glob("*.png"))
            if page_idx <= len(candidates):
                scan_path = sorted(candidates)[page_idx - 1]
        if scan_path.exists():
            parts.append(
                f'<div class="imgcell">'
                f'<img class="scan-thumb" src="file://{scan_path}" alt="Trang {page_idx} gốc"/>'
                f'</div>'
            )

    for r_idx, block in enumerate(blocks, start=1):
        region_id = f"r{r_idx:03d}"
        btype = block.get("type", "")

        # Recover lines from preproc if para_blocks has lines_deleted
        if not block.get("lines") and block.get("lines_deleted"):
            for pb in preproc:
                if pb.get("bbox") == block.get("bbox") or pb.get("index") == block.get("index"):
                    block = {**block, "lines": pb.get("lines", [])}
                    break

        lines = _block_lines(block, region_id)

        # Image
        if btype == "image":
            img_path = _block_image_path(block, book_sub)
            if img_path:
                parts.append(
                    f'<figure><img src="file://{img_path}" alt="Hình"/>'
                    f'<figcaption>Hình từ trang {page_idx}</figcaption></figure>'
                )
            continue

        # Text-like: assemble translated content
        if not lines:
            continue

        # Determine HTML tag based on type
        if btype == "title":
            tag = "h2" if r_idx > 1 else "h1"
        elif btype == "index":
            # TOC entries — render as list
            parts.append('<div class="toc-block">')
            parts.append('<div style="font-size:0.85em;color:#6d2727;font-weight:600;">Mục lục</div>')
            for line in lines:
                t = translations.get(line["line_id"], {}).get("text_vi", "")
                src = line["source_text"]
                disp = t or f'<span class="untranslated">{src}</span>'
                parts.append(f'<div class="toc-entry"><span class="title">{disp}</span></div>')
            parts.append('</div>')
            continue
        elif btype == "list":
            parts.append("<ul>")
            for line in lines:
                t = translations.get(line["line_id"], {}).get("text_vi", "")
                src = line["source_text"]
                disp = t or f'<span class="untranslated">{src}</span>'
                parts.append(f"<li>{disp}</li>")
            parts.append("</ul>")
            continue
        else:
            tag = "p"

        # Title / paragraph: assemble translated lines.
        # 2-layer aware: if any line has text_vi_luangiai, render passage-block
        # (Hán-Việt italic line + Luận giải main paragraph).
        hanviet_parts = []
        luangiai_parts = []
        has_luangiai = False
        for line in lines:
            tr = translations.get(line["line_id"], {}) or {}
            hv = tr.get("text_vi") or ""
            lg = tr.get("text_vi_luangiai") or ""
            src = line["source_text"]
            if lg:
                has_luangiai = True
            hanviet_parts.append(hv if hv else f'<span class="untranslated">{src}</span>')
            luangiai_parts.append(lg if lg else "")

        if tag in ("h1", "h2"):
            joined = " ".join(hanviet_parts).strip()
            parts.append(f"<{tag}>{joined}</{tag}>")
            # If heading has luangiai, show small below as subtitle
            lg_joined = " ".join(luangiai_parts).strip()
            if lg_joined and has_luangiai:
                parts.append(
                    f'<p style="text-align:center;font-size:0.85em;color:#777;'
                    f'font-style:italic;margin-top:-0.3em;text-indent:0;">'
                    f'{lg_joined}</p>'
                )
        elif has_luangiai:
            # 2-layer rendering: passage-block (Hán-Việt + Luận giải)
            hv_joined = " ".join(hanviet_parts).strip()
            lg_joined = " ".join(p for p in luangiai_parts if p).strip()
            parts.append('<div class="passage-block">')
            parts.append(f'<p class="passage-hanviet">{hv_joined}</p>')
            if lg_joined:
                parts.append(f'<p class="passage-luangiai">{lg_joined}</p>')
            parts.append('</div>')
        else:
            # Single-layer fallback (backward compat with old translations)
            joined = " ".join(hanviet_parts).strip()
            parts.append(f"<p>{joined}</p>")

    parts.append("</section>")
    return "\n".join(parts)


# ----------------------------- main entry -----------------------------

def build_book(
    book_id: str,
    *,
    title: str = "",
    author: str = "",
    hanzi_title: str = "",
    edition: str = "v0.1 (đang biên tập)",
    output_dir: Path = PUBLISHED_ROOT,
    include_scan: bool = False,
    page_range: Optional[tuple[int, int]] = None,
) -> dict:
    """Build a publishable PDF for a book.

    Args:
        book_id: e.g. 'tuvidauso-zh'
        title: Vietnamese title (default = book_id)
        author: e.g. 'Trần Đoàn (希夷陈先生)'
        hanzi_title: Chinese original title for cover
        edition: edition label
        include_scan: include scan thumbnail before each page (large file)
        page_range: (start, end) inclusive; None = all available

    Returns: {pdf_path, html_path, page_count, ...}
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    middle = _load_middle(book_id)
    book_sub = _resolve_book_dir(book_id)
    pages = middle.get("pdf_info", [])

    start_pg = page_range[0] if page_range else 1
    end_pg = min(page_range[1], len(pages)) if page_range else len(pages)

    title = title or book_id
    cover_html = (
        f'<section class="cover">'
        f'<div class="stamp">YI-CHRONOS</div>'
        f'<div class="hanzi">{hanzi_title}</div>'
        f'<h1>{title}</h1>'
        f'<div class="author">{author}</div>'
        f'<div class="edition">{edition} · {datetime.now().strftime("%Y-%m-%d")}</div>'
        f'</section>'
    )

    # Render pages
    page_htmls = []
    for pg_idx in range(start_pg, end_pg + 1):
        page = pages[pg_idx - 1]
        translations = _load_translations(book_id, pg_idx)
        page_html = _render_page(
            page_idx=pg_idx,
            page=page,
            book_id=book_id,
            book_sub=book_sub,
            translations=translations,
            include_scan=include_scan,
        )
        page_htmls.append(page_html)

    full_html = HTML_TEMPLATE.format(
        title=title,
        cover=cover_html,
        toc="",  # auto-toc disabled for now
        pages="\n".join(page_htmls),
    )

    # Write artifacts
    version = edition.split()[0].lstrip("v")
    stem = f"{book_id}-v{version}-p{start_pg}-{end_pg}"
    html_path = output_dir / f"{stem}.html"
    pdf_path = output_dir / f"{stem}.pdf"

    html_path.write_text(full_html, encoding="utf-8")
    logger.info(f"HTML written: {html_path} ({len(full_html)} chars)")

    # Render PDF via WeasyPrint
    try:
        from weasyprint import HTML
        HTML(string=full_html, base_url=str(book_sub)).write_pdf(str(pdf_path))
        pdf_size = pdf_path.stat().st_size
        logger.info(f"PDF written: {pdf_path} ({pdf_size / 1024:.1f} KB)")
    except Exception as e:
        logger.error(f"WeasyPrint failed: {e}")
        raise

    return {
        "book_id": book_id,
        "title": title,
        "page_count": end_pg - start_pg + 1,
        "html_path": str(html_path),
        "pdf_path": str(pdf_path),
        "pdf_size_kb": round(pdf_path.stat().st_size / 1024, 1),
        "edition": edition,
    }


if __name__ == "__main__":
    import argparse, sys
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--book-id", required=True)
    parser.add_argument("--title", default="")
    parser.add_argument("--author", default="")
    parser.add_argument("--hanzi-title", default="")
    parser.add_argument("--edition", default="v0.1")
    parser.add_argument("--include-scan", action="store_true")
    parser.add_argument("--start", type=int, default=None)
    parser.add_argument("--end", type=int, default=None)
    args = parser.parse_args()

    pr = None
    if args.start and args.end:
        pr = (args.start, args.end)

    result = build_book(
        args.book_id,
        title=args.title,
        author=args.author,
        hanzi_title=args.hanzi_title,
        edition=args.edition,
        include_scan=args.include_scan,
        page_range=pr,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
