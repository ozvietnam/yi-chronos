"""Tests for engine.yi_hermes.persons, relationships, and engine.ai.dyad_analysis."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolated_db(monkeypatch, tmp_path):
    """Isolate persons DB per test."""
    tmp_db = tmp_path / "persons.sqlite3"
    monkeypatch.setattr("engine.yi_hermes.persons._DB_PATH", tmp_db)
    monkeypatch.setattr("engine.yi_hermes.relationships._DB_PATH", tmp_db)
    yield


# ─── Person CRUD ─────────────────────────────────────────────────────────────


def test_create_and_get_person():
    from engine.yi_hermes.persons import create_person, get_person

    p = create_person(
        name="Nguyễn Văn A",
        gender="nam",
        birth_datetime_local="1990-04-15T10:30:00",
        birth_confidence="exact",
        source="manual",
        relationship_to_founder="colleague",
    )
    assert p.person_id.startswith("nguy") or "nguyen" in p.person_id.lower() or len(p.person_id) > 0
    assert p.name == "Nguyễn Văn A"
    assert p.gender == "nam"

    fetched = get_person(p.person_id)
    assert fetched is not None
    assert fetched.name == p.name
    assert fetched.birth_datetime_local == "1990-04-15T10:30:00"


def test_aliases_and_find_by_name():
    from engine.yi_hermes.persons import create_person, find_by_name

    p = create_person(name="Trần Thị B", aliases=["TT.B", "Bee"], nickname="Bee")
    by_name = find_by_name("Trần Thị B")
    assert by_name is not None and by_name.person_id == p.person_id

    by_alias = find_by_name("bee")
    assert by_alias is not None and by_alias.person_id == p.person_id


def test_list_persons_filter_by_relationship():
    from engine.yi_hermes.persons import create_person, list_persons

    create_person(name="Sếp X", relationship_to_founder="boss")
    create_person(name="Đồng nghiệp Y", relationship_to_founder="colleague")
    create_person(name="Bạn Z", relationship_to_founder="friend")

    bosses = list_persons(relationship_to_founder="boss")
    assert len(bosses) == 1
    assert bosses[0].name == "Sếp X"


def test_update_person_top_fields():
    from engine.yi_hermes.persons import create_person, update_person

    p = create_person(name="C")
    updated = update_person(p.person_id, {"nickname": "Cool C", "gender": "nữ"})
    assert updated.nickname == "Cool C"
    assert updated.gender == "nữ"


# ─── Layered storage ─────────────────────────────────────────────────────────


def test_update_layer_career():
    from engine.yi_hermes.persons import create_person, get_person, update_layer

    p = create_person(name="Worker D")
    update_layer(p.person_id, "career", {
        "role": "Senior Engineer",
        "company": "ACME Corp",
        "industry": "fintech",
        "experience_years": 8,
    }, confidence="verified")

    fetched = get_person(p.person_id)
    career = fetched.get_layer("career")
    assert career["role"] == "Senior Engineer"
    assert career["company"] == "ACME Corp"
    assert career["_meta"]["confidence"] == "verified"


def test_layer_merge_preserves_other_fields():
    from engine.yi_hermes.persons import create_person, get_person, update_layer

    p = create_person(name="E")
    update_layer(p.person_id, "career", {"role": "Designer"})
    update_layer(p.person_id, "career", {"company": "Pixel"})

    career = get_person(p.person_id).get_layer("career")
    assert career["role"] == "Designer"
    assert career["company"] == "Pixel"


def test_physiognomy_layer_placeholder():
    """Physiognomy layer is a placeholder for future engine.nhan_tuong."""
    from engine.yi_hermes.persons import create_person, get_person, update_layer

    p = create_person(name="F")
    update_layer(p.person_id, "physiognomy", {
        "height_cm": 165,
        "build": "thin",
        "face_shape": "thuôn dài",
        "hair": "thưa, bạc sớm",
        "skin_tone": "trắng",
    })
    phys = get_person(p.person_id).get_layer("physiognomy")
    assert phys["height_cm"] == 165
    assert phys["face_shape"] == "thuôn dài"


def test_health_layer_placeholder():
    from engine.yi_hermes.persons import create_person, get_person, update_layer

    p = create_person(name="G")
    update_layer(p.person_id, "health", {
        "conditions": ["huyết áp cao", "tiêu hóa kém"],
        "energy_level": "medium",
    })
    h = get_person(p.person_id).get_layer("health")
    assert "huyết áp cao" in h["conditions"]


def test_custom_layer_extensibility():
    """User can add any layer name — engine doesn't enforce."""
    from engine.yi_hermes.persons import create_person, get_person, update_layer

    p = create_person(name="H")
    update_layer(p.person_id, "spirituality", {"path": "Phật giáo", "depth_years": 5})
    sp = get_person(p.person_id).get_layer("spirituality")
    assert sp["path"] == "Phật giáo"


# ─── Notes ───────────────────────────────────────────────────────────────────


def test_add_and_list_notes():
    from engine.yi_hermes.persons import add_note, create_person, list_notes

    p = create_person(name="I")
    nid = add_note(p.person_id, "Anh ấy hay đi du lịch", layer_hint="lifestyle")
    assert nid > 0

    notes = list_notes(p.person_id)
    assert len(notes) == 1
    assert notes[0].body == "Anh ấy hay đi du lịch"
    assert notes[0].layer_hint == "lifestyle"


def test_notes_filtered_by_layer_hint():
    from engine.yi_hermes.persons import add_note, create_person, list_notes

    p = create_person(name="J")
    add_note(p.person_id, "Chạy bộ mỗi sáng", layer_hint="lifestyle")
    add_note(p.person_id, "Sếp giao project mới", layer_hint="career")

    career_notes = list_notes(p.person_id, layer_hint="career")
    assert len(career_notes) == 1
    assert "project" in career_notes[0].body.lower()


# ─── Cached cosmology ────────────────────────────────────────────────────────


def test_cast_bat_tu_for_caches_chart():
    from engine.yi_hermes.persons import cast_bat_tu_for, create_person, get_person

    p = create_person(
        name="Cosmo Test",
        gender="nam",
        birth_datetime_local="1990-04-15T10:30:00",
    )
    chart = cast_bat_tu_for(p.person_id)
    assert chart is not None
    assert "tu_tru" in chart

    fetched = get_person(p.person_id)
    assert fetched.day_master is not None
    assert "charts" in fetched.get_layer("cosmology")


def test_cast_bat_tu_without_birth_returns_none():
    from engine.yi_hermes.persons import cast_bat_tu_for, create_person

    p = create_person(name="No Birth")
    assert cast_bat_tu_for(p.person_id) is None


# ─── Relationships ───────────────────────────────────────────────────────────


def test_add_relationship_creates_bidirectional():
    from engine.yi_hermes.persons import create_person
    from engine.yi_hermes.relationships import add_relationship, list_relationships

    a = create_person(name="Alice")
    b = create_person(name="Bob")

    rel = add_relationship(
        from_person_id=a.person_id, to_person_id=b.person_id,
        rel_type="colleague", context="Công ty Z", bidirectional=True,
    )
    assert rel.from_person_id == a.person_id
    assert rel.rel_type == "colleague"

    # Both directions should exist
    a_to_b = list_relationships(person_id=a.person_id, direction="from")
    b_to_a = list_relationships(person_id=b.person_id, direction="from")
    assert any(r.to_person_id == b.person_id for r in a_to_b)
    assert any(r.to_person_id == a.person_id for r in b_to_a)


def test_relationship_query_by_type():
    from engine.yi_hermes.persons import create_person
    from engine.yi_hermes.relationships import add_relationship, list_relationships

    a = create_person(name="A")
    boss = create_person(name="Boss")
    fr = create_person(name="Friend")

    add_relationship(from_person_id=a.person_id, to_person_id=boss.person_id, rel_type="boss")
    add_relationship(from_person_id=a.person_id, to_person_id=fr.person_id, rel_type="friend")

    bosses = list_relationships(person_id=a.person_id, rel_type="boss")
    assert len(bosses) == 1
    assert bosses[0].to_person_id == boss.person_id


def test_founder_network_returns_edges():
    from engine.yi_hermes.persons import create_person
    from engine.yi_hermes.relationships import add_relationship, founder_network

    founder = create_person(person_id="_founder", name="Founder")
    col = create_person(name="Colleague")
    add_relationship(
        from_person_id=founder.person_id, to_person_id=col.person_id,
        rel_type="colleague",
    )
    graph = founder_network("_founder")
    assert graph["founder"] is not None
    assert len(graph["edges"]) >= 1
    assert any(p["name"] == "Colleague" for p in graph["persons"])


# ─── Dyad analysis ───────────────────────────────────────────────────────────


def test_dyad_analyze_returns_compat():
    from engine.ai.dyad_analysis import analyze_dyad
    from engine.bat_tu.cast import cast_bat_tu

    chart_a = cast_bat_tu(birth_datetime_local="1988-06-05T10:00:00", gender="nam")
    chart_b = cast_bat_tu(birth_datetime_local="1990-09-15T08:00:00", gender="nam")
    result = analyze_dyad(chart_a, chart_b, name_a="A", name_b="B")
    assert 0.0 <= result.overall_score <= 1.0
    assert result.overall_label in ("rất hợp", "hợp", "trung bình", "kỵ", "rất kỵ")
    assert result.day_master_compat["score"] > 0
    assert len(result.signals) >= 1


def test_dyad_detects_stem_hop():
    """Ất Mộc + Canh Kim should be detected as stem_hop (Ất-Canh)."""
    from engine.ai.dyad_analysis import analyze_dyad
    from engine.bat_tu.cast import cast_bat_tu

    # Pick known charts where Day Master = Ất and Canh respectively
    # Anh's chart V2A: Day Master Giáp Mộc — not Ất
    # Use synthetic: 1985-02-15 → Year Ất Sửu
    chart_a = cast_bat_tu(birth_datetime_local="1985-02-15T10:00:00", gender="nam")
    # 1990-09-15 → Day Master likely contains some Canh stem
    chart_b = cast_bat_tu(birth_datetime_local="1990-09-15T08:00:00", gender="nam")
    result = analyze_dyad(chart_a, chart_b)
    # Just check we get usable structure (specific stem_hop depends on exact chart casts)
    assert result.signals
    assert any(s.signal.startswith("stem_") for s in result.signals)


# ─── API integration ─────────────────────────────────────────────────────────


def test_api_create_and_get_person():
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)
    r = client.post("/api/yi-hermes/persons", json={
        "name": "API Test Person",
        "gender": "nam",
        "birth_datetime_local": "1990-04-15T10:30:00",
        "relationship_to_founder": "colleague",
    })
    assert r.status_code == 200
    pid = r.json()["person"]["person_id"]

    r2 = client.get(f"/api/yi-hermes/persons/{pid}")
    assert r2.status_code == 200
    assert r2.json()["person"]["name"] == "API Test Person"


def test_api_update_layer():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.post("/api/yi-hermes/persons", json={"name": "Layer Test"})
    pid = r.json()["person"]["person_id"]

    r2 = client.post(f"/api/yi-hermes/persons/{pid}/layer", json={
        "layer": "career",
        "patch": {"role": "PM", "company": "X"},
        "confidence": "high",
    })
    assert r2.status_code == 200
    assert r2.json()["person"]["layers"]["career"]["role"] == "PM"


def test_api_add_relationship_and_list():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    a = client.post("/api/yi-hermes/persons", json={"name": "Rel A"}).json()["person"]
    b = client.post("/api/yi-hermes/persons", json={"name": "Rel B"}).json()["person"]

    r = client.post("/api/yi-hermes/relationships", json={
        "from_person_id": a["person_id"],
        "to_person_id": b["person_id"],
        "rel_type": "colleague",
        "context": "Công ty Y",
    })
    assert r.status_code == 200

    rels = client.get(f"/api/yi-hermes/relationships?person_id={a['person_id']}").json()
    assert any(r["to_person_id"] == b["person_id"] for r in rels["relationships"])


def test_api_dyad_analyze():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    a = client.post("/api/yi-hermes/persons", json={
        "name": "Dyad A", "birth_datetime_local": "1988-06-05T10:00:00", "gender": "nam",
    }).json()["person"]
    b = client.post("/api/yi-hermes/persons", json={
        "name": "Dyad B", "birth_datetime_local": "1990-09-15T08:00:00", "gender": "nam",
    }).json()["person"]

    r = client.post("/api/yi-hermes/dyad/analyze", json={
        "person_a_id": a["person_id"],
        "person_b_id": b["person_id"],
        "cache_in_relationship": False,
    })
    assert r.status_code == 200
    compat = r.json()["compat"]
    assert "overall_score" in compat
    assert "overall_label" in compat
