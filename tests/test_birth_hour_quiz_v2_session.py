"""Tests for SQLite-backed quiz session storage."""
import os
import tempfile

from engine.yi_wiki.birth_hour_quiz_v2.session_store import (
    init_schema, create_session, get_session, update_session, mark_final,
)


def _tmp_db():
    f = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
    f.close()
    return f.name


def test_create_and_get_session():
    db = _tmp_db()
    try:
        init_schema(db)
        sid = create_session(
            db,
            user_id=1,
            birth_date="1988-05-02",
            timezone="Asia/Ho_Chi_Minh",
            hour_range=(6, 12),
            gender="nam",
            candidates_initial=["Mão", "Thìn", "Tỵ", "Ngọ"],
            strategy="single_round",
        )
        assert sid

        sess = get_session(db, sid)
        assert sess is not None
        assert sess["birth_date"] == "1988-05-02"
        assert sess["candidates_initial"] == ["Mão", "Thìn", "Tỵ", "Ngọ"]
        assert sess["status"] == "in_progress"
        assert sess["hour_range"] == (6, 12)
    finally:
        os.unlink(db)


def test_get_missing_session_returns_none():
    db = _tmp_db()
    try:
        init_schema(db)
        assert get_session(db, "does-not-exist") is None
    finally:
        os.unlink(db)


def test_update_session_accumulates_state():
    db = _tmp_db()
    try:
        init_schema(db)
        sid = create_session(
            db, user_id=None, birth_date="1988-05-02", timezone="Asia/Ho_Chi_Minh",
            hour_range=None, gender="nam",
            candidates_initial=["Mão", "Thìn"], strategy="single_round",
        )
        update_session(
            db, sid,
            candidates_remaining=["Mão", "Thìn"],
            accumulated_scores={"Mão": 5.0, "Thìn": 2.0},
            rounds_data=[{"round_num": 1, "answers": {"face_shape": "dai"}}],
        )
        sess = get_session(db, sid)
        assert sess["accumulated_scores"] == {"Mão": 5.0, "Thìn": 2.0}
        assert sess["rounds_data"][0]["round_num"] == 1
    finally:
        os.unlink(db)


def test_mark_final_sets_status_and_timestamp():
    db = _tmp_db()
    try:
        init_schema(db)
        sid = create_session(
            db, user_id=None, birth_date="1988-05-02", timezone="Asia/Ho_Chi_Minh",
            hour_range=None, gender="nam",
            candidates_initial=["Mão"], strategy="single_round",
        )
        mark_final(db, sid, final_result={"top_chi": "Mão", "confidence": "Cao"})
        sess = get_session(db, sid)
        assert sess["status"] == "final"
        assert sess["final_result"]["top_chi"] == "Mão"
        assert sess["completed_at"] is not None
    finally:
        os.unlink(db)


def test_init_schema_idempotent():
    db = _tmp_db()
    try:
        init_schema(db)
        init_schema(db)  # second call must not error
    finally:
        os.unlink(db)
