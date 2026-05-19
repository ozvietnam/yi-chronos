from core.luc_hao_data import (
    get_luc_hao_rule,
    list_luc_hao_reading_days,
    list_luc_hao_rules,
    load_luc_hao_reading_queue,
    load_luc_hao_rules,
    load_luc_hao_source_index,
)


def test_luc_hao_source_index_has_sources():
    payload = load_luc_hao_source_index()
    assert "sources" in payload
    assert len(payload["sources"]) >= 1


def test_luc_hao_rules_have_unique_rule_ids():
    payload = load_luc_hao_rules()
    rules = payload.get("rules", [])
    rule_ids = [rule["rule_id"] for rule in rules]
    assert len(rule_ids) == len(set(rule_ids))
    assert len(rules) >= 3


def test_get_rule_by_id():
    rule = get_luc_hao_rule("luc_hao.core.line_order")
    assert rule is not None
    assert rule["name_vi"] == "Thu tu hao trong que"


def test_list_rules_by_status():
    active_rules = list_luc_hao_rules(status="active")
    assert any(rule["rule_id"] == "luc_hao.core.line_order" for rule in active_rules)


def test_reading_queue_has_daily_plan():
    queue = load_luc_hao_reading_queue()
    days = queue.get("days", [])
    assert len(days) >= 7
    assert all("day_id" in day for day in days)


def test_list_reading_days_by_status():
    queued_days = list_luc_hao_reading_days(status="queued")
    assert len(queued_days) >= 1
