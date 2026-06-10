#!/usr/bin/env python3
"""Retranslate pages with missing line translations via the running API server.

Calls POST /api/yi-publishing/pages/{book_id}/{page}/auto-translate
(overwrite=false → only untranslated lines get filled).

Usage:
    python3 scripts/retranslate_missing_pages.py <book_id> \
        --pages 159,230,252 [--token-file /tmp/yi_owner_token] \
        [--base http://localhost:8001] [--delay 2]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request


def call_translate(base: str, token: str, book_id: str, page: int, timeout: int = 600,
                   overwrite: bool = False) -> dict:
    url = f"{base}/api/yi-publishing/pages/{book_id}/{page}/auto-translate"
    body = json.dumps({"overwrite": overwrite}).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json", "X-Session-Token": token},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("book_id")
    ap.add_argument("--pages", required=True, help="comma-separated page numbers")
    ap.add_argument("--token-file", default="/tmp/yi_owner_token")
    ap.add_argument("--base", default="http://localhost:8001")
    ap.add_argument("--delay", type=float, default=2.0)
    ap.add_argument("--overwrite", action="store_true",
                    help="dịch đè TOÀN BỘ dòng của trang (sửa trang dịch hỏng)")
    args = ap.parse_args()

    token = open(args.token_file).read().strip()
    pages = [int(p) for p in args.pages.split(",") if p.strip()]
    print(f"[retranslate] {args.book_id}: {len(pages)} pages", flush=True)

    ok = 0
    failed = []
    t0 = time.time()
    for i, page in enumerate(pages, 1):
        if i > 1 and args.delay > 0:
            time.sleep(args.delay)
        t1 = time.time()
        try:
            r = call_translate(args.base, token, args.book_id, page, overwrite=args.overwrite)
        except Exception as e:
            print(f"[{i}/{len(pages)}] p{page:04d} EXC: {e}", flush=True)
            failed.append(page)
            continue
        status = r.get("status")
        att = r.get("total_lines_attempted", 0)
        tr = r.get("total_lines_translated", 0)
        model = (r.get("stats") or {}).get("model_used", "?")
        dt = time.time() - t1
        if status == "ok" and (tr > 0 or att == 0):
            ok += 1
            print(f"[{i}/{len(pages)}] p{page:04d} ok {tr}/{att} lines via {model} ({dt:.0f}s)", flush=True)
        else:
            failed.append(page)
            print(f"[{i}/{len(pages)}] p{page:04d} PROBLEM status={status} {tr}/{att} msg={r.get('message','')[:120]}", flush=True)

    total_min = (time.time() - t0) / 60
    print(f"[retranslate] DONE: {ok}/{len(pages)} pages ok in {total_min:.1f} min", flush=True)
    if failed:
        print(f"[retranslate] FAILED pages: {','.join(map(str, failed))}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
