"""京房易 (Jīng Fáng) scaffolding for Lục Hào — 8 cung, Najia, Lục thân, 伏神 (Phục thần).

Reference algorithms ported from kentang2017/ichingshifa (MIT) — re-derived from
canonical 京房 sources rather than copied verbatim. See docs/upgrade-plan-...md
mục 6.1.

Convention:
- All hexagram binaries are TOP-DOWN 6-bit strings: bit[0] = hào 6 (top),
  bit[5] = hào 1 (bottom). Matches `core.hexagram.Hexagram.binary`.
- Yao positions are 1-indexed bottom-up (hào 1 = bottom, hào 6 = top).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from .constants import BRANCH_ELEMENT
from .twentyeight_xiu import primary_xiu_dict


# ─── 1. Primitives ─────────────────────────────────────────────────────────────

HEAVENLY_STEMS: tuple[str, ...] = (
    "Giáp", "Ất", "Bính", "Đinh", "Mậu",
    "Kỷ", "Canh", "Tân", "Nhâm", "Quý",
)

# 8 trigrams in 先天 order; top-down 3-bit binary (bit[0]=top yáo).
TRIGRAM_BINARY: dict[str, str] = {
    "Càn":  "111",
    "Đoài": "011",
    "Ly":   "101",
    "Chấn": "001",
    "Tốn":  "110",
    "Khảm": "010",
    "Cấn":  "100",
    "Khôn": "000",
}
BINARY_TO_TRIGRAM: dict[str, str] = {v: k for k, v in TRIGRAM_BINARY.items()}

TRIGRAM_ELEMENT: dict[str, str] = {
    "Càn":  "kim",
    "Đoài": "kim",
    "Ly":   "hỏa",
    "Chấn": "mộc",
    "Tốn":  "mộc",
    "Khảm": "thủy",
    "Cấn":  "thổ",
    "Khôn": "thổ",
}


# ─── 2. Yao bit helpers ────────────────────────────────────────────────────────

def _flip_yao(binary_top_down: str, yao_pos: int) -> str:
    """Flip hào at 1-based position (1=bottom, 6=top) in a top-down binary string."""
    if not 1 <= yao_pos <= 6:
        raise ValueError(f"yao_pos must be 1..6, got {yao_pos}")
    idx = 6 - yao_pos  # bottom = string index 5; top = string index 0
    chars = list(binary_top_down)
    chars[idx] = "1" if chars[idx] == "0" else "0"
    return "".join(chars)


def _split_trigrams(binary_top_down: str) -> tuple[str, str]:
    """Return (upper_trigram_name, lower_trigram_name). Top-down: upper = first 3 bits."""
    upper_bin = binary_top_down[0:3]
    lower_bin = binary_top_down[3:6]
    return BINARY_TO_TRIGRAM[upper_bin], BINARY_TO_TRIGRAM[lower_bin]


# ─── 3. 八宮 (8 Palaces) classifier ────────────────────────────────────────────
#
# Algorithm (canonical 京房 ordering):
#   For each pure trigram T, palace sequence is 8 hexagrams:
#     [0] 本卦   = T over T (3-bit doubled)
#     [1] 一世   = flip hào 1
#     [2] 二世   = flip hào 2 (cumulative)
#     [3] 三世   = flip hào 3
#     [4] 四世   = flip hào 4
#     [5] 五世   = flip hào 5
#     [6] 遊魂   = 五世 with hào 4 flipped back
#     [7] 歸魂   = 遊魂 with lower trigram replaced by T
#
# Verified against the canonical 京房八宮卦 chart for all 8 palaces.

PALACE_ORDER: tuple[str, ...] = (
    "Càn", "Đoài", "Ly", "Chấn", "Tốn", "Khảm", "Cấn", "Khôn",
)

PALACE_POSITION_NAMES: tuple[str, ...] = (
    "Bản cung",  # 0  本卦 (pure)
    "Nhất thế",  # 1  一世
    "Nhị thế",   # 2  二世
    "Tam thế",   # 3  三世
    "Tứ thế",    # 4  四世
    "Ngũ thế",   # 5  五世
    "Du hồn",    # 6  遊魂
    "Quy hồn",   # 7  歸魂
)

# 世爻 position (1-based bottom-up) for each palace position 0..7.
SHIH_POSITION_BY_PALACE_POS: tuple[int, ...] = (
    6,  # 本卦 → 世 at hào 6 (top)
    1,  # 一世 → 世 at hào 1
    2,  # 二世 → 世 at hào 2
    3,  # 三世 → 世 at hào 3
    4,  # 四世 → 世 at hào 4
    5,  # 五世 → 世 at hào 5
    4,  # 遊魂 → 世 at hào 4
    3,  # 歸魂 → 世 at hào 3
)


@lru_cache(maxsize=1)
def _build_palace_table() -> dict[str, tuple[str, int, str]]:
    """Build {binary → (palace_trigram, position_0_to_7, palace_element)}.

    Each entry covers exactly 1 of the 64 hexagrams. Total = 64 entries.
    """
    out: dict[str, tuple[str, int, str]] = {}
    for trigram in PALACE_ORDER:
        pure = TRIGRAM_BINARY[trigram] + TRIGRAM_BINARY[trigram]
        sequence = [pure]
        current = pure
        for yao in range(1, 6):
            current = _flip_yao(current, yao)
            sequence.append(current)
        # 遊魂: 五世 with hào 4 flipped
        youhun = _flip_yao(sequence[5], 4)
        sequence.append(youhun)
        # 歸魂: 遊魂 with lower trigram replaced by palace trigram
        guihun = youhun[0:3] + TRIGRAM_BINARY[trigram]
        sequence.append(guihun)

        for pos, binary in enumerate(sequence):
            out[binary] = (trigram, pos, TRIGRAM_ELEMENT[trigram])
    if len(out) != 64:
        raise RuntimeError(f"Palace table built {len(out)} entries, expected 64")
    return out


def palace_of(binary_top_down: str) -> tuple[str, int, str]:
    """Return (palace_trigram, position_0_to_7, palace_element) for a hexagram."""
    table = _build_palace_table()
    if binary_top_down not in table:
        raise ValueError(f"Unknown hexagram binary: {binary_top_down!r}")
    return table[binary_top_down]


def palace_pure_hexagram(binary_top_down: str) -> str:
    """Return the binary of the palace's 本卦 (pure trigram doubled) for this hexagram."""
    palace_trigram, _, _ = palace_of(binary_top_down)
    return TRIGRAM_BINARY[palace_trigram] + TRIGRAM_BINARY[palace_trigram]


# ─── 4. 納甲 (Najia) — stem/branch per yáo ─────────────────────────────────────
#
# Canonical 京房 納甲 rule:
#   - Inner trigram (下卦, hào 1..3): each trigram has a fixed (stem, branch) triple.
#   - Outer trigram (上卦, hào 4..6): each trigram has a different triple.
#   - 乾/坤 trigrams in outer position use 壬/癸 instead of 甲/乙 (天地分干 rule).
#   - Other trigrams reuse the same stem inner & outer; branches advance.
#
# Tables verified against 火珠林 / 京房易 charts.

# Inner (下卦) — for hào 1, 2, 3 (bottom-up).
NAJIA_INNER: dict[str, list[tuple[str, str]]] = {
    "Càn":  [("Giáp", "Tý"),   ("Giáp", "Dần"),  ("Giáp", "Thìn")],
    "Khôn": [("Ất",   "Mùi"),  ("Ất",   "Tỵ"),   ("Ất",   "Mão")],
    "Chấn": [("Canh", "Tý"),   ("Canh", "Dần"),  ("Canh", "Thìn")],
    "Tốn":  [("Tân",  "Sửu"),  ("Tân",  "Hợi"),  ("Tân",  "Dậu")],
    "Khảm": [("Mậu",  "Dần"),  ("Mậu",  "Thìn"), ("Mậu",  "Ngọ")],
    "Ly":   [("Kỷ",   "Mão"),  ("Kỷ",   "Sửu"),  ("Kỷ",   "Hợi")],
    "Cấn":  [("Bính", "Thìn"), ("Bính", "Ngọ"),  ("Bính", "Thân")],
    "Đoài": [("Đinh", "Tỵ"),   ("Đinh", "Mão"),  ("Đinh", "Sửu")],
}

# Outer (上卦) — for hào 4, 5, 6 (bottom-up).
NAJIA_OUTER: dict[str, list[tuple[str, str]]] = {
    "Càn":  [("Nhâm", "Ngọ"),  ("Nhâm", "Thân"), ("Nhâm", "Tuất")],
    "Khôn": [("Quý",  "Sửu"),  ("Quý",  "Hợi"),  ("Quý",  "Dậu")],
    "Chấn": [("Canh", "Ngọ"),  ("Canh", "Thân"), ("Canh", "Tuất")],
    "Tốn":  [("Tân",  "Mùi"),  ("Tân",  "Tỵ"),   ("Tân",  "Mão")],
    "Khảm": [("Mậu",  "Thân"), ("Mậu",  "Tuất"), ("Mậu",  "Tý")],
    "Ly":   [("Kỷ",   "Dậu"),  ("Kỷ",   "Mùi"),  ("Kỷ",   "Tỵ")],
    "Cấn":  [("Bính", "Tuất"), ("Bính", "Tý"),   ("Bính", "Dần")],
    "Đoài": [("Đinh", "Hợi"),  ("Đinh", "Dậu"),  ("Đinh", "Mùi")],
}


def najia_of(binary_top_down: str) -> list[tuple[str, str]]:
    """Return 6 (stem, branch) tuples, indexed by yáo position 1..6 (bottom-up).

    Output[0] = hào 1 (bottom), Output[5] = hào 6 (top).
    """
    upper, lower = _split_trigrams(binary_top_down)
    inner = NAJIA_INNER[lower]   # hào 1, 2, 3
    outer = NAJIA_OUTER[upper]   # hào 4, 5, 6
    return list(inner) + list(outer)


# ─── 5. 六親 (Lục thân) classifier ─────────────────────────────────────────────
#
# Rule:
#   - yao_element == palace_element     → Huynh Đệ (兄弟)
#   - yao generates palace               → Tử Tôn (子孫) [palace was born from yao]
#   - palace generates yao               → Phụ Mẫu (父母) [palace nurtures yao]
#   - yao controls palace                → Thê Tài (妻財) [palace is dominated by yao]
#   - palace controls yao                → Quan Quỷ (官鬼) [palace overpowers yao]

_GENERATES = {"mộc": "hỏa", "hỏa": "thổ", "thổ": "kim", "kim": "thủy", "thủy": "mộc"}
_CONTROLS = {"mộc": "thổ", "thổ": "thủy", "thủy": "hỏa", "hỏa": "kim", "kim": "mộc"}


def luc_than_of(yao_element: str, palace_element: str) -> str:
    """Return one of {Huynh Đệ, Tử Tôn, Phụ Mẫu, Thê Tài, Quan Quỷ}."""
    if yao_element == palace_element:
        return "Huynh Đệ"
    # NOTE: Lục thân classical comparison is yao vs palace (TA reference = palace).
    if _GENERATES.get(yao_element) == palace_element:
        return "Tử Tôn"         # yao 生 palace → yao là con, palace là mẹ (wait check)
    if _GENERATES.get(palace_element) == yao_element:
        return "Phụ Mẫu"        # palace 生 yao → palace là mẹ → yao là Phụ Mẫu? wait
    if _CONTROLS.get(yao_element) == palace_element:
        return "Thê Tài"        # yao 尅 palace → yao là Thê Tài (vợ - bị TA chinh phục)
    if _CONTROLS.get(palace_element) == yao_element:
        return "Quan Quỷ"       # palace 尅 yao
    raise ValueError(f"Cannot classify lục thân: yao={yao_element}, palace={palace_element}")


# Correction: in standard 京房 Lục thân convention with palace = TA reference:
#   - yao 生 palace = "yao nuôi palace" → yao = Phụ Mẫu (parent of palace)
#   - palace 生 yao = "palace sinh yao" → yao = Tử Tôn (child of palace)
#   - yao 尅 palace = "yao khắc palace" → yao = Quan Quỷ (oppresses TA)
#   - palace 尅 yao = "palace khắc yao" → yao = Thê Tài (TA conquers)
#
# Fix below — replaces the function with the correct mapping.

def luc_than_of(yao_element: str, palace_element: str) -> str:  # noqa: F811
    """Classify the yáo's relation to TA (= palace element)."""
    if yao_element == palace_element:
        return "Huynh Đệ"
    if _GENERATES.get(yao_element) == palace_element:
        return "Phụ Mẫu"       # yao 生 palace → yao là nguồn (Phụ Mẫu)
    if _GENERATES.get(palace_element) == yao_element:
        return "Tử Tôn"        # palace 生 yao → yao là sản phẩm (Tử Tôn)
    if _CONTROLS.get(yao_element) == palace_element:
        return "Quan Quỷ"      # yao 尅 palace → yao là Quan Quỷ
    if _CONTROLS.get(palace_element) == yao_element:
        return "Thê Tài"       # palace 尅 yao → yao là Thê Tài
    raise ValueError(f"Cannot classify: yao={yao_element}, palace={palace_element}")


# ─── 6. 世/應 + 身爻 positions ────────────────────────────────────────────────


def shih_yao_position(binary_top_down: str) -> int:
    """Return 世爻 1-based bottom-up position (1..6)."""
    _, palace_pos, _ = palace_of(binary_top_down)
    return SHIH_POSITION_BY_PALACE_POS[palace_pos]


def ying_yao_position(shih_pos: int) -> int:
    """應爻 = 世 ± 3, wrapping in [1..6]."""
    if shih_pos <= 3:
        return shih_pos + 3
    return shih_pos - 3


# 身爻 mapping: indexed by 世爻's branch.
_SHEN_BY_BRANCH: dict[str, int] = {
    "Tý":  1, "Ngọ":  1,
    "Sửu": 2, "Mùi":  2,
    "Dần": 3, "Thân": 3,
    "Mão": 4, "Dậu":  4,
    "Thìn": 5, "Tuất": 5,
    "Tỵ":  6, "Hợi":  6,
}


def shen_yao_position(shih_branch: str) -> int:
    """Return 身爻 1-based position from the 世爻's branch."""
    return _SHEN_BY_BRANCH[shih_branch]


# ─── 7. 伏神 (Phục thần / hidden lines) — KEY ALGORITHM ────────────────────────
#
# Rule (京房 positional):
#   1. Compute 六親 for all 6 yáo of the cast hexagram.
#   2. Identify which of {Huynh Đệ, Phụ Mẫu, Tử Tôn, Thê Tài, Quan Quỷ} are MISSING.
#   3. For each missing relation, look up the palace's 本卦 (pure hexagram).
#      Compute its 6-yáo 六親 (against the same palace element).
#   4. Find the yáo position in the pure hexagram carrying the missing relation.
#   5. That hidden yáo "sits under" the cast hexagram's yáo at the SAME position
#      (positional 京房 rule, not branch-matching).
#
# Output: list of dicts, one per missing relation.

ALL_LUC_THAN = ("Huynh Đệ", "Phụ Mẫu", "Tử Tôn", "Thê Tài", "Quan Quỷ")


@dataclass(frozen=True)
class PhucThan:
    """One hidden line (伏神) discovered under a visible yáo of the cast hexagram."""

    luc_than: str                     # missing relation now revealed
    visible_yao_position: int         # 1..6 — which cast-hexagram yáo it hides under
    visible_yao_luc_than: str         # the cast hexagram's relation at that position
    palace_pure_yao_position: int     # 1..6 — yáo of the palace's pure hexagram
    stem: str                         # Thiên can of the hidden yáo
    branch: str                       # Địa chi of the hidden yáo
    element: str                      # ngũ hành of the branch
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "luc_than": self.luc_than,
            "visible_yao_position": self.visible_yao_position,
            "visible_yao_luc_than": self.visible_yao_luc_than,
            "palace_pure_yao_position": self.palace_pure_yao_position,
            "stem": self.stem,
            "branch": self.branch,
            "element": self.element,
            "note": self.note,
        }


def luc_than_per_yao(binary_top_down: str) -> list[dict]:
    """Return 6 dicts (one per yáo, bottom-up) with full Najia + Lục thân info."""
    _, _, palace_element = palace_of(binary_top_down)
    najia = najia_of(binary_top_down)
    out: list[dict] = []
    for i, (stem, branch) in enumerate(najia):
        element = BRANCH_ELEMENT[branch]
        relation = luc_than_of(element, palace_element)
        out.append({
            "yao_position": i + 1,        # bottom-up
            "stem": stem,
            "branch": branch,
            "element": element,
            "luc_than": relation,
        })
    return out


def hidden_lines(binary_top_down: str) -> list[PhucThan]:
    """Detect 伏神 — all missing 六親 emerging from the palace's pure hexagram.

    Implements the 京房 positional rule (匹配 by yáo index, not branch).
    Robust to multi-missing cases (upstream ichingshifa silently fails here).
    """
    cast_yao = luc_than_per_yao(binary_top_down)
    cast_relations = {y["luc_than"] for y in cast_yao}

    missing = [r for r in ALL_LUC_THAN if r not in cast_relations]
    if not missing:
        return []

    pure_binary = palace_pure_hexagram(binary_top_down)
    pure_yao = luc_than_per_yao(pure_binary)
    # Map: relation → first yáo position carrying it in the pure hexagram.
    pure_relation_index: dict[str, int] = {}
    for y in pure_yao:
        pure_relation_index.setdefault(y["luc_than"], y["yao_position"])

    out: list[PhucThan] = []
    for relation in missing:
        if relation not in pure_relation_index:
            # Extremely rare: relation missing in both cast AND palace pure.
            # Skip — the canonical 京房 rule has no fallback here.
            continue
        pos = pure_relation_index[relation]
        pure_y = pure_yao[pos - 1]
        visible_y = cast_yao[pos - 1]
        out.append(PhucThan(
            luc_than=relation,
            visible_yao_position=pos,
            visible_yao_luc_than=visible_y["luc_than"],
            palace_pure_yao_position=pos,
            stem=pure_y["stem"],
            branch=pure_y["branch"],
            element=pure_y["element"],
            note=(
                f"Ẩn dưới hào {pos} của quẻ Chánh "
                f"(hào hiện {visible_y['luc_than']}). "
                f"Trích từ thuần quẻ cung "
                f"{palace_of(binary_top_down)[0]}."
            ),
        ))
    return out


# ─── 8. Top-level summary dataclass ────────────────────────────────────────────


@dataclass(frozen=True)
class JingFangScaffold:
    """Full 京房 scaffolding for one cast hexagram."""

    binary: str                          # top-down 6-bit
    palace_trigram: str                  # 八宮 (e.g. "Càn")
    palace_position: int                 # 0..7
    palace_position_name: str            # "Bản cung", ..., "Quy hồn"
    palace_element: str
    najia_per_yao: list[dict]            # 6 yáo, bottom-up
    shih_yao_position: int               # 1..6
    ying_yao_position: int               # 1..6
    shen_yao_position: int               # 1..6
    hidden_lines: list[PhucThan]         # 伏神
    primary_xiu: dict | None = None      # 28-tú primary mansion

    def to_dict(self) -> dict:
        return {
            "binary": self.binary,
            "palace_trigram": self.palace_trigram,
            "palace_position": self.palace_position,
            "palace_position_name": self.palace_position_name,
            "palace_element": self.palace_element,
            "najia_per_yao": self.najia_per_yao,
            "shih_yao_position": self.shih_yao_position,
            "ying_yao_position": self.ying_yao_position,
            "shen_yao_position": self.shen_yao_position,
            "hidden_lines": [h.to_dict() for h in self.hidden_lines],
            "primary_xiu": self.primary_xiu,
        }


def build_jingfang_scaffold(binary_top_down: str, king_wen_index: int | None = None) -> JingFangScaffold:
    """Construct full 京房 scaffold for a hexagram from its binary.

    `king_wen_index` is optional — if provided, attach the primary 28-tú mansion.
    """
    if len(binary_top_down) != 6 or set(binary_top_down) - {"0", "1"}:
        raise ValueError(f"Expected 6-bit binary, got: {binary_top_down!r}")
    palace_trigram, palace_pos, palace_element = palace_of(binary_top_down)
    najia = luc_than_per_yao(binary_top_down)
    shih = shih_yao_position(binary_top_down)
    shih_branch = najia[shih - 1]["branch"]
    xiu = primary_xiu_dict(king_wen_index) if king_wen_index is not None else None
    return JingFangScaffold(
        binary=binary_top_down,
        palace_trigram=palace_trigram,
        palace_position=palace_pos,
        palace_position_name=PALACE_POSITION_NAMES[palace_pos],
        palace_element=palace_element,
        najia_per_yao=najia,
        shih_yao_position=shih,
        ying_yao_position=ying_yao_position(shih),
        shen_yao_position=shen_yao_position(shih_branch),
        hidden_lines=hidden_lines(binary_top_down),
        primary_xiu=xiu,
    )
