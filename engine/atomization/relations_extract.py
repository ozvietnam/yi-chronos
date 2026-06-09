"""Relations Extractor — Find cross-atom links (atom A → atom B).

6 relation types:
- luan_giai_them      : B là luận giải sâu thêm cho A
- cong_thuc_apdung    : B là công thức áp dụng cho A
- kinh_nghiem_apdung  : B là kinh nghiệm khi gặp A
- trai_nghia          : B nói ngược A (cảnh báo)
- cach_cuc_lien_quan  : B nói về cách cục liên quan A
- cross_school        : B từ school khác về cùng chủ đề A

Strategy: candidate-then-classify
1. Find candidates: same chunk, same star, same palace, same combo
2. LLM classify each candidate pair → relation_type + confidence

Usage:
    python3 -m engine.atomization.relations_extract --limit 10
    python3 -m engine.atomization.relations_extract --all
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.ai.providers.minimax import MiniMaxProvider  # noqa: E402
from engine.ai.providers.base import ProviderError  # noqa: E402

DB = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"


CLASSIFY_PROMPT = """# Nhiệm vụ — Phân loại quan hệ giữa 2 atomic questions
Em là Tử Vi sage. Cho 2 atomic Q dưới (A và B), phân loại quan hệ giữa chúng.

# Atom A
Q: {q_a}
Source quote: {quote_a}
Category: {cat_a}

# Atom B
Q: {q_b}
Source quote: {quote_b}
Category: {cat_b}

# 6 loại quan hệ
- luan_giai_them      : B là luận giải SÂU THÊM cho A
- cong_thuc_apdung    : B là CÔNG THỨC tính/áp dụng cho A
- kinh_nghiem_apdung  : B là KINH NGHIỆM khi gặp tình huống A
- trai_nghia          : B nói NGƯỢC A (cảnh báo paradigm conflict)
- cach_cuc_lien_quan  : B nói về CÁCH CỤC LIÊN QUAN A
- cross_school        : B từ SCHOOL KHÁC nói về cùng chủ đề A
- none                : KHÔNG có quan hệ rõ ràng

# QUY TẮC
- Bám source quote 100%. KHÔNG suy đoán.
- Nếu unclear → chọn "none". Thà thiếu còn hơn sai.

# Output JSON (KHÔNG markdown)
{
  "relation_type": "<one of 6 types or 'none'>",
  "rationale": "<lý do, ngắn gọn 1-2 câu>",
  "confidence": <0.0-1.0>
}

# Output:
"""


def _parse_json(content: str) -> dict | None:
    raw = content.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(raw[start:end + 1])
            except json.JSONDecodeError:
                return None
    return None


def find_candidates(atom_id: int, max_candidates: int = 5) -> list[dict]:
    """Find candidate related atoms by:
    1. Same chunk (high prior)
    2. Same subject identifiers (sao/cung overlap)
    Returns top max_candidates ranked.
    """
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    # Get source atom info
    src = conn.execute("""
        SELECT atom_id, chunk_id, question_text, subject_identifiers, source_quote, from_category
        FROM atomic_questions WHERE atom_id=?
    """, (atom_id,)).fetchone()
    if not src:
        conn.close()
        return []
    src_ids = json.loads(src["subject_identifiers"] or "{}")
    src_values = {str(v) for v in src_ids.values() if v}

    # Candidate pool: same chunk + 50 random other chunks with overlap
    pool = conn.execute("""
        SELECT atom_id, chunk_id, question_text, subject_identifiers, source_quote, from_category
        FROM atomic_questions
        WHERE atom_id != ?
          AND (chunk_id = ? OR atom_id IN (
              SELECT atom_id FROM atomic_questions WHERE atom_id != ? LIMIT 200
          ))
        LIMIT 100
    """, (atom_id, src["chunk_id"], atom_id)).fetchall()

    candidates = []
    for r in pool:
        ids = json.loads(r["subject_identifiers"] or "{}")
        vals = {str(v) for v in ids.values() if v}
        overlap = len(src_values & vals)
        same_chunk = (r["chunk_id"] == src["chunk_id"])
        # Score: same chunk = +5, each overlap = +1
        score = (5 if same_chunk else 0) + overlap
        if score > 0:
            candidates.append({
                "atom_id": r["atom_id"],
                "question": r["question_text"],
                "quote": r["source_quote"] or "",
                "category": r["from_category"] or "",
                "score": score,
            })

    candidates.sort(key=lambda x: -x["score"])
    conn.close()
    return candidates[:max_candidates], dict(src)


def classify_pair(provider: MiniMaxProvider, atom_a: dict, atom_b: dict) -> tuple[dict | None, int]:
    prompt = (
        CLASSIFY_PROMPT
        .replace("{q_a}", atom_a["question_text"])
        .replace("{quote_a}", (atom_a["source_quote"] or "")[:300])
        .replace("{cat_a}", atom_a.get("from_category") or "")
        .replace("{q_b}", atom_b["question"])
        .replace("{quote_b}", atom_b["quote"][:300])
        .replace("{cat_b}", atom_b["category"])
    )
    try:
        r = provider.chat(messages=[{"role": "user", "content": prompt}],
                          model="MiniMax-M2", temperature=0.2, max_tokens=400)
    except ProviderError:
        return None, 0
    parsed = _parse_json(r.content)
    return parsed, r.prompt_tokens + r.completion_tokens


def persist_relation(from_id: int, to_id: int, rel: dict, extracted_by: str) -> None:
    if not rel or rel.get("relation_type") in (None, "none"):
        return
    conn = sqlite3.connect(DB)
    try:
        conn.execute("""
            INSERT OR IGNORE INTO atom_relations
                (from_atom_id, to_atom_id, relation_type, rationale, confidence, extracted_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            from_id, to_id, rel["relation_type"],
            rel.get("rationale", ""), rel.get("confidence", 0.7),
            extracted_by,
        ))
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--start", type=int, default=0, help="atom_id offset")
    args = parser.parse_args()

    conn = sqlite3.connect(DB)
    if args.all:
        atom_ids = [r[0] for r in conn.execute("SELECT atom_id FROM atomic_questions WHERE atom_id >= ? ORDER BY atom_id", (args.start,)).fetchall()]
    else:
        atom_ids = [r[0] for r in conn.execute("SELECT atom_id FROM atomic_questions WHERE atom_id >= ? ORDER BY atom_id LIMIT ?", (args.start, args.limit)).fetchall()]
    conn.close()

    print(f"📋 Extracting relations for {len(atom_ids)} atoms")
    keys = json.loads((PROJECT_ROOT / "data" / "ai_keys.json").read_text())
    provider = MiniMaxProvider(api_key=keys["minimax"])
    extracted_by = f"{provider.name}/MiniMax-M2"

    total_tok = 0
    n_rels = 0
    t_start = time.time()
    for idx, aid in enumerate(atom_ids, 1):
        candidates, src = find_candidates(aid, max_candidates=5)
        if not candidates:
            continue
        print(f"  [{idx}/{len(atom_ids)}] atom_id={aid} → {len(candidates)} candidates")
        for cand in candidates:
            rel, tok = classify_pair(provider, src, cand)
            total_tok += tok
            if rel and rel.get("relation_type") not in (None, "none"):
                persist_relation(aid, cand["atom_id"], rel, extracted_by)
                n_rels += 1

    elapsed = time.time() - t_start
    print(f"\n✅ {n_rels} relations extracted · {total_tok} tokens · {elapsed:.0f}s")


if __name__ == "__main__":
    main()
