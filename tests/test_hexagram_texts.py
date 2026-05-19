import json
from pathlib import Path

from core.hexagram_texts import (
    explain_by_policy,
    get_auto_audit_report,
    get_hexagram_interpretation_v2,
    get_hexagram_text,
    get_source_coverage,
    get_source_matrix,
)


def test_seed_contains_core_hexagrams():
    kien = get_hexagram_text("Kiền")
    khon = get_hexagram_text("Khôn")
    assert kien is not None
    assert khon is not None
    assert kien.get("judgement_text")
    assert isinstance(kien.get("line_texts"), dict)


def test_policy_explanation_returns_summary():
    output = explain_by_policy(
        hexagram_name="Kiền",
        transformed_name="Khôn",
        moving_lines=[1],
        moving_line_policy="moving_line_texts",
    )
    assert output["policy"] == "moving_line_texts"
    assert "summary" in output
    assert output["source_book"]
    assert output["easy_vi_explanation"]
    assert isinstance(output["source_refs"], list)
    assert "interpretation_v2" in output


def test_interpretation_v2_seed_can_resolve_core_hexagram():
    record = get_hexagram_interpretation_v2(king_wen_index=1)
    assert record is not None
    assert record["name_vi"] == "Kiền"
    assert record["the_gian_su_vu"]


def test_interpretation_v2_seed_has_extended_range_to_32():
    record = get_hexagram_interpretation_v2(king_wen_index=32)
    assert record is not None
    assert record["name_vi"] == "Hằng"


def test_seed_has_full_six_lines_for_all_hexagrams():
    seed_path = Path("data/seeds/hexagram_texts_ngotatto.json")
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    records = data.get("records", [])
    assert len(records) == 64
    for rec in records:
        line_texts = rec.get("line_texts", {})
        assert all(str(i) in line_texts and line_texts[str(i)].strip() for i in range(1, 7))


def test_tam_thien_seed_has_full_64_hexagrams():
    seed_path = Path("data/seeds/hexagram_insights_tam_thien.json")
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    records = data.get("records", [])
    assert len(records) == 64
    names = {item.get("name_vi") for item in records}
    assert len(names) == 64


def test_source_coverage_reports_complete_tam_thien_overlay():
    coverage = get_source_coverage()
    assert coverage["main_count"] == 64
    assert coverage["tam_thien_count"] == 64
    assert coverage["coverage_ratio_tam_thien_vs_main"] == 1.0
    assert coverage["missing_in_tam_thien"] == []


def test_source_matrix_contains_full_64_and_full_coverage():
    matrix = get_source_matrix()
    rows = matrix["rows"]
    assert matrix["count"] == 64
    assert len(rows) == 64
    assert rows[0]["king_wen_index"] == 1
    assert rows[-1]["king_wen_index"] == 64
    assert all(row["in_main_source"] for row in rows)
    assert all(row["in_tam_thien_source"] for row in rows)


def test_auto_audit_report_is_ok_when_both_sources_are_full():
    report = get_auto_audit_report()
    assert report["status"] == "ok"
    assert report["summary"]["total_hexagrams"] == 64
    assert report["summary"]["main_count"] == 64
    assert report["summary"]["tam_thien_count"] == 64
    assert report["missing"]["main_source"] == []
    assert report["missing"]["tam_thien_source"] == []
