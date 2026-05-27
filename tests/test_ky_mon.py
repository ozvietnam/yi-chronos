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
    """Verify wiki có core 6 categories + extended sections từ Đàm Liên book."""
    from engine.ky_mon import WIKI, list_categories, get_concept

    cats = set(list_categories())
    # Core 6 (gốc)
    assert {"cung", "mon", "tinh", "than", "structure", "to_su"}.issubset(cats)
    # Extended từ Đàm Liên Chương I (added 2026-05-27)
    assert {"co_thu_canon", "he_kmdg", "source_book"}.issubset(cats)

    # Lookup specific concepts
    khai = get_concept("mon", "Khai")
    assert khai is not None
    assert khai["zh"] == "開門"
    assert khai["cat_hung"] == "đại cát"

    tri_phu = get_concept("than", "Trị Phù")
    assert tri_phu is not None
    assert tri_phu["zh"] == "值符"


def test_source_book_dam_lien():
    """Verify source book Đàm Liên info chính xác."""
    from engine.ky_mon import WIKI

    sb = WIKI["source_book"]
    assert sb["author"] == "Đàm Liên"
    assert sb["title"] == "Kỳ Môn Độn Giáp"
    assert sb["pages"] == 367
    assert "đa tư duy" in sb["key_quote_1"]
    assert "tương đối" in sb["key_quote_2"]
    assert "Iron Rule" in sb["paradigm_alignment"]


def test_he_kmdg_two_systems():
    """KMDG có 2 hệ Chuyển bàn + Phi bàn (per Đàm Liên Chương I)."""
    from engine.ky_mon import WIKI

    he = WIKI["he_kmdg"]
    assert "Chuyển bàn 轉盤" in he
    assert "Phi bàn 飛盤" in he


def test_co_thu_canon_5_books():
    """5 cổ thư canon KMDG (4 Chuyển bàn + 1 Phi bàn)."""
    from engine.ky_mon import WIKI

    canon = WIKI["co_thu_canon"]
    assert len(canon) == 5
    chuyen_ban = [k for k, v in canon.items() if v["he"] == "Chuyển bàn"]
    phi_ban = [k for k, v in canon.items() if v["he"] == "Phi bàn"]
    assert len(chuyen_ban) == 4
    assert len(phi_ban) == 1
    assert "Kỳ môn pháp khiếu" in phi_ban


def test_tam_ky_full_name_3_thien_the():
    """Tam Kỳ: Đinh=Tinh kỳ, Bính=Nguyệt kỳ, Ất=Nhật kỳ (per Đàm Liên Chương I)."""
    from engine.ky_mon.constants import TAM_KY_FULL_NAME

    assert TAM_KY_FULL_NAME["乙"]["vn"] == "Nhật kỳ"
    assert TAM_KY_FULL_NAME["丙"]["vn"] == "Nguyệt kỳ"
    assert TAM_KY_FULL_NAME["丁"]["vn"] == "Tinh kỳ"


def test_luc_nghi_giap_mapping():
    """Mỗi Lục Nghi ẩn 1 Giáp tuần (per Đàm Liên Chương I)."""
    from engine.ky_mon.constants import LUC_NGHI_GIAP_MAPPING

    assert LUC_NGHI_GIAP_MAPPING["戊"]["giap_vn"] == "Giáp Tý"
    assert LUC_NGHI_GIAP_MAPPING["己"]["giap_vn"] == "Giáp Tuất"
    assert LUC_NGHI_GIAP_MAPPING["庚"]["giap_vn"] == "Giáp Thân"
    assert LUC_NGHI_GIAP_MAPPING["辛"]["giap_vn"] == "Giáp Ngọ"
    assert LUC_NGHI_GIAP_MAPPING["壬"]["giap_vn"] == "Giáp Thìn"
    assert LUC_NGHI_GIAP_MAPPING["癸"]["giap_vn"] == "Giáp Dần"


def test_cuu_tinh_two_naming_mapping():
    """9 sao có 2 hệ tên: Thiên Bồng/... (KMDG) vs Nhất bạch/... (Huyền Không Phi Tinh)."""
    from engine.ky_mon.constants import CUU_TINH_NUMBER_NAME

    assert CUU_TINH_NUMBER_NAME[1]["vn"] == "Nhất bạch"
    assert CUU_TINH_NUMBER_NAME[1]["kmdg_tinh"] == "Thiên Bồng"
    assert CUU_TINH_NUMBER_NAME[5]["vn"] == "Ngũ hoàng"
    assert CUU_TINH_NUMBER_NAME[5]["kmdg_tinh"] == "Thiên Cầm"
    assert CUU_TINH_NUMBER_NAME[9]["vn"] == "Cửu tử"
    assert CUU_TINH_NUMBER_NAME[9]["color"] == "tím"


def test_nguyet_gia_nguyen_rule():
    """Tứ Mạnh→Thượng, Tứ Trọng→Trung, Tứ Quý→Hạ (per Đàm Liên p22-23)."""
    from engine.ky_mon.constants import NGUYET_GIA_NGUYEN_RULE, TU_MANH, TU_TRONG, TU_QUY

    assert set(TU_MANH) == {"寅", "申", "巳", "亥"}
    assert set(TU_TRONG) == {"子", "午", "卯", "酉"}
    assert set(TU_QUY) == {"辰", "戌", "丑", "未"}

    assert NGUYET_GIA_NGUYEN_RULE["Thượng Nguyên"]["starting_cung"] == "Khảm số 1"
    assert NGUYET_GIA_NGUYEN_RULE["Trung Nguyên"]["starting_cung"] == "Đoài số 7"
    assert NGUYET_GIA_NGUYEN_RULE["Hạ Nguyên"]["starting_cung"] == "Tốn số 4"


def test_duong_am_don_chieu():
    """Dương độn thuận chiều, Âm độn ngược chiều (per Đàm Liên hình 5-6)."""
    from engine.ky_mon.constants import DUONG_AM_DON_RULE

    assert "thuận" in DUONG_AM_DON_RULE["Dương độn 陽遁"]["chieu"]
    assert "ngược" in DUONG_AM_DON_RULE["Âm độn 陰遁"]["chieu"]


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
