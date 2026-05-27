"""Tests for engine Kỳ Môn Độn Giáp.

Founder data: 1988-06-05 23:30 (giờ Tý đầu).
Ground truth verified against vendored kinqimen 0.0.6.6:
  - Tứ trụ: 戊辰年戊午月壬辰日庚子時
  - Tiết khí: 芒種 (Mang Chủng)
  - Bài cục: 陽遁九局下元 (Dương Cục 9 Hạ nguyên)
"""

import pytest
from fastapi.testclient import TestClient


def test_engine_cast_founder_data():
    """Cast với founder data → verify 4 trụ + tiết khí + cục."""
    from engine.ky_mon import cast

    r = cast(1988, 6, 5, 23, 30)

    # Tứ trụ
    assert r["tu_tru_zh"] == "戊辰年戊午月壬辰日庚子時"
    assert r["tu_tru"]["year"]["zh"] == "戊辰"
    assert r["tu_tru"]["year"]["can"]["vn"] == "Mậu"
    assert r["tu_tru"]["year"]["chi"]["vn"] == "Thìn"
    assert r["tu_tru"]["hour"]["can"]["vn"] == "Canh"
    assert r["tu_tru"]["hour"]["chi"]["vn"] == "Tý"

    # Tiết khí
    assert r["tiet_khi_zh"] == "芒種"
    assert r["tiet_khi_vn"] == "Mang Chủng"

    # Bài cục
    assert r["bai_cuc"]["duong_am"] == "Dương Cục"
    assert r["bai_cuc"]["cuc_so"] == 9
    assert r["bai_cuc"]["nguyen"] == "Hạ nguyên"


def test_engine_cast_9_cung_structure():
    """Verify 9 cung × các yếu tố đầy đủ."""
    from engine.ky_mon import cast

    r = cast(1988, 6, 5, 23, 30)

    # Thiên bàn + Địa bàn: 9 cung (8 cung + Trung)
    assert len(r["thien_ban"]) == 9
    assert len(r["dia_ban"]) == 9

    # Mỗi cung có cung_vn + can_vn + ngu_hanh
    for cell in r["thien_ban"]:
        assert "cung_vn" in cell
        assert "can_vn" in cell
        assert cell["cung_vn"] in {"Khảm", "Cấn", "Chấn", "Tốn", "Ly", "Khôn", "Đoài", "Càn", "Trung"}

    # 8 môn (không có Trung)
    assert len(r["mon"]) == 8
    for cell in r["mon"]:
        assert "mon_vn" in cell
        assert cell["mon_vn"] in {"Hưu", "Sinh", "Thương", "Đỗ", "Cảnh", "Tử", "Kinh", "Khai"}
        assert cell["cat_hung"] in {"cát", "đại cát", "trung bình", "hung", "đại hung"}

    # 9 tinh
    assert len(r["tinh"]) >= 8  # có thể 8-9 tùy bố trí (Thiên Cầm gộp Trung)
    for cell in r["tinh"]:
        assert cell["tinh_vn"].startswith("Thiên")

    # 8 thần
    assert len(r["than"]) == 8


def test_engine_cast_paradigm_note():
    """Verify paradigm note xuất hiện trong output."""
    from engine.ky_mon import cast

    r = cast(1988, 6, 5, 23, 30)
    assert "đồng dạng" in r["paradigm_note"]
    assert "predict" in r["paradigm_note"].lower()


def test_engine_methods():
    """Test 4 methods: chabu, zhirun, minute, gpan."""
    from engine.ky_mon import cast

    for method in ["chabu", "zhirun"]:
        r = cast(1988, 6, 5, 23, 30, method=method)
        assert r["method"] == method
        assert r["tu_tru_zh"]  # has 4 pillars

    # gpan (Golden Mirror daily) — khác output structure
    rg = cast(1988, 6, 5, 23, 30, method="gpan")
    assert rg["method"] == "gpan"
    assert "tinh" in rg
    assert "mon" in rg


def test_wiki_categories():
    """Verify wiki có đủ 6 categories."""
    from engine.ky_mon import WIKI, list_categories, get_concept

    cats = list_categories()
    assert set(cats) == {"cung", "mon", "tinh", "than", "structure", "to_su"}

    # Lookup specific concepts
    khai = get_concept("mon", "Khai")
    assert khai is not None
    assert khai["zh"] == "開門"
    assert khai["cat_hung"] == "đại cát"

    tri_phu = get_concept("than", "Trị Phù")
    assert tri_phu is not None
    assert tri_phu["zh"] == "值符"


def test_to_su_paradigm():
    """Verify tổ sư paradigm Lưu Bá Ôn được ghi nhận."""
    from engine.ky_mon import WIKI

    to_su = WIKI["to_su"]
    assert to_su["name"] == "Lưu Bá Ôn"
    assert "Trần" not in to_su["name"]  # không nhầm với Trần Đoàn (Tử Vi)
    assert "1311" in to_su["birth"]
    assert "lineage" in to_su


def test_api_cast_endpoint():
    """Test POST /api/ky-mon/cast end-to-end."""
    from api.main import app

    client = TestClient(app)
    r = client.post("/api/ky-mon/cast", json={
        "year": 1988, "month": 6, "day": 5, "hour": 23, "minute": 30
    })
    assert r.status_code == 200
    j = r.json()
    assert "ky_mon_state" in j
    assert j["ky_mon_state"]["tu_tru_zh"] == "戊辰年戊午月壬辰日庚子時"
    assert j["ky_mon_state"]["tiet_khi_vn"] == "Mang Chủng"


def test_api_wiki_endpoint():
    """Test GET /api/ky-mon/wiki end-to-end."""
    from api.main import app

    client = TestClient(app)
    r = client.get("/api/ky-mon/wiki")
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "ok"
    assert "cung" in j["wiki"]
    assert "to_su" in j["wiki"]


def test_api_cast_methods():
    """Test 4 methods qua API."""
    from api.main import app

    client = TestClient(app)
    for method in ["chabu", "zhirun", "gpan"]:
        r = client.post("/api/ky-mon/cast", json={
            "year": 1988, "month": 6, "day": 5, "hour": 23, "minute": 30,
            "method": method
        })
        assert r.status_code == 200, f"method={method} failed: {r.text}"
        assert r.json()["ky_mon_state"]["method"] == method


def test_no_predict_language_in_paradigm_note():
    """Paradigm Iron Rule #4 + #6: KHÔNG dùng predict-tone."""
    from engine.ky_mon import cast

    r = cast(1988, 6, 5, 23, 30)
    note = r["paradigm_note"].lower()
    # Đảm bảo có wording đúng paradigm
    assert "đồng dạng" in note or "phản chiếu" in note
    # Đảm bảo có warning không predict
    assert "không" in note and ("predict" in note or "dự đoán" in note or "tuyệt đối" in note)
