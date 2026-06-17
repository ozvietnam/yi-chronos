"""P0-2 — hồi quy `engine/subscriptions.py` sau khi chuyển sang engine.db.

Chạy CÙNG kịch bản gating trên 2 backend:
  - sqlite (luôn chạy) — chứng minh non-breaking trên dev.
  - postgres (chỉ khi YI_TEST_PG_DSN) — chứng minh chạy thật trên prod-driver.

Hành vi phải y hệt bản sqlite3 cũ: grant → allowed → consume hết lượt → denied
(no_uses_left) → expired → revoke (disabled).
"""
from __future__ import annotations

import os
import sqlite3
import time

import pytest
from sqlalchemy import text

import engine.db as db
import engine.subscriptions as subs

PG_DSN = os.environ.get("YI_TEST_PG_DSN", "").strip()

BACKENDS = ["sqlite"]
if PG_DSN:
    BACKENDS.append("pg")


@pytest.fixture(params=BACKENDS)
def backend(request, tmp_path, monkeypatch):
    """Trả backend đã có bảng + 1 user (user_id=1) sẵn sàng."""
    if request.param == "sqlite":
        path = tmp_path / "users.sqlite3"
        import api.auth as auth
        con = sqlite3.connect(path)
        auth._init_schema(con)  # tạo users + user_subscriptions (+ các bảng khác)
        con.execute("INSERT INTO users(user_id,email,display_name,password_hash,"
                    "password_salt,role,created_at) VALUES (1,'a@x','A','h','s','user',1)")
        con.commit(); con.close()
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
    else:
        monkeypatch.setenv("DATABASE_URL", PG_DSN)
        db.get_engine.cache_clear()
        with db.get_engine().begin() as conn:
            db.apply_schema(conn)
        with db.session_scope(service=True) as conn:
            conn.execute(text("TRUNCATE user_subscriptions, users RESTART IDENTITY CASCADE"))
            conn.execute(text("INSERT INTO users(user_id,email,display_name,password_hash,"
                              "password_salt,role,created_at) VALUES "
                              "(1,'a@x','A','h','s','user',1)"))
    db.get_engine.cache_clear()
    yield request.param
    db.get_engine.cache_clear()


def test_grant_check_consume_flow(backend):
    # chưa grant → no_subscription
    assert subs.check_access(1, "tu_vi_phe_menh_sau")["reason"] == "no_subscription"

    # grant 2 lượt
    r = subs.grant_subscription(1, "tu_vi_phe_menh_sau", tier="vip1", remaining_uses=2)
    assert r["action"] == "created"
    assert subs.check_access(1, "tu_vi_phe_menh_sau")["allowed"] is True

    # tiêu 2 lượt
    c1 = subs.consume_use(1, "tu_vi_phe_menh_sau")
    assert c1["remaining_uses"] == 1 and c1["total_uses"] == 1
    c2 = subs.consume_use(1, "tu_vi_phe_menh_sau")
    assert c2["remaining_uses"] == 0 and c2["total_uses"] == 2

    # hết lượt → denied
    chk = subs.check_access(1, "tu_vi_phe_menh_sau")
    assert chk["allowed"] is False and chk["reason"] == "no_uses_left"


def test_grant_update_and_unlimited(backend):
    # grant không remaining_uses (unlimited) — upsert sang 'updated'
    subs.grant_subscription(1, "tu_vi_phe_menh_sau", remaining_uses=1)
    r2 = subs.grant_subscription(1, "tu_vi_phe_menh_sau", remaining_uses=None)
    assert r2["action"] == "updated"
    assert subs.check_access(1, "tu_vi_phe_menh_sau")["allowed"] is True
    # consume khi unlimited: chỉ tăng total, remaining vẫn None
    c = subs.consume_use(1, "tu_vi_phe_menh_sau")
    assert c["remaining_uses"] is None and c["total_uses"] == 1


def test_expired_and_revoke(backend):
    subs.grant_subscription(1, "tu_vi_phe_menh_sau", expires_at=int(time.time()) - 10)
    assert subs.check_access(1, "tu_vi_phe_menh_sau")["reason"] == "expired"

    subs.grant_subscription(1, "tu_vi_phe_menh_sau", expires_at=None, remaining_uses=5)
    assert subs.check_access(1, "tu_vi_phe_menh_sau")["allowed"] is True
    subs.revoke_subscription(1, "tu_vi_phe_menh_sau")
    assert subs.check_access(1, "tu_vi_phe_menh_sau")["reason"] == "disabled"


def test_listings(backend):
    subs.grant_subscription(1, "tu_vi_phe_menh_sau", remaining_uses=3)
    mine = subs.list_user_subscriptions(1)
    assert len(mine) == 1 and mine[0]["feature_id"] == "tu_vi_phe_menh_sau"
    assert mine[0]["feature_meta"]["tier_required"] == "vip1"
    allsubs = subs.list_all_subscriptions()           # JOIN users
    assert any(s["email"] == "a@x" for s in allsubs)
    assert subs.list_all_subscriptions("tu_vi_phe_menh_sau")[0]["user_id"] == 1


def test_unknown_feature(backend):
    assert subs.check_access(1, "nope")["reason"] == "unknown_feature"
    assert subs.grant_subscription(1, "nope")["error"] == "unknown_feature"
