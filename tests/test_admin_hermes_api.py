"""Phòng Quản Trị Hermes (task 2/4/6) — API owner-only + audit. Guest→401, owner→flow."""
import pytest
from fastapi.testclient import TestClient

from engine.db import get_engine


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/aapi.sqlite3")
    get_engine.cache_clear()
    from api import sync
    sync._ensure_schema()
    yield
    get_engine.cache_clear()


def test_admin_endpoints_require_owner(temp_db):
    """Guest (không session) → 401/403 cho MỌI endpoint admin (regression privacy)."""
    from api.main import app
    c = TestClient(app)
    for path in ("/api/admin/hermes/roster", "/api/admin/hermes/metrics",
                 "/api/admin/hermes/audit", "/api/admin/hermes/evolve/pending",
                 "/api/admin/hermes/sage/tu_vi/soul"):
        assert c.get(path).status_code in (401, 403), path
    assert c.post("/api/admin/hermes/sage/tu_vi/toggle").status_code in (401, 403)
    assert c.post("/api/admin/hermes/commander/ask",
                  json={"question": "x"}).status_code in (401, 403)


def test_admin_owner_roster_toggle_audit(temp_db, as_owner):
    from api.main import app
    c = TestClient(app)
    r = c.get("/api/admin/hermes/roster")
    assert r.status_code == 200 and len(r.json()["roster"]) >= 9

    t = c.post("/api/admin/hermes/sage/tu_vi/toggle")
    assert t.status_code == 200 and t.json()["tag"] == "tu_vi"

    audit = c.get("/api/admin/hermes/audit").json()["audit"]
    assert any(x["action"] == "toggle_sage" for x in audit)   # task 6: audit ghi nhận


def test_admin_metrics_and_commander(temp_db, as_owner):
    from api.main import app
    c = TestClient(app)
    assert c.get("/api/admin/hermes/metrics").json()["metrics"]
    cm = c.post("/api/admin/hermes/commander/ask",
                json={"question": "hệ thống thế nào, có gì chờ duyệt?"})
    assert cm.status_code == 200
    assert cm.json()["answer"]
    assert "xác nhận" in cm.json()["note"].lower()            # chỉ đề xuất, không tự thực thi


def test_admin_soul_get_set(temp_db, as_owner):
    from api.main import app
    c = TestClient(app)
    g = c.get("/api/admin/hermes/sage/tu_vi/soul")
    assert g.status_code == 200 and "soul" in g.json()
    p = c.put("/api/admin/hermes/sage/tu_vi/soul", json={"content": "Persona test."})
    assert p.status_code == 200
    assert c.get("/api/admin/hermes/sage/_nope_/soul").status_code == 404
