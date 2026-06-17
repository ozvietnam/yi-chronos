"""P0-5 — LLM spend ledger + hard-stop ngân sách (chống đốt tiền LLM ở 20M).

Master plan: "theo dõi chi phí LLM realtime + ngắt khi vượt ngân sách". Mỗi lần
gọi LLM ghi 1 dòng (provider/feature/model/tokens/cost). Trước khi gọi LLM, code
check `over_daily_budget()` → nếu vượt → rớt về self-host/free hoặc từ chối.

Dual-driver (engine.db). Bảng llm_spend là ops/aggregate (không per-user nhạy cảm)
→ truy cập service-mode, không bật RLS. DDL portable (chạy cả SQLite lẫn Postgres).
"""
from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

# Ngân sách + dashboard tính theo NGÀY LOCAL Việt Nam (UTC+7), không phải UTC —
# nếu dùng UTC thì "ngày" rollover lúc 07:00 giờ VN, lệch mental-model của ops.
_TZ = ZoneInfo("Asia/Ho_Chi_Minh")

from sqlalchemy import text

from engine.db import session_scope

_DDL = """
CREATE TABLE IF NOT EXISTS llm_spend (
    ts          BIGINT NOT NULL,
    day         TEXT NOT NULL,
    provider    TEXT NOT NULL,
    feature     TEXT,
    model       TEXT,
    tokens_in   INTEGER DEFAULT 0,
    tokens_out  INTEGER DEFAULT 0,
    cost_usd    REAL DEFAULT 0,
    user_id     TEXT
)
"""
_DDL_IDX = "CREATE INDEX IF NOT EXISTS idx_llm_spend_day ON llm_spend(day)"


def _ensure(conn) -> None:
    conn.execute(text(_DDL))
    conn.execute(text(_DDL_IDX))


def _today() -> str:
    return datetime.now(_TZ).strftime("%Y-%m-%d")


def record_spend(*, provider: str, cost_usd: float, feature: str = "",
                 model: str = "", tokens_in: int = 0, tokens_out: int = 0,
                 user_id: Optional[str] = None) -> None:
    """Ghi 1 lần gọi LLM. Nuốt lỗi — đo chi phí không được làm hỏng request."""
    try:
        with session_scope(service=True) as conn:
            _ensure(conn)
            conn.execute(
                text("""INSERT INTO llm_spend
                        (ts, day, provider, feature, model, tokens_in, tokens_out, cost_usd, user_id)
                        VALUES (:ts,:day,:prov,:feat,:model,:ti,:to,:cost,:uid)"""),
                {"ts": int(time.time()), "day": _today(), "prov": provider,
                 "feat": feature, "model": model, "ti": tokens_in, "to": tokens_out,
                 "cost": float(cost_usd), "uid": user_id},
            )
    except Exception:
        pass


def day_total(day: Optional[str] = None) -> float:
    """Tổng chi phí USD trong ngày (mặc định hôm nay, giờ VN)."""
    day = day or _today()
    with session_scope(service=True) as conn:
        _ensure(conn)
        v = conn.execute(
            text("SELECT COALESCE(SUM(cost_usd),0) FROM llm_spend WHERE day=:d"),
            {"d": day},
        ).scalar()
    return float(v or 0.0)


def daily_budget_usd() -> float:
    """Ngân sách LLM/ngày (env LLM_DAILY_BUDGET_USD; mặc định 50 USD)."""
    try:
        return float(os.environ.get("LLM_DAILY_BUDGET_USD", "50"))
    except ValueError:
        return 50.0


def over_daily_budget() -> bool:
    """True nếu chi hôm nay ≥ ngân sách → caller rớt về self-host/free hoặc từ chối."""
    return day_total() >= daily_budget_usd()


def spend_summary(day: Optional[str] = None) -> dict:
    """Tóm tắt cho dashboard/observability: tổng + breakdown theo provider."""
    day = day or _today()
    with session_scope(service=True) as conn:
        _ensure(conn)
        rows = conn.execute(
            text("""SELECT provider, COUNT(*), COALESCE(SUM(cost_usd),0)
                    FROM llm_spend WHERE day=:d GROUP BY provider"""),
            {"d": day},
        ).fetchall()
    by_provider = {r[0]: {"calls": r[1], "cost_usd": round(float(r[2]), 4)} for r in rows}
    total = round(sum(p["cost_usd"] for p in by_provider.values()), 4)
    budget = daily_budget_usd()
    return {
        "day": day, "total_usd": total, "budget_usd": budget,
        "over_budget": total >= budget, "by_provider": by_provider,
    }
