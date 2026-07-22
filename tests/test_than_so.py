"""Tests for engine.than_so — Pythagoras (Decoz P0)."""
from __future__ import annotations

import pytest

from engine.than_so import (
    cast_than_so,
    compute_core,
    compute_extended,
    cross_bind_dong_phuong,
    life_path,
    normalize_vietnamese,
    personal_day,
    personal_month,
    personal_year,
    pinnacles_and_challenges,
    reduce_number,
)
from engine.than_so.core_numbers import reduce_with_trace
from engine.than_so.cycles import period_cycles
from engine.than_so.name_parts import split_name_parts


# ─── Reduce + master ──────────────────────────────────────────────────────────


def test_reduce_basic():
    assert reduce_number(28) == 1
    assert reduce_number(17) == 8


def test_reduce_keeps_master():
    assert reduce_number(11) == 11
    assert reduce_number(29) == 11
    assert reduce_number(33) == 33


def test_reduce_no_master_when_disabled():
    assert reduce_number(11, keep_master=False) == 2


# ─── Vietnamese normalize ─────────────────────────────────────────────────────


def test_normalize_strips_diacritics_and_d():
    assert normalize_vietnamese("Nguyễn Văn An") == "NGUYEN VAN AN"
    assert normalize_vietnamese("Đỗ Thị Hương") == "DO THI HUONG"


def test_normalize_no_consonant_cluster_split():
    assert normalize_vietnamese("Nguyễn").replace(" ", "") == "NGUYEN"


# ─── Decoz golden Life Path fixtures ─────────────────────────────────────────


def test_life_path_journal_example():
    lp = life_path(23, 11, 1990)
    assert lp["value"] == 8
    assert lp["components"]["month"] == 11


def test_life_path_decoz_aug_12_1990():
    # Decoz: 8 + 3 + 1 = 12 → 3
    lp = life_path(12, 8, 1990)
    assert lp["value"] == 3


def test_life_path_decoz_nov_22_1983():
    # 11 + 22 + 3 = 36 → 9
    lp = life_path(22, 11, 1983)
    assert lp["value"] == 9
    assert lp["components"]["month"] == 11
    assert lp["components"]["day"] == 22


def test_life_path_karmic_16_oct_15_1998():
    # Method A: 1 + 6 + 9 = 16 → 7 (shortcut 34 would hide 16)
    lp = life_path(15, 10, 1998)
    assert lp["value"] == 7
    assert lp["karmic_debt"] == 16


# ─── Name numbers ─────────────────────────────────────────────────────────────


def test_expression_john_pythagorean():
    core = compute_core("John", 1, 1, 2000, system="pythagorean", name_order="western")
    assert core["expression"]["value"] == 2


def test_soul_and_personality_split():
    core = compute_core("John", 1, 1, 2000, system="pythagorean", name_order="western")
    assert core["soul_urge"]["value"] == 6
    assert core["personality"]["value"] == 5


def test_expression_per_name_part_has_parts():
    core = compute_core("Nguyễn Văn An", 1, 1, 2000, name_order="vn")
    assert len(core["expression"]["parts"]) == 3
    assert core["name_parts"]["first_name"] == "AN"
    assert core["name_parts"]["last_name"] == "NGUYEN"


def test_name_order_vn_vs_western():
    vn = split_name_parts("Nguyễn Văn An", "vn")
    western = split_name_parts("An Van Nguyen", "western")
    assert vn["first_name"] == "AN"
    assert western["first_name"] == "AN"
    assert vn["last_name"] == "NGUYEN"


def test_chaldean_system_still_works():
    ch = compute_core("John", 1, 1, 2000, system="chaldean", name_order="western")
    assert 1 <= ch["expression"]["value"] <= 33


# ─── Karmic + Challenges ──────────────────────────────────────────────────────


def test_karmic_debt_trace():
    t = reduce_with_trace(13)
    assert t["reduced"] == 4
    assert t["karmic_debt"] == 13


def test_pinnacles_formula():
    pc = pinnacles_and_challenges(23, 11, 1990)
    m, d, y = 11, 5, 1
    p = [x["value"] for x in pc["pinnacles"]]
    assert p[0] == reduce_number(m + d)
    assert p[1] == reduce_number(d + y)
    assert p[3] == reduce_number(m + y)
    assert pc["challenges"][2]["main"] is True


def test_challenges_reduce_master_before_subtract():
    # Month 11 → challenge unit 2 (not 11)
    pc = pinnacles_and_challenges(23, 11, 1990)
    # c1 = |2 - 5| = 3
    assert pc["challenges"][0]["value"] == 3


def test_period_cycle_second_is_27_years():
    periods = period_cycles(23, 11, 1990)
    assert periods[1]["duration_years"] == 27
    # LP 8 → p1_end = 36-8 = 28; p2_end = 28+27 = 55
    assert periods[0]["age_end"] == 28
    assert periods[1]["age_end"] == 55


# ─── Extended ─────────────────────────────────────────────────────────────────


def test_extended_attitude_and_lessons():
    core = compute_core("Nguyễn Văn An", 23, 11, 1990)
    ext = compute_extended("Nguyễn Văn An", 23, 11, core, name_order="vn")
    # Attitude: month 11 + day 5 = 16 → 7
    assert ext["attitude"]["value"] == 7
    assert "values" in ext["karmic_lessons"]
    assert "life_path_expression" in ext["bridges"]
    assert "physical" in ext["planes_of_expression"]["planes"]


def test_extended_minor_from_current_name():
    core = compute_core("Nguyễn Văn An", 23, 11, 1990)
    ext = compute_extended(
        "Nguyễn Văn An", 23, 11, core, current_name="An", name_order="vn"
    )
    assert ext["minor"] is not None
    assert ext["minor"]["expression"]["value"] >= 1


def test_personal_month_day():
    py = personal_year(15, 5, 2026)
    assert py["value"] == 3  # Decoz: 5+6+1? 5+15→6 + 2026→10→1 = 5+6+1=12→3
    pm = personal_month(15, 5, 2026, 2)
    assert 1 <= pm["value"] <= 9
    pd = personal_day(15, 5, 2026, 2, 3)
    assert 1 <= pd["value"] <= 9


# ─── Cast E2E ─────────────────────────────────────────────────────────────────


def test_cast_full_chart_p0():
    res = cast_than_so("Nguyễn Văn An", "1990-11-23", target_year=2026, current_name="An")
    assert res["schema_version"] == "v2"
    assert res["core"]["life_path"]["value"] == 8
    assert "extended" in res
    assert res["extended"]["attitude"]["value"] == 7
    assert "personal_month" in res["cycles"]
    assert "personal_day" in res["cycles"]
    assert "essence" in res["cycles"]
    assert "transits" in res["cycles"]
    assert len(res["cycles"]["personal_calendar"]) == 24
    assert len(res["cycles"]["transit_timeline"]) == 9
    assert len(res["cycles"]["personal_year_calendar"]) == 9
    assert len(res["cycles"]["personal_day_window"]) == 21
    assert "deep_reading" in res
    assert res["deep_reading"]["core"]["life_path"]["read"]
    assert res["deep_reading"]["core"]["life_path"]["gap"]
    assert res["deep_reading"]["core"]["life_path"]["improve"]
    assert res["deep_reading"]["cycles"].get("pinnacles")
    assert res["deep_reading"]["cycles"].get("challenges")
    assert "method_audit" in res
    assert res["method_audit"]["decoz_method_a"]["value"] == 8
    assert res["extended"]["first_vowel"]["letter"]
    assert res["cross_reference"]["system"] == "chaldean"
    assert "dong_phuong_doi_chieu" not in res  # default off
    assert "predict" not in res["reading"]["paradigm_note"].lower()


def test_obama_life_path_western():
    res = cast_than_so(
        "Barack Hussein Obama",
        "1961-08-04",
        name_order="western",
        include_chaldean=False,
    )
    assert res["core"]["life_path"]["value"] == 2
    assert res["core"]["expression"]["value"] == 1


def test_method_audit_karmic_oct_15_1998():
    from engine.than_so.method_audit import method_audit

    audit = method_audit(15, 10, 1998)
    assert audit["decoz_method_a"]["value"] == 7
    assert audit["decoz_method_a"]["karmic_debt"] == 16
    assert audit["karmic_hidden_by_shortcut"] is True


def test_expression_audit_mary_ann_smith_diverges():
    """Flat full-name sum can diverge from Decoz per-part (Mary Ann Smith: 2 vs 11)."""
    from engine.than_so.method_audit import expression_name_audit

    audit = expression_name_audit("Mary Ann Smith", name_order="western")
    assert audit["decoz_per_part"]["value"] == 2
    assert audit["flat_full_name_shortcut"]["value"] == 11
    assert audit["diverged"] is True
    assert any(p["part"] == "ANN" and p["reduced"] == 11 for p in audit["decoz_per_part"]["parts"])


def test_cast_includes_expression_audit():
    res = cast_than_so("Mary Ann Smith", "1980-01-01", name_order="western", include_chaldean=False)
    assert "expression" in res["method_audit"]
    assert res["method_audit"]["expression"]["diverged"] is True
    assert res["core"]["expression"]["value"] == 2


def test_generate_pdf_bytes():
    from engine.than_so.report_pdf import generate_than_so_pdf

    pdf = generate_than_so_pdf("Nguyễn Văn An", "1990-11-23", current_name="An", target_year=2026)
    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 1000

def test_cast_dong_phuong_opt_in():
    res = cast_than_so("Nguyễn Văn An", "1990-11-23", include_dong_phuong=True)
    assert "dong_phuong_doi_chieu" in res


def test_cast_rejects_bad_date():
    with pytest.raises(ValueError):
        cast_than_so("Test", "23-11-1990")


def test_cast_rejects_empty_name():
    with pytest.raises(ValueError):
        cast_than_so("  ", "1990-11-23")


# ─── Cross-bind (opt-in, kept for regression) ─────────────────────────────────


def test_cross_bind_number_3_strong_consensus():
    cb = cross_bind_dong_phuong(3)
    assert "Mộc" in cb["consensus_ngu_hanh"]


def test_cross_bind_number_9_divergence_not_forced():
    cb = cross_bind_dong_phuong(9)
    assert cb["divergence"] is True


# ─── Compatibility (v10) ───────────────────────────────────────────────────────


def test_lookup_pair_4_9_is_low():
    from engine.than_so.compatibility import lookup_pair

    pair = lookup_pair(4, 9)
    assert pair["score"] == "low"
    assert pair["points"] == 1


def test_lookup_pair_master_11_maps_to_2():
    from engine.than_so.compatibility import lookup_pair, root_digit

    assert root_digit(11) == 2
    # 11×6 → same as 2×6 → high
    assert lookup_pair(11, 6)["score"] == "high"


def test_analyze_compatibility_structure():
    from engine.than_so.compatibility import analyze_compatibility

    report = analyze_compatibility(
        "Nguyễn Văn An",
        "1990-11-23",
        "Trần Thị Bình",
        "1992-04-15",
        relationship_type="partner",
        target_year=2026,
    )
    assert report["schema_version"] == "v2-compat"
    assert "predict" not in report["paradigm_note"].lower()
    assert len(report["aspects"]) == 4
    assert 0 <= report["overall"]["percent"] <= 100
    assert report["composite_life_path"]["value"]
    assert report["person_a"]["core"]["life_path"]["value"]
    assert report["person_b"]["core"]["life_path"]["value"]


def test_compatibility_pdf_bytes():
    from engine.than_so.compatibility import analyze_compatibility
    from engine.than_so.report_pdf import generate_compatibility_pdf

    report = analyze_compatibility(
        "Nguyễn Văn An",
        "1990-11-23",
        "Mary Ann Smith",
        "1980-01-01",
        name_order_b="western",
    )
    pdf = generate_compatibility_pdf(report)
    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 800


# ─── Library Balliett / Campbell / Cheiro (v11) ───────────────────────────────


def test_cheiro_compound_33_aliases_to_24():
    from engine.than_so.library import resolve_compound

    r = resolve_compound(33)
    assert r is not None
    assert r["resolved"] == 24


def test_cheiro_compound_37_has_own_potency():
    from engine.than_so.library import resolve_compound

    r = resolve_compound(37)
    assert r["resolved"] == 37
    assert "hợp tác" in r["meaning_vi"].lower() or "tình" in r["meaning_vi"].lower()


def test_cheiro_compound_51_and_52():
    from engine.than_so.library import resolve_compound

    assert resolve_compound(51)["resolved"] == 51
    assert resolve_compound(52)["resolved"] == 43


def test_inclusion_table_campbell():
    from engine.than_so.extended import inclusion_table, karmic_lessons, hidden_passion

    table = inclusion_table("Nguyễn Văn An")
    assert table["provenance"] == "campbell-your-days-are-numbered"
    assert "1" in table["frequency"]
    assert sum(table["frequency"].values()) == table["letter_count"]
    assert set(table["missing"]) <= set(range(1, 10))
    assert table["average"] == round(table["letter_count"] / 9, 3)
    assert table["missing"] == karmic_lessons("Nguyễn Văn An")["values"]
    assert table["dominant"] == hidden_passion("Nguyễn Văn An")["values"]
    assert 5 in table["above_average"]  # N/E heavy


def test_inclusion_passion_tie_and_empty():
    from engine.than_so.extended import inclusion_table, hidden_passion

    john = inclusion_table("John")
    assert len(john["dominant"]) == 4  # 1,5,6,8 each once
    assert john["dominant"] == hidden_passion("John")["values"]
    empty = inclusion_table("")
    assert empty["missing"] == list(range(1, 10))
    assert empty["dominant"] == []
    assert empty["average"] == 0.0


def test_series_affinity_includes_3_6_9():
    from engine.than_so.deep_reading import _name_birth_harmony

    h = _name_birth_harmony(3, 6)
    assert h["band"] == "series_affinity"
    assert h["series_birth"] == "3-6-9"


def test_compatibility_surfaces_cheiro_series_note():
    from engine.than_so.compatibility import lookup_pair

    pair = lookup_pair(1, 4)
    assert pair["score"] == "low"
    assert "cheiro_vi" in pair
    assert "1–4" in pair["cheiro_vi"] or "1-4" in pair["cheiro_vi"]


def test_number_meanings_m1_keeps_decoz_marks_conflict():
    import json
    from pathlib import Path

    data = json.loads(
        (Path("data/than_so/master/number_meanings.json")).read_text(encoding="utf-8")
    )
    assert data["audit_m1"]["cheiro_birth_conflicts"] == [3, 4, 9]
    assert "cheiro_birth_note" in data["numbers"]["3"]
    assert data["numbers"]["3"]["archetype_vi"].startswith("Người Sáng Tạo")


def test_cast_chaldean_xref_has_compound():
    res = cast_than_so("Nguyễn Văn An", "1990-11-23", include_chaldean=True)
    xref = res["cross_reference"]
    assert xref["system"] == "chaldean"
    assert "name_compound_flat" in xref
    assert xref["name_compound_flat"]["raw"] >= 1
    assert res["extended"]["inclusion_table"]["name_vi"]
    assert "balliett" in xref
    assert "balliett" in res
    assert res["balliett"]["birth_digit"]["birth_digit"] >= 1


# ─── Balliett B1/B2 tone-color ─────────────────────────────────────────────────


def test_resolve_balliett_tone_and_henry_elder_birth():
    from engine.than_so.library import resolve_balliett_tone, balliett_birth_digit

    t9 = resolve_balliett_tone(9)
    assert t9["colors"] == ["red"]
    assert "D" in t9["tones"]
    assert t9.get("present_both") is True  # Cheiro conflict note
    assert resolve_balliett_tone(11)["tones"] == ["full_octave_C"]
    assert resolve_balliett_tone(33) is None

    # Henry Elder: 1872-01-17 → 1+8+9 → 18 → 9
    he = balliett_birth_digit(1, 17, 1872)
    assert he["components"] == {"month": 1, "day_digit": 8, "year_digit": 9}
    assert he["birth_digit"] == 9

    # Wanamaker: 1838-07-11 → birth numbers 9, 11
    w = balliett_birth_digit(7, 11, 1838)
    assert w["wanamaker_mode"] is True
    assert w["birth_numbers"] == [9, 11]


def test_deep_reading_has_balliett_tone_layer():
    res = cast_than_so("Nguyễn Văn An", "1990-11-23", include_chaldean=False)
    layer = res["deep_reading"]["layers"]["balliett_tone"]
    assert "birth_digit" in layer
    assert "không" in layer["improve"].lower() or "không" in layer["read"]
    assert any("lucky" in f or "color" in f for f in layer["forbid"])
    assert res["balliett"]["expression_tone"]["value"] >= 1


def test_balliett_life_song_and_spiritual_birthday():
    from engine.than_so.library import (
        balliett_life_song,
        balliett_spiritual_birthday_days,
    )

    # OCR example: born day 1 → 1,10,19,28
    sb = balliett_spiritual_birthday_days(1)
    assert sb["days_in_month"] == [1, 10, 19, 28]
    assert "may" not in sb["yi_reframe"].lower() or "KHÔNG" in sb["yi_reframe"]

    # March 1, 1883 → birth digit 6, keynote A
    song = balliett_life_song(3, 1, 1883, expression_value=5)
    assert song["birth_digit"] == 6
    assert song["keynote"] == "A"
    assert song["chart_status"] == "missing_ocr"
    assert "1" in str(song["spiritual_birthday"]["days_in_month"])

    res = cast_than_so("Test User", "1883-03-01", include_chaldean=False)
    assert res["balliett"]["life_song"]["keynote"] == "A"
    layer = res["deep_reading"]["layers"]["balliett_tone"]
    assert "spiritual_birthday" in layer
    assert layer["life_song"]["chart_status"] == "missing_ocr"


def test_balliett_principle_in_v2():
    from engine.than_so.deep_reading import _principles

    ids = {p["id"] for p in _principles()["principles"]}
    assert "balliett_tone_color" in ids
    assert "balliett_life_song" in ids
    assert "balliett_spiritual_birthday" in ids


# ─── Deep principles from library (v12) ────────────────────────────────────────


def test_deep_reading_has_name_birth_harmony_and_cheiro_layers():
    res = cast_than_so("Nguyễn Văn An", "1990-11-23", include_chaldean=False)
    deep = res["deep_reading"]
    assert "layers" in deep
    assert "name_birth_harmony" in deep["layers"]
    assert deep["layers"]["name_birth_harmony"]["band"] in ("aligned", "series_affinity", "offset")
    assert "cheiro_birth_layers" in deep["layers"]
    assert deep["layers"]["cheiro_birth_layers"]["day"]["raw"] == 23
    assert "synthesis" in deep
    assert "đổi tên" not in deep["synthesis"]["improve"].lower() or "KHÔNG" in deep["synthesis"]["read"]
    assert "predict" not in deep["disclaimer"].lower()


def test_name_birth_harmony_offset_does_not_advise_rename():
    from engine.than_so.deep_reading import _name_birth_harmony

    h = _name_birth_harmony(1, 5)  # different roots, not same series
    assert h["band"] == "offset"
    assert "KHÔNG" in h["read"] and "đổi tên" in h["read"]
    assert "đổi tên để" not in h["improve"].lower()


def test_plain_summary_explains_karmic_debt_for_ordinary_reader():
    res = cast_than_so("Lại Minh Thắng", "1988-06-05", include_chaldean=False)
    ps = res["reading"]["plain_summary"]
    assert ps["title_vi"] == "Tóm tắt dễ hiểu"
    assert any("Bài học kèm 19" in b for b in ps["bullets"])
    assert any("Bài học kèm 13" in b for b in ps["bullets"])
    assert "kiếp trước" not in (ps.get("karmic_intro_vi") or "").lower() or "không phải án" in ps["karmic_intro_vi"].lower()

    debts = {d["number"]: d for d in res["reading"]["karmic_debts"]}
    assert 13 in debts and 19 in debts
    assert "plain_vi" in debts[13] and len(debts[13]["plain_vi"]) > 40
    assert "LAI" in debts[13]["where_vi"]
    assert debts[19]["where_vi"].startswith("Tổng trước khi rút gọn")
    assert "practice_vi" in debts[19] and "nhờ" in debts[19]["practice_vi"]

    # Deep reading carries karmic practice onto life path improve
    assert "nhờ" in res["deep_reading"]["core"]["life_path"]["improve"]
    assert res["deep_reading"]["core"]["life_path"].get("karmic", {}).get("number") == 19


def test_interpretation_principles_loaded():
    from engine.than_so.deep_reading import _principles

    p = _principles()
    assert p.get("schema_version") == "v2"
    ids = {x["id"] for x in p["principles"]}
    assert "birth_day_key" in ids
    assert "name_birth_harmony" in ids
    assert "concentration" in ids
    assert "cheiro_decoz_dual_lens" in ids
    assert "betting_refusal" in ids
    assert "medical_boundary" in ids
    forbid = p.get("forbid_user_facing") or []
    assert any("xổ số" in x or "đua ngựa" in x for x in forbid)


def test_cheiro_birth_numbers_dual_lens_on_birthday():
    from engine.than_so.library import resolve_cheiro_birth

    c3 = resolve_cheiro_birth(3)
    assert c3 is not None
    assert c3["conflict_with_decoz"] is True
    assert c3["planet"] == "Jupiter"

    # Day 12 → Birthday digit 3 (conflict digit) — dual lens in deep_reading
    res = cast_than_so("Nguyễn Văn An", "1990-03-12", include_chaldean=False)
    bday = res["deep_reading"]["core"]["birthday"]
    assert "cheiro_birth" in bday
    assert bday["cheiro_birth"]["planet"] == "Jupiter"
    assert "decoz_lens" in bday
    assert "BOTH" in bday["read"] or "Cheiro" in bday["read"]
    day_layer = res["deep_reading"]["layers"]["cheiro_birth_layers"]["day"]
    assert "cheiro" in day_layer
    assert day_layer["cheiro"]["conflict_with_decoz"] is True


def test_cheiro_birth_non_conflict_uses_cheiro_archetype():
    # Day 5 → digit 5 — Mercury, typically non-conflict in our table
    from engine.than_so.library import resolve_cheiro_birth

    c5 = resolve_cheiro_birth(5)
    assert c5["conflict_with_decoz"] is False
    res = cast_than_so("Test User", "1988-06-05", include_chaldean=False)
    bday = res["deep_reading"]["core"]["birthday"]
    assert bday["cheiro_birth"]["planet"] == "Mercury"
    assert "Mercury" in bday["read"] or "Thủy" in bday["read"] or "mercur" in bday["read"].lower() or "đa năng" in bday["read"].lower()


def test_disclaimer_forbids_betting_and_medical():
    res = cast_than_so("Nguyễn Văn An", "1990-11-23", include_chaldean=False)
    d = res["deep_reading"]["disclaimer"].lower()
    assert "cá cược" in d or "xổ số" in d
    assert "y tế" in d or "chẩn bệnh" in d


def test_than_so_master_dir_falls_back_when_volume_stale(tmp_path):
    """VPS volume may have partial data/than_so/master — prefer embedded_data."""
    import shutil
    from pathlib import Path

    from engine.than_so import paths

    root = Path(__file__).resolve().parents[1]
    src = root / "data" / "than_so" / "master"
    primary = tmp_path / "data" / "than_so" / "master"
    embedded = tmp_path / "embedded_data" / "than_so" / "master"
    primary.mkdir(parents=True)
    embedded.mkdir(parents=True)
    # Stale primary: only a couple of older files
    for name in ("pythagorean_spec.json", "number_meanings.json"):
        shutil.copy(src / name, primary / name)
    for src_file in src.glob("*.json"):
        shutil.copy(src_file, embedded / src_file.name)

    paths.than_so_master_dir.cache_clear()
    old_root = paths._ROOT
    try:
        paths._ROOT = tmp_path
        resolved = paths.than_so_master_dir()
        assert resolved == embedded
        assert (resolved / "balliett_tone_color.json").is_file()
        assert (resolved / "cheiro_birth_numbers.json").is_file()
    finally:
        paths._ROOT = old_root
        paths.than_so_master_dir.cache_clear()


def test_package_init_does_not_eager_import_report_pdf():
    """Cast must work even if fpdf2 missing — report_pdf is lazy (#71 follow-up)."""
    import importlib
    import sys

    for key in list(sys.modules):
        if key.startswith("engine.than_so"):
            del sys.modules[key]
    import engine.than_so as ts

    assert "engine.than_so.report_pdf" not in sys.modules
    res = ts.cast_than_so("Nguyen Van A", "1988-06-05", include_chaldean=False)
    assert res["core"]["life_path"]["value"] >= 1
    assert "balliett" in res
    # Lazy attribute still resolvable when PDF deps present
    assert callable(ts.generate_than_so_pdf)
