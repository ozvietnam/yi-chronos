"""H6.0 — rào phạm vi Socratic + post-filter paradigm (engine/hermes_guard)."""
from __future__ import annotations

import pytest

from engine.hermes_guard import classify_scope, is_predictive, paradigm_violations


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
