"""Chunker — Tạo chunks_v2 từ sách đã restore.

2 mode:
- `page_as_chunk`: cho sách OCR đã chia trang (vd. trung-chau-tu-vi-dau-so-2/pages/p*.md).
  Mỗi page = 1 chunk + LLM gen summary + forward_summary.
- `iterative_split`: cho sách raw markdown (future). Iterative text splitting với forward-summary
  recursive theo PIKE-RAG Insight #4.

MVP focus: mode `page_as_chunk` cho Trung Châu Q2.

Usage:
    python3 -m engine.atomization.chunker --book trung-chau-tu-vi-dau-so-2 --pages 1-20
    python3 -m engine.atomization.chunker --book trung-chau-tu-vi-dau-so-2  # all pages
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.ai.providers.minimax import MiniMaxProvider  # noqa: E402
from engine.ai.providers.base import ProviderError  # noqa: E402

DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
BOOKS_DIR = PROJECT_ROOT / "data" / "restored_books"


SUMMARY_PROMPT = """# Nhiệm vụ
Đọc đoạn văn dưới (1 trang sách Tử Vi/Bát Tự). Tóm tắt NGẮN GỌN nội dung chính.

QUY TẮC:
- Tối đa 3 câu. ~50-80 từ.
- Nêu rõ tên sao, cung, cách cục được nói trong đoạn.
- KHÔNG suy đoán ngoài đoạn.

# Context (tóm tắt các trang TRƯỚC đó nếu có)
{forward_summary}

# Đoạn cần tóm tắt
{content}

# Output (chỉ summary thuần, không markdown, không prefix):
"""


def _open_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _list_pages(book: str, page_range: tuple[int, int] | None = None) -> list[tuple[int, Path]]:
    """Return sorted [(page_num, file_path)]."""
    pages_dir = BOOKS_DIR / book / "pages"
    if not pages_dir.exists():
        return []
    out = []
    for p in sorted(pages_dir.glob("p*.md")):
        m = re.match(r"p(\d+)\.md", p.name)
        if not m:
            continue
        page_num = int(m.group(1))
        if page_range and not (page_range[0] <= page_num <= page_range[1]):
            continue
        out.append((page_num, p))
    return out


def _existing_chunk_pages(book: str) -> set[int]:
    """Pages đã có chunks_v2 row → skip."""
    conn = _open_db()
    rows = conn.execute(
        "SELECT page_start FROM chunks_v2 WHERE book_corpus_id=?", (book,)
    ).fetchall()
    conn.close()
    return {r[0] for r in rows}


def _gen_summary(
    provider: MiniMaxProvider,
    content: str,
    forward_summary: str,
    model: str = "MiniMax-M2",
) -> tuple[str | None, int]:
    """Returns (summary_text, total_tokens)."""
    prompt = SUMMARY_PROMPT.replace("{content}", content).replace(
        "{forward_summary}", forward_summary or "(trang đầu sách)"
    )
    try:
        resp = provider.chat(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=0.3,  # low for summary determinism
            max_tokens=400,
        )
    except ProviderError as e:
        print(f"   ⚠ Summary LLM fail: {e}")
        return None, 0
    return resp.content.strip(), resp.prompt_tokens + resp.completion_tokens


def chunk_book_pages(
    book: str,
    page_range: tuple[int, int] | None = None,
    skip_existing: bool = True,
    use_llm_summary: bool = True,
) -> None:
    """Mode page_as_chunk: 1 page → 1 chunks_v2 row."""
    pages = _list_pages(book, page_range)
    if not pages:
        sys.exit(f"❌ No pages found for book={book} range={page_range}")
    print(f"📚 Book: {book}")
    print(f"📄 Pages found: {len(pages)} (range: p{pages[0][0]:04d} → p{pages[-1][0]:04d})")

    existing = _existing_chunk_pages(book) if skip_existing else set()
    print(f"🔁 Skip existing: {len(existing)} pages already chunked")

    provider = None
    if use_llm_summary:
        keys = json.loads((PROJECT_ROOT / "data" / "ai_keys.json").read_text())
        provider = MiniMaxProvider(api_key=keys["minimax"])

    conn = _open_db()
    total_tok = 0
    forward_summary = ""  # accumulated through pages
    n_chunked = 0
    n_skipped = 0

    for idx, (page_num, path) in enumerate(pages, 1):
        if page_num in existing:
            n_skipped += 1
            continue

        text = path.read_text(encoding="utf-8").strip()
        if len(text) < 50:
            print(f"  [{idx}/{len(pages)}] p{page_num:04d}: ⏭ too short ({len(text)} chars)")
            n_skipped += 1
            continue

        # LLM summary
        summary = None
        if provider:
            print(f"  [{idx}/{len(pages)}] p{page_num:04d}: {len(text)} chars → summary...", end="", flush=True)
            summary, tok = _gen_summary(provider, text, forward_summary)
            total_tok += tok
            if summary:
                print(f" ✅ {len(summary)} chars · {tok} tok")
            else:
                print(f" ⚠ summary fail, persist without")
        else:
            print(f"  [{idx}/{len(pages)}] p{page_num:04d}: {len(text)} chars (no summary)")

        # Insert chunks_v2
        cur = conn.execute(
            """INSERT INTO chunks_v2 (book_corpus_id, page_start, page_end, text, summary, forward_summary)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (book, page_num, page_num, text, summary, forward_summary),
        )
        chunk_id = cur.lastrowid
        conn.commit()
        n_chunked += 1

        # Update forward_summary: append current to context for next iteration
        if summary:
            # Keep forward_summary bounded (~1500 chars total) — drop oldest
            new_fs = (forward_summary + f"\n[p{page_num}] {summary}").strip()
            if len(new_fs) > 1500:
                # Drop first lines
                lines = new_fs.split("\n")
                while len("\n".join(lines)) > 1500 and len(lines) > 3:
                    lines.pop(0)
                new_fs = "\n".join(lines)
            forward_summary = new_fs

    conn.close()
    print(f"\n✅ Chunked {n_chunked} pages · ⏭ Skipped {n_skipped}")
    print(f"📊 Total tokens (summary): {total_tok}")


def _parse_range(s: str) -> tuple[int, int]:
    if "-" in s:
        a, b = s.split("-", 1)
        return (int(a), int(b))
    n = int(s)
    return (n, n)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True, help="vd. trung-chau-tu-vi-dau-so-2")
    parser.add_argument("--pages", default=None, help="vd. 1-20 hoặc 347. Default: all")
    parser.add_argument("--no-summary", action="store_true", help="Skip LLM summary (just chunk)")
    parser.add_argument("--force", action="store_true", help="Re-chunk existing pages")
    args = parser.parse_args()

    page_range = _parse_range(args.pages) if args.pages else None
    chunk_book_pages(
        book=args.book,
        page_range=page_range,
        skip_existing=not args.force,
        use_llm_summary=not args.no_summary,
    )


if __name__ == "__main__":
    main()
