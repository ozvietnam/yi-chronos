"""Mã khuyến mãi tặng xu — tạo/đổi/1-lần-user/hạn/cap + seed OZFREIGHT + gate (Anh chốt 23/6)."""
import pytest

from engine.db import get_engine


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/promo.sqlite3")
    get_engine.cache_clear()
    from api import sync
    sync._ensure_schema()
    yield
    get_engine.cache_clear()


def test_create_redeem_once_per_user(temp_db):
    from engine import promo_codes as pc, xu_wallet as x
    pc.create_code("OZFREIGHT", 50, campaign="OZ", per_user_once=True)
    r1 = pc.redeem(7, "ozfreight")                       # nhập thường → normalize
    assert r1["ok"] and r1["xu"] == 50 and x.get_balance(7) == 50
    r2 = pc.redeem(7, "OZFREIGHT")                       # lần 2 cùng user
    assert not r2["ok"] and r2["reason"] == "already_redeemed" and x.get_balance(7) == 50
    r3 = pc.redeem(8, "OZFREIGHT")                       # user khác
    assert r3["ok"] and x.get_balance(8) == 50


def test_reject_reasons(temp_db):
    from engine import promo_codes as pc
    assert pc.redeem(1, "NOPE")["reason"] == "not_found"
    pc.create_code("OFFC", 10); pc.set_active("OFFC", False)
    assert pc.redeem(1, "OFFC")["reason"] == "inactive"
    pc.create_code("EXPC", 10, expires_at=1)             # quá khứ
    assert pc.redeem(1, "EXPC")["reason"] == "expired"
    pc.create_code("CAPC", 10, per_user_once=False, max_total=1)
    assert pc.redeem(1, "CAPC")["ok"]
    assert pc.redeem(2, "CAPC")["reason"] == "exhausted"


def test_dup_code_fails(temp_db):
    from engine import promo_codes as pc
    pc.create_code("DUP", 10)
    with pytest.raises(ValueError):
        pc.create_code("dup", 20)                        # trùng (normalize)


def test_seed_default_ozfreight_idempotent(temp_db):
    from engine import promo_codes as pc
    pc.seed_default_codes()
    c = pc.get_code("OZFREIGHT")
    assert c and c["xu"] == 50 and c["per_user_once"]
    pc.seed_default_codes()                              # gọi lại không lỗi/không nhân đôi
    assert pc.get_code("OZFREIGHT")["xu"] == 50


def test_endpoints_gated(temp_db):
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    assert c.post("/api/wallet/redeem", json={"code": "X"}).status_code in (401, 403)
    assert c.post("/api/admin/promo/codes", json={"code": "X", "xu": 1}).status_code in (401, 403)
    assert c.get("/api/admin/promo/codes").status_code in (401, 403)
    assert c.post("/api/sync/promo/redeem",
                  json={"firebase_uid": "u", "code": "X"}).status_code in (401, 403, 503)
