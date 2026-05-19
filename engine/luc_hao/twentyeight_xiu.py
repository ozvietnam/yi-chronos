"""28-tú (二十八宿) — 28 lunar mansions for Lục Hào 京房 scaffolding.

Reference: 朱雀玄武白虎青龍 four-quadrant sky map. Each quadrant has 7 mansions;
4 × 7 = 28. Each mansion correlates with a totem animal and a 七曜 weekday element
(木 Wood, 金 Metal, 土 Earth, 日 Sun, 月 Moon, 火 Fire, 水 Water).

This module provides:
1. The canonical 28-mansion ordered list with Vietnamese names + quadrant + 7-yao element.
2. `primary_xiu_for_hexagram(binary)` — assigns one mansion to each cast hexagram by
   cycling the 28-list (rotated to anchor on 參 / Sâm) over the canonical 64-hex order.
   This matches the kentang2017/ichingshifa convention.

NOT IMPLEMENTED (deferred):
- Per-yao mansion distribution (requires the full 二十八宿配干支 table per hexagram
  — see ichingshifa /tmp/ichingshifa.py L392–410). Future work: transcribe canonical
  table from 火珠林 + add unit tests covering all 384 yao.
- Day-stem-branch → mansion lookup (true 天文 layer). Future work: add lunar epoch
  alignment so the cast-date's mansion can be reported alongside.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from itertools import cycle as _itercycle

from core.hexagram import HEXAGRAMS


# ─── 1. Canonical 28-mansion data ──────────────────────────────────────────────
#
# Order is the standard 二十八宿 traversal: starting Đông phương 角 → Nam phương 軫.
# 7-element cycle (per Tống/Đường calendar): 木 金 土 日 月 火 水 — repeating ×4.

@dataclass(frozen=True)
class Mansion:
    index: int                  # 0..27, position in canonical order
    name_vi: str
    name_cn: str                # simplified — single char
    quadrant: str               # Đông / Bắc / Tây / Nam
    spirit: str                 # Thanh Long / Huyền Vũ / Bạch Hổ / Chu Tước
    element_7yao: str           # Mộc / Kim / Thổ / Nhật / Nguyệt / Hỏa / Thủy
    animal: str                 # totem animal — 蛟 龍 貉 …

    def to_dict(self) -> dict:
        return asdict(self)


# Element cycle: Mộc → Kim → Thổ → Nhật → Nguyệt → Hỏa → Thủy (repeating)
_ELEMENT_CYCLE = ("Mộc", "Kim", "Thổ", "Nhật", "Nguyệt", "Hỏa", "Thủy")

# 28 animals (totem) in canonical order — sourced from standard 28-宿 chart.
_ANIMALS = (
    "Giao", "Long", "Lạc", "Thố", "Hồ", "Hổ", "Báo",     # Đông
    "Giải", "Ngưu", "Bức", "Thử", "Yến", "Trư", "Du",     # Bắc
    "Lang", "Cẩu", "Trĩ", "Kê", "Ô", "Hầu", "Viên",       # Tây
    "Hãn", "Dương", "Chương", "Mã", "Lộc", "Xà", "Trùng", # Nam
)

# Build the 28-mansion list.
_MANSION_RAW = (
    # Đông phương Thanh Long (7)
    ("Giác",  "角", "Đông", "Thanh Long"),
    ("Cang",  "亢", "Đông", "Thanh Long"),
    ("Đê",    "氐", "Đông", "Thanh Long"),
    ("Phòng", "房", "Đông", "Thanh Long"),
    ("Tâm",   "心", "Đông", "Thanh Long"),
    ("Vĩ",    "尾", "Đông", "Thanh Long"),
    ("Cơ",    "箕", "Đông", "Thanh Long"),
    # Bắc phương Huyền Vũ (7)
    ("Đẩu",   "斗", "Bắc",  "Huyền Vũ"),
    ("Ngưu",  "牛", "Bắc",  "Huyền Vũ"),
    ("Nữ",    "女", "Bắc",  "Huyền Vũ"),
    ("Hư",    "虛", "Bắc",  "Huyền Vũ"),
    ("Nguy",  "危", "Bắc",  "Huyền Vũ"),
    ("Thất",  "室", "Bắc",  "Huyền Vũ"),
    ("Bích",  "壁", "Bắc",  "Huyền Vũ"),
    # Tây phương Bạch Hổ (7)
    ("Khuê",  "奎", "Tây",  "Bạch Hổ"),
    ("Lâu",   "婁", "Tây",  "Bạch Hổ"),
    ("Vị",    "胃", "Tây",  "Bạch Hổ"),
    ("Mão",   "昴", "Tây",  "Bạch Hổ"),
    ("Tất",   "畢", "Tây",  "Bạch Hổ"),
    ("Chủy",  "觜", "Tây",  "Bạch Hổ"),
    ("Sâm",   "參", "Tây",  "Bạch Hổ"),
    # Nam phương Chu Tước (7)
    ("Tỉnh",  "井", "Nam",  "Chu Tước"),
    ("Quỷ",   "鬼", "Nam",  "Chu Tước"),
    ("Liễu",  "柳", "Nam",  "Chu Tước"),
    ("Tinh",  "星", "Nam",  "Chu Tước"),
    ("Trương","張", "Nam",  "Chu Tước"),
    ("Dực",   "翼", "Nam",  "Chu Tước"),
    ("Chẩn",  "軫", "Nam",  "Chu Tước"),
)


@lru_cache(maxsize=1)
def all_mansions() -> tuple[Mansion, ...]:
    """Return the canonical 28-mansion tuple (length 28)."""
    out = []
    for i, (vi, cn, quad, spirit) in enumerate(_MANSION_RAW):
        out.append(Mansion(
            index=i,
            name_vi=vi,
            name_cn=cn,
            quadrant=quad,
            spirit=spirit,
            element_7yao=_ELEMENT_CYCLE[i % 7],
            animal=_ANIMALS[i],
        ))
    return tuple(out)


def mansion_by_name(name_vi: str) -> Mansion:
    """Look up a mansion by its Vietnamese name (case-sensitive)."""
    for m in all_mansions():
        if m.name_vi == name_vi:
            return m
    raise ValueError(f"Unknown mansion name: {name_vi!r}")


# ─── 2. Hexagram → primary mansion mapping ─────────────────────────────────────
#
# Implementation matches the kentang2017/ichingshifa scheme:
#   - Rotate the 28-mansion list so 參 (Sâm) is at the start.
#   - Cycle through this rotated list over the canonical 64-hex King-Wen order.
#   - Each hexagram gets ONE mansion as its 主宿 (primary star).
#
# This is a deliberately simple positional mapping. The classical 京房 system uses a
# more sophisticated table (二十八宿配干支), but that requires transcription from
# a printed chart. This positional version is reproducible and matches the
# de-facto ichingshifa output for cross-validation.

_ANCHOR_NAME = "Sâm"


@lru_cache(maxsize=1)
def _hexagram_mansion_map() -> dict[int, Mansion]:
    """{king_wen_index → Mansion} via the rotated-cycle algorithm."""
    mansions = all_mansions()
    anchor_idx = next(i for i, m in enumerate(mansions) if m.name_vi == _ANCHOR_NAME)
    rotated = mansions[anchor_idx:] + mansions[:anchor_idx]
    cycler = _itercycle(rotated)

    # HEXAGRAMS is internal-ID ordered; sort by King-Wen index for canonical traversal.
    out: dict[int, Mansion] = {}
    for h in sorted(HEXAGRAMS, key=lambda x: x.king_wen_index):
        out[h.king_wen_index] = next(cycler)
    return out


def primary_xiu_for_hexagram(king_wen_index: int) -> Mansion:
    """Return the primary 28-tú mansion for a given hexagram."""
    table = _hexagram_mansion_map()
    if king_wen_index not in table:
        raise ValueError(f"Invalid King-Wen index: {king_wen_index}")
    return table[king_wen_index]


def primary_xiu_dict(king_wen_index: int) -> dict:
    """Same as `primary_xiu_for_hexagram` but returns a JSON-serializable dict."""
    return primary_xiu_for_hexagram(king_wen_index).to_dict()
