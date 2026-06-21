"""P2 (review 2026-06-21) — KHOÁ hồi quy IDOR chéo-user (lỗ hổng #1 lịch sử dự án).

Audit 2026-05-27 đã gate self-or-owner cho /api/yi-hermes/soul|memory/{user_id} +
service-key-only cho /api/sync/*. Protection ĐÃ CÓ và đúng — nhưng (testing agent)
CHƯA có test chứng minh user-A KHÔNG đọc được data user-B. File này khoá nốt: nếu ai
gỡ gate sau này, test đỏ ngay.

Khác test_privacy_founder_isolation (guest-vs-owner) ở chỗ test ĐÚNG trục A-vs-B
(hai user thường khác nhau) — đúng class lỗi đã leak 3 lần.
"""
from __future__ import annotations

import pytest


@pytest.fixture
def client_noraise():
    from api.main import app
    from fastapi.testclient import TestClient
    # raise_server_exceptions=False: downstream thiếu data → 500 thành response, không
    # ném; ta chỉ quan tâm tầng GATE (401/403), không phải data layer.
    return TestClient(app, raise_server_exceptions=False)


def _as_user(monkeypatch, uid: int, role: str = "user"):
    """Giả lập user thường đăng nhập (id=uid). _yi_hermes_require_self_or_owner gọi
    require_user qua inline import → monkeypatch api.auth.require_user ăn."""
    import api.auth as auth
    u = {"user_id": uid, "role": role, "email": f"u{uid}@x.vn", "display_name": f"U{uid}"}
    monkeypatch.setattr(auth, "require_user", lambda request: u, raising=True)
    return u


# Endpoint yi-hermes per-user (đọc) — user A KHÔNG được chạm user_id của B.
CROSS_USER_GET = [
    "/api/yi-hermes/soul/{other}",
    "/api/yi-hermes/memory/{other}/facts",
    "/api/yi-hermes/memory/{other}/summaries",
    "/api/yi-hermes/memory/{other}/full",
]


@pytest.mark.parametrize("tmpl", CROSS_USER_GET)
def test_user_a_cannot_read_user_b(client_noraise, monkeypatch, tmpl):
    _as_user(monkeypatch, uid=2)  # đăng nhập là user 2 (non-owner)
    r = client_noraise.get(tmpl.format(other="999"))  # đọc data user 999
    assert r.status_code == 403, f"IDOR! user 2 đọc được {tmpl} của user 999: HTTP {r.status_code}"


def test_user_can_read_own_soul_not_403(client_noraise, monkeypatch):
    """Không over-gate: user đọc CỦA CHÍNH MÌNH qua được gate (không 403)."""
    _as_user(monkeypatch, uid=2)
    r = client_noraise.get("/api/yi-hermes/soul/2")  # chính mình
    assert r.status_code != 403, f"user bị chặn nhầm khỏi soul của chính mình: HTTP {r.status_code}"


def test_owner_can_read_any_user(client_noraise, monkeypatch):
    """Owner (founder) đọc được mọi user_id (self-or-OWNER)."""
    _as_user(monkeypatch, uid=1, role="owner")
    r = client_noraise.get("/api/yi-hermes/soul/999")
    assert r.status_code != 403, f"owner bị chặn nhầm: HTTP {r.status_code}"


def test_sync_history_requires_service_key(client_noraise):
    """/api/sync/* chỉ cho service-to-service (X-API-Key). Web/guest KHÔNG có key →
    chặn (không 200) → web user không thể đọc lịch sử user bất kỳ qua sync."""
    r = client_noraise.get("/api/sync/history/anyuid")
    # 401/403 = key sai; 503 = fail-closed (YI_SYNC_API_KEY chưa set → sync disabled).
    # Cả ba đều CHẶN (không trả data) — đúng tinh thần "web user không đọc được sync".
    assert r.status_code in (401, 403, 503), f"sync/history TRẢ DATA cho caller không-service-key: HTTP {r.status_code}"
