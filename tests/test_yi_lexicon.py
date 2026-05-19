"""Tests for engine.yi_lexicon — store, parser, ingestion stub, distill stub."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolated_db(monkeypatch, tmp_path):
    """Isolate lexicon DB per test."""
    tmp_db = tmp_path / "lexicon.sqlite3"
    monkeypatch.setattr("engine.yi_lexicon.store._DB_PATH", tmp_db)
    yield


# ─── Schema + CRUD ──────────────────────────────────────────────────────────


def test_bootstrap_creates_tables():
    from engine.yi_lexicon import stats
    s = stats()
    assert s["concepts"] == 0
    assert s["mappings"] == 0


def test_add_and_get_concept():
    from engine.yi_lexicon import add_concept, get_concept

    c = add_concept(
        canonical_vi="lá",
        canonical_zh="葉", canonical_en="leaf",
        concept_type="object",
        aliases=["lá cây"],
        schools=["mai_hoa", "common"],
        confidence=0.95,
    )
    assert c.concept_id is not None
    assert c.canonical_vi == "lá"
    assert "lá cây" in c.aliases

    fetched = get_concept(canonical_vi="lá")
    assert fetched is not None and fetched.concept_id == c.concept_id


def test_add_concept_idempotent_on_duplicate():
    from engine.yi_lexicon import add_concept

    c1 = add_concept(canonical_vi="dương", concept_type="concept")
    c2 = add_concept(canonical_vi="dương", concept_type="concept")
    assert c1.concept_id == c2.concept_id


def test_add_mapping():
    from engine.yi_lexicon import add_concept, add_mapping, mappings_for

    c = add_concept(canonical_vi="lá", concept_type="object")
    m = add_mapping(c.concept_id, "ngu_hanh", "mộc",
                    reasoning_vi="Lá là phần của cây", confidence=0.9)
    assert m.mapping_id is not None

    mappings = mappings_for(c.concept_id)
    assert len(mappings) == 1
    assert mappings[0].dim_value == "mộc"


def test_reverse_lookup():
    from engine.yi_lexicon import add_concept, add_mapping, reverse_lookup_concepts

    for name in ["lá", "hoa", "cỏ"]:
        c = add_concept(canonical_vi=name, concept_type="object")
        add_mapping(c.concept_id, "ngu_hanh", "mộc")

    hits = reverse_lookup_concepts("ngu_hanh", "mộc")
    assert len(hits) == 3
    assert {c.canonical_vi for c in hits} == {"lá", "hoa", "cỏ"}


def test_search_concepts_fts():
    from engine.yi_lexicon import add_concept, search_concepts

    add_concept(canonical_vi="lá rơi", concept_type="phenomenon")
    add_concept(canonical_vi="hoa nở", concept_type="phenomenon")
    add_concept(canonical_vi="lá xanh", concept_type="object")

    hits = search_concepts("lá")
    assert len(hits) >= 2
    assert any("lá" in h.canonical_vi for h in hits)


def test_search_schools_filter():
    from engine.yi_lexicon import add_concept, search_concepts

    add_concept(canonical_vi="quẻ Càn", concept_type="symbol",
                schools=["mai_hoa"])
    add_concept(canonical_vi="Day Master", concept_type="concept",
                schools=["bat_tu"])

    mai_hoa_hits = search_concepts("Càn", schools=["mai_hoa"])
    assert any("Càn" in h.canonical_vi for h in mai_hoa_hits)


# ─── Core seed ───────────────────────────────────────────────────────────────


def test_seed_all_loads_bedrock():
    from engine.yi_lexicon.core_seed import seed_all

    result = seed_all()
    assert result["concepts"] >= 50    # 5 hành × 5 dims + 8 quẻ + 10 can + 12 chi + ...
    assert result["mappings"] >= 100
    # Some core dim types should be populated
    assert "ngu_hanh" in result["mappings_by_dim"]
    assert "bat_quai" in result["mappings_by_dim"]


def test_seed_8_bat_quai():
    from engine.yi_lexicon import reverse_lookup_concepts
    from engine.yi_lexicon.core_seed import seed_all

    seed_all()
    # Each of the 8 trigrams should be discoverable
    for trigram in ("Càn", "Khôn", "Chấn", "Tốn", "Khảm", "Ly", "Cấn", "Đoài"):
        hits = reverse_lookup_concepts("bat_quai", trigram)
        assert hits, f"No concept maps to bat_quai={trigram}"


def test_seed_5_ngu_hanh_each_has_color():
    from engine.yi_lexicon import reverse_lookup_concepts
    from engine.yi_lexicon.core_seed import seed_all

    seed_all()
    for elem in ("mộc", "hỏa", "thổ", "kim", "thủy"):
        hits = reverse_lookup_concepts("ngu_hanh", elem)
        assert any(h.concept_type == "color" for h in hits), (
            f"{elem} has no color concept"
        )


# ─── Parser ──────────────────────────────────────────────────────────────────


def test_parser_extracts_numbers_arabic_and_vi():
    from engine.yi_lexicon.parser import _extract_numbers

    assert _extract_numbers("9h sáng 2 lá") == [9, 2]
    assert 2 in _extract_numbers("hai chiếc lá rơi")
    # Combined
    nums = _extract_numbers("3h sáng có hai cốc nước")
    assert 3 in nums and 2 in nums


def test_parser_extracts_time():
    from engine.yi_lexicon.parser import _extract_time

    assert "9h" in _extract_time("9h sáng đi làm").lower()
    assert _extract_time("không có giờ") is None


def test_interpret_observation_full_pipeline():
    """The flagship anh-example: 9h sáng 2 lá rơi"""
    from engine.yi_lexicon.core_seed import seed_all
    from engine.yi_lexicon.parser import interpret_observation

    seed_all()
    ctx = interpret_observation("9h sáng em ra đường gặp hai chiếc lá rơi")
    assert ctx.numbers_extracted == [9, 2]
    assert ctx.time_context is not None and "9h" in ctx.time_context
    # Lexicon should match lá + rơi + sáng + đường + gặp
    matched_vis = {t.canonical_vi for t in ctx.tokens}
    assert "lá" in matched_vis
    assert "rơi" in matched_vis
    # Mai Hoa candidate should be computed
    assert ctx.mai_hoa_candidate is not None
    assert ctx.mai_hoa_candidate["upper_quai"] in (
        "Càn", "Đoài", "Ly", "Chấn", "Tốn", "Khảm", "Cấn", "Khôn"
    )
    # Dimensions should be populated
    assert "mộc" in ctx.ngu_hanh_distribution
    # Narrative should reference findings
    assert "Phát hiện" in ctx.narrative_summary


def test_interpret_handles_empty_text():
    from engine.yi_lexicon.parser import interpret_observation

    ctx = interpret_observation("")
    assert ctx.tokens == []
    assert ctx.numbers_extracted == []


# ─── Distill queue ───────────────────────────────────────────────────────────


def test_distill_queue_default_auto_accepted():
    from engine.yi_lexicon import add_distill_item, get_distill_queue

    item = add_distill_item(
        kind="new_concept",
        payload={"canonical_vi": "xe đạp", "concept_type": "object"},
        source="council:test",
        confidence=0.7,
    )
    assert item.status == "auto_accepted"

    queue = get_distill_queue(status="auto_accepted")
    assert any(i.item_id == item.item_id for i in queue)


def test_resolve_distill_item():
    from engine.yi_lexicon import add_distill_item, get_distill_queue, resolve_distill_item

    item = add_distill_item(
        kind="new_concept",
        payload={"canonical_vi": "test"},
        source="council:test",
    )
    ok = resolve_distill_item(item.item_id, status="approved", reviewer_note="anh OK")
    assert ok

    queue = get_distill_queue(status="approved")
    assert any(i.item_id == item.item_id for i in queue)


def test_resolve_distill_rejects_invalid_status():
    from engine.yi_lexicon import resolve_distill_item

    with pytest.raises(ValueError):
        resolve_distill_item(1, status="maybe")


# ─── API integration ─────────────────────────────────────────────────────────


def test_api_lexicon_stats():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.get("/api/yi-lexicon/stats")
    assert r.status_code == 200
    assert "concepts" in r.json()["stats"]


def test_api_interpret_anh_example():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    # lifespan auto-seeds — but tests use isolated DB, so manually seed first
    from engine.yi_lexicon.core_seed import seed_all
    seed_all()

    r = client.post("/api/yi-lexicon/interpret", json={
        "text": "9h sáng em gặp hai chiếc lá rơi",
    })
    assert r.status_code == 200
    ctx = r.json()["context"]
    assert ctx["numbers_extracted"] == [9, 2]
    assert ctx["mai_hoa_candidate"] is not None


def test_api_concept_crud():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.post("/api/yi-lexicon/concepts", json={
        "canonical_vi": "máy bay",
        "concept_type": "object",
        "schools": ["common"],
    })
    assert r.status_code == 200
    cid = r.json()["concept"]["concept_id"]

    r2 = client.post("/api/yi-lexicon/mappings", json={
        "concept_id": cid, "dim_type": "ngu_hanh", "dim_value": "kim",
        "reasoning_vi": "Máy bay là máy móc kim loại",
    })
    assert r2.status_code == 200

    r3 = client.get(f"/api/yi-lexicon/concepts/{cid}")
    assert len(r3.json()["mappings"]) == 1


def test_api_reverse_lookup():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    from engine.yi_lexicon.core_seed import seed_all
    seed_all()

    r = client.get("/api/yi-lexicon/reverse-lookup?dim_type=ngu_hanh&dim_value=mộc")
    assert r.status_code == 200
    results = r.json()["results"]
    assert len(results) > 0
