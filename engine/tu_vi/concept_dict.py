"""Concept dictionary — 320 thuật ngữ Tử Vi từ Quyển 1.

Dùng cho WikiText highlight + tooltip popup.
Nguồn: `data/yi_publishing/q1_tuvi/master/concepts_index.json`
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DICT_PATH = Path(
    "/Users/ozvietnamdesktop/Desktop/yi/data/yi_publishing/q1_tuvi/master/concepts_index.json"
)


@lru_cache(maxsize=1)
def load_concepts() -> dict[str, dict]:
    """Load 320 concepts. Lazy + cached."""
    if not DICT_PATH.exists():
        return {}
    try:
        return json.loads(DICT_PATH.read_text())
    except Exception as e:
        logger.error(f"failed to load concepts: {e}")
        return {}


def lookup(term: str) -> Optional[dict]:
    d = load_concepts()
    if term in d:
        return d[term]
    tlow = term.lower().strip()
    for k, v in d.items():
        if tlow == k.lower():
            return v
    return None


def by_kind(kind: str) -> list[dict]:
    """Filter by kind: 'sao' | 'cung' | 'hoa' | 'bien_cach' | 'the_loai'."""
    return [v for v in load_concepts().values() if v.get("kind") == kind]


def all_terms() -> list[str]:
    """Return all term names — useful for wiki highlight matching."""
    return list(load_concepts().keys())


def top_terms(n: int = 50) -> list[dict]:
    """Top N by occurrences."""
    return sorted(load_concepts().values(),
                  key=lambda x: x.get("occurrences", 0), reverse=True)[:n]


def stats() -> dict:
    d = load_concepts()
    if not d:
        return {"total": 0}
    from collections import Counter
    kinds = Counter(v.get("kind", "?") for v in d.values())
    return {
        "total": len(d),
        "by_kind": dict(kinds),
    }


if __name__ == "__main__":
    print(json.dumps(stats(), ensure_ascii=False, indent=2))
    print("\nTop 10 terms:")
    for t in top_terms(10):
        print(f"  [{t.get('kind','?'):>10}] {t['occurrences']:2d}× {t['term']}: {t.get('definition','')[:60]}")
