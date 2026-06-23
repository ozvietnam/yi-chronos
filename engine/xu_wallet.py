"""Ví Xu — kinh tế tiền ảo TRUNG TÂM (YI = nguồn chân lý).

Quyết định 2026-06-19 (Anh chốt): YI là **ví trung tâm** cho cả 2 kênh —
  • AppChat (service-keyed): nạp xu (sau RevenueCat/IAP) + tiêu xu khi gọi Hermes.
  • YI-web (auth user): cùng một ví, parity hoàn toàn.
AppChat KHÔNG còn tự trừ ở Firestore — chỉ hiển thị + mở luồng nạp; mọi cộng/trừ
THẬT nằm ở đây để không double-charge / lệch số dư.

Hằng số KHỚP AppChat (prvchat `functions/src/xu/xuLedger.ts`):
  1 xu = 1.000₫ · quick 1 / council 5 / deep 99 · free quick 3/ngày ·
  login +10 xu/ngày trong cửa sổ welcome 30 ngày (tính từ users.created_at).

Hiện thực mirror `engine.llm_spend.try_charge`: MỘT transaction có khoá
(advisory lock PG cấp-transaction) → check-rồi-ghi nguyên tử, nhiều request đồng
thời không thể cùng tiêu quá số dư (đóng cửa sổ TOCTOU). Dual-driver (engine.db),
DDL portable (chạy cả SQLite lẫn Postgres). Số dư + sổ cái là dữ liệu tiền —
KHÔNG nuốt lỗi như đo lường: lỗi hạ tầng ở spend → coi như KHÔNG tiêu được.
"""
from __future__ import annotations

import time
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import text

from engine.db import is_postgres, session_scope

# Ngày "local" Việt Nam (UTC+7) — đồng bộ llm_spend + claimDailyXu phía AppChat.
_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
_DAY_MS = 86_400_000

# ── Hằng số kinh tế (single source of truth phía YI; khớp AppChat) ────────────
XU_VND = 1000  # 1 xu = 1.000₫ (CEO chốt 2026-06-19)
XU_COST = {
    "quick": 1,    # Hỏi nhanh (sau khi hết lượt free/ngày)
    "council": 5,  # Hội Đồng đa-sage
    "deep": 99,    # Luận sâu trọn lá số (DeepSeek)
}
FREE_QUICK_PER_DAY = 3   # Hỏi nhanh miễn phí mỗi ngày (rồi mới tiêu xu)
DAILY_BONUS_XU = 10      # Tặng khi đăng nhập, trong cửa sổ welcome
WELCOME_WINDOW_DAYS = 30  # Cửa sổ tặng xu đăng nhập kể từ khi tạo tài khoản

_DDL_WALLET = """
CREATE TABLE IF NOT EXISTS xu_wallet (
    user_id          BIGINT PRIMARY KEY,
    balance          BIGINT NOT NULL DEFAULT 0,
    daily_last_claim TEXT,
    created_at       BIGINT,
    updated_at       BIGINT
)
"""
# Sổ cái append-only (audit tiền). Không PK tự tăng → portable SQLite/PG như llm_spend.
_DDL_LEDGER = """
CREATE TABLE IF NOT EXISTS xu_ledger (
    ts            BIGINT NOT NULL,
    day           TEXT NOT NULL,
    user_id       BIGINT NOT NULL,
    delta         BIGINT NOT NULL,
    reason        TEXT,
    balance_after BIGINT NOT NULL,
    ref           TEXT
)
"""
_DDL_LEDGER_IDX = "CREATE INDEX IF NOT EXISTS idx_xu_ledger_user ON xu_ledger(user_id, ts)"


def _ensure(conn) -> None:
    conn.execute(text(_DDL_WALLET))
    conn.execute(text(_DDL_LEDGER))
    conn.execute(text(_DDL_LEDGER_IDX))


def _today() -> str:
    return datetime.now(_TZ).strftime("%Y-%m-%d")


def _lock(conn, user_id: int) -> None:
    """Serialize mọi thao tác ví của cùng 1 user tới khi commit (PG). SQLite 1-writer."""
    if is_postgres():
        conn.execute(
            text("SELECT pg_advisory_xact_lock(hashtext('yi_xu_wallet'), :u)"),
            {"u": int(user_id)},
        )


def _read_balance(conn, user_id: int) -> int:
    row = conn.execute(
        text("SELECT balance FROM xu_wallet WHERE user_id=:u"),
        {"u": int(user_id)},
    ).fetchone()
    return int(row[0]) if row else 0


def _write(conn, user_id: int, new_balance: int, *, daily: Optional[str] = None,
           keep_daily: bool = True) -> None:
    """Upsert số dư (portable: SELECT-then-INSERT/UPDATE dưới khoá)."""
    now = int(time.time())
    exists = conn.execute(
        text("SELECT 1 FROM xu_wallet WHERE user_id=:u"), {"u": int(user_id)},
    ).fetchone()
    if exists:
        if daily is not None:
            conn.execute(
                text("""UPDATE xu_wallet SET balance=:b, daily_last_claim=:d, updated_at=:t
                        WHERE user_id=:u"""),
                {"b": int(new_balance), "d": daily, "t": now, "u": int(user_id)},
            )
        else:
            conn.execute(
                text("UPDATE xu_wallet SET balance=:b, updated_at=:t WHERE user_id=:u"),
                {"b": int(new_balance), "t": now, "u": int(user_id)},
            )
    else:
        conn.execute(
            text("""INSERT INTO xu_wallet (user_id, balance, daily_last_claim, created_at, updated_at)
                    VALUES (:u, :b, :d, :t, :t)"""),
            {"u": int(user_id), "b": int(new_balance), "d": daily, "t": now},
        )


def _ledger(conn, user_id: int, delta: int, reason: str, balance_after: int,
            ref: Optional[str]) -> None:
    conn.execute(
        text("""INSERT INTO xu_ledger (ts, day, user_id, delta, reason, balance_after, ref)
                VALUES (:ts,:day,:u,:d,:r,:ba,:ref)"""),
        {"ts": int(time.time()), "day": _today(), "u": int(user_id), "d": int(delta),
         "r": reason, "ba": int(balance_after), "ref": ref},
    )


def get_balance(user_id: int) -> int:
    """Số dư xu hiện tại (0 nếu chưa có ví)."""
    with session_scope(service=True) as conn:
        _ensure(conn)
        return _read_balance(conn, user_id)


def recent_ledger(user_id: int, limit: int = 20) -> list[dict]:
    """Sổ cái xu gần đây của 1 user (cho admin xem lịch sử cộng/trừ)."""
    with session_scope(service=True) as conn:
        _ensure(conn)
        rows = conn.execute(
            text("""SELECT ts, day, delta, reason, balance_after, ref FROM xu_ledger
                    WHERE user_id=:u ORDER BY ts DESC LIMIT :n"""),
            {"u": int(user_id), "n": int(limit)},
        ).fetchall()
    return [{"ts": r[0], "day": r[1], "delta": int(r[2]), "reason": r[3],
             "balance_after": int(r[4]), "ref": r[5]} for r in rows]


def admin_adjust(user_id: int, delta: int, reason: str) -> dict:
    """OWNER cộng/trừ xu tay (admin). `delta` ±; số dư KHÔNG xuống dưới 0. Ghi sổ cái
    reason='admin:<reason>'. Trả {balance, delta_applied}. (grant chỉ cộng >0 — đây mới ±.)"""
    delta = int(delta)
    if delta == 0:
        return {"balance": get_balance(user_id), "delta_applied": 0}
    with session_scope(service=True) as conn:
        _ensure(conn)
        _lock(conn, user_id)
        bal = _read_balance(conn, user_id)
        new_bal = max(0, bal + delta)
        applied = new_bal - bal
        _write(conn, user_id, new_bal)
        _ledger(conn, user_id, applied, (f"admin:{reason}")[:120], new_bal, None)
    return {"balance": new_bal, "delta_applied": applied}


def grant(user_id: int, amount: int, reason: str, ref: Optional[str] = None) -> int:
    """Cộng xu (tặng/nạp). Trả số dư mới. amount phải > 0.

    IDEMPOTENT theo `ref` (nếu có): nếu đã tồn tại 1 dòng sổ cái cộng (delta>0) cùng
    (user_id, ref) → KHÔNG cộng lại, trả số dư hiện tại. Bảo vệ webhook RevenueCat
    retry + migration chạy lại không cộng trùng tiền. `ref` nên là id giao dịch
    toàn-cục-duy-nhất (RevenueCat txn) hoặc khoá migration (vd 'migrate:{uid}')."""
    if amount <= 0:
        raise ValueError("grant: amount phải > 0")
    with session_scope(service=True) as conn:
        _ensure(conn)
        _lock(conn, user_id)
        if ref is not None:
            dup = conn.execute(
                text("""SELECT 1 FROM xu_ledger
                        WHERE user_id=:u AND ref=:r AND delta>0 LIMIT 1"""),
                {"u": int(user_id), "r": ref},
            ).fetchone()
            if dup:
                return _read_balance(conn, user_id)   # đã cộng trước đó → no-op
        new = _read_balance(conn, user_id) + int(amount)
        _write(conn, user_id, new)
        _ledger(conn, user_id, int(amount), reason, new, ref)
        return new


def spend(user_id: int, amount: int, reason: str, ref: Optional[str] = None) -> dict:
    """Trừ xu nguyên tử. Trả {ok, balance, need, have}.

    ok=False (reason=insufficient_xu) nếu không đủ — caller mời nạp (KHÔNG ghi sổ).
    Lỗi hạ tầng KHÔNG nuốt (tiền): exception nổi lên → caller coi như chưa tiêu."""
    if amount <= 0:
        raise ValueError("spend: amount phải > 0")
    with session_scope(service=True) as conn:
        _ensure(conn)
        _lock(conn, user_id)
        have = _read_balance(conn, user_id)
        if have < amount:
            return {"ok": False, "balance": have, "need": int(amount), "have": have,
                    "reason": "insufficient_xu"}
        new = have - int(amount)
        _write(conn, user_id, new)
        _ledger(conn, user_id, -int(amount), reason, new, ref)
        return {"ok": True, "balance": new, "need": int(amount), "have": have}


# ── Tặng xu đăng nhập (login bonus) — quyết định THUẦN, mirror AppChat ─────────
def daily_bonus_decision(*, created_at_ms: int, now_ms: int,
                         last_claim_date: Optional[str], today_date: str,
                         bonus_xu: int = DAILY_BONUS_XU,
                         window_days: int = WELCOME_WINDOW_DAYS) -> dict:
    """Có tặng xu đăng nhập hôm nay không (giống dailyBonusDecision phía AppChat):
      • quá cửa sổ welcome → window_over
      • đã tặng hôm nay → already_claimed
      • còn lại → tặng bonus_xu.
    Trả {grant, amount, reason, days_left}."""
    window_end = created_at_ms + window_days * _DAY_MS
    days_left = max(0, -(-(window_end - now_ms) // _DAY_MS))  # ceil division
    if now_ms > window_end:
        return {"grant": False, "amount": 0, "reason": "window_over", "days_left": 0}
    if last_claim_date == today_date:
        return {"grant": False, "amount": 0, "reason": "already_claimed", "days_left": days_left}
    return {"grant": True, "amount": bonus_xu, "reason": "ok", "days_left": days_left}


def claim_daily(user_id: int, *, now_ms: Optional[int] = None) -> dict:
    """Tặng xu đăng nhập 1 lần/ngày (giờ VN) trong cửa sổ welcome kể từ
    users.created_at. Idempotent. Trả {claimed, xu, days_left, reason}."""
    now_ms = now_ms if now_ms is not None else int(time.time() * 1000)
    today = datetime.fromtimestamp(now_ms / 1000, _TZ).strftime("%Y-%m-%d")
    with session_scope(service=True) as conn:
        _ensure(conn)
        _lock(conn, user_id)
        acct = conn.execute(
            text("SELECT created_at FROM users WHERE user_id=:u"), {"u": int(user_id)},
        ).fetchone()
        # users.created_at là epoch GIÂY → ms. Không có tài khoản → coi như mới tạo.
        created_at_ms = int(acct[0]) * 1000 if acct and acct[0] else now_ms
        wrow = conn.execute(
            text("SELECT balance, daily_last_claim FROM xu_wallet WHERE user_id=:u"),
            {"u": int(user_id)},
        ).fetchone()
        cur = int(wrow[0]) if wrow else 0
        last_claim = wrow[1] if wrow else None

        d = daily_bonus_decision(created_at_ms=created_at_ms, now_ms=now_ms,
                                 last_claim_date=last_claim, today_date=today)
        if not d["grant"]:
            return {"claimed": False, "xu": cur, "days_left": d["days_left"],
                    "reason": d["reason"]}
        new = cur + d["amount"]
        _write(conn, user_id, new, daily=today)
        _ledger(conn, user_id, d["amount"], "daily_login_bonus", new, today)
        return {"claimed": True, "xu": new, "days_left": d["days_left"], "reason": "ok"}
