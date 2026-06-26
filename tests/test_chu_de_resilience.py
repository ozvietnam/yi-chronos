"""Endpoint /3-layer/chu-de phải trả bài đọc DETERMINISTIC kể cả khi LLM lỗi/timeout.

Kênh #3 #2 surfacing (Anh 'làm luôn' 2026-06-26): bài đọc cổ điển (Tử Tức/Phu Thê) không
được biến mất khi provider văn-dài (MiniMax...) timeout — đó là phần đáng tin nhất.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def _app_no_auth(monkeypatch):
    from api.main import app
    from api import tu_vi_3layer
    from api.service_auth import require_caller

    app.dependency_overrides[require_caller] = lambda: {"user_id": 1, "role": "owner", "via": "test"}
    monkeypatch.setattr(tu_vi_3layer, "rate_limit_caller", lambda *a, **k: None)
    # LLM văn-dài luôn lỗi (mô phỏng MiniMax timeout)
    import engine.atomization.narrative_gen as ng
    monkeypatch.setattr(ng, "generate_chu_de_narrative",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("LLM down (test)")))
    yield app
    app.dependency_overrides.clear()


def _post(app, chu_de):
    return TestClient(app).post("/api/tu-vi/3-layer/chu-de", json={
        "birth_datetime_local": "1988-06-05T23:30:00", "timezone": "Asia/Ho_Chi_Minh",
        "gender": "nam", "chu_de": chu_de})


def test_gia_dao_tra_tu_tuc_reading_khi_llm_loi(_app_no_auth):
    """Gia đạo: LLM lỗi → narrative null NHƯNG tu_tuc_reading vẫn có (card con cái hiện)."""
    r = _post(_app_no_auth, "gia_dao")
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["narrative"] is None
    assert d["tu_tuc_reading"] and "30%" in d["tu_tuc_reading"]["caveat"]


def test_tinh_duyen_tra_phu_the_signals_khi_llm_loi(_app_no_auth):
    """Tình duyên: LLM lỗi → vẫn có phu_the_signals (card tình duyên hiện)."""
    r = _post(_app_no_auth, "tinh_duyen")
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["narrative"] is None
    assert d["phu_the_signals"] and d["phu_the_signals"]["doc_than_risk"]


def test_topic_khong_deterministic_van_raise_khi_llm_loi(_app_no_auth):
    """Sự nghiệp (không có bài đọc deterministic): LLM lỗi → vẫn lỗi 500 (giữ hành vi cũ, không nuốt lỗi)."""
    client = TestClient(_app_no_auth, raise_server_exceptions=False)
    r = client.post("/api/tu-vi/3-layer/chu-de", json={
        "birth_datetime_local": "1988-06-05T23:30:00", "timezone": "Asia/Ho_Chi_Minh",
        "gender": "nam", "chu_de": "su_nghiep"})
    assert r.status_code == 500
