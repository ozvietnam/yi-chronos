"""Tests for engine.bat_tu.ai_chat — AI Q&A with chart context."""
from __future__ import annotations

import pytest

from engine.bat_tu import cast_bat_tu, chat_about_chart, compose_luan_giai
from engine.bat_tu.ai_chat import _compose_laso_context


@pytest.fixture
def founder_state():
    return cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )


@pytest.fixture
def founder_luan(founder_state):
    return compose_luan_giai(founder_state, current_age=38)


def test_context_compose_includes_tu_tru(founder_state, founder_luan):
    ctx = _compose_laso_context(founder_state, founder_luan)
    assert "TỨ TRỤ" in ctx
    # Founder pillars: Mậu Thìn / Mậu Ngọ / Nhâm Thìn / Canh Tý
    assert "Mậu" in ctx
    assert "Thìn" in ctx
    assert "Nhâm" in ctx
    assert "Canh" in ctx


def test_context_includes_nhat_chu(founder_state, founder_luan):
    ctx = _compose_laso_context(founder_state, founder_luan)
    assert "NHẬT CHỦ" in ctx
    assert "Nhâm" in ctx
    assert "thủy" in ctx


def test_context_includes_dung_than(founder_state, founder_luan):
    ctx = _compose_laso_context(founder_state, founder_luan)
    assert "DỤNG THẦN" in ctx


def test_context_includes_cach_cuc(founder_state, founder_luan):
    ctx = _compose_laso_context(founder_state, founder_luan)
    assert "CÁCH CỤC" in ctx
    assert "Chính Tài" in ctx


def test_chat_with_mock_provider(founder_state, founder_luan):
    """Mock provider should always work."""
    result = chat_about_chart(
        founder_state,
        "Tôi nên làm nghề gì?",
        luan_giai=founder_luan,
        provider_preferred=["mock"],
    )
    assert result["method_id"] == "bat_tu_ai_chat_v1"
    assert result["answer"]
    assert result["provider"] == "mock"
    assert "tokens" in result


def test_empty_question_rejected(founder_state):
    with pytest.raises(ValueError, match="empty"):
        chat_about_chart(founder_state, "", provider_preferred=["mock"])


def test_invalid_state_rejected():
    with pytest.raises(ValueError, match="tu_tru"):
        chat_about_chart({}, "test", provider_preferred=["mock"])


def test_chat_with_history(founder_state, founder_luan):
    """Multi-turn chat with history."""
    history = [
        {"role": "user", "content": "Lá số tôi như thế nào?"},
        {"role": "assistant", "content": "Lá số có Day Master Nhâm Thủy nhược..."},
    ]
    result = chat_about_chart(
        founder_state,
        "Vậy nên làm gì để bồi thân?",
        history=history,
        luan_giai=founder_luan,
        provider_preferred=["mock"],
    )
    assert result["answer"]


def test_context_size_reasonable(founder_state, founder_luan):
    """Context should be compact (not bloated)."""
    ctx = _compose_laso_context(founder_state, founder_luan)
    # Aim for under 4KB
    assert len(ctx) < 4000
    # But also not too sparse
    assert len(ctx) > 300
