"""Domain 5: tật ách / bệnh sử — derive từ sao an theo giờ (Tử Vi Bôn Ba video 091)."""
from engine.yi_wiki.birth_hour_quiz_v2.pillars import build_candidates
from engine.yi_wiki.birth_hour_quiz_v2.rules.tat_ach import derive_tat_ach_traits

VALID = {
    "health_hoa_linh": {"nong_trong", "binh_thuong", "unknown"},
    "health_khong_kiep": {"cang_than_kinh", "binh_thuong", "unknown"},
    "health_sat_tinh_than": {"nhieu_dau_vet", "it_dau_vet", "unknown"},
}


def _candidates():
    # Founder birth date — sinh giáp ranh giờ Hợi/Tý là ca dùng thật của quiz
    return build_candidates("1988-06-05", "Asia/Ho_Chi_Minh", (21, 1), gender="nam")


def test_candidates_carry_lunar_and_gender():
    cands = _candidates()
    assert cands, "phải có ứng viên trong khung 21h-1h"
    for c in cands:
        assert c["lunar"]["month"], c
        assert c["lunar"]["day"], c
        assert c["gender"] == "nam"


def test_traits_have_valid_values():
    cands = _candidates()
    for c in cands:
        traits = derive_tat_ach_traits(c)
        assert set(traits) == set(VALID)
        for k, v in traits.items():
            assert v in VALID[k], f"{c['chi']}: {k}={v!r}"
        # Có lá số đầy đủ → không được rơi về unknown
        assert traits["health_hoa_linh"] != "unknown", c["chi"]


def test_traits_discriminate_between_hours():
    """Lý do tồn tại của domain 5: các giờ ứng viên phải cho giá trị KHÁC nhau
    ở ít nhất một trait (sao an theo giờ xoay vị trí) — nếu mọi giờ giống hệt
    nhau thì câu hỏi vô dụng. Dùng khung rộng để chắc chắn có phân hóa."""
    cands = build_candidates("1988-06-05", "Asia/Ho_Chi_Minh", (0, 23), gender="nam")
    per_trait_values = {k: set() for k in VALID}
    for c in cands:
        traits = derive_tat_ach_traits(c)
        for k, v in traits.items():
            per_trait_values[k].add(v)
    assert any(len(vs - {"unknown"}) >= 2 for vs in per_trait_values.values()), \
        f"không trait nào phân biệt được giữa 12 giờ: {per_trait_values}"


def test_missing_lunar_returns_unknown():
    traits = derive_tat_ach_traits({"chi": "Tý", "pillars": {"year": {}}})
    assert all(v == "unknown" for v in traits.values())
