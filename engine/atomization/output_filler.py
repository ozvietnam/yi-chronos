"""Output Filler — Fill 3-layer output cho 1 field bằng atoms KB.

Cho mỗi field trong OutputTemplate:
  1. Retrieve atoms từ atomic_questions matching field.atomic_q_keywords
  2. Layer 1 "Chuyện về anh": synth narrative từ commentary.viet_thuan + vi_du_doi_song
  3. Layer 2 "Vì sao lại thế": synth từ commentary.nguyen_ly
  4. Layer 3 "Sách cổ đã nói": list source_quotes với book + page + author

Backend ĐỘC LẬP — callable from Python or via API.
KHÔNG cần LLM khi data đã có. Chỉ cần LLM khi muốn personalize cho la_so cụ thể.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.atomization.output_template import (  # noqa: E402
    OutputField, ThreeLayerOutput, build_full_template,
)
from engine.atomization.retriever import ChunkAtomRetriever  # noqa: E402

DB = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"


# Map (cung, sao) → preferred section_id từ Trung Châu Q2 Chương 5
# Chapter 5.X — Cung Viên Luận; X.Y — sao thứ tự trong cung X
CUNG_SAO_TO_SECTION = {
    ("Mệnh", "Tử Vi"): "5.1.1",
    ("Mệnh", "Thiên Cơ"): "5.1.2",
    ("Mệnh", "Thái Dương"): "5.1.3",
    ("Mệnh", "Vũ Khúc"): "5.1.4",
    ("Mệnh", "Thiên Đồng"): "5.1.5",
    ("Mệnh", "Liêm Trinh"): "5.1.6",
    ("Mệnh", "Thiên Phủ"): "5.1.7",
    ("Mệnh", "Thái Âm"): "5.1.8",
    ("Mệnh", "Tham Lang"): "5.1.9",
    ("Mệnh", "Cự Môn"): "5.1.10",
    ("Mệnh", "Thiên Tướng"): "5.1.11",
    ("Mệnh", "Thiên Lương"): "5.1.12",
    ("Mệnh", "Thất Sát"): "5.1.13",
    ("Mệnh", "Phá Quân"): "5.1.14",
    # ... 12 cung × 14 sao = 168 mappings (sẽ extend khi atomize section)
}


class OutputFiller:
    """Fill 3-layer output cho 1 field từ atoms KB."""

    def __init__(self, top_k_atoms: int = 5):
        self.retriever = ChunkAtomRetriever()
        self.top_k = top_k_atoms

    def fill_field(self, field: OutputField, la_so_context: dict | None = None) -> ThreeLayerOutput:
        """Retrieve atoms + assemble 3-layer output.

        Priority: atoms tagged với section_id matching (cung, sao) > phase_pre_stepwise scattered.

        Args:
            field: OutputField definition
            la_so_context: Optional lá số context để filter atoms relevant
                (vd. atoms về "Tử Vi Mệnh" — chỉ relevant nếu user có Tử Vi Mệnh)
        """
        # Step 0: Determine preferred section for this (cung, sao)
        preferred_section = CUNG_SAO_TO_SECTION.get((field.cung, field.sao_chinh))

        # Step 1a: DIRECT retrieve atoms WHERE section_id == preferred_section (highest priority)
        all_hits = []
        if preferred_section:
            import sqlite3
            conn = sqlite3.connect(DB)
            conn.row_factory = sqlite3.Row
            sec_rows = conn.execute("""
                SELECT
                    aq.atom_id, aq.question_text, aq.chunk_id,
                    aq.subject_identifiers, aq.from_category, aq.source_quote,
                    aq.confidence, aq.founder_verified,
                    c.text AS chunk_text, c.book_corpus_id, c.page_start, c.page_end,
                    cc.is_chu_the, cc.is_cong_thuc, cc.is_luan_giai,
                    cc.is_to_hop, cc.is_kinh_nghiem, cc.format_style
                FROM atomic_questions aq
                JOIN chunks_v2 c ON c.chunk_id = aq.chunk_id
                LEFT JOIN chunk_classifications cc ON cc.cc_id = aq.cc_id
                WHERE aq.section_id = ?
                ORDER BY aq.atom_id
                LIMIT ?
            """, (preferred_section, self.top_k * 2)).fetchall()
            conn.close()
            from engine.atomization.retriever import AtomRetrievalInfo
            for r in sec_rows:
                try:
                    ids = json.loads(r["subject_identifiers"] or "{}")
                except (json.JSONDecodeError, TypeError):
                    ids = {}
                all_hits.append(AtomRetrievalInfo(
                    atom_id=r["atom_id"],
                    atom_query="(section-direct)",
                    atom_question=r["question_text"],
                    chunk_id=r["chunk_id"],
                    chunk_text=r["chunk_text"] or "",
                    source_book=r["book_corpus_id"],
                    page_start=r["page_start"],
                    page_end=r["page_end"],
                    retrieval_score=1.0,  # max — direct hit
                    subject_identifiers=ids,
                    from_category=r["from_category"],
                    source_quote=r["source_quote"],
                    confidence=r["confidence"] or 0.85,
                    founder_verified=r["founder_verified"] or 0,
                    archetype={
                        "is_chu_the": r["is_chu_the"] or 0,
                        "is_cong_thuc": r["is_cong_thuc"] or 0,
                        "is_luan_giai": r["is_luan_giai"] or 0,
                        "is_to_hop": r["is_to_hop"] or 0,
                        "is_kinh_nghiem": r["is_kinh_nghiem"] or 0,
                    },
                    format_style=r["format_style"],
                ))

        # Step 1b: Augment via FTS keyword search (lower priority)
        for kw in field.atomic_q_keywords[:5]:
            hits = self.retriever.search_atom_fts(kw, limit=self.top_k * 3)
            all_hits.extend(hits)

        # Step 3: Fetch section_id for each atom to enable priority
        atom_ids = list(set(h.atom_id for h in all_hits))
        section_map = {}
        if atom_ids:
            import sqlite3
            conn = sqlite3.connect(DB)
            placeholders = ",".join("?" * len(atom_ids))
            rows = conn.execute(
                f"SELECT atom_id, section_id FROM atomic_questions WHERE atom_id IN ({placeholders})",
                atom_ids,
            ).fetchall()
            for aid, sid in rows:
                section_map[aid] = sid or ""
            conn.close()

        # Step 4: Dedup + sort with section priority
        seen = set()
        unique = []
        for h in all_hits:
            if h.atom_id in seen:
                continue
            seen.add(h.atom_id)
            unique.append(h)

        def priority_key(atom):
            sid = section_map.get(atom.atom_id, "")
            # Lower number = higher priority
            if preferred_section and sid == preferred_section:
                return (0, -atom.retrieval_score)  # exact section match — top
            if preferred_section and sid.startswith(preferred_section.rsplit(".", 1)[0]):
                return (1, -atom.retrieval_score)  # same chapter (5.1.x)
            if sid == "phase_pre_stepwise":
                return (3, -atom.retrieval_score)  # scattered atoms — fallback
            if sid:
                return (2, -atom.retrieval_score)  # other sections — mid
            return (4, -atom.retrieval_score)  # no section — last

        unique.sort(key=priority_key)
        top_atoms = unique[: self.top_k]

        # Step 2: Fetch commentaries for these atoms
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        atom_ids_str = ",".join(str(a.atom_id) for a in top_atoms) or "-1"
        commentaries = {}
        try:
            rows = conn.execute(f"""
                SELECT atom_id, han_viet_explain, viet_thuan, nguyen_ly,
                       vi_du_doi_song, iron_rule_warning
                FROM atom_commentaries
                WHERE atom_id IN ({atom_ids_str})
            """).fetchall()
            for r in rows:
                commentaries[r["atom_id"]] = dict(r)
        finally:
            conn.close()

        # Step 3: Assemble 3 layers
        result = ThreeLayerOutput(field_id=field.field_id)

        # ── LAYER 1 — Chuyện về anh (narrative) ───────────────────
        narrative_parts = []
        examples = []
        for atom in top_atoms:
            comm = commentaries.get(atom.atom_id, {})
            if comm.get("viet_thuan"):
                narrative_parts.append(comm["viet_thuan"])
            if comm.get("vi_du_doi_song"):
                examples.append(comm["vi_du_doi_song"])
        # Synth: first 2-3 viet_thuan paragraphs → narrative
        result.layer_1_narrative = "\n\n".join(narrative_parts[:3])
        result.layer_1_examples = examples[:3]

        # ── LAYER 2 — Vì sao lại thế (nguyên lý) ──────────────────
        nguyen_ly_parts = []
        for atom in top_atoms:
            comm = commentaries.get(atom.atom_id, {})
            if comm.get("nguyen_ly"):
                nguyen_ly_parts.append(comm["nguyen_ly"])
        result.layer_2_nguyen_ly = "\n\n".join(nguyen_ly_parts[:3])
        # Co_che: combine subject_identifiers ngũ hành / âm dương nếu có
        co_che_hints = []
        for atom in top_atoms[:3]:
            ids = atom.subject_identifiers
            for key in ("ngu_hanh", "am_duong", "hoa_khi", "hành"):
                if key in ids:
                    co_che_hints.append(f"{key}: {ids[key]}")
        result.layer_2_co_che = " · ".join(co_che_hints)

        # ── LAYER 3 — Sách cổ đã nói (citations) ──────────────────
        for atom in top_atoms:
            citation = {
                "atom_id": atom.atom_id,
                "book": atom.source_book,
                "page_start": atom.page_start,
                "page_end": atom.page_end,
                "atom_question": atom.atom_question,
                "source_quote": atom.source_quote or "",
                "category": atom.from_category,
                "confidence": atom.confidence,
                "founder_verified": atom.founder_verified,
            }
            # Add han_viet from commentary if exists
            comm = commentaries.get(atom.atom_id, {})
            if comm.get("han_viet_explain"):
                citation["han_viet_explain"] = comm["han_viet_explain"]
            result.layer_3_citations.append(citation)

        # ── META ──────────────────────────────────────────────────
        result.sources_atoms = [a.atom_id for a in top_atoms]
        result.sources_books = list(set(a.source_book for a in top_atoms))
        if top_atoms:
            result.confidence = sum(a.confidence for a in top_atoms) / len(top_atoms)
        # Iron Rule warning: pick first non-null from commentaries
        for atom in top_atoms:
            comm = commentaries.get(atom.atom_id, {})
            if comm.get("iron_rule_warning"):
                result.iron_rule_warning = comm["iron_rule_warning"]
                break

        return result

    def fill_cung(self, cung: str, la_so: dict) -> dict[str, ThreeLayerOutput]:
        """Fill all fields cho 1 cung của 1 lá số.

        Args:
            cung: vd. "Mệnh"
            la_so: dict với keys như {Mệnh: {chinh_tinh: "Tử Vi", chi: "Tý", ...}, ...}
        """
        # Get sao chính của cung này từ la_so
        cung_data = la_so.get(cung, {})
        sao_chinh_in_la_so = cung_data.get("chinh_tinh", []) if isinstance(cung_data.get("chinh_tinh"), list) else [cung_data.get("chinh_tinh")]
        # Filter None / empty
        sao_chinh_in_la_so = [s for s in sao_chinh_in_la_so if s]

        all_fields = build_full_template()
        # Filter: chỉ fields cho cung này + sao_chinh có trong lá số (hoặc vô chính diệu nếu rỗng)
        if sao_chinh_in_la_so:
            relevant = [f for f in all_fields if f.cung == cung and f.sao_chinh in sao_chinh_in_la_so]
        else:
            relevant = [f for f in all_fields if f.cung == cung and f.sao_chinh is None]

        out = {}
        for field in relevant:
            out[field.field_id] = self.fill_field(field, la_so_context=la_so)
        return out


# ═══════════════════════════════════════════════════════════════════
# CLI test
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    filler = OutputFiller(top_k_atoms=3)

    # Demo: fill 1 field — Mệnh Tử Vi tong_quan
    from engine.atomization.output_template import OutputField, build_atomic_keywords
    test_field = OutputField(
        field_id="Mệnh.Tử Vi.tong_quan",
        cung="Mệnh",
        sao_chinh="Tử Vi",
        variant="Tử Vi tại Mệnh",
        aspect="tong_quan",
        description_vi="Tổng quan Tử Vi tại Mệnh",
        atomic_q_keywords=build_atomic_keywords("Tử Vi", "Mệnh", "tong_quan"),
        section_priority={},
    )
    result = filler.fill_field(test_field)

    print(f"📐 Field: {result.field_id}")
    print(f"   {len(result.sources_atoms)} atoms used")
    print(f"   Books: {result.sources_books}")
    print(f"   Confidence avg: {result.confidence:.2f}")
    print()
    print("━" * 70)
    print("🌟 LAYER 1 — CHUYỆN VỀ ANH (Việt thuần):")
    print("━" * 70)
    print(result.layer_1_narrative[:600] or "(empty)")
    if result.layer_1_examples:
        print(f"\n📌 Ví dụ: {result.layer_1_examples[0][:200]}")
    print()
    print("━" * 70)
    print("🔬 LAYER 2 — VÌ SAO LẠI THẾ (Nguyên lý):")
    print("━" * 70)
    print(result.layer_2_nguyen_ly[:500] or "(empty)")
    print(f"\n⚙ Cơ chế: {result.layer_2_co_che}")
    print()
    print("━" * 70)
    print(f"📚 LAYER 3 — SÁCH CỔ ĐÃ NÓI ({len(result.layer_3_citations)} citations):")
    print("━" * 70)
    for i, c in enumerate(result.layer_3_citations[:3], 1):
        print(f"\n[{i}] {c['book']} p{c['page_start']}")
        print(f"    Q: {c['atom_question'][:80]}")
        if c.get('source_quote'):
            print(f"    Quote: {c['source_quote'][:200]}")
    if result.iron_rule_warning:
        print(f"\n⚠ Iron Rule #6: {result.iron_rule_warning[:200]}")
