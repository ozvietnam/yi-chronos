"""Corpus ingestion — feed classical texts to LLM → extract concepts/mappings.

Anh, 2026-05-12:
> "hấp thụ tinh hoa từ sách cổ, sách của người nổi tiếng — trước anh em
>  đọc sách để tìm ra quy luật, giờ vẫn sách ấy, tìm ra cách mở rộng từ
>  điển, biến thuật ngữ thành đơn giản dễ hiểu với người dùng."

## Flow

1. Anh add `Corpus` record + place text file at `data/yi_lexicon/corpora/X.txt`
2. `ingest_corpus(corpus_id)` reads file in chunks (~2000 tokens each)
3. For each chunk → LLM prompt: "extract Yi-related concepts + mappings"
4. LLM returns JSON: list of {canonical_vi, concept_type, mappings: [{dim_type, dim_value, reasoning_vi}]}
5. YOLO mode: auto-merge into lexicon (queue as 'auto_accepted', payload mang
   `_merged` ownership: concept_id + mapping_ids do merge này tạo)
6. Anh review queue later: approve → mark verified_by_anh; reject → ROLLBACK
   (gỡ mapping/concept đã merge khỏi lexicon — vòng YOLO khép end-to-end)

## v1 scope

This module ships the structure + LLM prompt template. Anh provides `LLMProvider`
when calling. Uses `engine.ai.providers` registry to pick DeepSeek by default.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

from .store import (
    add_concept,
    add_corpus,
    add_distill_item,
    add_mapping,
    bootstrap_db,
    find_mapping,
    get_concept,
)

_CORPORA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "yi_lexicon" / "corpora"


# ─── LLM prompt template ─────────────────────────────────────────────────────


_EXTRACTION_SYSTEM_PROMPT = """Bạn là chuyên gia Dịch học + ngôn ngữ học Trung-Việt. Nhiệm vụ: đọc đoạn văn cổ thư về Bát Quái / Ngũ Hành / Mai Hoa / Bát Tự / Lục Hào / Tử Vi / Hà Lạc — TRÍCH XUẤT mọi ánh xạ từ KHÁI NIỆM sang chiều cosmology.

## Output format BẮT BUỘC: JSON object

```json
{
  "concepts": [
    {
      "canonical_vi": "tên Việt",
      "canonical_zh": "tên Hán (nếu có trong text)",
      "canonical_en": "English equivalent (nếu rõ)",
      "concept_type": "object | phenomenon | color | number | action | relation | time | place | concept | symbol | other",
      "aliases": ["biến thể"],
      "schools": ["mai_hoa", "lien_hoa", "luc_hao", "bat_tu", "tu_vi", "ha_lac", "chiem_tinh", "common"],
      "mappings": [
        {
          "dim_type": "bat_quai | ngu_hanh | am_duong | thien_can | dia_chi | tiet_khi | hexagram | thap_than | than_sat | cung_tu_vi | huong | mua | tang_phu | thoi | khac",
          "dim_value": "Mộc / Đoài / Tỵ / Đại Quá / ...",
          "reasoning_vi": "1 câu giải thích NGẮN GỌN, đơn giản dễ hiểu",
          "reasoning_zh": "Hán văn nguyên bản nếu trích được",
          "confidence": 0.0-1.0
        }
      ]
    }
  ],
  "contextual_meanings": [
    {
      "phrase_vi": "vd: 'lá rơi mùa hạ'",
      "primary_concept_vi": "vd: 'lá rơi'",
      "modifier_concepts_vi": ["vd: 'mùa hạ'"],
      "meaning_vi": "1-2 câu giải nghĩa cô đọng",
      "school": "common | mai_hoa | ...",
      "confidence": 0.0-1.0
    }
  ]
}
```

## Nguyên tắc

1. **Đơn giản hoá**: dùng tiếng Việt phổ thông, KHÔNG dùng thuật ngữ Hán-Việt nặng nề trong `reasoning_vi`. Mục tiêu: người không biết Dịch cũng hiểu.
2. **Trung thực**: chỉ trích xuất gì TEXT NÊU RÕ. Confidence 0.9+ chỉ khi text khẳng định trực tiếp.
3. **Cô đọng**: mỗi reasoning ≤ 25 từ. Mỗi meaning ≤ 50 từ.
4. **Bỏ qua**: lý thuyết chung (không phải mapping cụ thể), references, lời mở đầu.
5. **Multi-school**: nếu khái niệm áp dụng nhiều phái → tag tất cả phái phù hợp.

## Ví dụ output đúng

Text: "Khôn quái thuộc thổ, đại diện đất, mẹ, vật chứa đựng. Số 8 ứng Khôn."

```json
{
  "concepts": [
    {
      "canonical_vi": "Khôn",
      "canonical_zh": "坤",
      "concept_type": "symbol",
      "aliases": ["quẻ Khôn", "☷"],
      "schools": ["mai_hoa", "common"],
      "mappings": [
        {"dim_type": "ngu_hanh", "dim_value": "thổ",
         "reasoning_vi": "Khôn là đất, đất thuộc thổ", "confidence": 0.95},
        {"dim_type": "bat_quai", "dim_value": "Khôn", "confidence": 1.0}
      ]
    },
    {
      "canonical_vi": "đất", "canonical_zh": "地",
      "concept_type": "concept",
      "mappings": [
        {"dim_type": "bat_quai", "dim_value": "Khôn",
         "reasoning_vi": "Đất là tượng của quẻ Khôn", "confidence": 0.9}
      ]
    }
  ]
}
```

Trả về CHỈ JSON, không markdown wrapper, không lời dẫn."""


# ─── Chunking ────────────────────────────────────────────────────────────────


def _chunk_text(text: str, max_chars: int = 3000) -> list[str]:
    """Split text into chunks of ~max_chars, splitting on paragraph boundaries."""
    paragraphs = re.split(r"\n\s*\n", text)
    chunks: list[str] = []
    cur: list[str] = []
    cur_len = 0
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if cur_len + len(p) > max_chars and cur:
            chunks.append("\n\n".join(cur))
            cur = [p]
            cur_len = len(p)
        else:
            cur.append(p)
            cur_len += len(p) + 2
    if cur:
        chunks.append("\n\n".join(cur))
    return chunks


# ─── Public API ──────────────────────────────────────────────────────────────


@dataclass
class IngestionResult:
    corpus_id: int
    chunks_processed: int
    concepts_added: int
    mappings_added: int
    contextual_added: int
    errors: list[str]


def register_corpus(
    name: str,
    file_path: str,
    *,
    author: str | None = None,
    school: str | None = None,
    language: str = "vi",
    notes: str | None = None,
) -> int:
    """Register a corpus entry (does NOT ingest yet). Returns corpus_id.

    `file_path` is relative to `data/yi_lexicon/corpora/` if not absolute.
    """
    bootstrap_db()
    if not Path(file_path).is_absolute():
        file_path = str(_CORPORA_DIR / file_path)
    c = add_corpus(name=name, author=author, school=school,
                   language=language, file_path=file_path, notes=notes)
    return c.corpus_id


def _merge_extracted(
    extracted: dict, *, source_tag: str, source_meta: dict | None = None,
) -> dict[str, int]:
    """Merge LLM-extracted JSON into lexicon.

    v2 (anh tuyên ngôn 2026-05-12): passes source_tier + source_book through
    `add_mapping()` so conflict detection + provenance work end-to-end.

    `source_meta` keys (all optional):
      - tier: 'S'|'A'|'B'|'C'
      - book_name, chapter, page
    """
    n_concepts = 0
    n_mappings = 0
    n_contextual = 0
    meta = source_meta or {}
    src_tier = meta.get("tier", "B")
    src_book = meta.get("book_name")
    src_chapter = meta.get("chapter")
    src_page = meta.get("page")

    for cdata in extracted.get("concepts", []):
        try:
            concept_type = cdata.get("concept_type", "other")
            # Ownership tracking (v3, đóng vòng YOLO): biết chính xác concept/mapping
            # nào do merge NÀY tạo mới → reject trong distill queue rollback được.
            pre_existing = get_concept(
                canonical_vi=cdata["canonical_vi"], concept_type=concept_type,
            )
            concept = add_concept(
                canonical_vi=cdata["canonical_vi"],
                canonical_zh=cdata.get("canonical_zh"),
                canonical_en=cdata.get("canonical_en"),
                concept_type=concept_type,
                aliases=cdata.get("aliases", []),
                schools=cdata.get("schools", ["common"]),
                source=source_tag,
                confidence=cdata.get("confidence", 0.6),
            )
            n_concepts += 1
            new_mapping_ids: list[int] = []
            for mdata in cdata.get("mappings", []):
                try:
                    mapping_existed = find_mapping(
                        concept.concept_id, mdata["dim_type"], mdata["dim_value"],
                    ) is not None
                    m = add_mapping(
                        concept_id=concept.concept_id,
                        dim_type=mdata["dim_type"],
                        dim_value=mdata["dim_value"],
                        reasoning_vi=mdata.get("reasoning_vi"),
                        reasoning_zh=mdata.get("reasoning_zh"),
                        source=source_tag,
                        confidence=mdata.get("confidence", 0.6),
                        source_tier=src_tier,
                        source_book=src_book,
                        source_chapter=src_chapter,
                        source_page=src_page,
                        source_quote=mdata.get("source_quote"),
                    )
                    n_mappings += 1
                    if not mapping_existed:
                        new_mapping_ids.append(m.mapping_id)
                except Exception:
                    continue
            # Enqueue distill item — payload mang `_merged` (ownership) để
            # anh reject là rollback được đúng phần merge này tạo ra.
            add_distill_item(
                kind="new_concept",
                payload={
                    **cdata,
                    "_merged": {
                        "concept_id": concept.concept_id,
                        "concept_created": pre_existing is None,
                        "mapping_ids": new_mapping_ids,
                    },
                },
                source=source_tag,
                confidence=cdata.get("confidence", 0.6),
                status="auto_accepted",
            )
        except Exception:
            continue

    for cmdata in extracted.get("contextual_meanings", []):
        try:
            # Resolve primary concept by canonical_vi (skip if not found)
            primary = get_concept(canonical_vi=cmdata.get("primary_concept_vi", ""))
            if not primary:
                continue
            from .store import add_contextual_meaning
            add_contextual_meaning(
                primary_concept_id=primary.concept_id,
                meaning_vi=cmdata["meaning_vi"],
                contextual_phrase_vi=cmdata.get("phrase_vi"),
                school=cmdata.get("school", "common"),
                source=source_tag,
                confidence=cmdata.get("confidence", 0.6),
            )
            n_contextual += 1
        except Exception:
            continue

    return {"concepts": n_concepts, "mappings": n_mappings, "contextual": n_contextual}


def ingest_corpus(
    corpus_id: int,
    *,
    llm_provider=None,
    model: str = "deepseek-v4-pro",
    max_chunks: int | None = None,
) -> IngestionResult:
    """Ingest a corpus via LLM extraction + auto-merge.

    Args:
        corpus_id: ID from `register_corpus()`.
        llm_provider: instance of `engine.ai.providers.LLMProvider`. If None,
            tries to load DeepSeek from registry.
        model: LLM model name.
        max_chunks: cap for testing/incremental ingestion.

    YOLO mode: extracted items auto-merge into lexicon. Anh review later via queue.
    """
    bootstrap_db()

    # Load corpus
    from .store import _conn
    with _conn() as c:
        row = c.execute("SELECT * FROM corpora WHERE corpus_id = ?", (corpus_id,)).fetchone()
    if not row:
        return IngestionResult(corpus_id=corpus_id, chunks_processed=0,
                               concepts_added=0, mappings_added=0,
                               contextual_added=0, errors=["corpus not found"])

    file_path = row["file_path"]
    if not file_path or not Path(file_path).exists():
        return IngestionResult(corpus_id=corpus_id, chunks_processed=0,
                               concepts_added=0, mappings_added=0,
                               contextual_added=0, errors=[f"file not found: {file_path}"])

    text = Path(file_path).read_text(encoding="utf-8")
    chunks = _chunk_text(text)
    if max_chunks:
        chunks = chunks[:max_chunks]

    # Resolve provider
    if llm_provider is None:
        try:
            from engine.ai.registry import get_registry
            llm_provider = get_registry().first_configured(
                preferred_order=["deepseek", "zai", "anthropic"]
            ) or None
        except Exception:
            pass
    if llm_provider is None:
        return IngestionResult(corpus_id=corpus_id, chunks_processed=0,
                               concepts_added=0, mappings_added=0,
                               contextual_added=0,
                               errors=["No LLM provider configured — set DEEPSEEK_API_KEY"])

    total = {"concepts": 0, "mappings": 0, "contextual": 0}
    errors: list[str] = []
    source_tag = f"corpus:{row['name']}:v{int(time.time())}"

    for i, chunk in enumerate(chunks):
        try:
            messages = [
                {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": f"## Đoạn text từ '{row['name']}':\n\n{chunk}\n\nTrả về JSON đúng schema."},
            ]
            response = llm_provider.chat(messages=messages, model=model, max_tokens=4000)
            content = response.content if hasattr(response, "content") else str(response)

            # Extract JSON (LLM sometimes wraps in markdown)
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if not json_match:
                errors.append(f"chunk {i}: no JSON found")
                continue
            extracted = json.loads(json_match.group(0))
            merged = _merge_extracted(extracted, source_tag=source_tag)
            for k in total:
                total[k] += merged[k]
        except Exception as e:
            errors.append(f"chunk {i}: {e}")

    # Update corpus stats
    with _conn() as c:
        c.execute(
            "UPDATE corpora SET ingested_at=?, concepts_extracted=?, mappings_extracted=? WHERE corpus_id=?",
            (int(time.time()),
             row["concepts_extracted"] + total["concepts"],
             row["mappings_extracted"] + total["mappings"],
             corpus_id),
        )

    return IngestionResult(
        corpus_id=corpus_id,
        chunks_processed=len(chunks),
        concepts_added=total["concepts"],
        mappings_added=total["mappings"],
        contextual_added=total["contextual"],
        errors=errors,
    )
