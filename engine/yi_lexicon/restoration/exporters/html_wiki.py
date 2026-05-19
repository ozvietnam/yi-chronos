"""HTML rendering for a single page — applies wikilinks → <a> tags.

Frontend can fetch raw markdown and render itself, OR fetch this HTML for
quick display. Wikilinks become clickable: [[Càn]] → <a href="/lexicon/concept?q=Càn">Càn</a>
"""

from __future__ import annotations

import html
import re
from pathlib import Path


_WIKILINK_RE = re.compile(r"\[\[([^\]:][^\]]*)\]\]")
_FIGURE_INLINE_RE = re.compile(r"\[\[FIGURE:([a-z_]+)\|([^\]]+)\]\]")


def _render_figures(text: str) -> str:
    """Replace [[FIGURE:type|desc]] markers with placeholder cards (highlighted).

    Cần render TRƯỚC khi escape HTML, vì [[FIGURE:...]] đã được escape thành
    `&lt;&lt;FIGURE:...&gt;&gt;`. Em handle bằng cách thay placeholder bằng marker
    duy nhất TRƯỚC escape, rồi inject HTML sau.
    """
    def repl(m):
        ftype = html.escape(m.group(1).strip())
        desc = html.escape(m.group(2).strip(), quote=True)
        return (
            f'<aside class="figure-placeholder" data-figure-type="{ftype}" '
            f'data-figure-desc="{desc}">'
            f'<div class="fp-head">📐 Hình {ftype.replace("_", " ").title()} — '
            f'<em>cần vẽ lại</em></div>'
            f'<div class="fp-desc">{html.escape(m.group(2).strip())}</div>'
            f'</aside>'
        )
    return _FIGURE_INLINE_RE.sub(repl, text)


def _render_wikilinks(text: str, *, link_base: str = "/lexicon/concept") -> str:
    """Replace [[Concept]] with HTML anchors. text is already HTML-escaped.

    Note: skip [[FIGURE:...]] (already rendered separately).
    """
    def repl(m):
        concept = m.group(1).strip()
        if concept.startswith("FIGURE:"):
            return m.group(0)  # leave for figure renderer
        safe = html.escape(concept, quote=True)
        return (
            f'<a class="wikilink" data-concept="{safe}" '
            f'href="{link_base}?q={safe}">{safe}</a>'
        )
    return _WIKILINK_RE.sub(repl, text)


_FIGURE_TOKEN_RE = re.compile(r"⟨FIG_TOKEN_(\d+)⟩")


def _md_to_html_minimal(md: str) -> str:
    """Lightweight markdown → HTML for the reader.

    Supports: # h1 / ## h2 / ### h3, > blockquote, paragraphs, simple lists, images.
    [[FIGURE:type|desc]] → placeholder card (extracted before line parsing).
    Not a full markdown parser — frontend can opt for `marked` if richer needs.
    """
    # Step 1: extract figure placeholders + replace with sentinel tokens so they survive escape
    figures: list[str] = []
    def _replace_fig(m):
        idx = len(figures)
        figures.append(_render_figures(m.group(0)))
        return f"⟨FIG_TOKEN_{idx}⟩"
    md_with_tokens = _FIGURE_INLINE_RE.sub(_replace_fig, md)

    lines = md_with_tokens.splitlines()
    html_out: list[str] = []
    in_list = False
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            if in_list:
                html_out.append("</ul>")
                in_list = False
            html_out.append("")
            continue
        # Headings
        m = re.match(r"^(#{1,4})\s+(.+)$", line)
        if m:
            if in_list:
                html_out.append("</ul>"); in_list = False
            level = len(m.group(1))
            content = html.escape(m.group(2))
            content = _render_wikilinks(content)
            html_out.append(f"<h{level}>{content}</h{level}>")
            continue
        # Blockquote
        if line.startswith("> "):
            if in_list:
                html_out.append("</ul>"); in_list = False
            content = html.escape(line[2:])
            content = _render_wikilinks(content)
            html_out.append(f"<blockquote>{content}</blockquote>")
            continue
        # List
        if line.startswith("- ") or line.startswith("* "):
            if not in_list:
                html_out.append("<ul>"); in_list = True
            content = html.escape(line[2:])
            content = _render_wikilinks(content)
            html_out.append(f"<li>{content}</li>")
            continue
        # Image
        m_img = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
        if m_img:
            if in_list:
                html_out.append("</ul>"); in_list = False
            alt = html.escape(m_img.group(1))
            src = html.escape(m_img.group(2), quote=True)
            html_out.append(f'<figure><img alt="{alt}" src="{src}"/><figcaption>{alt}</figcaption></figure>')
            continue
        # Paragraph
        if in_list:
            html_out.append("</ul>"); in_list = False
        content = html.escape(line)
        content = _render_wikilinks(content)
        html_out.append(f"<p>{content}</p>")
    if in_list:
        html_out.append("</ul>")
    result_html = "\n".join(html_out)
    # Step 2: re-inject figure HTML at sentinel token positions
    def _restore_fig(m):
        idx = int(m.group(1))
        return figures[idx] if 0 <= idx < len(figures) else ""
    return _FIGURE_TOKEN_RE.sub(_restore_fig, result_html)


def render_page_html(md_text: str, *, link_base: str = "/lexicon/concept") -> str:
    """Convert one page markdown to wiki-style HTML."""
    return _md_to_html_minimal(md_text)


def render_page_file_to_html(md_path: Path) -> str:
    return render_page_html(Path(md_path).read_text(encoding="utf-8"))
