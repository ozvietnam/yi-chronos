"""Cron job: scan all phe_menh_sau cache files → extract to wiki.

Usage:
  .venv/bin/python3 scripts/cron_extract_phe_menh_to_wiki.py
  .venv/bin/python3 scripts/cron_extract_phe_menh_to_wiki.py --dry-run
  .venv/bin/python3 scripts/cron_extract_phe_menh_to_wiki.py --force-all  # re-extract all (skip last-run check)

Cron suggestion (daily 3am):
  0 3 * * * cd /Users/ozvietnamdesktop/Desktop/yi && .venv/bin/python3 scripts/cron_extract_phe_menh_to_wiki.py >> /tmp/yi_wiki_extract.log 2>&1
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
sys.path.insert(0, str(PROJECT_ROOT))

from engine.tu_vi.wiki_extractor import extract_phe_menh_to_wiki

CACHE_ROOT = PROJECT_ROOT / "data/yi_publishing/analysis_cache"
LOG_FILE = PROJECT_ROOT / "data/wiki_extract_log.json"


def load_log() -> dict:
    if LOG_FILE.exists():
        try:
            with LOG_FILE.open() as f:
                return json.load(f)
        except Exception:
            return {"last_run": 0, "processed_files": {}}
    return {"last_run": 0, "processed_files": {}}


def save_log(log: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("w") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def scan_cache_files() -> list[Path]:
    """Find all phe_menh_sau.json under analysis_cache/u*/."""
    return list(CACHE_ROOT.glob("u*/*/phe_menh_sau.json"))


def main():
    dry_run = "--dry-run" in sys.argv
    force_all = "--force-all" in sys.argv

    log = load_log()
    last_run = log.get("last_run", 0)
    processed = log.get("processed_files", {})

    files = scan_cache_files()
    print(f"📂 Scanning {CACHE_ROOT}")
    print(f"   Found {len(files)} phe_menh_sau cache files")
    print(f"   Last run: {time.strftime('%Y-%m-%d %H:%M', time.localtime(last_run)) if last_run else 'never'}")
    print(f"   Mode: {'DRY-RUN' if dry_run else 'LIVE'} {'(force-all)' if force_all else ''}")
    print()

    total_added_quotes = 0
    total_added_cach = 0
    files_processed = 0
    files_skipped = 0

    for f in sorted(files):
        rel = str(f.relative_to(PROJECT_ROOT))
        mtime = f.stat().st_mtime
        prev_mtime = processed.get(rel, 0)
        # Skip if not modified since last extract (unless force-all)
        if not force_all and mtime <= prev_mtime:
            files_skipped += 1
            continue
        try:
            with f.open() as fh:
                data = json.load(fh)
        except Exception as e:
            print(f"⚠️  Cannot read {rel}: {e}")
            continue
        if data.get("status") != "ok":
            files_skipped += 1
            continue

        if dry_run:
            print(f"📝 [DRY] Would extract: {rel}")
            files_processed += 1
            continue

        result = extract_phe_menh_to_wiki(data, verbose=False)
        added_q = result.get("added_quotes", 0)
        added_c = result.get("added_cach_cuc", 0)
        total_added_quotes += added_q
        total_added_cach += added_c
        files_processed += 1
        processed[rel] = mtime
        print(f"✅ {rel}: +{added_q} phú, +{added_c} cách cục")

    if not dry_run:
        log["last_run"] = int(time.time())
        log["processed_files"] = processed
        log["last_summary"] = {
            "ts": log["last_run"],
            "files_processed": files_processed,
            "files_skipped": files_skipped,
            "added_quotes": total_added_quotes,
            "added_cach_cuc": total_added_cach,
        }
        save_log(log)

    print()
    print(f"📊 Summary:")
    print(f"   Processed: {files_processed} files")
    print(f"   Skipped (no changes): {files_skipped} files")
    print(f"   📚 Added to wiki: {total_added_quotes} phú + {total_added_cach} cách cục")
    if not dry_run:
        print(f"   📝 Log saved: {LOG_FILE}")


if __name__ == "__main__":
    main()
