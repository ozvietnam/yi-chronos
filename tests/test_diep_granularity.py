from __future__ import annotations

import pytest

from core.yi64.derivations.diep_granularity import (
    DEFAULT_DIEP_COUNT,
    DEFAULT_DIEP_MINUTES,
    compute_diep_sequence_for_datetime,
)


def test_default_returns_5_diep_of_12_minutes():
    seq = compute_diep_sequence_for_datetime("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    assert seq.diep_count == DEFAULT_DIEP_COUNT == 5
    assert seq.diep_minutes == DEFAULT_DIEP_MINUTES == 12
    assert len(seq.entries) == 5


def test_diep_minute_intervals_cover_hour():
    seq = compute_diep_sequence_for_datetime("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    for i, entry in enumerate(seq.entries):
        assert entry.diep_index == i
        assert entry.minute_start == i * seq.diep_minutes
        assert entry.minute_end == min((i + 1) * seq.diep_minutes - 1, 59)


def test_diep_entries_have_distinct_quai():
    """Five diệp in same hour should produce different primary hexagrams (typical)."""
    seq = compute_diep_sequence_for_datetime("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    binaries = {e.primary_binary for e in seq.entries}
    # Most hours will produce 5 distinct quẻ; allow degenerate hours with only 4.
    assert len(binaries) >= 4


def test_each_entry_has_full_5_derived_hexagrams():
    seq = compute_diep_sequence_for_datetime("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    for entry in seq.entries:
        assert set(entry.derived_hexagrams.keys()) == {
            "chanh", "ho", "bien", "giao", "phuc", "bao"
        }


def test_moving_line_in_valid_range():
    seq = compute_diep_sequence_for_datetime("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    for entry in seq.entries:
        assert 1 <= entry.moving_line <= 6
        assert 1 <= entry.upper_num <= 8
        assert 1 <= entry.lower_num <= 8


def test_invalid_diep_count_rejected():
    with pytest.raises(ValueError):
        compute_diep_sequence_for_datetime(
            "2026-05-11T10:00:00", "Asia/Ho_Chi_Minh", diep_count=7
        )
    with pytest.raises(ValueError):
        compute_diep_sequence_for_datetime(
            "2026-05-11T10:00:00", "Asia/Ho_Chi_Minh", diep_count=0
        )
    with pytest.raises(ValueError):
        compute_diep_sequence_for_datetime(
            "2026-05-11T10:00:00", "Asia/Ho_Chi_Minh", diep_count=13
        )


def test_valid_diep_counts_accepted():
    for n in (1, 2, 3, 4, 5, 6, 10, 12):
        seq = compute_diep_sequence_for_datetime(
            "2026-05-11T10:00:00", "Asia/Ho_Chi_Minh", diep_count=n
        )
        assert seq.diep_count == n
        assert len(seq.entries) == n
        assert seq.diep_minutes == 60 // n


def test_determinism_same_input_same_sequence():
    a = compute_diep_sequence_for_datetime("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    b = compute_diep_sequence_for_datetime("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    assert a.to_dict() == b.to_dict()


def test_serializable():
    import json
    seq = compute_diep_sequence_for_datetime("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    payload = json.dumps(seq.to_dict())
    restored = json.loads(payload)
    assert restored["diep_count"] == 5
    assert len(restored["entries"]) == 5
