"""LLM prompt builder + response parser for Domain 2 + 4 traits."""
from __future__ import annotations

import json
import re

# Allowed values per LLM-derived trait (validated on parse).
LLM_OUTPUT_SCHEMA = {
    "decision_style":         ["impulsive", "analytical", "consultative", "patient"],
    "leadership_orientation": ["dominant", "collaborative", "supportive", "independent"],
    "emotional_pattern":      ["cool", "passionate", "volatile", "steady"],
    "communication_style":    ["direct", "nuanced", "quiet", "expressive"],
    "career_direction":       ["corporate", "creative", "entrepreneurial", "professional", "craftsman"],
    "marriage_timing_rough":  ["som_25", "25_30", "30_35", "muon_35"],
    "health_pattern_general": ["strong", "on", "nhay", "yeu_vung_x"],
}


def build_trait_prompt(candidates: list[dict]) -> str:
    """Build single-shot prompt asking LLM to predict 7 LLM-traits per candidate.

    Args:
        candidates: list of {"chi": str, "pillars": {year/month/day/hour: {stem,branch}}}
    """
    cand_blocks = []
    for c in candidates:
        p = c["pillars"]
        line = (f"- Giờ {c['chi']}: năm={p['year']['stem']}{p['year']['branch']}, "
                f"tháng={p['month']['stem']}{p['month']['branch']}, "
                f"ngày={p['day']['stem']}{p['day']['branch']}, "
                f"giờ={p['hour']['stem']}{p['hour']['branch']}")
        cand_blocks.append(line)

    enum_lines = "\n".join(
        f"  - {trait}: {' | '.join(values)}"
        for trait, values in LLM_OUTPUT_SCHEMA.items()
    )

    return f"""You are a Tử Bình (Four Pillars / Bát Tự) expert. For EACH bát tự candidate below, predict 7 personality + life-event traits.

CANDIDATES:
{chr(10).join(cand_blocks)}

For each candidate, predict these 7 traits (use EXACTLY one of the allowed values):
{enum_lines}

Reasoning hints:
- decision_style: derive from Thập Thần dominant pattern (Tỷ Kiếp → impulsive; Ấn → analytical; Tài Quan balance → consultative)
- leadership_orientation: derive from Cách Cục + Quan Sát strength
- emotional_pattern: derive from Thủy/Hỏa balance across pillars
- communication_style: Thực Thần/Thương Quan presence
- career_direction: Cách Cục + dominant element career affinity
- marriage_timing_rough: Quan/Sát timing relative to day master
- health_pattern_general: Day Master vượng/nhược + xung-khắc

OUTPUT FORMAT — strict JSON only, no prose, no markdown:
{{
  "<chi_name>": {{"decision_style": "...", "leadership_orientation": "...", ...}},
  ...
}}
"""


_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.+?\})\s*```", re.DOTALL)
_JSON_OBJECT_RE = re.compile(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", re.DOTALL)


def _extract_json_payload(raw: str) -> str:
    """Pull out the most likely JSON object from raw LLM text.

    Priority:
      1. fenced ```json ... ``` block
      2. last balanced { ... } in the text (handles reasoner CoT preambles)
      3. raw stripped
    """
    if not raw:
        return ""
    m = _JSON_FENCE_RE.search(raw)
    if m:
        return m.group(1)
    # Take the LARGEST {...} block — typically the structured answer at end
    candidates = _JSON_OBJECT_RE.findall(raw)
    if candidates:
        return max(candidates, key=len)
    return raw.strip()


def parse_llm_response(raw: str, expected_candidates: list[str]) -> dict:
    """Extract + validate JSON from LLM response.

    Returns: {chi: {trait: value}, ...}
    Raises: ValueError on invalid JSON or invalid enum values.
    """
    payload = _extract_json_payload(raw)
    if not payload:
        raise ValueError("LLM returned non-JSON: empty response")

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned non-JSON: {e}") from e

    if not isinstance(data, dict):
        raise ValueError(f"LLM returned non-object root: {type(data).__name__}")

    # Validate enum values
    for chi in expected_candidates:
        if chi not in data:
            continue  # partial — engine handles missing per trait
        chi_traits = data[chi]
        if not isinstance(chi_traits, dict):
            raise ValueError(f"Candidate {chi} not a dict")
        for trait, value in chi_traits.items():
            if trait in LLM_OUTPUT_SCHEMA:
                allowed = LLM_OUTPUT_SCHEMA[trait]
                if value not in allowed:
                    raise ValueError(
                        f"Invalid value for {trait}: {value!r} "
                        f"(allowed: {allowed})"
                    )
    return data
