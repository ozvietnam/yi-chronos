"""CLI: Run Smart Book Onboarding Pipeline on one book.

Usage:
    python3 scripts/onboard_book.py <book_id> [--samples N]

Example:
    python3 scripts/onboard_book.py shao-yong-shao-yuan-heng-etc-z-library-sk-1lib-sk-z-lib-sk --samples 3

Reads PDF from data/raw_pdfs/<book_id>.pdf
Writes artifacts to data/yi_publishing/onboarding/<book_id>/
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Ensure project root on path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from engine.yi_publishing.onboarding import onboard_book

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)


def main():
    ap = argparse.ArgumentParser(description="Smart Book Onboarding Pipeline")
    ap.add_argument("book_id", help="book slug (filename without .pdf in raw_pdfs)")
    ap.add_argument(
        "--samples", type=int, default=3,
        help="number of sample pages for profile spike (default 3, real MinerU ~21s each × 2 configs)",
    )
    ap.add_argument(
        "--skip-thumbnails", action="store_true",
        help="skip thumbnail rendering (use cached page_types.json)",
    )
    args = ap.parse_args()

    pdf_path = PROJECT_ROOT / "data" / "raw_pdfs" / f"{args.book_id}.pdf"
    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = PROJECT_ROOT / "data" / "yi_publishing" / "onboarding" / args.book_id

    print(f"📚 Onboarding: {args.book_id}")
    print(f"   PDF: {pdf_path}")
    print(f"   Output: {output_dir}")
    print(f"   Samples: {args.samples} pages × 2 spike configs")
    print()

    summary = onboard_book(
        book_id=args.book_id,
        pdf_path=pdf_path,
        output_dir=output_dir,
        n_sample_pages=args.samples,
        skip_thumbnails=args.skip_thumbnails,
    )

    print()
    print("✅ Onboarding complete")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
