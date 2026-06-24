"""Tests cho engine.tinh_duyen.cau_hoi_router (trả lời câu hỏi theo tuổi) +
engine.tinh_duyen.gieo_que_quyet_dinh (Mai Hoa decision helper, paradigm đọc đồng dạng).

PARADIGM (Iron Rule #4/#6/#8): KHÔNG bói, KHÔNG phán có/không. Câu QUYẾT ĐỊNH →
flag gieo quẻ Mai Hoa (KHÔNG chốt từ lá số). Câu 'khắc chồng' → QUA chan_doan_cap_do.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from engine.tinh_duyen.cau_hoi_router import tra_loi_cau_hoi_tuoi
from engine.tinh_duyen.gieo_que_quyet_dinh import (
    METHOD_ID as GIEO_METHOD_ID,
    gieo_que_tinh_duyen,
)
from engine.tinh_duyen.reading import read_tinh_duyen

# Lá nữ có Mệnh chính tinh + cung Phu Thê đầy đủ.
_BIRTH_27 = "1999-03-15T14:30"   # ~27 (nhóm 26-30)
_BIRTH_17 = "2009-05-10T08:00"   # ~17 (nhóm 16-20)
_BIRTH_33 = "1993-07-07T06:00"   # ~33 (nhóm 31-35)

# Từ cấm verdict phán-vào-người (TUYỆT ĐỐI không lọt câu trả lời dạng verdict trần).
FORBIDDEN_PERSON_VERDICTS = [
    "em sẽ khắc chồng", "số cô quả", "chắc chắn ly hôn",
    "sẽ không lấy được chồng", "mệnh em là khắc chồng",
]

ROUTER_ITEM_KEYS = {
    "cau_hoi", "he_tra_loi", "tra_loi", "can_gieo_que", "can_la_so_doi",
    "do_tin", "section_nguon", "tan_suat",
}


# --------------------------------------------------------------------------- #
# VIỆC 1 — cau_hoi_router
# --------------------------------------------------------------------------- #
def _reading(birth: str) -> dict:
    return read_tinh_duyen(birth, gender="nữ", as_of_year=2026)


def test_router_returns_list_with_contract_keys():
    out = _reading(_BIRTH_27)
    res = tra_loi_cau_hoi_tuoi(out, age=27)
    assert isinstance(res, list) and res
    for item in res:
        assert ROUTER_ITEM_KEYS.issubset(item.keys()), \
            f"thiếu khoá: {ROUTER_ITEM_KEYS - set(item.keys())}"
        assert item["cau_hoi"]
        assert item["tra_loi"]
        assert item["do_tin"] in ("cao", "trung", "thấp")


@pytest.mark.parametrize("age,expect_question_substr", [
    (17, "khó lấy chồng"),       # nhóm 16-20
    (27, "năm vàng"),            # nhóm 26-30
    (33, "ly hôn"),              # nhóm 31-35
])
def test_router_picks_age_group(age, expect_question_substr):
    """Chọn đúng nhóm tuổi từ age — mỗi nhóm có câu đặc trưng riêng."""
    out = _reading(_BIRTH_27)  # reading nào cũng được; router chọn nhóm theo `age`.
    res = tra_loi_cau_hoi_tuoi(out, age=age)
    assert res, f"tuổi {age} phải có câu hỏi"
    joined = " ".join((q["cau_hoi"] or "").lower() for q in res)
    assert expect_question_substr in joined, \
        f"tuổi {age} phải có câu đặc trưng chứa {expect_question_substr!r}"


def test_router_age_clamps_out_of_range():
    """Tuổi ngoài biên (12 và 70) clamp vào nhóm đầu/cuối, KHÔNG crash/rỗng."""
    out = _reading(_BIRTH_27)
    young = tra_loi_cau_hoi_tuoi(out, age=12)
    old = tra_loi_cau_hoi_tuoi(out, age=70)
    assert young and old


def test_router_age_falls_back_to_reading_input():
    """age=None -> lấy từ reading_output['input']['tuoi']."""
    out = _reading(_BIRTH_27)
    res = tra_loi_cau_hoi_tuoi(out, age=None)
    assert res
    # Tuổi 27 -> nhóm 26-30 có câu 'năm vàng kết hôn'.
    assert any("năm vàng" in (q["cau_hoi"] or "").lower() for q in res)


def test_router_decision_question_flags_gieo_que():
    """Câu QUYẾT ĐỊNH nhị nguyên (can_gieo_que) → tra_loi gợi gieo quẻ Mai Hoa,
    he_tra_loi='mai_hoa', do_tin='thấp' — KHÔNG chốt từ lá số."""
    out = _reading(_BIRTH_27)
    res = tra_loi_cau_hoi_tuoi(out, age=27)
    decision = [q for q in res if q["can_gieo_que"]]
    assert decision, "nhóm 26-30 phải có ít nhất 1 câu quyết định (đợi/chấp nhận)"
    for q in decision:
        assert q["he_tra_loi"] == "mai_hoa"
        assert q["tra_loi"].startswith("Câu này nên gieo quẻ Mai Hoa quyết định:")
        assert q["do_tin"] == "thấp"


def test_router_la_so_doi_question_flags_so_sanh_duyen():
    """Câu cần lá số người kia (can_la_so_doi, KHÔNG quyết định) → gợi so-sánh-duyên."""
    out = _reading("2005-09-09T10:00")  # ~21 (nhóm 21-25 có câu 'hai lá số có hợp')
    res = tra_loi_cau_hoi_tuoi(out, age=21)
    la_so_doi = [q for q in res
                 if q["can_la_so_doi"] and not q["can_gieo_que"]]
    assert la_so_doi, "nhóm 21-25 phải có câu cần lá số đôi (không phải quyết định)"
    for q in la_so_doi:
        assert "so-sánh-duyên" in q["tra_loi"]


def test_router_khac_chong_via_cham_cap_not_verdict():
    """Câu 'có khắc chồng?' trả QUA chan_doan_cap_do (cấp + lộ trình constructive),
    KHÔNG verdict 'có/không'."""
    out = _reading(_BIRTH_27)
    res = tra_loi_cau_hoi_tuoi(out, age=27)
    khac = [q for q in res if "khắc chồng" in (q["cau_hoi"] or "").lower()]
    assert khac, "nhóm 26-30 phải có câu 'có khắc chồng?'"
    for q in khac:
        assert q["section_nguon"] == "chan_doan_cap_do"
        low = q["tra_loi"].lower()
        # Phải nói tới CẤP/độ thử thách + KHÔNG verdict.
        assert ("mức độ thử thách" in low or "cấp" in low)
        for bad in FORBIDDEN_PERSON_VERDICTS:
            assert bad not in low, f"verdict phán-vào-người lọt: {bad!r}"


def test_router_answer_grounded_not_fabricated():
    """Câu trả lời rút TỪ section thật (không bịa): câu cung Phu Thê phải nhắc chính
    tinh / branch thật của lá số."""
    out = _reading(_BIRTH_27)
    res = tra_loi_cau_hoi_tuoi(out, age=27)
    pt = [q for q in res if q["section_nguon"] == "cung_phu_the_tuvi"]
    assert pt, "phải có câu route vào cung_phu_the_tuvi"
    branch = out["cung_phu_the_tuvi"]["phu_the_branch"]
    assert any(branch in q["tra_loi"] for q in pt), \
        "câu cung Phu Thê phải ground branch thật của lá số"


@pytest.mark.parametrize("birth", [_BIRTH_17, _BIRTH_27, _BIRTH_33])
def test_router_no_person_verdict_anywhere(birth):
    """Không câu trả lời nào chứa verdict phán-vào-người dạng trần."""
    out = _reading(birth)
    res = tra_loi_cau_hoi_tuoi(out, age=out["input"]["tuoi"])
    for q in res:
        low = q["tra_loi"].lower()
        for bad in FORBIDDEN_PERSON_VERDICTS:
            assert bad not in low, f"{birth}: verdict lọt câu trả lời: {bad!r}"


# --------------------------------------------------------------------------- #
# Tích hợp: reading.py có key 'cau_hoi_tuoi' + GIỮ key cũ
# --------------------------------------------------------------------------- #
def test_reading_has_cau_hoi_tuoi_key():
    out = _reading(_BIRTH_27)
    assert "cau_hoi_tuoi" in out
    assert isinstance(out["cau_hoi_tuoi"], list) and out["cau_hoi_tuoi"]
    for item in out["cau_hoi_tuoi"]:
        assert ROUTER_ITEM_KEYS.issubset(item.keys())


def test_reading_question_text_not_scrubbed():
    """REGRESSION: field 'cau_hoi' (câu hỏi của user, vd 'Tôi có khắc chồng không?')
    KHÔNG bị _scrub_tree thay placeholder — nếu không UI hiển thị câu hỏi thành
    '[lời cổ … đã được lược]'. Câu hỏi là khái-niệm-phân-tích hợp lệ."""
    out = _reading(_BIRTH_27)
    items = out["cau_hoi_tuoi"]
    # Có câu chứa 'khắc chồng' và câu đó PHẢI giữ nguyên text, không placeholder.
    khac = [q for q in items if "khắc chồng" in (q["cau_hoi"] or "").lower()]
    assert khac, "nhóm 26-30 phải có câu 'có khắc chồng?'"
    for q in items:
        assert "đã được lược" not in (q["cau_hoi"] or ""), \
            f"câu hỏi bị scrub xoá trắng: {q['cau_hoi']!r}"


def test_reading_old_keys_preserved():
    """KEY MỚI không phá API cũ — mọi key cũ vẫn còn."""
    out = _reading(_BIRTH_27)
    old_keys = {
        "method_id", "input", "stage", "personality", "cung_phu_the_tuvi",
        "batu_hon_nhan", "song_phai_reconcile", "cach_cuc", "dinh_thoi",
        "narration_brief", "quy_trinh_day_du", "chan_doan_cap_do",
        "base_12_khia_canh", "paradigm_ok", "scrub_caution_count",
        "sources", "_disclaimer",
    }
    assert old_keys.issubset(out.keys()), f"thiếu key cũ: {old_keys - set(out.keys())}"


# --------------------------------------------------------------------------- #
# VIỆC 2 — gieo_que_quyet_dinh (Mai Hoa decision helper)
# --------------------------------------------------------------------------- #
_NOW = datetime(2026, 6, 25, 0, 40)


def test_gieo_que_basic_structure():
    r = gieo_que_tinh_duyen("Tôi có nên cưới người này không?", seed_numbers=[5, 8, 3])
    assert r["method_id"] == GIEO_METHOD_ID
    for k in ("que_chinh", "que_ho", "que_bien", "hao_dong", "the_dung",
              "bon_buoc", "can_hoi_them", "tam_phap", "_paradigm"):
        assert k in r, f"thiếu khoá {k}"
    # Quẻ chính/hỗ/biến đều có tên quẻ thật (64 quẻ King Wen).
    assert r["que_chinh"]["ten_que"]
    assert r["que_ho"]["ten_que"]
    assert r["que_bien"]["ten_que"]
    assert 1 <= r["hao_dong"] <= 6


def test_gieo_que_deterministic_from_seed():
    """Cùng seed_numbers -> cùng quẻ (deterministic)."""
    a = gieo_que_tinh_duyen("X", seed_numbers=[5, 8, 3])
    b = gieo_que_tinh_duyen("X", seed_numbers=[5, 8, 3])
    assert a["que_chinh"]["binary"] == b["que_chinh"]["binary"]
    assert a["hao_dong"] == b["hao_dong"]
    assert a["que_bien"]["binary"] == b["que_bien"]["binary"]


def test_gieo_que_known_seed_values():
    """Kiểm chứng cụ thể seed [5,8,3]: thượng=Tốn(5), hạ=Khôn(8), hào=3.
    -> quẻ chính = Phong Địa Quán; biến lật hào 3."""
    r = gieo_que_tinh_duyen("X", seed_numbers=[5, 8, 3])
    assert r["quai_so"]["thuong_quai"] == "Tốn"
    assert r["quai_so"]["ha_quai"] == "Khôn"
    assert r["hao_dong"] == 3
    assert r["que_chinh"]["ten_que"] == "Quán"
    # Hào 3 ở HẠ quái -> hạ = Dụng, thượng = Thể.
    assert r["the_dung"]["que_the"] == "Tốn"
    assert r["the_dung"]["que_dung"] == "Khôn"


def test_gieo_que_time_fallback_when_no_seed():
    """Không seed (hoặc <2 số) -> lập theo THỜI GIAN (NNTT), không crash."""
    r = gieo_que_tinh_duyen("Có nên chia tay?", now=_NOW)
    assert r["lap_que"]["phep"] == "thời-gian (NNTT)"
    assert r["que_chinh"]["ten_que"]
    r1 = gieo_que_tinh_duyen("Có nên chia tay?", seed_numbers=[5], now=_NOW)
    assert r1["lap_que"]["phep"] == "thời-gian (NNTT)"
    assert "ghi_chu_seed" in r1["lap_que"]


def test_gieo_que_four_steps_present():
    """4 BƯỚC ĐOÁN QUẺ (Iron Rule #4): lời quẻ/hào + Thể-Dụng + ngoại ứng + tư thế."""
    r = gieo_que_tinh_duyen("X", seed_numbers=[3, 4, 5])
    bb = r["bon_buoc"]
    assert "buoc_1_loi_que_hao" in bb
    assert "buoc_2_the_dung" in bb
    assert "buoc_3_ngoai_ung" in bb
    assert "buoc_4_tu_the" in bb
    # Bước 3 + 4 BẮT BUỘC hỏi user (engine không tự bịa).
    assert bb["buoc_3_ngoai_ung"]["cau_hoi_cho_user"]
    assert bb["buoc_4_tu_the"]["cau_hoi_cho_user"]
    assert len(r["can_hoi_them"]) == 2


def test_gieo_que_no_predict_no_cat_hung():
    """Paradigm: KHÔNG predict cát/hung, KHÔNG chốt nên/không.
    the_dung surface 'doc_dong_dang' (đọc đồng dạng), KHÔNG surface 'cat_hung' gốc."""
    r = gieo_que_tinh_duyen("Có nên ly hôn không?", seed_numbers=[6, 2, 4])
    td = r["the_dung"]
    assert "doc_dong_dang" in td and td["doc_dong_dang"]
    assert "cat_hung" not in td, "KHÔNG surface cat_hung gốc (predict)"
    # Toàn bộ output không chứa lời chốt nên/không hay cát/hung verdict.
    import json
    blob = json.dumps(r, ensure_ascii=False).lower()
    for bad in ("nên cưới", "không nên cưới", "sẽ thành công", "sẽ thất bại",
                "chắc chắn ly hôn"):
        assert bad not in blob, f"lọt lời predict/verdict: {bad!r}"
    # Có nhắc tâm pháp 'một việc một lần'.
    assert "một" in r["tam_phap"]["mot_viec_mot_lan"].lower()


def test_gieo_que_tam_phap_present():
    """Quy tắc TÂM: không nghi không bói + một việc một lần + một câu một quẻ."""
    r = gieo_que_tinh_duyen("X", seed_numbers=[1, 2])
    tp = r["tam_phap"]
    assert "khong_nghi_khong_boi" in tp
    assert "mot_viec_mot_lan" in tp
    assert "mot_cau_mot_que" in tp
