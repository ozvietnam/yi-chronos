"""P0 — unit cho helper coercion của migrate script (không cần DB).

Trọng tâm: _json_or_none chuẩn hoá giá trị cột JSONB để CAST không abort batch.
"""
from __future__ import annotations

from scripts.migrate_sqlite_to_postgres import _json_or_none


def test_json_or_none_passthrough_valid():
    assert _json_or_none('{"a":1}') == '{"a":1}'
    assert _json_or_none("[1,2,3]") == "[1,2,3]"


def test_json_or_none_empty_and_blank_to_null():
    assert _json_or_none("") is None
    assert _json_or_none("   ") is None
    assert _json_or_none(None) is None


def test_json_or_none_malformed_to_null():
    # text không phải JSON (dữ liệu cũ lỡ ghi) → NULL, không làm vỡ CAST AS JSONB
    assert _json_or_none("not json") is None
    assert _json_or_none("{bad") is None


def test_json_or_none_dict_list_serialized():
    assert _json_or_none({"a": 1}) == '{"a": 1}'
    assert _json_or_none([1, 2]) == "[1, 2]"
