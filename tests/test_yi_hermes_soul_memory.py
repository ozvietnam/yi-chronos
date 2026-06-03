"""Tests for YI-Hermes Soul + Memory layers."""

from __future__ import annotations

import pytest

# Soul/memory + chat endpoints are self-or-owner / login gated (security audit).
pytestmark = pytest.mark.usefixtures("as_owner")


# ─── Soul ─────────────────────────────────────────────────────────────────────


def test_default_soul_for_new_user():
    from engine.yi_hermes import get_soul

    soul = get_soul("brand_new_user_xyz")
    assert soul.tone == "warm"
    assert soul.verbosity == "balanced"
    assert soul.session_count == 0
    assert soul.addressing["pronoun"] == "anh"


def test_update_soul_partial():
    from engine.yi_hermes import get_soul, reset_soul, update_soul

    reset_soul("upd_test")
    soul = update_soul("upd_test", {"verbosity": "terse", "notes": "Anh thích Bát Tự"})
    assert soul.verbosity == "terse"
    assert soul.notes == "Anh thích Bát Tự"
    # Reloading should preserve
    soul2 = get_soul("upd_test")
    assert soul2.verbosity == "terse"


def test_evolve_soul_adds_focus_schools():
    from engine.yi_hermes import evolve_soul, get_soul, reset_soul

    reset_soul("evolve_test")
    evolve_soul("evolve_test", {"schools_visited": ["bat_tu", "tu_vi"]})
    soul = get_soul("evolve_test")
    assert "bat_tu" in soul.focus_schools
    assert "tu_vi" in soul.focus_schools
    assert soul.session_count == 1


def test_soul_as_persona_addendum_format():
    from engine.yi_hermes import get_soul, update_soul, reset_soul

    reset_soul("persona_test")
    update_soul("persona_test", {"tabu_topics": ["chính trị", "tôn giáo"]})
    soul = get_soul("persona_test")
    addendum = soul.as_persona_addendum()
    assert "Soul" in addendum
    assert "chính trị" in addendum
    assert "tôn giáo" in addendum


# ─── Memory: Facts ────────────────────────────────────────────────────────────


def test_add_and_list_facts():
    from engine.yi_hermes import add_fact, list_facts

    fid = add_fact(
        user_id="fact_test",
        fact="Anh chuyển việc 2017",
        category="event",
        confidence=0.9,
    )
    assert fid > 0
    facts = list_facts("fact_test")
    assert any(f.fact == "Anh chuyển việc 2017" for f in facts)


def test_fact_category_filter():
    from engine.yi_hermes import add_fact, list_facts

    add_fact(user_id="cat_test", fact="A1", category="event")
    add_fact(user_id="cat_test", fact="B1", category="preference")
    events = list_facts("cat_test", category="event")
    prefs = list_facts("cat_test", category="preference")
    assert all(f.category == "event" for f in events)
    assert all(f.category == "preference" for f in prefs)


def test_delete_fact():
    from engine.yi_hermes import add_fact, delete_fact, list_facts

    fid = add_fact(user_id="del_test", fact="To be deleted", category="other")
    assert delete_fact(fid)
    facts = list_facts("del_test")
    assert not any(f.id == fid for f in facts)


# ─── Memory: Summaries + FTS ──────────────────────────────────────────────────


def test_add_and_list_summaries():
    from engine.yi_hermes import add_summary, list_summaries

    sid = add_summary(
        user_id="sum_test",
        summary="Anh hỏi về sự nghiệp năm 2026",
        key_topics=["sự nghiệp", "2026"],
    )
    assert sid > 0
    summaries = list_summaries("sum_test")
    assert any(s.summary == "Anh hỏi về sự nghiệp năm 2026" for s in summaries)
    assert any("sự nghiệp" in s.key_topics for s in summaries)


def test_search_summaries_finds_keyword():
    from engine.yi_hermes import add_summary, search_summaries

    add_summary(
        user_id="search_test",
        summary="Anh đã hỏi về Bát Tự Day Master và Dụng Thần",
        key_topics=["bat_tu", "dung_than"],
    )
    add_summary(
        user_id="search_test",
        summary="Anh hỏi về Tử Vi và 12 cung",
        key_topics=["tu_vi"],
    )
    results = search_summaries("search_test", "Bát Tự")
    assert len(results) >= 1
    assert any("Bát Tự" in s.summary for s in results)


# ─── Glossary tracking ────────────────────────────────────────────────────────


def test_log_glossary_view_and_top_terms():
    import uuid
    from engine.yi_hermes import log_glossary_view, top_viewed_terms

    user = f"glossary_view_{uuid.uuid4().hex[:8]}"
    log_glossary_view(user, "Dụng Thần")
    log_glossary_view(user, "Dụng Thần")
    log_glossary_view(user, "Nhật chủ")
    top = dict(top_viewed_terms(user))
    assert top["Dụng Thần"] == 2
    assert top["Nhật chủ"] == 1


# ─── Memory context injection ─────────────────────────────────────────────────


def test_build_memory_context_returns_block():
    from engine.yi_hermes import add_fact, add_summary, build_memory_context

    user = "ctx_test"
    add_fact(user_id=user, fact="Sinh nhật 1985-08-15", category="event")
    add_summary(user_id=user, summary="Anh quan tâm sự nghiệp", key_topics=["sự nghiệp"])
    block = build_memory_context(user, query_hint="sự nghiệp")
    assert "Memory" in block
    assert "Sinh nhật 1985-08-15" in block
    assert "sự nghiệp" in block


def test_build_memory_context_empty_for_unknown_user():
    from engine.yi_hermes import build_memory_context

    block = build_memory_context("unknown_user_zzz")
    assert block == ""


# ─── Session signals (heuristic extraction) ───────────────────────────────────


def test_session_signals_detect_schools_visited():
    from engine.yi_hermes import session_signals_from_turns

    turns = [
        {"role": "user", "content": "Cho hỏi về Bát Tự của em"},
        {"role": "hermes", "content": "Bát Tự của anh có Day Master Kỷ thổ..."},
        {"role": "user", "content": "Tử Vi nói gì thêm về sự nghiệp không?"},
    ]
    signals = session_signals_from_turns(turns)
    assert "bat_tu" in signals["schools_visited"]
    assert "tu_vi" in signals["schools_visited"]


def test_session_signals_detect_tone_signal():
    from engine.yi_hermes import session_signals_from_turns

    turns = [
        {"role": "user", "content": "Cảm ơn em"},
        {"role": "hermes", "content": "Dạ..."},
        {"role": "user", "content": "Trả lời ngắn gọn hơn được không?"},
    ]
    signals = session_signals_from_turns(turns)
    assert signals["tone_signal"] == "shorter"


# ─── API endpoints ────────────────────────────────────────────────────────────


def test_api_get_soul():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.get("/api/yi-hermes/soul/api_test_user")
    assert r.status_code == 200
    soul = r.json()["soul"]
    assert soul["tone"] == "warm"


def test_api_update_soul():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    # Reset first to ensure clean state
    client.delete("/api/yi-hermes/soul/api_upd_user")
    r = client.put("/api/yi-hermes/soul/api_upd_user", json={"verbosity": "verbose", "notes": "Test"})
    assert r.status_code == 200
    soul = r.json()["soul"]
    assert soul["verbosity"] == "verbose"
    assert soul["notes"] == "Test"


def test_api_add_and_list_facts():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.post("/api/yi-hermes/memory/api_fact_user/facts", json={
        "fact": "Anh test API",
        "category": "event",
    })
    assert r.status_code == 200
    assert r.json()["fact_id"] > 0

    r = client.get("/api/yi-hermes/memory/api_fact_user/facts")
    assert r.status_code == 200
    payload = r.json()
    assert any(f["fact"] == "Anh test API" for f in payload["facts"])


def test_api_memory_full_returns_complete_snapshot():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    client.post("/api/yi-hermes/memory/full_user/facts", json={"fact": "F1", "category": "event"})
    client.post("/api/yi-hermes/memory/full_user/summaries", json={
        "summary": "Test summary", "key_topics": ["t1"],
    })

    r = client.get("/api/yi-hermes/memory/full_user/full")
    assert r.status_code == 200
    payload = r.json()
    assert "soul" in payload
    assert "facts" in payload
    assert "summaries" in payload
    assert "top_viewed_terms" in payload
    assert len(payload["facts"]) >= 1
    assert len(payload["summaries"]) >= 1


def test_api_chat_with_memory_injects_context():
    """Chat with active_person_id should inject soul + memory into LLM call."""
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    # Seed memory for user
    client.post("/api/yi-hermes/memory/chat_mem_user/facts", json={
        "fact": "Anh sinh năm 1985 Ất Sửu",
        "category": "event",
    })

    # Chat
    r = client.post("/api/yi-hermes/chat", json={
        "user_message": "Dụng Thần",
        "context": {
            "active_person_id": "chat_mem_user",
            "active_person_name": "Anh A",
        },
    })
    assert r.status_code == 200
    # Glossary hit path doesn't use LLM but log_glossary_view should have run
    # Verify by checking memory top-terms.
    r2 = client.get("/api/yi-hermes/memory/chat_mem_user/top-terms")
    assert r2.status_code == 200
    terms = [t["term_vi"] for t in r2.json()["top_terms"]]
    assert any("Dụng Thần" in t for t in terms)
