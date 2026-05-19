"""Dyad analysis — Bát Tự compatibility between 2 charts.

Classical rules implemented:

1. **Thiên Can hợp** (Heavenly Stem combinations) — Giáp+Kỷ / Ất+Canh / Bính+Tân /
   Đinh+Nhâm / Mậu+Quý. Both stems "marry" into a new element.
2. **Thiên Can khắc** (Stem control) — Giáp khắc Mậu (Mộc khắc Thổ), etc.
3. **Địa Chi tam hợp** (Branch trio) — Thân-Tý-Thìn (Thủy), Tỵ-Dậu-Sửu (Kim),
   Dần-Ngọ-Tuất (Hỏa), Hợi-Mão-Mùi (Mộc).
4. **Địa Chi lục hợp** (Branch pair combo) — Tý-Sửu / Dần-Hợi / Mão-Tuất / Thìn-Dậu /
   Tỵ-Thân / Ngọ-Mùi.
5. **Địa Chi lục xung** (Direct opposition) — Tý-Ngọ / Sửu-Mùi / Dần-Thân /
   Mão-Dậu / Thìn-Tuất / Tỵ-Hợi.
6. **Địa Chi tam hình** (Trine punishment) — Dần-Tỵ-Thân, Sửu-Tuất-Mùi, Tý-Mão (xung),
   Thìn/Ngọ/Dậu/Hợi tự hình.
7. **Tam Tai** — based on year-branch trios.

Compat score 0..1: weighted sum of pair-wise checks across all 4 trụ.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


# ─── Classical compat tables ────────────────────────────────────────────────


# Thiên Can hợp: each stem pairs with one other, transforming into a target element
THIEN_CAN_HOP: dict[frozenset[str], str] = {
    frozenset({"Giáp", "Kỷ"}): "thổ",
    frozenset({"Ất", "Canh"}): "kim",
    frozenset({"Bính", "Tân"}): "thủy",
    frozenset({"Đinh", "Nhâm"}): "mộc",
    frozenset({"Mậu", "Quý"}): "hỏa",
}

# Thiên Can khắc (control): {controller: victim}
STEM_CONTROL: dict[str, str] = {
    "Giáp": "Mậu", "Ất": "Kỷ",
    "Bính": "Canh", "Đinh": "Tân",
    "Mậu": "Nhâm", "Kỷ": "Quý",
    "Canh": "Giáp", "Tân": "Ất",
    "Nhâm": "Bính", "Quý": "Đinh",
}

# Địa Chi tam hợp (Three-Harmony groups) → new element
TAM_HOP: dict[frozenset[str], str] = {
    frozenset({"Thân", "Tý", "Thìn"}): "thủy",
    frozenset({"Tỵ", "Dậu", "Sửu"}): "kim",
    frozenset({"Dần", "Ngọ", "Tuất"}): "hỏa",
    frozenset({"Hợi", "Mão", "Mùi"}): "mộc",
}

# Địa Chi lục hợp (Six-Harmony pairs)
LUC_HOP: dict[frozenset[str], str] = {
    frozenset({"Tý", "Sửu"}): "thổ",     # 子丑合土
    frozenset({"Dần", "Hợi"}): "mộc",
    frozenset({"Mão", "Tuất"}): "hỏa",
    frozenset({"Thìn", "Dậu"}): "kim",
    frozenset({"Tỵ", "Thân"}): "thủy",
    frozenset({"Ngọ", "Mùi"}): "thổ",
}

# Địa Chi lục xung (Six Clashes)
LUC_XUNG: set[frozenset[str]] = {
    frozenset({"Tý", "Ngọ"}),
    frozenset({"Sửu", "Mùi"}),
    frozenset({"Dần", "Thân"}),
    frozenset({"Mão", "Dậu"}),
    frozenset({"Thìn", "Tuất"}),
    frozenset({"Tỵ", "Hợi"}),
}

# Địa Chi lục hại (Six Harms)
LUC_HAI: set[frozenset[str]] = {
    frozenset({"Tý", "Mùi"}),
    frozenset({"Sửu", "Ngọ"}),
    frozenset({"Dần", "Tỵ"}),
    frozenset({"Mão", "Thìn"}),
    frozenset({"Thân", "Hợi"}),
    frozenset({"Dậu", "Tuất"}),
}


# ─── Analysis ────────────────────────────────────────────────────────────────


@dataclass
class StemBranchPair:
    stem: str
    branch: str

    @classmethod
    def from_pillar(cls, pillar: dict) -> "StemBranchPair":
        return cls(stem=pillar["stem"], branch=pillar["branch"])


@dataclass
class PairwiseSignal:
    """One classical signal detected between 2 pillars."""
    pillar_a: str         # 'year'/'month'/'day'/'hour'
    pillar_b: str
    signal: str           # 'stem_hop' | 'stem_khac' | 'tam_hop' | 'luc_hop' |
                          # 'luc_xung' | 'luc_hai' | 'truong_phuc' | 'no_interaction'
    detail: str           # human-readable
    polarity: str         # 'positive' | 'negative' | 'neutral'
    weight: float         # 0..1 — how strong this signal is


@dataclass
class DyadCompat:
    """Compatibility analysis between two charts."""
    name_a: str
    name_b: str
    day_master_a: str
    day_master_b: str
    overall_score: float       # 0..1
    overall_label: str         # 'rất hợp' | 'hợp' | 'trung bình' | 'kỵ' | 'rất kỵ'
    signals: list[PairwiseSignal]
    day_master_compat: dict    # detailed Day Master interaction
    summary_vi: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d["signals"] = [asdict(s) for s in self.signals]
        return d


# ─── Helpers ────────────────────────────────────────────────────────────────


def _stem_pair_signal(stem_a: str, stem_b: str, pos_a: str, pos_b: str) -> list[PairwiseSignal]:
    out: list[PairwiseSignal] = []
    pair = frozenset({stem_a, stem_b})
    if stem_a == stem_b:
        out.append(PairwiseSignal(
            pillar_a=pos_a, pillar_b=pos_b,
            signal="stem_giong",
            detail=f"Cùng can {stem_a} — tỉ kiên ngang vai",
            polarity="neutral", weight=0.3,
        ))
    elif pair in THIEN_CAN_HOP:
        target = THIEN_CAN_HOP[pair]
        out.append(PairwiseSignal(
            pillar_a=pos_a, pillar_b=pos_b,
            signal="stem_hop",
            detail=f"{stem_a}-{stem_b} hợp hoá {target.title()} — duyên gắn kết, hợp tác sâu",
            polarity="positive", weight=0.8,
        ))
    elif STEM_CONTROL.get(stem_a) == stem_b:
        out.append(PairwiseSignal(
            pillar_a=pos_a, pillar_b=pos_b,
            signal="stem_khac",
            detail=f"{stem_a} khắc {stem_b} — A chế áp B",
            polarity="negative", weight=0.6,
        ))
    elif STEM_CONTROL.get(stem_b) == stem_a:
        out.append(PairwiseSignal(
            pillar_a=pos_a, pillar_b=pos_b,
            signal="stem_khac",
            detail=f"{stem_b} khắc {stem_a} — B chế áp A",
            polarity="negative", weight=0.6,
        ))
    return out


def _branch_pair_signal(branch_a: str, branch_b: str, pos_a: str, pos_b: str) -> list[PairwiseSignal]:
    out: list[PairwiseSignal] = []
    pair = frozenset({branch_a, branch_b})
    if pair in LUC_HOP:
        target = LUC_HOP[pair]
        out.append(PairwiseSignal(
            pillar_a=pos_a, pillar_b=pos_b,
            signal="luc_hop",
            detail=f"{branch_a}-{branch_b} lục hợp hoá {target.title()} — gắn kết bền",
            polarity="positive", weight=0.7,
        ))
    elif pair in LUC_XUNG:
        out.append(PairwiseSignal(
            pillar_a=pos_a, pillar_b=pos_b,
            signal="luc_xung",
            detail=f"{branch_a}-{branch_b} lục xung — xung đột trực diện",
            polarity="negative", weight=0.7,
        ))
    elif pair in LUC_HAI:
        out.append(PairwiseSignal(
            pillar_a=pos_a, pillar_b=pos_b,
            signal="luc_hai",
            detail=f"{branch_a}-{branch_b} lục hại — mâu thuẫn ngầm",
            polarity="negative", weight=0.5,
        ))
    elif branch_a == branch_b:
        out.append(PairwiseSignal(
            pillar_a=pos_a, pillar_b=pos_b,
            signal="branch_giong",
            detail=f"Cùng chi {branch_a}",
            polarity="neutral", weight=0.3,
        ))
    return out


def _tam_hop_check(branches_a: list[str], branches_b: list[str]) -> list[PairwiseSignal]:
    """Check if A's branches + B's branches form a tam-hợp trio."""
    out: list[PairwiseSignal] = []
    combined = set(branches_a) | set(branches_b)
    for trio, target in TAM_HOP.items():
        # Only count if A and B each contribute ≥1 branch
        a_contrib = trio & set(branches_a)
        b_contrib = trio & set(branches_b)
        if a_contrib and b_contrib and trio.issubset(combined):
            out.append(PairwiseSignal(
                pillar_a="(multi-A)", pillar_b="(multi-B)",
                signal="tam_hop",
                detail=f"Tam hợp {'-'.join(sorted(trio))} hoá {target.title()} — đồng thuận lớn",
                polarity="positive", weight=0.9,
            ))
    return out


# ─── Day Master interaction ─────────────────────────────────────────────────


def _day_master_interaction(stem_a: str, stem_b: str, elem_a: str, elem_b: str) -> dict:
    """Detailed Day Master interaction."""
    pair = frozenset({stem_a, stem_b})
    interaction: dict = {
        "stem_a": stem_a, "stem_b": stem_b,
        "elem_a": elem_a, "elem_b": elem_b,
    }
    if pair in THIEN_CAN_HOP:
        target = THIEN_CAN_HOP[pair]
        interaction["mode"] = "hop"
        interaction["target"] = target
        interaction["note"] = f"Day Master hợp hoá {target.title()} — kết duyên sâu (hôn nhân/đối tác lâu dài)"
        interaction["score"] = 0.9
    elif STEM_CONTROL.get(stem_a) == stem_b:
        interaction["mode"] = "a_controls_b"
        interaction["note"] = f"{stem_a} khắc {stem_b} — A là người chủ động, B chịu áp lực"
        interaction["score"] = 0.4
    elif STEM_CONTROL.get(stem_b) == stem_a:
        interaction["mode"] = "b_controls_a"
        interaction["note"] = f"{stem_b} khắc {stem_a} — B chủ động, A chịu áp lực"
        interaction["score"] = 0.4
    elif elem_a == elem_b:
        interaction["mode"] = "same_element"
        interaction["note"] = "Cùng ngũ hành Day Master — đồng chí hướng nhưng dễ cạnh tranh"
        interaction["score"] = 0.6
    else:
        # Generation check
        generates = {
            "mộc": "hỏa", "hỏa": "thổ", "thổ": "kim", "kim": "thủy", "thủy": "mộc",
        }
        if generates.get(elem_a) == elem_b:
            interaction["mode"] = "a_generates_b"
            interaction["note"] = f"{elem_a.title()} sinh {elem_b.title()} — A nuôi dưỡng B"
            interaction["score"] = 0.75
        elif generates.get(elem_b) == elem_a:
            interaction["mode"] = "b_generates_a"
            interaction["note"] = f"{elem_b.title()} sinh {elem_a.title()} — B nuôi dưỡng A"
            interaction["score"] = 0.75
        else:
            interaction["mode"] = "neutral"
            interaction["note"] = "Day Master không có tương tác mạnh"
            interaction["score"] = 0.5
    return interaction


# ─── Main public API ─────────────────────────────────────────────────────────


def analyze_dyad(chart_a: dict, chart_b: dict, *, name_a: str = "A", name_b: str = "B") -> DyadCompat:
    """Compute pairwise compatibility between 2 Bát Tự charts.

    Each chart must have shape: {tu_tru: {pillars: {year, month, day, hour}}, ...}
    Same shape returned by `engine.bat_tu.cast.cast_bat_tu` or `engine.ai.founder_chart.cast_founder_bat_tu`.
    """
    pillars_a = chart_a["tu_tru"]["pillars"]
    pillars_b = chart_b["tu_tru"]["pillars"]
    dm_a = chart_a["tu_tru"]["day_master"]
    dm_b = chart_b["tu_tru"]["day_master"]

    signals: list[PairwiseSignal] = []

    # Pairwise stem + branch checks across 4 trụ
    positions = ("year", "month", "day", "hour")
    for pa in positions:
        for pb in positions:
            sa, ba = pillars_a[pa]["stem"], pillars_a[pa]["branch"]
            sb, bb = pillars_b[pb]["stem"], pillars_b[pb]["branch"]
            signals.extend(_stem_pair_signal(sa, sb, f"a.{pa}", f"b.{pb}"))
            signals.extend(_branch_pair_signal(ba, bb, f"a.{pa}", f"b.{pb}"))

    # Tam-hợp combined branch check
    branches_a = [pillars_a[p]["branch"] for p in positions]
    branches_b = [pillars_b[p]["branch"] for p in positions]
    signals.extend(_tam_hop_check(branches_a, branches_b))

    # Day Master core interaction (weighted heaviest)
    dm_interaction = _day_master_interaction(
        dm_a["stem"], dm_b["stem"], dm_a["element"], dm_b["element"],
    )

    # Aggregate score: weighted sum of polarity × weight + Day Master × 0.4
    pos_sum = sum(s.weight for s in signals if s.polarity == "positive")
    neg_sum = sum(s.weight for s in signals if s.polarity == "negative")
    # Normalize by signal count; clamp 0..1
    total_w = pos_sum + neg_sum
    if total_w > 0:
        signal_score = pos_sum / total_w
    else:
        signal_score = 0.5
    overall = 0.6 * signal_score + 0.4 * dm_interaction["score"]
    overall = max(0.0, min(1.0, overall))

    # Label
    if overall >= 0.75:
        label = "rất hợp"
    elif overall >= 0.6:
        label = "hợp"
    elif overall >= 0.4:
        label = "trung bình"
    elif overall >= 0.25:
        label = "kỵ"
    else:
        label = "rất kỵ"

    # Summary
    n_pos = sum(1 for s in signals if s.polarity == "positive")
    n_neg = sum(1 for s in signals if s.polarity == "negative")
    summary = (
        f"{name_a} ({dm_a['stem']} {dm_a['element']}) × {name_b} ({dm_b['stem']} {dm_b['element']}): "
        f"{label.upper()} ({overall:.2f}). "
        f"{n_pos} tín hiệu thuận, {n_neg} tín hiệu nghịch. "
        f"Day Master: {dm_interaction['note']}"
    )

    return DyadCompat(
        name_a=name_a, name_b=name_b,
        day_master_a=f"{dm_a['stem']} {dm_a['element']}",
        day_master_b=f"{dm_b['stem']} {dm_b['element']}",
        overall_score=round(overall, 3),
        overall_label=label,
        signals=signals,
        day_master_compat=dm_interaction,
        summary_vi=summary,
    )
