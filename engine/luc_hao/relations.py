"""Element / branch relations + dụng-thần selection.

Public:
- _relation: 5-element relation between day and line
- _impact_label: text label for moving-line impact on Thế
- _days_until_branch: cyclic distance between two earthly branches
- _detect_target_relation: keyword-based domain → lục thân
- _select_dung_than_line / _detect_hidden_line_candidates
"""

from __future__ import annotations

from typing import Any

from .constants import (
    EARTHLY_BRANCHES,
    ELEMENT_CONTROLS,
    ELEMENT_GENERATES,
    QUESTION_DOMAIN_RELATION_MAP,
    RELATION_BY_ELEMENT,
)


def _relation(day_element: str, line_element: str) -> str:
    if day_element == line_element:
        return RELATION_BY_ELEMENT["same"]
    if ELEMENT_GENERATES[day_element] == line_element:
        return RELATION_BY_ELEMENT["generated_by_day"]
    if ELEMENT_GENERATES[line_element] == day_element:
        return RELATION_BY_ELEMENT["generates_day"]
    if ELEMENT_CONTROLS[day_element] == line_element:
        return RELATION_BY_ELEMENT["controlled_by_day"]
    return RELATION_BY_ELEMENT["controls_day"]


def _impact_label(the_element: str, moving_element: str) -> str:
    if ELEMENT_GENERATES[moving_element] == the_element:
        return "Hào động sinh Thế (thuận)"
    if ELEMENT_GENERATES[the_element] == moving_element:
        return "Thế sinh hào động (hao lực)"
    if ELEMENT_CONTROLS[moving_element] == the_element:
        return "Hào động khắc Thế (cảnh giác)"
    if ELEMENT_CONTROLS[the_element] == moving_element:
        return "Thế khắc hào động (chủ động)"
    return "Đồng hành"


def _days_until_branch(current_branch: str, target_branch: str) -> int:
    if current_branch not in EARTHLY_BRANCHES or target_branch not in EARTHLY_BRANCHES:
        return 0
    current_idx = EARTHLY_BRANCHES.index(current_branch)
    target_idx = EARTHLY_BRANCHES.index(target_branch)
    return (target_idx - current_idx) % 12


def _detect_target_relation(question_text: str) -> str:
    q = question_text.lower()
    for keywords, relation in QUESTION_DOMAIN_RELATION_MAP:
        if any(keyword in q for keyword in keywords):
            return relation
    return ""


def _select_dung_than_line(lines: list[dict[str, Any]], question_text: str) -> dict[str, Any]:
    target_relation = _detect_target_relation(question_text)
    if target_relation:
        for line in lines:
            if line["luc_than"] == target_relation:
                return line
    moving_lines = [line for line in lines if line["moving"]]
    return moving_lines[0] if moving_lines else lines[2]


def _detect_hidden_line_candidates(
    lines: list[dict[str, Any]], dung_than_line: dict[str, Any]
) -> list[dict[str, Any]]:
    target_relation = dung_than_line.get("luc_than", "")
    target_pos = dung_than_line.get("line_position")
    hidden = []
    for line in lines:
        if line["line_position"] == target_pos:
            continue
        if line["luc_than"] == target_relation and not line["moving"]:
            hidden.append(
                {
                    "line_position": line["line_position"],
                    "branch": line["branch"],
                    "element": line["element"],
                    "reason": "Đồng lục thân với Dụng thần nhưng ẩn dưới hào tĩnh",
                }
            )
    return hidden
