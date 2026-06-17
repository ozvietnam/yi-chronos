"""P0-2c — hồi quy engine/yi_hermes/memory.py sau khi chuyển sang engine.db.

Chạy cùng kịch bản trên 2 backend:
  - sqlite (luôn) — file riêng memory.sqlite3 (non-breaking), FTS5.
  - postgres (gated YI_TEST_PG_DSN) — DB hợp nhất, GIN to_tsvector.
"""
from __future__ import annotations

import os

import pytest
from sqlalchemy import text

import engine.db as db
import engine.yi_hermes.memory as mem

PG_DSN = os.environ.get("YI_TEST_PG_DSN", "").strip()
BACKENDS = ["sqlite"] + (["pg"] if PG_DSN else [])


@pytest.fixture(params=BACKENDS)
def backend(request, tmp_path, monkeypatch):
    if request.param == "sqlite":
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setattr(mem, "_DB_PATH", tmp_path / "memory.sqlite3")
    else:
        monkeypatch.setenv("DATABASE_URL", PG_DSN)
        db.get_engine.cache_clear()
        with db.get_engine().begin() as conn:
            db.apply_schema(conn)
        with db.session_scope(service=True) as conn:
            conn.execute(text("TRUNCATE user_facts, chat_summaries, glossary_views "
                              "RESTART IDENTITY CASCADE"))
    db.get_engine.cache_clear()
    yield request.param
    db.get_engine.cache_clear()


def test_facts_add_list_filter_delete(backend):
    u = "u_facts"
    fid = mem.add_fact(user_id=u, fact="Chuyển việc 2017", category="event")
    assert fid >= 1
    mem.add_fact(user_id=u, fact="Thích ngành công nghệ", category="preference")
    assert len(mem.list_facts(u)) == 2
    assert len(mem.list_facts(u, category="event")) == 1
    # relevance theo query_hint
    top = mem.list_facts(u, limit=1, query_hint="công nghệ")
    assert top[0].category == "preference"
    assert mem.delete_fact(fid) is True
    assert len(mem.list_facts(u)) == 1


def test_summaries_and_fulltext_search(backend):
    u = "u_sum"
    mem.add_summary(user_id=u, summary="Anh quan tâm sự nghiệp và thăng tiến",
                    key_topics=["sự nghiệp"])
    mem.add_summary(user_id=u, summary="Hỏi về hôn nhân tuổi hợp", key_topics=["hôn nhân"])
    assert len(mem.list_summaries(u)) == 2
    assert mem.list_summaries(u)[0].key_topics  # JSON parse đúng (list)
    # full-text: tìm 'nghiệp' → ra bản summary sự nghiệp (FTS5 sqlite / GIN pg)
    hits = mem.search_summaries(u, "nghiệp", limit=5)
    assert any("sự nghiệp" in s.summary for s in hits)


def test_glossary_and_context(backend):
    u = "u_ctx"
    mem.log_glossary_view(u, "Tử Vi")
    mem.log_glossary_view(u, "Tử Vi")
    mem.log_glossary_view(u, "Bát Tự")
    top = dict(mem.top_viewed_terms(u))
    assert top["Tử Vi"] == 2 and top["Bát Tự"] == 1

    mem.add_fact(user_id=u, fact="Sinh 1985", category="event")
    mem.add_summary(user_id=u, summary="Quan tâm sự nghiệp", key_topics=["sự nghiệp"])
    block = mem.build_memory_context(u, query_hint="sự nghiệp")
    assert "Bộ nhớ về user" in block and "Sinh 1985" in block


def test_empty_context_unknown_user(backend):
    assert mem.build_memory_context("nobody_zzz") == ""
