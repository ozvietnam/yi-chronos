"""Quẻ bản mệnh + compatibility scoring.

Compute the user's "natal" hexagram from their birth datetime via
Mai Hoa Niên-Nguyệt-Nhật-Thời, then score the resonance between any
target moment's hexagram + Can-Chi state and that birth state.

Score is in [0, 100]. State-only — describes resonance, not advice.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from core.chronos import ChronosState, calculate_chronos_state
from core.hexagram import TRIGRAM_BITS
from core.yi64.derivations.derived_hexagrams import (
    compute_all_derived,
    derived_summary_dict,
)
from core.yi64.derivations.mai_hoa_nntt import (
    METHOD_ID,
    SOURCE_REF,
    derivation_summary,
    derive_line_states,
)
from core.yi64.transforms import lines_to_binary, moving_lines_from_states


TRIGRAM_ELEMENT = {
    "Càn": "kim", "Đoài": "kim",
    "Ly": "hỏa",
    "Chấn": "mộc", "Tốn": "mộc",
    "Khảm": "thủy",
    "Cấn": "thổ", "Khôn": "thổ",
}

GENERATES = {"mộc": "hỏa", "hỏa": "thổ", "thổ": "kim", "kim": "thủy", "thủy": "mộc"}
CONTROLS = {"mộc": "thổ", "thổ": "thủy", "thủy": "hỏa", "hỏa": "kim", "kim": "mộc"}

# Earthly Branch interactions.
BRANCH_CLASH = {
    "Tý": "Ngọ", "Sửu": "Mùi", "Dần": "Thân", "Mão": "Dậu",
    "Thìn": "Tuất", "Tỵ": "Hợi", "Ngọ": "Tý", "Mùi": "Sửu",
    "Thân": "Dần", "Dậu": "Mão", "Tuất": "Thìn", "Hợi": "Tỵ",
}
BRANCH_SIX_HARMONY = {
    "Tý": "Sửu", "Sửu": "Tý", "Dần": "Hợi", "Hợi": "Dần",
    "Mão": "Tuất", "Tuất": "Mão", "Thìn": "Dậu", "Dậu": "Thìn",
    "Tỵ": "Thân", "Thân": "Tỵ", "Ngọ": "Mùi", "Mùi": "Ngọ",
}
THREE_HARMONY_GROUPS = (
    {"Thân", "Tý", "Thìn"},
    {"Hợi", "Mão", "Mùi"},
    {"Dần", "Ngọ", "Tuất"},
    {"Tỵ", "Dậu", "Sửu"},
)

# Tiết khí element emphasis (24 tiết khí mapped to dominant element).
TIET_KHI_ELEMENT = {
    "Lập xuân": "mộc", "Vũ thủy": "mộc", "Kinh trập": "mộc",
    "Xuân phân": "mộc", "Thanh minh": "mộc", "Cốc vũ": "mộc",
    "Lập hạ": "hỏa", "Tiểu mãn": "hỏa", "Mang chủng": "hỏa",
    "Hạ chí": "hỏa", "Tiểu thử": "hỏa", "Đại thử": "thổ",
    "Lập thu": "thổ", "Xử thử": "kim", "Bạch lộ": "kim",
    "Thu phân": "kim", "Hàn lộ": "kim", "Sương giáng": "thổ",
    "Lập đông": "thủy", "Tiểu tuyết": "thủy", "Đại tuyết": "thủy",
    "Đông chí": "thủy", "Tiểu hàn": "thủy", "Đại hàn": "thổ",
}


@dataclass(frozen=True)
class NatalHexagram:
    method_id: str
    source_ref: str
    birth_local_datetime: str
    birth_timezone: str
    derivation: dict
    primary_binary: str
    primary_name: str
    primary_king_wen: int
    upper_trigram: str
    lower_trigram: str
    upper_element: str
    lower_element: str
    moving_line: int
    derived_hexagrams: dict  # chanh/ho/bien/giao/phuc/bao
    natal_ganzhi: dict       # year/month/day/hour pillars
    natal_solar_term: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class CompatibilityBreakdown:
    base_score: int
    self_match_bonus: int
    derived_overlap_bonus: int
    upper_element_score: int
    lower_element_score: int
    branch_interaction_score: int
    stem_score: int
    tiet_khi_score: int
    final_score: int                 # clamped 0..100
    notes: tuple[str, ...]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["notes"] = list(self.notes)
        return d


def _natal_from_state(state: ChronosState, birth_local_datetime: str, birth_timezone: str) -> NatalHexagram:
    line_states = derive_line_states(state)
    primary_binary = lines_to_binary(line_states)
    moving = moving_lines_from_states(line_states)
    summary = derivation_summary(state)
    derived = derived_summary_dict(primary_binary, moving)
    primary = compute_all_derived(primary_binary, moving)["chanh"]

    return NatalHexagram(
        method_id=METHOD_ID,
        source_ref=SOURCE_REF,
        birth_local_datetime=birth_local_datetime,
        birth_timezone=birth_timezone,
        derivation=summary,
        primary_binary=primary_binary,
        primary_name=primary.name_vi,
        primary_king_wen=primary.king_wen_index,
        upper_trigram=summary["upper_trigram"],
        lower_trigram=summary["lower_trigram"],
        upper_element=TRIGRAM_ELEMENT[summary["upper_trigram"]],
        lower_element=TRIGRAM_ELEMENT[summary["lower_trigram"]],
        moving_line=summary["moving_line"],
        derived_hexagrams=derived,
        natal_ganzhi={
            "year": state.ganzhi.year,
            "month": state.ganzhi.month,
            "day": state.ganzhi.day,
            "hour": state.ganzhi.hour,
        },
        natal_solar_term=state.solar_term.name_vi,
    )


def compute_natal_hexagram(birth_datetime_local: str, timezone: str = "Asia/Ho_Chi_Minh") -> NatalHexagram:
    state = calculate_chronos_state(birth_datetime_local, timezone)
    return _natal_from_state(state, birth_datetime_local, timezone)


def _branch_of_pillar(pillar: str) -> str:
    return pillar.split()[1]


def _stem_of_pillar(pillar: str) -> str:
    return pillar.split()[0]


def _element_relation_score(a: str, b: str) -> tuple[int, str]:
    """Return (score in -15..+15, label) for two-element interaction."""
    if a == b:
        return 10, "tỷ hòa"
    if GENERATES.get(a) == b:
        return 12, f"{a} sinh {b}"
    if GENERATES.get(b) == a:
        return 8, f"{b} sinh {a}"
    if CONTROLS.get(a) == b:
        return -10, f"{a} khắc {b}"
    if CONTROLS.get(b) == a:
        return -8, f"{b} khắc {a}"
    return 0, "trung tính"


def _branch_interaction_score(target_branch: str, natal_branch: str) -> tuple[int, str]:
    if target_branch == natal_branch:
        return 8, "đồng chi"
    if BRANCH_CLASH.get(target_branch) == natal_branch:
        return -25, f"xung {target_branch}-{natal_branch}"
    if BRANCH_SIX_HARMONY.get(target_branch) == natal_branch:
        return 18, f"lục hợp {target_branch}-{natal_branch}"
    for group in THREE_HARMONY_GROUPS:
        if target_branch in group and natal_branch in group:
            return 12, f"tam hợp ({', '.join(sorted(group))})"
    return 0, "trung tính"


def score_compatibility(natal: NatalHexagram, target_state: ChronosState) -> CompatibilityBreakdown:
    """Score how the target_state's day resonates with natal hexagram + Can-Chi."""
    target_lines = derive_line_states(target_state)
    target_binary = lines_to_binary(target_lines)
    target_moving = moving_lines_from_states(target_lines)
    target_summary = derivation_summary(target_state)
    target_derived = derived_summary_dict(target_binary, target_moving)
    target_upper = TRIGRAM_ELEMENT[target_summary["upper_trigram"]]
    target_lower = TRIGRAM_ELEMENT[target_summary["lower_trigram"]]

    base = 50
    notes: list[str] = []

    self_match = 0
    if target_binary == natal.primary_binary:
        self_match = 25
        notes.append("Quẻ ngày trùng quẻ bản mệnh — cộng hưởng tự thân.")

    derived_overlap = 0
    natal_set = {hx["binary"] for hx in natal.derived_hexagrams.values()}
    target_set = {hx["binary"] for hx in target_derived.values()}
    overlap = natal_set & target_set
    if overlap:
        derived_overlap = min(15, 4 * len(overlap))
        notes.append(f"{len(overlap)} quẻ phái sinh trùng (Hỗ/Biến/Giao/Phục/Bao).")

    upper_score, upper_label = _element_relation_score(natal.upper_element, target_upper)
    if upper_score != 0:
        notes.append(f"Thượng quái: {upper_label}.")
    lower_score, lower_label = _element_relation_score(natal.lower_element, target_lower)
    if lower_score != 0:
        notes.append(f"Hạ quái: {lower_label}.")

    target_day_branch = _branch_of_pillar(target_state.ganzhi.day)
    natal_day_branch = _branch_of_pillar(natal.natal_ganzhi["day"])
    branch_score, branch_label = _branch_interaction_score(target_day_branch, natal_day_branch)
    if branch_score != 0:
        notes.append(f"Chi ngày: {branch_label}.")

    target_day_stem = _stem_of_pillar(target_state.ganzhi.day)
    natal_day_stem = _stem_of_pillar(natal.natal_ganzhi["day"])
    stem_score = 6 if target_day_stem == natal_day_stem else 0
    if stem_score:
        notes.append(f"Cùng thiên can ngày ({target_day_stem}).")

    target_tiet = target_state.solar_term.name_vi
    target_tiet_element = TIET_KHI_ELEMENT.get(target_tiet, None)
    natal_dominant = natal.upper_element  # use upper as primary expression
    tiet_score = 0
    if target_tiet_element:
        if target_tiet_element == natal_dominant:
            tiet_score = 5
            notes.append(f"Tiết khí ({target_tiet}) cùng hành với thượng quái bản mệnh.")
        elif GENERATES.get(target_tiet_element) == natal_dominant:
            tiet_score = 4
            notes.append(f"Tiết khí ({target_tiet}) sinh thượng quái bản mệnh.")
        elif CONTROLS.get(target_tiet_element) == natal_dominant:
            tiet_score = -6
            notes.append(f"Tiết khí ({target_tiet}) khắc thượng quái bản mệnh.")

    raw = base + self_match + derived_overlap + upper_score + lower_score + branch_score + stem_score + tiet_score
    final = max(0, min(100, raw))

    return CompatibilityBreakdown(
        base_score=base,
        self_match_bonus=self_match,
        derived_overlap_bonus=derived_overlap,
        upper_element_score=upper_score,
        lower_element_score=lower_score,
        branch_interaction_score=branch_score,
        stem_score=stem_score,
        tiet_khi_score=tiet_score,
        final_score=final,
        notes=tuple(notes),
    )
