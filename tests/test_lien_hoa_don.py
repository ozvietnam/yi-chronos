"""Tests for Liên Hoa Độn Pháp engine — verified against book LIENHOADON.pdf."""

from __future__ import annotations

import pytest

from engine.lien_hoa import cast_lien_hoa
from engine.lien_hoa.don import (
    compute_don_chain,
    expected_dot_count,
    expected_khong_thoi_count,
    step_don,
)
from engine.lien_hoa.luc_than import luc_than_of_element
from engine.lien_hoa.quai_ops import (
    chanh_binary,
    flip_hao,
    hao_side,
    ho_binary,
    mod_hao,
    mod_quai,
)


# ---------- Primitives ----------

class TestQuaiOps:
    def test_mod_quai_basic(self):
        assert mod_quai(1) == 1
        assert mod_quai(8) == 8
        assert mod_quai(9) == 1
        assert mod_quai(16) == 8  # Book p.5 example: rem 0 → 8.
        assert mod_quai(25) == 1
        assert mod_quai(32) == 8

    def test_mod_hao_basic(self):
        assert mod_hao(1) == 1
        assert mod_hao(6) == 6
        assert mod_hao(7) == 1
        assert mod_hao(12) == 6

    def test_chanh_binary_known(self):
        # P=1 (Càn), T=8 (Khôn) → Thiên Địa Bỉ (111000).
        assert chanh_binary(1, 8) == "111000"
        # Càn / Càn = Kiền (111111).
        assert chanh_binary(1, 1) == "111111"

    def test_ho_binary_for_quai(self):
        # Quải (011111) → Hổ should be Càn (111111).
        # Chánh top-down: 0 1 1 1 1 1 (line 6→1).
        # Hổ upper = chánh[1,2,3] = 1,1,1 → Càn.
        # Hổ lower = chánh[2,3,4] = 1,1,1 → Càn.
        assert ho_binary("011111") == "111111"

    def test_flip_hao(self):
        # Top-down "111000": line 6..1 = '1','1','1','0','0','0'.
        # Hào 3 = top-down index 6-3=3 = '0' → flip → '1'. Result "111100".
        assert flip_hao("111000", 3) == "111100"
        # Hào 1 = index 5 = '0' → '1'. Result "111001".
        assert flip_hao("111000", 1) == "111001"
        # Hào 6 = index 0 = '1' → '0'. Result "011000".
        assert flip_hao("111000", 6) == "011000"

    def test_hao_side(self):
        assert hao_side(1) == "lower"
        assert hao_side(3) == "lower"
        assert hao_side(4) == "upper"
        assert hao_side(6) == "upper"


# ---------- Lục thân ----------

class TestLucThan:
    def test_kim_vs_thuy(self):
        # Kim sanh Thủy → Thủy là Tử Tôn của TA Kim.
        assert luc_than_of_element("kim", "thủy") == "C"

    def test_kim_vs_moc(self):
        # Kim khắc Mộc → Mộc là Thê Tài của TA Kim.
        assert luc_than_of_element("kim", "mộc") == "T"

    def test_kim_vs_tho(self):
        # Thổ sanh Kim → Thổ là Phụ Mẫu của TA Kim.
        assert luc_than_of_element("kim", "thổ") == "P"

    def test_kim_vs_hoa(self):
        # Hỏa khắc Kim → Hỏa là Quan Quỷ của TA Kim.
        assert luc_than_of_element("kim", "hỏa") == "Q"

    def test_kim_vs_kim(self):
        # Đồng hành → Huynh Đệ.
        assert luc_than_of_element("kim", "kim") == "H"


# ---------- Độn chain ----------

class TestDonChain:
    def test_step_don_single_step(self):
        # Tiên đề 1/8 hào 3 → bước 1: 5/6 hào 1.
        # Vì: 1+4=5, 8+6=14, 14-8=6, 3+4=7, 7-6=1.
        u, l, h = step_don(1, 8, 3)
        assert (u, l, h) == (5, 6, 1)

    def test_step_don_book_example_full_chain(self):
        # Book p.17-18: Tiên đề 1/8 hào 3 sinh chuỗi:
        #   Hậu đề 1: 5/6 hào 1 (Phong Thủy Hoán)
        #   Hậu đề 2: 1/4 hào 5 (Thiên Lôi Vô Vọng)
        #   Hậu đề 3: 5/2 hào 3 (Phong Trạch Trung Phu)
        #   Hậu đề 4: 1/8 hào 1 (Thiên Địa Bỉ — chánh quay về tiên đề)
        steps = compute_don_chain(1, 8, 3)
        assert len(steps) == 4
        assert (steps[0].upper, steps[0].lower, steps[0].hao) == (5, 6, 1)
        assert (steps[1].upper, steps[1].lower, steps[1].hao) == (1, 4, 5)
        assert (steps[2].upper, steps[2].lower, steps[2].hao) == (5, 2, 3)
        assert (steps[3].upper, steps[3].lower, steps[3].hao) == (1, 8, 1)

    def test_expected_dot_count_by_hao(self):
        # Book p.19: hào 3 hoặc 6 → 1 đợt; hào 4 hoặc 1 → 2 đợt; hào 5 hoặc 2 → 3 đợt.
        assert expected_dot_count(3) == 1
        assert expected_dot_count(6) == 1
        assert expected_dot_count(4) == 2
        assert expected_dot_count(1) == 2
        assert expected_dot_count(5) == 3
        assert expected_dot_count(2) == 3

    def test_expected_khong_thoi_count(self):
        assert expected_khong_thoi_count(3) == 5
        assert expected_khong_thoi_count(1) == 9
        assert expected_khong_thoi_count(5) == 13

    def test_chain_length_matches_dot_count(self):
        for hao in (1, 2, 3, 4, 5, 6):
            steps = compute_don_chain(1, 1, hao)
            assert len(steps) == expected_dot_count(hao) * 4


# ---------- cast_lien_hoa top-level ----------

class TestCastLienHoa:
    def test_book_example_p17_full(self):
        """Sách trang 17: P=1, T=8 → 5 không thời, Tiên đề Bỉ động hào 3."""
        r = cast_lien_hoa(number_right_hand=1, number_left_hand=8)
        assert r["dot_count"] == 1
        assert r["khong_thoi_count"] == 5
        assert r["completed"] is True
        assert r["ta_reference_trigram"] == "Càn"
        assert r["ta_reference_element"] == "kim"
        assert len(r["khong_thoi"]) == 5

        kt = r["khong_thoi"]
        # KT1 Tiên đề: Bỉ
        assert kt[0]["chanh"]["name_vi"] == "Bĩ"
        assert kt[0]["hao"] == 3
        assert kt[0]["ta_trigram"] == "Càn"
        assert kt[0]["chu_su"] == "TA"

        # KT2: Phong Thủy Hoán
        assert kt[1]["chanh"]["name_vi"] == "Hoán"
        assert kt[1]["hao"] == 1
        assert kt[1]["chu_su"] == "T"  # Tốn (mộc) là Thê Tài của TA Kim.

        # KT3: Thiên Lôi Vô Vọng
        assert kt[2]["chanh"]["name_vi"] == "Vô Vọng"
        assert kt[2]["hao"] == 5
        assert kt[2]["chu_su"] == "T"  # Chấn (mộc) là Thê Tài.

        # KT4: Phong Trạch Trung Phu
        assert kt[3]["chanh"]["name_vi"] == "Trung Phu"
        assert kt[3]["hao"] == 3
        assert kt[3]["chu_su"] == "T"  # Tốn (mộc).

        # KT5: trở về Bỉ but hào 1, TA Càn giành lại chủ sự.
        assert kt[4]["chanh"]["name_vi"] == "Bĩ"
        assert kt[4]["hao"] == 1
        assert kt[4]["chu_su"] == "TA"

    def test_two_dot_case_hao_1(self):
        """Hào động 1 → 2 đợt → 9 không thời."""
        r = cast_lien_hoa(number_right_hand=1, number_left_hand=6)  # 1+6=7 mod 6 = 1
        assert r["dot_count"] == 2
        assert r["khong_thoi_count"] == 9
        assert len(r["khong_thoi"]) == 9
        # Đợt 1 boundary (KT5) — chưa hoàn thành; đợt 2 (KT9) hoàn thành.
        assert r["completed"] is True

    def test_three_dot_case_hao_2(self):
        """Hào động 2 → 3 đợt → 13 không thời."""
        r = cast_lien_hoa(number_right_hand=1, number_left_hand=7)  # 1+7=8 mod 6 = 2
        assert r["dot_count"] == 3
        assert r["khong_thoi_count"] == 13
        assert len(r["khong_thoi"]) == 13
        assert r["completed"] is True

    def test_each_kts_has_6_tagged_trigrams(self):
        r = cast_lien_hoa(number_right_hand=1, number_left_hand=8)
        for kt in r["khong_thoi"]:
            assert len(kt["tagged"]) == 6
            for tag in kt["tagged"]:
                assert tag["luc_than"] in {"TA", "H", "P", "C", "Q", "T"}

    def test_menh_cung_is_ho_at_ta_side(self):
        r = cast_lien_hoa(number_right_hand=1, number_left_hand=8)
        kt = r["khong_thoi"][0]
        assert kt["menh_cung_side"] == kt["ta_side"]

    def test_gender_required(self):
        with pytest.raises(ValueError):
            cast_lien_hoa(number_right_hand=1, number_left_hand=8, gender="other")

    def test_positive_numbers_required(self):
        with pytest.raises(ValueError):
            cast_lien_hoa(number_right_hand=0, number_left_hand=1)
        with pytest.raises(ValueError):
            cast_lien_hoa(number_right_hand=1, number_left_hand=-3)

    def test_large_numbers_normalized(self):
        # Book p.5: P=12, T=38 → P mod 8 = 4 (Chấn), T mod 8 = 6 (Khảm).
        r = cast_lien_hoa(number_right_hand=12, number_left_hand=38)
        assert r["input"]["right_quai_num"] == 4
        assert r["input"]["left_quai_num"] == 6
        # Tổng 12+38=50, 50 mod 6 = 2 → hào 2.
        assert r["input"]["initial_hao"] == 2

    def test_determinism(self):
        a = cast_lien_hoa(number_right_hand=1, number_left_hand=8)
        b = cast_lien_hoa(number_right_hand=1, number_left_hand=8)
        assert a == b

    def test_serializable(self):
        import json
        r = cast_lien_hoa(number_right_hand=4, number_left_hand=6)
        payload = json.dumps(r, ensure_ascii=False)
        restored = json.loads(payload)
        assert restored["method_id"] == "lien_hoa_don_v1"
