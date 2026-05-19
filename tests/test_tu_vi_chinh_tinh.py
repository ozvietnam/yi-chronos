"""Tests for engine.tu_vi.chinh_tinh — 14 chính tinh schema loader."""

from __future__ import annotations

import pytest

from engine.tu_vi import (
    ALL_CHINH_TINH,
    ChinhTinh,
    get_chinh_tinh,
    list_chinh_tinh,
)
from engine.tu_vi.chinh_tinh import get_chinh_tinh_by_name


EXPECTED_STAR_IDS = {
    "tu_vi", "thien_co", "thai_duong", "vu_khuc", "thien_dong",
    "liem_trinh", "thien_phu", "thai_am", "tham_lang", "cu_mon",
    "thien_tuong", "thien_luong", "that_sat", "pha_quan",
}


def test_loads_14_chinh_tinh():
    assert len(ALL_CHINH_TINH) == 14
    ids = {s.id for s in ALL_CHINH_TINH}
    assert ids == EXPECTED_STAR_IDS


def test_each_star_has_required_fields():
    for s in ALL_CHINH_TINH:
        assert s.id
        assert s.ten_vi
        assert s.ten_zh
        assert s.ngu_hanh
        assert s.am_duong in ("âm", "dương")
        assert isinstance(s.chu_ve, list) and len(s.chu_ve) >= 2
        assert isinstance(s.dac_dia, list) and len(s.dac_dia) >= 1
        assert isinstance(s.keywords, list) and len(s.keywords) >= 3
        assert s.tich_cuc, f"{s.id}: missing tich_cuc"
        assert s.tieu_cuc, f"{s.id}: missing tieu_cuc"


def test_get_chinh_tinh_lookup():
    tu_vi = get_chinh_tinh("tu_vi")
    assert tu_vi.ten_vi == "Tử Vi"
    assert tu_vi.ten_zh == "紫微"
    assert tu_vi.ngu_hanh == "thổ"


def test_get_chinh_tinh_rejects_unknown():
    with pytest.raises(ValueError):
        get_chinh_tinh("not_a_star")


def test_get_chinh_tinh_by_name():
    s = get_chinh_tinh_by_name("Thái Dương")
    assert s.id == "thai_duong"
    assert s.ngu_hanh == "hỏa"


def test_list_chinh_tinh_returns_full_list():
    lst = list_chinh_tinh()
    assert len(lst) == 14
    assert all(isinstance(s, ChinhTinh) for s in lst)


def test_known_star_polarities():
    """Spot-check 5 stars with known yin/yang assignments."""
    cases = {
        "tu_vi": "âm",
        "thai_duong": "dương",
        "thai_am": "âm",
        "thien_phu": "dương",
        "thien_dong": "dương",
        "vu_khuc": "âm",
    }
    for star_id, polarity in cases.items():
        assert get_chinh_tinh(star_id).am_duong == polarity, f"{star_id} polarity mismatch"


def test_known_star_elements():
    cases = {
        "tu_vi": "thổ",
        "thai_duong": "hỏa",
        "thai_am": "thủy",
        "vu_khuc": "kim",
        "thien_co": "mộc",
    }
    for star_id, element in cases.items():
        assert get_chinh_tinh(star_id).ngu_hanh == element


def test_schema_is_json_serializable():
    import json
    stars_dict = [s.to_dict() for s in ALL_CHINH_TINH]
    s = json.dumps(stars_dict, ensure_ascii=False)
    decoded = json.loads(s)
    assert len(decoded) == 14


def test_api_chinh_tinh_endpoint():
    """Smoke test for /api/tu-vi/chinh-tinh list endpoint."""
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)
    response = client.get("/api/tu-vi/chinh-tinh")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert len(payload["stars"]) == 14
    # Check the first star has tich_cuc / tieu_cuc
    tu_vi = next(s for s in payload["stars"] if s["id"] == "tu_vi")
    assert tu_vi["tich_cuc"]
    assert tu_vi["tieu_cuc"]


def test_api_single_chinh_tinh_endpoint():
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)
    response = client.get("/api/tu-vi/chinh-tinh/thai_duong")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["star"]["ten_vi"] == "Thái Dương"


def test_api_single_chinh_tinh_not_found():
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)
    response = client.get("/api/tu-vi/chinh-tinh/nonexistent")
    assert response.status_code == 200
    assert response.json()["status"] == "not_found"
