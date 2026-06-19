"""#41 G1 verify — boot toàn bộ schema dual-driver + CRUD round-trip trên Postgres THẬT.

Bắt mọi SQLite-ism (AUTOINCREMENT, INSERT OR REPLACE, strftime, ? placeholder...) sẽ
nổ trên Postgres. Chạy với Postgres Docker:
    DATABASE_URL='postgresql+psycopg://postgres:yi@localhost:55432/yitest' \\
        .venv/bin/python3 scripts/verify_postgres_boot.py
"""
import os
import sys
import traceback

assert os.environ.get("DATABASE_URL", "").startswith("postgresql"), "Cần DATABASE_URL Postgres"

from engine.db import get_engine, is_postgres
get_engine.cache_clear()
assert is_postgres(), "is_postgres() phải True"

results = []


def check(name, fn):
    try:
        fn()
        results.append((name, "OK", ""))
    except Exception as e:
        results.append((name, "FAIL", f"{type(e).__name__}: {e}"))
        traceback.print_exc()


# 1) Schema chính (users/persons/castings/feedback/quick_job_results…)
def _sync_schema():
    from api import sync
    sync._ensure_schema()
check("sync._ensure_schema (user tables)", _sync_schema)


# 2) system_meta (ADR T1 — knowledge_version)
def _system_meta():
    from engine import system_meta
    v0 = system_meta.get_knowledge_version()
    v1 = system_meta.bump_knowledge_version()
    assert v1 == v0 + 1, f"bump {v0}->{v1}"
    system_meta.set_meta("probe_pg", "xin chào")
    assert system_meta.get_meta("probe_pg") == "xin chào"
check("system_meta (knowledge_version + set/get upsert)", _system_meta)


# 3) llm_spend (ngân sách — try_charge/record_spend)
def _llm_spend():
    from engine import llm_spend
    llm_spend.record_spend(provider="probe", cost_usd=0.01, feature="probe", model="m", user_id="1")
    s = llm_spend.spend_summary()
    assert isinstance(s, dict)
check("llm_spend (record_spend + summary)", _llm_spend)


# 4) ratelimit (token-bucket — Redis hoặc in-memory/DB fallback)
def _ratelimit():
    from engine import ratelimit
    ratelimit.allow("probe_pg:1", 5, 86400)
check("ratelimit.allow", _ratelimit)


# 5) menh_profile (ADR T2 — bảng user_menh_profile)
def _menh_profile():
    from engine import menh_profile
    got = menh_profile.get_profile(99999)   # chưa có → None, nhưng bảng phải tạo + query chạy
    assert got is None
check("menh_profile (get_profile + table DDL)", _menh_profile)


print("\n" + "=" * 60)
ok = sum(1 for _, s, _ in results if s == "OK")
for name, status, err in results:
    mark = "✓" if status == "OK" else "✗"
    print(f"  {mark} {name}: {status}" + (f" — {err}" if err else ""))
print(f"\n  {ok}/{len(results)} module chạy sạch trên Postgres")
sys.exit(0 if ok == len(results) else 1)
