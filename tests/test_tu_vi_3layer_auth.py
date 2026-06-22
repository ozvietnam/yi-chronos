"""P0 security (review 2026-06-21) — gate các endpoint Tử Vi 3-layer.

Lỗ hổng: các route gọi LLM (tốn tiền API) + demo founder bị BỎ NGỎ cho khách ẩn danh
→ ai cũng spam ngày sinh ngẫu nhiên đốt quota LLM của founder; founder-demo lộ lá số.
Vá: require_caller (đồng bộ /api/tu-vi/cast vốn đã gate) + rate_limit; founder-demo +
context/reload → owner-only. Test này khoá hồi quy.

Guest = TestClient không cookie/không X-API-Key → require_caller raise 401 TRƯỚC khi
chạm LLM. KHÔNG dùng fixture as_owner (cố tình test đường khách).
"""
from __future__ import annotations

import pytest


@pytest.fixture
def client():
    from api.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)


_BIRTH = {"birth_datetime_local": "1988-06-05T23:30", "timezone": "Asia/Ho_Chi_Minh", "gender": "nam"}

# Route gọi LLM hoặc tính nặng (render_from_birth ×N) — guest PHẢI 401, KHÔNG được chạy.
EXPENSIVE_POST = [
    ("/api/tu-vi/3-layer/narrative", dict(_BIRTH)),
    ("/api/tu-vi/3-layer/chu-de", {**_BIRTH, "chu_de": "su-nghiep"}),
    ("/api/tu-vi/3-layer/chu-de-sau", {**_BIRTH, "chu_de": "su-nghiep"}),
    ("/api/tu-vi/3-layer/gia-vi", {**_BIRTH, "chu_de": "su-nghiep"}),
    ("/api/tu-vi/duyen-tho", {"birth": "1988-06-05T23:30", "gender": "nam"}),
    ("/api/tu-vi/so-sanh-duyen", {"me": {"birth": "1988-06-05T23:30", "gender": "nam"}, "others": []}),
    ("/api/tu-vi/3-layer/thai-do-so-phan", dict(_BIRTH)),  # (d) hồ sơ thái-độ-số-phận
]


@pytest.mark.parametrize("path,body", EXPENSIVE_POST)
def test_guest_blocked_from_expensive_tuvi(client, path, body):
    r = client.post(path, json=body)
    assert r.status_code == 401, f"{path} cho guest chạy (đốt tiền LLM/CPU): HTTP {r.status_code}"


def test_founder_demo_is_owner_only(client):
    r = client.get("/api/tu-vi/3-layer/founder-demo")
    assert r.status_code in (401, 403), f"founder-demo rò lá số founder cho guest: HTTP {r.status_code}"


def test_context_reload_is_owner_only(client):
    r = client.post("/api/yi-hermes/context/reload")
    assert r.status_code in (401, 403), f"context/reload mở cho guest: HTTP {r.status_code}"


def test_public_chu_de_list_still_open(client):
    """GET /3-layer/chu-de (danh sách chủ đề tĩnh, KHÔNG LLM) vẫn public — không over-gate."""
    r = client.get("/api/tu-vi/3-layer/chu-de")
    assert r.status_code == 200, f"danh sách chủ đề tĩnh bị chặn nhầm: HTTP {r.status_code}"


def test_founder_demo_not_blocked_for_owner(as_owner):
    """KHÔNG over-gate: owner qua được cổng require_owner (KHÔNG 401/403).

    Gate require_owner là dòng ĐẦU thân hàm, trước render. CI thiếu data wiki →
    render đổ 500 (no such table) — nhưng việc chạm được tới render CHỨNG MINH cổng
    auth đã cho owner qua (nếu chặn sẽ 403, không bao giờ tới render). Dùng client
    raise_server_exceptions=False để 500 thành response thay vì exception.
    """
    from api.main import app
    from fastapi.testclient import TestClient
    c = TestClient(app, raise_server_exceptions=False)
    r = c.get("/api/tu-vi/3-layer/founder-demo")
    assert r.status_code not in (401, 403), f"owner bị cổng auth chặn nhầm: HTTP {r.status_code}"
