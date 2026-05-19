from __future__ import annotations

import pytest

from engine.family_system import (
    FamilyMember,
    ROLE_TO_LUC_THAN,
    ROLE_VI,
    YEAR_BRANCH_BY_INDEX,
    _interaction_between_branches,
    analyze_element_bridging,
    compute_family_resonance,
    compute_marriage_hexagram,
    compute_thai_tue_overlay,
    compute_unified_household_hexagram,
    year_branch_for,
    year_branch_idx_for,
)
from engine.personal_quai import compute_natal_hexagram


@pytest.fixture
def basic_family():
    return [
        FamilyMember(role="self", name="Anh", birth_year=1985,
                     birth_datetime_local="1985-07-20T03:30:00"),
        FamilyMember(role="spouse", name="Vợ", birth_year=1990,
                     birth_datetime_local="1990-03-15T10:00:00"),
        FamilyMember(role="child", name="Con", birth_year=2018,
                     birth_datetime_local="2018-06-10T14:00:00"),
    ]


def test_year_branch_anchors():
    assert year_branch_for(1984) == "Tý"
    assert year_branch_for(1985) == "Sửu"
    assert year_branch_for(1996) == "Tý"  # 1984 + 12.
    assert year_branch_idx_for(1984) == 1
    assert year_branch_idx_for(1985) == 2


def test_role_to_luc_than_mappings_complete():
    expected_roles = {"self", "spouse", "child", "parent", "sibling", "boss"}
    assert set(ROLE_TO_LUC_THAN.keys()) == expected_roles
    assert all(r in ROLE_VI for r in expected_roles)


def test_year_branch_by_index_is_canonical():
    assert YEAR_BRANCH_BY_INDEX == (
        "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
        "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
    )


class TestBranchInteraction:
    def test_same_branch_is_dong_chi(self):
        kind, score, _ = _interaction_between_branches("Tý", "Tý")
        assert kind == "đồng chi"
        assert score == 8

    def test_clash_negative(self):
        kind, score, _ = _interaction_between_branches("Tý", "Ngọ")
        assert kind == "xung"
        assert score == -25

    def test_six_harmony_positive(self):
        kind, score, _ = _interaction_between_branches("Tý", "Sửu")
        assert kind == "lục hợp"
        assert score == 18

    def test_three_harmony_positive(self):
        kind, score, _ = _interaction_between_branches("Thân", "Tý")
        assert kind == "tam hợp"
        assert score == 12

    def test_neutral_score_zero(self):
        kind, score, _ = _interaction_between_branches("Tý", "Dần")
        assert kind == "trung tính"
        assert score == 0


class TestMarriageHexagram:
    def test_returns_natal_hexagram_of_wedding_moment(self):
        nh = compute_marriage_hexagram("2017-10-21T10:00:00", "Asia/Ho_Chi_Minh")
        assert nh.method_id == "mai_hoa_nntt_v1"
        assert nh.primary_name
        assert 1 <= nh.primary_king_wen <= 64

    def test_determinism(self):
        a = compute_marriage_hexagram("2017-10-21T10:00:00", "Asia/Ho_Chi_Minh")
        b = compute_marriage_hexagram("2017-10-21T10:00:00", "Asia/Ho_Chi_Minh")
        assert a.primary_binary == b.primary_binary


class TestThaiTueOverlay:
    def test_self_member_excluded_from_overlay(self, basic_family):
        natal = compute_natal_hexagram(basic_family[0].birth_datetime_local, "Asia/Ho_Chi_Minh")
        overlay = compute_thai_tue_overlay(natal, basic_family)
        assert all(item.member_role != "self" for item in overlay)

    def test_each_remaining_member_appears_once(self, basic_family):
        natal = compute_natal_hexagram(basic_family[0].birth_datetime_local, "Asia/Ho_Chi_Minh")
        overlay = compute_thai_tue_overlay(natal, basic_family)
        names = [item.member_name for item in overlay]
        assert names == ["Vợ", "Con"]

    def test_score_in_known_range(self, basic_family):
        natal = compute_natal_hexagram(basic_family[0].birth_datetime_local, "Asia/Ho_Chi_Minh")
        overlay = compute_thai_tue_overlay(natal, basic_family)
        for item in overlay:
            assert -25 <= item.score <= 18


class TestUnifiedHousehold:
    def test_basic_fields(self, basic_family):
        h = compute_unified_household_hexagram(basic_family)
        assert 1 <= h.upper_num <= 8
        assert 1 <= h.lower_num <= 8
        assert 1 <= h.moving_line <= 6
        assert len(h.primary_binary) == 6
        assert h.primary_name
        assert 1 <= h.primary_king_wen <= 64

    def test_member_signatures_count_matches(self, basic_family):
        h = compute_unified_household_hexagram(basic_family)
        assert len(h.member_signatures) == len(basic_family)

    def test_full_sum_includes_children(self, basic_family):
        h = compute_unified_household_hexagram(basic_family)
        assert h.sum_full > h.sum_excluding_children

    def test_no_member_raises(self):
        with pytest.raises(ValueError):
            compute_unified_household_hexagram([])

    def test_works_with_year_only_members(self):
        members = [
            FamilyMember(role="self", name="A", birth_year=1985),
            FamilyMember(role="spouse", name="B", birth_year=1990),
        ]
        h = compute_unified_household_hexagram(members)
        assert h.primary_name

    def test_full_5_derived_present(self, basic_family):
        h = compute_unified_household_hexagram(basic_family)
        assert set(h.derived_hexagrams.keys()) == {
            "chanh", "ho", "bien", "giao", "phuc", "bao"
        }

    def test_determinism(self, basic_family):
        a = compute_unified_household_hexagram(basic_family)
        b = compute_unified_household_hexagram(basic_family)
        assert a.to_dict() == b.to_dict()


class TestElementBridging:
    def test_pairs_count_correct(self, basic_family):
        # n=3 → C(3,2) = 3 pairs.
        bridges = analyze_element_bridging(basic_family)
        assert len(bridges) == 3

    def test_bridge_found_when_clash_with_intermediate_element(self):
        # Husband Kim, wife Mộc (Kim khắc Mộc). Add child Thủy → Kim sinh Thủy sinh Mộc.
        # Use year-only fallback to control elements via branch-element table.
        # Branch element: Thân/Dậu = kim, Dần/Mão = mộc, Tý/Hợi = thủy.
        members = [
            FamilyMember(role="self", name="Kim", birth_year=1980),    # Thân = kim
            FamilyMember(role="spouse", name="Moc", birth_year=1986),  # Dần = mộc
            FamilyMember(role="child", name="Thuy", birth_year=1996),  # Tý = thủy
        ]
        bridges = analyze_element_bridging(members)
        clash_pair = next(b for b in bridges if b.clash_type == "khắc"
                          and b.pair_a in ("Kim", "Moc") and b.pair_b in ("Kim", "Moc"))
        assert clash_pair.bridge_member == "Thuy"
        assert clash_pair.bridge_element == "thủy"

    def test_no_bridge_returns_none(self):
        # 2 members khắc, no third → no bridge possible.
        members = [
            FamilyMember(role="self", name="Kim", birth_year=1980),
            FamilyMember(role="spouse", name="Moc", birth_year=1986),
        ]
        bridges = analyze_element_bridging(members)
        for b in bridges:
            if b.clash_type == "khắc":
                assert b.bridge_member is None


class TestComputeFamilyResonance:
    def test_returns_all_4_methods(self, basic_family):
        r = compute_family_resonance(basic_family,
                                     wedding_datetime_local="2017-10-21T10:00:00")
        assert r.self_natal is not None
        assert r.marriage_hexagram is not None
        assert len(r.thai_tue_overlay) == 2  # spouse + child (excludes self)
        assert r.unified_household is not None
        assert len(r.bridges) == 3

    def test_no_wedding_returns_none_marriage(self, basic_family):
        r = compute_family_resonance(basic_family)
        assert r.marriage_hexagram is None

    def test_no_self_member_skips_natal_overlay(self):
        members = [
            FamilyMember(role="spouse", name="A", birth_year=1990),
            FamilyMember(role="child", name="B", birth_year=2018),
        ]
        r = compute_family_resonance(members)
        assert r.self_natal is None
        assert r.thai_tue_overlay == ()
        # Unified math still works.
        assert r.unified_household is not None

    def test_serializable(self, basic_family):
        import json
        r = compute_family_resonance(basic_family,
                                     wedding_datetime_local="2017-10-21T10:00:00")
        payload = json.dumps(r.to_dict(), ensure_ascii=False)
        restored = json.loads(payload)
        assert "members" in restored
        assert "unified_household" in restored
