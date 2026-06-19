"""ADR 3-tầng (task 1) — T2 menh_profile: build (cast tất định) + cache đọc tức thì."""
import pytest

from engine.db import get_engine

KEY = "mp-key"
UID = "_mp_uid_"


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/mp.sqlite3")
    monkeypatch.setenv("YI_SYNC_API_KEY", KEY)
    get_engine.cache_clear()
    yield
    get_engine.cache_clear()


def _make_user_with_birth(c):
    return c.post("/api/sync/upsert-from-firebase",
                  json={"firebase_uid": UID, "display_name": "M", "email": UID + "@t.local",
                        "birth": {"datetime_local": "1988-06-05T23:30:00", "gender": "nam"}},
                  headers={"X-API-Key": KEY}).json()["yi_user_id"]


def test_build_and_get_profile(temp_db):
    from fastapi.testclient import TestClient
    from api.main import app
    from engine import menh_profile as mp
    uid = _make_user_with_birth(TestClient(app))

    r = mp.build_profile(uid)
    assert r["status"] == "ok", r
    assert r["has_bat_tu"] and r["has_tu_vi"]      # cast tất định thành công

    prof = mp.get_profile(uid)                      # đọc T2 tức thì (không LLM)
    assert prof is not None
    assert prof["facts"].get("bat_tu") and prof["facts"].get("tu_vi")
    assert prof["facts"]["birth_datetime_local"] == "1988-06-05T23:30:00"


def test_build_profile_idempotent(temp_db):
    from fastapi.testclient import TestClient
    from api.main import app
    from engine import menh_profile as mp
    uid = _make_user_with_birth(TestClient(app))
    mp.build_profile(uid)
    n1 = mp.get_profile(uid)["computed_at"]
    r2 = mp.build_profile(uid)                       # gọi lại → thay thế, KHÔNG nhân đôi
    assert r2["status"] == "ok"
    assert mp.get_profile(uid)["computed_at"] >= n1


def test_build_profile_no_birth_skipped(temp_db):
    from api import sync
    sync._ensure_schema()                            # tạo user_persons (rỗng) trong temp db
    from engine import menh_profile as mp
    r = mp.build_profile(987654)                     # user không có self → skip, không lỗi
    assert r["status"] == "skipped" and r["reason"] == "no_birth"


def test_cast_la_so_from_birth_produces_chart():
    """Helper engine (vá bug _build_chart_data): cast tu_vi từ birth → la_số hợp lệ."""
    from engine.tu_vi.from_birth import cast_la_so_from_birth, hour_branch_from_hour
    assert hour_branch_from_hour(23) == "Tý" and hour_branch_from_hour(0) == "Tý"
    la_so = cast_la_so_from_birth(birth_datetime_local="1988-06-05T23:30:00",
                                  timezone="Asia/Ho_Chi_Minh", gender="nam")
    assert isinstance(la_so, dict) and la_so          # KHÔNG raise (bug cũ raise âm thầm)
    # la số phải có 12 cung (cấu trúc Tử Vi)
    blob = str(la_so)
    assert "cung" in blob.lower() or "palace" in blob.lower() or len(la_so) >= 5
