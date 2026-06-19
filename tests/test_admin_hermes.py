"""Phòng Quản Trị Hermes (task 1) — roster + metrics + enable toggle + audit."""
import pytest

from engine.db import get_engine


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/admin.sqlite3")
    get_engine.cache_clear()
    from api import sync
    sync._ensure_schema()           # audit_log + user_castings + user_subscriptions...
    yield
    get_engine.cache_clear()


def test_roster_has_sages_arbiter_orchestrator(temp_db):
    from engine import admin_hermes as ah
    roster = ah.get_roster()
    tags = {r["tag"] for r in roster}
    # 8 sage + orchestrator + arbiter
    for t in ("mai_hoa", "tu_vi", "bat_tu", "luc_hao", "than_so", "arbiter"):
        assert t in tags, f"thiếu vai {t}"
    for r in roster:
        assert {"tag", "name_vi", "icon", "enabled", "soul_size", "knowledge_version"} <= set(r)


def test_sage_enable_toggle(temp_db):
    from engine import admin_hermes as ah
    assert ah.is_sage_enabled("tu_vi") is True          # mặc định bật
    ah.set_sage_enabled("tu_vi", False)
    assert ah.is_sage_enabled("tu_vi") is False
    roster = {r["tag"]: r for r in ah.get_roster()}
    assert roster["tu_vi"]["enabled"] is False
    ah.set_sage_enabled("tu_vi", True)
    assert ah.is_sage_enabled("tu_vi") is True


def test_audit_roundtrip(temp_db):
    from engine import admin_hermes as ah
    ah.audit("toggle_sage", actor_user_id=1, details={"tag": "tu_vi", "enabled": False})
    ah.audit("edit_soul", actor_user_id=1, details={"tag": "bat_tu"})
    log = ah.list_audit(limit=10)
    assert len(log) >= 2
    assert log[0]["action"] in ("edit_soul", "toggle_sage")   # mới nhất trước
    assert log[0]["actor_user_id"] == 1


def test_metrics_shape(temp_db):
    from engine import admin_hermes as ah
    m = ah.get_metrics()
    assert "spend" in m and "by_method" in m
    assert "paradigm_flags" in m and isinstance(m["paradigm_flags"], int)
    assert "evolve_pending" in m
