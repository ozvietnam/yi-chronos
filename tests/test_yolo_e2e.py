"""YOLO E2E — vòng đời ĐẦY ĐỦ của YOLO mode (Lexicon ingest → merge → duyệt).

YOLO mode (2026-05-12): LLM extract concept/mapping từ corpus → AUTO-MERGE
vào lexicon TRƯỚC, anh duyệt SAU qua distill queue. Trước v3, reject chỉ đổi
status — dữ liệu đã merge vẫn nằm nguyên trong lexicon (vòng KHÔNG khép).

v3 đóng vòng end-to-end:
  1. register_corpus → ingest_corpus (LLM fake) → _merge_extracted auto-merge
  2. distill_queue item 'auto_accepted' mang payload._merged (ownership:
     concept_id + concept_created + mapping_ids do merge này tạo)
  3. REJECT  → ROLLBACK: gỡ mappings; gỡ concept nếu do item tạo + mồ côi
  4. APPROVE → mark verified_by_anh=1 cho mappings của item
  5. Ownership đúng khi re-ingest trùng (không claim mapping của item trước)
  6. Conflict group được dọn khi rollback mapping gây mâu thuẫn
  7. API endpoints: /corpora → /ingest → /distill-queue → /resolve
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest


@pytest.fixture(autouse=True)
def _isolated_db(monkeypatch, tmp_path):
    """Isolate lexicon DB per test."""
    tmp_db = tmp_path / "lexicon.sqlite3"
    monkeypatch.setattr("engine.yi_lexicon.store._DB_PATH", tmp_db)
    yield


# ─── Fake LLM extraction provider ────────────────────────────────────────────

EXTRACTION = {
    "concepts": [
        {
            "canonical_vi": "lá bàng",
            "canonical_zh": "欖仁葉",
            "concept_type": "object",
            "aliases": ["lá cây bàng"],
            "schools": ["mai_hoa", "common"],
            "confidence": 0.9,
            "mappings": [
                {"dim_type": "ngu_hanh", "dim_value": "mộc",
                 "reasoning_vi": "Lá là phần của cây", "confidence": 0.9},
                {"dim_type": "mua", "dim_value": "thu",
                 "reasoning_vi": "Lá bàng rụng mùa thu", "confidence": 0.8},
            ],
        },
        {
            "canonical_vi": "chim khách",
            "concept_type": "object",
            "schools": ["mai_hoa"],
            "confidence": 0.7,
            "mappings": [
                {"dim_type": "bat_quai", "dim_value": "Đoài",
                 "reasoning_vi": "Chim khách báo tin, Đoài là miệng lời",
                 "confidence": 0.7},
            ],
        },
    ],
    "contextual_meanings": [
        {"phrase_vi": "lá bàng rơi trước cổng",
         "primary_concept_vi": "lá bàng",
         "meaning_vi": "Điềm chuyển mùa, tin từ xa tới",
         "school": "mai_hoa", "confidence": 0.6},
    ],
}


class FakeExtractionProvider:
    """Fake LLM: luôn trả JSON extraction hợp lệ (deterministic, không cần key)."""

    def __init__(self, payload: dict | None = None):
        self.payload = payload if payload is not None else EXTRACTION
        self.calls = 0

    def chat(self, *, messages, model=None, temperature=0.6, max_tokens=1500):
        self.calls += 1
        return SimpleNamespace(
            content=json.dumps(self.payload, ensure_ascii=False)
        )


def _make_corpus(tmp_path, name="Sách Test YOLO") -> int:
    from engine.yi_lexicon.ingestion import register_corpus

    f = tmp_path / "corpus.txt"
    f.write_text(
        "Lá bàng thuộc mộc, rụng mùa thu.\n\nChim khách kêu là Đoài động, có tin.",
        encoding="utf-8",
    )
    return register_corpus(name, str(f), author="Test", school="mai_hoa")


def _ingest(corpus_id: int, payload: dict | None = None):
    from engine.yi_lexicon.ingestion import ingest_corpus

    provider = FakeExtractionProvider(payload)
    result = ingest_corpus(corpus_id, llm_provider=provider, model="fake-v1")
    return result, provider


def _queue_item_by_vi(canonical_vi: str, status: str = "auto_accepted"):
    from engine.yi_lexicon import get_distill_queue

    for item in get_distill_queue(status=status):
        if item.payload.get("canonical_vi") == canonical_vi:
            return item
    return None


# ─── 1+2. Ingest → YOLO merge → queue với ownership ─────────────────────────


def test_yolo_ingest_merges_and_queues_with_ownership(tmp_path):
    from engine.yi_lexicon import get_concept, mappings_for, stats
    from engine.yi_lexicon.store import _conn

    cid = _make_corpus(tmp_path)
    result, provider = _ingest(cid)

    assert result.errors == []
    assert provider.calls >= 1
    assert result.concepts_added == 2
    assert result.mappings_added == 3
    assert result.contextual_added == 1

    # Lexicon state — merged thật
    la_bang = get_concept(canonical_vi="lá bàng")
    assert la_bang is not None
    assert {m.dim_value for m in mappings_for(la_bang.concept_id)} == {"mộc", "thu"}
    chim = get_concept(canonical_vi="chim khách")
    assert chim is not None

    # Queue — mỗi concept 1 item auto_accepted, payload mang _merged ownership
    s = stats()
    assert s["distill_queue"].get("auto_accepted") == 2
    item = _queue_item_by_vi("lá bàng")
    assert item is not None
    merged = item.payload["_merged"]
    assert merged["concept_id"] == la_bang.concept_id
    assert merged["concept_created"] is True
    assert len(merged["mapping_ids"]) == 2

    # Corpus stats được cập nhật
    with _conn() as c:
        row = c.execute(
            "SELECT concepts_extracted, mappings_extracted FROM corpora WHERE corpus_id=?",
            (cid,),
        ).fetchone()
    assert row["concepts_extracted"] == 2
    assert row["mappings_extracted"] == 3


# ─── 3. REJECT → rollback ────────────────────────────────────────────────────


def test_yolo_reject_rolls_back_concept_and_mappings(tmp_path):
    from engine.yi_lexicon import get_concept, review_distill_item

    cid = _make_corpus(tmp_path)
    _ingest(cid)

    item = _queue_item_by_vi("chim khách")
    assert item is not None
    concept_id = item.payload["_merged"]["concept_id"]

    result = review_distill_item(
        item.item_id, status="rejected", reviewer_note="LLM bịa — không có nguồn"
    )
    assert result["found"] is True
    assert result["rolled_back"]["mapping_ids"] == item.payload["_merged"]["mapping_ids"]
    assert result["rolled_back"]["concept_deleted"] is True

    # Lexicon sạch như trước merge: concept + mapping đều bị gỡ
    assert get_concept(concept_id=concept_id) is None
    # Item còn lại KHÔNG bị ảnh hưởng
    assert get_concept(canonical_vi="lá bàng") is not None
    # Queue item đổi status + ghi lại rollback
    rejected = _queue_item_by_vi("chim khách", status="rejected")
    assert rejected is not None
    assert rejected.payload["_review"]["rolled_back"] is True


def test_yolo_reject_keeps_concept_referenced_elsewhere(tmp_path):
    """Concept có contextual_meaning tham chiếu → rollback gỡ mappings nhưng
    GIỮ concept (không phá tham chiếu ngoài ownership của item)."""
    from engine.yi_lexicon import get_concept, mappings_for, review_distill_item

    cid = _make_corpus(tmp_path)
    _ingest(cid)

    item = _queue_item_by_vi("lá bàng")
    result = review_distill_item(item.item_id, status="rejected")

    la_bang = get_concept(canonical_vi="lá bàng")
    assert la_bang is not None                       # contextual meaning giữ concept
    assert mappings_for(la_bang.concept_id) == []    # mappings đã gỡ
    assert result["rolled_back"]["concept_deleted"] is False
    assert len(result["rolled_back"]["mapping_ids"]) == 2


def test_yolo_reject_search_no_longer_finds_concept(tmp_path):
    """FTS row phải được dọn cùng concept (external-content FTS5 delete)."""
    from engine.yi_lexicon import review_distill_item, search_concepts

    cid = _make_corpus(tmp_path)
    _ingest(cid)
    assert any("chim khách" in c.canonical_vi for c in search_concepts("chim khách"))

    item = _queue_item_by_vi("chim khách")
    review_distill_item(item.item_id, status="rejected")

    assert not any(
        "chim khách" in c.canonical_vi for c in search_concepts("chim khách")
    )


# ─── 4. APPROVE → verified ───────────────────────────────────────────────────


def test_yolo_approve_marks_mappings_verified(tmp_path):
    from engine.yi_lexicon import get_concept, mappings_for, review_distill_item

    cid = _make_corpus(tmp_path)
    _ingest(cid)

    item = _queue_item_by_vi("lá bàng")
    result = review_distill_item(
        item.item_id, status="approved", reviewer_note="anh duyệt OK"
    )
    assert result["found"] is True
    assert sorted(result["verified_mapping_ids"]) == sorted(
        item.payload["_merged"]["mapping_ids"]
    )

    la_bang = get_concept(canonical_vi="lá bàng")
    for m in mappings_for(la_bang.concept_id):
        assert m.verified_by_anh == 1

    approved = _queue_item_by_vi("lá bàng", status="approved")
    assert approved is not None
    assert approved.reviewer_note == "anh duyệt OK"


def test_yolo_reject_then_approve_warns_no_restore(tmp_path):
    """Anh đổi ý sau khi reject: approve chỉ đổi status, KHÔNG hồi sinh data
    (đã rollback) — phải cảnh báo rõ, không im lặng giả vờ."""
    from engine.yi_lexicon import get_concept, review_distill_item

    cid = _make_corpus(tmp_path)
    _ingest(cid)

    item = _queue_item_by_vi("chim khách")
    review_distill_item(item.item_id, status="rejected")
    result = review_distill_item(item.item_id, status="approved")

    assert result["warnings"], "phải cảnh báo data đã rollback"
    assert result["verified_mapping_ids"] == []
    assert get_concept(canonical_vi="chim khách") is None


# ─── 5. Ownership đúng khi trùng lặp ─────────────────────────────────────────


def test_yolo_reingest_duplicate_claims_no_ownership(tmp_path):
    """Ingest lần 2 cùng nội dung: dedup trả mapping cũ → item mới KHÔNG claim
    ownership; reject item mới không được phá data của item cũ."""
    from engine.yi_lexicon import get_concept, get_distill_queue, mappings_for, review_distill_item

    cid = _make_corpus(tmp_path)
    _ingest(cid)
    _ingest(cid)  # lần 2 — toàn duplicate

    items = [
        i for i in get_distill_queue(status="auto_accepted")
        if i.payload.get("canonical_vi") == "lá bàng"
    ]
    assert len(items) == 2
    owners = [i for i in items if i.payload["_merged"]["mapping_ids"]]
    dups = [i for i in items if not i.payload["_merged"]["mapping_ids"]]
    assert len(owners) == 1 and len(dups) == 1
    assert dups[0].payload["_merged"]["concept_created"] is False

    # Reject bản duplicate → lexicon còn nguyên
    result = review_distill_item(dups[0].item_id, status="rejected")
    assert result["rolled_back"]["mapping_ids"] == []
    assert result["rolled_back"]["concept_deleted"] is False
    la_bang = get_concept(canonical_vi="lá bàng")
    assert la_bang is not None
    assert len(mappings_for(la_bang.concept_id)) == 2


# ─── 6. Rollback dọn conflict group ──────────────────────────────────────────


def test_yolo_reject_conflicting_mapping_tidies_conflict_group(tmp_path):
    from engine.yi_lexicon import add_concept, add_mapping, mappings_for, review_distill_item
    from engine.yi_lexicon.store import _conn

    # Anh seed trước: "cửa sổ" thuộc mộc (nguồn tay, tier A)
    cua_so = add_concept(canonical_vi="cửa sổ", concept_type="object")
    add_mapping(cua_so.concept_id, "ngu_hanh", "mộc",
                source="manual", source_tier="A")

    # LLM extract nói "cửa sổ" thuộc kim → conflict (ngu_hanh single-value)
    payload = {
        "concepts": [{
            "canonical_vi": "cửa sổ",
            "concept_type": "object",
            "confidence": 0.6,
            "mappings": [
                {"dim_type": "ngu_hanh", "dim_value": "kim",
                 "reasoning_vi": "Khung cửa kim loại", "confidence": 0.6},
            ],
        }],
    }
    cid = _make_corpus(tmp_path)
    _ingest(cid, payload)

    flagged = mappings_for(cua_so.concept_id)
    assert {m.dim_value for m in flagged} == {"mộc", "kim"}
    assert all(m.conflict_flag == 1 for m in flagged), "cả 2 phải bị flag conflict"

    # Anh reject bản LLM → mapping kim bị gỡ, mộc hết flag, group đóng
    item = _queue_item_by_vi("cửa sổ")
    result = review_distill_item(item.item_id, status="rejected")
    assert len(result["rolled_back"]["mapping_ids"]) == 1
    assert result["rolled_back"]["concept_deleted"] is False  # concept của anh

    remaining = mappings_for(cua_so.concept_id)
    assert [m.dim_value for m in remaining] == ["mộc"]
    assert remaining[0].conflict_flag == 0
    with _conn() as c:
        groups = c.execute(
            "SELECT status FROM conflict_groups WHERE concept_id=?",
            (cua_so.concept_id,),
        ).fetchall()
    assert groups and all(g["status"] != "open" for g in groups)


# ─── 7. Item legacy (trước v3, không có _merged) ─────────────────────────────


def test_yolo_legacy_item_without_ownership_only_flips_status():
    from engine.yi_lexicon import add_distill_item, review_distill_item

    item = add_distill_item(
        kind="new_concept",
        payload={"canonical_vi": "xe đạp", "concept_type": "object"},
        source="council:legacy",
    )
    result = review_distill_item(item.item_id, status="rejected")
    assert result["found"] is True
    assert result["rolled_back"]["mapping_ids"] == []
    assert any("legacy" in w for w in result["warnings"])


def test_yolo_review_not_found():
    from engine.yi_lexicon import review_distill_item

    assert review_distill_item(999999, status="approved")["found"] is False


def test_yolo_review_invalid_status_raises():
    from engine.yi_lexicon import review_distill_item

    with pytest.raises(ValueError):
        review_distill_item(1, status="maybe")


# ─── 8. API E2E: corpora → ingest → queue → resolve ──────────────────────────


def test_api_yolo_full_cycle(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    import engine.ai.registry as registry_mod
    from api.main import app

    # Registry fake — API /ingest tự resolve provider từ registry
    class _FakeRegistry:
        def first_configured(self, preferred_order):
            return FakeExtractionProvider()

    monkeypatch.setattr(registry_mod, "get_registry", lambda: _FakeRegistry())

    client = TestClient(app)

    # 1. Register corpus
    f = tmp_path / "api_corpus.txt"
    f.write_text("Lá bàng thuộc mộc. Chim khách kêu Đoài động.", encoding="utf-8")
    r = client.post("/api/yi-lexicon/corpora", json={
        "name": "API YOLO E2E", "file_path": str(f), "school": "mai_hoa",
    })
    assert r.status_code == 200
    corpus_id = r.json()["corpus_id"]

    # 2. Ingest (YOLO auto-merge)
    r = client.post("/api/yi-lexicon/ingest", json={"corpus_id": corpus_id})
    assert r.status_code == 200
    ingest = r.json()["result"]
    assert ingest["errors"] == []
    assert ingest["concepts_added"] == 2

    # 3. Queue có items auto_accepted mang ownership
    r = client.get("/api/yi-lexicon/distill-queue?status=auto_accepted")
    items = r.json()["items"]
    by_vi = {i["payload"].get("canonical_vi"): i for i in items}
    assert "lá bàng" in by_vi and "chim khách" in by_vi
    assert by_vi["chim khách"]["payload"]["_merged"]["mapping_ids"]

    # 4. Reject qua API → response trả chi tiết rollback
    item_id = by_vi["chim khách"]["item_id"]
    r = client.post(f"/api/yi-lexicon/distill-queue/{item_id}/resolve", json={
        "status": "rejected", "reviewer_note": "không có nguồn",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["review"]["rolled_back"]["concept_deleted"] is True

    # 5. Lexicon phản ánh rollback: concept biến mất khỏi search
    r = client.get("/api/yi-lexicon/concepts?q=chim khách")
    assert not any(
        c["canonical_vi"] == "chim khách" for c in r.json()["results"]
    )

    # 6. Approve item còn lại → verified
    item_id = by_vi["lá bàng"]["item_id"]
    r = client.post(f"/api/yi-lexicon/distill-queue/{item_id}/resolve", json={
        "status": "approved",
    })
    assert r.json()["review"]["verified_mapping_ids"]

    # 7. Resolve item không tồn tại → not_found
    r = client.post("/api/yi-lexicon/distill-queue/999999/resolve", json={
        "status": "approved",
    })
    assert r.json()["status"] == "not_found"
