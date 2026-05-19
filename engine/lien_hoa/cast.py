"""Top-level orchestrator for Liên Hoa Độn Pháp cast.

Public function `cast_lien_hoa(...)` accepts the two raw input numbers
(P = right hand, T = left hand) plus question + gender, then returns a full
bản quái kiện with 5 / 9 / 13 không thời sự.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .constants import METHOD_ID, SOURCE_REF, TRIGRAM_ELEMENT
from .don import (
    check_completion,
    compute_don_chain,
    expected_dot_count,
    expected_khong_thoi_count,
)
from .khong_thoi import KhongThoi, build_khong_thoi
from .luan_su import luan_su
from .luan_su_deeper import luan_su_deeper
from .quai_ops import hao_side, mod_hao, mod_quai, trigram_from_num


@dataclass(frozen=True)
class LienHoaSpread:
    method_id: str
    source_ref: str
    question_text: str
    gender: str                          # "nam" or "nữ" — affects lục thân interpretation downstream
    input: dict                          # raw P, T, derived nums
    ta_reference_trigram: str            # TA of Tiên đề
    ta_reference_element: str
    dot_count: int                       # 1, 2, or 3
    khong_thoi_count: int                # 5, 9, or 13
    completed: bool
    khong_thoi: list[KhongThoi]
    note: str

    def to_dict(self) -> dict:
        d = {
            "method_id": self.method_id,
            "source_ref": self.source_ref,
            "question_text": self.question_text,
            "gender": self.gender,
            "input": self.input,
            "ta_reference_trigram": self.ta_reference_trigram,
            "ta_reference_element": self.ta_reference_element,
            "dot_count": self.dot_count,
            "khong_thoi_count": self.khong_thoi_count,
            "completed": self.completed,
            "khong_thoi": [k.to_dict() for k in self.khong_thoi],
            "note": self.note,
        }
        return d


def cast_lien_hoa(
    *,
    number_right_hand: int,
    number_left_hand: int,
    question_text: str = "",
    gender: str = "nam",
) -> dict:
    """Cast a Liên Hoa spread from two raw user-provided numbers.

    Returns a JSON-serializable dict (full bản quái kiện).
    """
    if number_right_hand < 1 or number_left_hand < 1:
        raise ValueError("Both P and T must be ≥ 1")
    if gender not in ("nam", "nữ"):
        raise ValueError("gender must be 'nam' or 'nữ'")

    p_num = mod_quai(number_right_hand)
    t_num = mod_quai(number_left_hand)
    initial_hao = mod_hao(number_right_hand + number_left_hand)

    # Determine TA reference (đơn quái không có hào động of Tiên đề).
    initial_ta_side = "lower" if hao_side(initial_hao) == "upper" else "upper"
    ta_ref_trigram_name = (
        trigram_from_num(p_num) if initial_ta_side == "upper" else trigram_from_num(t_num)
    )
    ta_ref_element = TRIGRAM_ELEMENT[ta_ref_trigram_name]

    # Build Tiên đề KTS.
    tien_de = build_khong_thoi(
        upper_num=p_num,
        lower_num=t_num,
        hao=initial_hao,
        index=1,
        is_tien_de=True,
        ta_reference_element=ta_ref_element,
        ta_reference_trigram=ta_ref_trigram_name,
    )

    # Compute độn chain — sinh hậu đề.
    don_steps = compute_don_chain(p_num, t_num, initial_hao)

    hau_de_list: list[KhongThoi] = []
    for s in don_steps:
        hau_de_list.append(
            build_khong_thoi(
                upper_num=s.upper,
                lower_num=s.lower,
                hao=s.hao,
                index=1 + s.step_index,
                is_tien_de=False,
                ta_reference_element=ta_ref_element,
                ta_reference_trigram=ta_ref_trigram_name,
            )
        )

    completed, dot_at_completion = check_completion(don_steps, initial_ta_side)
    dot_count = expected_dot_count(initial_hao)

    note = (
        f"Đợt độn hoàn thành sau {dot_at_completion}/{dot_count} đợt — "
        f"TA quái {ta_ref_trigram_name} ({ta_ref_element}) "
        f"{'giành lại quyền chủ sự' if completed else 'chưa giành lại chủ sự'}."
    )

    spread = LienHoaSpread(
        method_id=METHOD_ID,
        source_ref=SOURCE_REF,
        question_text=question_text,
        gender=gender,
        input={
            "number_right_hand": number_right_hand,
            "number_left_hand": number_left_hand,
            "right_quai_num": p_num,
            "left_quai_num": t_num,
            "initial_hao": initial_hao,
        },
        ta_reference_trigram=ta_ref_trigram_name,
        ta_reference_element=ta_ref_element,
        dot_count=dot_count,
        khong_thoi_count=expected_khong_thoi_count(initial_hao),
        completed=completed,
        khong_thoi=[tien_de] + hau_de_list,
        note=note,
    )
    spread_dict = spread.to_dict()
    # Append luận sự (interpretation layer).
    spread_dict["luan_su"] = luan_su(spread_dict).to_dict()
    # Deeper layer: per-KTS narrative + extra domains + tổng kết
    spread_dict["luan_su_deeper"] = luan_su_deeper(spread_dict)
    return spread_dict
