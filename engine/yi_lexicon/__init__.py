"""YI-Lexicon — Dịch Tự Điển (Yi-Knowledge Graph for YI-CHRONOS).

Motto (anh, 2026-05-12):
> "Trước anh em mình đọc sách để tìm ra quy luật, còn giờ vẫn sách ấy,
>  tìm ra cách mở rộng từ điển, tìm cách biến thuật ngữ thành đơn giản
>  dễ hiểu với người dùng."

Architecture: see `engine/yi_lexicon/__init__.py` docstring (this file).

## Layers

```
CONCEPT  =  atomic symbol (token-level)
            "lá" / "vàng" / "rơi" / "9h sáng"

MAPPING  =  concept → cosmology dimension
            (concept "lá") → (dim "ngũ_hành" = "mộc") with reasoning

CONTEXTUAL  =  composite meaning of multiple concepts
                "lá rơi mùa hạ" → "bất thường, có biến cố quan hệ đôi"

CORPUS   =  source text (cổ thư, sách phái) ingested via LLM

DISTILL_QUEUE  =  proposed concepts/mappings from LLM, anh review (YOLO auto-accept default)
```

## Languages

Mỗi concept lưu 3 ngôn ngữ: `canonical_vi` (chính), `canonical_zh` (易经 nguyên bản),
`canonical_en` (cross-ref international). Aliases multilang trong JSON array.

## Schools

Tất cả trường phái dùng CHUNG thư viện. Mỗi concept tag `schools_json` (e.g.
`["mai_hoa", "lien_hoa"]`) để query filter khi cần specialize.

## Public API

```python
from engine.yi_lexicon import (
    add_concept, get_concept, search_concepts,
    add_mapping, mappings_for,
    interpret_observation,
    ingest_corpus, distill_from_council,
)
```
"""

from .store import (
    Concept,
    ConflictGroup,
    Mapping,
    ContextualMeaning,
    Corpus,
    DistillItem,
    add_concept,
    add_contextual_meaning,
    add_corpus,
    add_distill_item,
    add_mapping,
    bootstrap_db,
    delete_concept_if_orphan,
    delete_mapping,
    find_mapping,
    get_concept,
    get_distill_item,
    get_distill_queue,
    list_conflicts,
    list_corpora,
    mappings_for,
    resolve_conflict,
    resolve_distill_item,
    review_distill_item,
    reverse_lookup_concepts,
    search_concepts,
    stats,
)

__all__ = [
    "Concept",
    "ConflictGroup",
    "Mapping",
    "ContextualMeaning",
    "Corpus",
    "DistillItem",
    "add_concept",
    "add_contextual_meaning",
    "add_corpus",
    "add_distill_item",
    "add_mapping",
    "bootstrap_db",
    "delete_concept_if_orphan",
    "delete_mapping",
    "find_mapping",
    "get_concept",
    "get_distill_item",
    "get_distill_queue",
    "list_conflicts",
    "list_corpora",
    "mappings_for",
    "resolve_conflict",
    "resolve_distill_item",
    "review_distill_item",
    "reverse_lookup_concepts",
    "search_concepts",
    "stats",
]
