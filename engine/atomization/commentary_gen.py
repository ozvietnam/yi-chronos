"""Commentary Generator — LLM-gen chú giải chi tiết per atomic_question.

4 lớp chú giải mỗi atom:
1. han_viet_explain   — giải nghĩa từ Hán-Việt cốt
2. viet_thuan          — diễn giải Việt thuần cho user thường
3. nguyen_ly           — nguyên lý vận hành (KHI nào áp, TẠI sao)
4. vi_du_doi_song      — ví dụ tình huống đời sống

+ cross_school_notes (nếu có data)
+ iron_rule_warning (cảnh báo Iron Rule #6 nếu atom dễ predict)

Usage:
    python3 -m engine.atomization.commentary_gen --limit 5  # test 5 atoms
    python3 -m engine.atomization.commentary_gen --all      # all pending
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.ai.providers.minimax import MiniMaxProvider  # noqa: E402
from engine.ai.providers.base import ProviderError  # noqa: E402

DB = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"


COMMENTARY_PROMPT = """# Nhiệm vụ — Chú giải Atomic Question
Em là Tử Vi sage, hỗ trợ user thường (không phải chuyên gia). Cho atomic question
dưới đây + source quote + chunk text gốc, hãy viết 4 lớp CHÚ GIẢI thân thiện.

# Atomic Question
{question}

# Subject identifiers
{subject_identifiers}

# Source quote (trích nguyên văn từ sách)
{source_quote}

# Chunk full text (đoạn sách gốc)
{chunk_text}

# From category (LLM-proposed)
{from_category}

# Format style chunk
{format_style}

# QUY TẮC viết chú giải
1. ⛔ KHÔNG suy đoán ngoài source. Bám 100% nội dung sách.
2. ⛔ KHÔNG predict cứng (Iron Rule #6 — đọc đồng dạng).
3. ✅ Mỗi lớp 100-400 chars. Việt thuần dễ hiểu.
4. ✅ Nêu rõ entity (sao, cung, chi) — không đại từ.
5. ✅ Nếu source không đủ data cho 1 lớp → field đó để null.

# Output JSON (KHÔNG markdown fence)
{
  "han_viet_explain": "<giải nghĩa các từ Hán-Việt cốt trong câu hỏi/quote. Vd: 'Triều củng' = 'chầu hầu vây quanh, như bách quan triều bái vua'.>",
  "viet_thuan": "<diễn giải Việt thuần cho user thường, 2-4 câu. Trả lời atomic_question dùng nội dung chunk. KHÔNG dùng Hán-Việt khó.>",
  "nguyen_ly": "<giải thích NGUYÊN LÝ vận hành — KHI nào điều này áp dụng, TẠI sao cấu hình này tạo ra hệ quả đó. Bám source.>",
  "vi_du_doi_song": "<ví dụ tình huống ĐỜI SỐNG cụ thể — vd: 'Người mệnh Vũ-Phá Tỵ thường thấy mình ở vị thế lãnh đạo nhưng cô đơn, ra quyết định khó nhằn'. KHÔNG predict thành công/thất bại cứng.>",
  "cross_school_notes": null,
  "iron_rule_warning": "<null hoặc text cảnh báo NẾU atom dễ bị hiểu thành predict cứng. Vd: 'Đoạn này không nói lá số chắc chắn thành công — chỉ phản chiếu xu hướng khai sáng có sức.'>"
}

# Output:
"""


def _parse_json(content: str) -> tuple[dict | None, str | None]:
    raw = content.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines)
    try:
        return json.loads(raw), None
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(raw[start:end + 1]), None
            except json.JSONDecodeError as e:
                return None, str(e)
        return None, "no JSON object found"


def fetch_pending_atoms(limit: int | None = None) -> list[dict]:
    """Atoms chưa có commentary."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    sql = """
        SELECT aq.atom_id, aq.question_text, aq.subject_identifiers,
               aq.source_quote, aq.from_category,
               cc.format_style,
               c.text as chunk_text, c.book_corpus_id, c.page_start
        FROM atomic_questions aq
        JOIN chunks_v2 c ON c.chunk_id = aq.chunk_id
        LEFT JOIN chunk_classifications cc ON cc.cc_id = aq.cc_id
        LEFT JOIN atom_commentaries ac ON ac.atom_id = aq.atom_id
        WHERE ac.commentary_id IS NULL
        ORDER BY aq.atom_id
    """
    if limit:
        sql += f" LIMIT {limit}"
    rows = [dict(r) for r in conn.execute(sql).fetchall()]
    conn.close()
    return rows


def gen_commentary(provider: MiniMaxProvider, atom: dict, model: str = "MiniMax-M2",
                    max_retries: int = 3) -> tuple[dict | None, int]:
    prompt = (
        COMMENTARY_PROMPT
        .replace("{question}", atom["question_text"])
        .replace("{subject_identifiers}", atom["subject_identifiers"] or "{}")
        .replace("{source_quote}", atom["source_quote"] or "(no quote)")
        .replace("{chunk_text}", (atom["chunk_text"] or "")[:2500])
        .replace("{from_category}", atom["from_category"] or "(no cat)")
        .replace("{format_style}", atom["format_style"] or "(unknown)")
    )
    total_tok = 0
    for attempt in range(max_retries):
        try:
            r = provider.chat(messages=[{"role": "user", "content": prompt}], model=model,
                              temperature=0.5, max_tokens=2500)
        except ProviderError:
            time.sleep(2)
            continue
        total_tok += r.prompt_tokens + r.completion_tokens
        # Retry on empty content (MiniMax flaky)
        if not r.content.strip():
            time.sleep(1 + attempt)
            continue
        parsed, err = _parse_json(r.content)
        if parsed is not None:
            return parsed, total_tok
        time.sleep(1)
    return None, total_tok


def persist_commentary(atom_id: int, c: dict, extracted_by: str) -> None:
    conn = sqlite3.connect(DB)
    cross_school = c.get("cross_school_notes")
    if cross_school is not None and not isinstance(cross_school, str):
        cross_school = json.dumps(cross_school, ensure_ascii=False)
    conn.execute("""
        INSERT INTO atom_commentaries
            (atom_id, han_viet_explain, viet_thuan, nguyen_ly, vi_du_doi_song,
             cross_school_notes, iron_rule_warning, extracted_by, confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0.85)
    """, (
        atom_id, c.get("han_viet_explain"), c.get("viet_thuan"),
        c.get("nguyen_ly"), c.get("vi_du_doi_song"),
        cross_school, c.get("iron_rule_warning"),
        extracted_by,
    ))
    conn.commit()
    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    limit = None if args.all else args.limit
    pending = fetch_pending_atoms(limit)
    if not pending:
        print("✅ Nothing pending")
        return
    print(f"📋 {len(pending)} atoms pending commentary")

    keys = json.loads((PROJECT_ROOT / "data" / "ai_keys.json").read_text())
    provider = MiniMaxProvider(api_key=keys["minimax"])
    extracted_by = f"{provider.name}/MiniMax-M2"

    total_tok = 0
    success = 0
    t_start = time.time()
    for idx, atom in enumerate(pending, 1):
        print(f"  [{idx}/{len(pending)}] atom_id={atom['atom_id']} ({atom['question_text'][:60]}...)")
        t1 = time.time()
        c, tok = gen_commentary(provider, atom)
        total_tok += tok
        d = time.time() - t1
        if c:
            persist_commentary(atom["atom_id"], c, extracted_by)
            print(f"     ✅ {d:.1f}s · {tok} tok")
            success += 1
        else:
            print(f"     ❌ {d:.1f}s · fail")

    elapsed = time.time() - t_start
    print(f"\n✅ Success: {success}/{len(pending)} · {total_tok} tokens · {elapsed:.0f}s")


if __name__ == "__main__":
    main()
