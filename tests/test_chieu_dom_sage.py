"""Sage Chiếu Đởm Kinh (Bắc phái / 18 Phi Tinh) — đăng ký toàn hệ + paradigm nội tâm.
Anh chốt 2026-06-19: lăng kính nội tâm độc lập."""
from engine.ai import prompt_store as ps
from engine.ai.council import DEFAULT_AGENT_PROVIDER
from engine.ai.kanban_council import SAGES_BY_TAG


def test_registered_everywhere():
    assert "chieu_dom" in ps.AGENT_IDS
    assert ps.AGENT_METADATA["chieu_dom"]["name_vi"].startswith("Chiếu Đởm")
    assert "chieu_dom" in DEFAULT_AGENT_PROVIDER
    assert SAGES_BY_TAG["chieu_dom"] == "chieu-dom-kinh-sage"


def test_prompt_has_paradigm_guards():
    p = ps.get_prompt("chieu_dom")
    assert len(p) > 500
    # Bắc phái + nội tâm + KHÔNG predict (Iron Rule #4/#6/#8)
    assert "18 Phi Tinh" in p and "nội tâm" in p.lower()
    assert "KHÔNG tiên tri" in p or "không tiên tri" in p.lower()
    assert "đồng dạng" in p          # đọc đồng dạng, không predict


def test_cast_from_birth_returns_chart():
    from engine.tu_vi.from_birth import cast_chieu_dom_from_birth
    chart = cast_chieu_dom_from_birth(
        birth_datetime_local="1988-06-05T23:30:00",
        timezone="Asia/Ho_Chi_Minh", gender="nam")
    assert "stars" in chart and "menh_branch" in chart
    assert chart["year_branch"]  # Mậu Thìn year → branch Thìn


def test_roster_includes_chieu_dom():
    from engine.admin_hermes import get_roster
    row = next((r for r in get_roster() if r["tag"] == "chieu_dom"), None)
    assert row and "Bắc phái" in row["specialty"]
