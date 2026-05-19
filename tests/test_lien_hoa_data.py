from core.lien_hoa_data import (
    get_lien_hoa_rule,
    list_lien_hoa_rules,
    load_lien_hoa_reading_queue,
    load_lien_hoa_rules,
    load_lien_hoa_source_index,
)


def test_lien_hoa_source_index_non_empty():
    payload = load_lien_hoa_source_index()
    assert len(payload.get("sources", [])) >= 5


def test_lien_hoa_rules_have_unique_ids():
    rules = load_lien_hoa_rules().get("rules", [])
    ids = [rule["rule_id"] for rule in rules]
    assert len(ids) == len(set(ids))
    assert len(rules) >= 8


def test_lien_hoa_get_specific_rule():
    rule = get_lien_hoa_rule("lien_hoa.dun.plus_4_6_4_cycle")
    assert rule is not None
    assert "4-6-4" in rule["name_vi"] or "4-6-4" in rule["logic_summary"]


def test_lien_hoa_queue_has_daily_items():
    queue = load_lien_hoa_reading_queue()
    assert len(queue.get("days", [])) >= 5


def test_lien_hoa_list_rules_filter():
    active = list_lien_hoa_rules(status="active")
    assert any(rule["rule_id"] == "lien_hoa.core.chanh_quai_build" for rule in active)
