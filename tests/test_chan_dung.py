"""Chân Dung khách hàng — tổng hợp deterministic 3 lá số + endpoint gate."""
from engine.chan_dung import build_chan_dung


def test_build_portrait_complete():
    r = build_chan_dung({"birth_datetime_local": "1988-06-05T23:30:00", "gender": "nam",
                         "name": "Test", "timezone": "Asia/Ho_Chi_Minh"})
    assert r["ok"] is True
    # Tử Vi mệnh có thật
    assert r["menh"]["menh_cung"] and r["menh"]["menh_chu"]
    assert isinstance(r["menh"]["chinh_tinh_tai_menh"], list)
    # Bát Tự cốt cách có nhật chủ + tính cách (tái dùng life_overview)
    assert r["cot_cach"]["nhat_chu"]
    # sản phẩm bệ phóng
    assert len(r["products"]) >= 2
    # paradigm note đọc đồng dạng
    assert "không" in r["paradigm_note"].lower()
    # depth v2: cách cục + đại vận hiện tại + hướng dẫn Bát Tự
    assert "cach_cuc" in r["menh"] and "dai_van_hien_tai" in r["menh"]
    assert "huong_dan" in r and isinstance(r["huong_dan"].get("su_nghiep"), list)


def test_la_so_input_builder():
    """build_la_so_input → per-palace + đại vận hiện tại (cho cách cục matcher)."""
    from engine.tu_vi.from_birth import cast_la_so_from_birth
    from engine.tu_vi.la_so_input_builder import build_la_so_input
    ls = cast_la_so_from_birth(birth_datetime_local="1988-06-05T23:30:00",
                               timezone="Asia/Ho_Chi_Minh", gender="nam")
    lsi = build_la_so_input(ls, "nam", birth_year=1988, now_year=2026)
    assert lsi["menh_palace"] and isinstance(lsi["chinh_tinh_per_palace"], dict)
    assert lsi["dai_van_hien_tai"] and lsi["dai_van_hien_tai"]["start_age"] <= 39 <= lsi["dai_van_hien_tai"]["end_age"]


def test_missing_birth():
    r = build_chan_dung({"gender": "nam"})
    assert r["ok"] is False and r["reason"] == "missing_birth"


def test_endpoint_login_gated():
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    assert c.get("/api/chan-dung").status_code in (401, 403)
    assert c.get("/api/chan-dung?person_key=self").status_code in (401, 403)


def test_sync_chan_dung_service_gated():
    """Cầu nối AppChat: /api/sync/chan-dung yêu cầu service key (X-API-Key)."""
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    r = c.post("/api/sync/chan-dung", json={"firebase_uid": "x", "person_key": "self"})
    # 503 = YI_SYNC_API_KEY chưa cấu hình (môi trường test) · 401 = key sai · cả hai = không lọt
    assert r.status_code in (401, 403, 503)
