from __future__ import annotations

import argparse
import os
from pathlib import Path

from .models import LlmConfig, PipelineConfig
from .pipeline import ROOT, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan a Douyin channel and export raw + cleaned text.")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="Scan a Douyin channel/user URL")
    scan.add_argument("channel_url")
    scan.add_argument("--out-root", type=Path, default=ROOT / "data" / "research" / "douyin_transcripts")
    scan.add_argument("--limit", type=int, default=None)
    scan.add_argument("--jobs", type=int, default=4)
    scan.add_argument("--cookies", type=Path, default=None, help="Netscape cookies.txt for Douyin if login is required")
    scan.add_argument("--subtitle-langs", default="zh-Hans,zh-CN,zh,en")
    scan.add_argument("--ocr-langs", default="chi_sim+eng")
    scan.add_argument("--transcriber", choices=["none", "local-whisper", "openai"], default="none")
    scan.add_argument("--whisper-model", default="small")
    scan.add_argument("--llm", action="store_true", help="Use OpenAI-compatible LLM cleanup after deterministic cleanup")
    scan.add_argument("--llm-model", default=None, help="Model name, e.g. gpt-4o-mini or value routed by LiteLLM")
    scan.add_argument("--llm-api-key-env", default="LITELLM_API_KEY")
    scan.add_argument("--llm-base-url-env", default="LITELLM_BASE_URL")
    scan.add_argument("--llm-max-output-tokens", type=int, default=800)
    scan.add_argument("--target-language", default="original", help="original or vi")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "scan":
        llm = LlmConfig(
            enabled=args.llm,
            model=args.llm_model or os.getenv("LITELLM_MODEL"),
            api_key_env=args.llm_api_key_env,
            base_url_env=args.llm_base_url_env,
            max_output_tokens=args.llm_max_output_tokens,
            target_language=args.target_language,
        )
        config = PipelineConfig(
            channel_url=args.channel_url,
            out_root=args.out_root,
            limit=args.limit,
            jobs=args.jobs,
            cookies=args.cookies,
            subtitle_langs=tuple(lang.strip() for lang in args.subtitle_langs.split(",") if lang.strip()),
            ocr_langs=args.ocr_langs,
            transcriber=args.transcriber,
            whisper_model=args.whisper_model,
            llm=llm,
        )
        output = run_pipeline(config)
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
