"""Tests cho catalog_sync — extract tool mentions từ research report."""

from __future__ import annotations

from pathlib import Path
import pytest


def test_extract_github_urls():
    from engine.yi_research.catalog_sync import extract_tools_from_report
    md = """
    Top tools:
    - https://github.com/microsoft/markitdown
    - https://github.com/assafelovic/gpt-researcher (27k stars)
    - github.com/stanford-oval/storm
    """
    tools = extract_tools_from_report(md)
    names = {t.canonical for t in tools}
    assert "markitdown" in names
    assert "gpt-researcher" in names
    assert "storm" in names


def test_extract_pip_install():
    from engine.yi_research.catalog_sync import extract_tools_from_report
    md = "Install via `pip install markitdown[all]` and `pip install -U faster-whisper`"
    tools = extract_tools_from_report(md)
    names = {t.canonical for t in tools}
    assert "markitdown" in names
    assert "faster-whisper" in names


def test_extract_npm_install():
    from engine.yi_research.catalog_sync import extract_tools_from_report
    md = "Run `npm install langchain` then `npm install -g @langchain/openai`"
    tools = extract_tools_from_report(md)
    names = {t.canonical for t in tools}
    assert "langchain" in names


def test_extract_skips_common_repos():
    from engine.yi_research.catalog_sync import extract_tools_from_report
    md = "See github.com/example/docs and github.com/example/examples"
    tools = extract_tools_from_report(md)
    # docs and examples should be filtered out
    canonicals = {t.canonical for t in tools}
    assert "docs" not in canonicals
    assert "examples" not in canonicals


def test_dedupe_multiple_mentions():
    from engine.yi_research.catalog_sync import extract_tools_from_report
    md = """
    First mention: github.com/microsoft/markitdown
    Install: pip install markitdown
    """
    tools = extract_tools_from_report(md)
    markitdown = [t for t in tools if t.canonical == "markitdown"]
    assert len(markitdown) == 1
    # Should merge github_url + pip_name
    t = markitdown[0]
    assert t.github_url and "microsoft/markitdown" in t.github_url
    assert t.pip_name == "markitdown"


def test_load_catalog_tools(tmp_path):
    from engine.yi_research.catalog_sync import load_catalog_tools
    catalog = tmp_path / "catalog.md"
    catalog.write_text("""# Tool Catalog

## Document
### MarkItDown · document
- repo: ...

### Docling · pdf
- ...

## OCR
### Qwen2.5-VL · vision
- ...
""")
    known = load_catalog_tools(catalog)
    assert "markitdown" in known
    assert "docling" in known
    assert "qwen2.5-vl" in known


def test_find_new_tools(tmp_path):
    from engine.yi_research.catalog_sync import find_new_tools, ToolMention
    catalog = tmp_path / "catalog.md"
    catalog.write_text("### MarkItDown · document\n- ...\n")
    mentions = [
        ToolMention(name="MarkItDown", canonical="markitdown"),
        ToolMention(name="Docling", canonical="docling"),
        ToolMention(name="NewTool", canonical="newtool"),
    ]
    new = find_new_tools(mentions, catalog)
    canonicals = {t.canonical for t in new}
    assert "markitdown" not in canonicals
    assert "docling" in canonicals
    assert "newtool" in canonicals


def test_format_catalog_entry():
    from engine.yi_research.catalog_sync import format_catalog_entry, ToolMention
    t = ToolMention(
        name="GPT Researcher",
        canonical="gpt-researcher",
        github_url="https://github.com/assafelovic/gpt-researcher",
        pip_name="gpt-researcher",
        context="autonomous research agent",
    )
    entry = format_catalog_entry(t)
    assert "GPT Researcher" in entry
    assert "to-investigate" in entry
    assert "gpt-researcher" in entry
    assert "github.com/assafelovic" in entry
    assert "pip install" in entry


def test_sync_from_report_dry_run(tmp_path):
    from engine.yi_research.catalog_sync import sync_from_report
    catalog = tmp_path / "catalog.md"
    catalog.write_text("### MarkItDown · document\n")

    report = """
    Top tools researched:
    - github.com/microsoft/markitdown — already known
    - github.com/example/new-tool — new!
    - pip install awesome-pkg
    """
    result = sync_from_report(report, catalog_path=catalog, apply=False, verbose=False)
    assert result["applied"] is False
    new_names = {n.lower() for n in result["new"]}
    assert "markitdown" not in new_names  # known
    # Should have new-tool and awesome-pkg as new
    catalog_text = catalog.read_text()
    assert "new-tool" not in catalog_text.lower()  # dry-run, not applied


def test_sync_from_report_apply(tmp_path):
    from engine.yi_research.catalog_sync import sync_from_report
    catalog = tmp_path / "catalog.md"
    catalog.write_text("# Catalog\n\n### MarkItDown · document\n")

    report = "Try github.com/example/cool-tool and pip install awesome-pkg"
    result = sync_from_report(report, catalog_path=catalog, apply=True, verbose=False)
    assert result["applied"] is True
    catalog_text = catalog.read_text()
    assert "to-investigate" in catalog_text  # new entries marked
    assert "cool-tool" in catalog_text.lower()


def test_append_creates_catalog_if_missing(tmp_path):
    from engine.yi_research.catalog_sync import append_to_catalog, ToolMention
    catalog = tmp_path / "new-catalog.md"
    assert not catalog.exists()
    tools = [ToolMention(name="TestTool", canonical="testtool",
                          github_url="https://github.com/test/tool")]
    append_to_catalog(tools, catalog)
    assert catalog.exists()
    assert "TestTool" in catalog.read_text()
