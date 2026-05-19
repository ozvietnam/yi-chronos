"""Family / household system — multi-actor extension of personal_quai.

Implements 4 fusion methods specified by user directive:

1. Gia Đạo Hexagram — Mai Hoa NNTT applied to the wedding moment, treated
   as the household's "natal" hexagram. State of the system, not the person.

2. Thái Tuế Nhập Quái — for each family member, look up which Lục thân
   (Thê Tài / Tử Tôn / Phụ Mẫu / Huynh Đệ / Quan Quỷ) corresponds to their
   structural role, and check how their year branch interacts with lines
   of that Lục thân in the husband's natal hexagram (sinh / khắc / xung / hợp).

3. Số học Mai Hoa hợp nhất — formula:
       upper = (sum_of_all_members_signature) mod 8     [excluding children]
       lower = (sum_of_all_members_signature) mod 8     [including children]
       moving_line = (full_sum) mod 6
   Each member's "signature" = year_branch_idx + lunar_month + lunar_day
   (their NNTT pre-mod input).

4. Element bridging — analyse element graph (Kim/Mộc/Thủy/Hỏa/Thổ) of all
   members' upper-trigram elements; identify members whose element bridges
   a clash between two others via the generation cycle.

Framing rule: like everything in this codebase, output describes
RESONANCE STATE, not destiny. Gated by EXPERIMENTAL_MODE for prescriptive
suggestions (we surface state only here; GPS layer handles prescription).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional

from core.chronos import calculate_chronos_state
from engine.personal_quai import (
    BRANCH_CLASH,
    BRANCH_SIX_HARMONY,
    CONTROLS,
    GENERATES,
    THREE_HARMONY_GROUPS,
    TRIGRAM_ELEMENT,
    NatalHexagram,
    compute_natal_hexagram,
)


# Role → which Lục thân the family member symbolically occupies in the
# husband's chart. Source: classical Lục Hào pháp (Hoàng Cực Kinh Thế).
ROLE_TO_LUC_THAN = {
    "self": None,            # Hào Thế itself, not a Lục thân.
    "spouse": "Thê Tài",     # 妻財 — wife / wealth.
    "child": "Tử Tôn",       # 子孫 — children / blessings, dissolves Quan Quỷ.
    "parent": "Phụ Mẫu",     # 父母 — parents / structure.
    "sibling": "Huynh Đệ",   # 兄弟 — siblings / peers.
    "boss": "Quan Quỷ",      # 官鬼 — authority / pressure.
}

ROLE_VI = {
    "self": "Bản thân",
    "spouse": "Vợ / Chồng",
    "child": "Con",
    "parent": "Cha mẹ",
    "sibling": "Anh chị em",
    "boss": "Cấp trên",
}

# Year branch index 1..12 anchored on 1984 = Giáp Tý.
YEAR_BRANCH_BY_INDEX = (
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
    "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
)


def year_branch_for(year: int) -> str:
    return YEAR_BRANCH_BY_INDEX[((year - 1984) % 12 + 12) % 12]


def year_branch_idx_for(year: int) -> int:
    return ((year - 1984) % 12 + 12) % 12 + 1  # 1..12


@dataclass(frozen=True)
class FamilyMember:
    role: str                          # See ROLE_TO_LUC_THAN keys.
    name: str
    birth_year: int                    # Always required (drives year branch).
    birth_datetime_local: Optional[str] = None  # Optional — full NNTT if given.
    timezone: str = "Asia/Ho_Chi_Minh"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class MemberSignature:
    """Per-member numbers used by Method 3 (Unified Math)."""
    role: str
    name: str
    year: int
    year_branch: str
    year_branch_idx: int        # 1..12
    lunar_month: int            # 1..12 (defaults to 1 if no full datetime)
    lunar_day: int              # 1..30 (defaults to 1 if no full datetime)
    signature_sum: int          # year_branch_idx + lunar_month + lunar_day

    def to_dict(self) -> dict:
        return asdict(self)


def _signature_for_member(m: FamilyMember) -> MemberSignature:
    year_branch = year_branch_for(m.birth_year)
    year_branch_idx = year_branch_idx_for(m.birth_year)
    if m.birth_datetime_local:
        state = calculate_chronos_state(m.birth_datetime_local, m.timezone)
        lunar_day_str, lunar_month_str, _ = state.almanac.lunar_date.split("/")
        lunar_month = int(lunar_month_str)
        lunar_day = int(lunar_day_str)
    else:
        # Year-only fallback. Use month=1, day=1 as deterministic placeholder.
        # User can refine later by adding birth_datetime_local.
        lunar_month = 1
        lunar_day = 1

    signature_sum = year_branch_idx + lunar_month + lunar_day
    return MemberSignature(
        role=m.role,
        name=m.name,
        year=m.birth_year,
        year_branch=year_branch,
        year_branch_idx=year_branch_idx,
        lunar_month=lunar_month,
        lunar_day=lunar_day,
        signature_sum=signature_sum,
    )


# -----------------------------------------------------------------------------
# Method 1: Gia Đạo Hexagram — wedding moment as household natal.
# -----------------------------------------------------------------------------

def compute_marriage_hexagram(
    wedding_datetime_local: str,
    timezone: str = "Asia/Ho_Chi_Minh",
) -> NatalHexagram:
    """Mai Hoa NNTT applied to the wedding moment.

    The household has its own "natal" hexagram, separate from each spouse's.
    """
    return compute_natal_hexagram(wedding_datetime_local, timezone)


# -----------------------------------------------------------------------------
# Method 2: Thái Tuế Nhập Quái — branch interactions between members & lines.
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class BranchInteraction:
    member_role: str
    member_role_vi: str
    member_name: str
    member_year_branch: str
    luc_than_target: str
    interaction: str         # "đồng chi" | "lục hợp" | "tam hợp" | "xung" | "trung tính"
    score: int               # -25..+18 (negative = clash, positive = harmony)
    explanation: str

    def to_dict(self) -> dict:
        return asdict(self)


def _interaction_between_branches(member_branch: str, line_branch: str) -> tuple[str, int, str]:
    """Score the interaction of two earthly branches.

    Mirrors logic in engine.personal_quai._branch_interaction_score but
    returns Vietnamese label first.
    """
    if member_branch == line_branch:
        return "đồng chi", 8, f"Cùng chi {member_branch} — cộng hưởng tự nhiên."
    if BRANCH_CLASH.get(member_branch) == line_branch:
        return "xung", -25, f"Xung {member_branch}-{line_branch} — đối nghịch trực tiếp."
    if BRANCH_SIX_HARMONY.get(member_branch) == line_branch:
        return "lục hợp", 18, f"Lục hợp {member_branch}-{line_branch} — kết dính bền."
    for group in THREE_HARMONY_GROUPS:
        if member_branch in group and line_branch in group:
            return (
                "tam hợp",
                12,
                f"Tam hợp ({', '.join(sorted(group))}) — phối hợp 3 lực thuận chiều.",
            )
    return "trung tính", 0, "Không có tương tác trực tiếp."


def compute_family_overlay_for_branch(
    family_members: list[FamilyMember],
    target_branch: str,
    skip_self: bool = True,
) -> tuple[tuple[BranchInteraction, ...], int]:
    """Score how each family member's year branch interacts with a given branch.

    Returns: (per_member_overlay, average_score).
    Used by van_trong_van (target=day branch) and gps (target=hour-pillar branch).
    """
    interactions: list[BranchInteraction] = []
    for m in family_members:
        if skip_self and m.role == "self":
            continue
        member_branch = year_branch_for(m.birth_year)
        kind, score, expl = _interaction_between_branches(member_branch, target_branch)
        interactions.append(
            BranchInteraction(
                member_role=m.role,
                member_role_vi=ROLE_VI.get(m.role, m.role),
                member_name=m.name,
                member_year_branch=member_branch,
                luc_than_target=ROLE_TO_LUC_THAN.get(m.role, "—") or "—",
                interaction=kind,
                score=score,
                explanation=expl,
            )
        )
    if not interactions:
        return tuple(), 0
    avg = round(sum(i.score for i in interactions) / len(interactions))
    return tuple(interactions), avg


def compute_thai_tue_overlay(
    natal: NatalHexagram,
    family_members: list[FamilyMember],
) -> list[BranchInteraction]:
    """For each member, score how their year branch interacts with relevant chart points.

    For v1: compare member's year branch to natal day-pillar branch (which
    drives Lục thân attribution in Lục Hào). Deeper version would walk all
    6 lines of the natal Lục Hào cast — left for a future iteration.
    """
    natal_day_branch = natal.natal_ganzhi["day"].split()[1]

    out: list[BranchInteraction] = []
    for m in family_members:
        if m.role == "self":
            continue  # Self is the Hào Thế baseline.
        member_branch = year_branch_for(m.birth_year)
        kind, score, expl = _interaction_between_branches(member_branch, natal_day_branch)
        out.append(
            BranchInteraction(
                member_role=m.role,
                member_role_vi=ROLE_VI.get(m.role, m.role),
                member_name=m.name,
                member_year_branch=member_branch,
                luc_than_target=ROLE_TO_LUC_THAN.get(m.role, "—") or "—",
                interaction=kind,
                score=score,
                explanation=expl,
            )
        )
    return out


# -----------------------------------------------------------------------------
# Method 3: Số học Mai Hoa hợp nhất — unified formula across members.
# -----------------------------------------------------------------------------

def _mod8(value: int) -> int:
    rem = value % 8
    return rem if rem != 0 else 8


def _mod6(value: int) -> int:
    rem = value % 6
    return rem if rem != 0 else 6


# Tiên-thiên trigram order, indexed 1..8.
TIEN_THIEN_TRIGRAMS = (
    "Càn", "Đoài", "Ly", "Chấn", "Tốn", "Khảm", "Cấn", "Khôn",
)


@dataclass(frozen=True)
class UnifiedHouseholdHexagram:
    member_signatures: tuple[MemberSignature, ...]
    sum_excluding_children: int     # husband + wife + parents + ...
    sum_full: int                   # + children
    upper_num: int                  # 1..8
    lower_num: int                  # 1..8
    moving_line: int                # 1..6
    upper_trigram: str
    lower_trigram: str
    primary_binary: str             # 6-char top-down
    primary_name: str
    primary_king_wen: int
    derived_hexagrams: dict         # full 5 derived (chanh/ho/bien/giao/phuc/bao)

    def to_dict(self) -> dict:
        d = {
            "member_signatures": [s.to_dict() for s in self.member_signatures],
            "sum_excluding_children": self.sum_excluding_children,
            "sum_full": self.sum_full,
            "upper_num": self.upper_num,
            "lower_num": self.lower_num,
            "moving_line": self.moving_line,
            "upper_trigram": self.upper_trigram,
            "lower_trigram": self.lower_trigram,
            "primary_binary": self.primary_binary,
            "primary_name": self.primary_name,
            "primary_king_wen": self.primary_king_wen,
            "derived_hexagrams": self.derived_hexagrams,
        }
        return d


def compute_unified_household_hexagram(
    family_members: list[FamilyMember],
) -> UnifiedHouseholdHexagram:
    """Method 3: unified Mai Hoa across the family.

    upper = (sum of non-child members' signatures) mod 8
    lower = (sum of all members' signatures incl. children) mod 8
    moving = (sum of all signatures) mod 6
    """
    from core.hexagram import TRIGRAM_BITS
    from core.yi64.derivations.derived_hexagrams import (
        compute_all_derived,
        derived_summary_dict,
    )

    sigs = tuple(_signature_for_member(m) for m in family_members)

    sum_no_children = sum(s.signature_sum for s in sigs if s.role != "child")
    sum_full = sum(s.signature_sum for s in sigs)

    if not sigs:
        raise ValueError("family_members must not be empty")

    upper_num = _mod8(sum_no_children) if sum_no_children > 0 else _mod8(sum_full)
    lower_num = _mod8(sum_full)
    moving_line = _mod6(sum_full)

    upper_trigram = TIEN_THIEN_TRIGRAMS[upper_num - 1]
    lower_trigram = TIEN_THIEN_TRIGRAMS[lower_num - 1]
    primary_binary = f"{TRIGRAM_BITS[upper_trigram]}{TRIGRAM_BITS[lower_trigram]}"

    derived = compute_all_derived(primary_binary, (moving_line,))
    primary = derived["chanh"]

    return UnifiedHouseholdHexagram(
        member_signatures=sigs,
        sum_excluding_children=sum_no_children,
        sum_full=sum_full,
        upper_num=upper_num,
        lower_num=lower_num,
        moving_line=moving_line,
        upper_trigram=upper_trigram,
        lower_trigram=lower_trigram,
        primary_binary=primary_binary,
        primary_name=primary.name_vi,
        primary_king_wen=primary.king_wen_index,
        derived_hexagrams=derived_summary_dict(primary_binary, (moving_line,)),
    )


# -----------------------------------------------------------------------------
# Method 4: Element bridging — find members who resolve clash via generation.
# -----------------------------------------------------------------------------

def _member_element(m: FamilyMember) -> str:
    """Get a member's "primary element" via their natal upper trigram.

    Uses Mai Hoa NNTT if full datetime given; otherwise falls back to the
    branch-element of their year branch.
    """
    if m.birth_datetime_local:
        try:
            natal = compute_natal_hexagram(m.birth_datetime_local, m.timezone)
            return natal.upper_element
        except Exception:
            pass
    # Year-branch element fallback.
    from engine.luc_hao.constants import BRANCH_ELEMENT
    return BRANCH_ELEMENT[year_branch_for(m.birth_year)]


@dataclass(frozen=True)
class BridgeRelation:
    pair_a: str          # member name A
    pair_b: str          # member name B
    element_a: str
    element_b: str
    clash_type: str      # "khắc" | "đồng" | "sinh" | "neutral"
    bridge_member: str | None  # name of a member whose element bridges via generation
    bridge_element: str | None
    bridge_path: str | None    # e.g., "Kim → Thủy → Mộc"

    def to_dict(self) -> dict:
        return asdict(self)


def analyze_element_bridging(
    family_members: list[FamilyMember],
) -> list[BridgeRelation]:
    """For every pair of members, identify if a third member's element
    creates a generation-chain bridge that thông quan the clash."""

    enriched = [(m, _member_element(m)) for m in family_members]
    out: list[BridgeRelation] = []
    n = len(enriched)
    for i in range(n):
        for j in range(i + 1, n):
            ma, ea = enriched[i]
            mb, eb = enriched[j]
            if ea == eb:
                clash_type = "đồng"
            elif GENERATES.get(ea) == eb or GENERATES.get(eb) == ea:
                clash_type = "sinh"
            elif CONTROLS.get(ea) == eb or CONTROLS.get(eb) == ea:
                clash_type = "khắc"
            else:
                clash_type = "neutral"

            bridge_member = None
            bridge_element = None
            bridge_path = None

            if clash_type == "khắc":
                # Find any third member whose element c satisfies:
                #   ea generates c AND c generates eb,
                # OR eb generates c AND c generates ea.
                for k in range(n):
                    if k in (i, j):
                        continue
                    mc, ec = enriched[k]
                    if GENERATES.get(ea) == ec and GENERATES.get(ec) == eb:
                        bridge_member = mc.name
                        bridge_element = ec
                        bridge_path = f"{ea} → {ec} → {eb}"
                        break
                    if GENERATES.get(eb) == ec and GENERATES.get(ec) == ea:
                        bridge_member = mc.name
                        bridge_element = ec
                        bridge_path = f"{eb} → {ec} → {ea}"
                        break

            out.append(
                BridgeRelation(
                    pair_a=ma.name,
                    pair_b=mb.name,
                    element_a=ea,
                    element_b=eb,
                    clash_type=clash_type,
                    bridge_member=bridge_member,
                    bridge_element=bridge_element,
                    bridge_path=bridge_path,
                )
            )
    return out


# -----------------------------------------------------------------------------
# Top-level family resonance composition.
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class FamilyResonance:
    """Combined output of all 4 methods for one household."""
    members: tuple[FamilyMember, ...]
    self_natal: dict | None             # NatalHexagram of "self" member, if present
    marriage_hexagram: dict | None      # NatalHexagram of wedding moment, if given
    thai_tue_overlay: tuple[BranchInteraction, ...]  # Method 2
    unified_household: dict             # Method 3
    bridges: tuple[BridgeRelation, ...]  # Method 4

    def to_dict(self) -> dict:
        return {
            "members": [m.to_dict() for m in self.members],
            "self_natal": self.self_natal,
            "marriage_hexagram": self.marriage_hexagram,
            "thai_tue_overlay": [i.to_dict() for i in self.thai_tue_overlay],
            "unified_household": self.unified_household,
            "bridges": [b.to_dict() for b in self.bridges],
        }


def compute_family_resonance(
    members: list[FamilyMember],
    wedding_datetime_local: str | None = None,
    wedding_timezone: str = "Asia/Ho_Chi_Minh",
) -> FamilyResonance:
    """Top-level: run all 4 methods given a list of family members + optional wedding."""
    self_member = next((m for m in members if m.role == "self"), None)
    self_natal = None
    if self_member and self_member.birth_datetime_local:
        natal = compute_natal_hexagram(self_member.birth_datetime_local, self_member.timezone)
        self_natal = natal.to_dict()
        thai_tue = compute_thai_tue_overlay(natal, members)
    else:
        thai_tue = ()

    marriage_dict = None
    if wedding_datetime_local:
        marriage_natal = compute_marriage_hexagram(wedding_datetime_local, wedding_timezone)
        marriage_dict = marriage_natal.to_dict()

    unified = compute_unified_household_hexagram(members)
    bridges = analyze_element_bridging(members)

    return FamilyResonance(
        members=tuple(members),
        self_natal=self_natal,
        marriage_hexagram=marriage_dict,
        thai_tue_overlay=tuple(thai_tue),
        unified_household=unified.to_dict(),
        bridges=tuple(bridges),
    )
