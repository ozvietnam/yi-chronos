from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from core.hexagram import list_hexagrams

SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "seeds" / "hexagram_texts_ngotatto.json"
TAM_THIEN_SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "seeds" / "hexagram_insights_tam_thien.json"
INTERPRET_V2_SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "seeds" / "hexagram_interpretation_v2.json"


@lru_cache(maxsize=1)
def _load_seed() -> dict[str, Any]:
    if not SEED_PATH.exists():
        return {"records": []}
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _load_tam_thien_seed() -> dict[str, Any]:
    if not TAM_THIEN_SEED_PATH.exists():
        return {"records": []}
    return json.loads(TAM_THIEN_SEED_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _load_interpret_v2_seed() -> dict[str, Any]:
    if not INTERPRET_V2_SEED_PATH.exists():
        return {"records": []}
    return json.loads(INTERPRET_V2_SEED_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _by_name() -> dict[str, dict[str, Any]]:
    records = _load_seed().get("records", [])
    return {str(item.get("name_vi", "")).strip().lower(): item for item in records}


@lru_cache(maxsize=1)
def _tam_thien_by_name() -> dict[str, dict[str, Any]]:
    records = _load_tam_thien_seed().get("records", [])
    return {str(item.get("name_vi", "")).strip().lower(): item for item in records}


@lru_cache(maxsize=1)
def _interpret_v2_by_index() -> dict[int, dict[str, Any]]:
    records = _load_interpret_v2_seed().get("records", [])
    return {int(item.get("king_wen_index")): item for item in records if item.get("king_wen_index") is not None}


@lru_cache(maxsize=1)
def _interpret_v2_by_name() -> dict[str, dict[str, Any]]:
    records = _load_interpret_v2_seed().get("records", [])
    return {str(item.get("name_vi", "")).strip().lower(): item for item in records}


def get_hexagram_text(name_vi: str) -> dict[str, Any] | None:
    return _by_name().get(name_vi.strip().lower())


def get_hexagram_interpretation_v2(*, name_vi: str | None = None, king_wen_index: int | None = None) -> dict[str, Any] | None:
    if king_wen_index is not None:
        record = _interpret_v2_by_index().get(int(king_wen_index))
        if record:
            return record
    if name_vi:
        return _interpret_v2_by_name().get(name_vi.strip().lower())
    return None


def _summarize_easy_vi(
    *,
    current_judgement: str,
    transformed_judgement: str,
    selected_lines: list[dict[str, Any]],
    policy: str,
    tam_thien_plain_vi: str,
) -> str:
    current_short = re.sub(r"\s+", " ", current_judgement).strip()[:220]
    transformed_short = re.sub(r"\s+", " ", transformed_judgement).strip()[:200]
    lines_short = [re.sub(r"\s+", " ", item.get("text", "")).strip()[:120] for item in selected_lines if item.get("text")]

    if policy == "original_judgement":
        base = f"Nên bám quẻ gốc: {current_short}"
    elif policy == "moving_line_texts":
        if lines_short:
            base = "Ưu tiên hào động: " + " | ".join(lines_short)
        else:
            base = f"Ưu tiên quẻ gốc: {current_short}"
    elif policy == "dual_hexagram_context":
        base = f"Đọc song song quẻ gốc và quẻ biến. Gốc: {current_short} | Biến: {transformed_short}"
    else:
        base = f"Nghiêng về quẻ biến: {transformed_short or current_short}"

    if tam_thien_plain_vi:
        return f"{base}. Gợi ý Tam Thiên: {tam_thien_plain_vi}."
    return base


def explain_by_policy(
    *,
    hexagram_name: str,
    transformed_name: str,
    moving_lines: list[int],
    moving_line_policy: str,
) -> dict[str, Any]:
    current = get_hexagram_text(hexagram_name) or {}
    transformed = get_hexagram_text(transformed_name) or {}
    tam_thien = _tam_thien_by_name().get(hexagram_name.strip().lower(), {})
    current_judgement = current.get("judgement_text", "") or ""
    transformed_judgement = transformed.get("judgement_text", "") or ""
    line_texts = current.get("line_texts", {}) or {}
    selected_lines = [
        {"line": line, "text": line_texts.get(str(line), "")}
        for line in sorted(set(moving_lines))
    ]

    if moving_line_policy == "original_judgement":
        summary = current_judgement
    elif moving_line_policy == "moving_line_texts":
        non_empty = [item["text"] for item in selected_lines if item["text"]]
        summary = " | ".join(non_empty) if non_empty else current_judgement
    elif moving_line_policy == "dual_hexagram_context":
        summary = f"{current_judgement} || Quẻ biến: {transformed_judgement}".strip()
    else:
        summary = transformed_judgement or current_judgement

    easy_vi = _summarize_easy_vi(
        current_judgement=current_judgement,
        transformed_judgement=transformed_judgement,
        selected_lines=selected_lines,
        policy=moving_line_policy,
        tam_thien_plain_vi=tam_thien.get("plain_vi", ""),
    )
    source_refs = [value for value in {_load_seed().get("source_book"), tam_thien.get("source_ref")} if value]
    interpret_v2 = get_hexagram_interpretation_v2(name_vi=hexagram_name)

    return {
        "policy": moving_line_policy,
        "hexagram_name": hexagram_name,
        "transformed_hexagram_name": transformed_name,
        "judgement_text": current_judgement,
        "transformed_judgement_text": transformed_judgement,
        "selected_line_texts": selected_lines,
        "summary": summary.strip(),
        "easy_vi_explanation": easy_vi,
        "tam_thien_plain_vi": tam_thien.get("plain_vi", ""),
        "interpretation_v2": interpret_v2,
        "source_refs": source_refs,
        "source_book": _load_seed().get("source_book"),
    }


def get_source_coverage() -> dict[str, Any]:
    main_records = _load_seed().get("records", [])
    tam_thien_records = _load_tam_thien_seed().get("records", [])

    main_names = {str(item.get("name_vi", "")).strip() for item in main_records if item.get("name_vi")}
    tam_thien_names = {str(item.get("name_vi", "")).strip() for item in tam_thien_records if item.get("name_vi")}

    missing_tam_thien = sorted(name for name in main_names if name and name not in tam_thien_names)

    return {
        "main_source": _load_seed().get("source_book"),
        "tam_thien_source": _load_tam_thien_seed().get("source_book"),
        "main_count": len(main_names),
        "tam_thien_count": len(tam_thien_names),
        "coverage_ratio_tam_thien_vs_main": round(len(tam_thien_names) / len(main_names), 4) if main_names else 0.0,
        "missing_in_tam_thien": missing_tam_thien,
    }


def get_source_matrix() -> dict[str, Any]:
    main_by_name = _by_name()
    tam_thien_by_name = _tam_thien_by_name()
    rows: list[dict[str, Any]] = []

    for hx in sorted(list_hexagrams(), key=lambda item: item.king_wen_index):
        key = hx.name_vi.strip().lower()
        in_main = key in main_by_name
        in_tam_thien = key in tam_thien_by_name
        rows.append(
            {
                "king_wen_index": hx.king_wen_index,
                "name_vi": hx.name_vi,
                "in_main_source": in_main,
                "in_tam_thien_source": in_tam_thien,
                "main_source_ref": main_by_name.get(key, {}).get("source_ref"),
                "tam_thien_source_ref": tam_thien_by_name.get(key, {}).get("source_ref"),
                "tam_thien_plain_vi": tam_thien_by_name.get(key, {}).get("plain_vi", ""),
            }
        )

    return {
        "main_source": _load_seed().get("source_book"),
        "tam_thien_source": _load_tam_thien_seed().get("source_book"),
        "count": len(rows),
        "rows": rows,
    }


def get_auto_audit_report() -> dict[str, Any]:
    coverage = get_source_coverage()
    matrix = get_source_matrix()
    rows = matrix.get("rows", [])
    missing_main = [row["name_vi"] for row in rows if not row.get("in_main_source")]
    missing_tam_thien = [row["name_vi"] for row in rows if not row.get("in_tam_thien_source")]

    status = "ok" if not missing_main and not missing_tam_thien else "degraded"
    return {
        "status": status,
        "summary": {
            "total_hexagrams": matrix.get("count", 0),
            "main_count": coverage.get("main_count", 0),
            "tam_thien_count": coverage.get("tam_thien_count", 0),
            "coverage_ratio_tam_thien_vs_main": coverage.get("coverage_ratio_tam_thien_vs_main", 0.0),
        },
        "missing": {
            "main_source": missing_main,
            "tam_thien_source": missing_tam_thien,
        },
        "sources": {
            "main_source": coverage.get("main_source"),
            "tam_thien_source": coverage.get("tam_thien_source"),
        },
    }
