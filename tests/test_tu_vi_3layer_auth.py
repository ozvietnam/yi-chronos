"""Auth + rate-limit cho các route Tử Vi 3-Layer gọi LLM (api/tu_vi_3layer.py).

Bối cảnh: các endpoint sinh narrative (chuyện về anh / món chủ đề / đào sâu / gia vị /
duyên thơ) gọi engine.atomization.narrative_gen.generate_* → chain LLM tốn tiền API.
Trước fix: guest ẩn danh gửi vô số ngày sinh + force=true → đốt quota/tiền của founder.

Khoá (codify thành test hồi quy):
  - Guest (không session, không service-key) → 401 trên MỌI route LLM (+ so-sánh 8× cast).
  - User có session vượt ngưỡng → 429.
  - Owner web miễn rate-limit; chỉ owner mới được force=true (bỏ cache → sinh lại).
  - AppChat server-to-server (X-API-Key + X-User-Id) vẫn gọi được (dual-auth).
  - /3-layer/from-birth (an sao thuần, không LLM) vẫn cho guest, nhưng rate-limit nhẹ
    chống abuse CPU; /3-layer (render thuần) vẫn mở.

Không gọi LLM thật: autouse stub các generate_* + ép rate-limit về in-memory.
"""
from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

import api.tu_vi_3layer as mod
from engine import ratelimit

BIRTH = {"birth_datetime_local": "1988-06-05T23:30", "gender": "nam"}


@pytest.fixture
def client():
    from api.main import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def _no_llm_inmem_rl(monkeypatch):
    """Chặn LLM thật (mạng/tiền) + ép rate-limit dùng in-memory (bỏ Redis) cho tất
    định. Reset bộ đếm giữa các test."""
    import engine.atomization.narrative_gen as ng

    def stub(*a, **k):
        return {"narrative": "stub", "cached": False, "model": "mock"}

    monkeypatch.setattr(ng, "generate_narrative", stub, raising=True)
    monkeypatch.setattr(ng, "generate_chu_de_narrative", stub, raising=True)
    monkeypatch.setattr(ng, "generate_chu_de_sau_narrative", stub, raising=True)
    monkeypatch.setattr(ng, "generate_gia_vi_questions", lambda *a, **k: [], raising=True)
    monkeypatch.setattr(ng, "generate_duyen_narrative",
                        lambda *a, **k: {"narrative": "stub"}, raising=True)
    # Ép fallback in-memory (bỏ qua Redis nếu máy dev có chạy) → seed _mem tất định.
    monkeypatch.setattr(ratelimit, "_redis", False, raising=False)
    ratelimit.reset()
    yield
    ratelimit.reset()


def _as_session(monkeypatch, *, user_id=42, role="user"):
    """Giả lập user đã đăng nhập (session web)."""
    import api.auth as auth
    u = {"user_id": user_id, "email": f"u{user_id}@x.vn",
         "role": role, "display_name": "U"}
    monkeypatch.setattr(auth, "get_current_user", lambda request: u, raising=True)
    return u


# ─── 1) Guest bị chặn 401 trên mọi route LLM ────────────────────────────────
LLM_ROUTES = [
    ("/api/tu-vi/3-layer/narrative", {**BIRTH}),
    ("/api/tu-vi/3-layer/chu-de", {**BIRTH, "chu_de": "su_nghiep"}),
    ("/api/tu-vi/3-layer/chu-de-sau", {**BIRTH, "chu_de": "su_nghiep"}),
    ("/api/tu-vi/3-layer/gia-vi", {**BIRTH, "chu_de": "su_nghiep"}),
    ("/api/tu-vi/duyen-tho", {"birth": "1988-06-05T23:30", "gender": "nam"}),
    ("/api/tu-vi/so-sanh-duyen",
     {"me": {"birth": "1988-06-05T23:30", "gender": "nam"},
      "others": [{"birth": "1990-02-02T10:00", "gender": "nữ"}]}),
]


@pytest.mark.parametrize("path,body", LLM_ROUTES)
def test_guest_blocked_401(client, path, body):
    """Guest ẩn danh KHÔNG gọi được LLM (gate chặn TRƯỚC body → 0 LLM call)."""
    r = client.post(path, json=body)
    assert r.status_code == 401, f"{path}: guest phải 401, nhận {r.status_code}"


def test_invalid_service_key_401(client, monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", "right-key")
    r = client.post("/api/tu-vi/3-layer/narrative",
                    headers={"X-API-Key": "wrong", "X-User-Id": "u1"}, json={**BIRTH})
    assert r.status_code == 401


# ─── 2) Vượt ngưỡng → 429 ───────────────────────────────────────────────────
def test_session_user_rate_limited_429(client, monkeypatch):
    _as_session(monkeypatch, user_id=77, role="user")
    # seed bucket đầy đúng ngưỡng cho user 77 → request kế tiếp vượt → 429
    ratelimit._mem[f"{mod.LLM_BUCKET}:77"] = [time.time()] * mod.LLM_LIMIT
    r = client.post("/api/tu-vi/3-layer/narrative", json={**BIRTH})
    assert r.status_code == 429


def test_owner_exempt_from_rate_limit(client, monkeypatch):
    _as_session(monkeypatch, user_id=1, role="owner")
    ratelimit._mem[f"{mod.LLM_BUCKET}:1"] = [time.time()] * (mod.LLM_LIMIT + 5)
    r = client.post("/api/tu-vi/3-layer/narrative", json={**BIRTH})
    assert r.status_code == 200  # owner web miễn rate-limit (không tự chặn founder)


# ─── 3) force=true: chỉ owner mới được bypass cache ─────────────────────────
def _cap_force(monkeypatch):
    cap = {}
    import engine.atomization.narrative_gen as ng

    def capgen(three_layer, ls_in, force=False, feedback=None):
        cap["force"] = force
        return {"narrative": "x", "cached": False, "model": "m"}

    monkeypatch.setattr(ng, "generate_narrative", capgen, raising=True)
    return cap


def test_nonowner_force_downgraded(client, monkeypatch):
    _as_session(monkeypatch, user_id=55, role="user")
    cap = _cap_force(monkeypatch)
    r = client.post("/api/tu-vi/3-layer/narrative", json={**BIRTH, "force": True})
    assert r.status_code == 200
    assert cap["force"] is False  # non-owner KHÔNG ép sinh lại (không đốt LLM qua force)


def test_owner_force_allowed(client, monkeypatch):
    _as_session(monkeypatch, user_id=1, role="owner")
    cap = _cap_force(monkeypatch)
    r = client.post("/api/tu-vi/3-layer/narrative", json={**BIRTH, "force": True})
    assert r.status_code == 200
    assert cap["force"] is True


def test_valid_service_key_passes_gate(client, monkeypatch):
    """AppChat server-to-server (X-API-Key + X-User-Id) vẫn gọi được."""
    monkeypatch.setenv("YI_SYNC_API_KEY", "right-key")
    r = client.post("/api/tu-vi/3-layer/narrative",
                    headers={"X-API-Key": "right-key", "X-User-Id": "app-uid"},
                    json={**BIRTH})
    assert r.status_code == 200


# ─── 4) /from-birth: guest vẫn được, rate-limit nhẹ; /3-layer mở ────────────
def test_from_birth_guest_allowed(client):
    r = client.post("/api/tu-vi/3-layer/from-birth", json={**BIRTH})
    assert r.status_code == 200  # an sao thuần — guest vẫn xem được lá số


def test_from_birth_rate_limited(client, monkeypatch):
    _as_session(monkeypatch, user_id=33, role="user")
    ratelimit._mem[f"{mod.CAST_BUCKET}:33"] = [time.time()] * mod.CAST_LIMIT
    r = client.post("/api/tu-vi/3-layer/from-birth", json={**BIRTH})
    assert r.status_code == 429


def test_pure_3layer_render_open(client):
    r = client.post("/api/tu-vi/3-layer", json={
        "can": "mau", "chi": "thin", "menh_palace": "ty", "than_palace": "than",
        "cuc": "thuy_nhi_cuc", "gender": "M",
        "chinh_tinh_per_palace": {"ty": ["thien_dong"]}})
    assert r.status_code == 200  # render thuần (không LLM) — vẫn mở


# ─── 5) Route cấu trúc nặng (an sao/Bát Tự, KHÔNG LLM): guest VẪN dùng, nhưng
#        throttle nhẹ chống abuse CPU (bucket chung tuvi_cast). ───────────────
STRUCTURAL_ROUTES = [
    ("/api/tu-vi/hop-hon",
     {"birth1": "1988-06-05T23:30", "gender1": "nam",
      "birth2": "1990-02-02T10:00", "gender2": "nữ"}),
    ("/api/tu-vi/thien-luong", {"birth": "1988-06-05T23:30", "gender": "nam"}),
    ("/api/tu-vi/cung-sau", {"birth": "1988-06-05T23:30", "gender": "nam"}),
    ("/api/tu-vi/duyen", {"birth": "1988-06-05T23:30", "gender": "nam"}),
    ("/api/tu-vi/gia-dao",
     {"birth1": "1988-06-05T23:30", "gender1": "nam",
      "birth2": "1990-02-02T10:00", "gender2": "nữ"}),
    ("/api/tu-vi/dat-ten", {"birth_con": "2020-03-03T08:00"}),
    ("/api/tu-vi/luan-con", {"birth_con": "2020-03-03T08:00", "gender_con": "nam"}),
]


@pytest.mark.parametrize("path,body", STRUCTURAL_ROUTES)
def test_structural_guest_allowed(client, path, body):
    """Route cấu trúc (CPU, không LLM) KHÔNG hard-gate — guest vẫn dùng được."""
    r = client.post(path, json=body)
    assert r.status_code != 401, f"{path}: không nên chặn guest (chỉ throttle), nhận {r.status_code}"


@pytest.mark.parametrize("path,body", STRUCTURAL_ROUTES)
def test_structural_rate_limited(client, monkeypatch, path, body):
    """Vượt ngưỡng CPU (bucket tuvi_cast) → 429 cho cả route cấu trúc."""
    _as_session(monkeypatch, user_id=91, role="user")
    ratelimit._mem[f"{mod.CAST_BUCKET}:91"] = [time.time()] * mod.CAST_LIMIT
    r = client.post(path, json=body)
    assert r.status_code == 429, f"{path}: vượt ngưỡng phải 429, nhận {r.status_code}"
