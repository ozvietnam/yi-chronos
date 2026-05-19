"""Tests cho yi_research wrapper.

Real research call quá đắt + slow cho CI — em mock GPTResearcher.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_research_config_defaults():
    from engine.yi_research import ResearchConfig
    cfg = ResearchConfig()
    assert cfg.llm_provider == "ollama"
    assert cfg.llm_model == "qwen3:32b"
    assert cfg.retriever == "duckduckgo"
    assert cfg.max_iterations == 3
    assert cfg.save_report is True


def test_make_gptr_config():
    from engine.yi_research.agent import _make_gptr_config, ResearchConfig
    cfg = ResearchConfig(llm_provider="deepseek", llm_model="deepseek-chat",
                         retriever="tavily")
    env = _make_gptr_config(cfg)
    assert env["FAST_LLM"] == "deepseek:deepseek-chat"
    assert env["SMART_LLM"] == "deepseek:deepseek-chat"
    assert env["RETRIEVER"] == "tavily"


def test_slugify():
    from engine.yi_research.agent import _slugify
    assert _slugify("Best Vietnamese OCR Tools 2026") == "best-vietnamese-ocr-tools-2026"
    assert _slugify("phục chế PDF tiếng Việt") == "phuc-che-pdf-tieng-viet"
    assert _slugify("") == "research"


@pytest.mark.asyncio
async def test_research_mocked_gpt_researcher(tmp_path, monkeypatch):
    """Mock GPTResearcher → verify wrapper passes through correctly."""
    from engine.yi_research import agent

    # Redirect output to tmp
    monkeypatch.setattr(agent, "_REPORTS_DIR", tmp_path)

    fake_researcher = MagicMock()
    fake_researcher.conduct_research = AsyncMock()
    fake_researcher.write_report = AsyncMock(return_value="# Test Report\n\nMock content.")
    fake_researcher.get_source_urls = MagicMock(return_value=["http://example.com/a", "http://example.com/b"])
    fake_researcher.get_research_images = MagicMock(return_value=[])
    fake_researcher.get_costs = MagicMock(return_value=0.001)

    fake_module = MagicMock()
    fake_module.GPTResearcher = MagicMock(return_value=fake_researcher)
    import sys
    monkeypatch.setitem(sys.modules, "gpt_researcher", fake_module)

    report = await agent.research("test query")
    assert "Mock content" in report.markdown
    assert report.query == "test query"
    assert len(report.sources) == 2
    assert report.cost_usd == 0.001
    assert report.saved_path is not None  # saved to tmp
    saved = tmp_path / next(iter(p.name for p in tmp_path.glob("*.md")))
    assert "Mock content" in saved.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_research_returns_error_report_on_exception(tmp_path, monkeypatch):
    from engine.yi_research import agent
    monkeypatch.setattr(agent, "_REPORTS_DIR", tmp_path)

    fake_researcher = MagicMock()
    fake_researcher.conduct_research = AsyncMock(side_effect=RuntimeError("network down"))
    fake_module = MagicMock()
    fake_module.GPTResearcher = MagicMock(return_value=fake_researcher)
    import sys
    monkeypatch.setitem(sys.modules, "gpt_researcher", fake_module)

    report = await agent.research("test", config=agent.ResearchConfig(save_report=False))
    assert "Research Error" in report.markdown
    assert "network down" in report.markdown
    # Should not raise — graceful fallback


def test_research_sync_wraps_async(tmp_path, monkeypatch):
    from engine.yi_research import agent
    monkeypatch.setattr(agent, "_REPORTS_DIR", tmp_path)

    fake_researcher = MagicMock()
    fake_researcher.conduct_research = AsyncMock()
    fake_researcher.write_report = AsyncMock(return_value="sync OK")
    fake_researcher.get_source_urls = MagicMock(return_value=[])
    fake_researcher.get_research_images = MagicMock(return_value=[])
    fake_researcher.get_costs = MagicMock(return_value=0)
    fake_module = MagicMock()
    fake_module.GPTResearcher = MagicMock(return_value=fake_researcher)
    import sys
    monkeypatch.setitem(sys.modules, "gpt_researcher", fake_module)

    report = agent.research_sync("test sync", config=agent.ResearchConfig(save_report=False))
    assert "sync OK" in report.markdown


def test_research_config_serializable():
    """ResearchReport.to_dict() works for JSON saving."""
    from engine.yi_research import ResearchReport
    r = ResearchReport(query="q", markdown="md", sources=["a", "b"])
    d = r.to_dict()
    assert d["query"] == "q"
    assert d["sources"] == ["a", "b"]


def test_cli_module_importable():
    """CLI module imports without errors."""
    from engine.yi_research import __main__
    assert hasattr(__main__, "main")
