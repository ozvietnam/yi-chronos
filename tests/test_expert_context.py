"""RAG grounding cho council sage — bơm tri thức sâu trích sách vào prompt."""
from engine.ai.agents import _user_message_for_agent
from engine.ai.expert_context import build_expert_context


def test_empty_question_returns_blank():
    assert build_expert_context("", "tu_vi") == ""
    assert build_expert_context("   ", "tu_vi") == ""


def test_grounds_with_book_quotes_when_db_present():
    """Có wiki.sqlite3 → block có trích sách (>); không có DB → '' (best-effort, không vỡ)."""
    block = build_expert_context("Vận sự nghiệp công danh tài lộc của tôi thế nào?", "tu_vi")
    assert isinstance(block, str)
    if block:
        assert "TRI THỨC SÂU" in block and ">" in block


def test_user_message_injects_expert_context_and_cites():
    msg = _user_message_for_agent(
        question="Q", chart_data={"a": 1},
        expert_context="## TRI THỨC SÂU TỪ SÁCH\n- > trích nguyên văn")
    assert "TRI THỨC SÂU" in msg and "DẪN cụ thể" in msg


def test_user_message_without_expert_context_unchanged():
    msg = _user_message_for_agent(question="Q", chart_data={"a": 1})
    assert "TRI THỨC SÂU" not in msg
    assert "dựa CHỈ trên dữ liệu chart" in msg


def test_challenge_round_skips_expert_block():
    """Vòng phản biện (có challenges) → KHÔNG bơm expert (tập trung chất vấn)."""
    msg = _user_message_for_agent(
        question="Q", chart_data={"a": 1}, challenges="Phản biện X",
        expert_context="## TRI THỨC SÂU TỪ SÁCH\n- > trích")
    assert "CHẤT VẤN" in msg
