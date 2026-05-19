from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

LUC_HAO_SOURCE_INDEX_PATH = Path(__file__).resolve().parent.parent / "data" / "seeds" / "luc_hao_source_index.json"
LUC_HAO_RULES_PATH = Path(__file__).resolve().parent.parent / "data" / "seeds" / "luc_hao_rules_v1.json"
LUC_HAO_READING_QUEUE_PATH = Path(__file__).resolve().parent.parent / "data" / "seeds" / "luc_hao_reading_queue.json"


@lru_cache(maxsize=1)
def load_luc_hao_source_index() -> dict[str, Any]:
    if not LUC_HAO_SOURCE_INDEX_PATH.exists():
        return {"sources": []}
    return json.loads(LUC_HAO_SOURCE_INDEX_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_luc_hao_rules() -> dict[str, Any]:
    if not LUC_HAO_RULES_PATH.exists():
        return {"rules": []}
    return json.loads(LUC_HAO_RULES_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_luc_hao_reading_queue() -> dict[str, Any]:
    if not LUC_HAO_READING_QUEUE_PATH.exists():
        return {"days": []}
    return json.loads(LUC_HAO_READING_QUEUE_PATH.read_text(encoding="utf-8"))


def list_luc_hao_rules(status: str | None = None) -> list[dict[str, Any]]:
    rules = list(load_luc_hao_rules().get("rules", []))
    if status:
        return [rule for rule in rules if str(rule.get("status", "")).lower() == status.lower()]
    return rules


def get_luc_hao_rule(rule_id: str) -> dict[str, Any] | None:
    for rule in load_luc_hao_rules().get("rules", []):
        if rule.get("rule_id") == rule_id:
            return rule
    return None


def list_luc_hao_reading_days(status: str | None = None) -> list[dict[str, Any]]:
    days = list(load_luc_hao_reading_queue().get("days", []))
    if status:
        return [day for day in days if str(day.get("status", "")).lower() == status.lower()]
    return days
