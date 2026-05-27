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


def test_cuu_tinh_cat_hung_corrected():
    """9 sao cat_hung CORRECTED per Đàm Liên Chương I phần IV (batch 2).

    - 5 cát: Phụ Cầm Tâm (đại cát), Xung Nhậm (tiểu cát)
    - 4 hung: Bồng Nhuế (đại hung), Trụ Anh (tiểu hung)
    """
    from engine.ky_mon.constants import TINH_CAT_HUNG

    # Đại cát = 3 sao
    assert TINH_CAT_HUNG["輔"] == "đại cát"  # Phụ
    assert TINH_CAT_HUNG["禽"] == "đại cát"  # Cầm
    assert TINH_CAT_HUNG["心"] == "đại cát"  # Tâm

    # Tiểu cát = 2 sao
    assert TINH_CAT_HUNG["沖"] == "cát"      # Xung
    assert TINH_CAT_HUNG["任"] == "cát"      # Nhậm

    # Đại hung = 2 sao
    assert TINH_CAT_HUNG["蓬"] == "đại hung"  # Bồng
    assert TINH_CAT_HUNG["芮"] == "đại hung"  # Nhuế

    # Tiểu hung = 2 sao (corrected from "trung bình")
    assert TINH_CAT_HUNG["柱"] == "hung"      # Trụ
    assert TINH_CAT_HUNG["英"] == "hung"      # Anh


def test_am_duong_ban_4_tang():
    """Âm Dương Bàn = 4 tầng (Địa/Môn/Thiên/Thần) per Đàm Liên phần IV."""
    from engine.ky_mon import WIKI

    sec = WIKI["am_duong_ban_4_tang"]
    assert sec["tang_1_dia_ban"]["name"] == "Địa Bàn 地盤"
    assert sec["tang_4_than_ban"]["name"] == "Thần Bàn 神盤"
    assert "Trung cung" in sec["trung_cung_trick"]


def test_cach_cuc_detect_founder_hinh_cach():
    """Founder data (1988-06-05 23:30) phải detect được Hình Cách (đại hung).

    Per Đàm Liên Chương I phần V (page 49):
    - Hình Cách: Thiên Bàn Lục Canh, Địa Bàn Lục Kỷ (cùng cung)
    - Founder bàn: cung Khảm có Thiên Canh + Địa Kỷ → match
    """
    from engine.ky_mon import cast

    r = cast(1988, 6, 5, 23, 30)
    detected_names = {cc["name"] for cc in r["cach_cuc_detected"]}
    assert "Hình Cách" in detected_names

    hinh_cach = next(cc for cc in r["cach_cuc_detected"] if cc["name"] == "Hình Cách")
    assert hinh_cach["loai"] == "đại hung"
    assert hinh_cach["zh"] == "刑格"


def test_cach_cuc_canon_25_entries():
    """CACH_CUC_CANON có ít nhất 25 entries (13 cát + 12 hung)."""
    from engine.ky_mon.constants import CACH_CUC_CANON

    assert len(CACH_CUC_CANON) >= 25
    cat = [k for k, v in CACH_CUC_CANON.items() if "cát" in v["loai"]]
    hung = [k for k, v in CACH_CUC_CANON.items() if "hung" in v["loai"]]
    assert len(cat) >= 12
    assert len(hung) >= 10


def test_bo_cuc_numbers_4320_1080_72_18():
    """4 cấp số bố cục KMDG (Đàm Liên Chương II)."""
    from engine.ky_mon import WIKI

    bc = WIKI["bo_cuc_numbers"]
    assert "4320" in bc
    assert "1080" in bc
    assert "72" in bc
    assert "18_dia_ban" in bc
    assert "Yên Ba Chước Du Ca" in bc["18_dia_ban"]


def test_tiet_vs_trung_khi_12_12():
    """24 tiết khí = 12 Tiết + 12 Trung Khí (Đàm Liên Chương II)."""
    from engine.ky_mon import WIKI

    tk = WIKI["tiet_vs_trung_khi"]
    assert len(tk["12_tiet"]) == 12
    assert len(tk["12_trung_khi"]) == 12
    assert "Lập Xuân" in tk["12_tiet"]
    assert "Hạ Chí" in tk["12_trung_khi"]


def test_phu_dau_rule_3_nguyen():
    """Phù Đầu rule: Thượng=Tứ Trọng, Trung=Tứ Mạnh, Hạ=Tứ Quý."""
    from engine.ky_mon import WIKI

    pd = WIKI["phu_dau_rule"]
    assert "Tứ Trọng" in pd["thuong_nguyen"]
    assert "Tứ Mạnh" in pd["trung_nguyen"]
    assert "Tứ Quý" in pd["ha_nguyen"]


def test_tri_nhuan_explain_chabu_zhirun():
    """Wiki giải thích chabu vs zhirun (methods trong kinqimen)."""
    from engine.ky_mon import WIKI

    tn = WIKI["tri_nhuan_chabu"]
    assert "chabu_拆補" in tn
    assert "zhirun_置閏" in tn
    assert tn["chabu_拆補"]["library_value"] == "method='chabu' trong kinqimen (default)"


def test_task_profiles_16_tasks():
    """16 task profiles (15 cụ thể + Quan-sát chung)."""
    from engine.ky_mon import TASK_PROFILES, list_tasks

    assert len(TASK_PROFILES) == 16
    assert "Kết hôn" in TASK_PROFILES
    assert "Chữa bệnh" in TASK_PROFILES
    assert "Quan-sát chung" in TASK_PROFILES

    tasks = list_tasks()
    assert len(tasks) == 16
    assert all("key" in t and "label" in t for t in tasks)


def test_analyze_for_task_ket_hon_founder():
    """Founder data + task 'Kết hôn' should rank hướng tốt/tránh."""
    from engine.ky_mon import cast, analyze_for_task

    state = cast(1988, 6, 5, 23, 30)
    analysis = analyze_for_task(state, "Kết hôn")

    assert analysis["task"] == "Kết hôn"
    assert analysis["task_label"] == "Kết hôn / Cưới gả"
    assert "Đàm Liên" in analysis["note"]

    # huong_tot có 3 entries (sorted by score desc)
    assert len(analysis["huong_tot"]) <= 3
    if analysis["huong_tot"]:
        scores = [h["score"] for h in analysis["huong_tot"]]
        assert scores == sorted(scores, reverse=True)
        assert all(h["score"] > 0 for h in analysis["huong_tot"])

    # huong_tranh có scores âm
    if analysis["huong_tranh"]:
        assert all(h["score"] < 0 for h in analysis["huong_tranh"])

    # cách cục relevant: founder có Hình Cách → avoid cho Kết hôn
    cc_names = {cc["name"] for cc in analysis["cach_cuc_relevant"]}
    assert "Hình Cách" in cc_names
    hinh_cach = next(cc for cc in analysis["cach_cuc_relevant"] if cc["name"] == "Hình Cách")
    assert hinh_cach["task_match"] == "avoid"


def test_analyze_for_task_quan_sat_chung_no_ranking():
    """Task 'Quan-sát chung' không có ranking."""
    from engine.ky_mon import cast, analyze_for_task

    state = cast(1988, 6, 5, 23, 30)
    analysis = analyze_for_task(state, "Quan-sát chung")

    assert analysis["task"] == "Quan-sát chung"
    assert analysis["huong_tot"] == []
    assert analysis["huong_tranh"] == []


def test_analyze_for_task_chua_benh_emphasizes_thien_tam():
    """Task 'Chữa bệnh' favor Thiên Tâm + Hưu Trá per Đàm Liên."""
    from engine.ky_mon import TASK_PROFILES

    p = TASK_PROFILES["Chữa bệnh"]
    assert "心" in p["favored_tinh"]  # Thiên Tâm
    assert "Hưu Trá" in p["favored_cach_cuc"]
    assert "uống thuốc" in p["note"].lower() or "y dược" in p["note"].lower()


def test_api_cast_with_task():
    """API endpoint trả task_analysis khi request có task."""
    from api.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    r = client.post("/api/ky-mon/cast", json={
        "year": 1988, "month": 6, "day": 5, "hour": 23, "minute": 30,
        "task": "Kết hôn",
    })
    assert r.status_code == 200
    j = r.json()
    assert "task_analysis" in j["ky_mon_state"]
    assert j["ky_mon_state"]["task_analysis"]["task"] == "Kết hôn"


def test_api_tasks_endpoint():
    """GET /api/ky-mon/tasks return 16 tasks."""
    from api.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    r = client.get("/api/ky-mon/tasks")
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "ok"
    assert len(j["tasks"]) == 16


def test_detect_cach_cuc_returns_list():
    """detect_cach_cuc() trả về list (có thể empty)."""
    from engine.ky_mon.cast import detect_cach_cuc

    # Empty case
    result = detect_cach_cuc({}, {})
    assert isinstance(result, list)
    assert result == []

    # Phi Điểu Trật Huyệt case: Thiên Bính + Địa Mậu (Lục Giáp ẩn)
    result = detect_cach_cuc({"離": "丙"}, {"離": "戊"})
    names = [cc["name"] for cc in result]
    assert "Phi Điểu Trật Huyệt" in names


def test_theo_3_tranh_5_rule():
    """Quy tắc 'Theo 3 tránh 5' — 3 cát môn + 5 hung môn."""
    from engine.ky_mon import WIKI

    rule = WIKI["theo_3_tranh_5"]
    assert set(rule["cat_mon"]) == {"Khai môn", "Hưu môn", "Sinh môn"}
    assert set(rule["hung_mon"]) == {"Thương môn", "Đỗ môn", "Cảnh môn", "Tử môn", "Kinh môn"}
    assert len(rule["cat_mon"]) == 3
    assert len(rule["hung_mon"]) == 5


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
