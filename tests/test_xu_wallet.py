"""Ví Xu trung tâm (YI) — engine.xu_wallet. Dual-driver (test trên SQLite tmp).

Khớp kinh tế AppChat: quick 1 / council 5 / deep 99 · free quick 3/ngày ·
login +10 xu/ngày trong cửa sổ 30 ngày. Tiền → spend phải nguyên tử, không âm.
"""
import time

import pytest
from sqlalchemy import text

from engine.db import get_engine, session_scope


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/xu.sqlite3")
    get_engine.cache_clear()
    yield
    get_engine.cache_clear()


def _mk_user(user_id: int, created_at: int) -> None:
    """Tạo 1 user tối thiểu (xu_wallet.claim_daily đọc users.created_at)."""
    with session_scope(service=True) as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY, email TEXT, display_name TEXT,
                password_hash TEXT, password_salt TEXT, role TEXT, created_at BIGINT,
                firebase_uid TEXT
            )"""))
        conn.execute(
            text("""INSERT INTO users (user_id, email, display_name, password_hash,
                    password_salt, role, created_at) VALUES (:u,:e,'n','h','s','user',:c)"""),
            {"u": user_id, "e": f"u{user_id}@x.vn", "c": created_at},
        )


# ── Hằng số khớp AppChat ──────────────────────────────────────────────────────
def test_constants_match_appchat(temp_db):
    from engine import xu_wallet as w
    assert w.XU_COST == {"quick": 1, "council": 5, "deep": 99}
    assert w.FREE_QUICK_PER_DAY == 3
    assert w.DAILY_BONUS_XU == 10
    assert w.WELCOME_WINDOW_DAYS == 30
    assert w.XU_VND == 1000


# ── grant / spend ─────────────────────────────────────────────────────────────
def test_grant_increases_balance(temp_db):
    from engine import xu_wallet as w
    assert w.get_balance(1) == 0
    assert w.grant(1, 100, "topup") == 100
    assert w.grant(1, 50, "topup") == 150
    assert w.get_balance(1) == 150


def test_grant_idempotent_by_ref(temp_db):
    from engine import xu_wallet as w
    assert w.grant(3, 100, "topup", ref="rc_txn_99") == 100
    # webhook retry cùng ref → KHÔNG cộng lại
    assert w.grant(3, 100, "topup", ref="rc_txn_99") == 100
    assert w.get_balance(3) == 100
    # ref khác → cộng bình thường
    assert w.grant(3, 50, "topup", ref="rc_txn_100") == 150
    # không ref → luôn cộng (vd thưởng thủ công)
    assert w.grant(3, 10, "manual") == 160
    assert w.grant(3, 10, "manual") == 170


def test_grant_rejects_nonpositive(temp_db):
    from engine import xu_wallet as w
    with pytest.raises(ValueError):
        w.grant(1, 0, "x")
    with pytest.raises(ValueError):
        w.grant(1, -5, "x")


def test_spend_ok_decreases(temp_db):
    from engine import xu_wallet as w
    w.grant(7, 10, "topup")
    r = w.spend(7, 5, "council")
    assert r["ok"] is True
    assert r["balance"] == 5
    assert w.get_balance(7) == 5


def test_spend_insufficient_no_change(temp_db):
    from engine import xu_wallet as w
    w.grant(7, 3, "topup")
    r = w.spend(7, 99, "deep")
    assert r["ok"] is False
    assert r["reason"] == "insufficient_xu"
    assert r["need"] == 99 and r["have"] == 3
    assert w.get_balance(7) == 3  # KHÔNG trừ


def test_spend_exact_to_zero(temp_db):
    from engine import xu_wallet as w
    w.grant(7, 1, "topup")
    assert w.spend(7, 1, "quick")["ok"] is True
    assert w.get_balance(7) == 0


def test_ledger_records_each_move(temp_db):
    from engine import xu_wallet as w
    w.grant(9, 100, "topup", ref="rc_txn_1")
    w.spend(9, 5, "council", ref="cast_42")
    with session_scope(service=True) as conn:
        rows = conn.execute(
            text("SELECT delta, reason, balance_after, ref FROM xu_ledger WHERE user_id=9 ORDER BY ts"),
        ).fetchall()
    assert [(r[0], r[1], r[2]) for r in rows] == [(100, "topup", 100), (-5, "council", 95)]
    assert rows[0][3] == "rc_txn_1" and rows[1][3] == "cast_42"


# ── spend idempotent (PRVchat lì xì / hong bao — chống double-charge) ──────────
def test_spend_idempotent_by_ref(temp_db):
    """Cloud Function retry cùng ref → CHỈ trừ 1 lần. Người gửi lì xì không mất 2 lần xu."""
    from engine import xu_wallet as w
    w.grant(11, 100, "topup")
    r1 = w.spend(11, 50, "hong_bao_send", ref="hongBao_xyz", idempotent=True)
    assert r1["ok"] is True and r1["balance"] == 50 and not r1.get("idempotent_hit")
    r2 = w.spend(11, 50, "hong_bao_send", ref="hongBao_xyz", idempotent=True)  # retry
    assert r2["ok"] is True and r2["balance"] == 50 and r2["idempotent_hit"] is True
    assert w.get_balance(11) == 50            # trừ đúng 1 lần
    r3 = w.spend(11, 20, "hong_bao_send", ref="hongBao_abc", idempotent=True)  # ref khác
    assert r3["ok"] is True and r3["balance"] == 30
    assert w.get_balance(11) == 30


def test_spend_idempotent_off_by_default(temp_db):
    """KHÔNG bật idempotent → cùng ref VẪN trừ mỗi lần (giữ nguyên hành vi caller cũ, vd cross_paradigm)."""
    from engine import xu_wallet as w
    w.grant(12, 100, "topup")
    assert w.spend(12, 10, "council", ref="cast_1")["balance"] == 90
    assert w.spend(12, 10, "council", ref="cast_1")["balance"] == 80  # trừ lại
    assert w.get_balance(12) == 80


def test_spend_idempotent_still_blocks_insufficient(temp_db):
    """ref mới nhưng không đủ xu → vẫn 402-path (ok=False), KHÔNG ghi sổ."""
    from engine import xu_wallet as w
    w.grant(13, 20, "topup")
    r = w.spend(13, 50, "hong_bao_send", ref="hb_new", idempotent=True)
    assert r["ok"] is False and r["reason"] == "insufficient_xu"
    assert w.get_balance(13) == 20


# ── daily bonus (pure) ────────────────────────────────────────────────────────
def test_daily_bonus_decision_ok(temp_db):
    from engine import xu_wallet as w
    now = 1_000_000_000_000
    d = w.daily_bonus_decision(created_at_ms=now, now_ms=now,
                               last_claim_date=None, today_date="2026-06-19")
    assert d["grant"] is True and d["amount"] == 10 and d["reason"] == "ok"
    assert d["days_left"] == 30


def test_daily_bonus_already_claimed(temp_db):
    from engine import xu_wallet as w
    now = 1_000_000_000_000
    d = w.daily_bonus_decision(created_at_ms=now, now_ms=now,
                               last_claim_date="2026-06-19", today_date="2026-06-19")
    assert d["grant"] is False and d["reason"] == "already_claimed"


def test_daily_bonus_window_over(temp_db):
    from engine import xu_wallet as w
    created = 1_000_000_000_000
    now = created + 31 * 86_400_000  # 31 ngày sau
    d = w.daily_bonus_decision(created_at_ms=created, now_ms=now,
                               last_claim_date=None, today_date="2026-07-20")
    assert d["grant"] is False and d["reason"] == "window_over" and d["days_left"] == 0


# ── claim_daily (stateful) ────────────────────────────────────────────────────
def test_claim_daily_grants_once_per_day(temp_db):
    from engine import xu_wallet as w
    now_ms = int(time.time() * 1000)
    _mk_user(5, created_at=now_ms // 1000)  # tạo TK hôm nay
    r1 = w.claim_daily(5, now_ms=now_ms)
    assert r1["claimed"] is True and r1["xu"] == 10
    r2 = w.claim_daily(5, now_ms=now_ms)  # cùng ngày → không tặng lại
    assert r2["claimed"] is False and r2["reason"] == "already_claimed" and r2["xu"] == 10
    assert w.get_balance(5) == 10


def test_claim_daily_window_over_for_old_account(temp_db):
    from engine import xu_wallet as w
    now_ms = int(time.time() * 1000)
    _mk_user(6, created_at=(now_ms // 1000) - 40 * 86_400)  # TK tạo 40 ngày trước
    r = w.claim_daily(6, now_ms=now_ms)
    assert r["claimed"] is False and r["reason"] == "window_over"
    assert w.get_balance(6) == 0
