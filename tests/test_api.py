import pytest
from fastapi.testclient import TestClient

from api.main import app

# #34: cast/quiz endpoints giờ dual-auth → test chạy as owner (session) để qua gate.
pytestmark = pytest.mark.usefixtures("as_owner")


client = TestClient(app)


def test_universe_now_returns_versioned_snapshot():
    response = client.get("/api/universe-now")

    assert response.status_code == 200
    payload = response.json()
    assert payload["algorithm_version"] == "mvp-0.1.0"
    assert "yi_state" in payload
    assert "scores" in payload


def test_personal_profile_accepts_exact_and_unknown_birth_precision():
    for precision in ("exact", "unknown"):
        response = client.post(
            "/api/personal-profile",
            json={
                "birth_datetime_local": "1995-08-15T10:30:00",
                "timezone": "Asia/Ho_Chi_Minh",
                "location_ref": "VN-SG",
                "birth_precision": precision,
                "gender_optional": None,
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["algorithm_version"] == "mvp-0.1.0"
        assert "sync_score" in payload
        assert len(payload["milestone_prompts"]) >= 1


def test_feedback_accepts_all_response_enums_and_empty_optional_fields():
    profile = client.post(
        "/api/personal-profile",
        json={
            "birth_datetime_local": "1995-08-15T10:30:00",
            "timezone": "Asia/Ho_Chi_Minh",
            "location_ref": "VN-SG",
            "birth_precision": "exact",
            "gender_optional": None,
        },
    ).json()
    prompt_id = profile["milestone_prompts"][0]["prompt_id"]

    for response_enum in ("matched", "partly", "false", "unknown"):
        response = client.post(
            "/api/feedback",
            json={
                "prompt_id": prompt_id,
                "response_enum": response_enum,
                "confidence_enum": "unsure",
                "tags": [],
                "free_text_optional": "",
            },
        )

        assert response.status_code == 200
        assert response.json()["status"] == "stored"


def test_luc_hao_cast_endpoint_returns_structured_result():
    response = client.post(
        "/api/luc-hao/cast",
        json={
            "datetime_local": "2026-05-08T20:00:00",
            "timezone": "Asia/Ho_Chi_Minh",
            "question_text": "Việc này có thuận không?",
            "interaction_signal": {
                "hold_duration_ms": 3180,
                "move_event_count": 42,
                "path_length_px": 286.5,
                "release_timestamp_ms": 1746700800000,
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "luc_hao_state" in payload
    assert "primary_hexagram" in payload["luc_hao_state"]
    assert "lines" in payload["luc_hao_state"]
    assert len(payload["luc_hao_state"]["lines"]) == 6
    assert payload["luc_hao_state"]["verdict"]["tag"] in {"favorable", "caution", "neutral"}
    assert "mai_hoa_environment" in payload["luc_hao_state"]
    assert "energy_flow_summary" in payload["luc_hao_state"]
    assert "timing_prediction" in payload["luc_hao_state"]
    assert "best_match" in payload["luc_hao_state"]["timing_prediction"]
    assert "dung_than" in payload["luc_hao_state"]
    assert "hidden_line_candidates" in payload["luc_hao_state"]
    assert "timing_funnel_matrix" in payload["luc_hao_state"]
    assert "ruler_profile" in payload["luc_hao_state"]
    assert payload["luc_hao_state"]["ruler_profile"]["id"] == "tam_thien_v1"
    assert "decision_quality" in payload["luc_hao_state"]["ruler_profile"]
    assert "context_trigram_roles" in payload["luc_hao_state"]["ruler_profile"]
    assert "strategy_mode" in payload["luc_hao_state"]["ruler_profile"]
    assert "reverse_probe" in payload["luc_hao_state"]["ruler_profile"]
    assert "staged_plan" in payload["luc_hao_state"]["ruler_profile"]
    assert "leverage_mode" in payload["luc_hao_state"]["ruler_profile"]
    assert "recovery_cycle" in payload["luc_hao_state"]["ruler_profile"]
    assert "coalition_strength" in payload["luc_hao_state"]["ruler_profile"]
    assert "conflict_mode" in payload["luc_hao_state"]["ruler_profile"]
    assert "counterparty_risk" in payload["luc_hao_state"]["ruler_profile"]
    assert "evidence_gate" in payload["luc_hao_state"]["ruler_profile"]
    assert "scope_gate" in payload["luc_hao_state"]["ruler_profile"]
    assert "tradeoff_hint" in payload["luc_hao_state"]["ruler_profile"]
    assert "triple_condition_check" in payload["luc_hao_state"]["ruler_profile"]
    assert "one_line_verdict" in payload["luc_hao_state"]["ruler_profile"]
    assert "pair_dynamics" in payload["luc_hao_state"]["ruler_profile"]
    assert "timing_dual_view" in payload["luc_hao_state"]["ruler_profile"]


def test_calculate_can_embed_luc_hao_state_when_interaction_present():
    response = client.post(
        "/calculate",
        json={
            "datetime_local": "2026-05-08T20:00:00",
            "timezone": "Asia/Ho_Chi_Minh",
            "question_text": "Có nên ký hợp đồng tuần này không?",
            "interaction_signal": {
                "hold_duration_ms": 2550,
                "move_event_count": 30,
                "path_length_px": 191.2,
                "release_timestamp_ms": 1746700800123,
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "luc_hao_state" in payload
    assert payload["luc_hao_state"]["question_text"] == "Có nên ký hợp đồng tuần này không?"


def test_luc_hao_case_save_and_feedback_flow():
    cast = client.post(
        "/api/luc-hao/cast",
        json={
            "datetime_local": "2026-05-08T20:00:00",
            "timezone": "Asia/Ho_Chi_Minh",
            "question_text": "Dự án này có về đích đúng hạn không?",
            "interaction_signal": {
                "hold_duration_ms": 2800,
                "move_event_count": 35,
                "path_length_px": 220.5,
                "release_timestamp_ms": 1746700801123,
            },
        },
    )
    cast_payload = cast.json()
    save = client.post(
        "/api/luc-hao/save-case",
        json={
            "question_text": cast_payload["luc_hao_state"]["question_text"],
            "timezone": "Asia/Ho_Chi_Minh",
            "luc_hao_state": cast_payload["luc_hao_state"],
            "interaction_signal": {
                "hold_duration_ms": 2800,
                "move_event_count": 35,
                "path_length_px": 220.5,
                "release_timestamp_ms": 1746700801123,
            },
        },
    )
    assert save.status_code == 200
    save_payload = save.json()
    assert save_payload["status"] == "stored"
    case_id = save_payload["case_id"]

    feedback = client.post(
        "/api/luc-hao/feedback",
        json={
            "case_id": case_id,
            "result_enum": "partly",
            "confidence_enum": "medium",
            "event_summary": "Kết quả đến chậm 2 ngày nhưng xu hướng đúng.",
            "resolved_at_local": "2026-05-10T09:00:00",
            "tags": ["tiến độ", "hợp đồng"],
        },
    )
    assert feedback.status_code == 200
    assert feedback.json()["status"] == "stored"


def test_lien_hoa_cast_endpoint_returns_full_spread():
    """New v2 endpoint returns full Bản Quái Kiện 5/9/13 không thời sự."""
    response = client.post(
        "/api/lien-hoa/cast",
        json={
            "question_text": "Có nên đổi hướng công việc tháng này không?",
            "number_right_hand": 12,
            "number_left_hand": 38,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "lien_hoa_state" in payload
    state = payload["lien_hoa_state"]
    # Shape from new Liên Hoa Độn Pháp engine.
    assert state["method_id"] == "lien_hoa_don_v1"
    assert "khong_thoi" in state
    assert "dot_count" in state
    assert "khong_thoi_count" in state
    assert "ta_reference_trigram" in state
    # 12+38=50 mod 6 = 2 → 3 đợt → 13 KTS.
    assert state["dot_count"] == 3
    assert len(state["khong_thoi"]) == 13
    # Each KTS has chánh / hổ / biến + tagged trigrams.
    first = state["khong_thoi"][0]
    assert "chanh" in first and "ho" in first and "bien" in first
    assert "tagged" in first and len(first["tagged"]) == 6


def test_hexagram_interpretation_v2_endpoint_returns_record():
    response = client.get("/api/hexagram-interpretation-v2/1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["record"]["name_vi"] == "Kiền"
    assert payload["record"]["an_bai_the_su"]
