"""Markdown exporter — concat all per-page markdowns into one canonical file.

`content.md` is the source of truth: anh có thể đọc thẳng bằng VS Code / Obsidian
(WikiLinks `[[Càn]]` tương thích với Obsidian linking ngay).
"""

from __future__ import annotations

from pathlib import Path

from ..manifest import BookManifest


def export_full_markdown(manifest: BookManifest, root_dir: Path) -> Path:
    """Concat all `pages/page-NNNN.md` into `content.md` with frontmatter."""
    root = Path(root_dir)
    pages_dir = root / "pages"
    target = root / "content.md"

    lines: list[str] = []
    lines.append("---")
    lines.append(f"title: \"{manifest.book_name}\"")
    if manifest.author:
        lines.append(f"author: \"{manifest.author}\"")
    lines.append(f"tier: \"{manifest.tier}\"")
    lines.append(f"copyright_status: \"{manifest.copyright_status}\"")
    lines.append(f"corpus_id: {manifest.corpus_id}")
    lines.append(f"pages_restored: {manifest.pages_restored}")
    lines.append(f"pages_total: {manifest.pages_total}")
    lines.append(f"pipeline_version: \"{manifest.pipeline_version}\"")
    lines.append("---")
    lines.append("")
    lines.append(f"# {manifest.book_name}")
    if manifest.author:
        lines.append(f"*— {manifest.author}*")
    lines.append("")
    lines.append("> ⚠️ Bản phục chế nội bộ phục vụ nghiên cứu. KHÔNG thay thế bản in gốc.")
    lines.append("> Mua sách gốc tại nhà xuất bản để ủng hộ tác giả.")
    lines.append("")

    # Page-by-page concat with section anchors
    for page in sorted(manifest.pages, key=lambda p: p.page):
        if not page.md_path:
            continue
        page_md = pages_dir / Path(page.md_path).name
        if not page_md.exists():
            continue
        lines.append(f"\n<a id=\"page-{page.page}\"></a>")
        lines.append(f"<!-- Trang {page.page} -->")
        lines.append(page_md.read_text(encoding="utf-8"))
        lines.append("")

    target.write_text("\n".join(lines), encoding="utf-8")
    return target
