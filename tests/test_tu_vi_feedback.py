"""Tests cho endpoint phản hồi độ khớp Tử Vi — POST /api/tu-vi/feedback.

Isolate DB sang tmp_path qua monkeypatch FEEDBACK_DB. Không cần LLM/emulator.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path: Path, monkeypatch):
    from api import tu_vi_3layer
    from api.main import app

    db = tmp_path / "yi_users" / "tuvi_feedback.sqlite3"
    monkeypatch.setattr(tu_vi_3layer, "FEEDBACK_DB", db)
    return TestClient(app), db


def test_submit_feedback_correct_persists(client):
    c, db = client
    res = c.post(
        "/api/tu-vi/feedback",
        json={"section": "khai_vi", "verdict": "correct", "note": "đúng quá"},
        headers={"X-User-Id": "uid_1"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["stored"] is True
    assert body["birth_doubt"] is False

    rows = sqlite3.connect(db).execute(
        "SELECT user_id, section, verdict, note FROM tuvi_feedback"
    ).fetchall()
    assert rows == [("uid_1", "khai_vi", "correct", "đúng quá")]


@pytest.mark.parametrize("verdict", ["wrong", "vague"])
def test_wrong_or_vague_flags_birth_doubt(client, verdict):
    c, _ = client
    res = c.post(
        "/api/tu-vi/feedback",
        json={"section": "su-nghiep", "verdict": verdict},
        headers={"X-User-Id": "uid_2"},
    )
    assert res.status_code == 200
    assert res.json()["birth_doubt"] is True


def test_verdict_normalized_case_insensitive(client):
    c, _ = client
    res = c.post("/api/tu-vi/feedback", json={"section": "khai_vi", "verdict": "CORRECT"})
    assert res.status_code == 200
    assert res.json()["verdict"] == "correct"


def test_invalid_verdict_422(client):
    c, _ = client
    res = c.post("/api/tu-vi/feedback", json={"section": "khai_vi", "verdict": "maybe"})
    assert res.status_code == 422


def test_missing_section_422(client):
    c, _ = client
    res = c.post("/api/tu-vi/feedback", json={"section": "  ", "verdict": "correct"})
    assert res.status_code == 422


def test_user_id_optional(client):
    c, db = client
    res = c.post("/api/tu-vi/feedback", json={"section": "tinh-duyen", "verdict": "close"})
    assert res.status_code == 200
    row = sqlite3.connect(db).execute(
        "SELECT user_id, verdict FROM tuvi_feedback"
    ).fetchone()
    assert row == (None, "close")
