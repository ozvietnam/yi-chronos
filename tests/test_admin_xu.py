"""Owner kiểm soát ví Xu của user trong admin (cộng/trừ ±, sàn 0, sổ cái, gate owner)."""
import pytest

from engine.db import get_engine


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/axu.sqlite3")
    get_engine.cache_clear()
    from api import sync
    sync._ensure_schema()
    yield
    get_engine.cache_clear()


def test_admin_adjust_floor_and_ledger(temp_db):
    from engine import xu_wallet as x
    x.grant(7, 100, "seed")
    assert x.admin_adjust(7, -30, "phạt")["balance"] == 70
    r = x.admin_adjust(7, -200, "trừ quá tay")
    assert r["balance"] == 0 and r["delta_applied"] == -70      # sàn 0, không âm
    assert x.admin_adjust(7, 50, "tặng")["balance"] == 50
    led = x.recent_ledger(7, 10)
    assert len(led) == 4                                        # seed + 3 adjust
    assert led[0]["reason"] == "admin:tặng"                     # mới nhất trước
    assert all(l["reason"].startswith("admin:") for l in led[:3])


def test_admin_adjust_zero_noop(temp_db):
    from engine import xu_wallet as x
    x.grant(9, 40, "seed")
    assert x.admin_adjust(9, 0, "noop")["delta_applied"] == 0


def test_admin_xu_endpoint_owner_only(temp_db):
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    r = c.post("/api/admin/users/7/xu", json={"delta": 10, "reason": "test"})
    assert r.status_code in (401, 403)                          # khách ẩn danh chặn
