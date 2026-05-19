"""Immutable pre-registered prediction log + feedback collection.

CRITICAL invariants:
- A prediction can only be registered for `for_date >= today` (no back-dating).
- Once registered, content is identified by `payload_hash` (sha256). Any
  attempt to update produces an integrity error (sqlite UNIQUE constraint).
- Feedback can only be submitted after `for_date` has passed.
- All tables include algorithm_version for rule attribution across versions.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import insert, select, update

from core.config import ALGORITHM_VERSION, EXPERIMENTAL_MODE, gps_enabled_for
from data.database import engine, gps_feedback, gps_prediction, init_db
from engine.gps_engine import GPSDay, Trigger, hash_trigger


class PredictionLogError(RuntimeError):
    pass


class GpsDisabledError(PredictionLogError):
    pass


class BackDatingError(PredictionLogError):
    pass


class DuplicatePredictionError(PredictionLogError):
    pass


class FeedbackTooEarlyError(PredictionLogError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _today_local() -> date:
    return date.today()


def register_predictions(gps_day: GPSDay, profile_hash: str | None = None) -> list[dict[str, Any]]:
    """Register every trigger of a GPSDay as an immutable prediction.

    Returns a list of registration receipts (one per trigger).
    Raises GpsDisabledError if EXPERIMENTAL_MODE gate refuses this profile.
    Raises BackDatingError if for_date is in the past.
    """
    init_db()

    actual_hash = profile_hash or gps_day.profile_hash
    if not gps_enabled_for(actual_hash):
        raise GpsDisabledError(
            "GPS pre-registration disabled for this profile by current runtime mode."
        )

    target = date.fromisoformat(gps_day.date_local)
    if target < _today_local():
        raise BackDatingError(
            f"Cannot register predictions for past date {target.isoformat()}."
        )

    receipts: list[dict[str, Any]] = []
    created_at = _utc_now_iso()

    with engine.begin() as conn:
        for trigger in gps_day.triggers:
            payload_hash = hash_trigger(trigger, actual_hash, gps_day.date_local)
            payload = {
                "trigger": trigger.to_dict(),
                "day": {
                    "date_local": gps_day.date_local,
                    "day_pillar": gps_day.day_pillar,
                    "day_quai": gps_day.day_quai,
                    "solar_term": gps_day.solar_term,
                },
                "natal_snapshot": gps_day.natal_snapshot,
                "runtime_mode": gps_day.runtime_mode,
            }
            prediction_id = f"gp_{uuid4().hex}"
            try:
                conn.execute(
                    insert(gps_prediction).values(
                        prediction_id=prediction_id,
                        profile_hash=actual_hash,
                        created_at_utc=created_at,
                        for_date=gps_day.date_local,
                        for_hour_branch=trigger.hour_branch,
                        domain=trigger.domain,
                        score=str(trigger.score),
                        rule_id=trigger.rule_id,
                        action_text=trigger.action_text,
                        payload_json=json.dumps(payload, ensure_ascii=False, sort_keys=True),
                        payload_hash=payload_hash,
                        status="active",
                        algorithm_version=ALGORITHM_VERSION,
                    )
                )
            except Exception as e:
                # UNIQUE constraint violation = duplicate registration of same trigger.
                if "UNIQUE" in str(e) or "duplicate" in str(e).lower():
                    raise DuplicatePredictionError(
                        f"Trigger already registered (hash {payload_hash[:12]})."
                    ) from e
                raise
            receipts.append(
                {
                    "prediction_id": prediction_id,
                    "payload_hash": payload_hash,
                    "for_date": gps_day.date_local,
                    "domain": trigger.domain,
                    "hour_branch": trigger.hour_branch,
                    "score": trigger.score,
                    "rule_id": trigger.rule_id,
                    "created_at_utc": created_at,
                }
            )
    return receipts


def list_predictions(profile_hash: str, status: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
    """List predictions for a profile, newest first."""
    init_db()
    stmt = select(gps_prediction).where(gps_prediction.c.profile_hash == profile_hash)
    if status:
        stmt = stmt.where(gps_prediction.c.status == status)
    stmt = stmt.order_by(gps_prediction.c.for_date.desc()).limit(limit)

    out: list[dict[str, Any]] = []
    with engine.begin() as conn:
        for row in conn.execute(stmt):
            out.append(
                {
                    "prediction_id": row.prediction_id,
                    "profile_hash": row.profile_hash,
                    "created_at_utc": row.created_at_utc,
                    "for_date": row.for_date,
                    "for_hour_branch": row.for_hour_branch,
                    "domain": row.domain,
                    "score": int(row.score),
                    "rule_id": row.rule_id,
                    "action_text": row.action_text,
                    "payload_hash": row.payload_hash,
                    "status": row.status,
                    "algorithm_version": row.algorithm_version,
                }
            )
    return out


def submit_feedback(
    prediction_id: str,
    response_enum: str,
    confidence_enum: str = "unsure",
    actual_outcome: str | None = None,
) -> dict[str, Any]:
    """Submit feedback for a prediction. Only allowed after `for_date` has passed."""
    init_db()
    if response_enum not in {"matched", "partly", "false", "unknown"}:
        raise ValueError(f"invalid response_enum: {response_enum}")
    if confidence_enum not in {"high", "medium", "low", "unsure"}:
        raise ValueError(f"invalid confidence_enum: {confidence_enum}")

    with engine.begin() as conn:
        row = conn.execute(
            select(gps_prediction).where(gps_prediction.c.prediction_id == prediction_id)
        ).first()
        if row is None:
            raise PredictionLogError(f"unknown prediction_id: {prediction_id}")

        for_date = date.fromisoformat(row.for_date)
        if for_date >= _today_local():
            raise FeedbackTooEarlyError(
                f"Cannot submit feedback for {row.for_date} — date has not yet passed."
            )

        feedback_id = f"gf_{uuid4().hex}"
        recorded_at = _utc_now_iso()
        payload = {
            "prediction_id": prediction_id,
            "response_enum": response_enum,
            "confidence_enum": confidence_enum,
            "actual_outcome": actual_outcome,
            "recorded_at_utc": recorded_at,
        }
        conn.execute(
            insert(gps_feedback).values(
                feedback_id=feedback_id,
                prediction_id=prediction_id,
                response_enum=response_enum,
                confidence_enum=confidence_enum,
                actual_outcome=actual_outcome or "",
                recorded_at_utc=recorded_at,
                payload_json=json.dumps(payload, ensure_ascii=False, sort_keys=True),
                algorithm_version=ALGORITHM_VERSION,
            )
        )
        conn.execute(
            update(gps_prediction)
            .where(gps_prediction.c.prediction_id == prediction_id)
            .values(status="feedback_received")
        )

    return {
        "feedback_id": feedback_id,
        "prediction_id": prediction_id,
        "response_enum": response_enum,
        "confidence_enum": confidence_enum,
        "recorded_at_utc": recorded_at,
    }


def compute_accuracy_stats(profile_hash: str) -> dict[str, Any]:
    """Compute rolling accuracy metrics from feedback history."""
    init_db()

    with engine.begin() as conn:
        joined = conn.execute(
            select(
                gps_prediction.c.domain,
                gps_prediction.c.rule_id,
                gps_feedback.c.response_enum,
                gps_feedback.c.confidence_enum,
            )
            .select_from(
                gps_prediction.join(
                    gps_feedback,
                    gps_prediction.c.prediction_id == gps_feedback.c.prediction_id,
                )
            )
            .where(gps_prediction.c.profile_hash == profile_hash)
        ).all()

    total = len(joined)
    matched = sum(1 for r in joined if r.response_enum == "matched")
    partly = sum(1 for r in joined if r.response_enum == "partly")
    false_count = sum(1 for r in joined if r.response_enum == "false")
    unknown = sum(1 for r in joined if r.response_enum == "unknown")

    # Domain-level breakdown.
    by_domain: dict[str, dict[str, int]] = {}
    for r in joined:
        d = by_domain.setdefault(r.domain, {"total": 0, "matched": 0, "partly": 0, "false": 0, "unknown": 0})
        d["total"] += 1
        d[r.response_enum] += 1

    # Rule-level breakdown.
    by_rule: dict[str, dict[str, int]] = {}
    for r in joined:
        d = by_rule.setdefault(r.rule_id, {"total": 0, "matched": 0, "partly": 0, "false": 0, "unknown": 0})
        d["total"] += 1
        d[r.response_enum] += 1

    return {
        "total_feedback": total,
        "matched": matched,
        "partly": partly,
        "false": false_count,
        "unknown": unknown,
        "match_rate": (matched / total) if total else None,
        "match_or_partly_rate": ((matched + partly) / total) if total else None,
        "by_domain": by_domain,
        "by_rule": by_rule,
        "experimental_mode": EXPERIMENTAL_MODE,
        "n_required_for_significance": 30,
    }
