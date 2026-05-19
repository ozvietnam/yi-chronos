"""GPT Researcher wrapper — autonomous research agent.

Em delegate task search existing solutions cho agent này.
Backed by GPT Researcher (Apache-2.0, 27k★) + Ollama (free local).
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path


_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "yi_research"
_REPORTS_DIR = _DATA_DIR / "reports"


@dataclass
class ResearchConfig:
    """Research agent config. Sensible defaults — free, local, fast."""
    # Backend selection
    llm_provider: str = "ollama"               # 'ollama'|'openai'|'deepseek'|'minimax'|'openrouter'
    llm_model: str = "qwen3:32b"               # default fast on M4
    embedding_provider: str = "ollama"
    embedding_model: str = "nomic-embed-text"
    retriever: str = "duckduckgo"              # free, no API key needed
    # Report depth
    report_type: str = "research_report"       # 'research_report'|'detailed_report'|'deep'
    max_iterations: int = 3                    # cap recursion
    max_sources: int = 15
    # Output
    save_report: bool = True
    output_dir: str | None = None              # default: data/yi_research/reports/


@dataclass
class ResearchReport:
    """Structured output từ research agent."""
    query: str
    markdown: str
    sources: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    cost_usd: float = 0.0
    config: dict = field(default_factory=dict)
    saved_path: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _make_gptr_config(cfg: ResearchConfig) -> dict:
    """Build GPT Researcher config dict (env-style) từ ResearchConfig."""
    return {
        # LLM
        "FAST_LLM": f"{cfg.llm_provider}:{cfg.llm_model}",
        "SMART_LLM": f"{cfg.llm_provider}:{cfg.llm_model}",
        "STRATEGIC_LLM": f"{cfg.llm_provider}:{cfg.llm_model}",
        # Embedding
        "EMBEDDING": f"{cfg.embedding_provider}:{cfg.embedding_model}",
        # Retriever (search backend)
        "RETRIEVER": cfg.retriever,
        # Depth
        "MAX_ITERATIONS": str(cfg.max_iterations),
        "MAX_SEARCH_RESULTS_PER_QUERY": str(cfg.max_sources),
        # Ollama endpoint
        "OLLAMA_BASE_URL": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
    }


async def research(
    query: str,
    *,
    config: ResearchConfig | None = None,
    verbose: bool = False,
) -> ResearchReport:
    """Autonomous deep research on `query`. Returns ResearchReport with citations.

    Em delegate task tìm existing solutions cho function này — replace manual
    WebSearch + WebFetch dance.
    """
    cfg = config or ResearchConfig()
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Inject config vào env vars (GPT Researcher reads from env)
    env_config = _make_gptr_config(cfg)
    for k, v in env_config.items():
        os.environ.setdefault(k, v)

    t0 = time.time()

    # Lazy import — keep package light
    try:
        from gpt_researcher import GPTResearcher
    except ImportError as e:
        raise RuntimeError(
            "GPT Researcher not installed. Run: "
            "pip install gpt-researcher"
        ) from e

    researcher = GPTResearcher(
        query=query,
        report_type=cfg.report_type,
        verbose=verbose,
    )

    if verbose:
        print(f"[yi_research] START · {cfg.llm_provider}:{cfg.llm_model} · "
              f"retriever={cfg.retriever}", flush=True)

    # Run autonomous research
    try:
        await researcher.conduct_research()
        markdown = await researcher.write_report()
    except Exception as e:
        # Graceful fallback — return error report rather than raise
        return ResearchReport(
            query=query,
            markdown=f"# Research Error\n\n{type(e).__name__}: {e}\n",
            duration_seconds=time.time() - t0,
            config=env_config,
        )

    duration = time.time() - t0
    sources = researcher.get_source_urls() if hasattr(researcher, "get_source_urls") else []
    images = researcher.get_research_images() if hasattr(researcher, "get_research_images") else []
    costs = researcher.get_costs() if hasattr(researcher, "get_costs") else 0.0

    report = ResearchReport(
        query=query,
        markdown=markdown,
        sources=list(sources) if sources else [],
        images=list(images) if images else [],
        duration_seconds=round(duration, 1),
        cost_usd=float(costs) if costs else 0.0,
        config=env_config,
    )

    # Save report to disk
    if cfg.save_report:
        slug = _slugify(query)[:60]
        ts = time.strftime("%Y%m%d-%H%M%S")
        out_dir = Path(cfg.output_dir) if cfg.output_dir else _REPORTS_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        report_path = out_dir / f"{ts}_{slug}.md"
        meta_path = out_dir / f"{ts}_{slug}.json"
        # Markdown with frontmatter
        fm = (
            f"---\n"
            f'query: "{query}"\n'
            f"duration_seconds: {duration:.1f}\n"
            f"cost_usd: {report.cost_usd}\n"
            f"sources_count: {len(report.sources)}\n"
            f"backend: {cfg.llm_provider}:{cfg.llm_model}\n"
            f"---\n\n"
        )
        report_path.write_text(fm + markdown, encoding="utf-8")
        meta_path.write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        report.saved_path = str(report_path)

    if verbose:
        print(f"[yi_research] DONE · {duration:.1f}s · "
              f"sources={len(report.sources)} · cost=${report.cost_usd:.4f}",
              flush=True)
        if report.saved_path:
            print(f"  → {report.saved_path}", flush=True)

    return report


def _slugify(text: str) -> str:
    import re
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    ascii_text = re.sub(r"[^A-Za-z0-9]+", "-", ascii_text).strip("-").lower()
    return ascii_text or "research"


def research_sync(query: str, **kwargs) -> ResearchReport:
    """Sync convenience wrapper around async `research`."""
    return asyncio.run(research(query, **kwargs))
