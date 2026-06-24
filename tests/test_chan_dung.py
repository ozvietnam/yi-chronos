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


def test_missing_birth():
    r = build_chan_dung({"gender": "nam"})
    assert r["ok"] is False and r["reason"] == "missing_birth"


def test_endpoint_login_gated():
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    assert c.get("/api/chan-dung").status_code in (401, 403)
    assert c.get("/api/chan-dung?person_key=self").status_code in (401, 403)
