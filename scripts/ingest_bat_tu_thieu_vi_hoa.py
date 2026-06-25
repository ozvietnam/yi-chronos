#!/usr/bin/env python3
"""PHA A — Ingest 5 cuốn Bát Tự (Thiệu Vĩ Hoa, author_id=10) vào wiki passages.

Mỗi TRANG thực (`<!-- page N -->`) = 1 passage (page_start=page_end=N), raw_text =
NGUYÊN văn trang. Trang >4000 ký tự → split theo ranh giới đoạn (KHÔNG cắt cụt).
Trang trống / <50 ký tự thực → skip. concepts_mentioned scan theo concept_index
school tu_binh_ba_tu (canonical_vi/zh) → link 2 chiều qua append_concept_passage.

TÁI DÙNG: WikiStore.insert_passage() (FTS5 trigger tự cập nhật) + page-parse regex
`<!-- page N -->` (pattern scripts/ingest_reading_round.py) + pattern register
works (engine/yi_publishing/q1_wiki_import.py).

AN TOÀN:
  (1) BACKUP wiki.sqlite3 → .bak-<stamp> TRƯỚC khi ghi.
  (2) IDEMPOTENT: skip nếu đã có (corpus_id, page_start, page_end).
  (3) KHÔNG silent-truncate: split ở ranh giới đoạn.
  (4) Skip trang trống / <50 ký tự thực.
  (5) KHÔNG đụng prod/VPS, KHÔNG đụng corpus Tử Vi.

Usage:
  .venv/bin/python3 scripts/ingest_bat_tu_thieu_vi_hoa.py
"""
from __future__ import annotations

import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.yi_wiki.store import get_store  # noqa: E402
from engine.yi_wiki.models import Passage, Work  # noqa: E402

DB = ROOT / "data/yi_wiki/wiki.sqlite3"
AUTHOR_ID = 10  # Thiệu Vĩ Hoa (邵伟华) — đã có sẵn
SCHOOL = "tu_binh_ba_tu"
MAX_CHARS = 4000          # >MAX_CHARS → split theo đoạn
MIN_REAL_CHARS = 50       # <MIN_REAL_CHARS ký tự thực → trang trống, skip

# (slug = corpus_id, title_vi, title_zh)
BOOKS = [
    ("du-doan-tu-tru-thieu-vy-hoa",
     "Dự Đoán Theo Tứ Trụ", "四柱預測學"),
    ("bat-tu-ha-lac-va-quy-dao-doi-nguoi",
     "Bát Tự Hà Lạc Và Quỹ Đạo Đời Người", "八字河洛與人生軌道"),
    ("du-bao-theo-tu-binh",
     "Dự Báo Theo Tử Bình", "子平預測"),
    ("chu-dich-du-doan-cac-vi-du-co-giai-thieu-vi-hoa",
     "Chu Dịch Dự Đoán — Các Ví Dụ Cổ Giải", "周易預測例題解"),
    ("tu-xem-van-menh-theo-tu-tru",
     "Tự Xem Vận Mệnh Theo Tứ Trụ", "自己學算四柱"),
]

# Trang trống marker thường gặp trong restored_books
_BLANK_RE = re.compile(r"trang\s*trống", re.IGNORECASE)
# MỌI HTML comment (<!-- ... -->), kể cả nhiều dòng — strip khỏi raw_text trang.
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# Trang lỗi cleanup (LLM trả HTML error dump) → KHÔNG phải trang thực, skip.
_ERROR_PAGE_RE = re.compile(r"ERROR\s*cleanup|Internal Server Error", re.IGNORECASE)
# Separator artifact (dòng chỉ gồm '***') còn sót sau khi bỏ comment.
_SEP_RE = re.compile(r"^[ \t]*\*{3,}[ \t]*$", re.MULTILINE)


def strip_comments(text: str) -> str:
    """Bỏ MỌI HTML comment + separator '***' lẻ; gom whitespace dư.

    KHÔNG cắt cụt nội dung thực — chỉ loại marker (<!-- trang trống -->,
    <!-- ERROR cleanup -->, ...) và dòng '***' phân cách trang còn sót."""
    text = _COMMENT_RE.sub("", text)
    text = _SEP_RE.sub("", text)
    # gom >2 dòng trống liên tiếp về 2 (giữ ranh giới đoạn cho split_by_paragraph)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_pages(content_md: Path) -> list[tuple[int, str, bool]]:
    """Trả [(page_num, clean_text, is_error_page)] theo marker <!-- page N -->.

    is_error_page = trang chứa marker ERROR-cleanup (LLM trả HTML error) →
    caller skip hẳn (đây là rác cleanup, KHÔNG phải nội dung sách)."""
    raw = content_md.read_text(encoding="utf-8")
    parts = re.split(r"<!-- page (\d+) -->", raw)
    out: list[tuple[int, str, bool]] = []
    for i in range(1, len(parts), 2):
        num = int(parts[i])
        page_raw = parts[i + 1]
        is_err = bool(_ERROR_PAGE_RE.search(page_raw))
        out.append((num, strip_comments(page_raw), is_err))
    return out


def _real_len(text: str) -> int:
    """Số ký tự thực (bỏ whitespace) để phát hiện trang trống."""
    return len(re.sub(r"\s+", "", text))


def is_blank(text: str) -> bool:
    if _real_len(text) < MIN_REAL_CHARS:
        return True
    if _BLANK_RE.fullmatch(text.strip()):
        return True
    return False


def split_by_paragraph(text: str, limit: int = MAX_CHARS) -> list[str]:
    """Split text dài ở ranh giới đoạn (\\n\\n), KHÔNG cắt cụt mất chữ.

    Gộp các đoạn lại tới khi gần `limit`; 1 đoạn đơn lẻ vượt limit thì giữ
    NGUYÊN (thà 1 passage hơi dài còn hơn cắt mất chữ giữa câu)."""
    if len(text) <= limit:
        return [text]
    paras = re.split(r"\n\s*\n", text)
    chunks: list[str] = []
    cur = ""
    for p in paras:
        p = p.strip()
        if not p:
            continue
        if cur and len(cur) + len(p) + 2 > limit:
            chunks.append(cur)
            cur = p
        else:
            cur = f"{cur}\n\n{p}" if cur else p
    if cur:
        chunks.append(cur)
    return chunks or [text]


def build_concept_table(store) -> list[tuple[int, str, str]]:
    """[(concept_id, canonical_vi, canonical_zh)] cho school tu_binh_ba_tu."""
    with store._conn() as conn:
        rows = conn.execute(
            "SELECT concept_id, canonical_vi, canonical_zh FROM concept_index "
            "WHERE school LIKE '%binh%'"
        ).fetchall()
    table = []
    for r in rows:
        vi = (r["canonical_vi"] or "").strip()
        zh = (r["canonical_zh"] or "").strip()
        table.append((r["concept_id"], vi, zh))
    return table


def scan_concepts(text: str, table: list[tuple[int, str, str]]) -> list[int]:
    """Tìm concept (canonical_vi hoặc canonical_zh) xuất hiện trong text trang.

    - Hán (zh): match trực tiếp substring (chữ Hán không có khoảng trắng).
    - Việt (vi): match word-boundary, case-insensitive, để tránh false-positive
      kiểu 'Bổ' khớp 'bổ sung' — nhưng Hán-Việt thuật ngữ thường viết hoa nên
      ta dùng so khớp có biên từ trên text gốc giữ nguyên hoa/thường.
    """
    found: set[int] = set()
    low = text.lower()
    for cid, vi, zh in table:
        if zh and zh in text:
            found.add(cid)
            continue
        if vi:
            # word-boundary, không phân biệt hoa thường; vi có dấu nên \b ổn với re.UNICODE
            if re.search(r"(?<![\wÀ-ỹ])" + re.escape(vi.lower()) + r"(?![\wÀ-ỹ])", low):
                found.add(cid)
    return sorted(found)


def existing_pages(store, corpus_id: str) -> set[tuple[int, int]]:
    with store._conn() as conn:
        rows = conn.execute(
            "SELECT page_start, page_end FROM passages WHERE corpus_id=?",
            (corpus_id,),
        ).fetchall()
    return {(r["page_start"], r["page_end"]) for r in rows}


def ensure_work(store, corpus_id: str, title_vi: str, title_zh: str) -> bool:
    """Register work nếu chưa có (idempotent). Trả True nếu vừa tạo."""
    for w in store.list_works(author_id=AUTHOR_ID):
        if w.get("corpus_id") == corpus_id:
            return False
    store.upsert_work(Work(
        author_id=AUTHOR_ID,
        title_vi=title_vi,
        title_zh=title_zh,
        role="translation",
        corpus_id=corpus_id,
        is_canonical=True,
        notes=f"Bát Tự — Thiệu Vĩ Hoa (school {SCHOOL})",
    ))
    return True


def ingest_book(store, slug: str, title_vi: str, title_zh: str,
                concept_table: list[tuple[int, str, str]]) -> dict:
    book_dir = ROOT / "data/restored_books" / slug
    content_md = book_dir / "content.md"
    if not content_md.exists():
        return {"slug": slug, "error": "content.md not found"}

    created_work = ensure_work(store, slug, title_vi, title_zh)
    done = existing_pages(store, slug)
    pages = parse_pages(content_md)

    inserted = 0
    skipped_existing = 0
    skipped_blank = 0
    skipped_error = 0
    concept_links = 0
    linked_concept_ids: set[int] = set()

    for num, text, is_err in pages:
        if (num, num) in done:
            skipped_existing += 1
            continue
        if is_err:
            # Trang lỗi cleanup (HTML error dump + OCR rác) — KHÔNG phải sách.
            skipped_error += 1
            continue
        if is_blank(text):
            skipped_blank += 1
            continue
        segments = split_by_paragraph(text, MAX_CHARS)
        for seg in segments:
            if is_blank(seg):
                continue
            cids = scan_concepts(seg, concept_table)
            topic = f"Trang {num}" if len(segments) == 1 else f"Trang {num} (phần)"
            pid = store.insert_passage(Passage(
                author_id=AUTHOR_ID,
                corpus_id=slug,
                page_start=num,
                page_end=num,
                raw_text=seg,
                topic=topic,
                summary_50w=seg[:200],
                concepts_mentioned=cids,
                is_canonical=True,
            ))
            inserted += 1
            for cid in cids:
                store.append_concept_passage(cid, pid)
                concept_links += 1
                linked_concept_ids.add(cid)

    return {
        "slug": slug,
        "created_work": created_work,
        "inserted": inserted,
        "skipped_existing": skipped_existing,
        "skipped_blank": skipped_blank,
        "skipped_error": skipped_error,
        "concept_links": concept_links,
        "distinct_concepts_linked": len(linked_concept_ids),
        "_linked_ids": linked_concept_ids,
    }


def main() -> None:
    if not DB.exists():
        print(f"DB not found: {DB}", file=sys.stderr)
        sys.exit(1)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup = DB.parent / f"wiki.sqlite3.bak-{stamp}"
    shutil.copy2(DB, backup)
    print(f"BACKUP: {backup.name}")

    store = get_store()
    concept_table = build_concept_table(store)
    print(f"Concept table (school binh): {len(concept_table)} concepts")

    results = []
    all_linked: set[int] = set()
    total_inserted = 0
    for slug, title_vi, title_zh in BOOKS:
        r = ingest_book(store, slug, title_vi, title_zh, concept_table)
        results.append(r)
        all_linked |= r.pop("_linked_ids", set())
        total_inserted += r.get("inserted", 0)
        print(f"  {slug}: inserted={r.get('inserted')} "
              f"skip_existing={r.get('skipped_existing')} "
              f"skip_blank={r.get('skipped_blank')} "
              f"skip_error={r.get('skipped_error')} "
              f"concept_links={r.get('concept_links')} "
              f"work_created={r.get('created_work')}")

    print("\n=== TỔNG ===")
    print(f"  passages inserted: {total_inserted}")
    print(f"  distinct concepts (thập thần + Bát Tự) linked: {len(all_linked)}")
    print(f"  backup: {backup.name}")

    # FTS5 sanity (trigger tự cập nhật)
    with store._conn() as conn:
        fts = conn.execute("SELECT COUNT(*) FROM passages_fts").fetchone()[0]
        tot = conn.execute("SELECT COUNT(*) FROM passages").fetchone()[0]
    print(f"  passages total now: {tot} (FTS rows: {fts})")


if __name__ == "__main__":
    main()
