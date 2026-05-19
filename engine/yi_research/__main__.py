"""CLI entry: python3 -m engine.yi_research "<query>"

Examples:
    python3 -m engine.yi_research "best Vietnamese OCR tools 2026"
    python3 -m engine.yi_research "PDF to markdown libraries" --provider deepseek
    python3 -m engine.yi_research "audio transcription tools" --model qwen2.5:7b-instruct-q8_0
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from .agent import ResearchConfig, research


async def _main(args) -> int:
    cfg = ResearchConfig(
        llm_provider=args.provider,
        llm_model=args.model,
        retriever=args.retriever,
        report_type=args.depth,
        max_iterations=args.max_iters,
        max_sources=args.max_sources,
        save_report=not args.no_save,
    )
    report = await research(args.query, config=cfg, verbose=not args.quiet)
    # Print markdown to stdout
    print()
    print("=" * 70)
    print(report.markdown)
    print("=" * 70)
    if report.saved_path:
        print(f"\n📁 Saved: {report.saved_path}")
    if report.sources:
        print(f"\n🔗 Sources ({len(report.sources)}):")
        for s in report.sources[:10]:
            print(f"  - {s}")
        if len(report.sources) > 10:
            print(f"  ... and {len(report.sources) - 10} more")
    if report.cost_usd > 0:
        print(f"\n💰 Cost: ${report.cost_usd:.4f}")
    print(f"⏱  Duration: {report.duration_seconds}s")

    # Auto-extract tool mentions vào catalog
    if args.catalog_sync:
        print("\n" + "─" * 70)
        print("🔁 Catalog sync — extracting tool mentions...")
        from .catalog_sync import sync_from_report
        result = sync_from_report(
            report.markdown,
            apply=args.catalog_apply,
            verbose=True,
        )
        if not args.catalog_apply and result["new"]:
            print(f"\n💡 Dry-run only. Use --catalog-apply to actually append.")

    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="YI-Research — autonomous AI research agent.")
    p.add_argument("query", help="Research query (in quotes)")
    p.add_argument("--provider", default="ollama",
                   choices=["ollama", "openai", "deepseek", "minimax", "openrouter", "anthropic"],
                   help="LLM provider (default: ollama free local)")
    p.add_argument("--model", default="qwen3:32b",
                   help="LLM model name (default: qwen3:32b for Ollama)")
    p.add_argument("--retriever", default="duckduckgo",
                   choices=["duckduckgo", "tavily", "exa", "google", "bing", "searx"],
                   help="Search backend (default: duckduckgo free no-key)")
    p.add_argument("--depth", default="research_report",
                   choices=["research_report", "detailed_report", "deep"],
                   help="Report depth")
    p.add_argument("--max-iters", type=int, default=3, help="Max research iterations")
    p.add_argument("--max-sources", type=int, default=15, help="Max sources per query")
    p.add_argument("--no-save", action="store_true", help="Don't save report to disk")
    p.add_argument("--quiet", "-q", action="store_true", help="Suppress progress logs")
    p.add_argument("--catalog-sync", action="store_true",
                   help="Auto-extract tool mentions từ report → propose vào tool-catalog.md")
    p.add_argument("--catalog-apply", action="store_true",
                   help="With --catalog-sync: actually append new tools (not just dry-run)")
    args = p.parse_args(argv)
    return asyncio.run(_main(args))


if __name__ == "__main__":
    sys.exit(main())
