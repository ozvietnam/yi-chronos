"""Vòng Trường Sinh (12-stage life cycle) — assesses each pillar's branch
against the Day Master's life-energy phase.

Canonical 子平 rule:
- Yang stems (Giáp, Bính, Mậu, Canh, Nhâm) walk FORWARD through 12 branches.
- Yin stems (Ất, Đinh, Kỷ, Tân, Quý) walk BACKWARD.

Starting positions (Trường Sinh — long life / birth):
    Giáp → Hợi, Ất → Ngọ
    Bính + Mậu → Dần, Đinh + Kỷ → Dậu
    Canh → Tỵ, Tân → Tý
    Nhâm → Thân, Quý → Mão

Each pillar's branch position relative to Day Master's Trường Sinh determines
its phase (0..11 corresponding to the 12 stages).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .constants import EARTHLY_BRANCHES, STEM_POLARITY


# 12 phases in canonical order (starting from Trường Sinh = long life / birth)
TRUONG_SINH_PHASES: tuple[str, ...] = (
    "Trường Sinh",   # 0  — birth / long life
    "Mộc Dục",       # 1  — bathing / youthful confusion
    "Quan Đới",      # 2  — cap and belt / coming of age
    "Lâm Quan",      # 3  — taking office / entering career
    "Đế Vượng",      # 4  — emperor's prosperity / peak
    "Suy",           # 5  — decline
    "Bệnh",          # 6  — sickness
    "Tử",            # 7  — death
    "Mộ",            # 8  — tomb
    "Tuyệt",         # 9  — severed
    "Thai",          # 10 — gestation
    "Dưỡng",         # 11 — nurturing / preparation for rebirth
)

# Short labels
TRUONG_SINH_TAG: dict[str, str] = {
    "Trường Sinh": "TS",
    "Mộc Dục": "MD",
    "Quan Đới": "QĐ",
    "Lâm Quan": "LQ",
    "Đế Vượng": "ĐV",
    "Suy": "Suy",
    "Bệnh": "Bệnh",
    "Tử": "Tử",
    "Mộ": "Mộ",
    "Tuyệt": "Tuyệt",
    "Thai": "Thai",
    "Dưỡng": "Dưỡng",
}

# Strength score per phase (rough heuristic for chart assessment).
# Positive = supports Day Master strength; negative = drains.
PHASE_STRENGTH: dict[str, int] = {
    "Trường Sinh": +3,
    "Mộc Dục": +1,
    "Quan Đới": +2,
    "Lâm Quan": +3,
    "Đế Vượng": +4,
    "Suy": 0,
    "Bệnh": -2,
    "Tử": -3,
    "Mộ": -1,
    "Tuyệt": -4,
    "Thai": -1,
    "Dưỡng": +1,
}

# Trường Sinh starting branch per stem.
_TRUONG_SINH_START: dict[str, str] = {
    "Giáp": "Hợi",
    "Ất":   "Ngọ",
    "Bính": "Dần",
    "Đinh": "Dậu",
    "Mậu":  "Dần",
    "Kỷ":   "Dậu",
    "Canh": "Tỵ",
    "Tân":  "Tý",
    "Nhâm": "Thân",
    "Quý":  "Mão",
}


def phase_of_branch(day_master_stem: str, target_branch: str) -> str:
    """Determine the Trường Sinh phase of `target_branch` for `day_master_stem`.

    Yang stems walk forward in the 12-branch cycle starting from their Trường Sinh.
    Yin stems walk backward.
    """
    if day_master_stem not in _TRUONG_SINH_START:
        raise ValueError(f"Unknown stem: {day_master_stem!r}")
    if target_branch not in EARTHLY_BRANCHES:
        raise ValueError(f"Unknown branch: {target_branch!r}")

    start_branch = _TRUONG_SINH_START[day_master_stem]
    start_idx = EARTHLY_BRANCHES.index(start_branch)
    target_idx = EARTHLY_BRANCHES.index(target_branch)
    polarity = STEM_POLARITY[day_master_stem]

    if polarity == "dương":
        # Walk forward: phase index = (target - start) mod 12
        phase_idx = (target_idx - start_idx) % 12
    else:
        # Walk backward: phase index = (start - target) mod 12
        phase_idx = (start_idx - target_idx) % 12

    return TRUONG_SINH_PHASES[phase_idx]


@dataclass(frozen=True)
class TruongSinhEntry:
    """One pillar's Trường Sinh state."""

    pillar_position: str        # 'year' / 'month' / 'day' / 'hour'
    pillar_position_vi: str
    branch: str                 # the pillar's branch
    phase: str                  # one of TRUONG_SINH_PHASES
    phase_tag: str              # short label
    strength_score: int         # -4..+4

    def to_dict(self) -> dict:
        return asdict(self)


def compute_truong_sinh_chart(pillars: dict, day_master_stem: str) -> dict:
    """Compute Trường Sinh phase for each of the 4 pillars vs Day Master.

    Returns:
        {
            'day_master_stem': '...',
            'truong_sinh_start_branch': '...',
            'pillars': {
                'year': TruongSinhEntry.to_dict(),
                ...
            },
            'total_strength_score': int,
        }
    """
    out_pillars: dict[str, dict] = {}
    total = 0
    for pos in ("year", "month", "day", "hour"):
        p = pillars[pos]
        branch = p["branch"]
        phase = phase_of_branch(day_master_stem, branch)
        score = PHASE_STRENGTH[phase]
        entry = TruongSinhEntry(
            pillar_position=pos,
            pillar_position_vi=p.get("position_vi", pos),
            branch=branch,
            phase=phase,
            phase_tag=TRUONG_SINH_TAG[phase],
            strength_score=score,
        )
        out_pillars[pos] = entry.to_dict()
        total += score

    return {
        "day_master_stem": day_master_stem,
        "truong_sinh_start_branch": _TRUONG_SINH_START[day_master_stem],
        "pillars": out_pillars,
        "total_strength_score": total,
    }
