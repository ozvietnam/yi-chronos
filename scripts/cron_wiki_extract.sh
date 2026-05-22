#!/bin/bash
# Cron wrapper for nightly wiki extraction from phê mệnh sâu cache
# Runs from /Users/ozvietnamdesktop/Desktop/yi (project root)

set -e
cd /Users/ozvietnamdesktop/Desktop/yi
.venv/bin/python3 scripts/cron_extract_phe_menh_to_wiki.py
