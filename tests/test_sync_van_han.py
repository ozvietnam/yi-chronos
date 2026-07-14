"""Cầu AppChat cho vận hạn Tử Vi — POST /api/sync/tu-vi/van-han (service-keyed).

Mirror engine van_han (P1 2026-07-14): block tất định Thể-Dụng + Tứ Hóa rọi cung,
grounded quote-or-silence. AppChat mặc định want_llm=False (nhanh/free); thiếu
year/month → tự lấy kỳ HIỆN TẠI giờ VN (phục vụ 'nguyệt vận hiện tại' + nhắc Lưu
Niên prvchat#46 C2).
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

UID = "_test_vanhan_uid_"
UID_NO_BIRTH = "_test_vanhan_nobirth_"
KEY = "test-vanhan-key"
_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", KEY)
    from api.main import app
    c = TestClient(app)
    H = {"X-API-Key": KEY}
    c.post("/api/sync/upsert-from-firebase",
           json={"firebase_uid": UID, "display_name": "T", "email": UID + "@t.local",
                 "birth": {"datetime_local": "1988-06-05T23:30:00", "gender": "nam"}},
           headers=H)
    c.post("/api/sync/upsert-from-firebase",
           json={"firebase_uid": UID_NO_BIRTH, "display_name": "N",
                 "email": UID_NO_BIRTH + "@t.local"},
           headers=H)
    yield c, H
    from engine.db import session_scope
    with session_scope(service=True) as conn:
        for uid in (UID, UID_NO_BIRTH):
            r = conn.execute(text("SELECT user_id FROM users WHERE firebase_uid=:u"),
                             {"u": uid}).fetchone()
            if r:
                conn.execute(text("DELETE FROM user_persons WHERE user_id=:i"), {"i": r[0]})
                conn.execute(text("DELETE FROM users WHERE user_id=:i"), {"i": r[0]})


def test_requires_service_key(client):
    c, _ = client
    assert c.post("/api/sync/tu-vi/van-han",
                  json={"firebase_uid": UID, "tang": "luu_nien"}).status_code == 401


def test_unknown_uid_404(client):
    c, H = client
    assert c.post("/api/sync/tu-vi/van-han",
                  json={"firebase_uid": "nope_uid", "tang": "luu_nien"},
                  headers=H).status_code == 404


def test_missing_birth_422(client):
    c, H = client
    assert c.post("/api/sync/tu-vi/van-han",
                  json={"firebase_uid": UID_NO_BIRTH, "tang": "luu_nien"},
                  headers=H).status_code == 422


def test_luu_nien_explicit_year(client):
    c, H = client
    r = c.post("/api/sync/tu-vi/van-han",
               json={"firebase_uid": UID, "tang": "luu_nien", "year": 2026},
               headers=H)
    assert r.status_code == 200
    d = r.json()
    assert d["available"] is True
    blk = d["block"]
    assert blk["tang"] == "luu_nien" and blk["year"] == 2026
    assert blk["year_can_chi"] == "Bính Ngọ"        # khớp test engine P1
    assert blk["cung_the"] and blk["vi_tri"]         # Thể-Dụng có mặt
    assert isinstance(blk["tu_hoa_van"], list) and len(blk["tu_hoa_van"]) == 4
    assert d["luan"] == ""                            # want_llm mặc định False


def test_luu_nguyet_defaults_to_current_period(client):
    """Không truyền year/month → kỳ hiện tại giờ VN (nguyệt vận NGAY BÂY GIỜ)."""
    c, H = client
    now = datetime.now(_TZ)
    r = c.post("/api/sync/tu-vi/van-han",
               json={"firebase_uid": UID, "tang": "luu_nguyet"}, headers=H)
    assert r.status_code == 200
    blk = r.json()["block"]
    assert blk["tang"] == "luu_nguyet"
    assert blk["year"] == now.year and blk["month"] == now.month


def test_tuan_defaults_from_today(client):
    """Tuần không truyền → suy từ ngày hôm nay (1-10 thượng · 11-20 trung · 21+ hạ)."""
    c, H = client
    now = datetime.now(_TZ)
    expected_tuan = 1 if now.day <= 10 else (2 if now.day <= 20 else 3)
    r = c.post("/api/sync/tu-vi/van-han",
               json={"firebase_uid": UID, "tang": "tuan"}, headers=H)
    assert r.status_code == 200
    blk = r.json()["block"]
    assert blk["tang"] == "tuan" and blk["tuan"] == expected_tuan
    assert blk["year"] == now.year and blk["month"] == now.month


def test_dai_van_requires_cycle_index(client):
    c, H = client
    r = c.post("/api/sync/tu-vi/van-han",
               json={"firebase_uid": UID, "tang": "dai_van"}, headers=H)
    assert r.status_code == 400
    ok = c.post("/api/sync/tu-vi/van-han",
                json={"firebase_uid": UID, "tang": "dai_van", "cycle_index": 4},
                headers=H)
    assert ok.status_code == 200 and ok.json()["block"]["tang"] == "dai_van"


def test_invalid_tang_400(client):
    c, H = client
    assert c.post("/api/sync/tu-vi/van-han",
                  json={"firebase_uid": UID, "tang": "gio_hoang_dao"},
                  headers=H).status_code == 400


def test_month_out_of_range_400(client):
    c, H = client
    assert c.post("/api/sync/tu-vi/van-han",
                  json={"firebase_uid": UID, "tang": "luu_nguyet", "year": 2026,
                        "month": 13},
                  headers=H).status_code == 400
