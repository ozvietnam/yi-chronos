"""Tests for the engine-critique extractor + SQLite store."""

from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolated_db(monkeypatch, tmp_path):
    """Point CRITIQUE_DB to a tmp file so tests don't pollute real store."""
    from engine.ai import critique_store as cs

    tmp_db = tmp_path / "crit.sqlite3"
    monkeypatch.setattr(cs, "CRITIQUE_DB", tmp_db)
    yield


# ─── Parser ──────────────────────────────────────────────────────────────────


def test_parse_multi_line_format():
    from engine.ai.critique_store import parse_critiques

    sage_out = """## READ
Day Master Kỷ thổ ...

## GAP
- chart_gap: thiếu Hỏa
- engine_gap: Thần Sát chưa đầy đủ

## IMPROVE

### improve_user
- Hướng Nam, màu đỏ

### improve_system
- target: engine.bat_tu.than_sat
  suggestion: thêm Khôi Cương, Văn Xương vào output
  priority: medium
  rationale: hiện chỉ có 6/15 sao phụ
- target: engine.bat_tu.dung_than
  suggestion: cross-validate với Tử Vi cung Tài
  priority: high
  rationale: tăng confidence Dụng Thần
"""
    items = parse_critiques(sage_out)
    assert len(items) == 2
    assert items[0].target == "engine.bat_tu.than_sat"
    assert "Khôi Cương" in items[0].suggestion
    assert items[0].priority == "medium"
    assert items[0].rationale.startswith("hiện chỉ có")
    assert items[1].priority == "high"


def test_parse_missing_priority_normalizes_to_none():
    from engine.ai.critique_store import parse_critiques

    sage_out = """### improve_system
- target: engine.tu_vi.luu_tru
  suggestion: thêm lưu trú phụ tinh
  priority: medium-high
  rationale: ...
"""
    items = parse_critiques(sage_out)
    assert len(items) == 1
    # 'medium-high' isn't valid → normalized to None
    assert items[0].priority is None


def test_parse_missing_section_returns_empty():
    from engine.ai.critique_store import parse_critiques

    assert parse_critiques("just a READ block") == []
    assert parse_critiques("") == []


def test_parse_rejects_bullet_without_target():
    from engine.ai.critique_store import parse_critiques

    sage_out = """### improve_system
- suggestion: orphan with no target
  priority: high
"""
    assert parse_critiques(sage_out) == []


# ─── Storage ─────────────────────────────────────────────────────────────────


def test_store_and_list_critiques():
    from engine.ai.critique_store import (
        ParsedCritique, list_critiques, store_critiques,
    )

    items = [
        ParsedCritique(
            target="engine.bat_tu.than_sat",
            suggestion="A",
            priority="high",
            rationale="r1",
        ),
        ParsedCritique(
            target="engine.tu_vi.an_sao",
            suggestion="B",
            priority="low",
            rationale="r2",
        ),
    ]
    ids = store_critiques(
        root_id="t_root", sage_tag="bat_tu", task_id="t_a", critiques=items
    )
    assert len(ids) == 2

    open_list = list_critiques(status="open")
    assert len(open_list) == 2
    # High-priority should sort first
    assert open_list[0]["priority"] == "high"


def test_list_filter_by_priority_and_target():
    from engine.ai.critique_store import ParsedCritique, list_critiques, store_critiques

    store_critiques(
        root_id="r", sage_tag="bat_tu", task_id="t1",
        critiques=[
            ParsedCritique("engine.bat_tu.x", "s1", "high", "r1"),
            ParsedCritique("engine.tu_vi.y", "s2", "low", "r2"),
        ],
    )
    bat_tu_only = list_critiques(target_prefix="engine.bat_tu")
    assert len(bat_tu_only) == 1
    assert bat_tu_only[0]["target"].startswith("engine.bat_tu")

    high_only = list_critiques(priority="high")
    assert all(c["priority"] == "high" for c in high_only)


def test_resolve_and_dismiss_critique():
    from engine.ai.critique_store import (
        ParsedCritique, dismiss_critique, list_critiques, resolve_critique,
        store_critiques,
    )

    ids = store_critiques(
        root_id="r", sage_tag="bat_tu", task_id="t1",
        critiques=[ParsedCritique("engine.x.y", "s", "low", "r")],
    )
    cid = ids[0]
    assert resolve_critique(cid, resolution="fixed in PR #42")
    resolved = list_critiques(status="resolved")
    assert any(c["id"] == cid for c in resolved)
    assert resolved[0]["resolution"] == "fixed in PR #42"

    ids2 = store_critiques(
        root_id="r", sage_tag="bat_tu", task_id="t2",
        critiques=[ParsedCritique("engine.x.y", "s2", "low", "r")],
    )
    assert dismiss_critique(ids2[0], reason="duplicate")
    dismissed = list_critiques(status="dismissed")
    assert any(c["resolution"] == "duplicate" for c in dismissed)


def test_harvest_is_idempotent():
    """Calling harvest twice on the same task must not double-insert."""
    from engine.ai.critique_store import harvest_from_sage_task, list_critiques

    sage_out = """### improve_system
- target: engine.foo.bar
  suggestion: do X
  priority: low
  rationale: r
"""
    ids1 = harvest_from_sage_task(
        root_id="r", sage_tag="bat_tu", task_id="t_dup", sage_output=sage_out
    )
    ids2 = harvest_from_sage_task(
        root_id="r", sage_tag="bat_tu", task_id="t_dup", sage_output=sage_out
    )
    assert len(ids1) == 1
    assert ids2 == []
    assert len(list_critiques()) == 1


def test_stats_dashboard():
    from engine.ai.critique_store import ParsedCritique, stats, store_critiques

    store_critiques(
        root_id="r", sage_tag="bat_tu", task_id="t",
        critiques=[
            ParsedCritique("a.b.c", "s", "high", "r"),
            ParsedCritique("a.b.d", "s", "low", "r"),
            ParsedCritique("a.b.e", "s", "low", "r"),
        ],
    )
    s = stats()
    assert s["total"] == 3
    assert s["open"]["high"] == 1
    assert s["open"]["low"] == 2


# ─── API ─────────────────────────────────────────────────────────────────────


def test_api_list_and_stats():
    from fastapi.testclient import TestClient

    from api.main import app
    from engine.ai.critique_store import ParsedCritique, store_critiques

    store_critiques(
        root_id="r_api", sage_tag="tu_vi", task_id="t_api",
        critiques=[
            ParsedCritique("engine.tu_vi.luu_tru", "add transit", "high", "rationale"),
        ],
    )
    client = TestClient(app)
    r = client.get("/api/ai/council/critiques?target_prefix=engine.tu_vi")
    assert r.status_code == 200
    crits = r.json()["critiques"]
    assert any(c["target"] == "engine.tu_vi.luu_tru" for c in crits)

    r2 = client.get("/api/ai/council/critiques/stats")
    assert r2.status_code == 200
    assert r2.json()["stats"]["total"] >= 1


def test_api_resolve_critique():
    from fastapi.testclient import TestClient

    from api.main import app
    from engine.ai.critique_store import ParsedCritique, store_critiques

    ids = store_critiques(
        root_id="r", sage_tag="bat_tu", task_id="t",
        critiques=[ParsedCritique("engine.x.y", "s", "low", "r")],
    )
    cid = ids[0]
    client = TestClient(app)
    r = client.post(
        f"/api/ai/council/critiques/{cid}/resolve",
        json={"resolution": "applied in commit abc", "action": "resolve"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
