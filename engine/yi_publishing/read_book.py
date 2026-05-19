"""read_book.py — orchestrator 7-step Bookflow v2.0 cho mỗi phiên đọc sách.

Mỗi phiên đọc sách = 1 lệnh duy nhất:

    .venv/bin/python -m engine.yi_publishing.read_book \\
        --pdf "thư viện sách/.../sach-x.pdf" \\
        --book-id sach-x \\
        --title "Tên Việt của sách" \\
        --author "Tác giả" \\
        --school tu_vi --tier S \\
        --pages 1-50

Script chạy đủ 7 bước:
    1. (Library)        Register vào corpora (idempotent)
    2. (OCR)            MinerU layout-aware parse
    3. (Translate)      Auto-batch dịch với paid fallback
    4. (Publish draft)  Build PDF nháp
    5. (Wiki)           Mở UI tab Term-catch (manual)
    6. (Deep read)      Generate gap analysis report
    7. (Upgrade ideas)  Append to UPGRADE-PROPOSALS.md

Bước 5-7 cần human-in-loop, script chỉ chuẩn bị artifacts.
"""
from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
MINERU_OUTPUT = PROJECT_ROOT / "data/yi_publishing_mineru"
PUBLISHED_ROOT = PROJECT_ROOT / "data/published"
MINERU_BIN = PROJECT_ROOT / ".venv-mineru/bin/mineru"
API_URL = "http://localhost:8000"


# ─── helpers ──────────────────────────────────────────────────────────────────

def _api_post(path: str, payload: dict, timeout: float = 1800) -> dict:
    req = urllib.request.Request(
        f"{API_URL}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _check_api() -> bool:
    try:
        with urllib.request.urlopen(f"{API_URL}/api/health", timeout=5) as r:
            json.loads(r.read())
            return True
    except Exception:
        return False


# ─── Step 1: register in library ─────────────────────────────────────────────

def step1_register_library(
    book_id: str,
    title: str,
    author: str,
    school: str,
    tier: str,
    file_path: Path,
    pages_total: int,
    notes: str = "",
) -> int:
    """Register corpus into thư viện (lexicon.corpora).

    Idempotent — first matches by file_path (most reliable), then by exact name.
    """
    import sqlite3
    rel_path = str(file_path.relative_to(PROJECT_ROOT))

    db = sqlite3.connect(PROJECT_ROOT / "data/yi_lexicon/lexicon.sqlite3")
    # Match by file_path first
    row = db.execute(
        "SELECT corpus_id, name FROM corpora WHERE file_path = ?",
        (rel_path,),
    ).fetchone()
    if row:
        logger.info(f"  📚 Library: reuse #{row[0]} — {row[1][:50]} (matched by file_path)")
        db.close()
        return row[0]
    db.close()

    from engine.yi_lexicon.store import add_corpus
    corpus = add_corpus(
        name=title,
        author=author,
        school=school,
        language="zh",
        file_path=rel_path,
        notes=notes,
        status="in_progress",
        tier=tier,
        tier_decided_by="read_book.py",
        pages_total=pages_total,
        schools_tags=[school] if school else [],
    )
    logger.info(f"  📚 Library: created #{corpus.corpus_id} — {corpus.name[:50]}")
    return corpus.corpus_id


def _update_progress(corpus_id: int, *, pages_ingested: int,
                      pages_total: int, restored_path: str, status: str = "in_progress"):
    import sqlite3
    db = sqlite3.connect(PROJECT_ROOT / "data/yi_lexicon/lexicon.sqlite3")
    db.execute("""
        UPDATE corpora SET
            pages_ingested = ?, progress_percent = ?,
            restored_status = ?, restored_pages = ?,
            restored_path = ?, restored_at = ?,
            restore_method = ?
        WHERE corpus_id = ?
    """, (
        pages_ingested,
        round(pages_ingested / max(pages_total, 1) * 100, 2),
        status, pages_ingested, restored_path, int(time.time()),
        "mineru-layout-aware-pipeline-3.1.14", corpus_id,
    ))
    db.commit()
    db.close()


# ─── Step 2: OCR ─────────────────────────────────────────────────────────────

def step2_ocr(pdf_path: Path, book_id: str, start: int, end: int) -> Path:
    """Run MinerU pipeline backend."""
    out_dir = MINERU_OUTPUT
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(MINERU_BIN), "-p", str(pdf_path), "-o", str(out_dir),
        "-b", "pipeline", "-l", "ch",
        "-s", str(start), "-e", str(end), "-m", "auto",
    ]
    logger.info(f"  🔍 MinerU OCR pages {start}-{end}...")
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    elapsed = time.time() - t0
    if proc.returncode != 0:
        logger.error(f"MinerU stderr (last 500 chars):\n{proc.stderr[-500:]}")
        raise RuntimeError(f"MinerU failed with code {proc.returncode}")

    # Resolve output dir (auto/ or ocr/)
    book_dir = out_dir / book_id
    for sub in ("auto", "ocr"):
        candidate = book_dir / sub
        if (candidate / f"{book_id}_middle.json").exists():
            logger.info(f"  ✓ MinerU done in {elapsed:.1f}s → {candidate}")
            return candidate
    raise FileNotFoundError(f"No middle.json produced for {book_id}")


# ─── Step 3: Translate ───────────────────────────────────────────────────────

def step3_translate(book_id: str, start: int, end: int,
                    *, allow_paid_fallback: bool = True,
                    overwrite: bool = False) -> dict:
    """Call AUTO batch endpoint."""
    logger.info(f"  🇻🇳 Translating pages {start}-{end} (paid_fallback={allow_paid_fallback})...")
    t0 = time.time()
    payload = {
        "start_page": start, "end_page": end,
        "overwrite": overwrite,
        "delay_seconds": 2.0, "retry_on_429": 2,
        "allow_paid_fallback": allow_paid_fallback,
    }
    result = _api_post(f"/api/yi-publishing/books/{book_id}/auto-batch", payload, timeout=3600)
    elapsed = time.time() - t0
    s = result.get("summary", {})
    logger.info(
        f"  ✓ Translated in {elapsed:.1f}s: "
        f"{s.get('total_lines_translated', 0)}/{s.get('total_lines_attempted', 0)} lines, "
        f"FIT {s.get('avg_fit_score', 0)}%, "
        f"cost ${s.get('total_cost_usd', 0):.4f}, "
        f"paid pages {s.get('paid_pages_count', 0)}"
    )
    return result


# ─── Step 4: PDF draft ───────────────────────────────────────────────────────

def step4_publish_draft(book_id: str, title: str, hanzi_title: str,
                        author: str, edition: str,
                        start: int, end: int,
                        include_scan: bool = False) -> dict:
    """Build PDF draft."""
    from engine.yi_publishing.publisher import build_book
    logger.info(f"  📕 Building PDF (pages {start}-{end})...")
    t0 = time.time()
    result = build_book(
        book_id, title=title, hanzi_title=hanzi_title,
        author=author, edition=edition,
        include_scan=include_scan,
        page_range=(start, end),
    )
    logger.info(f"  ✓ PDF built in {time.time()-t0:.1f}s: {result['pdf_path']} ({result['pdf_size_kb']} KB)")
    return result


# ─── Step 5-6-7: deep-read prep ──────────────────────────────────────────────

def step5_wiki_hint(book_id: str, start: int, end: int) -> str:
    """Just print hint for human."""
    msg = (
        f"\n  📚 Bước 5 (Wiki) — human-in-loop:\n"
        f"     Mở UI: http://localhost:5173 → tab Workspace dịch sách\n"
        f"     Chọn book: {book_id}, trang {start}-{end}\n"
        f"     Tab 📑 Đối chiếu → bôi đen chữ Hán → modal Term-catch\n"
    )
    logger.info(msg)
    return msg


def step6_gap_analysis(book_id: str, start: int, end: int,
                       translate_result: dict) -> Path:
    """Generate gap analysis report (anh đọc rồi viết phản vấn)."""
    report_dir = PROJECT_ROOT / "docs/sessions"
    report_dir.mkdir(parents=True, exist_ok=True)
    today = time.strftime("%Y%m%d")
    report_path = report_dir / f"{book_id}-p{start}-{end}-{today}.md"

    s = translate_result.get("summary", {})
    pages_data = translate_result.get("pages", [])

    issue_count = 0
    issue_examples = []
    for p in pages_data:
        for iss in (p.get("issues") or [])[:2]:
            for w in iss.get("warnings", []):
                if w["level"] == "error":
                    issue_count += 1
                    if len(issue_examples) < 6:
                        issue_examples.append(
                            f"- p{p['page_num']} `{iss['source_preview'][:30]}` "
                            f"→ `{iss['target_preview'][:40]}` ({w['code']})"
                        )

    md = f"""# {book_id} — Phiên đọc {start}-{end} ({today})

## Tổng quan kết quả

| Metric | Value |
|---|---|
| Pages | {s.get('pages_processed', 0)} |
| Lines | {s.get('total_lines_translated', 0)} / {s.get('total_lines_attempted', 0)} |
| Avg FIT | {s.get('avg_fit_score', 0)}% |
| Errors | {s.get('total_errors', 0)} |
| Warnings | {s.get('total_warnings', 0)} |
| Cost | ${s.get('total_cost_usd', 0):.4f} |
| Paid pages | {s.get('paid_pages_count', 0)} |
| Elapsed | {s.get('batch_elapsed_seconds', 0)}s |

## Issues bắt được ({issue_count} errors total)

{chr(10).join(issue_examples) if issue_examples else '_(không có issue nào)_'}

## TODO cho Anh (Bước 6 — đọc sâu, phản vấn)

- [ ] Mở PDF nháp trong `data/published/{book_id}-...pdf` và đọc qua 1 lần
- [ ] Đánh dấu các khái niệm quan trọng cần thêm vào wiki
- [ ] Note các đoạn cần dịch lại / clarify
- [ ] Đặt câu hỏi nghiên cứu (research question) — ghi vào section dưới

## Phản vấn / Đề xuất (Bước 7)

_(em điền vào đây sau khi anh feedback)_

## Bước 7 — Ứng dụng UI

_(em sẽ propose feature cải tiến panel sau khi có anh feedback)_
"""
    report_path.write_text(md, encoding="utf-8")
    logger.info(f"  📝 Gap analysis report: {report_path}")
    return report_path


# ─── main ────────────────────────────────────────────────────────────────────

def run(
    pdf_path: Path, book_id: str,
    *, title: str, hanzi_title: str, author: str,
    school: str, tier: str, pages_total: int,
    notes: str,
    page_range: tuple[int, int],
    edition: str = "v0.1-draft",
    include_scan: bool = False,
    allow_paid_fallback: bool = True,
    overwrite: bool = False,
    skip_ocr: bool = False,
) -> dict:
    """Run full Bookflow v2.0 for one reading session."""
    start, end = page_range
    logger.info(f"━━━ 📖 Reading session: {book_id} pages {start}-{end} ━━━")
    t0 = time.time()

    if not _check_api():
        raise RuntimeError(
            "API server not running at localhost:8000. "
            "Start: .venv/bin/python -m uvicorn api.main:app --port 8000"
        )

    # Step 1: Library
    logger.info("━━━ Bước 1: Đăng ký thư viện ━━━")
    corpus_id = step1_register_library(
        book_id=book_id, title=title, author=author, school=school,
        tier=tier, file_path=pdf_path, pages_total=pages_total, notes=notes,
    )

    # Step 2: OCR
    logger.info("━━━ Bước 2: OCR layout-aware (MinerU) ━━━")
    if skip_ocr:
        ocr_dir = MINERU_OUTPUT / book_id / "auto"
        if not (ocr_dir / f"{book_id}_middle.json").exists():
            ocr_dir = MINERU_OUTPUT / book_id / "ocr"
        logger.info(f"  ⊘ Skip OCR; using existing {ocr_dir}")
    else:
        ocr_dir = step2_ocr(pdf_path, book_id, start, end)

    # Step 3: Translate
    logger.info("━━━ Bước 3: Dịch sang tiếng Việt ━━━")
    trans_result = step3_translate(
        book_id, start, end,
        allow_paid_fallback=allow_paid_fallback,
        overwrite=overwrite,
    )

    # Update library progress
    _update_progress(corpus_id, pages_ingested=end,
                     pages_total=pages_total,
                     restored_path=str(ocr_dir.parent.relative_to(PROJECT_ROOT)),
                     status="in_progress")

    # Step 4: PDF draft
    logger.info("━━━ Bước 4: Bản in nháp (PDF) ━━━")
    pdf_result = step4_publish_draft(
        book_id, title, hanzi_title, author, edition,
        start, end, include_scan=include_scan,
    )

    # Step 5: Wiki hint
    logger.info("━━━ Bước 5: Bổ sung wiki (Anh) ━━━")
    step5_wiki_hint(book_id, start, end)

    # Step 6: Gap analysis
    logger.info("━━━ Bước 6: Báo cáo gap (cho anh phản vấn) ━━━")
    gap_path = step6_gap_analysis(book_id, start, end, trans_result)

    # Step 7: UI prep (note in same report)
    logger.info("━━━ Bước 7: Đề xuất UI (chờ Anh feedback) ━━━")

    total_elapsed = time.time() - t0
    logger.info(f"\n━━━ ✓ DONE in {total_elapsed:.1f}s ━━━")

    return {
        "book_id": book_id,
        "corpus_id": corpus_id,
        "pages": [start, end],
        "translate_summary": trans_result.get("summary"),
        "pdf_path": pdf_result["pdf_path"],
        "gap_report": str(gap_path),
        "total_elapsed_seconds": round(total_elapsed, 1),
    }


def _parse_pages(s: str) -> tuple[int, int]:
    """Parse '1-50' → (1, 50)"""
    if "-" in s:
        a, b = s.split("-", 1)
        return int(a), int(b)
    return 1, int(s)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pdf", required=True, help="Path to source PDF (under thư viện sách/)")
    p.add_argument("--book-id", required=True, help="Short slug (e.g. tuvidauso-zh)")
    p.add_argument("--title", required=True, help="Vietnamese book title")
    p.add_argument("--hanzi-title", default="", help="Original Chinese title for cover")
    p.add_argument("--author", default="", help="Author (with Hán-Việt name)")
    p.add_argument("--school", default="common",
                   choices=["mai_hoa", "tu_vi", "luc_hao", "bat_tu", "phong_thuy", "ha_lac", "common"])
    p.add_argument("--tier", default="B", choices=["S", "A", "B", "C"])
    p.add_argument("--pages-total", type=int, required=True, help="Total pages in source PDF")
    p.add_argument("--pages", default="1-10", help="Page range for this session (e.g. '1-50')")
    p.add_argument("--notes", default="", help="Optional library notes")
    p.add_argument("--edition", default="v0.1-draft")
    p.add_argument("--include-scan", action="store_true", help="Include scan thumbnails in PDF")
    p.add_argument("--no-paid", action="store_true", help="Disable DeepSeek paid fallback")
    p.add_argument("--overwrite", action="store_true", help="Re-translate existing pages")
    p.add_argument("--skip-ocr", action="store_true", help="Skip MinerU step (use existing)")
    args = p.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.is_absolute():
        pdf_path = PROJECT_ROOT / pdf_path
    if not pdf_path.exists():
        sys.exit(f"PDF not found: {pdf_path}")

    result = run(
        pdf_path, args.book_id,
        title=args.title, hanzi_title=args.hanzi_title, author=args.author,
        school=args.school, tier=args.tier, pages_total=args.pages_total,
        notes=args.notes,
        page_range=_parse_pages(args.pages),
        edition=args.edition,
        include_scan=args.include_scan,
        allow_paid_fallback=not args.no_paid,
        overwrite=args.overwrite,
        skip_ocr=args.skip_ocr,
    )
    print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
