from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy import Column, DateTime, MetaData, String, Table, Text, create_engine, func, insert

DEFAULT_DATABASE_URL = "sqlite:///data/yi_chronos.sqlite3"
DATABASE_URL = os.getenv("YI_CHRONOS_DATABASE_URL", DEFAULT_DATABASE_URL)

if DATABASE_URL.startswith("sqlite:///"):
    Path(DATABASE_URL.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(DATABASE_URL, future=True)
metadata = MetaData()

universe_snapshot = Table(
    "universe_snapshot",
    metadata,
    Column("snapshot_id", String, primary_key=True),
    Column("timestamp_utc", String, nullable=False),
    Column("payload_json", Text, nullable=False),
    Column("algorithm_version", String, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

user_profile = Table(
    "user_profile",
    metadata,
    Column("user_id", String, primary_key=True),
    Column("birth_profile_hash", String, nullable=False),
    Column("payload_json", Text, nullable=False),
    Column("algorithm_version", String, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

personal_profile_cache = Table(
    "personal_profile_cache",
    metadata,
    Column("user_id", String, primary_key=True),
    Column("payload_json", Text, nullable=False),
    Column("algorithm_version", String, nullable=False),
    Column("generated_at", DateTime, server_default=func.now()),
)

milestone_prompt = Table(
    "milestone_prompt",
    metadata,
    Column("prompt_id", String, primary_key=True),
    Column("user_id", String, nullable=False),
    Column("payload_json", Text, nullable=False),
    Column("algorithm_version", String, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

feedback_event = Table(
    "feedback_event",
    metadata,
    Column("feedback_id", String, primary_key=True),
    Column("prompt_id", String, nullable=False),
    Column("payload_json", Text, nullable=False),
    Column("algorithm_version", String, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

luc_hao_case = Table(
    "luc_hao_case",
    metadata,
    Column("case_id", String, primary_key=True),
    Column("question_text", String, nullable=False),
    Column("payload_json", Text, nullable=False),
    Column("algorithm_version", String, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

luc_hao_feedback = Table(
    "luc_hao_feedback",
    metadata,
    Column("feedback_id", String, primary_key=True),
    Column("case_id", String, nullable=False),
    Column("payload_json", Text, nullable=False),
    Column("algorithm_version", String, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

# GPS Phase 3 — immutable pre-registered predictions.
gps_prediction = Table(
    "gps_prediction",
    metadata,
    Column("prediction_id", String, primary_key=True),
    Column("profile_hash", String, nullable=False, index=True),
    Column("created_at_utc", String, nullable=False),  # ISO 8601, the registration moment
    Column("for_date", String, nullable=False, index=True),  # YYYY-MM-DD
    Column("for_hour_branch", String, nullable=True),
    Column("domain", String, nullable=False),
    Column("score", String, nullable=False),  # stored as string to keep schema simple
    Column("rule_id", String, nullable=False),
    Column("action_text", String, nullable=False),
    Column("payload_json", Text, nullable=False),
    Column("payload_hash", String, nullable=False, unique=True),
    Column("status", String, nullable=False, server_default="active"),  # active | expired | feedback_received
    Column("algorithm_version", String, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

# GPS prediction feedback — links to gps_prediction.
gps_feedback = Table(
    "gps_feedback",
    metadata,
    Column("feedback_id", String, primary_key=True),
    Column("prediction_id", String, nullable=False, index=True),
    Column("response_enum", String, nullable=False),  # matched | partly | false | unknown
    Column("confidence_enum", String, nullable=False),  # high | medium | low | unsure
    Column("actual_outcome", Text, nullable=True),
    Column("recorded_at_utc", String, nullable=False),
    Column("payload_json", Text, nullable=False),
    Column("algorithm_version", String, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

TABLES = {
    "universe_snapshot": universe_snapshot,
    "user_profile": user_profile,
    "personal_profile_cache": personal_profile_cache,
    "milestone_prompt": milestone_prompt,
    "feedback_event": feedback_event,
    "luc_hao_case": luc_hao_case,
    "luc_hao_feedback": luc_hao_feedback,
    "gps_prediction": gps_prediction,
    "gps_feedback": gps_feedback,
}


def init_db() -> None:
    metadata.create_all(engine)


def store_json(table: str, key_field: str, payload: dict[str, Any], algorithm_version: str, key: str | None = None) -> str:
    init_db()
    record_id = key or f"{key_field[0]}_{uuid4().hex}"
    payload_json = json.dumps(payload)
    if table == "universe_snapshot":
        values = {
            "snapshot_id": record_id,
            "timestamp_utc": payload["timestamp_utc"],
            "payload_json": payload_json,
            "algorithm_version": algorithm_version,
        }
    elif table == "user_profile":
        values = {
            "user_id": record_id,
            "birth_profile_hash": payload["birth_profile_hash"],
            "payload_json": payload_json,
            "algorithm_version": algorithm_version,
        }
    elif table == "personal_profile_cache":
        values = {"user_id": record_id, "payload_json": payload_json, "algorithm_version": algorithm_version}
    elif table == "milestone_prompt":
        values = {
            "prompt_id": record_id,
            "user_id": payload["user_id"],
            "payload_json": payload_json,
            "algorithm_version": algorithm_version,
        }
    elif table == "feedback_event":
        values = {
            "feedback_id": record_id,
            "prompt_id": payload["prompt_id"],
            "payload_json": payload_json,
            "algorithm_version": algorithm_version,
        }
    elif table == "luc_hao_case":
        values = {
            "case_id": record_id,
            "question_text": payload["question_text"],
            "payload_json": payload_json,
            "algorithm_version": algorithm_version,
        }
    elif table == "luc_hao_feedback":
        values = {
            "feedback_id": record_id,
            "case_id": payload["case_id"],
            "payload_json": payload_json,
            "algorithm_version": algorithm_version,
        }
    else:
        raise ValueError(f"unknown table: {table}")

    with engine.begin() as connection:
        connection.execute(insert(TABLES[table]).values(**values))
    return record_id
