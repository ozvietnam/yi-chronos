"""H6.0 — rào phạm vi Socratic + post-filter paradigm (engine/hermes_guard)."""
from __future__ import annotations

import pytest

from engine.hermes_guard import (
    DISCLAIMER,
    classify_scope,
    is_predictive,
    is_ta_mang,
    paradigm_violations,
    ta_mang_violations,
    with_disclaimer,
)


@pytest.mark.parametrize("q", [
    "Lá số Tử Vi của em cung mệnh có sao gì đáng chú ý?",
    "Đại vận hiện tại của em nói gì về hướng nghề?",
    "Giải thích giúp em khái niệm Dụng Thần trong Bát Tự",
    "Quẻ em vừa gieo có ý nghĩa thế nào về việc chuyển việc?",
    "Em với người tuổi Dần có hợp tuổi cưới không?",
])
def test_in_scope_menh_ly(q):
    assert classify_scope(q).verdict == "in_scope"


@pytest.mark.parametrize("q", [
    "Viết giúp em đoạn code Python tính giai thừa",
    "Làm hộ em bài tập toán phương trình bậc 2",
    "Dịch giúp em đoạn này sang tiếng Anh",
    "Viết giúp em một bài luận văn về môi trường",
    "Thủ đô của nước Pháp là gì",
    "Soạn giúp em cái email xin nghỉ phép",
])
def test_out_of_scope_lam_ho(q):
    v = classify_scope(q)
    assert v.verdict == "out_of_scope" and v.reply


@pytest.mark.parametrize("q", ["ok", "chào em", "alo", "?"])
def test_needs_focus_when_vague(q):
    v = classify_scope(q)
    assert v.verdict == "needs_focus" and v.reply


def test_works_without_diacritics():
    # user gõ thiếu dấu vẫn phải bắt được miền + làm-hộ
    assert classify_scope("la so tu vi cua em the nao").verdict == "in_scope"
    assert classify_scope("viet ho em code python").verdict == "out_of_scope"


@pytest.mark.parametrize("ans", [
    "Năm 2027 anh chắc chắn sẽ giàu to.",
    "Con số may mắn của anh là 39, cứ đánh con 39.",
    "Số anh đã định, nhất định sẽ thành công.",
    "Tương lai của anh sẽ là một doanh nhân lớn.",
])
def test_paradigm_predictive_flagged(ans):
    assert is_predictive(ans) is True
    assert paradigm_violations(ans)


@pytest.mark.parametrize("ans", [
    "Cấu trúc lá số này vận hành tốt nhất khi anh chủ động học hỏi — anh thấy điều đó phản chiếu thế nào?",
    "Cung Quan Lộc có Thái Dương: anh có thiên hướng dẫn dắt; anh đang ở vị trí nào trong việc này?",
])
def test_paradigm_dong_dang_passes(ans):
    assert is_predictive(ans) is False


# ── Iron #9: LẰN RANH ĐẠO ĐỨC BRAHMAJĀLA (tà mạng) ───────────────────────────

@pytest.mark.parametrize("ans", [
    # cờ bạc / số đề / lô đề → tà mạng, BỊ CHẶN
    "Con số may mắn của anh là 39, cứ đánh con 39.",
    "Tối nay anh nên đánh đề con 68 cho chắc ăn.",
    "Lá số này hợp chơi lô đề, anh cứ chơi lô đi.",
    "Quẻ này gợi ý anh nên cá độ trận bóng tối nay.",
    "Hôm nay là ngày đẹp để anh đánh bạc đó.",
    # ngày-giờ tốt để TRỤC LỢI cờ bạc
    "Giờ tốt nhất để anh đánh đề là 9 giờ tối.",
    # PHÁN sống-chết / tai-hoạ vào người
    "Năm tới anh chắc chắn sẽ gặp tai nạn lớn.",
    "Số cô nhất định yểu mệnh, không qua khỏi tuổi 40.",
    "Anh sẽ chết vào năm hạn này, không tránh được.",
])
def test_ta_mang_blocked(ans):
    assert is_ta_mang(ans) is True
    assert ta_mang_violations(ans)
    # tà mạng cũng phải bị paradigm_violations bắt (choke-point dùng chung)
    assert is_predictive(ans) is True


@pytest.mark.parametrize("ans", [
    # khái niệm PHÂN TÍCH trung tính về sao/cung chủ sức khoẻ — KHÔNG chặn nhầm
    "Cung Tật Ách có Thiên Lương: anh quan tâm việc giữ gìn sức khoẻ thế nào?",
    "Sao này trong cổ thư chủ về bệnh tật — anh chăm sóc thân thể ra sao?",
    # chọn ngày khởi sự chung chung, KHÔNG trục lợi cờ bạc — hợp lệ
    "Xem ngày tốt để khởi sự một dự án là việc nên cân nhắc kỹ lưỡng.",
    # mô tả cấu trúc Tử Bình trung tính (đã có sẵn trong guard cũ) vẫn qua
    "Thương Quan khắc Quan là một cấu trúc cần được chế hoá, anh thấy sao?",
    # soi tâm bình thường
    "Cung Phúc Đức phản chiếu cách anh tìm an trong nội tâm — anh đang thấy gì?",
])
def test_ta_mang_context_aware_passes(ans):
    assert is_ta_mang(ans) is False
    assert is_predictive(ans) is False


def test_so_de_question_can_be_reframed_at_scope():
    # "số đề con gì" — câu HỎI: không có domain term cờ bạc trong _DOMAIN nên
    # rơi vào needs_focus (mời nêu rõ việc) thay vì bị làm hộ.
    v = classify_scope("tối nay đánh đề con gì cho trúng")
    assert v.verdict in ("needs_focus", "out_of_scope") and v.reply
    # và NẾU output sage lỡ trượt vào gợi số → bị chặn ở post-filter
    assert is_ta_mang("anh cứ đánh con 88 tối nay là trúng") is True


# ── DISCLAIMER (Iron #9) ─────────────────────────────────────────────────────

def test_with_disclaimer_appends():
    out = with_disclaimer("Cung Mệnh có Tử Vi, anh thấy điều gì phản chiếu?")
    assert DISCLAIMER in out
    assert out.startswith("Cung Mệnh")


def test_with_disclaimer_idempotent():
    once = with_disclaimer("Nội dung soi tâm.")
    twice = with_disclaimer(once)
    assert once == twice
    assert once.count("không thay tu học hay y tế") == 1


def test_with_disclaimer_empty_returns_disclaimer():
    assert with_disclaimer("") == DISCLAIMER
