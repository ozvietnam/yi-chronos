"""Build a complete KHÔNG THỜI SỰ (space-time event row) for one step.

Each không thời sự (KTS) chứa:
  - upper_num, lower_num, hao (the gia số state)
  - chánh quái (binary, hexagram info)
  - hổ quái  (binary, hexagram info)
  - biến quái (binary, hexagram info)
  - TA side (upper / lower) — đơn quái không có hào động
  - TA quái name (the đơn quái that is TA)
  - SỰ side / SỰ quái — đơn quái có hào động
  - Chủ sự: với KTS tiên đề = "TA"; với KTS hậu đề = lục thân của SỰ quái
              relative to TA reference (= TA quái của Tiên đề).
  - Mệnh cung = thượng-Hổ if TA ở thượng, hạ-Hổ if TA ở hạ.
  - Lục thân tag cho TẤT CẢ 6 đơn quái trong Chánh + Hổ + Biến.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .constants import TRIGRAM_ELEMENT
from .luc_than import luc_than_name, luc_than_of_trigram
from .quai_ops import (
    chanh_binary,
    flip_hao,
    hao_side,
    hexagram_info,
    ho_binary,
    lower_trigram_of,
    trigram_from_num,
    upper_trigram_of,
)


@dataclass(frozen=True)
class TaggedTrigram:
    position: str        # "chanh_upper" | "chanh_lower" | "ho_upper" | "ho_lower" | "bien_upper" | "bien_lower"
    trigram: str
    element: str
    luc_than: str        # H/P/C/Q/T (or "TA" if this trigram IS TA)
    luc_than_name: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class KhongThoi:
    index: int                       # 1 for Tiên đề, 2..N for hậu đề
    label: str                       # "Tiên đề" or "Hậu đề 1..4"
    upper_num: int
    lower_num: int
    hao: int
    chanh: dict                      # hexagram_info
    ho: dict
    bien: dict
    ta_side: str                     # "upper" or "lower" (NEW TA of this KTS)
    ta_trigram: str
    su_side: str
    su_trigram: str
    chu_su: str                      # "TA" | "H" | "P" | "C" | "Q" | "T"
    chu_su_name: str                 # "TA" | "Huynh Đệ" | ...
    menh_cung: str                   # "Phong Sơn Tiệm" — name of Hổ quái viewed as Mệnh
    menh_cung_side: str              # "upper" or "lower"
    tagged: list[TaggedTrigram]      # 6 đơn quái với lục thân tag

    def to_dict(self) -> dict:
        d = asdict(self)
        d["tagged"] = [t.to_dict() for t in self.tagged]
        return d


def build_khong_thoi(
    *,
    upper_num: int,
    lower_num: int,
    hao: int,
    index: int,
    is_tien_de: bool,
    ta_reference_element: str,   # element of TA quái of Tiên đề
    ta_reference_trigram: str = "",  # name of TA quái of Tiên đề (e.g. "Càn")
) -> KhongThoi:
    """Construct one không thời sự from gia số state.

    `ta_reference_element` is the element of the TA quái fixed at the Tiên đề.
    All lục thân tags in all không thời are computed relative to this reference.
    """
    chanh_bin = chanh_binary(upper_num, lower_num)
    ho_bin = ho_binary(chanh_bin)
    bien_bin = flip_hao(chanh_bin, hao)

    side_dong = hao_side(hao)
    ta_side = "lower" if side_dong == "upper" else "upper"
    su_side = side_dong

    upper_trigram_name = trigram_from_num(upper_num)
    lower_trigram_name = trigram_from_num(lower_num)
    ta_trigram = upper_trigram_name if ta_side == "upper" else lower_trigram_name
    su_trigram = upper_trigram_name if su_side == "upper" else lower_trigram_name

    # Chủ sự (book p.16+):
    #   Tiên đề: TA là chủ sự (người cầu sự là chủ).
    #   Hậu đề: chủ sự = TA QUÁI CỦA KTS NÀY (đơn quái bất động) — KHÔNG phải SỰ quái.
    #           Lục thân = quan hệ của TA quái KTS này với TA reference (= TA của Tiên đề).
    if is_tien_de:
        chu_su = "TA"
        chu_su_display = "TA"
    elif ta_reference_trigram and ta_trigram == ta_reference_trigram:
        # TA quái giành lại quyền chủ sự (đơn quái bất động = TA original).
        chu_su = "TA"
        chu_su_display = "TA"
    else:
        chu_su = luc_than_of_trigram(ta_reference_element, ta_trigram)
        chu_su_display = luc_than_name(chu_su)

    # Mệnh cung = Hổ quái at TA side (book p.36).
    if ta_side == "upper":
        menh_cung_trigram = upper_trigram_of(ho_bin)
    else:
        menh_cung_trigram = lower_trigram_of(ho_bin)
    menh_cung_side = ta_side

    # Tag lục thân for all 6 đơn quái.
    def tag(position: str, tg: str) -> TaggedTrigram:
        # If this trigram IS the TA of THIS không thời, mark "TA".
        # (Note: lục thân is always relative to Tiên đề's TA element.)
        element = TRIGRAM_ELEMENT[tg]
        is_ta_of_this = (
            (position.endswith("upper") and tg == upper_trigram_name and ta_side == "upper")
            or (position.endswith("lower") and tg == lower_trigram_name and ta_side == "lower")
        )
        if element == ta_reference_element:
            # Same element as TA reference → Huynh Đệ. But if it's literally the TA quái of this KTS, mark "TA".
            key = "TA" if is_ta_of_this and is_tien_de else "H"
            name = "TA" if key == "TA" else luc_than_name("H")
        else:
            key = luc_than_of_trigram(ta_reference_element, tg)
            name = luc_than_name(key)
        return TaggedTrigram(
            position=position,
            trigram=tg,
            element=element,
            luc_than=key,
            luc_than_name=name,
        )

    tagged = [
        tag("chanh_upper", upper_trigram_of(chanh_bin)),
        tag("chanh_lower", lower_trigram_of(chanh_bin)),
        tag("ho_upper", upper_trigram_of(ho_bin)),
        tag("ho_lower", lower_trigram_of(ho_bin)),
        tag("bien_upper", upper_trigram_of(bien_bin)),
        tag("bien_lower", lower_trigram_of(bien_bin)),
    ]

    label = "Tiên đề" if is_tien_de else f"Hậu đề {((index - 1) - 1) % 4 + 1}"

    return KhongThoi(
        index=index,
        label=label,
        upper_num=upper_num,
        lower_num=lower_num,
        hao=hao,
        chanh=hexagram_info(chanh_bin),
        ho=hexagram_info(ho_bin),
        bien=hexagram_info(bien_bin),
        ta_side=ta_side,
        ta_trigram=ta_trigram,
        su_side=su_side,
        su_trigram=su_trigram,
        chu_su=chu_su,
        chu_su_name=chu_su_display,
        menh_cung=menh_cung_trigram,
        menh_cung_side=menh_cung_side,
        tagged=tagged,
    )
