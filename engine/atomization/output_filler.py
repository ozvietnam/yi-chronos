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


class OutputFiller:
    """Fill 3-layer output cho 1 field từ atoms KB."""

    def __init__(self, top_k_atoms: int = 5):
        self.retriever = ChunkAtomRetriever()
        self.top_k = top_k_atoms

    def fill_field(self, field: OutputField, la_so_context: dict | None = None) -> ThreeLayerOutput:
        """Retrieve atoms + assemble 3-layer output.

        Args:
            field: OutputField definition
            la_so_context: Optional lá số context để filter atoms relevant
                (vd. atoms về "Tử Vi Mệnh" — chỉ relevant nếu user có Tử Vi Mệnh)
        """
        # Step 1: Multi-keyword retrieval
        all_hits = []
        for kw in field.atomic_q_keywords[:5]:  # top-5 keywords
            hits = self.retriever.search_atom_fts(kw, limit=self.top_k)
            all_hits.extend(hits)

        # Dedup by atom_id + rank by retrieval_score
        seen = set()
        unique = []
        for h in sorted(all_hits, key=lambda x: -x.retrieval_score):
            if h.atom_id in seen:
                continue
            seen.add(h.atom_id)
            unique.append(h)
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
