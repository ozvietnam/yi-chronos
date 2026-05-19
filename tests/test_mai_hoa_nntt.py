"""Tests for Mai Hoa Niên-Nguyệt-Nhật-Thời derivation + 5 derived hexagrams."""

from __future__ import annotations

import pytest

from core.chronos import calculate_chronos_state
from core.yi64.derivations.derived_hexagrams import (
    compute_all_derived,
    compute_envelope,
    compute_nuclear,
    compute_opposing,
    compute_reversed,
    compute_transformed,
)
from core.yi64.derivations.mai_hoa_nntt import (
    EARTHLY_BRANCHES,
    METHOD_ID,
    TIEN_THIEN_TRIGRAMS,
    derivation_summary,
    derive_line_states,
)
from core.yi64.transforms import lines_to_binary, moving_lines_from_states


class TestDerivationFromKnownInputs:
    def test_basic_2026_05_10_noon(self):
        """Spot check with known chronos state."""
        state = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
        summary = derivation_summary(state)
        # Năm Bính Ngọ → branch Ngọ → idx 7.
        assert summary["year_branch_idx"] == 7
        # Lunar 24/03/2026.
        assert summary["lunar_day"] == 24
        assert summary["lunar_month"] == 3
        # Giờ Bính Ngọ (12:00 falls in Ngọ hour) → idx 7.
        assert summary["hour_branch_idx"] == 7
        # 7+3+24 = 34, mod 8 = 2 → Đoài.
        assert summary["upper_num"] == 2
        assert summary["upper_trigram"] == "Đoài"
        # +7 = 41, mod 8 = 1 → Càn; mod 6 = 5.
        assert summary["lower_num"] == 1
        assert summary["lower_trigram"] == "Càn"
        assert summary["moving_line"] == 5

    def test_line_states_correct_count_and_polarity(self):
        state = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
        line_states = derive_line_states(state)
        assert len(line_states) == 6
        positions = [ls.line_position for ls in line_states]
        assert positions == [1, 2, 3, 4, 5, 6]

    def test_exactly_one_moving_line(self):
        state = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
        line_states = derive_line_states(state)
        moving = moving_lines_from_states(line_states)
        assert len(moving) == 1
        assert moving[0] == 5  # As verified above.

    def test_determinism_same_input_same_output(self):
        s1 = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
        s2 = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
        b1 = lines_to_binary(derive_line_states(s1))
        b2 = lines_to_binary(derive_line_states(s2))
        assert b1 == b2


class TestModularArithmetic:
    def test_mod8_zero_returns_8(self):
        from core.yi64.derivations.mai_hoa_nntt import _mod8
        assert _mod8(8) == 8
        assert _mod8(16) == 8
        assert _mod8(0) == 8
        assert _mod8(7) == 7
        assert _mod8(1) == 1

    def test_mod6_zero_returns_6(self):
        from core.yi64.derivations.mai_hoa_nntt import _mod6
        assert _mod6(6) == 6
        assert _mod6(12) == 6
        assert _mod6(5) == 5

    def test_method_id_constant(self):
        assert METHOD_ID == "mai_hoa_nntt_v1"

    def test_tien_thien_order_is_canonical(self):
        assert TIEN_THIEN_TRIGRAMS == (
            "Càn", "Đoài", "Ly", "Chấn", "Tốn", "Khảm", "Cấn", "Khôn"
        )


class TestDerivedHexagrams:
    """The 5 derived charts: Hỗ, Biến, Giao, Phục, Bao."""

    def test_nuclear_of_qian_is_qian(self):
        # Càn (111111) → nuclear from middle 4 lines all yang → still Càn.
        assert compute_nuclear("111111") == "111111"

    def test_nuclear_of_kun_is_kun(self):
        assert compute_nuclear("000000") == "000000"

    def test_nuclear_of_quai_43_is_qian(self):
        # Quải = 011111 → nuclear = (1,1,1) + (1,1,1) = 111111 = Càn.
        assert compute_nuclear("011111") == "111111"

    def test_transformed_flips_moving_lines(self):
        # 111111 with moving line 1 (bottom) → 111110.
        assert compute_transformed("111111", (1,)) == "111110"
        # 111111 with moving lines 1, 2 → 111100.
        assert compute_transformed("111111", (1, 2)) == "111100"

    def test_transformed_no_moving_lines_unchanged(self):
        assert compute_transformed("011010", ()) == "011010"

    def test_opposing_flips_all_six_lines(self):
        assert compute_opposing("111111") == "000000"  # Càn → Khôn.
        assert compute_opposing("000000") == "111111"  # Khôn → Càn.
        assert compute_opposing("011111") == "100000"  # Quải → Bác.

    def test_reversed_inverts_line_order(self):
        # Reverse of "abcdef" is "fedcba".
        assert compute_reversed("011111") == "111110"  # Quải → Cấu.
        assert compute_reversed("111111") == "111111"  # Càn → Càn (palindrome).
        assert compute_reversed("000000") == "000000"  # Khôn → Khôn.

    def test_envelope_uses_only_top_and_bottom(self):
        # Top yang, bottom yang: 111111 → 111+111 = 111111 (Càn).
        assert compute_envelope("111111") == "111111"
        # Top yin, bottom yin: 000000 → 000000 (Khôn).
        assert compute_envelope("000000") == "000000"
        # Top yin, bottom yang: 0xxxxx1 → 000111 (Thái).
        assert compute_envelope("011111") == "000111"
        # Top yang, bottom yin: 1xxxxx0 → 111000 (Bĩ).
        assert compute_envelope("100000") == "111000"

    def test_compute_all_derived_returns_full_set(self):
        result = compute_all_derived("011111", moving_lines=(5,))
        assert set(result.keys()) == {"chanh", "ho", "bien", "giao", "phuc", "bao"}

    def test_compute_all_derived_chanh_is_primary(self):
        result = compute_all_derived("011111", moving_lines=(5,))
        assert result["chanh"].binary_code == "011111"
        assert result["chanh"].king_wen_index == 43  # Quải.

    def test_compute_all_derived_known_values_for_quai(self):
        """Known values for Quẻ Quải (43, binary 011111) with moving line 5."""
        result = compute_all_derived("011111", moving_lines=(5,))
        assert result["ho"].king_wen_index == 1   # Càn.
        assert result["bien"].king_wen_index == 34 # Đại Tráng (flip line 5: 001111).
        assert result["giao"].king_wen_index == 23 # Bác (100000).
        assert result["phuc"].king_wen_index == 44 # Cấu (111110).
        assert result["bao"].king_wen_index == 11  # Thái (000111).
