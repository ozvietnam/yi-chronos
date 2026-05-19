"""Restoration plan — per-book kế hoạch phục chế chi tiết.

Theo nguyên tắc anh chốt:
1. Phase 1 (ngay): Phục dựng nguyên văn — OCR + cleanup nhẹ, KHÔNG wikilink
2. Phase 2 (sau, chờ anh): Đọc kỹ đọc sâu — anh đọc tay, Claude support
3. Phase 3 (cuối cùng): Wiki + Mapping vào Lexicon

Plan = `data/yi_restored/<slug>/plan.md`. Markdown để dễ đọc + edit tay.
Status được lưu trong frontmatter YAML để parse được.

KHÔNG auto-trigger pipeline. Plan chỉ ghi nhận thứ tự + ETA. Anh quyết định
khi nào chạy.
"""

from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from ..store import bootstrap_db, get_corpus
from .manifest import make_book_slug


RESTORED_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "data" / "yi_restored"


# ─── Data classes ────────────────────────────────────────────────────────────


@dataclass
class PlanBatch:
    """One batch of pages within Phase 1."""
    batch_id: str             # 'p1-batch-01'
    page_start: int
    page_end: int
    description: str = ""     # 'Chương Đại Cương', 'Đồ thuyết'
    status: str = "pending"   # 'pending' | 'in_progress' | 'done' | 'failed'
    started_at: int | None = None
    finished_at: int | None = None
    pages_done: int = 0
    notes: str = ""


@dataclass
class RestorationPlan:
    """Top-level plan for one book."""
    corpus_id: int
    book_name: str
    book_slug: str
    tier: str = "B"
    author: str | None = None
    schools: list[str] = field(default_factory=list)
    pages_total: int = 0
    file_path: str | None = None
    copyright_status: str = "internal_only"
    created_at: int = 0
    updated_at: int = 0
    current_phase: int = 1                       # 1, 2, 3
    # Phase config
    phase1_ocr_backend: str = "qwen-vl"
    phase1_llm_provider: str = "ollama"
    phase1_llm_model: str = "qwen2.5:7b"
    phase1_batches: list[PlanBatch] = field(default_factory=list)
    phase1_eta_hours: float = 0.0
    phase1_status: str = "not_started"           # 'not_started'|'in_progress'|'done'
    phase2_status: str = "not_started"           # đọc kỹ — chờ anh
    phase2_notes: str = ""
    phase3_status: str = "not_started"           # wiki+mapping
    phase3_notes: str = ""
    # Sample analysis (5 trang ngẫu nhiên đầu/giữa/cuối)
    sample_pages: list[int] = field(default_factory=list)
    sample_quality: str = "unknown"              # 'good'|'medium'|'mờ'|'unknown'
    has_chinese: bool = False
    has_figures: bool = False
    has_footnotes: bool = False
    layout_columns: int = 1
    # Free-form
    risks: list[str] = field(default_factory=list)
    notes: str = ""
    log: list[dict] = field(default_factory=list)   # [{ts, event}]

    def to_dict(self) -> dict:
        from dataclasses import asdict
        return asdict(self)


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _plan_dir(slug: str) -> Path:
    p = RESTORED_ROOT / slug
    p.mkdir(parents=True, exist_ok=True)
    return p


def _plan_path(slug: str) -> Path:
    return _plan_dir(slug) / "plan.md"


def _plan_state_path(slug: str) -> Path:
    """Sidecar JSON to make plan machine-parseable (markdown stays human-friendly)."""
    return _plan_dir(slug) / "plan.json"


def _pdf_page_count(pdf_path: Path) -> int:
    try:
        out = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True, text=True, timeout=15,
        )
        for line in out.stdout.splitlines():
            if line.lower().startswith("pages:"):
                return int(line.split(":", 1)[1].strip())
    except Exception:
        pass
    return 0


def _sample_quick_ocr(pdf_path: Path, pages: list[int]) -> dict:
    """Quick Tesseract OCR sample to detect quality + Chinese characters + columns.

    Lightweight — for plan-time analysis only (no LLM cost).
    Returns: {pages: [{page, text_preview, has_chinese, char_count, low_signal}], ...}
    """
    import tempfile
    results = {"pages": [], "overall_quality": "unknown",
               "has_chinese": False, "has_footnotes": False}
    if not pdf_path.exists():
        return results
    with tempfile.TemporaryDirectory(prefix="yi_plan_") as tmp:
        for pn in pages:
            png_prefix = Path(tmp) / f"p-{pn:04d}"
            try:
                subprocess.run(
                    ["pdftoppm", "-r", "150", "-f", str(pn), "-l", str(pn),
                     "-png", "-singlefile", str(pdf_path), str(png_prefix)],
                    check=True, capture_output=True, timeout=30,
                )
                png = Path(tmp) / f"p-{pn:04d}.png"
                if not png.exists():
                    continue
                with png.open("rb") as f:
                    r = subprocess.run(
                        ["tesseract", "-", "-", "-l", "vie"],
                        stdin=f, capture_output=True, timeout=30,
                    )
                txt = r.stdout.decode("utf-8", errors="replace")
                has_zh = bool(re.search(r"[一-鿿]", txt))
                # Footnote markers like [16], (16)
                has_fn = bool(re.search(r"\[\d{1,3}\]|\(\d{1,3}\)", txt))
                char_count = len(txt.strip())
                # Low signal = mostly garbage characters or empty
                clean_ratio = len(re.findall(r"\w", txt)) / max(len(txt), 1)
                low_signal = char_count < 100 or clean_ratio < 0.5
                results["pages"].append({
                    "page": pn,
                    "char_count": char_count,
                    "has_chinese": has_zh,
                    "has_footnotes": has_fn,
                    "low_signal": low_signal,
                    "preview": txt[:200].replace("\n", " "),
                })
                if has_zh:
                    results["has_chinese"] = True
                if has_fn:
                    results["has_footnotes"] = True
            except Exception:
                continue
    # Overall quality verdict
    if results["pages"]:
        good = sum(1 for p in results["pages"] if not p["low_signal"])
        ratio = good / len(results["pages"])
        results["overall_quality"] = (
            "good" if ratio >= 0.8 else
            "medium" if ratio >= 0.5 else
            "mờ"
        )
    return results


def _propose_phase1_batches(pages_total: int, default_chunk: int = 50) -> list[PlanBatch]:
    """Split pages into batches of ~50 pages. Returns list of PlanBatch."""
    batches: list[PlanBatch] = []
    if pages_total <= 0:
        return batches
    idx = 1
    page = 1
    while page <= pages_total:
        end = min(page + default_chunk - 1, pages_total)
        batches.append(PlanBatch(
            batch_id=f"p1-batch-{idx:02d}",
            page_start=page,
            page_end=end,
            description=f"Trang {page}-{end}",
        ))
        page = end + 1
        idx += 1
    return batches


def _eta_phase1(pages: int, *, sec_per_page: float = 70.0) -> float:
    """Estimate Phase 1 duration in hours (Ollama Qwen2.5-VL + Qwen2.5:7b)."""
    return pages * sec_per_page / 3600.0


# ─── Plan generation + persistence ──────────────────────────────────────────


def create_plan(
    corpus_id: int,
    *,
    sample_pages: list[int] | None = None,
    overwrite: bool = False,
) -> RestorationPlan:
    """Create (or load existing) restoration plan for a book.

    1. Loads corpus row
    2. Counts pages via pdfinfo if not set
    3. Samples 5 random pages (with Tesseract quick OCR)
    4. Generates Phase 1 batches (~50 pages each)
    5. Saves plan.md + plan.json
    """
    bootstrap_db()
    corpus = get_corpus(corpus_id=corpus_id)
    if not corpus:
        raise ValueError(f"corpus {corpus_id} not found")
    if not corpus.file_path:
        raise ValueError(f"corpus {corpus_id} has no file_path")
    pdf_path = Path(corpus.file_path)

    slug = make_book_slug(corpus.name)
    existing = load_plan(corpus_id)
    if existing and not overwrite:
        return existing

    pages_total = corpus.pages_total or _pdf_page_count(pdf_path)
    sample_pages = sample_pages or _default_sample(pages_total)
    quick = _sample_quick_ocr(pdf_path, sample_pages)

    batches = _propose_phase1_batches(pages_total)
    eta = _eta_phase1(pages_total)

    plan = RestorationPlan(
        corpus_id=corpus.corpus_id,
        book_name=corpus.name,
        book_slug=slug,
        tier=corpus.tier or "B",
        author=corpus.author,
        schools=list(corpus.schools_tags or []),
        pages_total=pages_total,
        file_path=corpus.file_path,
        copyright_status=corpus.copyright_status or "internal_only",
        created_at=int(time.time()),
        updated_at=int(time.time()),
        sample_pages=sample_pages,
        sample_quality=quick.get("overall_quality", "unknown"),
        has_chinese=quick.get("has_chinese", False),
        has_footnotes=quick.get("has_footnotes", False),
        phase1_batches=batches,
        phase1_eta_hours=eta,
    )
    # Risks heuristic
    if plan.sample_quality == "mờ":
        plan.risks.append("Scan mờ — có thể cần tăng DPI lên 300 hoặc thử minicpm-v")
    if plan.has_chinese:
        plan.risks.append("Có Hán xen — verify với chuyên gia khi xong Phase 1")
    if plan.pages_total > 500:
        plan.risks.append(f"Sách dài ({pages_total} trang) — chia làm 3-5 đêm")
    plan.log.append({"ts": int(time.time()), "event": "plan-created"})

    save_plan(plan, quick_sample=quick)
    return plan


def _default_sample(total: int) -> list[int]:
    """Pick 5 distributed sample pages."""
    if total <= 5:
        return list(range(1, total + 1))
    quarters = [
        max(1, int(total * 0.05)),
        int(total * 0.25),
        int(total * 0.5),
        int(total * 0.75),
        max(1, int(total * 0.95)),
    ]
    seen = set()
    out = []
    for p in quarters:
        if p not in seen:
            out.append(p); seen.add(p)
    return out


def save_plan(plan: RestorationPlan, *, quick_sample: dict | None = None) -> Path:
    """Persist plan.md + plan.json. Parallel-safe via file lock + merge.

    Khi nhiều process parallel update plan (e.g. mỗi cái chạy 1 batch), em
    re-read disk + merge batch statuses + log entries → write back.
    """
    import fcntl
    import os
    plan.updated_at = int(time.time())
    pdir = _plan_dir(plan.book_slug)
    state_path = _plan_state_path(plan.book_slug)
    lock_path = state_path.with_suffix(".lock")
    pdir.mkdir(parents=True, exist_ok=True)

    with lock_path.open("w") as lock_f:
        fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
        try:
            # Re-read disk + merge our changes
            if state_path.exists():
                try:
                    disk_plan = load_plan(plan.corpus_id)
                    if disk_plan:
                        plan = _merge_plans(disk_plan, plan)
                except Exception:
                    pass
            # Atomic write JSON
            tmp = state_path.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(plan.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(tmp, state_path)
            # Markdown (not race-critical, just write)
            md = _render_plan_markdown(plan, quick_sample=quick_sample)
            md_path = _plan_path(plan.book_slug)
            md_path.write_text(md, encoding="utf-8")
        finally:
            fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
    return _plan_path(plan.book_slug)


def _merge_plans(disk: "RestorationPlan", mine: "RestorationPlan") -> "RestorationPlan":
    """Merge plan changes from multiple parallel processes.

    - phase1_batches: merge by batch_id, prefer mine if status changed
    - log: union (dedupe by ts+event)
    - phase status: prefer "further along" (in_progress > not_started, done > in_progress)
    - notes/risks: keep mine if non-empty, else disk
    """
    batches_by_id: dict[str, PlanBatch] = {b.batch_id: b for b in disk.phase1_batches}
    for b in mine.phase1_batches:
        if b.batch_id in batches_by_id:
            existing = batches_by_id[b.batch_id]
            # Status precedence: done > in_progress > pending > failed (last writer if same)
            status_rank = {"pending": 0, "in_progress": 1, "failed": 2, "done": 3}
            if status_rank.get(b.status, 0) >= status_rank.get(existing.status, 0):
                batches_by_id[b.batch_id] = b
        else:
            batches_by_id[b.batch_id] = b

    # Restore original order
    merged_batches: list[PlanBatch] = []
    for b in (disk.phase1_batches or mine.phase1_batches):
        if b.batch_id in batches_by_id:
            merged_batches.append(batches_by_id[b.batch_id])
            del batches_by_id[b.batch_id]
    # Append any new batches
    merged_batches.extend(batches_by_id.values())

    # Log union
    seen_log = {(e.get("ts"), e.get("event")) for e in disk.log}
    merged_log = list(disk.log)
    for e in mine.log:
        if (e.get("ts"), e.get("event")) not in seen_log:
            merged_log.append(e)

    # Phase status precedence
    phase_rank = {"not_started": 0, "in_progress": 1, "done": 2}
    def pick_phase(a, b):
        return a if phase_rank.get(a, 0) >= phase_rank.get(b, 0) else b

    result = RestorationPlan(
        corpus_id=mine.corpus_id,
        book_name=mine.book_name or disk.book_name,
        book_slug=mine.book_slug or disk.book_slug,
        tier=mine.tier or disk.tier,
        author=mine.author or disk.author,
        schools=mine.schools or disk.schools,
        pages_total=mine.pages_total or disk.pages_total,
        file_path=mine.file_path or disk.file_path,
        copyright_status=mine.copyright_status or disk.copyright_status,
        created_at=min(x for x in [disk.created_at, mine.created_at] if x) if (disk.created_at or mine.created_at) else 0,
        updated_at=max(disk.updated_at, mine.updated_at),
        current_phase=max(disk.current_phase, mine.current_phase),
        phase1_ocr_backend=mine.phase1_ocr_backend or disk.phase1_ocr_backend,
        phase1_llm_provider=mine.phase1_llm_provider or disk.phase1_llm_provider,
        phase1_llm_model=mine.phase1_llm_model or disk.phase1_llm_model,
        phase1_batches=merged_batches,
        phase1_eta_hours=mine.phase1_eta_hours or disk.phase1_eta_hours,
        phase1_status=pick_phase(mine.phase1_status, disk.phase1_status),
        phase2_status=pick_phase(mine.phase2_status, disk.phase2_status),
        phase2_notes=mine.phase2_notes or disk.phase2_notes,
        phase3_status=pick_phase(mine.phase3_status, disk.phase3_status),
        phase3_notes=mine.phase3_notes or disk.phase3_notes,
        sample_pages=mine.sample_pages or disk.sample_pages,
        sample_quality=mine.sample_quality or disk.sample_quality,
        has_chinese=mine.has_chinese or disk.has_chinese,
        has_figures=mine.has_figures or disk.has_figures,
        has_footnotes=mine.has_footnotes or disk.has_footnotes,
        layout_columns=mine.layout_columns or disk.layout_columns,
        risks=mine.risks or disk.risks,
        notes=mine.notes or disk.notes,
        log=merged_log,
    )
    return result


def load_plan(corpus_id: int) -> RestorationPlan | None:
    """Load plan from JSON sidecar."""
    bootstrap_db()
    c = get_corpus(corpus_id=corpus_id)
    if not c:
        return None
    slug = make_book_slug(c.name)
    state_path = _plan_state_path(slug)
    if not state_path.exists():
        return None
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        batches = [PlanBatch(**b) for b in data.pop("phase1_batches", [])]
        return RestorationPlan(phase1_batches=batches, **data)
    except Exception:
        return None


def append_log(plan: RestorationPlan, event: str) -> None:
    """Append timestamped event to plan log."""
    plan.log.append({"ts": int(time.time()), "event": event})


def mark_batch(plan: RestorationPlan, batch_id: str, *,
               status: str, pages_done: int | None = None,
               notes: str = "") -> PlanBatch | None:
    """Update a Phase 1 batch's status. Returns updated batch."""
    for b in plan.phase1_batches:
        if b.batch_id == batch_id:
            old_status = b.status
            b.status = status
            if pages_done is not None:
                b.pages_done = pages_done
            if notes:
                b.notes = notes
            now = int(time.time())
            if status == "in_progress" and old_status != "in_progress":
                b.started_at = now
            if status in ("done", "failed"):
                b.finished_at = now
            return b
    return None


def advance_phase(plan: RestorationPlan, *, to_phase: int) -> bool:
    """Move plan to a new phase. Anh quyết định khi phase 1 đã chạy đủ tốt."""
    if to_phase not in (1, 2, 3):
        return False
    if to_phase == 2:
        # Mark phase 1 done
        plan.phase1_status = "done"
        plan.current_phase = 2
        plan.phase2_status = "in_progress"
        append_log(plan, "phase-1-done → entering phase-2 (đọc sâu)")
    elif to_phase == 3:
        plan.phase2_status = "done"
        plan.current_phase = 3
        plan.phase3_status = "in_progress"
        append_log(plan, "phase-2-done → entering phase-3 (wiki+mapping)")
    elif to_phase == 1:
        plan.current_phase = 1
        plan.phase1_status = "in_progress"
        append_log(plan, "phase-1-started")
    return True


# ─── Markdown rendering ─────────────────────────────────────────────────────


def _render_plan_markdown(plan: RestorationPlan, *, quick_sample: dict | None = None) -> str:
    lines: list[str] = []
    lines.append("---")
    lines.append(f"corpus_id: {plan.corpus_id}")
    lines.append(f"book_name: \"{plan.book_name}\"")
    lines.append(f"tier: \"{plan.tier}\"")
    lines.append(f"current_phase: {plan.current_phase}")
    lines.append(f"phase1_status: \"{plan.phase1_status}\"")
    lines.append(f"phase2_status: \"{plan.phase2_status}\"")
    lines.append(f"phase3_status: \"{plan.phase3_status}\"")
    lines.append(f"updated_at: {plan.updated_at}")
    lines.append("---")
    lines.append("")
    lines.append(f"# Kế hoạch phục chế: {plan.book_name}")
    lines.append("")
    lines.append("> ⚠️ Theo nguyên tắc anh: làm việc nhỏ → phục dựng nguyên văn TRƯỚC → đọc sâu → wiki cuối. KHÔNG vội.")
    lines.append("")
    # Meta
    lines.append("## Thông tin")
    lines.append(f"- **Corpus ID**: {plan.corpus_id}")
    lines.append(f"- **Tác giả**: {plan.author or '—'}")
    lines.append(f"- **Tier**: {plan.tier}")
    lines.append(f"- **Trường phái**: {', '.join(plan.schools) if plan.schools else '—'}")
    lines.append(f"- **Tổng trang**: {plan.pages_total}")
    lines.append(f"- **Bản quyền**: {plan.copyright_status}")
    lines.append(f"- **File**: `{plan.file_path}`")
    lines.append("")
    # Sample
    lines.append("## Sample analysis (5 trang ngẫu nhiên)")
    lines.append(f"- Chất lượng OCR sơ bộ: **{plan.sample_quality}**")
    lines.append(f"- Có Hán xen: {'✓' if plan.has_chinese else '✗'}")
    lines.append(f"- Có footnote: {'✓' if plan.has_footnotes else '✗'}")
    lines.append(f"- Trang sample: {plan.sample_pages}")
    if quick_sample and quick_sample.get("pages"):
        lines.append("")
        lines.append("| Trang | Char count | Chinese? | Footnote? | Preview |")
        lines.append("|---|---|---|---|---|")
        for p in quick_sample["pages"]:
            preview = (p.get("preview") or "")[:80].replace("|", "\\|")
            lines.append(
                f"| {p['page']} | {p['char_count']} | "
                f"{'✓' if p['has_chinese'] else '—'} | "
                f"{'✓' if p['has_footnotes'] else '—'} | {preview} |"
            )
    lines.append("")
    # Risks
    if plan.risks:
        lines.append("## Rủi ro")
        for r in plan.risks:
            lines.append(f"- ⚠️ {r}")
        lines.append("")
    # Phase 1
    lines.append("## Phase 1 — Phục dựng nguyên văn")
    lines.append(f"**Status**: `{plan.phase1_status}` · **ETA**: {plan.phase1_eta_hours:.1f} giờ")
    lines.append("")
    lines.append(f"**Pipeline config**:")
    lines.append(f"- OCR backend: `{plan.phase1_ocr_backend}`")
    lines.append(f"- LLM provider: `{plan.phase1_llm_provider}`")
    lines.append(f"- LLM model: `{plan.phase1_llm_model}`")
    lines.append("- Wikilinks: **disabled** (Phase 3 mới làm)")
    lines.append("")
    lines.append("**Batches**:")
    for b in plan.phase1_batches:
        mark = {"pending": "[ ]", "in_progress": "[~]",
                "done": "[x]", "failed": "[!]"}.get(b.status, "[?]")
        lines.append(
            f"- {mark} `{b.batch_id}`: trang {b.page_start}-{b.page_end} "
            f"({b.pages_done}/{b.page_end - b.page_start + 1}) — {b.description}"
        )
        if b.notes:
            lines.append(f"    > {b.notes}")
    lines.append("")
    # Phase 2
    lines.append("## Phase 2 — Đọc kỹ đọc sâu")
    lines.append(f"**Status**: `{plan.phase2_status}`")
    lines.append("")
    lines.append("- [ ] Anh đọc tay từng chương")
    lines.append("- [ ] Cập nhật `sections[]` trong manifest")
    lines.append("- [ ] Đánh dấu các đoạn cốt lõi để Phase 3 ưu tiên link")
    lines.append("- [ ] Cập nhật `librarian_summary` sau khi đã hiểu sách")
    if plan.phase2_notes:
        lines.append("")
        lines.append(f"> {plan.phase2_notes}")
    lines.append("")
    # Phase 3
    lines.append("## Phase 3 — Wiki + Mapping vào Lexicon")
    lines.append(f"**Status**: `{plan.phase3_status}`")
    lines.append("")
    lines.append("- [ ] Pass LLM thứ 2 — gắn wikilinks (sau khi đã hiểu sách → ít hallucination)")
    lines.append("- [ ] Cập nhật `wikilink_index` trong manifest")
    lines.append("- [ ] Mỗi concept Lexicon → backlink đến trang sách")
    lines.append("- [ ] Random verify 10 wikilinks: đúng context không?")
    if plan.phase3_notes:
        lines.append("")
        lines.append(f"> {plan.phase3_notes}")
    lines.append("")
    # Log
    lines.append("## Log")
    if plan.log:
        for ev in plan.log[-20:]:  # cap to last 20
            ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(ev.get("ts", 0)))
            lines.append(f"- `{ts}` — {ev.get('event', '')}")
    else:
        lines.append("- (chưa có sự kiện)")
    lines.append("")
    # Notes
    if plan.notes:
        lines.append("## Notes")
        lines.append(plan.notes)
    return "\n".join(lines)
