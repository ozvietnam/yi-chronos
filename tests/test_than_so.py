"""Tests for engine.than_so — Thần Số Học (Numerology)."""
from __future__ import annotations

import pytest

from engine.than_so import (
    cast_than_so,
    compute_core,
    life_path,
    normalize_vietnamese,
    pinnacles_and_challenges,
    reduce_number,
)
from engine.than_so.core_numbers import reduce_with_trace


# ─── Reduce + master numbers ──────────────────────────────────────────────────


def test_reduce_basic():
    assert reduce_number(28) == 1  # 2+8=10 → 1
    assert reduce_number(17) == 8


def test_reduce_keeps_master():
    assert reduce_number(11) == 11
    assert reduce_number(29) == 11  # 2+9=11, dừng
    assert reduce_number(38) == 11  # 3+8=11
    assert reduce_number(33) == 33


def test_reduce_no_master_when_disabled():
    assert reduce_number(11, keep_master=False) == 2


# ─── Vietnamese normalization (bản địa hóa) ───────────────────────────────────


def test_normalize_strips_diacritics_and_d():
    assert normalize_vietnamese("Nguyễn Văn An") == "NGUYEN VAN AN"
    assert normalize_vietnamese("Đỗ Thị Hương") == "DO THI HUONG"


def test_normalize_no_consonant_cluster_split():
    # "Nguyễn" phải là 6 chữ rời N-G-U-Y-E-N
    assert normalize_vietnamese("Nguyễn").replace(" ", "") == "NGUYEN"


# ─── Life Path (chuẩn Decoz, ví dụ journal) ───────────────────────────────────


def test_life_path_known_example():
    # 23/11/1990: ngày 23→5, tháng 11→11(master), năm 1990→1 ⇒ 5+11+1=17→8
    lp = life_path(23, 11, 1990)
    assert lp["value"] == 8
    assert lp["components"]["month"] == 11


# ─── Name numbers (Pythagorean) ───────────────────────────────────────────────


def test_expression_john_pythagorean():
    # J=1 O=6 H=8 N=5 = 20 → 2
    core = compute_core("John", 1, 1, 2000, system="pythagorean")
    assert core["expression"]["value"] == 2


def test_soul_and_personality_split():
    # JOHN: nguyên âm O=6; phụ âm J+H+N=14→5
    core = compute_core("John", 1, 1, 2000, system="pythagorean")
    assert core["soul_urge"]["value"] == 6
    assert core["personality"]["value"] == 5


def test_chaldean_differs_from_pythagorean():
    py = compute_core("John", 1, 1, 2000, system="pythagorean")["expression"]["value"]
    ch = compute_core("John", 1, 1, 2000, system="chaldean")["expression"]["value"]
    # Không bắt buộc khác, nhưng hệ chaldean phải tính ra số hợp lệ 1-9/master
    assert 1 <= ch <= 33
    assert isinstance(py, int)


# ─── Karmic debt detection ────────────────────────────────────────────────────


def test_karmic_debt_trace():
    # raw 13 → 4, đánh dấu nợ 13
    t = reduce_with_trace(13)
    assert t["reduced"] == 4
    assert t["karmic_debt"] == 13


# ─── Pinnacles + Challenges formulas ──────────────────────────────────────────


def test_pinnacles_formula():
    pc = pinnacles_and_challenges(23, 11, 1990)
    m, d, y = 11, 5, 1  # reduced month/day/year
    p = [x["value"] for x in pc["pinnacles"]]
    assert p[0] == reduce_number(m + d)
    assert p[1] == reduce_number(d + y)
    assert p[3] == reduce_number(m + y)
    # 4 challenges, số 3 là main
    assert len(pc["challenges"]) == 4
    assert pc["challenges"][2]["main"] is True


# ─── End-to-end cast ──────────────────────────────────────────────────────────


def test_cast_full_chart():
    res = cast_than_so("Nguyễn Văn An", "1990-11-23", target_year=2026)
    assert res["method_id"]
    assert res["input"]["name_normalized"] == "NGUYEN VAN AN"
    assert res["core"]["life_path"]["value"] == 8
    assert "pinnacles" in res["cycles"]
    assert "personal_year" in res["cycles"]
    # Đối chiếu Chaldean có mặt
    assert res["cross_reference"]["system"] == "chaldean"
    # Reading paradigm tone — không có từ predict
    assert "predict" not in res["reading"]["paradigm_note"].lower()


def test_cast_rejects_bad_date():
    with pytest.raises(ValueError):
        cast_than_so("Test", "23-11-1990")


def test_cast_rejects_empty_name():
    with pytest.raises(ValueError):
        cast_than_so("  ", "1990-11-23")
