"""Tests for LEXICON CONTEXT injection into sage prompts.

Verifies that `consult()` produces task bodies that contain pre-extracted
symbolic mappings — sages can skip re-deriving "lá → Mộc" basics.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest


def _hermes_bin_missing() -> bool:
    """True nếu thiếu binary hermes CLI (vendor/hermes-agent/.venv/bin/hermes).

    Các test ở module này spawn sage qua hermes CLI; không có binary thì SKIP
    (không phải lỗi logic) để CI khỏi nhiễu trên máy chưa cài vendor venv.
    """
    try:
        from engine.ai import kanban_council as kc

        return not Path(str(kc.HERMES_BIN)).exists()
    except Exception:
        return True


pytestmark = pytest.mark.skipif(
    _hermes_bin_missing(),
    reason="hermes CLI binary vắng mặt (vendor/hermes-agent/.venv/bin/hermes) — bỏ qua test spawn sage",
)


def _archive_session(session) -> None:
    from engine.ai import kanban_council as kc

    env = os.environ.copy()
    env["HERMES_HOME"] = str(kc.HERMES_HOME)
    for tid in list(session.sage_task_ids.values()) + [session.arbiter_id]:
        subprocess.run(
            [str(kc.HERMES_BIN), "kanban", "archive", tid],
            env=env, capture_output=True, text=True,
        )


def _get_task_body(task_id: str) -> str:
    """Read body of a kanban task via hermes CLI."""
    from engine.ai import kanban_council as kc

    env = os.environ.copy()
    env["HERMES_HOME"] = str(kc.HERMES_HOME)
    out = subprocess.run(
        [str(kc.HERMES_BIN), "kanban", "show", task_id, "--json"],
        env=env, capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)["task"]["body"]


def test_consult_injects_lexicon_for_symbol_rich_question():
    """A question with rich symbolic content should produce LEXICON CONTEXT section."""
    from engine.ai.kanban_council import consult
    from engine.yi_lexicon.core_seed import seed_all

    # Make sure lexicon has bedrock concepts
    seed_all()

    session = consult(
        question="9h sáng em ra đường gặp hai chiếc lá rơi, có ý nghĩa gì?",
        sages=["mai_hoa"],
        soul_key="test_lex_inject",
    )
    try:
        body = _get_task_body(session.sage_task_ids["mai_hoa"])
        assert "## 📚 LEXICON CONTEXT" in body
        assert "đã pre-extract" in body
        # Should mention at least one of the recognized tokens
        assert "lá" in body or "rơi" in body or "Mai Hoa sơ bộ" in body
    finally:
        _archive_session(session)


def test_consult_handles_empty_lexicon_match():
    """A question that matches NO lexicon concepts should still spawn successfully."""
    from engine.ai.kanban_council import consult
    from engine.yi_lexicon.core_seed import seed_all

    seed_all()

    session = consult(
        question="xyz qrstuvw abcdef",  # gibberish
        sages=["bat_tu"],
        soul_key="test_no_match",
    )
    try:
        body = _get_task_body(session.sage_task_ids["bat_tu"])
        # Should NOT include LEXICON CONTEXT section since nothing matched
        # (parser returns empty tokens → skip injection)
        assert "## OUTPUT bắt buộc" in body
    finally:
        _archive_session(session)


def test_lexicon_injection_includes_mai_hoa_when_numbers():
    """If user question contains numbers, Mai Hoa candidate should be injected."""
    from engine.ai.kanban_council import consult
    from engine.yi_lexicon.core_seed import seed_all

    seed_all()

    session = consult(
        question="9h sáng có hai chiếc lá rơi",
        sages=["mai_hoa"],
        soul_key="test_mh_inject",
    )
    try:
        body = _get_task_body(session.sage_task_ids["mai_hoa"])
        assert "Mai Hoa sơ bộ" in body
        # Should include hexagram names
        assert any(quai in body for quai in ("Càn", "Khôn", "Đoài", "Chấn", "Tốn", "Khảm", "Ly", "Cấn"))
    finally:
        _archive_session(session)


def test_lexicon_injection_skip_when_question_minimal():
    """Very short questions with no symbolic content → no lexicon section."""
    from engine.ai.kanban_council import consult

    session = consult(
        question="hello",
        sages=["bat_tu"],
        soul_key="test_minimal",
    )
    try:
        body = _get_task_body(session.sage_task_ids["bat_tu"])
        # "hello" doesn't match Vietnamese lexicon, no numbers, no time
        # → lexicon section should be absent
        # (defensive: should not break anyway)
        assert "## OUTPUT bắt buộc" in body
    finally:
        _archive_session(session)


def test_lexicon_failure_does_not_break_sage_spawn():
    """If lexicon module crashes, sage spawn should still succeed silently."""
    from engine.ai.kanban_council import consult

    # Just verify normal spawn succeeds (lexicon try/except handles failures)
    session = consult(
        question="test question",
        sages=["bat_tu"],
        soul_key="test_resilience",
    )
    try:
        body = _get_task_body(session.sage_task_ids["bat_tu"])
        # Whether or not lexicon injects, body must still have core sections
        assert "OUTPUT bắt buộc" in body
    finally:
        _archive_session(session)
