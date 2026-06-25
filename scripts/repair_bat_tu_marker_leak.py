#!/usr/bin/env python3
"""PHA E repair — vá 6 passage bát-tự lọt marker (<!-- ... -->) đã ingest.

Phát hiện sau PHA D: 6/2242 passage còn marker HTML comment trong raw_text mà
verify report (sample 5 random) bỏ sót:
  - 5 trang: nội dung THỰC nhưng đuôi còn `*** <!-- trang trống -->` → STRIP marker,
    GIỮ NGUYÊN nội dung (concept links vẫn đúng vì đến từ nội dung, không từ marker).
  - 1 trang (pid 5166, tu-xem p1): rác cleanup hoàn toàn (LLM trả HTML error dump +
    OCR nhiễu, KHÔNG phải nội dung sách) → DELETE hẳn (không concept link nào trỏ tới).

AN TOÀN:
  (1) BACKUP wiki.sqlite3 → .bak-<stamp> TRƯỚC khi ghi.
  (2) IDEMPOTENT: chỉ chạm row còn '<!--'; chạy lại = no-op.
  (3) KHÔNG cắt cụt: dùng đúng strip_comments() của script ingest.
  (4) FTS5 tự đồng bộ qua trigger UPDATE/DELETE trên passages.
  (5) KHÔNG đụng prod/VPS, KHÔNG đụng corpus Tử Vi.

Usage:
  .venv/bin/python3 scripts/repair_bat_tu_marker_leak.py
"""
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ingest_bat_tu_thieu_vi_hoa import strip_comments, BOOKS  # noqa: E402
from engine.yi_wiki.store import get_store  # noqa: E402

DB = ROOT / "data/yi_wiki/wiki.sqlite3"
CORPORA = [b[0] for b in BOOKS]
# Trang rác cleanup hoàn toàn → DELETE (không phải nội dung sách).
DELETE_PIDS = {5166}


def main() -> None:
    if not DB.exists():
        print(f"DB not found: {DB}", file=sys.stderr)
        sys.exit(1)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup = DB.parent / f"wiki.sqlite3.bak-{stamp}"
    shutil.copy2(DB, backup)
    print(f"BACKUP: {backup.name}")

    store = get_store()
    placeholders = ",".join("?" for _ in CORPORA)
    fixed = deleted = unchanged = 0
    with store._conn() as conn:
        rows = conn.execute(
            f"SELECT passage_id, corpus_id, page_start, raw_text FROM passages "
            f"WHERE corpus_id IN ({placeholders}) AND raw_text LIKE '%<!--%'",
            CORPORA,
        ).fetchall()
        print(f"Rows with marker leak: {len(rows)}")
        for r in rows:
            pid = r["passage_id"]
            if pid in DELETE_PIDS:
                conn.execute("DELETE FROM passages WHERE passage_id=?", (pid,))
                deleted += 1
                print(f"  DELETE pid={pid} ({r['corpus_id']} p{r['page_start']}) — rác cleanup")
                continue
            cleaned = strip_comments(r["raw_text"])
            if cleaned == r["raw_text"]:
                unchanged += 1
                continue
            # UPDATE trigger passages_au tự cập nhật FTS.
            conn.execute(
                "UPDATE passages SET raw_text=?, summary_50w=? WHERE passage_id=?",
                (cleaned, cleaned[:200], pid),
            )
            fixed += 1
            print(f"  FIX    pid={pid} ({r['corpus_id']} p{r['page_start']}) "
                  f"len {len(r['raw_text'])}->{len(cleaned)}")
        conn.commit()

    # Verify: no marker remains, FTS in sync.
    with store._conn() as conn:
        leak = conn.execute(
            f"SELECT COUNT(*) FROM passages WHERE corpus_id IN ({placeholders}) "
            f"AND raw_text LIKE '%<!--%'", CORPORA,
        ).fetchone()[0]
        tot = conn.execute("SELECT COUNT(*) FROM passages").fetchone()[0]
        fts = conn.execute("SELECT COUNT(*) FROM passages_fts").fetchone()[0]

    print(f"\n=== KẾT QUẢ ===")
    print(f"  fixed={fixed} deleted={deleted} unchanged={unchanged}")
    print(f"  marker leak còn lại (5 corpus bát-tự): {leak}")
    print(f"  passages total: {tot} (FTS rows: {fts})")
    print(f"  backup: {backup.name}")
    if leak != 0 or tot != fts:
        print("  ⚠️  CHƯA SẠCH — kiểm tra lại!", file=sys.stderr)
        sys.exit(2)
    print("  ✓ sạch + FTS đồng bộ")


if __name__ == "__main__":
    main()
