"""Integration tests for Birth Hour Quiz v2 API endpoints (LLM mocked)."""
from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

FAKE_LLM = {
    chi: {
        "decision_style": "analytical", "leadership_orientation": "supportive",
        "emotional_pattern": "cool", "communication_style": "nuanced",
        "career_direction": "creative", "marriage_timing_rough": "25_30",
        "health_pattern_general": "on",
    }
    for chi in ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
}


@patch("engine.yi_wiki.birth_hour_quiz_v2.derivation.call_trait_llm", return_value=FAKE_LLM)
def test_start_quiz_returns_session_and_round1(mock_llm):
    resp = client.post(
        "/api/yi-wiki/birth-hour-quiz-v2/start",
        json={
            "birth_date": "1988-05-02",
            "timezone": "Asia/Ho_Chi_Minh",
            "hour_range": {"start": 7, "end": 11},
            "gender": "nam",
        },
    )
    assert resp.status_code == 200
    d = resp.json()
    assert d["status"] == "ok"
    assert "session_id" in d
    assert d["strategy"] in {"single_round", "two_round", "three_round"}
    assert len(d["candidates"]) >= 1
    assert "round_1" in d
    assert len(d["round_1"]["questions"]) > 0
    for q in d["round_1"]["questions"]:
        assert "options" in q
        assert any(o["id"] == "unsure" for o in q["options"])


@patch("engine.yi_wiki.birth_hour_quiz_v2.derivation.call_trait_llm", return_value=FAKE_LLM)
def test_submit_round_returns_final_or_continue(mock_llm):
    r1 = client.post("/api/yi-wiki/birth-hour-quiz-v2/start", json={
        "birth_date": "1988-05-02", "timezone": "Asia/Ho_Chi_Minh",
        "hour_range": {"start": 6, "end": 12}, "gender": "nam",
    }).json()
    sid = r1["session_id"]
    questions = r1["round_1"]["questions"]
    # answer first non-unsure option for each
    answers = {}
    for q in questions:
        first = next((o for o in q["options"] if o["id"] != "unsure"), None)
        if first:
            answers[q["id"]] = first["id"]

    r2 = client.post("/api/yi-wiki/birth-hour-quiz-v2/submit-round", json={
        "session_id": sid, "round_num": 1, "answers": answers,
    }).json()
    assert r2["status"] in {"CONTINUE", "FINAL", "FINAL_UNCERTAIN"}
    assert "scores" in r2


@patch("engine.yi_wiki.birth_hour_quiz_v2.derivation.call_trait_llm", return_value=FAKE_LLM)
def test_get_session(mock_llm):
    r1 = client.post("/api/yi-wiki/birth-hour-quiz-v2/start", json={
        "birth_date": "1988-05-02", "timezone": "Asia/Ho_Chi_Minh",
        "hour_range": {"start": 7, "end": 9}, "gender": "nam",
    }).json()
    sid = r1["session_id"]
    r2 = client.get(f"/api/yi-wiki/birth-hour-quiz-v2/session/{sid}")
    assert r2.status_code == 200
    d = r2.json()
    assert d["api_status"] == "ok"
    assert d["session"]["session_id"] == sid
    assert d["session"]["status"] in {"in_progress", "final"}


@patch("engine.yi_wiki.birth_hour_quiz_v2.derivation.call_trait_llm", return_value=FAKE_LLM)
def test_save_result_smoke(mock_llm):
    """End-to-end: start → submit → save. Save may fail if person_id missing, but endpoint responds."""
    r1 = client.post("/api/yi-wiki/birth-hour-quiz-v2/start", json={
        "birth_date": "1988-05-02", "timezone": "Asia/Ho_Chi_Minh",
        "hour_range": {"start": 7, "end": 9}, "gender": "nam",
    }).json()
    sid = r1["session_id"]
    questions = r1["round_1"]["questions"]
    answers = {}
    for q in questions:
        first = next((o for o in q["options"] if o["id"] != "unsure"), None)
        if first:
            answers[q["id"]] = first["id"]
    r2 = client.post("/api/yi-wiki/birth-hour-quiz-v2/submit-round", json={
        "session_id": sid, "round_num": 1, "answers": answers,
    }).json()
    if r2["status"] in {"FINAL", "FINAL_UNCERTAIN"}:
        r3 = client.post("/api/yi-wiki/birth-hour-quiz-v2/save-result", json={
            "session_id": sid, "person_id": "_founder",
        })
        assert r3.status_code == 200
        assert "status" in r3.json()
