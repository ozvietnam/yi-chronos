"""ADR 3-tầng (task 2) — system_meta + knowledge_version (T1 versioning)."""
import pytest

from engine.db import get_engine


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/meta.sqlite3")
    get_engine.cache_clear()
    yield
    get_engine.cache_clear()


def test_knowledge_version_default_is_1(temp_db):
    from engine import system_meta as sm
    assert sm.get_knowledge_version() == 1


def test_bump_knowledge_version_increments(temp_db):
    from engine import system_meta as sm
    assert sm.bump_knowledge_version() == 2
    assert sm.bump_knowledge_version() == 3
    assert sm.get_knowledge_version() == 3


def test_meta_set_get_upsert(temp_db):
    from engine import system_meta as sm
    assert sm.get_meta("k_x", "fallback") == "fallback"   # default khi chưa có
    sm.set_meta("k_x", "v1")
    assert sm.get_meta("k_x") == "v1"
    sm.set_meta("k_x", "v2")                                # upsert
    assert sm.get_meta("k_x") == "v2"


def test_profile_schema_version_default(temp_db):
    from engine import system_meta as sm
    assert sm.get_profile_schema_version() == 1


# ─── wiring evolve_gate.review → bump knowledge_version (ADR §3) ─────────────

def test_evolve_approve_high_impact_bumps_version(temp_db):
    from engine import evolve_gate, system_meta as sm
    p = evolve_gate.submit_proposal(kind="new_book", payload={"x": 1},
                                    confidence=0.9, impact="high", title="Sách mới")
    assert p["status"] == "pending"          # high luôn cần Anh duyệt
    before = sm.get_knowledge_version()
    r = evolve_gate.review(p["id"], approve=True, reviewer="founder")
    assert r["status"] == "approved"
    assert r.get("knowledge_version") == before + 1
    assert sm.get_knowledge_version() == before + 1


def test_evolve_approve_low_impact_no_bump(temp_db):
    from engine import evolve_gate, system_meta as sm
    p = evolve_gate.submit_proposal(kind="skill_tweak", payload={},
                                    confidence=0.5, impact="low")
    assert p["status"] == "pending"          # low-confidence → pending
    before = sm.get_knowledge_version()
    r = evolve_gate.review(p["id"], approve=True, reviewer="founder")
    assert r["status"] == "approved" and "knowledge_version" not in r
    assert sm.get_knowledge_version() == before   # low-impact KHÔNG bump


def test_evolve_reject_no_bump(temp_db):
    from engine import evolve_gate, system_meta as sm
    p = evolve_gate.submit_proposal(kind="new_book", payload={},
                                    confidence=0.9, impact="high")
    before = sm.get_knowledge_version()
    r = evolve_gate.review(p["id"], approve=False, reviewer="founder")
    assert r["status"] == "rejected"
    assert sm.get_knowledge_version() == before   # reject KHÔNG bump


def test_cache_t3_invalidated_by_knowledge_bump(temp_db):
    """ADR §8 acceptance: bump knowledge_version ⇒ cache T3 cũ MISS ⇒ luận lại."""
    import time
    from sqlalchemy import text
    from engine.db import session_scope
    from engine import hermes_service, system_meta as sm
    from api import sync
    sync._ensure_schema()                       # tạo user_castings trong temp db
    uid, method, q = 999, "hermes_quick", "Câu test cache versioning"
    now = int(time.time())
    with session_scope(service=True) as conn:
        conn.execute(text(
            """INSERT INTO user_castings (user_id, method, subject_person_key, question,
                   result_json, verdict, tags, note, algo_version, created_at)
               VALUES (:u,:m,'self',:q,'{}',NULL,'quick',NULL,'v1',:t)"""),
            {"u": uid, "m": method, "q": q, "t": now - 100})
    cid, _ = hermes_service._cached(uid, method, q)
    assert cid is not None                      # HIT (trong TTL, chưa bump)
    sm.bump_knowledge_version()                 # set knowledge_version.updated_at = now
    cid2, _ = hermes_service._cached(uid, method, q)
    assert cid2 is None                         # MISS (entry tạo trước mốc bump)
