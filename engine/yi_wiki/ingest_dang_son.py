"""Wiki-ingest corpus ĐẰNG SƠN — 40 vòng đọc sâu 《Tử Vi Hoàn Toàn Khoa Học》 (T1+T2) → wiki.sqlite3.

Phase 3 (sau Phase 2 đọc xong, Iron Rule #2). Parse các section 'PHASE B — WIKI' trong 40 journal
docs/design/tu-vi-dang-son-* → concept tokens (kebab-case) → upsert vào WikiStore với:
  • author Đằng Sơn (phái khoa-học-hóa, kế thừa Tạ Phồn Trị)
  • 2 works (Tập 1, Tập 2)
  • corpus 'tuvi-dang-son', school 'tu_vi_dang_son'

Chạy:  python -m engine.yi_wiki.ingest_dang_son          # ingest vào DB mặc định
       python -m engine.yi_wiki.ingest_dang_son --dry    # chỉ trích + xuất manifest, không ghi DB
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from .models import Author, ConceptIndex, Work
from .store import get_store

_ROOT = Path(__file__).resolve().parents[2]
_JOURNAL_DIR = _ROOT / "docs" / "design"
_MANIFEST = _JOURNAL_DIR / "dang-son-wiki-concepts.json"
_CORPUS = "tuvi-dang-son"
_SCHOOL = "tu_vi_dang_son"

# **token (gloss)** trong section PHASE B; tách canonical (trước "(") + gloss (trong ngoặc).
_BOLD = re.compile(r"\*\*([^*]+?)\*\*")
_PAGE = re.compile(r"-p(\d+)")


def _glob_journals() -> list[Path]:
    """20 vòng Tập 1 (FULL) + 20 vòng Tập 2 (T2), bỏ file tổng quan."""
    files = sorted(_JOURNAL_DIR.glob("tu-vi-dang-son-FULL-vong-*.md")) + \
        sorted(_JOURNAL_DIR.glob("tu-vi-dang-son-T2-vong-*.md"))
    return files


def _phase_b_block(text: str) -> str:
    """Trích nội dung từ '## ...PHASE B' tới heading '##' kế tiếp."""
    m = re.search(r"PHASE B[^\n]*\n(.*?)(?:\n##\s|\Z)", text, re.S)
    return m.group(1) if m else ""


def _split_token(tok: str) -> tuple[str, str]:
    """'lộc-phùng-xung-phá (cát-xứ-tàng-hung)' → ('lộc-phùng-xung-phá', 'cát-xứ-tàng-hung')."""
    tok = tok.strip()
    m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", tok)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return tok, ""


def extract_concepts(journals: list[Path] | None = None) -> list[dict]:
    """Trích concept tokens từ section PHASE B của các journal → list dedupe theo canonical_vi.

    Mỗi concept: {canonical_vi, short_note, first_seen_page, sources:[vòng-file], count}.
    """
    journals = journals or _glob_journals()
    by_canon: dict[str, dict] = {}
    for jp in journals:
        text = jp.read_text(encoding="utf-8")
        block = _phase_b_block(text)
        if not block:
            continue
        pm = _PAGE.search(jp.name)
        page = int(pm.group(1)) if pm else 0
        for raw in _BOLD.findall(block):
            canon, gloss = _split_token(raw)
            if not canon or len(canon) < 2:
                continue
            key = canon.lower()
            if key not in by_canon:
                by_canon[key] = {
                    "canonical_vi": canon, "short_note": gloss,
                    "first_seen_page": page, "sources": [jp.stem], "count": 1,
                }
            else:
                c = by_canon[key]
                c["count"] += 1
                if jp.stem not in c["sources"]:
                    c["sources"].append(jp.stem)
                if not c["short_note"] and gloss:
                    c["short_note"] = gloss
    return sorted(by_canon.values(), key=lambda c: (-c["count"], c["canonical_vi"]))


def seed_dang_son(store) -> tuple[int, list[int]]:
    """Upsert author Đằng Sơn + 2 works (Tập 1, Tập 2). Trả (author_id, [work_ids])."""
    author = Author(
        author_id=0,
        name_vi="Đằng Sơn",
        name_zh="",
        tier_in_lineage=2,           # kế thừa Tạ Phồn Trị (khoa-học-hóa)
        era="hiện đại (Đài Loan, Cao Hùng)",
        birth_year=None, death_year=None,
        worldview_school=_SCHOOL,
        foundational_axioms=[
            "Tử Vi suy diễn được từ âm dương (first principles)",
            "Ngũ hành = phép tính GẦN ĐÚNG của âm dương",
            "Thần sát = tài Thiên-Địa (năm), không thể bỏ (≠ phái giản lược)",
            "Đọc đồng dạng / cơ-biến — không định mệnh cứng",
        ],
        hermeneutic_style="khoa-học-hóa: dựng tử vi như chuỗi định lý dẫn xuất, kiểm chứng bằng lý",
        works=[],
        bio_summary=(
            "Tác giả 《Tử Vi Hoàn Toàn Khoa Học》 (Cao Hùng, Đài Loan), kế thừa Tạ Phồn Trị. "
            "Khoa-học-hóa Tử Vi: suy mọi sao/cách từ âm dương + giải thích cơ chế."
        ),
        teachers=[], disciples=[], created_at=0,
    )
    aid = store.upsert_author(author)
    work_ids = []
    for tap, title in ((1, "Tử Vi Hoàn Toàn Khoa Học — Tập 1"),
                       (2, "Tử Vi Hoàn Toàn Khoa Học — Tập 2 (Thần sát · Tuần Triệt)")):
        w = Work(
            work_id=0, author_id=aid, title_vi=title, title_zh="",
            year_composed=None, role="primary", corpus_id=_CORPUS,
            is_canonical=True, notes=f"Tập {tap} · đọc sâu 20 vòng (2026-06-23)", created_at=0,
        )
        work_ids.append(store.upsert_work(w))
    return aid, work_ids


def ingest(store=None, *, dry: bool = False) -> dict:
    """Trích + (nếu không dry) seed author/works + upsert concepts. Trả báo cáo."""
    store = store or get_store()
    concepts = extract_concepts()
    # luôn xuất manifest (reviewable, re-runnable)
    _MANIFEST.write_text(
        json.dumps({"corpus": _CORPUS, "school": _SCHOOL, "n": len(concepts),
                    "concepts": concepts}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    if dry:
        return {"dry": True, "n_concepts": len(concepts), "manifest": str(_MANIFEST)}

    aid, work_ids = seed_dang_son(store)
    cids = []
    for c in concepts:
        cid = store.upsert_concept(ConceptIndex(
            concept_id=0, canonical_vi=c["canonical_vi"], canonical_zh="",
            aliases=[], mentioned_in_passages=[],
            short_note=c["short_note"] or None,
            first_seen_corpus=_CORPUS, first_seen_page=c["first_seen_page"], created_at=0,
        ))
        cids.append(cid)
    # gắn school/corpora cho các concept vừa nhập (cột store.upsert không ghi)
    db = getattr(store, "db_path", None)
    if db:
        conn = sqlite3.connect(str(db))
        conn.execute(
            "UPDATE concept_index SET school=?, corpora=? WHERE first_seen_corpus=?",
            (_SCHOOL, json.dumps([_CORPUS], ensure_ascii=False), _CORPUS),
        )
        conn.commit()
        conn.close()
    return {"author_id": aid, "work_ids": work_ids,
            "n_concepts": len(cids), "manifest": str(_MANIFEST)}


if __name__ == "__main__":
    import sys
    rep = ingest(dry="--dry" in sys.argv)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
