"""Tests for YI-Hermes — concierge agent."""

from __future__ import annotations

import pytest

# /api/yi-hermes/chat + glossary write endpoints are login/owner gated.
pytestmark = pytest.mark.usefixtures("as_owner")


# ─── Librarian ────────────────────────────────────────────────────────────────


def test_librarian_lists_7_modules():
    from engine.yi_hermes import get_librarian

    lib = get_librarian()
    modules = lib.list_modules()
    assert len(modules) == 7


def test_librarian_schools_summary():
    from engine.yi_hermes import get_librarian

    sch = get_librarian().schools_summary()
    assert sch["total"] == 7
    assert len(sch["dong"]) == 6
    assert len(sch["tay"]) == 1
    assert "Mai Hoa" in sch["dong"][0] or "Tử Vi" in str(sch["dong"])


def test_librarian_find_by_name():
    from engine.yi_hermes import get_librarian

    results = get_librarian().find_by_name_vi("Tử Vi")
    assert len(results) >= 1
    assert any("Tử Vi" in m.name_vi for m in results)


# ─── Glossary ─────────────────────────────────────────────────────────────────


def test_glossary_seeded_with_core_terms():
    from engine.yi_hermes import get_glossary_store

    store = get_glossary_store()
    assert store.count() >= 50

    # Core terms must exist
    for term in ("Dụng Thần", "Nhật chủ", "Thập Thần", "Hổ quái", "Cung Mệnh"):
        t = store.get(term)
        assert t is not None, f"Missing term: {term}"
        assert t.short_def
        assert t.long_def


def test_glossary_search_fuzzy():
    from engine.yi_hermes import get_glossary_store

    results = get_glossary_store().search("hổ", limit=5)
    assert len(results) >= 1
    # Both Mai Hoa + Liên Hoa have Hổ quái
    names = [r.term_vi for r in results]
    assert any("Hổ" in n for n in names)


def test_glossary_modules_distribution():
    from engine.yi_hermes import get_glossary_store

    dist = get_glossary_store().modules_summary()
    expected = {"bat_tu", "tu_vi", "lien_hoa", "luc_hao", "ha_lac", "mai_hoa", "western", "shared"}
    assert set(dist.keys()) == expected


def test_glossary_upsert_and_delete():
    from engine.yi_hermes import GlossaryTerm, get_glossary_store

    store = get_glossary_store()
    term = GlossaryTerm(
        term_vi="Test Term Xyz",
        term_zh="测试",
        module="shared",
        short_def="Test definition",
        long_def="Longer test definition for unit testing.",
        example="Test example",
        see_also=["Nhật chủ"],
    )
    store.upsert(term)
    assert store.get("Test Term Xyz") is not None

    # Delete
    assert store.delete("Test Term Xyz")
    assert store.get("Test Term Xyz") is None


# ─── Chat engine ──────────────────────────────────────────────────────────────


def test_chat_greeting():
    from engine.yi_hermes import HermesChat, HermesContext

    chat = HermesChat()
    r = chat.send(user_message="chào em", context=HermesContext())
    assert r["intent"] == "greeting"
    assert r["provider"] == "local"
    assert "Hermes" in r["content"]


def test_chat_greeting_with_context():
    from engine.yi_hermes import HermesChat, HermesContext

    chat = HermesChat()
    r = chat.send(
        user_message="hi",
        context=HermesContext(
            active_tab="bat-tu",
            active_person_name="Test Person",
        ),
    )
    assert "Test Person" in r["content"]
    assert "Bát Tự" in r["content"]


def test_chat_glossary_hit_for_known_term():
    from engine.yi_hermes import HermesChat, HermesContext

    chat = HermesChat()
    r = chat.send(user_message="Dụng Thần", context=HermesContext())
    assert r["intent"] == "glossary_hit"
    assert "Dụng Thần" in r["content"]
    assert "Nhật chủ" in r["content"]  # cross-ref


def test_chat_route_to_council_keyword():
    """Council-keyword triggers auto-spawn (legacy `suggest_council` flag removed
    after v2 wiring — now returns council_root_id directly).
    """
    import os, subprocess
    from engine.ai import kanban_council as kc
    from engine.yi_hermes import HermesChat, HermesContext

    chat = HermesChat()
    r = chat.send(
        user_message="Em muốn tranh luận về có nên đổi nghề không?",
        context=HermesContext(),
    )
    try:
        assert r["intent"] == "route_to_council"
        # v2: spawned a real kanban consultation
        assert "council_root_id" in r
        assert r["council_sages"]  # at least one sage selected
    finally:
        # Cleanup the spawned tasks so daemon doesn't actually run them
        env = os.environ.copy()
        env["HERMES_HOME"] = str(kc.HERMES_HOME)
        session = kc.load_session(r["council_root_id"])
        if session:
            for tid in list(session.sage_task_ids.values()) + [session.arbiter_id]:
                subprocess.run(
                    [str(kc.HERMES_BIN), "kanban", "archive", tid],
                    env=env, capture_output=True, text=True,
                )


# ─── API endpoints ────────────────────────────────────────────────────────────


def test_api_yi_hermes_modules():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.get("/api/yi-hermes/modules")
    assert r.status_code == 200
    payload = r.json()
    assert len(payload["modules"]) == 7
    assert payload["summary"]["total"] == 7


def test_api_yi_hermes_glossary_list():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.get("/api/yi-hermes/glossary")
    assert r.status_code == 200
    payload = r.json()
    assert payload["count"] >= 50


def test_api_yi_hermes_glossary_list_by_module():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.get("/api/yi-hermes/glossary?module=bat_tu")
    assert r.status_code == 200
    payload = r.json()
    assert all(t["module"] == "bat_tu" for t in payload["terms"])


def test_api_yi_hermes_glossary_search():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.get("/api/yi-hermes/glossary/search?q=Nhật")
    assert r.status_code == 200
    payload = r.json()
    assert payload["count"] >= 1
    assert any("Nhật" in t["term_vi"] for t in payload["terms"])


def test_api_yi_hermes_glossary_term_lookup():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    # URL-encoded "Dụng Thần"
    import urllib.parse
    encoded = urllib.parse.quote("Dụng Thần")
    r = client.get(f"/api/yi-hermes/glossary/term/{encoded}")
    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "ok"
    assert payload["term"]["term_vi"] == "Dụng Thần"


def test_api_yi_hermes_chat_greeting():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.post("/api/yi-hermes/chat", json={
        "user_message": "chào em",
        "context": {"active_tab": "bat-tu"},
    })
    assert r.status_code == 200
    payload = r.json()
    assert payload["response"]["intent"] == "greeting"


def test_api_yi_hermes_chat_term_lookup():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.post("/api/yi-hermes/chat", json={
        "user_message": "Cách Cục",
    })
    assert r.status_code == 200
    payload = r.json()
    assert payload["response"]["intent"] == "glossary_hit"
