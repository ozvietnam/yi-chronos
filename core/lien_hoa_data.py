from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

LIEN_HOA_SOURCE_INDEX_PATH = Path(__file__).resolve().parent.parent / "data" / "seeds" / "lien_hoa_source_index.json"
LIEN_HOA_RULES_PATH = Path(__file__).resolve().parent.parent / "data" / "seeds" / "lien_hoa_rules_v1.json"
LIEN_HOA_READING_QUEUE_PATH = Path(__file__).resolve().parent.parent / "data" / "seeds" / "lien_hoa_reading_queue.json"


@lru_cache(maxsize=1)
def load_lien_hoa_source_index() -> dict[str, Any]:
    if not LIEN_HOA_SOURCE_INDEX_PATH.exists():
        return {"sources": []}
    return json.loads(LIEN_HOA_SOURCE_INDEX_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_lien_hoa_rules() -> dict[str, Any]:
    if not LIEN_HOA_RULES_PATH.exists():
        return {"rules": []}
    return json.loads(LIEN_HOA_RULES_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_lien_hoa_reading_queue() -> dict[str, Any]:
    if not LIEN_HOA_READING_QUEUE_PATH.exists():
        return {"days": []}
    return json.loads(LIEN_HOA_READING_QUEUE_PATH.read_text(encoding="utf-8"))


def list_lien_hoa_rules(status: str | None = None) -> list[dict[str, Any]]:
    rules = list(load_lien_hoa_rules().get("rules", []))
    if status:
        return [rule for rule in rules if str(rule.get("status", "")).lower() == status.lower()]
    return rules


def get_lien_hoa_rule(rule_id: str) -> dict[str, Any] | None:
    for rule in load_lien_hoa_rules().get("rules", []):
        if rule.get("rule_id") == rule_id:
            return rule
    return None
