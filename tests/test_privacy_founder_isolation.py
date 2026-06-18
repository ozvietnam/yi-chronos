"""D (privacy) — KHOÁ cô lập founder/PII: guest (chưa đăng nhập) KHÔNG được đọc data
nhạy cảm. Codify audit 2026-05-27 (3 đợt rò founder) thành test hồi quy chống tái diễn.

Đường H6 mới (council/quick) vốn resolve theo user_id (cô lập) — test này khoá nốt các
endpoint LEGACY /api/yi-hermes/* (founder/soul/memory/persons/network) phải gate.
"""
from __future__ import annotations

import pytest


@pytest.fixture
def client():
    from api.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)


# GET nhạy cảm — guest PHẢI bị chặn (401 chưa auth / 403 không phải owner)
SENSITIVE_GET = [
    "/api/yi-hermes/context/founder",
    "/api/yi-hermes/soul/_founder",
    "/api/yi-hermes/memory/_founder/facts",
    "/api/yi-hermes/memory/_founder/summaries",
    "/api/yi-hermes/memory/_founder/full",
    "/api/yi-hermes/persons",
    "/api/yi-hermes/persons/_founder",
    "/api/yi-hermes/network/_founder",
    "/api/yi-hermes/context/summary/_founder",
]


@pytest.mark.parametrize("path", SENSITIVE_GET)
def test_guest_blocked_from_sensitive_get(client, path):
    r = client.get(path)
    assert r.status_code in (401, 403), f"{path} rò cho guest: HTTP {r.status_code}"


# POST nhạy cảm — guest PHẢI bị chặn
SENSITIVE_POST = [
    ("/api/yi-hermes/chat", {"user_message": "hi", "history": []}),
    ("/api/hermes/ask", {"question": "Lá số tử vi của tôi?"}),
    ("/api/yi-hermes/memory/_founder/facts", {"fact": "x", "category": "event"}),
    ("/api/yi-hermes/persons", {"person_key": "x", "name": "X"}),
]


@pytest.mark.parametrize("path,body", SENSITIVE_POST)
def test_guest_blocked_from_sensitive_post(client, path, body):
    r = client.post(path, json=body)
    assert r.status_code in (401, 403), f"{path} rò cho guest: HTTP {r.status_code}"


def test_health_still_public(client):
    # không phải khoá tất — health vẫn public (smoke)
    assert client.get("/api/health").status_code == 200
