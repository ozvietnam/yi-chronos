"""Batch Atomize — Run Atomizer trên N chunks chưa atomize.

Usage:
    python3 -m engine.atomization.batch_atomize --book trung-chau-tu-vi-dau-so-2 --limit 20
    python3 -m engine.atomization.batch_atomize --book trung-chau-tu-vi-dau-so-2 --all
    python3 -m engine.atomization.batch_atomize --book trung-chau-tu-vi-dau-so-2 --pages 100-150
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.atomization.atomizer import Atomizer  # noqa: E402

DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"


def fetch_pending_chunks(
    book: str,
    page_range: tuple[int, int] | None = None,
    limit: int | None = None,
) -> list[tuple[int, int, str]]:
    """Return [(chunk_id, page_start, text)] chưa atomize."""
    conn = sqlite3.connect(DB_PATH)
    sql = """
        SELECT c.chunk_id, c.page_start, c.text
        FROM chunks_v2 c
        LEFT JOIN chunk_classifications cc ON cc.chunk_id = c.chunk_id
        WHERE c.book_corpus_id = ?
          AND cc.cc_id IS NULL
    """
    params = [book]
    if page_range:
        sql += " AND c.page_start BETWEEN ? AND ?"
        params.extend(page_range)
    sql += " ORDER BY c.page_start"
    if limit:
        sql += f" LIMIT {limit}"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True)
    parser.add_argument("--pages", help="vd 100-150")
    parser.add_argument("--limit", type=int, help="max chunks to atomize this run")
    parser.add_argument("--all", action="store_true", help="atomize all pending")
    parser.add_argument("--no-sync", action="store_true",
                        help="bỏ qua auto-sync wiki.sqlite3 lên VPS cuối run")
    args = parser.parse_args()

    page_range = None
    if args.pages:
        a, b = args.pages.split("-", 1)
        page_range = (int(a), int(b))

    limit = None if args.all else (args.limit or 20)

    pending = fetch_pending_chunks(args.book, page_range, limit)
    if not pending:
        print(f"✅ Nothing pending for book={args.book} range={page_range}")
        return
    print(f"📋 {len(pending)} chunks pending atomize")
    print(f"📚 Book: {args.book}")
    if page_range:
        print(f"📄 Range: p{page_range[0]:04d} → p{page_range[1]:04d}")
    print()

    atomizer = Atomizer()
    print(f"🔧 Provider: {atomizer.provider.name}/{atomizer.model}\n")

    t_start = time.time()
    total_atoms = 0
    total_tokens = 0
    success = 0
    fail = 0

    for idx, (chunk_id, page, text) in enumerate(pending, 1):
        t1 = time.time()
        print(f"  [{idx}/{len(pending)}] chunk_id={chunk_id} p{page:04d} ({len(text)} chars)...", end="", flush=True)
        result = atomizer.atomize_chunk(chunk_id, text, args.book, skip_if_exists=True)
        d = time.time() - t1
        if result.error:
            print(f" ❌ {d:.1f}s · {result.error[:80]}")
            fail += 1
        else:
            n = len(result.atomic_questions)
            print(f" ✅ {d:.1f}s · {n} atoms · {result.total_tokens} tok")
            success += 1
            total_atoms += n
            total_tokens += result.total_tokens

    elapsed = time.time() - t_start
    print(f"\n{'═'*60}")
    print(f"✅ Success: {success}/{len(pending)} chunks")
    print(f"❌ Fail: {fail}/{len(pending)} chunks")
    print(f"📌 Total atomic Q: {total_atoms}")
    print(f"📊 Total tokens: {total_tokens}")
    print(f"⏱  Total time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    if success > 0:
        print(f"📈 Avg per chunk: {elapsed/success:.1f}s · {total_atoms/success:.1f} atoms · {total_tokens/success:.0f} tok")

    # Auto-sync lên VPS — data KHÔNG tự deploy theo CI (lesson 2026-06-11:
    # live lệch nửa ngày vì quên chạy tay). Best-effort, không fail run.
    if success > 0 and not args.no_sync:
        import subprocess
        sync_sh = PROJECT_ROOT / "scripts" / "sync-atoms-to-vps.sh"
        print("\n🔄 Auto-sync wiki.sqlite3 → VPS ...")
        try:
            r = subprocess.run([str(sync_sh)], capture_output=True, text=True, timeout=300)
            tail = (r.stdout or "").strip().splitlines()[-1:] or ["(no output)"]
            print(f"   {'✅' if r.returncode == 0 else '⚠'} {tail[0]}")
        except Exception as e:
            print(f"   ⚠ sync fail (chạy tay scripts/sync-atoms-to-vps.sh): {str(e)[:100]}")


if __name__ == "__main__":
    main()
