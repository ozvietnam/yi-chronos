"""YI-Research — Autonomous AI research agent.

Em wrap GPT Researcher (assafelovic/gpt-researcher) để delegate task search
existing solutions thay vì em manual WebSearch.

Tích hợp với skill `research-existing-solutions`:
- Em invoke skill → skill nhắc em GỌI tool này thay vì manual search
- Tool autonomously: search web → aggregate → score → output structured report
- Em receive report → propose plan with citations

Backend default:
- LLM: Ollama qwen3:32b (free, local, privacy)
- Search: DuckDuckGo (free, no API key required)
- Fallback: DeepSeek / OpenRouter / MiniMax nếu Ollama down

Usage:
    from engine.yi_research import research
    report = await research("find PDF to markdown tools 2026")
    print(report.markdown)

CLI:
    python3 -m engine.yi_research "query here"
"""

from .agent import research, ResearchReport, ResearchConfig
from .catalog_sync import (
    sync_from_report,
    extract_tools_from_report,
    find_new_tools,
    ToolMention,
)

__all__ = [
    "research", "ResearchReport", "ResearchConfig",
    "sync_from_report", "extract_tools_from_report", "find_new_tools",
    "ToolMention",
]
