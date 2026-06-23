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


def test_system_stats_revenue_and_classification(temp_db):
    """Doanh thu = nạp IAP; phân loại đúng hoạt động; quy đổi ₫."""
    from engine import xu_wallet as x
    x.grant(1, 100, "iap_pack_100")           # nạp IAP → doanh thu
    x.grant(1, 10, "daily_bonus")             # thưởng (không tính doanh thu)
    x.spend(1, 5, "hermes_council")           # tiêu Hội Đồng
    x.spend(1, 30, "cross_paradigm_couple_sync")   # tiêu giao duyên
    s = x.system_stats()
    assert s["revenue_xu"] == 100 and s["revenue_vnd"] == 100 * x.XU_VND
    assert s["circulating"] == 75 and s["spent_total"] == 35
    assert s["by_category"]["council"]["spent"] == 5
    assert s["by_category"]["giao_duyen"]["spent"] == 30
    assert s["bonus_given_xu"] == 10
    g = x.recent_ledger_global(10)
    assert g and g[0]["cat"] in ("council", "giao_duyen", "topup", "daily_bonus")


def test_xu_overview_transactions_owner_only(temp_db):
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    assert c.get("/api/admin/xu/overview").status_code in (401, 403)
    assert c.get("/api/admin/xu/transactions").status_code in (401, 403)
