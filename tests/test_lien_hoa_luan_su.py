"""Tests for engine.lien_hoa.luan_su — interpretation layer.

Reference example: P=1 (Càn), T=8 (Khôn), question='test' → Tiên đề Bĩ.
Theo sách Liên Hoa Độn Pháp p.17-50.
"""

from __future__ import annotations

import pytest

from engine.lien_hoa import cast_lien_hoa, luan_su
from engine.lien_hoa.luan_su import (
    DomainReading,
    LuanSu,
    chanh_dang_of,
    chu_su_distribution,
    interpret_health,
    interpret_house,
    interpret_life_arc,
    interpret_marriage,
    interpret_travel_safety,
    interpret_wealth,
    menh_cung_lt_of,
)


# ---------- Fixtures ----------


@pytest.fixture
def spread_bi_nam() -> dict:
    """P=1 T=8 → Tiên đề Bĩ (Càn/Khôn), TA Nam. Hào động 3 → 1 đợt → 5 KTS."""
    return cast_lien_hoa(
        number_right_hand=1,
        number_left_hand=8,
        question_text="ví dụ sách trang 17",
        gender="nam",
    )


@pytest.fixture
def spread_3dot_nam() -> dict:
    """A spread with hào 2 or 5 → 3 đợt → 13 KTS. P=2 T=1 → hào 3, P=3 T=2 → hào 5."""
    return cast_lien_hoa(
        number_right_hand=3,
        number_left_hand=2,
        question_text="test 3 đợt",
        gender="nam",
    )


# ---------- Helpers ----------


def test_chu_su_distribution_counts_all_six_keys(spread_bi_nam):
    counts = chu_su_distribution(spread_bi_nam["khong_thoi"])
    assert set(counts.keys()) >= {"TA", "H", "P", "C", "Q", "T"}
    assert sum(counts.values()) == spread_bi_nam["khong_thoi_count"]


def test_menh_cung_lt_returns_string_tag(spread_bi_nam):
    tien_de = spread_bi_nam["khong_thoi"][0]
    tag = menh_cung_lt_of(tien_de)
    assert tag in {"TA", "H", "P", "C", "Q", "T"}


def test_chanh_dang_starts_with_TA(spread_bi_nam):
    tien_de = spread_bi_nam["khong_thoi"][0]
    dang = chanh_dang_of(tien_de)
    assert dang.startswith("TA/")
    assert dang.split("/")[1] in {"TA", "H", "P", "C", "Q", "T"}


# ---------- Per-domain interpreters ----------


def test_interpret_marriage_returns_DomainReading(spread_bi_nam):
    r = interpret_marriage(spread_bi_nam)
    assert isinstance(r, DomainReading)
    assert r.domain == "marriage"
    assert r.domain_vi == "Hôn nhân"
    assert r.verdict
    assert r.explanation
    assert isinstance(r.evidence, list)


def test_interpret_marriage_nam_T_cu_menh_is_hop_cach(spread_bi_nam):
    """P=1 T=8 → Tiên đề Bĩ, Mệnh cung = Thê Tài (T). TA Nam → hợp cách."""
    r = interpret_marriage(spread_bi_nam)
    assert "hợp cách" in r.verdict.lower() or "thành" in r.verdict.lower()


def test_interpret_marriage_nu_uses_Q_expected():
    """Nữ kỳ vọng Q cư Mệnh. P=1 T=8 Mệnh=T → bất thành cho Nữ."""
    spread = cast_lien_hoa(
        number_right_hand=1,
        number_left_hand=8,
        gender="nữ",
    )
    r = interpret_marriage(spread)
    # T cư mệnh nhưng kỳ vọng là Q → not "hợp cách"
    assert "hợp cách" not in r.verdict.lower()


def test_interpret_wealth_returns_DomainReading(spread_bi_nam):
    r = interpret_wealth(spread_bi_nam)
    assert r.domain == "wealth"
    assert r.verdict


def test_interpret_house_returns_DomainReading(spread_bi_nam):
    r = interpret_house(spread_bi_nam)
    assert r.domain == "house"
    # P=1 T=8 cho dạng TA/P → nhà mặt đường
    assert "mặt đường" in r.verdict.lower() or "ngõ" in r.verdict.lower() or "chưa rõ" in r.verdict.lower()


def test_interpret_health_returns_DomainReading(spread_bi_nam):
    r = interpret_health(spread_bi_nam)
    assert r.domain == "health"
    assert r.verdict


def test_interpret_life_arc_1_dot_is_stable(spread_bi_nam):
    """Hào 3 hoặc 6 → 1 đợt → ổn định."""
    assert spread_bi_nam["dot_count"] == 1
    r = interpret_life_arc(spread_bi_nam)
    assert r.domain == "life_arc"
    assert "ổn định" in r.verdict.lower() or "ít biến" in r.verdict.lower()


def test_interpret_life_arc_3_dot_is_thang_tram(spread_3dot_nam):
    """Hào 2 hoặc 5 → 3 đợt → thăng trầm."""
    assert spread_3dot_nam["dot_count"] == 3
    r = interpret_life_arc(spread_3dot_nam)
    assert "thăng trầm" in r.verdict.lower() or "nhiều" in r.verdict.lower()


def test_interpret_travel_safety_returns_DomainReading(spread_bi_nam):
    r = interpret_travel_safety(spread_bi_nam)
    assert r.domain == "travel"
    assert r.verdict


# ---------- Top-level luan_su ----------


def test_luan_su_returns_LuanSu(spread_bi_nam):
    result = luan_su(spread_bi_nam)
    assert isinstance(result, LuanSu)
    assert result.chu_su_counts
    assert result.menh_cung_lt in {"TA", "H", "P", "C", "Q", "T"}
    assert result.chanh_dang_tien_de.startswith("TA/")
    assert len(result.domain_readings) == 6
    assert result.composed_summary


def test_luan_su_to_dict_is_json_serializable(spread_bi_nam):
    import json

    result = luan_su(spread_bi_nam).to_dict()
    s = json.dumps(result, ensure_ascii=False)
    assert "composed_summary" in s
    assert "domain_readings" in s


def test_cast_lien_hoa_includes_luan_su_in_dict(spread_bi_nam):
    """cast_lien_hoa() output dict must have luan_su key (wired via cast.py)."""
    assert "luan_su" in spread_bi_nam
    luan = spread_bi_nam["luan_su"]
    assert "domain_readings" in luan
    assert "composed_summary" in luan
    assert "chu_su_counts" in luan
    assert "menh_cung_lt" in luan
    assert "chanh_dang_tien_de" in luan
    assert len(luan["domain_readings"]) == 6


def test_luan_su_domain_coverage(spread_bi_nam):
    """All 6 domains present."""
    result = luan_su(spread_bi_nam)
    domains = {r.domain for r in result.domain_readings}
    assert domains == {"life_arc", "wealth", "marriage", "house", "health", "travel"}


def test_luan_su_summary_contains_gender_and_quai(spread_bi_nam):
    result = luan_su(spread_bi_nam)
    assert "TA Nam" in result.composed_summary
    assert "Bĩ" in result.composed_summary or "TA/" in result.composed_summary
