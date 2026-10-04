"""Route Tử Vi cấu trúc (an sao/Bát Tự, KHÔNG LLM): khách ẩn danh VẪN dùng được nhưng bị throttle
nhẹ theo user/IP (bucket tuvi_cast) — chống abuse CPU. Port từ nhánh cũ (commit e648ab34), viết lại
trên api/tu_vi_3layer.py hiện tại. Không gọi LLM; ép rate-limit in-memory cho tất định."""
from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

import api.tu_vi_3layer as mod
from engine import ratelimit

BIRTH = {"birth_datetime_local": "1988-06-05T23:30", "gender": "nam"}

ROUTES = [
    ("/api/tu-vi/3-layer/from-birth", {**BIRTH}),
    ("/api/tu-vi/hop-hon", {"birth1": "1988-06-05T23:30", "gender1": "nam",
                            "birth2": "1990-02-02T10:00", "gender2": "nữ"}),
    ("/api/tu-vi/thien-luong", {"birth": "1988-06-05T23:30", "gender": "nam"}),
    ("/api/tu-vi/cung-sau", {"birth": "1988-06-05T23:30", "gender": "nam"}),
    ("/api/tu-vi/duyen", {"birth": "1988-06-05T23:30", "gender": "nam"}),
    ("/api/tu-vi/gia-dao", {"birth1": "1988-06-05T23:30", "gender1": "nam",
                            "birth2": "1990-02-02T10:00", "gender2": "nữ"}),
    ("/api/tu-vi/dat-ten", {"birth_con": "2020-03-03T08:00"}),
    ("/api/tu-vi/luan-con", {"birth_con": "2020-03-03T08:00", "gender_con": "nam"}),
]


@pytest.fixture
def client():
    from api.main import app
    # raise_server_exceptions=False: môi trường thiếu DB gitignore (CI/clone sạch) trả 500 chứ không
    # làm test nổ — điều cần khoá ở đây chỉ là khách KHÔNG bị 401/429.
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def _inmem_rl(monkeypatch):
    monkeypatch.setattr(ratelimit, "_redis", False, raising=False)
    ratelimit.reset()
    yield
    ratelimit.reset()


def _as_session(monkeypatch, *, user_id, role="user"):
    import api.auth as auth
    u = {"user_id": user_id, "email": f"u{user_id}@x.vn", "role": role, "display_name": "U"}
    monkeypatch.setattr(auth, "get_current_user", lambda request: u, raising=True)


@pytest.mark.parametrize("path,body", ROUTES)
def test_guest_allowed(client, path, body):
    r = client.post(path, json=body)
    assert r.status_code not in (401, 429), f"{path}: khách phải được dùng, nhận {r.status_code}"


@pytest.mark.parametrize("path,body", ROUTES)
def test_user_over_limit_gets_429(client, monkeypatch, path, body):
    _as_session(monkeypatch, user_id=91)
    ratelimit._mem[f"{mod.CAST_BUCKET}:91"] = [time.time()] * mod.CAST_LIMIT
    assert client.post(path, json=body).status_code == 429


def test_guest_throttled_per_ip_not_shared(client):
    """Khách khoá theo IP (phần tử CUỐI của X-Forwarded-For — Traefik ghi): IP A hết quota không làm
    IP B bị chặn; phần tử đứng trước (khách tự giả) không đổi được khoá."""
    path, body = "/api/tu-vi/dat-ten", {"birth_con": "2020-03-03T08:00"}
    ratelimit._mem[f"{mod.CAST_BUCKET}:ip:1.1.1.1"] = [time.time()] * mod.CAST_LIMIT
    assert client.post(path, json=body, headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 429
    assert client.post(path, json=body, headers={"X-Forwarded-For": "2.2.2.2"}).status_code == 200
    # giả mạo phần tử đầu để né: vẫn bị khoá theo phần tử cuối (1.1.1.1)
    assert client.post(path, json=body,
                       headers={"X-Forwarded-For": "9.9.9.9, 1.1.1.1"}).status_code == 429


def test_owner_exempt(client, monkeypatch):
    _as_session(monkeypatch, user_id=1, role="owner")
    ratelimit._mem[f"{mod.CAST_BUCKET}:1"] = [time.time()] * mod.CAST_LIMIT
    assert client.post("/api/tu-vi/dat-ten", json={"birth_con": "2020-03-03T08:00"}).status_code == 200
