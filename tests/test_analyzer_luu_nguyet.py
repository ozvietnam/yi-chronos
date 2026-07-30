"""TDD: TuViAnalyzer.luu_nguyet() — cung lưu nguyệt mỗi tháng PHẢI khớp Đẩu Quân
(TVĐSTT Q2 tr.88), CÙNG quy ước với badge "Đẩu Quân tháng" (an_sao.nguyet_van_per_cung).

Bug đã sửa 2026-07-05: trước đây hàm này khởi tháng 1 từ Tiểu Hạn của năm (quy ước
KHÁC, không có nguồn), khiến văn bản luận giải AI mô tả sai cung so với badge hiển
thị cùng panel. Test này khoá lại quy ước đúng bằng cách stub client DeepSeek (không
gọi API thật, không tốn phí) và chỉ kiểm phần gán cung — không kiểm nội dung AI viết.

Neo lá số founder (1988-06-05 23:30 +07): Mệnh Tỵ, sinh tháng 4 âm, giờ Tý.
"""
from unittest.mock import MagicMock, patch

from engine.tu_vi.analyzer import Person, TuViAnalyzer
from engine.tu_vi.dau_quan import compute_dau_quan_for_months

FOUNDER = Person(
    person_key="_test_founder",
    name="Test Founder",
    birth_datetime_local="1988-06-05T23:30:00",
    gender="nam",
)


def _stub_deepseek_client():
    resp = MagicMock()
    resp.choices = [MagicMock(message=MagicMock(content='{"chu_de": "test"}'))]
    resp.usage = MagicMock(prompt_tokens=10, completion_tokens=10)
    client = MagicMock()
    client.chat.completions.create.return_value = resp
    return client


def test_luu_nguyet_branch_khop_dau_quan_2026():
    """Cung mỗi tháng của analyzer.luu_nguyet(2026) PHẢI == Đẩu Quân lưu niên 2026,
    KHÔNG phải Tiểu Hạn (bug cũ)."""
    expected = {
        m["luu_nguyet_month"]: m["dau_quan_branch"]
        for m in compute_dau_quan_for_months("Ngọ", 4, "Tý")   # 2026 = Bính Ngọ
    }
    az = TuViAnalyzer(FOUNDER, force=True)
    with patch("engine.yi_publishing.translator.get_deepseek_client", return_value=_stub_deepseek_client()):
        data = az.luu_nguyet(2026)
    assert len(data["months"]) == 12
    for m in data["months"]:
        assert m["branch"] == expected[m["thang_am"]], (
            f"tháng {m['thang_am']}: engine trả {m['branch']}, Đẩu Quân đúng phải là {expected[m['thang_am']]}"
        )


def test_luu_nguyet_thang3_la_menh():
    """Founder 2026: tháng 3 âm → Đẩu Quân tại Tỵ = cung Mệnh (đã tay-verify)."""
    az = TuViAnalyzer(FOUNDER, force=True)
    with patch("engine.yi_publishing.translator.get_deepseek_client", return_value=_stub_deepseek_client()):
        data = az.luu_nguyet(2026)
    m3 = next(m for m in data["months"] if m["thang_am"] == 3)
    assert m3["branch"] == "Tỵ"
    assert m3["palace"] == "Mệnh"
