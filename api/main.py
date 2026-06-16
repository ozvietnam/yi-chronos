from __future__ import annotations

import json
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.schemas import (
    CalculateRequest,
    CalendarConvertRequest,
    CompareBasicRequest,
    FeedbackRequest,
    AiCouncilRequest,
    AiCritiqueResolveRequest,
    AiKanbanCouncilRequest,
    AiPromptUpdateRequest,
    AiProviderKeyRequest,
    AiProviderNotesRequest,
    AiProviderTestRequest,
    DyadAnalysisRequest,
    LexiconConceptCreateRequest,
    LexiconCorpusRegisterRequest,
    LexiconDistillRequest,
    LexiconIngestRequest,
    LexiconInterpretRequest,
    LexiconMappingCreateRequest,
    LexiconResolveItemRequest,
    LexiconResolveConflictRequest,
    PersonCreateRequest,
    PersonLayerUpdateRequest,
    PersonNoteRequest,
    PersonUpdateRequest,
    RelationshipCreateRequest,
    YiHermesChatRequest,
    YiHermesContentUpdateRequest,
    YiHermesFactAddRequest,
    YiHermesGlossaryUpsertRequest,
    YiHermesSoulUpdateRequest,
    YiHermesSummaryAddRequest,
    BatTuCastRequest,
    HaLacCastRequest,
    KyMonCastRequest,
    LienHoaCastRequest,
    TuViCastRequest,
    LucHaoCastRequest,
    LucHaoFeedbackRequest,
    LucHaoSaveCaseRequest,
    PersonalProfileRequest,
)
from collectors.jpl_horizons import get_planet_positions
from collectors.noaa_swpc import get_current_kp
from core.chronos import calculate_chronos_state, parse_local_datetime
from core.config import ALGORITHM_VERSION, ZIWEI_RULESET_ID, ZIWEI_RULESET_LABEL, ZIWEI_SCHOOL
from core.hexagram import (
    apply_moving_lines,
    classify_moving_lines,
    compose_hexagram_binary,
    get_hexagram_by_binary,
    hexagram_to_vector,
    list_hexagrams,
)
from core.hexagram_texts import (
    explain_by_policy,
    get_auto_audit_report,
    get_hexagram_interpretation_v2,
    get_source_matrix,
    get_hexagram_text,
    get_source_coverage,
)
from core.lunar_calendar import lunar_to_solar, solar_to_lunar
from core.yi64.derivations.derived_hexagrams import (
    compute_all_derived,
    derived_summary_dict,
)
from core.yi64.derivations.diep_granularity import compute_diep_sequence_for_datetime
from core.yi64.derivations.mai_hoa_nntt import (
    METHOD_ID as MAI_HOA_NNTT_METHOD_ID,
    SOURCE_REF as MAI_HOA_NNTT_SOURCE_REF,
    derivation_summary as mai_hoa_nntt_summary,
    derive_line_states as mai_hoa_nntt_lines,
)
from core.yi64.narrative import build_narrative
from core.yi64.transforms import lines_to_binary, moving_lines_from_states
from engine.gps_engine import compute_gps_day
from engine.gps_storage import (
    BackDatingError,
    DuplicatePredictionError,
    FeedbackTooEarlyError,
    GpsDisabledError,
    PredictionLogError,
    compute_accuracy_stats,
    list_predictions,
    register_predictions,
    submit_feedback,
)
from engine.family_system import FamilyMember, compute_family_resonance
from engine.personal_quai import compute_natal_hexagram, score_compatibility
from engine.van_trong_van import compute_van_trong_van
from data.database import init_db, store_json
from engine.personal import BirthProfile, build_personal_vector, generate_milestone_prompts
from engine.lien_hoa import cast_lien_hoa
from engine.luc_hao import InteractionSignal, cast_luc_hao
from engine.resonance import calculate_sync_score
from engine.scoring import calculate_scores
from engine.eclipses import compute_eclipses
from engine.life_timeline import compute_life_timeline
from engine.lunar_returns import compute_lunar_returns
from engine.progressions import (
    compute_progressed_chart,
    compute_progressed_moon_timeline,
)
from engine.returns import compute_solar_returns
from engine.sky import calculate_sky_chart
from engine.solar_arc import compute_solar_arc_hits
from engine.transit_timeline import compute_transit_hits


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    # Bootstrap founder Person profile on first startup (idempotent)
    try:
        from engine.yi_hermes.persons import ensure_founder
        ensure_founder()
    except Exception:
        # Don't break app startup if founder profile init fails
        import logging
        logging.exception("ensure_founder() failed at startup")
    # Bootstrap YI-Lexicon core seed (idempotent — skips existing concepts)
    try:
        from engine.yi_lexicon.core_seed import seed_all
        seed_all()
    except Exception:
        import logging
        logging.exception("yi_lexicon seed_all() failed at startup")
    yield


app = FastAPI(title="YI-CHRONOS MVP", version=ALGORITHM_VERSION, lifespan=lifespan)
_cors_env = os.environ.get("YI_CHRONOS_CORS_ORIGINS", "")
_CORS_ORIGINS = [o.strip() for o in _cors_env.split(",") if o.strip()] or [
    "http://localhost:5173",
    "http://localhost:5174",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Multi-user auth (tính năng tích hợp của YI):
# - Founder (anh) đăng nhập 1 lần, mọi panel dùng profile anh
# - User mới (gia đình/khách) đăng ký, có namespace persons + quẻ history riêng
# - Owner thấy mọi tab, user thường ẩn dev tabs (Cài đặt, Lexicon, ...)
from api.auth import router as auth_router  # noqa: E402
from api.admin import router as admin_router  # noqa: E402
from api.atomization import router as atomization_router  # noqa: E402
from api.tu_vi_3layer import router as tu_vi_3layer_router  # noqa: E402
from api.atoms_verify import router as atoms_verify_router  # noqa: E402
from api.thiet_ban import router as thiet_ban_router  # noqa: E402
from api.hoang_cuc import router as hoang_cuc_router  # noqa: E402
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(atomization_router)
app.include_router(tu_vi_3layer_router)
app.include_router(atoms_verify_router)
app.include_router(thiet_ban_router)
app.include_router(hoang_cuc_router)

# ⭐ Serve figures from restored books — cho UI hiển thị ảnh minh hoạ
from fastapi.staticfiles import StaticFiles
from pathlib import Path as _Path
_YI_ROOT = _Path(os.environ.get("YI_PROJECT_ROOT", "/Users/ozvietnamdesktop/Desktop/yi"))
_FIGURES_ROOT = _YI_ROOT / "data" / "yi_restored"
if _FIGURES_ROOT.exists():
    app.mount("/figures", StaticFiles(directory=str(_FIGURES_ROOT)), name="figures")

# Workbench static — section-aware research project (đúng nguyên tắc 2026-06-09)
_WORKBENCH_ROOT = _YI_ROOT / "client" / "workbench"
if _WORKBENCH_ROOT.exists():
    app.mount("/workbench", StaticFiles(directory=str(_WORKBENCH_ROOT), html=True), name="workbench")


def _derive_hexagram_state(state) -> dict[str, object]:
    """Derive primary + 5 derived hexagrams via Mai Hoa Niên-Nguyệt-Nhật-Thời.

    Replaces previous ad-hoc cycle-index trigram math. Source:
    Thiệu Khang Tiết — Mai Hoa Dịch Số Toàn Tập.
    """
    line_states = mai_hoa_nntt_lines(state)
    binary = lines_to_binary(line_states)
    moving_lines_tuple = moving_lines_from_states(line_states)
    moving_lines = list(moving_lines_tuple)
    moving_line_policy = classify_moving_lines(moving_lines)

    derived = compute_all_derived(binary, moving_lines_tuple)
    primary_hex = get_hexagram_by_binary(binary)
    transformed_hex = get_hexagram_by_binary(derived["bien"].binary_code)
    transformed_binary = derived["bien"].binary_code

    explanation = explain_by_policy(
        hexagram_name=primary_hex.name_vi,
        transformed_name=transformed_hex.name_vi,
        moving_lines=moving_lines,
        moving_line_policy=moving_line_policy,
    )

    return {
        # Backward-compatible fields (existing UI / tests rely on these).
        "hexagram": primary_hex,
        "binary": binary,
        "moving_lines": moving_lines,
        "moving_line_policy": moving_line_policy,
        "transformed_binary": transformed_binary,
        "transformed_hexagram": transformed_hex,
        "explanation": explanation,
        # New: full Mai Hoa NNTT provenance + 5 derived hexagrams.
        "method_id": MAI_HOA_NNTT_METHOD_ID,
        "source_ref": MAI_HOA_NNTT_SOURCE_REF,
        "derivation": mai_hoa_nntt_summary(state),
        "derived_hexagrams": derived_summary_dict(binary, moving_lines_tuple),
    }


def build_universe_snapshot(datetime_local: str | None = None, timezone_name: str = "Asia/Ho_Chi_Minh") -> dict[str, object]:
    state = calculate_chronos_state(datetime_local, timezone_name)
    kp = get_current_kp()
    scores = calculate_scores(state, float(kp["kp_index"]))
    yi = _derive_hexagram_state(state)
    hexagram = yi["hexagram"]
    transformed = yi["transformed_hexagram"]
    binary = yi["binary"]
    payload = {
        "timestamp_utc": state.timestamp_utc,
        "timezone": state.timezone,
        "ganzhi": state.ganzhi.model_dump(),
        "solar_term": state.solar_term.model_dump(),
        "moon_phase": {
            "name": state.moon_phase.name,
            "illumination": state.moon_phase.illumination,
        },
        "almanac": state.almanac.model_dump(),
        "space_weather": kp,
        "yi_state": {
            "hexagram_id": hexagram.id,
            "king_wen_index": hexagram.king_wen_index,
            "hexagram_name": hexagram.name_vi,
            "hexagram_binary": binary,
            "upper_trigram": hexagram.upper_trigram,
            "lower_trigram": hexagram.lower_trigram,
            "moving_lines": yi["moving_lines"],
            "moving_line_policy": yi["moving_line_policy"],
            "transformed_binary": yi["transformed_binary"],
            "transformed_hexagram_name": transformed.name_vi,
            "yi_vector": hexagram_to_vector(binary),
            "source_ref": hexagram.source_ref,
            "interpretation": yi["explanation"],
        },
        "scores": scores,
        "reflection_prompt": "Tín hiệu nhiều tầng đang thay đổi nhẹ trong khung hiện tại. Hãy quan sát và đối chiếu với trải nghiệm thực.",
        "algorithm_version": ALGORITHM_VERSION,
        "ziwei_school": ZIWEI_SCHOOL,
        "ziwei_ruleset_id": ZIWEI_RULESET_ID,
        "ziwei_ruleset_label": ZIWEI_RULESET_LABEL,
    }
    store_json("universe_snapshot", "snapshot_id", payload, ALGORITHM_VERSION, key=f"u_{uuid4().hex}")
    return payload


@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "algorithm_version": ALGORITHM_VERSION,
        "ziwei_school": ZIWEI_SCHOOL,
        "ziwei_ruleset_id": ZIWEI_RULESET_ID,
    }


@app.get("/api/ruleset/active")
def active_ruleset() -> dict[str, str]:
    return {
        "ziwei_school": ZIWEI_SCHOOL,
        "ziwei_ruleset_id": ZIWEI_RULESET_ID,
        "ziwei_ruleset_label": ZIWEI_RULESET_LABEL,
        "algorithm_version": ALGORITHM_VERSION,
        "status": "active",
    }


@app.post("/calculate")
def calculate(request: CalculateRequest) -> dict[str, object]:
    state = calculate_chronos_state(request.datetime_local, request.timezone)
    yi = _derive_hexagram_state(state)
    hexagram = yi["hexagram"]
    transformed = yi["transformed_hexagram"]
    response = {
        **state.model_dump(),
        "yi_state": {
            "hexagram_id": hexagram.id,
            "king_wen_index": hexagram.king_wen_index,
            "hexagram_name": hexagram.name_vi,
            "hexagram_binary": yi["binary"],
            "upper_trigram": hexagram.upper_trigram,
            "lower_trigram": hexagram.lower_trigram,
            "moving_lines": yi["moving_lines"],
            "moving_line_policy": yi["moving_line_policy"],
            "transformed_binary": yi["transformed_binary"],
            "transformed_hexagram_name": transformed.name_vi,
            "source_ref": hexagram.source_ref,
            "interpretation": yi["explanation"],
        },
        "algorithm_version": ALGORITHM_VERSION,
        "ziwei_school": ZIWEI_SCHOOL,
        "ziwei_ruleset_id": ZIWEI_RULESET_ID,
        "ziwei_ruleset_label": ZIWEI_RULESET_LABEL,
    }
    if request.question_text and request.interaction_signal:
        response["luc_hao_state"] = cast_luc_hao(
            datetime_local=request.datetime_local,
            timezone=request.timezone,
            question_text=request.question_text,
            interaction=InteractionSignal(**request.interaction_signal.model_dump()),
        )
    return response


@app.get("/api/universe-now")
def universe_now(lat: float | None = None, lon: float | None = None) -> dict[str, object]:
    payload = build_universe_snapshot()
    payload["sky"] = calculate_sky_chart(lat=lat, lon=lon).to_dict()
    return payload


@app.get("/api/sky-now")
def sky_now(
    lat: float | None = None,
    lon: float | None = None,
    at: str | None = None,
) -> dict[str, object]:
    """Western astrology state of the sky.

    Query params:
    - lat, lon: observer coordinates (degrees). Both required for ASC/MC.
    - at: ISO 8601 UTC timestamp (e.g. "2026-05-10T15:00:00Z"). Defaults to now.
    """
    dt_utc = None
    if at:
        cleaned = at.replace("Z", "+00:00")
        dt_utc = datetime.fromisoformat(cleaned)
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        else:
            dt_utc = dt_utc.astimezone(timezone.utc)
    return calculate_sky_chart(dt_utc=dt_utc, lat=lat, lon=lon).to_dict()


def _parse_birth_utc(birth_at: str) -> datetime:
    cleaned = birth_at.replace("Z", "+00:00")
    dt = datetime.fromisoformat(cleaned)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt


@app.get("/api/transit-hits")
def transit_hits(
    birth_at: str,
    lat: float | None = None,
    lon: float | None = None,
    span_years: int = 90,
) -> dict[str, object]:
    """Compute transit hits from slow planets to natal personal points.

    Query params:
    - birth_at: ISO 8601 (UTC if no offset).
    - lat, lon: birth location for ASC/MC contacts (optional).
    - span_years: 1..120, defaults 90.
    """
    birth_dt = _parse_birth_utc(birth_at)
    hits = compute_transit_hits(birth_dt, lat=lat, lon=lon, span_years=span_years)
    return {
        "birth_utc": birth_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "span_years": span_years,
        "has_location": lat is not None and lon is not None,
        "ephemeris_source": "JPL DE440s",
        "hits": [h.to_dict() for h in hits],
    }


@app.get("/api/progressed-chart")
def progressed_chart(
    birth_at: str,
    at_age: float,
    lat: float | None = None,
    lon: float | None = None,
) -> dict[str, object]:
    """Secondary progression chart at given age (1 day = 1 year)."""
    birth_dt = _parse_birth_utc(birth_at)
    chart = compute_progressed_chart(birth_dt, at_age_years=at_age, lat=lat, lon=lon)
    return {
        "birth_utc": birth_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "at_age": at_age,
        "ephemeris_source": "JPL DE440s",
        "chart": chart.to_dict(),
    }


@app.get("/api/progressed-moon-timeline")
def progressed_moon_timeline(
    birth_at: str,
    span_years: int = 90,
) -> dict[str, object]:
    """Progressed Moon's sign across a lifespan."""
    birth_dt = _parse_birth_utc(birth_at)
    phases = compute_progressed_moon_timeline(birth_dt, span_years=span_years)
    return {
        "birth_utc": birth_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "span_years": span_years,
        "ephemeris_source": "JPL DE440s",
        "phases": [p.to_dict() for p in phases],
    }


@app.get("/api/lunar-returns")
def lunar_returns(
    birth_at: str,
    from_at: str | None = None,
    count: int = 12,
    lat: float | None = None,
    lon: float | None = None,
) -> dict[str, object]:
    """Next `count` lunar returns starting at or after `from_at` (default now)."""
    birth_dt = _parse_birth_utc(birth_at)
    from_dt = _parse_birth_utc(from_at) if from_at else None
    rs = compute_lunar_returns(birth_dt, from_dt=from_dt, count=count, lat=lat, lon=lon)
    return {
        "birth_utc": birth_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "from_utc": from_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z") if from_dt else None,
        "count": count,
        "ephemeris_source": "JPL DE440s",
        "returns": [r.to_dict() for r in rs],
    }


@app.get("/api/solar-arc-hits")
def solar_arc_hits(
    birth_at: str,
    lat: float | None = None,
    lon: float | None = None,
    span_years: int = 90,
) -> dict[str, object]:
    """Solar arc directions: arc'd planet aspects to natal points."""
    birth_dt = _parse_birth_utc(birth_at)
    hits = compute_solar_arc_hits(birth_dt, lat=lat, lon=lon, span_years=span_years)
    return {
        "birth_utc": birth_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "span_years": span_years,
        "has_location": lat is not None and lon is not None,
        "ephemeris_source": "JPL DE440s",
        "hits": [h.to_dict() for h in hits],
    }


@app.get("/api/eclipses")
def eclipses_api(
    birth_at: str,
    lat: float | None = None,
    lon: float | None = None,
    span_years: int = 90,
    only_activated: bool = True,
) -> dict[str, object]:
    """Solar/lunar eclipses + activation against natal points."""
    birth_dt = _parse_birth_utc(birth_at)
    es = compute_eclipses(birth_dt, lat=lat, lon=lon, span_years=span_years, only_activated=only_activated)
    return {
        "birth_utc": birth_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "span_years": span_years,
        "only_activated": only_activated,
        "ephemeris_source": "JPL DE440s",
        "eclipses": [e.to_dict() for e in es],
    }


@app.get("/api/solar-returns")
def solar_returns(
    birth_at: str,
    lat: float | None = None,
    lon: float | None = None,
    span_years: int = 90,
) -> dict[str, object]:
    """Compute exact Solar Return moments + chart for each year of life."""
    birth_dt = _parse_birth_utc(birth_at)
    rs = compute_solar_returns(birth_dt, lat=lat, lon=lon, span_years=span_years)
    return {
        "birth_utc": birth_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "span_years": span_years,
        "has_location": lat is not None and lon is not None,
        "ephemeris_source": "JPL DE440s",
        "returns": [r.to_dict() for r in rs],
    }


@app.get("/api/life-timeline")
def life_timeline(
    birth_at: str,
    span_years: int = 90,
) -> dict[str, object]:
    """Compute astrological life milestones from birth.

    Query params:
    - birth_at: ISO 8601 (UTC if no offset). E.g. "1985-07-20T03:30:00Z".
    - span_years: how far ahead to scan (default 90).
    """
    birth_dt = _parse_birth_utc(birth_at)
    milestones = compute_life_timeline(birth_dt, span_years=span_years)
    return {
        "birth_utc": birth_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "span_years": span_years,
        "ephemeris_source": "JPL DE440s",
        "milestones": [m.to_dict() for m in milestones],
    }


@app.get("/api/planet-positions")
def planet_positions() -> dict[str, object]:
    return get_planet_positions()


@app.get("/api/gps-day")
def gps_day(
    birth_datetime_local: str,
    target_date: str,
    timezone: str = "Asia/Ho_Chi_Minh",
    min_score: int = 55,
) -> dict[str, object]:
    """Compute GPS recommendations for a specific date (preview, no persistence)."""
    from datetime import date as _date
    natal = compute_natal_hexagram(birth_datetime_local, timezone)
    target = _date.fromisoformat(target_date)
    gps = compute_gps_day(natal, target, timezone, min_score_for_trigger=min_score)
    return gps.to_dict()


@app.post("/api/gps-pre-register")
def gps_pre_register(payload: dict) -> dict[str, object]:
    """Pre-register every trigger of a future GPS day as immutable predictions.

    payload: { birth_datetime_local, target_date, timezone, min_score }
    """
    from datetime import date as _date
    birth_datetime_local = payload.get("birth_datetime_local")
    target_date = payload.get("target_date")
    timezone = payload.get("timezone", "Asia/Ho_Chi_Minh")
    min_score = int(payload.get("min_score", 70))
    if not birth_datetime_local or not target_date:
        return {"status": "error", "message": "birth_datetime_local and target_date required"}

    natal = compute_natal_hexagram(birth_datetime_local, timezone)
    target = _date.fromisoformat(target_date)
    gps = compute_gps_day(natal, target, timezone, min_score_for_trigger=min_score)
    try:
        receipts = register_predictions(gps)
    except GpsDisabledError as e:
        return {"status": "gps_disabled", "message": str(e), "runtime_mode": gps.runtime_mode}
    except BackDatingError as e:
        return {"status": "back_dating_rejected", "message": str(e)}
    except DuplicatePredictionError as e:
        return {"status": "duplicate", "message": str(e)}
    return {
        "status": "registered",
        "profile_hash": gps.profile_hash,
        "for_date": gps.date_local,
        "registered_count": len(receipts),
        "receipts": receipts,
        "runtime_mode": gps.runtime_mode,
    }


@app.get("/api/gps-predictions")
def gps_predictions(profile_hash: str, status: str | None = None, limit: int = 200) -> dict[str, object]:
    """List immutable predictions for a profile."""
    rows = list_predictions(profile_hash, status=status, limit=limit)
    return {"profile_hash": profile_hash, "count": len(rows), "predictions": rows}


@app.post("/api/gps-prediction-feedback")
def gps_prediction_feedback(payload: dict) -> dict[str, object]:
    """Submit feedback for an expired prediction.

    payload: { prediction_id, response_enum, confidence_enum, actual_outcome }
    """
    prediction_id = payload.get("prediction_id")
    response_enum = payload.get("response_enum")
    confidence_enum = payload.get("confidence_enum", "unsure")
    actual_outcome = payload.get("actual_outcome")
    if not prediction_id or not response_enum:
        return {"status": "error", "message": "prediction_id and response_enum required"}
    try:
        receipt = submit_feedback(prediction_id, response_enum, confidence_enum, actual_outcome)
    except FeedbackTooEarlyError as e:
        return {"status": "too_early", "message": str(e)}
    except PredictionLogError as e:
        return {"status": "error", "message": str(e)}
    except ValueError as e:
        return {"status": "invalid_input", "message": str(e)}
    return {"status": "stored", **receipt}


@app.get("/api/gps-accuracy")
def gps_accuracy(profile_hash: str) -> dict[str, object]:
    """Rolling accuracy metrics for a profile's GPS predictions."""
    return compute_accuracy_stats(profile_hash)


def _parse_family_members(raw: list | None) -> list:
    if not raw:
        return []
    return [
        FamilyMember(
            role=m.get("role", "self"),
            name=m.get("name", ""),
            birth_year=int(m["birth_year"]),
            birth_datetime_local=m.get("birth_datetime_local"),
            timezone=m.get("timezone", "Asia/Ho_Chi_Minh"),
        )
        for m in raw
    ]


@app.post("/api/van-trong-van-with-family")
def van_trong_van_with_family(payload: dict) -> dict[str, object]:
    """30-day outlook with optional family overlay per day.

    payload: {
      birth_datetime_local, timezone, start_date (YYYY-MM-DD), span_days,
      members: [...] (optional, same shape as /api/family-resonance)
    }
    """
    from datetime import datetime as _dt
    from zoneinfo import ZoneInfo

    birth_local = payload.get("birth_datetime_local")
    timezone = payload.get("timezone", "Asia/Ho_Chi_Minh")
    span_days = int(payload.get("span_days", 30))
    if not birth_local:
        return {"status": "error", "message": "birth_datetime_local required"}

    natal = compute_natal_hexagram(birth_local, timezone)
    family = _parse_family_members(payload.get("members"))
    start_iso = payload.get("start_date")
    if start_iso:
        start_dt = _dt.fromisoformat(start_iso).replace(tzinfo=ZoneInfo(timezone))
    else:
        start_dt = None

    result = compute_van_trong_van(
        natal,
        start_date=start_dt,
        span_days=span_days,
        timezone_name=timezone,
        family_members=family or None,
    )
    return {"status": "ok", **result.to_dict()}


@app.post("/api/gps-day-with-family")
def gps_day_with_family(payload: dict) -> dict[str, object]:
    """GPS preview for one date with optional family overlay per trigger."""
    from datetime import date as _date

    birth_local = payload.get("birth_datetime_local")
    target_date = payload.get("target_date")
    timezone = payload.get("timezone", "Asia/Ho_Chi_Minh")
    min_score = int(payload.get("min_score", 55))
    if not birth_local or not target_date:
        return {"status": "error", "message": "birth_datetime_local + target_date required"}

    natal = compute_natal_hexagram(birth_local, timezone)
    family = _parse_family_members(payload.get("members"))
    target = _date.fromisoformat(target_date)
    gps = compute_gps_day(
        natal, target, timezone,
        min_score_for_trigger=min_score,
        family_members=family or None,
    )
    return {"status": "ok", **gps.to_dict()}


@app.post("/api/gps-pre-register-with-family")
def gps_pre_register_with_family(payload: dict) -> dict[str, object]:
    """Pre-register predictions for a future date — family-aware variant."""
    from datetime import date as _date

    birth_local = payload.get("birth_datetime_local")
    target_date = payload.get("target_date")
    timezone = payload.get("timezone", "Asia/Ho_Chi_Minh")
    min_score = int(payload.get("min_score", 70))
    if not birth_local or not target_date:
        return {"status": "error", "message": "birth_datetime_local + target_date required"}

    natal = compute_natal_hexagram(birth_local, timezone)
    family = _parse_family_members(payload.get("members"))
    target = _date.fromisoformat(target_date)
    gps = compute_gps_day(
        natal, target, timezone,
        min_score_for_trigger=min_score,
        family_members=family or None,
    )
    try:
        receipts = register_predictions(gps)
    except GpsDisabledError as e:
        return {"status": "gps_disabled", "message": str(e), "runtime_mode": gps.runtime_mode}
    except BackDatingError as e:
        return {"status": "back_dating_rejected", "message": str(e)}
    except DuplicatePredictionError as e:
        return {"status": "duplicate", "message": str(e)}
    return {
        "status": "registered",
        "profile_hash": gps.profile_hash,
        "for_date": gps.date_local,
        "registered_count": len(receipts),
        "receipts": receipts,
        "runtime_mode": gps.runtime_mode,
        "family_aware": bool(family),
    }


@app.post("/api/family-resonance")
def family_resonance(payload: dict) -> dict[str, object]:
    """Compute multi-actor household hexagram analysis.

    payload:
      {
        "members": [
          {"role": "self|spouse|child|parent|sibling|boss", "name": str,
           "birth_year": int,
           "birth_datetime_local": "YYYY-MM-DDTHH:MM:SS" (optional),
           "timezone": "Asia/Ho_Chi_Minh" (optional)},
          ...
        ],
        "wedding_datetime_local": "YYYY-MM-DDTHH:MM:SS" (optional),
        "wedding_timezone": "Asia/Ho_Chi_Minh" (optional)
      }
    """
    raw_members = payload.get("members") or []
    if not raw_members:
        return {"status": "error", "message": "members must not be empty"}
    members = [
        FamilyMember(
            role=m.get("role", "self"),
            name=m.get("name", ""),
            birth_year=int(m["birth_year"]),
            birth_datetime_local=m.get("birth_datetime_local"),
            timezone=m.get("timezone", "Asia/Ho_Chi_Minh"),
        )
        for m in raw_members
    ]
    wedding_local = payload.get("wedding_datetime_local")
    wedding_tz = payload.get("wedding_timezone", "Asia/Ho_Chi_Minh")
    result = compute_family_resonance(
        members,
        wedding_datetime_local=wedding_local,
        wedding_timezone=wedding_tz,
    )
    return {"status": "ok", **result.to_dict()}


@app.get("/api/personal-quai")
def personal_quai(
    birth_datetime_local: str,
    timezone: str = "Asia/Ho_Chi_Minh",
) -> dict[str, object]:
    """Compute quẻ bản mệnh + 5 derived charts from birth Mai Hoa NNTT."""
    natal = compute_natal_hexagram(birth_datetime_local, timezone)
    return natal.to_dict()


@app.get("/api/van-trong-van")
def van_trong_van(
    birth_datetime_local: str,
    timezone: str = "Asia/Ho_Chi_Minh",
    start_date: str | None = None,
    span_days: int = 30,
) -> dict[str, object]:
    """30-day forward outlook of compatibility with quẻ bản mệnh."""
    from zoneinfo import ZoneInfo

    natal = compute_natal_hexagram(birth_datetime_local, timezone)
    if start_date:
        start_dt = datetime.fromisoformat(start_date).replace(tzinfo=ZoneInfo(timezone))
    else:
        start_dt = None
    result = compute_van_trong_van(
        natal, start_date=start_dt, span_days=span_days, timezone_name=timezone
    )
    return result.to_dict()


@app.get("/api/yi-narrative")
def yi_narrative(
    datetime_local: str | None = None,
    timezone: str = "Asia/Ho_Chi_Minh",
) -> dict[str, object]:
    """6-hexagram timeline narrative for the given moment (Mai Hoa NNTT)."""
    state = calculate_chronos_state(datetime_local, timezone)
    n = build_narrative(state)
    return {
        "timezone": timezone,
        "local_datetime": state.local_datetime,
        "ganzhi": state.ganzhi.model_dump(),
        "lunar_date": state.almanac.lunar_date,
        **n.to_dict(),
    }


@app.get("/api/yi-diep-sequence")
def yi_diep_sequence(
    datetime_local: str | None = None,
    timezone: str = "Asia/Ho_Chi_Minh",
    diep_count: int = 5,
) -> dict[str, object]:
    """Lá/cánh hoa — N sub-hexagrams within an hour (default 5)."""
    seq = compute_diep_sequence_for_datetime(datetime_local, timezone, diep_count=diep_count)
    return {
        "timezone": timezone,
        **seq.to_dict(),
    }


@app.get("/api/hexagrams-master")
def hexagrams_master() -> dict[str, object]:
    records = [
        {
            "king_wen_index": item.king_wen_index,
            "legacy_binary_id": item.id,
            "name_vi": item.name_vi,
            "name_en": item.name_en,
            "binary": item.binary,
            "upper_trigram": item.upper_trigram,
            "lower_trigram": item.lower_trigram,
            "source_ref": item.source_ref,
        }
        for item in sorted(list_hexagrams(), key=lambda h: h.king_wen_index)
    ]
    return {"count": len(records), "records": records}


@app.get("/api/hexagram-text/{name_vi}")
def hexagram_text(name_vi: str) -> dict[str, object]:
    record = get_hexagram_text(name_vi)
    if not record:
        return {"status": "not_found", "name_vi": name_vi}
    return {"status": "ok", "record": record}


@app.get("/api/hexagram-interpretation-v2/{king_wen_index}")
def hexagram_interpretation_v2(king_wen_index: int) -> dict[str, object]:
    record = get_hexagram_interpretation_v2(king_wen_index=king_wen_index)
    if not record:
        return {"status": "not_found", "king_wen_index": king_wen_index}
    return {"status": "ok", "record": record}


@app.get("/api/hexagram-by-slug/{slug}")
def hexagram_by_slug(slug: str) -> dict[str, object]:
    """Resolve a hexagram slug (e.g. '3-thuy-loi-truan') to full interpretation."""
    from core.yi64.slugs import king_wen_from_slug, slug_for

    king_wen_index = king_wen_from_slug(slug)
    if king_wen_index is None:
        return {"status": "not_found", "slug": slug}
    record = get_hexagram_interpretation_v2(king_wen_index=king_wen_index)
    if not record:
        return {"status": "not_found", "slug": slug, "king_wen_index": king_wen_index}
    return {
        "status": "ok",
        "slug": slug,
        "canonical_slug": slug_for(king_wen_index),
        "king_wen_index": king_wen_index,
        "record": record,
    }


@app.get("/api/hexagram-slugs")
def hexagram_slugs() -> dict[str, object]:
    """Return the full {king_wen: slug} table — useful for client-side routing/sitemaps."""
    from core.yi64.slugs import slug_table

    return {"status": "ok", "slugs": slug_table()}


@app.get("/api/hexagram-source-coverage")
def hexagram_source_coverage() -> dict[str, object]:
    report = get_source_coverage()
    return {"status": "ok", "report": report}


@app.get("/api/hexagram-source-matrix")
def hexagram_source_matrix() -> dict[str, object]:
    report = get_source_matrix()
    return {"status": "ok", "report": report}


@app.get("/api/hexagram-auto-audit")
def hexagram_auto_audit() -> dict[str, object]:
    report = get_auto_audit_report()
    return {"status": "ok", "report": report}


@app.post("/api/calendar-convert")
def calendar_convert(request: CalendarConvertRequest) -> dict[str, object]:
    local_dt = parse_local_datetime(request.datetime_local, request.timezone)
    zone = ZoneInfo(request.timezone)
    tz_offset_hours = local_dt.utcoffset().total_seconds() / 3600 if local_dt.utcoffset() else 7.0

    if request.source_calendar == "solar":
        lunar = solar_to_lunar(local_dt.day, local_dt.month, local_dt.year, tz_offset_hours)
        converted = datetime(
            lunar.year,
            lunar.month,
            lunar.day,
            local_dt.hour,
            local_dt.minute,
            local_dt.second,
            tzinfo=zone,
        )
        return {
            "source_calendar": "solar",
            "target_calendar": "lunar",
            "source_datetime_local": local_dt.replace(microsecond=0).isoformat(),
            "converted_datetime_local": converted.replace(microsecond=0).isoformat(),
            "is_leap_month": lunar.is_leap,
            "timezone": request.timezone,
            "ziwei_school": ZIWEI_SCHOOL,
            "ziwei_ruleset_id": ZIWEI_RULESET_ID,
        }

    day, month, year = lunar_to_solar(
        local_dt.day,
        local_dt.month,
        local_dt.year,
        request.is_leap_month,
        tz_offset_hours,
    )
    converted = datetime(year, month, day, local_dt.hour, local_dt.minute, local_dt.second, tzinfo=zone)
    return {
        "source_calendar": "lunar",
        "target_calendar": "solar",
        "source_datetime_local": local_dt.replace(microsecond=0).isoformat(),
        "converted_datetime_local": converted.replace(microsecond=0).isoformat(),
        "is_leap_month": request.is_leap_month,
        "timezone": request.timezone,
        "ziwei_school": ZIWEI_SCHOOL,
        "ziwei_ruleset_id": ZIWEI_RULESET_ID,
    }


@app.post("/api/compare-basic")
def compare_basic(request: CompareBasicRequest) -> dict[str, object]:
    local_dt = parse_local_datetime(request.birth_datetime_local, request.timezone)
    utc_dt = local_dt.astimezone(timezone.utc)
    chronos = calculate_chronos_state(request.birth_datetime_local, request.timezone)
    planets = get_planet_positions(utc_dt)

    earth = next((planet for planet in planets.get("planets", []) if planet.get("name_vi") == "Trái Đất"), None)
    moon_name_map = {
        "new_moon": "Sóc",
        "waxing_crescent": "Trăng non",
        "first_quarter": "Thượng huyền",
        "waxing_gibbous": "Trăng gần tròn",
        "full_moon": "Vọng",
        "waning_gibbous": "Trăng khuyết dần",
        "last_quarter": "Hạ huyền",
        "waning_crescent": "Tàn nguyệt",
    }
    moon_phase_label = moon_name_map.get(chronos.moon_phase.name, chronos.moon_phase.name)
    score = 0
    checks = []

    checks.append(
        {
            "id": "time_frame",
            "label": "Khung thời gian",
            "status": "matched",
            "detail": f"{chronos.ganzhi.hour} · {chronos.solar_term.name_vi}",
        }
    )
    score += 1

    moon_status = "matched" if chronos.moon_phase.illumination >= 0 else "unknown"
    checks.append(
        {
            "id": "moon_phase",
            "label": "Pha Trăng",
            "status": moon_status,
            "detail": f"{moon_phase_label} ({chronos.moon_phase.illumination:.3f})",
        }
    )
    score += 1 if moon_status == "matched" else 0

    earth_status = "matched" if earth else "unknown"
    checks.append(
        {
            "id": "earth_position",
            "label": "Vector Trái Đất",
            "status": earth_status,
            "detail": (
                f"r={earth['distance_au']:.4f} AU, lon={earth['ecliptic_longitude_deg']:.2f}°"
                if earth
                else "Không có dữ liệu Trái Đất"
            ),
        }
    )
    score += 1 if earth else 0

    checks.append(
        {
            "id": "almanac_consistency",
            "label": "Lịch vạn niên cơ bản",
            "status": "matched",
            "detail": f"Âm lịch {chronos.almanac.lunar_date} · Trực {chronos.almanac.truc_of_day} · {chronos.almanac.weekday_vi}",
        }
    )
    score += 1

    confidence = round(score / max(len(checks), 1), 3)
    report_lines = [
        "# Báo cáo so sánh cơ bản",
        f"- Ruleset: {ZIWEI_RULESET_ID} ({ZIWEI_RULESET_LABEL})",
        f"- Thời điểm sinh: {local_dt.replace(microsecond=0).isoformat()}",
        f"- Múi giờ: {request.timezone}",
        f"- Nguồn thiên văn: {planets.get('source', 'UNKNOWN')}",
        f"- Lịch vạn niên: âm lịch {chronos.almanac.lunar_date} · trực {chronos.almanac.truc_of_day}",
        f"- Vận hạn cơ bản: năm {chronos.almanac.annual_fortune} · tháng {chronos.almanac.monthly_fortune} · ngày {chronos.almanac.daily_fortune} · giờ {chronos.almanac.hourly_fortune}",
        "",
    ]
    for check in checks:
        report_lines.append(f"- [{check['status']}] {check['label']}: {check['detail']}")

    return {
        "birth_datetime_local": local_dt.replace(microsecond=0).isoformat(),
        "timezone": request.timezone,
        "location_ref": request.location_ref,
        "confidence": confidence,
        "checks": checks,
        "report_markdown": "\n".join(report_lines),
        "algorithm_version": ALGORITHM_VERSION,
        "ziwei_school": ZIWEI_SCHOOL,
        "ziwei_ruleset_id": ZIWEI_RULESET_ID,
        "ziwei_ruleset_label": ZIWEI_RULESET_LABEL,
    }


@app.post("/api/personal-profile")
def personal_profile(request: PersonalProfileRequest) -> dict[str, object]:
    profile = BirthProfile(**request.model_dump())
    personal_vector = build_personal_vector(profile)
    universe = build_universe_snapshot(timezone_name=request.timezone)
    sync_score = calculate_sync_score(personal_vector, universe["scores"])
    user_id = f"user_{uuid4().hex}"
    store_json("user_profile", "user_id", {**request.model_dump(), **personal_vector}, ALGORITHM_VERSION, key=user_id)
    store_json("personal_profile_cache", "user_id", personal_vector, ALGORITHM_VERSION, key=user_id)
    prompts = []
    for prompt in generate_milestone_prompts(profile):
        row = {**prompt, "user_id": user_id, "algorithm_version": ALGORITHM_VERSION}
        store_json("milestone_prompt", "prompt_id", row, ALGORITHM_VERSION, key=prompt["prompt_id"])
        prompts.append(prompt)
    return {
        "user_id": user_id,
        "personal_vector": {
            "five_element_bias": personal_vector["five_element_bias"],
            "pillar_summary": personal_vector["pillar_summary"],
        },
        "sync_score": sync_score,
        "milestone_prompts": prompts,
        "algorithm_version": ALGORITHM_VERSION,
        "ziwei_school": ZIWEI_SCHOOL,
        "ziwei_ruleset_id": ZIWEI_RULESET_ID,
        "ziwei_ruleset_label": ZIWEI_RULESET_LABEL,
    }


@app.post("/api/feedback")
def feedback(request: FeedbackRequest) -> dict[str, object]:
    payload = {**request.model_dump(), "algorithm_version": ALGORITHM_VERSION}
    feedback_id = store_json("feedback_event", "feedback_id", payload, ALGORITHM_VERSION, key=f"f_{uuid4().hex}")
    return {"status": "stored", "feedback_id": feedback_id, "algorithm_version": ALGORITHM_VERSION}


@app.post("/api/luc-hao/cast")
def luc_hao_cast(request: LucHaoCastRequest) -> dict[str, object]:
    result = cast_luc_hao(
        datetime_local=request.datetime_local,
        timezone=request.timezone,
        question_text=request.question_text,
        interaction=InteractionSignal(**request.interaction_signal.model_dump()),
    )
    return {
        "timezone": request.timezone,
        "algorithm_version": ALGORITHM_VERSION,
        "ziwei_school": ZIWEI_SCHOOL,
        "ziwei_ruleset_id": ZIWEI_RULESET_ID,
        "ziwei_ruleset_label": ZIWEI_RULESET_LABEL,
        "luc_hao_state": result,
    }


@app.post("/api/luc-hao/save-case")
def luc_hao_save_case(request: LucHaoSaveCaseRequest) -> dict[str, object]:
    payload = {
        "question_text": request.question_text,
        "timezone": request.timezone,
        "luc_hao_state": request.luc_hao_state,
        "interaction_signal": request.interaction_signal.model_dump(),
        "saved_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    case_id = store_json("luc_hao_case", "case_id", payload, ALGORITHM_VERSION, key=f"lh_{uuid4().hex}")
    return {"status": "stored", "case_id": case_id, "algorithm_version": ALGORITHM_VERSION}


@app.post("/api/luc-hao/feedback")
def luc_hao_feedback(request: LucHaoFeedbackRequest) -> dict[str, object]:
    payload = {
        **request.model_dump(),
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    feedback_id = store_json("luc_hao_feedback", "feedback_id", payload, ALGORITHM_VERSION, key=f"lf_{uuid4().hex}")
    return {"status": "stored", "feedback_id": feedback_id, "algorithm_version": ALGORITHM_VERSION}


@app.post("/api/lien-hoa/cast")
def lien_hoa_cast(request: LienHoaCastRequest) -> dict[str, object]:
    result = cast_lien_hoa(
        number_right_hand=request.number_right_hand,
        number_left_hand=request.number_left_hand,
        question_text=request.question_text,
        gender=request.gender,
    )
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "ziwei_school": ZIWEI_SCHOOL,
        "ziwei_ruleset_id": ZIWEI_RULESET_ID,
        "ziwei_ruleset_label": ZIWEI_RULESET_LABEL,
        "lien_hoa_state": result,
    }


# ─── Thần Số Học (Numerology) ────────────────────────────────────────────────


class ThanSoCastRequest(BaseModel):
    name: str
    birth_date: str  # 'YYYY-MM-DD'
    system: str = "pythagorean"  # 'pythagorean' | 'chaldean'
    include_chaldean: bool = True
    target_year: int | None = None


@app.post("/api/than-so/cast")
def than_so_cast(request: ThanSoCastRequest) -> dict[str, object]:
    """Lập lá số Thần Số Học từ TÊN + NGÀY SINH (Pythagoras + đối chiếu Chaldean).

    Paradigm đọc đồng dạng (Iron Rule #4/#6) — KHÔNG predict.
    """
    from engine.than_so import cast_than_so

    return cast_than_so(
        name=request.name,
        birth_date=request.birth_date,
        system=request.system,
        include_chaldean=request.include_chaldean,
        target_year=request.target_year,
    )


@app.get("/api/than-so/glossary")
def than_so_glossary() -> dict[str, object]:
    """Bảng ý nghĩa số 1-9 + master 11/22/33 (cho UI tra cứu)."""
    from engine.than_so.constants import METHOD_ID, number_meanings

    return {"method_id": METHOD_ID, "numbers": number_meanings()}


@app.post("/api/bat-tu/cast")
def bat_tu_cast(request: BatTuCastRequest) -> dict[str, object]:
    """Cast a Bát Tự chart (Tứ trụ + Thập thần + Ngũ hành balance)."""
    from engine.bat_tu import cast_bat_tu

    result = cast_bat_tu(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
    )
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "bat_tu_state": result,
    }


class BatTuLuanGiaiRequest(BaseModel):
    birth_datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    gender: str = "nam"
    current_age: int | None = None  # for Đại Vận current cycle detection


class BatTuLuuNienRequest(BaseModel):
    birth_datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    gender: str = "nam"
    current_age: int | None = None
    target_year: int | None = None  # default = current year
    include_luu_nguyet: bool = True


class BatTuLifeDomainRequest(BaseModel):
    """Generic request for Hôn nhân / Sự nghiệp endpoints."""
    birth_datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    gender: str = "nam"


@app.post("/api/bat-tu/luan-giai")
def bat_tu_luan_giai(request: BatTuLuanGiaiRequest) -> dict[str, object]:
    """Luận giải tổng hợp Bát Tự — synthesize Tứ Trụ + Thập Thần + Cách Cục +
    Trường Sinh + Đại Vận + Dụng Thần into a paradigm-tone narrative.

    Source: Thiệu Vĩ Hoa & Trần Viên — Dự đoán theo Tứ trụ (Chương 1-3).
    Paradigm: Tử Bình KHÔNG predict, đọc đồng dạng → tri mệnh → Bổ cân bằng.
    """
    from engine.bat_tu import cast_bat_tu, compose_luan_giai

    state = cast_bat_tu(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
    )
    # Auto-compute current_age from birth if not provided
    age = request.current_age
    if age is None:
        try:
            from datetime import datetime
            birth_year = int(request.birth_datetime_local[:4])
            age = datetime.now().year - birth_year
        except (ValueError, IndexError):
            age = None

    luan = compose_luan_giai(state, current_age=age)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "bat_tu_state": state,
        "luan_giai": luan,
    }


@app.post("/api/bat-tu/luu-nien")
def bat_tu_luu_nien(request: BatTuLuuNienRequest) -> dict[str, object]:
    """Lưu Niên — phân tích năm hiện tại đi qua lá số + 12 tháng (Lưu Nguyệt).

    Source: Thiệu Vĩ Hoa & Trần Viên — Dự đoán theo Tứ trụ.
    Paradigm: Lưu Niên phản chiếu cấu hình khí năm hiện tại, KHÔNG predict.
    """
    from engine.bat_tu import analyze_luu_nien, cast_bat_tu

    state = cast_bat_tu(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
    )
    age = request.current_age
    if age is None:
        try:
            from datetime import datetime
            birth_year = int(request.birth_datetime_local[:4])
            age = datetime.now().year - birth_year
        except (ValueError, IndexError):
            age = None
    luu = analyze_luu_nien(
        state,
        current_age=age,
        target_year=request.target_year,
        timezone=request.timezone,
        include_luu_nguyet=request.include_luu_nguyet,
    )
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "bat_tu_state": state,
        "luu_nien": luu,
    }


@app.post("/api/bat-tu/hon-nhan")
def bat_tu_hon_nhan(request: BatTuLifeDomainRequest) -> dict[str, object]:
    """Hôn nhân — phân tích Cung Phối + Tài/Quan tinh + Đào hoa + thời điểm.

    Paradigm: KHÔNG dự đoán lấy ai/khi nào — đọc cấu trúc khí.
    Source: Thiệu Vĩ Hoa Q. 4-6.
    """
    from engine.bat_tu import analyze_hon_nhan, cast_bat_tu

    state = cast_bat_tu(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
    )
    hn = analyze_hon_nhan(state)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "bat_tu_state": state,
        "hon_nhan": hn,
    }


@app.post("/api/bat-tu/su-nghiep")
def bat_tu_su_nghiep(request: BatTuLifeDomainRequest) -> dict[str, object]:
    """Sự nghiệp — recommend nghề từ Cách Cục + Dụng Thần + Thập Thần patterns.

    Paradigm: KHÔNG predict, đọc cấu trúc khí → recommend hành phù hợp.
    Source: Thiệu Vĩ Hoa Q. 2 + Q. 4.
    """
    from engine.bat_tu import analyze_su_nghiep, cast_bat_tu

    state = cast_bat_tu(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
    )
    sn = analyze_su_nghiep(state)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "bat_tu_state": state,
        "su_nghiep": sn,
    }


@app.post("/api/bat-tu/tai-van")
def bat_tu_tai_van(request: BatTuLifeDomainRequest) -> dict[str, object]:
    """Tài Vận — phân tích Tài tinh + DM balance + 6 patterns + Đại Vận tài timing.

    Hoàn thành 'tam thân': Hôn nhân ✅ + Sự nghiệp ✅ + Tài vận ✅.
    Source: Thiệu Vĩ Hoa Q. 4-6.
    Paradigm: KHÔNG predict tài lộc khi nào, đọc cấu hình khí tài.
    """
    from engine.bat_tu import analyze_tai_van, cast_bat_tu

    state = cast_bat_tu(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
    )
    tv = analyze_tai_van(state)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "bat_tu_state": state,
        "tai_van": tv,
    }


@app.post("/api/bat-tu/suc-khoe")
def bat_tu_suc_khoe(request: BatTuLifeDomainRequest) -> dict[str, object]:
    """Sức Khỏe — ngũ hành thừa/thiếu → tạng phủ (Trung y) + Đại Vận cảnh báo + dietary."""
    from engine.bat_tu import analyze_suc_khoe, cast_bat_tu

    state = cast_bat_tu(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
    )
    sk = analyze_suc_khoe(state)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "bat_tu_state": state,
        "suc_khoe": sk,
    }


class BatTuCompatibilityRequest(BaseModel):
    person_a_birth: str
    person_b_birth: str
    person_a_gender: str = "nam"
    person_b_gender: str = "nữ"
    timezone: str = "Asia/Ho_Chi_Minh"
    relationship_type: str = "spouse"


@app.post("/api/bat-tu/compatibility")
def bat_tu_compatibility(request: BatTuCompatibilityRequest) -> dict[str, object]:
    """So 2 lá số Bát Tự (vợ-chồng / partner / cha-con / sibling).

    Source: Nạp Âm + 5 hợp Can + Lục/Tam hợp chi.
    Paradigm: KHÔNG predict ly hôn/hạnh phúc, đọc cấu hình tương tác.
    """
    from engine.bat_tu import analyze_compatibility, cast_bat_tu

    chart_a = cast_bat_tu(
        birth_datetime_local=request.person_a_birth,
        timezone=request.timezone,
        gender=request.person_a_gender,
    )
    chart_b = cast_bat_tu(
        birth_datetime_local=request.person_b_birth,
        timezone=request.timezone,
        gender=request.person_b_gender,
    )
    result = analyze_compatibility(chart_a, chart_b, request.relationship_type)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "chart_a": chart_a,
        "chart_b": chart_b,
        "compatibility": result,
    }


class BatTuBaoMenhPDFRequest(BaseModel):
    birth_datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    gender: str = "nam"
    current_age: int | None = None


@app.post("/api/bat-tu/bao-menh-pdf")
def bat_tu_bao_menh_pdf(request: BatTuBaoMenhPDFRequest):
    """Báo Mệnh PDF — compose all luận giải vào 1 PDF artifact (Bookflow v2.0)."""
    import traceback
    from fastapi.responses import JSONResponse, Response
    try:
        from engine.bat_tu.bao_menh_pdf import generate_bao_menh_pdf
        pdf_bytes = generate_bao_menh_pdf(
            birth_datetime_local=request.birth_datetime_local,
            timezone=request.timezone,
            gender=request.gender,
            current_age=request.current_age,
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(limit=20),
            },
        )
    safe_birth = request.birth_datetime_local.replace(":", "-").replace("T", "_")
    filename = f"BaoMenh_{safe_birth}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/bat-tu/luc-than")
def bat_tu_luc_than(request: BatTuLifeDomainRequest) -> dict[str, object]:
    """Lục Thân — Cha + Mẹ + Anh chị em + Vợ/Chồng + Con cái analysis qua Thập Thần."""
    from engine.bat_tu import analyze_luc_than, cast_bat_tu

    state = cast_bat_tu(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
    )
    lt = analyze_luc_than(state)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "bat_tu_state": state,
        "luc_than": lt,
    }


class BatTuAIChatRequest(BaseModel):
    birth_datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    gender: str = "nam"
    question: str
    history: list[dict] | None = None
    provider_preferred: list[str] | None = None


@app.post("/api/bat-tu/ai-chat")
def bat_tu_ai_chat(request: BatTuAIChatRequest) -> dict[str, object]:
    """AI Chat về lá số Bát Tự — Q&A với LLM, context = full luận giải.

    Paradigm: LLM bị strict guard không được predict, chỉ đọc cấu hình khí.
    """
    from engine.bat_tu import cast_bat_tu, chat_about_chart, compose_luan_giai

    state = cast_bat_tu(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
    )
    luan = compose_luan_giai(state)
    result = chat_about_chart(
        state,
        request.question,
        history=request.history,
        luan_giai=luan,
        provider_preferred=request.provider_preferred,
    )
    return {
        "algorithm_version": ALGORITHM_VERSION,
        **result,
    }


class BatTuAuspiciousEventRequest(BaseModel):
    birth_datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    gender: str = "nam"
    event_type: str = "general"  # wedding / business_opening / moving_house / signing_contract / travel / general
    start_date: str  # YYYY-MM-DD
    end_date: str
    top_n: int = 10


@app.post("/api/bat-tu/auspicious-event")
def bat_tu_auspicious_event(request: BatTuAuspiciousEventRequest) -> dict[str, object]:
    """Chọn ngày tốt cho event cụ thể dựa trên Bát Tự + nature of event."""
    from engine.bat_tu import cast_bat_tu, pick_auspicious_dates

    user_chart = cast_bat_tu(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
    )
    result = pick_auspicious_dates(
        user_chart,
        event_type=request.event_type,
        start_date=request.start_date,
        end_date=request.end_date,
        timezone=request.timezone,
        top_n=request.top_n,
    )
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "user_chart": user_chart,
        "auspicious_event": result,
    }


class HaLacLuanGiaiRequest(BaseModel):
    birth_datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    gender: str = "nam"
    current_age: int | None = None


@app.post("/api/ha-lac/luan-giai")
def ha_lac_luan_giai_endpoint(request: HaLacLuanGiaiRequest) -> dict[str, object]:
    """Bát Tự Hà Lạc — luận giải tổng hợp (Học Năng 1974 paradigm).

    Output: 2 quẻ (Tiên thiên + Hậu thiên) + comparison + 12 hào trajectory +
    current stage + Bổ Hướng.

    Paradigm: KHÔNG predict, đọc cấu trúc khí 84-90 năm cuộc đời.
    """
    from engine.ha_lac import cast_ha_lac, compose_ha_lac_luan_giai

    state = cast_ha_lac(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
    )
    age = request.current_age
    if age is None:
        try:
            from datetime import datetime
            birth_year = int(request.birth_datetime_local[:4])
            age = datetime.now().year - birth_year
        except (ValueError, IndexError):
            age = None
    luan = compose_ha_lac_luan_giai(state, current_age=age)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "ha_lac_state": state,
        "luan_giai": luan,
    }


@app.post("/api/ha-lac/cast")
def ha_lac_cast(request: HaLacCastRequest) -> dict[str, object]:
    """Cast Bát Tự Hà Lạc — derives 2 personal hexagrams + decade trajectory.

    Cross-module: Bát Tự → 2 Kinh Dịch hexagrams + lifetime decade walk.
    """
    from engine.ha_lac import cast_ha_lac

    result = cast_ha_lac(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
    )
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "ha_lac_state": result,
    }


@app.get("/api/chu-de-catalog")
def chu_de_catalog_list(truong_phai: str | None = None, keyword: str | None = None) -> dict[str, object]:
    """Chủ Đề Catalog — quản trị 30+ sách Đông phương theo CHỦ ĐỀ.

    Paradigm Anh duyệt (2026-06-02): VÒNG 3 cross-reference theo chủ đề.

    Query params:
    - truong_phai: filter by trường phái (bat-tu / tu-vi / ha-lac / mai-hoa / kmdg / cross / nen-tang / kinh-dich)
    - keyword: search trong tên, mô tả, related_concepts
    """
    from engine.yi_research.chu_de_catalog import (
        CATALOG, search_chu_de, list_chu_de_by_truong_phai, get_summary_stats,
    )
    if keyword:
        results = search_chu_de(keyword)
    elif truong_phai:
        results = list_chu_de_by_truong_phai(truong_phai)
    else:
        results = list(CATALOG)
    return {
        "stats": get_summary_stats(),
        "results": [c.to_dict() for c in results],
    }


@app.get("/api/chu-de-catalog/{chu_de_id}")
def chu_de_catalog_detail(chu_de_id: str) -> dict[str, object]:
    """Detail 1 chủ đề + markdown render."""
    from engine.yi_research.chu_de_catalog import get_chu_de, render_chu_de_markdown
    c = get_chu_de(chu_de_id)
    if not c:
        return {"error": f"Không có chủ đề id={chu_de_id}"}
    return {
        "chu_de": c.to_dict(),
        "markdown": render_chu_de_markdown(c),
    }


@app.post("/api/bat-tu/luan-giai-soi-nhieu-sach")
def bat_tu_luan_giai_soi_nhieu_sach(request: HaLacCastRequest) -> dict[str, object]:
    """Luận Giải Tứ Trụ SOI 4 SÁCH paradigm (Anh duyệt 2026-06-02).

    Pull tứ trụ → cross-reference 4 sách CỐT (TTT + Thiệu Vĩ Hoa + Tử Bình + Hoàng Tuấn)
    → render luận giải tường minh với citation rõ ràng từng nguồn.
    """
    from engine.bat_tu import extract_tu_tru
    from engine.bat_tu.luan_giai_soi_nhieu_sach import (
        luan_giai_tu_tru_soi_nhieu_sach,
        render_full_markdown,
    )

    tu_tru = extract_tu_tru(request.birth_datetime_local, request.timezone)
    luan = luan_giai_tu_tru_soi_nhieu_sach(tu_tru)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "tu_tru": tu_tru,
        "luan_giai_soi_nhieu_sach": luan,
        "markdown": render_full_markdown(luan),
    }


@app.get("/api/bat-tu/glossary")
def bat_tu_glossary_list() -> dict[str, object]:
    """List tất cả thuật ngữ Bát Tự trong glossary (paradigm 'Ấn Tỷ ánh sáng')."""
    from engine.bat_tu.concept_glossary import GLOSSARY
    return {
        "count": len(GLOSSARY),
        "concepts": [cd.to_dict() for cd in GLOSSARY.values()],
    }


@app.get("/api/bat-tu/glossary/{key}")
def bat_tu_glossary_lookup(key: str) -> dict[str, object]:
    """Lookup 1 thuật ngữ → full definition + trích sách + render markdown."""
    from engine.bat_tu.concept_glossary import glossary_explain, render_concept_markdown
    cd = glossary_explain(key, depth="full")
    if not cd:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy thuật ngữ '{key}'")
    return {
        "concept": cd,
        "markdown": render_concept_markdown(key),
    }


class DongYRequest(BaseModel):
    birth_datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    gender: str = "nam"
    chan_thuong: str = ""


class MonthlyHealthRequest(BaseModel):
    birth_datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    gender: str = "nam"
    year: int = 2026


@app.post("/api/dong-y/monthly-health")
def dong_y_monthly_health(request: MonthlyHealthRequest) -> dict[str, object]:
    """Lịch sức khỏe 12 tháng cá nhân — Bát Tự Lưu Nguyệt × Đông Y × chân dung sức khỏe."""
    from engine.bat_tu import extract_tu_tru
    from engine.dong_y.health_monthly_view import build_monthly_health_view, render_monthly_view_markdown
    base = extract_tu_tru(request.birth_datetime_local, request.timezone)
    tu_tru = {"pillars": base["pillars"]}
    view = build_monthly_health_view(tu_tru, current_year=request.year)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "tu_tru": base,
        "monthly_view": view,
        "markdown": render_monthly_view_markdown(view),
    }


class WeeklyPlanRequest(BaseModel):
    birth_datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    gender: str = "nam"
    start_date: str | None = None


@app.post("/api/dong-y/ha-lac-tat-ach")
def dong_y_ha_lac_tat_ach(request: MonthlyHealthRequest) -> dict[str, object]:
    """Hà Lạc Tật Ách — đọc tạng phủ qua 2 quẻ + hào nguyên đường."""
    from engine.ha_lac import cast_ha_lac
    from engine.ha_lac.tat_ach import analyze_ha_lac_tat_ach, render_ha_lac_tat_ach_markdown
    from engine.bat_tu import extract_tu_tru
    from engine.bat_tu.constants import STEM_ELEMENT as SE
    base = extract_tu_tru(request.birth_datetime_local, request.timezone)
    dm_el = SE.get(base["pillars"]["day"]["stem"], "")
    ha_lac = cast_ha_lac(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
    )
    result = analyze_ha_lac_tat_ach(ha_lac, day_master_element=dm_el)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "result": result.to_dict(),
        "markdown": render_ha_lac_tat_ach_markdown(result),
    }


@app.post("/api/dong-y/synthesis")
def dong_y_synthesis(request: MonthlyHealthRequest) -> dict[str, object]:
    """Health Synthesis — báo cáo tổng hợp 4 trường phái."""
    from engine.dong_y.health_synthesis import build_health_synthesis, render_synthesis_markdown
    result = build_health_synthesis(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
        current_year=request.year,
    )
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "result": result.to_dict(),
        "markdown": render_synthesis_markdown(result),
    }


@app.post("/api/dong-y/today-brief")
def dong_y_today_brief(request: WeeklyPlanRequest) -> dict[str, object]:
    """Brief sức khỏe HÔM NAY — chỉ 1 ngày từ weekly_planner.

    UI auto-load khi vào tab Sức khỏe → hiển thị card "Hôm nay" trên đầu.
    """
    from engine.dong_y.weekly_planner import build_weekly_plan
    from datetime import datetime, timezone, timedelta

    # Today VN
    vn_tz = timezone(timedelta(hours=7))
    today_str = request.start_date or datetime.now(vn_tz).strftime("%Y-%m-%d")

    weekly = build_weekly_plan(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
        start_date=today_str,
    )
    today_data = weekly.days[0] if weekly.days else None

    return {
        "algorithm_version": ALGORITHM_VERSION,
        "date": today_str,
        "day_master": weekly.day_master,
        "day_master_element": weekly.day_master_element,
        "today": today_data,
    }


@app.post("/api/dong-y/weekly-plan")
def dong_y_weekly_plan(request: WeeklyPlanRequest) -> dict[str, object]:
    """Lịch dưỡng sinh 7 ngày cá nhân hóa."""
    from engine.dong_y.weekly_planner import build_weekly_plan, render_weekly_markdown
    result = build_weekly_plan(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
        start_date=request.start_date,
    )
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "result": result.to_dict(),
        "markdown": render_weekly_markdown(result),
    }


@app.post("/api/dong-y/benh-tat-ttt")
def dong_y_benh_tat_ttt(request: MonthlyHealthRequest) -> dict[str, object]:
    """Bệnh tật theo Trích Thiên Tủy chương 25 (Nhâm Thiết Tiều).

    Kỳ thần nhập ngũ tạng = bệnh hung. Khách thần du lục kinh = bệnh nhẹ.
    Cross với Day Master + kỵ thần để cá nhân hóa.
    """
    from engine.bat_tu import extract_tu_tru
    from engine.bat_tu.phu_uc_route import route_phu_uc
    from engine.bat_tu.constants import STEM_ELEMENT as SE
    from engine.dong_y.benh_tat_ttt import analyze_benh_tat_ttt, render_benh_tat_ttt_markdown

    base = extract_tu_tru(request.birth_datetime_local, request.timezone)
    tu_tru = {"pillars": base["pillars"]}
    dm_stem = base["pillars"]["day"]["stem"]
    dm_el = SE.get(dm_stem, "")

    # Get kỵ thần từ Phù-Ức
    phu_uc = route_phu_uc(tu_tru)
    ky_than_els = phu_uc.ky_than_elements or []

    result = analyze_benh_tat_ttt(dm_el, ky_than_els)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "day_master_element": dm_el,
        "ky_than_elements": ky_than_els,
        "result": result.to_dict(),
        "markdown": render_benh_tat_ttt_markdown(result),
    }


@app.post("/api/dong-y/ngu-van-luc-khi")
def dong_y_ngu_van_luc_khi(request: MonthlyHealthRequest) -> dict[str, object]:
    """Ngũ Vận Lục Khí — vận khí năm + Lục Dâm cảnh báo (Lê Văn Sửu).

    Paradigm Hoàng Đế Nội Kinh — tính trung vận + khí trời năm,
    cross với Day Master để cảnh báo 6 tà khí ngoài.
    """
    from engine.bat_tu import extract_tu_tru
    from engine.bat_tu.luu_nien import compute_luu_nien_pillar_by_year
    from engine.dong_y.ngu_van_luc_khi import compute_ngu_van_luc_khi, render_ngu_van_luc_khi_markdown
    from engine.bat_tu.constants import STEM_ELEMENT as SE

    base = extract_tu_tru(request.birth_datetime_local, request.timezone)
    dm_stem = base["pillars"]["day"]["stem"]
    dm_el = SE.get(dm_stem, "")

    year_pillar = compute_luu_nien_pillar_by_year(request.year)
    result = compute_ngu_van_luc_khi(
        can_nam=year_pillar["stem"],
        chi_nam=year_pillar["branch"],
        year=request.year,
        day_master_element=dm_el,
    )
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "year_pillar": year_pillar,
        "day_master_element": dm_el,
        "result": result.to_dict(),
        "markdown": render_ngu_van_luc_khi_markdown(result),
    }


@app.get("/api/dong-y/paradigm")
def dong_y_paradigm_overview() -> dict[str, object]:
    """Paradigm overview Liệu pháp Tượng Số — 5 phương pháp + quy tắc số 0 + 6 lưu ý."""
    from engine.dong_y.lieu_phap_tuong_so import get_paradigm_overview
    return get_paradigm_overview()


@app.post("/api/dong-y/full")
def dong_y_full_analysis(request: DongYRequest) -> dict[str, object]:
    """Đông Y full — Tạng phủ + Kinh lạc + Âm dương + Liệu pháp tượng số.

    Anh duyệt 2026-06-02: trang sức khỏe + đọc 'Chữa bệnh theo Chu Dịch'.
    4 module mới: tang_phu_chan_doan + kinh_lac + am_duong + lieu_phap_tuong_so.
    🪷 Iron Rule #4+6: KHÔNG predict, chỉ đọc cấu trúc thân thể.
    """
    from engine.bat_tu import extract_tu_tru
    from engine.dong_y.tang_phu_chan_doan import chan_doan_tang_phu, render_tang_phu_markdown
    from engine.dong_y.kinh_lac_overview import tra_kinh_lac, render_kinh_lac_markdown
    from engine.dong_y.am_duong_can_bang import evaluate_am_duong_can_bang, render_am_duong_markdown
    from engine.dong_y.lieu_phap_tuong_so import tim_tuong_so, render_tuong_so_markdown

    base = extract_tu_tru(request.birth_datetime_local, request.timezone)
    tu_tru = {"pillars": base["pillars"]}

    # 1. Tạng phủ chẩn đoán
    tang_phu = chan_doan_tang_phu(request.chan_thuong)

    # 2. Kinh lạc (lookup theo primary tạng)
    kinh_lac = tra_kinh_lac(tang_phu.primary_tang) if tang_phu.primary_tang else None

    # 3. Âm dương cân bằng
    am_duong = evaluate_am_duong_can_bang(tu_tru, chan_thuong=request.chan_thuong)

    # 4. Liệu pháp tượng số
    tuong_so = tim_tuong_so(request.chan_thuong)

    return {
        "algorithm_version": ALGORITHM_VERSION,
        "tu_tru": base,
        "tang_phu_chan_doan": {
            "result": tang_phu.to_dict(),
            "markdown": render_tang_phu_markdown(tang_phu),
        },
        "kinh_lac": {
            "result": kinh_lac.to_dict() if kinh_lac else None,
            "markdown": render_kinh_lac_markdown(kinh_lac) if kinh_lac else "_(Không tra được kinh)_",
        },
        "am_duong": {
            "result": am_duong.to_dict(),
            "markdown": render_am_duong_markdown(am_duong),
        },
        "lieu_phap_tuong_so": {
            "result": tuong_so.to_dict(),
            "markdown": render_tuong_so_markdown(tuong_so),
        },
        "iron_rule_note": (
            "🪷 Iron Rule #4+6: 4 module đọc cấu trúc thân thể theo paradigm "
            "Bát Quái + Hoàng Đế Nội Kinh + 'Chữa bệnh theo Chu Dịch'. "
            "KHÔNG predict, KHÔNG thay y học hiện đại. Đức năng thắng số."
        ),
        "sources": [
            "Chữa bệnh theo Chu Dịch (Lý Ngọc Sơn + Lý Kiện Dân)",
            "Hoàng Đế Nội Kinh (paradigm chung)",
            "Engine YI-Chronos Bát Tự",
        ],
    }


class SucKhoeSauRequest(BaseModel):
    birth_datetime_local: str
    timezone: str = "Asia/Ho_Chi_Minh"
    gender: str = "nam"
    chan_thuong: str = ""
    current_age: int | None = None


@app.post("/api/bat-tu/suc-khoe-sau")
def bat_tu_suc_khoe_sau(request: SucKhoeSauRequest) -> dict[str, object]:
    """Sức Khỏe SÂU — tích hợp Bát Tự + Đông y + chấn thương cụ thể.

    Anh duyệt 2026-06-02: trang sức khỏe riêng. Engine tích hợp Phù-Ức +
    Nguyên Lưu + chấn thương input → lời khuyên thực tiễn (dinh dưỡng, vận động).
    🪷 KHÔNG predict — chỉ đọc cấu trúc thân thể.
    """
    from engine.bat_tu import extract_tu_tru
    from engine.bat_tu.suc_khoe_sau import analyze_suc_khoe_sau, render_suc_khoe_sau_markdown
    base = extract_tu_tru(request.birth_datetime_local, request.timezone)
    tu_tru = {"pillars": base["pillars"]}
    result = analyze_suc_khoe_sau(
        tu_tru,
        chan_thuong=request.chan_thuong,
        current_age=request.current_age,
    )
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "tu_tru": base,
        "suc_khoe_sau": result.to_dict(),
        "markdown": render_suc_khoe_sau_markdown(result),
    }


@app.post("/api/bat-tu/nguyen-luu-trace")
def bat_tu_nguyen_luu_trace(request: HaLacCastRequest) -> dict[str, object]:
    """Trace Nguyên Lưu (TTT chương 19) — dòng chảy ngũ hành trong 4 trụ."""
    from engine.bat_tu import extract_tu_tru
    from engine.bat_tu.nguyen_luu_trace import trace_nguyen_luu, render_nguyen_luu_markdown
    base = extract_tu_tru(request.birth_datetime_local, request.timezone)
    tu_tru = {"pillars": base["pillars"]}
    result = trace_nguyen_luu(tu_tru)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "tu_tru": base,
        "nguyen_luu": result.to_dict(),
        "markdown": render_nguyen_luu_markdown(result),
    }


@app.post("/api/bat-tu/benh-thuoc")
def bat_tu_benh_thuoc(request: HaLacCastRequest) -> dict[str, object]:
    """Detect Bệnh-Thuốc (TTT chương 18) — phát hiện bệnh + tìm thần thuốc."""
    from engine.bat_tu import extract_tu_tru
    from engine.bat_tu.benh_thuoc_detector import detect_benh_thuoc, render_benh_thuoc_markdown
    base = extract_tu_tru(request.birth_datetime_local, request.timezone)
    tu_tru = {"pillars": base["pillars"]}
    result = detect_benh_thuoc(tu_tru)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "tu_tru": base,
        "benh_thuoc": result.to_dict(),
        "markdown": render_benh_thuoc_markdown(result),
    }


@app.post("/api/bat-tu/tong-cach-route")
def bat_tu_tong_cach_route(request: HaLacCastRequest) -> dict[str, object]:
    """Route Tòng Cách — 4 path khi Day Master cực đoan (TTT chương 17 bậc 2).

    Anh duyệt 2026-06-02 sau thâm nhuần TTT chương 17. Engine check trước
    Phù-Ức bình thường: nếu match Tòng Cách → đảo paradigm.

    4 path: Tòng Tài / Tòng Sát / Tòng Vượng / Tòng Cường.
    Nếu không match → trả is_tong=False với lý do.
    """
    from engine.bat_tu import extract_tu_tru
    from engine.bat_tu.tong_cach_route import route_tong_cach, render_tong_markdown

    base = extract_tu_tru(request.birth_datetime_local, request.timezone)
    tu_tru = {"pillars": base["pillars"]}
    result = route_tong_cach(tu_tru)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "tu_tru": base,
        "tong_cach": result.to_dict(),
        "markdown": render_tong_markdown(result),
    }


@app.post("/api/bat-tu/phu-uc-route")
def bat_tu_phu_uc_route(request: HaLacCastRequest) -> dict[str, object]:
    """Route Phù-Ức (Trợ vs Sinh) — 8 path theo Trích Thiên Tủy.

    Anh duyệt 2026-06-02: paradigm 'Ấn Tỷ ánh sáng' — engine generalize
    cho mọi lá số. Trả về Dụng-Kỵ thần + trích sách + hành động cụ thể.
    """
    from engine.bat_tu import extract_tu_tru
    from engine.bat_tu.phu_uc_route import route_phu_uc, render_phu_uc_markdown

    base = extract_tu_tru(request.birth_datetime_local, request.timezone)
    tu_tru = {"pillars": base["pillars"]}
    result = route_phu_uc(tu_tru)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "tu_tru": base,
        "phu_uc": result.to_dict(),
        "markdown": render_phu_uc_markdown(result),
    }


@app.post("/api/ha-lac/luan-giai-sau")
def ha_lac_luan_giai_sau(request: HaLacCastRequest) -> dict[str, object]:
    """Luận giải SÂU Hà Lạc — render paradigm thành narrative tường minh.

    Paradigm Anh (2026-06-02): 'Engine ra được cách cục, chứ chưa luận giải sâu được.'
    → Module này = bước cuối: cast() → engine output → narrative tường minh.

    3 lớp luận giải cho cả Tiên Thiên + Hậu Thiên:
    1. LỚP NỀN: bản chất + nên thế nào + tượng + key paradigm + case study
    2. LỚP HÀO NĐ: case study cho hào nguyên đường (hoặc generic guidance)
    3. LỚP IRON RULE CROSS-LINK: paradigm cổ ↔ Iron Rule project
    + Tổng synthesis THỂ-DỤNG (đặc biệt cho founder paradigm).
    """
    from engine.ha_lac import cast_ha_lac
    from engine.ha_lac.luan_giai_sau import render_full_luan_giai

    cast_result = cast_ha_lac(
        birth_datetime_local=request.birth_datetime_local,
        timezone=request.timezone,
        gender=request.gender,
    )
    luan = render_full_luan_giai(cast_result)
    return {
        "algorithm_version": ALGORITHM_VERSION,
        "ha_lac_state": cast_result,
        "luan_giai_sau": luan,
    }


@app.post("/api/ky-mon/cast")
def ky_mon_cast(request: KyMonCastRequest) -> dict[str, object]:
    """Cast a Kỳ Môn Độn Giáp chart (奇門遁甲).

    Trường phái thứ 6 của YI-Chronos. Tổ sư: Lưu Bá Ôn (1311-1375).
    Paradigm: ĐỌC ĐỒNG DẠNG, không predict (Iron Rule #4 + #6).

    Returns 9 cung × 8 môn × 9 tinh × 8 thần — bản đồ năng lượng thời-không.
    Nếu có `task`, thêm field `task_analysis` (3 hướng tốt + 2 hướng tránh
    + cách cục liên quan task) — per Đàm Liên Chương I phần V.
    """
    from engine.ky_mon import cast as cast_ky_mon, analyze_for_task

    result = cast_ky_mon(
        year=request.year,
        month=request.month,
        day=request.day,
        hour=request.hour,
        minute=request.minute,
        method=request.method,
    )

    if request.task:
        result["task_analysis"] = analyze_for_task(result, request.task)

    return {
        "algorithm_version": ALGORITHM_VERSION,
        "ky_mon_state": result,
    }


@app.get("/api/ky-mon/wiki")
def ky_mon_wiki() -> dict[str, object]:
    """Return full KMDG wiki — categories: cung, mon, tinh, than, structure, to_su."""
    from engine.ky_mon import WIKI

    return {"status": "ok", "wiki": WIKI}


@app.get("/api/ky-mon/tasks")
def ky_mon_tasks() -> dict[str, object]:
    """Return 15 task list cho UI dropdown (per Đàm Liên cổ điển)."""
    from engine.ky_mon import list_tasks

    return {"status": "ok", "tasks": list_tasks()}


@app.post("/api/ky-mon/personal-reading")
def ky_mon_personal_reading(request: KyMonCastRequest) -> dict[str, object]:
    """Đọc lá số sinh cá nhân theo Đàm Liên — luận paradigm tác động user.

    Cast bàn KMDG tại khoảnh khắc sinh + run interpret_personal_chart →
    return list of insights specific to user's birth chart.

    Paradigm: KMDG cross-paradigm reading — đọc cấu trúc thời-không tại
    khoảnh khắc ra đời (theo Iron Rule #4 'đọc đồng dạng'), không predict.
    """
    from engine.ky_mon import cast as cast_ky_mon, interpret_personal_chart

    state = cast_ky_mon(
        year=request.year, month=request.month, day=request.day,
        hour=request.hour, minute=request.minute, method=request.method,
    )
    insights = interpret_personal_chart(state)

    return {
        "algorithm_version": ALGORITHM_VERSION,
        "ky_mon_state": state,
        "personal_insights": insights,
    }


@app.get("/api/ky-mon/founder-birth-data")
def ky_mon_founder_birth(request: Request) -> dict[str, object]:
    """Founder default birth data — owner-only (contains personal birth datetime)."""
    from api.auth import require_owner
    from engine.ky_mon import list_founder_data

    require_owner(request)
    return {"status": "ok", "data": list_founder_data()}


@app.get("/api/ky-mon/combo-patterns")
def ky_mon_combo_patterns() -> dict[str, object]:
    """Return danh sách 14+ combo Môn × Tinh × Thần patterns (từ deep_readings)."""
    from engine.ky_mon import list_combo_patterns

    return {"status": "ok", "patterns": list_combo_patterns()}


class KyMonCellDeepRequest(BaseModel):
    """Luận sâu 1 cell trong bàn KMDG."""
    cung_vn: str
    mon_vn: str | None = None
    tinh_vn: str | None = None
    than_vn: str | None = None
    thien_can: str | None = None
    dia_can: str | None = None


@app.post("/api/ky-mon/cell-deep")
def ky_mon_cell_deep(request: KyMonCellDeepRequest) -> dict[str, object]:
    """Luận sâu 1 cell (cung + môn + tinh + thần) — micro-readings từ Đàm Liên.

    Trả về: mon_deep + tinh_deep + than_deep + triple_combo (nếu có) + overall.
    """
    from engine.ky_mon import interpret_cell_deep

    result = interpret_cell_deep(
        cung_vn=request.cung_vn,
        mon_vn=request.mon_vn,
        tinh_vn=request.tinh_vn,
        than_vn=request.than_vn,
        thien_can=request.thien_can,
        dia_can=request.dia_can,
    )
    return {"status": "ok", "cell_deep": result}


@app.get("/api/ky-mon/element-deep/{kind}/{name}")
def ky_mon_element_deep(kind: str, name: str) -> dict[str, object]:
    """Luận sâu 1 element (mon/tinh/than) — for UI quick lookup.

    kind: 'mon' | 'tinh' | 'than'
    name: VN name (Khai, Thiên Phụ, Trị Phù, ...)
    """
    from engine.ky_mon import MON_DEEP, TINH_DEEP, THAN_DEEP

    pool = {"mon": MON_DEEP, "tinh": TINH_DEEP, "than": THAN_DEEP}.get(kind)
    if pool is None:
        return {"status": "not_found", "reason": f"unknown kind: {kind}"}
    data = pool.get(name)
    if data is None:
        return {"status": "not_found", "reason": f"{kind} '{name}' không có trong deep_readings"}
    return {"status": "ok", "kind": kind, "name": name, "deep": data}


@app.get("/api/tu-vi/chinh-tinh")
def tu_vi_chinh_tinh_list() -> dict[str, object]:
    """Return all 14 chính tinh metadata + interpretation templates."""
    from engine.tu_vi import list_chinh_tinh

    return {
        "status": "ok",
        "stars": [s.to_dict() for s in list_chinh_tinh()],
    }


@app.get("/api/tu-vi/chinh-tinh/{star_id}")
def tu_vi_chinh_tinh_detail(star_id: str) -> dict[str, object]:
    """Return one chính tinh by id slug."""
    from engine.tu_vi import get_chinh_tinh

    try:
        s = get_chinh_tinh(star_id)
    except ValueError:
        return {"status": "not_found", "id": star_id}
    return {"status": "ok", "star": s.to_dict()}


@app.get("/api/tu-vi/do-hinh-co")
def tu_vi_do_hinh_co() -> dict[str, object]:
    """4 đồ hình âm dương cổ (Thái cực · Tiên thiên · Hậu thiên · Hà Đồ) cho
    đồ hình tương tác. Bồi từ vòng đọc sâu Lê Văn Sửu p21-40 (2026-06-13)."""
    from engine.tu_vi.do_hinh_co import do_hinh_payload
    return {"status": "ok", **do_hinh_payload()}


@app.get("/api/tu-vi/star-profiles")
def tu_vi_star_profiles() -> dict[str, object]:
    """Hồ sơ sâu 14 chính tinh (+ Vô Chính Diệu) + kiến thức nền Âm Dương Ngũ Hành.

    Gộp 3 tầng: (1) metadata cổ truyền Q2 (hành, âm dương, hóa khí, chủ về,
    tích cực/tiêu cực); (2) profile Ngũ Uẩn 5 lớp trường phái Tử Vi Bôn Ba;
    (3) bảng miếu-vượng-đắc-hãm tại 12 chi ("độ khó bài học" theo từng đất cung).
    """
    import json as _json
    import unicodedata as _ud
    from pathlib import Path as _Path

    from engine.tu_vi import list_chinh_tinh
    from engine.tu_vi import ngu_uan as ngu_uan_mod
    from engine.tu_vi.mieu_vuong_ham import level_at
    from engine.tu_vi.ngu_hanh_nen import HANH_CHI, vong_sinh_khac

    def _slug(s: str) -> str:
        nfkd = _ud.normalize("NFD", s)
        s2 = "".join(c for c in nfkd if not _ud.combining(c))
        return s2.lower().strip().replace(" ", "_").replace("đ", "d")

    deep_dir = _Path(__file__).resolve().parents[1] / "data/yi_wiki/tu_vi_star_deep"

    def _deep_profile(star_vi: str) -> dict | None:
        """Chuyên khảo luận giải sâu đa phái (build từ atoms 6 nguồn) nếu đã có."""
        p = deep_dir / f"{_slug(star_vi)}.json"
        if not p.exists():
            return None
        try:
            return _json.loads(p.read_text(encoding="utf-8"))
        except (OSError, _json.JSONDecodeError):
            return None

    chi_12 = list(HANH_CHI.keys())
    profiles = []
    for s in list_chinh_tinh():
        tvbb = ngu_uan_mod.get_star_profile(s.ten_vi)
        profiles.append({
            "co_ban": s.to_dict(),
            "ngu_uan": tvbb,  # None nếu dataset chưa có sao này
            "sao_o_dau_thi": ngu_uan_mod.sao_o_dau_thi(s.ten_vi),
            "mieu_ham_12_chi": {chi: level_at(s.ten_vi, chi) for chi in chi_12},
            "luan_giai_sau": _deep_profile(s.ten_vi),  # None nếu chưa build
        })
    # Vô Chính Diệu — "tính cách thứ 15" (chỉ có trong dataset hiện đại)
    vcd = ngu_uan_mod.get_star_profile("Vô Chính Diệu")
    if vcd:
        profiles.append({
            "co_ban": {"ten_vi": "Vô Chính Diệu", "ten_zh": "無正曜",
                       "ngu_hanh": None, "am_duong": None, "hoa_khi": None,
                       "keywords": vcd.get("tom_gon") or [],
                       "tich_cuc": None, "tieu_cuc": None, "chu_ve": []},
            "ngu_uan": vcd,
            "sao_o_dau_thi": ngu_uan_mod.sao_o_dau_thi("Vô Chính Diệu"),
            "mieu_ham_12_chi": {},
        })
    return {
        "status": "ok",
        "nen_tang": vong_sinh_khac(),
        "profiles": profiles,
        "paradigm_note": (
            "Sao không tốt không xấu — mỗi sao là một dạng lực sống; "
            "miếu hay hãm là độ khó của bài học tại từng đất cung, không phải lời khen chê."
        ),
    }


_HOUR_BRANCH_BY_HOUR = (
    "Tý", "Sửu", "Sửu", "Dần", "Dần", "Mão", "Mão",
    "Thìn", "Thìn", "Tỵ", "Tỵ", "Ngọ", "Ngọ",
    "Mùi", "Mùi", "Thân", "Thân", "Dậu", "Dậu",
    "Tuất", "Tuất", "Hợi", "Hợi", "Tý",
)


def _hour_branch_from_hour(hour: int) -> str:
    """Map 0..23 to địa chi hour."""
    return _HOUR_BRANCH_BY_HOUR[hour]


@app.post("/api/tu-vi/cast")
def tu_vi_cast(request: TuViCastRequest) -> dict[str, object]:
    """Cast a full Tử Vi lá số.

    Two input modes:
    - Direct (lunar_month + lunar_day + hour_branch + year_stem + year_branch + gender)
    - Convenient (birth_datetime_local — auto-converts via core.chronos)
    """
    from engine.tu_vi import cast_la_so

    # Resolve inputs.
    if request.birth_datetime_local:
        from core.chronos import calculate_chronos_state
        from engine.yi_wiki.lich_conversion import SolarDateTime, solar_to_lunar

        chronos = calculate_chronos_state(request.birth_datetime_local, request.timezone)
        from datetime import datetime as _dt
        local_dt = _dt.fromisoformat(request.birth_datetime_local)
        # lich_conversion handles 早子時: hour≥23 → lunar day of next day (#13 fix)
        solar = SolarDateTime(
            year=local_dt.year, month=local_dt.month, day=local_dt.day,
            hour=local_dt.hour, minute=local_dt.minute,
        )
        lunar = solar_to_lunar(solar)
        lunar_month = lunar.lunar_month
        lunar_day = lunar.lunar_day
        # Hour branch from local datetime hour.
        hour_branch = _hour_branch_from_hour(local_dt.hour)
        # Year stem/branch from chronos.ganzhi.
        year_parts = chronos.ganzhi.year.split()
        year_stem = year_parts[0]
        year_branch = year_parts[1]
    else:
        # Direct mode — require all fields.
        missing = [k for k, v in {
            "lunar_month": request.lunar_month,
            "lunar_day": request.lunar_day,
            "hour_branch": request.hour_branch,
            "year_stem": request.year_stem,
            "year_branch": request.year_branch,
        }.items() if v is None]
        if missing:
            return {"status": "error", "missing_fields": missing}
        lunar_month = request.lunar_month
        lunar_day = request.lunar_day
        hour_branch = request.hour_branch
        year_stem = request.year_stem
        year_branch = request.year_branch

    result = cast_la_so(
        lunar_month=lunar_month,
        lunar_day=lunar_day,
        hour_branch=hour_branch,
        year_stem=year_stem,
        year_branch=year_branch,
        gender=request.gender,
    )

    # Optional layers.
    response: dict[str, object] = {
        "algorithm_version": ALGORITHM_VERSION,
        "input_resolved": {
            "lunar_month": lunar_month,
            "lunar_day": lunar_day,
            "hour_branch": hour_branch,
            "year_stem": year_stem,
            "year_branch": year_branch,
            "gender": request.gender,
        },
        "la_so": result,
    }

    if request.include_interpretation:
        from engine.tu_vi import interpret_la_so

        response["interpretation"] = interpret_la_so(result)

    # Lưu trú sao for target_year if provided.
    if request.target_year is not None and request.birth_datetime_local:
        from datetime import datetime as _dt
        from engine.tu_vi import luu_tru_for_year

        local_dt = _dt.fromisoformat(request.birth_datetime_local)
        birth_year = local_dt.year
        response["luu_tru_year"] = luu_tru_for_year(
            la_so=result,
            target_year=request.target_year,
            birth_year=birth_year,
        )

    return response



# ─── AI Hội Đồng (Sages Council) endpoints ──────────────────────────────────


@app.get("/api/ai/providers")
def ai_list_providers(http_request: Request) -> dict:
    """List all LLM providers + their status (configured? unhealthy?). Owner-only."""
    from api.auth import require_owner
    require_owner(http_request)
    from engine.ai.registry import get_registry

    reg = get_registry()
    providers = reg.list_providers()
    for p in providers:
        p["is_unhealthy"] = reg.is_unhealthy(p["name"])
    return {"status": "ok", "providers": providers}


@app.post("/api/ai/providers/{name}/key")
def ai_set_provider_key(name: str, req: AiProviderKeyRequest, http_request: Request) -> dict:
    """Update API key for a provider at runtime. Owner-only."""
    from api.auth import require_owner
    require_owner(http_request)
    from engine.ai.registry import get_registry

    reg = get_registry()
    try:
        status = reg.set_api_key(name, req.api_key)
        reg.reset_health()  # clear unhealthy marks since key changed
        return {"status": "ok", "provider": status}
    except KeyError:
        return {"status": "not_found", "name": name}


@app.post("/api/ai/providers/reset-health")
def ai_reset_provider_health(http_request: Request) -> dict:
    """Clear all unhealthy marks — useful after recharging account. Owner-only."""
    from api.auth import require_owner
    require_owner(http_request)
    from engine.ai.registry import get_registry

    get_registry().reset_health()
    return {"status": "ok"}


@app.post("/api/ai/providers/{name}/notes")
def ai_set_provider_notes(name: str, req: AiProviderNotesRequest, http_request: Request) -> dict:
    """Update notes + plan_type cho provider. Owner-only.

    plan_type:
      - 'coding_plan'        — Claude Code subscription, Cursor Pro, etc.
      - 'api_pay_per_token'  — DeepSeek/OpenAI pay-per-use
      - 'free_tier'          — free credit, has quota limit
      - 'local'              — Ollama, self-hosted
    """
    from api.auth import require_owner
    require_owner(http_request)
    from engine.ai.registry import get_registry
    try:
        notes = get_registry().set_notes(
            name, plan_type=req.plan_type, notes=req.notes
        )
        return {"status": "ok", "provider": name, "notes": notes}
    except KeyError:
        return {"status": "not_found", "name": name}


@app.post("/api/ai/providers/{name}/test")
def ai_test_provider(name: str, req: AiProviderTestRequest, http_request: Request) -> dict:
    """Test 1 call ngắn tới provider. Đo latency + verify key/config OK. Owner-only."""
    from api.auth import require_owner
    require_owner(http_request)
    from engine.ai.registry import get_registry
    import time as _time
    reg = get_registry()
    try:
        p = reg.get(name)
    except KeyError:
        return {"status": "not_found", "name": name}
    if not p.is_configured:
        return {
            "status": "not_configured",
            "provider": name,
            "message": "Provider chưa được cấu hình (thiếu API key hoặc server chưa chạy)",
        }
    model = req.model or p.default_model
    t0 = _time.time()
    # Reasoning models (M2, R1, etc.) need budget for <think> block before answering.
    is_reasoning = any(s in model.lower() for s in ("m2", "reasoner", "thinking", "o1"))
    max_tok = 500 if is_reasoning else 80
    try:
        resp = p.chat(
            messages=[{"role": "user", "content": req.prompt}],
            model=model, temperature=0.1, max_tokens=max_tok,
        )
        dt = _time.time() - t0
        return {
            "status": "ok",
            "provider": name,
            "model": model,
            "latency_seconds": round(dt, 2),
            "response_preview": resp.content[:200],
            "tokens": {
                "prompt": resp.prompt_tokens,
                "completion": resp.completion_tokens,
                "total": resp.total_tokens,
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "provider": name,
            "model": model,
            "error": f"{type(e).__name__}: {str(e)[:300]}",
        }


@app.get("/api/ai/agents")
def ai_list_agents(http_request: Request) -> dict:
    """List agents with metadata. Owner-only."""
    from api.auth import require_owner
    require_owner(http_request)
    from engine.ai.prompt_store import AGENT_IDS, AGENT_METADATA, is_overridden

    agents = []
    for aid in AGENT_IDS:
        meta = AGENT_METADATA[aid]
        agents.append({
            "id": aid,
            "name_vi": meta["name_vi"],
            "icon": meta["icon"],
            "specialty": meta["specialty"],
            "best_for": meta["best_for"],
            "prompt_overridden": is_overridden(aid),
        })
    return {"status": "ok", "agents": agents}


@app.get("/api/ai/prompts/{agent_id}")
def ai_get_prompt(agent_id: str, http_request: Request) -> dict:
    """Get current prompt (override if exists, else default) + default for reset. Owner-only."""
    from api.auth import require_owner
    require_owner(http_request)
    from engine.ai.prompt_store import ALL_PROMPT_IDS, get_default, get_prompt, is_overridden

    if agent_id not in ALL_PROMPT_IDS:
        return {"status": "not_found", "agent_id": agent_id}
    return {
        "status": "ok",
        "agent_id": agent_id,
        "current": get_prompt(agent_id),
        "default": get_default(agent_id),
        "is_overridden": is_overridden(agent_id),
    }


@app.put("/api/ai/prompts/{agent_id}")
def ai_set_prompt(agent_id: str, req: AiPromptUpdateRequest, http_request: Request) -> dict:
    """Save user override for a prompt. Owner-only."""
    from api.auth import require_owner
    require_owner(http_request)
    from engine.ai.prompt_store import ALL_PROMPT_IDS, set_prompt

    if agent_id not in ALL_PROMPT_IDS:
        return {"status": "not_found", "agent_id": agent_id}
    set_prompt(agent_id, req.content)
    return {"status": "ok", "agent_id": agent_id}


@app.delete("/api/ai/prompts/{agent_id}")
def ai_reset_prompt(agent_id: str, http_request: Request) -> dict:
    """Reset prompt to default (delete user override). Owner-only."""
    from api.auth import require_owner
    require_owner(http_request)
    from engine.ai.prompt_store import ALL_PROMPT_IDS, reset_prompt

    if agent_id not in ALL_PROMPT_IDS:
        return {"status": "not_found", "agent_id": agent_id}
    reset_prompt(agent_id)
    return {"status": "ok", "agent_id": agent_id}


@app.post("/api/ai/council/consult")
def ai_council_consult(req: AiCouncilRequest, http_request: Request) -> dict:
    """Run a full council consultation (3-round Socratic debate). Login required."""
    from api.auth import require_user
    require_user(http_request)
    from engine.ai.council import consult_council

    result = consult_council(
        question=req.question,
        chart_data=req.chart_data,
        chart_summary=req.chart_summary,
        explicit_agents=req.explicit_agents,
        parallel=req.parallel,
        skip_challenge=req.skip_challenge,
        persist=req.persist,
    )
    return {"status": "ok", "session": result}


@app.get("/api/ai/council/sessions")
def ai_council_recent_sessions(limit: int = 20) -> dict:
    from engine.ai.council import list_recent_sessions

    return {"status": "ok", "sessions": list_recent_sessions(limit=limit)}


@app.get("/api/ai/council/sessions/{session_id}")
def ai_council_session(session_id: int) -> dict:
    from engine.ai.council import get_session

    s = get_session(session_id)
    if s is None:
        return {"status": "not_found", "id": session_id}
    return {"status": "ok", "session": s}


# ─── Kanban-based Council (durable, async) ──────────────────────────────────


@app.post("/api/ai/council/kanban/consult")
def ai_kanban_council_consult(req: AiKanbanCouncilRequest, http_request: Request) -> dict:
    """Spawn a P3-quorum kanban council consultation. Login required.

    Server auto-precasts engine outputs for selected sages (if `birth` or
    `event` supplied) so sages don't waste tokens recomputing. Caller can
    also pass `precast_data` directly to skip auto-cast.

    Returns immediately with root_id; client polls /kanban/sessions/{root_id}.
    """
    from api.auth import require_user
    require_user(http_request)
    from engine.ai.kanban_council import consult, save_session, select_sages
    from engine.ai.precast import precast_for_sages

    sages = req.sages or select_sages(req.question)

    # Build precast: explicit precast_data takes precedence, then auto from birth/event
    precast: dict[str, dict] = {}
    if req.birth or req.event:
        precast.update(
            precast_for_sages(sages, birth=req.birth, event=req.event)
        )
    if req.precast_data:
        precast.update(req.precast_data)  # explicit wins

    session = consult(
        question=req.question,
        sages=sages,
        precast_data=precast,
        chart_context=req.chart_context,
        soul_key=req.soul_key,
    )
    save_session(session)
    return {
        "status": "ok",
        "session": session.to_dict(),
        "precast_sages": list(precast.keys()),
    }


@app.get("/api/ai/council/kanban/sessions/{root_id}")
def ai_kanban_council_session(root_id: str) -> dict:
    """Live snapshot of a kanban council session."""
    from engine.ai.kanban_council import load_session, session_snapshot

    session = load_session(root_id)
    if session is None:
        return {"status": "not_found", "root_id": root_id}
    return {"status": "ok", "snapshot": session_snapshot(session)}


@app.get("/api/ai/council/kanban/sessions")
def ai_kanban_council_recent(limit: int = 20) -> dict:
    from engine.ai.kanban_council import list_recent_sessions

    return {"status": "ok", "sessions": list_recent_sessions(limit=limit)}


@app.get("/api/ai/council/kanban/sessions/{root_id}/synthesis")
def ai_kanban_council_synthesis(root_id: str) -> dict:
    """Arbiter's final report if complete; otherwise null."""
    from engine.ai.kanban_council import get_synthesis, load_session

    session = load_session(root_id)
    if session is None:
        return {"status": "not_found", "root_id": root_id}
    synthesis = get_synthesis(session)
    return {
        "status": "ok" if synthesis else "pending",
        "root_id": root_id,
        "synthesis": synthesis,
    }


# ─── Critique queue (sage-suggested engine improvements) ─────────────────────


@app.get("/api/ai/council/critiques")
def ai_council_critiques_list(
    status: str | None = "open",
    priority: str | None = None,
    target_prefix: str | None = None,
    limit: int = 100,
) -> dict:
    """Browse sage-suggested engine improvements.

    Filters:
      - status: open | resolved | dismissed (default: open)
      - priority: low | medium | high
      - target_prefix: e.g. "engine.bat_tu"
    """
    from engine.ai.critique_store import list_critiques

    return {
        "status": "ok",
        "critiques": list_critiques(
            status=status, priority=priority,
            target_prefix=target_prefix, limit=limit,
        ),
    }


@app.get("/api/ai/council/critiques/stats")
def ai_council_critiques_stats() -> dict:
    """Critique queue dashboard summary."""
    from engine.ai.critique_store import stats

    return {"status": "ok", "stats": stats()}


@app.post("/api/ai/council/critiques/{critique_id}/resolve")
def ai_council_critique_resolve(
    critique_id: int, req: AiCritiqueResolveRequest, http_request: Request,
) -> dict:
    """Mark a critique as resolved (anh fixed it) or dismissed (won't fix). Owner-only."""
    from api.auth import require_owner
    require_owner(http_request)
    from engine.ai.critique_store import dismiss_critique, resolve_critique

    if req.action == "dismiss":
        ok = dismiss_critique(critique_id, reason=req.resolution)
    else:
        ok = resolve_critique(critique_id, resolution=req.resolution)
    return {"status": "ok" if ok else "not_found", "id": critique_id}


# ─── YI-Hermes endpoints (separate namespace from user's Mac Hermes) ────────


@app.post("/api/yi-hermes/chat")
def yi_hermes_chat(req: YiHermesChatRequest, http_request: Request) -> dict:
    """Send a message to YI-Hermes — multi-turn chat. Login required."""
    from api.auth import require_user
    require_user(http_request)
    from engine.yi_hermes import HermesChat, HermesContext
    from engine.yi_hermes.chat import HermesTurn

    ctx_dict = req.context.model_dump() if req.context else {}
    ctx = HermesContext(**ctx_dict)
    history = [
        HermesTurn(
            role=h.get("role", "user"),
            content=h.get("content", ""),
            intent=h.get("intent", ""),
            tokens_used=h.get("tokens_used", 0),
        )
        for h in req.history
    ]

    chat = HermesChat()
    result = chat.send(
        user_message=req.user_message,
        context=ctx,
        history=history,
    )
    return {"status": "ok", "response": result}


@app.get("/api/yi-hermes/modules")
def yi_hermes_modules() -> dict:
    """List all modules YI-Hermes knows about."""
    from engine.yi_hermes import get_librarian

    lib = get_librarian()
    return {
        "status": "ok",
        "modules": lib.list_modules(),
        "summary": lib.schools_summary(),
    }


@app.get("/api/yi-hermes/glossary")
def yi_hermes_glossary_list(module: str | None = None) -> dict:
    """List glossary terms, optionally filtered by module."""
    from engine.yi_hermes import get_glossary_store

    store = get_glossary_store()
    terms = store.list_all(module=module)
    return {
        "status": "ok",
        "count": len(terms),
        "modules_summary": store.modules_summary(),
        "terms": [t.to_dict() for t in terms],
    }


@app.get("/api/yi-hermes/glossary/search")
def yi_hermes_glossary_search(q: str, limit: int = 30) -> dict:
    """Fuzzy search glossary."""
    from engine.yi_hermes import get_glossary_store

    if not q.strip():
        return {"status": "error", "message": "Query empty"}
    results = get_glossary_store().search(q, limit=limit)
    return {
        "status": "ok",
        "query": q,
        "count": len(results),
        "terms": [t.to_dict() for t in results],
    }


@app.get("/api/yi-hermes/glossary/term/{term_vi}")
def yi_hermes_glossary_get(term_vi: str) -> dict:
    """Get single term by Vietnamese name (URL-encoded)."""
    from engine.yi_hermes import get_glossary_store

    t = get_glossary_store().get(term_vi)
    if t is None:
        return {"status": "not_found", "term_vi": term_vi}
    return {"status": "ok", "term": t.to_dict()}


@app.put("/api/yi-hermes/glossary/term/{term_vi}")
def yi_hermes_glossary_upsert(term_vi: str, req: YiHermesGlossaryUpsertRequest, http_request: Request) -> dict:
    """Add or update a glossary term. Owner-only."""
    from api.auth import require_owner
    require_owner(http_request)
    from engine.yi_hermes import GlossaryTerm, get_glossary_store

    term = GlossaryTerm(
        term_vi=req.term_vi or term_vi,
        term_zh=req.term_zh,
        module=req.module,
        short_def=req.short_def,
        long_def=req.long_def,
        example=req.example,
        see_also=req.see_also,
    )
    get_glossary_store().upsert(term)
    return {"status": "ok", "term": term.to_dict()}


@app.delete("/api/yi-hermes/glossary/term/{term_vi}")
def yi_hermes_glossary_delete(term_vi: str, http_request: Request) -> dict:
    """Delete glossary term. Owner-only."""
    from api.auth import require_owner
    require_owner(http_request)
    from engine.yi_hermes import get_glossary_store

    deleted = get_glossary_store().delete(term_vi)
    return {"status": "ok" if deleted else "not_found", "term_vi": term_vi}


# ─── YI-Hermes Soul + Memory endpoints ────────────────────────────────────


# Helper for yi-hermes per-user resources: must be the calling user OR owner.
# Previously these endpoints were fully unauthenticated — anyone could curl
# /api/yi-hermes/soul/1 and read anh's communication style + learned traits.
def _yi_hermes_require_self_or_owner(user_id: str, request: Request) -> dict:
    from api.auth import require_user
    user = require_user(request)
    if user.get("role") == "owner":
        return user
    if str(user.get("user_id")) == str(user_id):
        return user
    raise HTTPException(403, "forbidden")


@app.get("/api/yi-hermes/soul/{user_id}")
def yi_hermes_soul_get(user_id: str, request: Request) -> dict:
    """Get user's Soul profile (creates default if not seen before)."""
    from engine.yi_hermes import get_soul

    _yi_hermes_require_self_or_owner(user_id, request)
    soul = get_soul(user_id)
    return {"status": "ok", "soul": soul.to_dict()}


@app.put("/api/yi-hermes/soul/{user_id}")
def yi_hermes_soul_update(user_id: str, req: YiHermesSoulUpdateRequest, request: Request) -> dict:
    """Partial update to Soul (only non-None fields are applied)."""
    from engine.yi_hermes import update_soul

    _yi_hermes_require_self_or_owner(user_id, request)
    patch = {k: v for k, v in req.model_dump().items() if v is not None}
    soul = update_soul(user_id, patch)
    return {"status": "ok", "soul": soul.to_dict()}


@app.delete("/api/yi-hermes/soul/{user_id}")
def yi_hermes_soul_reset(user_id: str, request: Request) -> dict:
    """Wipe Soul → restart with default."""
    from engine.yi_hermes import reset_soul

    _yi_hermes_require_self_or_owner(user_id, request)
    soul = reset_soul(user_id)
    return {"status": "ok", "soul": soul.to_dict()}


@app.get("/api/yi-hermes/memory/{user_id}/facts")
def yi_hermes_memory_list_facts(user_id: str, request: Request, category: str | None = None, limit: int = 50) -> dict:
    """List facts about user. Self-or-owner only."""
    from engine.yi_hermes import fact_categories_summary, list_facts

    _yi_hermes_require_self_or_owner(user_id, request)
    facts = list_facts(user_id, category=category, limit=limit)
    return {
        "status": "ok",
        "count": len(facts),
        "category_summary": fact_categories_summary(user_id),
        "facts": [f.to_dict() for f in facts],
    }


@app.post("/api/yi-hermes/memory/{user_id}/facts")
def yi_hermes_memory_add_fact(user_id: str, req: YiHermesFactAddRequest, request: Request) -> dict:
    """Add a fact about user. Self-or-owner only."""
    from engine.yi_hermes import add_fact

    _yi_hermes_require_self_or_owner(user_id, request)
    fact_id = add_fact(
        user_id=user_id,
        fact=req.fact,
        category=req.category,
        confidence=req.confidence,
        notes=req.notes,
    )
    return {"status": "ok", "fact_id": fact_id}


@app.delete("/api/yi-hermes/memory/facts/{fact_id}")
def yi_hermes_memory_delete_fact(fact_id: int, request: Request) -> dict:
    """Delete a memory fact. Owner-only (we don't have fact→user mapping
    cheaply here; restrict to owner)."""
    from api.auth import require_owner
    from engine.yi_hermes import delete_fact

    require_owner(request)
    deleted = delete_fact(fact_id)
    return {"status": "ok" if deleted else "not_found", "fact_id": fact_id}


@app.get("/api/yi-hermes/memory/{user_id}/summaries")
def yi_hermes_memory_list_summaries(user_id: str, request: Request, limit: int = 20) -> dict:
    from engine.yi_hermes import list_summaries

    _yi_hermes_require_self_or_owner(user_id, request)
    summaries = list_summaries(user_id, limit=limit)
    return {
        "status": "ok",
        "count": len(summaries),
        "summaries": [s.to_dict() for s in summaries],
    }


@app.post("/api/yi-hermes/memory/{user_id}/summaries")
def yi_hermes_memory_add_summary(user_id: str, req: YiHermesSummaryAddRequest, request: Request) -> dict:
    from engine.yi_hermes import add_summary

    _yi_hermes_require_self_or_owner(user_id, request)
    sid = add_summary(
        user_id=user_id,
        summary=req.summary,
        key_topics=req.key_topics,
        chart_data_hash=req.chart_data_hash,
    )
    return {"status": "ok", "summary_id": sid}


@app.get("/api/yi-hermes/memory/{user_id}/search")
def yi_hermes_memory_search(user_id: str, q: str, request: Request, limit: int = 5) -> dict:
    """FTS search past summaries. Self-or-owner only."""
    from engine.yi_hermes import search_summaries

    _yi_hermes_require_self_or_owner(user_id, request)
    results = search_summaries(user_id, q, limit=limit)
    return {
        "status": "ok",
        "query": q,
        "count": len(results),
        "summaries": [s.to_dict() for s in results],
    }


@app.get("/api/yi-hermes/memory/{user_id}/top-terms")
def yi_hermes_memory_top_terms(user_id: str, request: Request, limit: int = 10) -> dict:
    from engine.yi_hermes import top_viewed_terms

    _yi_hermes_require_self_or_owner(user_id, request)
    rows = top_viewed_terms(user_id, limit=limit)
    return {
        "status": "ok",
        "top_terms": [{"term_vi": t, "count": c} for t, c in rows],
    }


@app.get("/api/yi-hermes/memory/{user_id}/full")
def yi_hermes_memory_full(user_id: str, request: Request) -> dict:
    """Full memory + soul snapshot for the 'Hermes nhớ về anh' UI panel.
    Self-or-owner only — previously unrestricted."""
    from engine.yi_hermes import (
        get_soul,
        list_facts,
        list_summaries,
        top_viewed_terms,
        fact_categories_summary,
    )

    _yi_hermes_require_self_or_owner(user_id, request)
    soul = get_soul(user_id)
    facts = list_facts(user_id, limit=20)
    summaries = list_summaries(user_id, limit=10)
    top_terms = top_viewed_terms(user_id, limit=10)

    return {
        "status": "ok",
        "user_id": user_id,
        "soul": soul.to_dict(),
        "facts": [f.to_dict() for f in facts],
        "fact_categories": fact_categories_summary(user_id),
        "summaries": [s.to_dict() for s in summaries],
        "top_viewed_terms": [{"term_vi": t, "count": c} for t, c in top_terms],
    }


# ─── YI-Hermes Context (Manifest + Founder + Bootstrap) ──────────────────────


@app.get("/api/yi-hermes/context/manifest")
def yi_hermes_get_manifest() -> dict:
    """Get the YI-CHRONOS project manifest that Hermes reads on every chat."""
    from engine.yi_hermes import get_manifest

    content = get_manifest()
    return {
        "status": "ok",
        "content": content,
        "size_chars": len(content),
    }


@app.put("/api/yi-hermes/context/manifest")
def yi_hermes_update_manifest(req: YiHermesContentUpdateRequest, request: Request) -> dict:
    """Overwrite project manifest. Hermes reloads automatically. Owner-only —
    previously anyone could PUT and wipe the project manifest file."""
    from api.auth import require_owner
    from engine.yi_hermes import update_manifest

    require_owner(request)
    update_manifest(req.content)
    return {"status": "ok", "size_chars": len(req.content)}


@app.get("/api/yi-hermes/context/founder")
def yi_hermes_get_founder(request: Request) -> dict:
    """Get the founder profile that Hermes reads when chatting with anh.

    Owner-only: this file contains anh's personal identity (email,
    Telegram ID, location, communication style, Bát Tự pillars, etc.).
    Previously unrestricted — `curl /api/yi-hermes/context/founder`
    returned the full markdown to any visitor.
    """
    from api.auth import get_current_user
    from engine.yi_hermes import get_founder_profile, get_founder_soul_keys

    user = get_current_user(request)
    if not user or user.get("role") != "owner":
        raise HTTPException(403, "owner-only")

    content = get_founder_profile()
    return {
        "status": "ok",
        "content": content,
        "size_chars": len(content),
        "founder_soul_keys": list(get_founder_soul_keys()),
    }


@app.put("/api/yi-hermes/context/founder")
def yi_hermes_update_founder(req: YiHermesContentUpdateRequest, request: Request) -> dict:
    """Overwrite founder profile. Hermes reloads automatically.

    Owner-only: previously any caller could PUT and replace anh's
    profile file on disk — content integrity + Hermes behavior leak.
    """
    from api.auth import get_current_user
    from engine.yi_hermes import update_founder_profile

    user = get_current_user(request)
    if not user or user.get("role") != "owner":
        raise HTTPException(403, "owner-only")

    update_founder_profile(req.content)
    return {"status": "ok", "size_chars": len(req.content)}


@app.post("/api/yi-hermes/context/reload")
def yi_hermes_reload_context() -> dict:
    """Force-reload manifest + founder from disk (clear cache)."""
    from engine.yi_hermes import reload_context_files

    reload_context_files()
    return {"status": "ok"}


@app.get("/api/yi-hermes/context/summary/{soul_key}")
def yi_hermes_context_summary_for(soul_key: str) -> dict:
    """Show what context is currently injected for a given soul_key.

    For UI: 'Hermes biết gì về user này?'
    """
    from engine.yi_hermes import context_summary

    # URL-decode soul_key (might contain ':')
    return {"status": "ok", "context": context_summary(soul_key)}


# ─── Person + Relationship + Dyad endpoints ─────────────────────────────────


# ─── Note on /api/yi-hermes/persons/* gating ─────────────────────────────────
# This namespace is anh's personal social graph: founder Bát Tự + family +
# colleagues + relationship notes. Previously entirely unauthenticated —
# `curl /api/yi-hermes/persons/_founder` returned anh's full chart. Gating
# everything to owner-only since these endpoints are not exposed to public
# users (each end-user has their own `user_persons` namespace via /api/auth/my).


@app.post("/api/yi-hermes/persons")
def yi_hermes_create_person(req: PersonCreateRequest, request: Request) -> dict:
    """Create a new Person profile (owner-only — anh's social graph)."""
    from api.auth import require_owner
    from engine.yi_hermes.persons import create_person

    require_owner(request)
    p = create_person(**req.model_dump())
    return {"status": "ok", "person": p.to_dict()}


@app.get("/api/yi-hermes/persons")
def yi_hermes_list_persons(
    request: Request,
    relationship_to_founder: str | None = None,
    day_master: str | None = None,
    limit: int = 100,
) -> dict:
    from api.auth import require_owner
    from engine.yi_hermes.persons import list_persons

    require_owner(request)
    persons = list_persons(
        relationship_to_founder=relationship_to_founder,
        day_master=day_master, limit=limit,
    )
    return {"status": "ok", "persons": [p.to_dict() for p in persons], "count": len(persons)}


@app.get("/api/yi-hermes/persons/{person_id}")
def yi_hermes_get_person(person_id: str, request: Request) -> dict:
    from api.auth import require_owner
    from engine.yi_hermes.persons import get_person

    require_owner(request)
    p = get_person(person_id)
    if not p:
        return {"status": "not_found", "person_id": person_id}
    return {"status": "ok", "person": p.to_dict()}


@app.put("/api/yi-hermes/persons/{person_id}")
def yi_hermes_update_person(person_id: str, req: PersonUpdateRequest, request: Request) -> dict:
    from api.auth import require_owner
    from engine.yi_hermes.persons import update_person

    require_owner(request)
    patch = {k: v for k, v in req.model_dump().items() if v is not None}
    p = update_person(person_id, patch)
    if not p:
        return {"status": "not_found", "person_id": person_id}
    return {"status": "ok", "person": p.to_dict()}


@app.post("/api/yi-hermes/persons/{person_id}/layer")
def yi_hermes_update_layer(person_id: str, req: PersonLayerUpdateRequest, request: Request) -> dict:
    """Merge `patch` into the named layer of person (career/health/physiognomy/...). Owner-only."""
    from api.auth import require_owner
    from engine.yi_hermes.persons import update_layer

    require_owner(request)
    p = update_layer(person_id, req.layer, req.patch, confidence=req.confidence)
    if not p:
        return {"status": "not_found", "person_id": person_id}
    return {"status": "ok", "person": p.to_dict()}


@app.post("/api/yi-hermes/persons/{person_id}/notes")
def yi_hermes_add_person_note(person_id: str, req: PersonNoteRequest, request: Request) -> dict:
    from api.auth import require_owner
    from engine.yi_hermes.persons import add_note

    require_owner(request)
    note_id = add_note(
        person_id, req.body, source=req.source,
        confidence=req.confidence, layer_hint=req.layer_hint,
    )
    return {"status": "ok", "note_id": note_id}


@app.get("/api/yi-hermes/persons/{person_id}/notes")
def yi_hermes_list_person_notes(person_id: str, request: Request, layer_hint: str | None = None, limit: int = 50) -> dict:
    from api.auth import require_owner
    from engine.yi_hermes.persons import list_notes

    require_owner(request)
    notes = list_notes(person_id, layer_hint=layer_hint, limit=limit)
    return {"status": "ok", "notes": [n.to_dict() for n in notes]}


@app.post("/api/yi-hermes/persons/{person_id}/cast-bat-tu")
def yi_hermes_person_cast_bat_tu(person_id: str, request: Request) -> dict:
    """Lazy-cast (and cache) Bát Tự for a person who has birth_datetime_local set. Owner-only."""
    from api.auth import require_owner
    from engine.yi_hermes.persons import cast_bat_tu_for, get_person

    require_owner(request)
    p = get_person(person_id)
    if not p:
        return {"status": "not_found", "person_id": person_id}
    if not p.birth_datetime_local:
        return {"status": "no_birth_data", "person_id": person_id}
    chart = cast_bat_tu_for(person_id)
    return {"status": "ok", "chart": chart}


@app.delete("/api/yi-hermes/persons/{person_id}")
def yi_hermes_delete_person(person_id: str, request: Request) -> dict:
    from api.auth import require_owner
    from engine.yi_hermes.persons import delete_person

    require_owner(request)
    ok = delete_person(person_id)
    return {"status": "ok" if ok else "not_found", "person_id": person_id}


# ─── Relationships ────────────────────────────────────────────────────────


@app.post("/api/yi-hermes/relationships")
def yi_hermes_add_relationship(req: RelationshipCreateRequest, request: Request) -> dict:
    """Owner-only: relationships are anh's personal social graph."""
    from api.auth import require_owner
    from engine.yi_hermes.relationships import add_relationship

    require_owner(request)
    rel = add_relationship(**req.model_dump())
    return {"status": "ok", "relationship": rel.to_dict()}


@app.get("/api/yi-hermes/relationships")
def yi_hermes_list_relationships(
    request: Request,
    person_id: str | None = None,
    rel_type: str | None = None,
    direction: str = "from",
    limit: int = 100,
) -> dict:
    from api.auth import require_owner
    from engine.yi_hermes.relationships import list_relationships

    require_owner(request)
    rels = list_relationships(
        person_id=person_id, rel_type=rel_type,
        direction=direction, limit=limit,
    )
    return {"status": "ok", "relationships": [r.to_dict() for r in rels], "count": len(rels)}


@app.get("/api/yi-hermes/network/{founder_id}")
def yi_hermes_network(founder_id: str, request: Request) -> dict:
    """Return the founder's social graph (depth 1).

    Owner-only when querying `_founder` — that returns anh's full Bát Tự,
    day master, cách cục, birth datetime, and entire relationship graph
    (spouse, children, colleagues). For non-`_founder` IDs, still require
    login since this endpoint exposes personal birth data either way.
    """
    from api.auth import get_current_user
    from engine.yi_hermes.relationships import founder_network

    user = get_current_user(request)
    if founder_id == "_founder":
        if not user or user.get("role") != "owner":
            raise HTTPException(403, "owner-only")
    elif not user:
        raise HTTPException(401, "login required")

    return {"status": "ok", "graph": founder_network(founder_id)}


# ─── Dyad analysis ─────────────────────────────────────────────────────────


# ─── YI-Lexicon endpoints ───────────────────────────────────────────────────


@app.get("/api/yi-lexicon/stats")
def yi_lexicon_stats() -> dict:
    from engine.yi_lexicon import stats
    return {"status": "ok", "stats": stats()}


@app.post("/api/yi-lexicon/concepts")
def yi_lexicon_create_concept(req: LexiconConceptCreateRequest) -> dict:
    from engine.yi_lexicon import add_concept
    c = add_concept(**req.model_dump())
    return {"status": "ok", "concept": c.to_dict()}


@app.get("/api/yi-lexicon/concepts")
def yi_lexicon_search_concepts(q: str, schools: str | None = None, limit: int = 20) -> dict:
    """Search concepts (FTS5). `schools` is comma-separated filter."""
    from engine.yi_lexicon import search_concepts
    school_list = [s.strip() for s in schools.split(",")] if schools else None
    hits = search_concepts(q, schools=school_list, limit=limit)
    return {"status": "ok", "results": [c.to_dict() for c in hits]}


@app.get("/api/yi-lexicon/concepts/{concept_id}")
def yi_lexicon_get_concept(concept_id: int) -> dict:
    from engine.yi_lexicon import get_concept, mappings_for
    c = get_concept(concept_id=concept_id)
    if not c:
        return {"status": "not_found"}
    return {
        "status": "ok",
        "concept": c.to_dict(),
        "mappings": [m.to_dict() for m in mappings_for(concept_id)],
    }


@app.post("/api/yi-lexicon/mappings")
def yi_lexicon_add_mapping(req: LexiconMappingCreateRequest) -> dict:
    from engine.yi_lexicon import add_mapping
    m = add_mapping(**req.model_dump())
    return {"status": "ok", "mapping": m.to_dict()}


@app.get("/api/yi-lexicon/reverse-lookup")
def yi_lexicon_reverse_lookup(dim_type: str, dim_value: str, limit: int = 50) -> dict:
    """Find concepts that map to (dim_type, dim_value). E.g. 'what concepts → mộc?'"""
    from engine.yi_lexicon import reverse_lookup_concepts
    hits = reverse_lookup_concepts(dim_type, dim_value, limit=limit)
    return {"status": "ok", "results": [c.to_dict() for c in hits]}


@app.post("/api/yi-lexicon/interpret")
def yi_lexicon_interpret(req: LexiconInterpretRequest) -> dict:
    """Parse free-text observation → symbolic context (cho LLM prompt enrichment)."""
    from engine.yi_lexicon.parser import interpret_observation
    ctx = interpret_observation(req.text, schools=req.schools)
    return {"status": "ok", "context": ctx.to_dict()}


@app.post("/api/yi-lexicon/corpora")
def yi_lexicon_register_corpus(req: LexiconCorpusRegisterRequest) -> dict:
    from engine.yi_lexicon.ingestion import register_corpus
    cid = register_corpus(**req.model_dump())
    return {"status": "ok", "corpus_id": cid}


@app.get("/api/yi-lexicon/corpora")
def yi_lexicon_list_corpora() -> dict:
    from engine.yi_lexicon import list_corpora
    return {"status": "ok", "corpora": [c.to_dict() for c in list_corpora()]}


@app.post("/api/yi-lexicon/ingest")
def yi_lexicon_ingest(req: LexiconIngestRequest) -> dict:
    """Read corpus + LLM extract concepts/mappings + YOLO auto-merge."""
    from engine.yi_lexicon.ingestion import ingest_corpus
    result = ingest_corpus(req.corpus_id, max_chunks=req.max_chunks)
    return {"status": "ok", "result": result.__dict__}


@app.post("/api/yi-lexicon/distill")
def yi_lexicon_distill(req: LexiconDistillRequest) -> dict:
    """Distill knowledge from a completed council session."""
    from engine.yi_lexicon.distill import distill_from_council
    result = distill_from_council(req.root_id)
    return {"status": "ok", "result": result.__dict__}


@app.get("/api/yi-lexicon/distill-queue")
def yi_lexicon_distill_queue(status: str | None = None, limit: int = 100) -> dict:
    from engine.yi_lexicon import get_distill_queue
    items = get_distill_queue(status=status, limit=limit)
    return {"status": "ok", "items": [i.to_dict() for i in items]}


@app.post("/api/yi-lexicon/distill-queue/{item_id}/resolve")
def yi_lexicon_resolve_distill(item_id: int, req: LexiconResolveItemRequest) -> dict:
    from engine.yi_lexicon import resolve_distill_item
    ok = resolve_distill_item(item_id, status=req.status, reviewer_note=req.reviewer_note)
    return {"status": "ok" if ok else "not_found"}


# ─── Lexicon conflict resolver (anh arbiter) ─────────────────────────────────


@app.get("/api/yi-lexicon/conflicts")
def yi_lexicon_list_conflicts(status: str = "open", limit: int = 50) -> dict:
    """List conflict groups — mappings that disagree on (concept, dim_type, school)."""
    from engine.yi_lexicon import list_conflicts
    return {"status": "ok", "conflicts": list_conflicts(status=status, limit=limit)}


@app.post("/api/yi-lexicon/conflicts/{conflict_group_id}/resolve")
def yi_lexicon_resolve_conflict(conflict_group_id: int, req: LexiconResolveConflictRequest) -> dict:
    """Anh chốt conflict — 'resolved' (chọn primary) | 'kept_all' | 'dismissed'."""
    from engine.yi_lexicon import resolve_conflict
    ok = resolve_conflict(
        conflict_group_id,
        primary_mapping_id=req.primary_mapping_id,
        status=req.status,
        anh_note=req.anh_note,
    )
    return {"status": "ok" if ok else "not_found"}


@app.get("/api/yi-lexicon/tiers/manifest")
def yi_lexicon_tier_manifest() -> dict:
    """Return the source tier manifest (42 PDFs + reading plan)."""
    from engine.yi_lexicon.tiers import _load_manifest
    return {"status": "ok", "manifest": _load_manifest()}


@app.get("/api/yi-lexicon/tiers/current-week")
def yi_lexicon_current_week() -> dict:
    """Next pending week in reading plan."""
    from engine.yi_lexicon.tiers import current_reading_week
    week = current_reading_week()
    return {"status": "ok", "current_week": week}


# ─── Library / Thủ thư endpoints (v3, 2026-05-12) ────────────────────────────

# ─── Restored Books Library — phục chế sách Việt qua OCR/MarkItDown ───
# Anh đọc trực tiếp trên live — content.md đã embedded vào image

@app.get("/api/library/restored-books/list")
def yi_library_restored_books_list() -> dict:
    """List all restored books (Tứ Trụ, Tử Vi, Chu Dịch Việt) đã phục chế."""
    from engine.yi_library.restored_books import list_books
    books = list_books()
    # Group by category
    by_category: dict[str, list] = {}
    for b in books:
        by_category.setdefault(b["category"], []).append(b)
    total_chars = sum(b["chars"] for b in books)
    total_pages = sum(b["total_pages"] for b in books)
    return {
        "status": "ok",
        "total_books": len(books),
        "total_chars": total_chars,
        "total_pages": total_pages,
        "categories": by_category,
        "books": books,
    }


@app.get("/api/library/restored-books/{book_id}/content")
def yi_library_restored_book_content(book_id: str, page: int | None = None) -> dict:
    """Get full markdown content of a restored book, hoặc 1 page cụ thể."""
    from engine.yi_library.restored_books import get_book_content
    return get_book_content(book_id, page=page)


@app.get("/api/library/restored-books/search")
def yi_library_restored_books_search(q: str, max_results: int = 30) -> dict:
    """Full-text search across all restored books. Returns snippets with context."""
    from engine.yi_library.restored_books import search_books
    hits = search_books(q, max_results=max_results)
    return {
        "status": "ok",
        "query": q,
        "total_hits": len(hits),
        "hits": hits,
    }


@app.get("/api/yi-lexicon/library")
def yi_lexicon_library_list(
    tier: str | None = None,
    status: str | None = None,
    school: str | None = None,
) -> dict:
    """List books in library. Optional filters: tier / status / school."""
    from engine.yi_lexicon.store import (
        library_stats,
        list_corpora,
        sync_restoration_metadata_from_manifest,
    )
    corpora = [
        sync_restoration_metadata_from_manifest(c)
        for c in list_corpora(tier=tier, status=status, school=school)
    ]
    books = [c.to_dict() for c in corpora]
    return {
        "status": "ok",
        "books": books,
        "stats": library_stats(tier=tier, status=status, school=school),
    }


@app.get("/api/yi-lexicon/library/stats")
def yi_lexicon_library_stats(
    tier: str | None = None,
    status: str | None = None,
    school: str | None = None,
) -> dict:
    """Library dashboard counts: total, by_tier, by_status, overall progress."""
    from engine.yi_lexicon.store import library_stats
    return {"status": "ok", "stats": library_stats(tier=tier, status=status, school=school)}


@app.get("/api/yi-lexicon/library/books/{corpus_id}")
def yi_lexicon_library_book(corpus_id: int) -> dict:
    """Single book detail."""
    from engine.yi_lexicon.store import get_corpus
    c = get_corpus(corpus_id=corpus_id)
    if not c:
        return {"status": "error", "message": "book not found"}
    return {"status": "ok", "book": c.to_dict()}


class LibraryUpdateRequest(BaseModel):
    status: str | None = None
    tier: str | None = None
    tier_decided_by: str | None = None
    schools_tags: list[str] | None = None
    author: str | None = None
    notes: str | None = None
    pages_total: int | None = None
    pages_ingested: int | None = None


@app.patch("/api/yi-lexicon/library/books/{corpus_id}")
def yi_lexicon_library_update_book(corpus_id: int, req: LibraryUpdateRequest) -> dict:
    """Anh edits book metadata (tier / status / schools / notes)."""
    from engine.yi_lexicon.store import update_corpus
    payload = req.model_dump(exclude_unset=True)
    # If anh manually decides tier, mark provenance
    if "tier" in payload and "tier_decided_by" not in payload:
        payload["tier_decided_by"] = "anh"
    c = update_corpus(corpus_id, **payload)
    if not c:
        return {"status": "error", "message": "update failed"}
    return {"status": "ok", "book": c.to_dict()}


class LibrarianAnalyzeRequest(BaseModel):
    file_path: str
    ocr_pages: int = 6
    skip_llm: bool = False
    register: bool = True  # auto-add to corpora


@app.post("/api/yi-lexicon/library/analyze")
def yi_lexicon_library_analyze(req: LibrarianAnalyzeRequest) -> dict:
    """Run Thủ thư analysis on a PDF.

    1. Page count + cover thumbnail
    2. Manifest lookup (tier-config)
    3. If not in manifest: OCR 5-6 intro pages → LLM classify
    4. If `register=True`: insert into corpora table with status='queued'
    """
    from engine.yi_lexicon.librarian import analyze_book, register_proposal_as_corpus
    prop = analyze_book(req.file_path, ocr_pages=req.ocr_pages, skip_llm=req.skip_llm)
    out: dict = {"status": "ok", "proposal": prop.to_dict()}
    if req.register and not prop.errors:
        try:
            corpus = register_proposal_as_corpus(prop)
            out["corpus"] = corpus.to_dict()
        except Exception as e:
            out["register_error"] = str(e)
    return out


@app.post("/api/yi-lexicon/library/scan-text-layers")
def yi_lexicon_scan_text_layers(only_unprobed: bool = False) -> dict:
    """Probe text layer của tất cả PDFs trong thư viện. Phân loại:
    - text_layer (chars/page ≥ 200) → restore qua MarkItDown (1300x faster)
    - hybrid (50-200) → MarkItDown + OCR fallback
    - pure_scan (< 50) → qwen-vl OCR pipeline

    Lưu kết quả vào corpora.restore_method.
    `only_unprobed=true` để skip sách đã probe.
    """
    from engine.yi_lexicon.librarian import scan_library_text_layers
    result = scan_library_text_layers(
        update_corpora=True, only_unprobed=only_unprobed,
    )
    return {"status": "ok", **result}


@app.get("/api/yi-lexicon/library/classify/{corpus_id}")
def yi_lexicon_classify_one(corpus_id: int) -> dict:
    """Probe + classify text layer cho 1 sách. Live (không cache)."""
    from engine.yi_lexicon.librarian import classify_text_layer
    from engine.yi_lexicon.store import get_corpus, update_corpus
    c = get_corpus(corpus_id=corpus_id)
    if not c or not c.file_path:
        return {"status": "error", "message": "book not found or no file_path"}
    info = classify_text_layer(c.file_path)
    update_corpus(
        corpus_id,
        restore_method=info.get("method", "unknown"),
        text_layer_chars_per_page=info.get("chars_per_page", 0.0),
        bump_text_layer_probed_at=True,
    )
    return {"status": "ok", "corpus_id": corpus_id,
            "name": c.name, "classification": info}


@app.post("/api/yi-lexicon/library/sync")
def yi_lexicon_library_sync(skip_llm: bool = True) -> dict:
    """Scan `thư viện sách/` and sync all PDFs into corpora table.

    `skip_llm=True` (default) uses only filename + manifest — fast bulk scan.
    Set `skip_llm=False` to run LLM classifier on every uncatalogued book (slow + costs API).
    """
    from engine.yi_lexicon.librarian import sync_library_to_corpora
    result = sync_library_to_corpora(skip_llm=skip_llm)
    return {"status": "ok", **result}


@app.get("/api/yi-lexicon/library/scan")
def yi_lexicon_library_scan(skip_llm: bool = True, limit: int | None = None) -> dict:
    """Dry-run discovery: walk thư viện/ and return proposals WITHOUT persisting."""
    from engine.yi_lexicon.librarian import scan_library_dir
    proposals = scan_library_dir(skip_llm=skip_llm, limit=limit)
    return {"status": "ok", "count": len(proposals), "proposals": proposals}


@app.get("/api/yi-lexicon/schools")
def yi_lexicon_schools() -> dict:
    """List all registered schools (extensible — anh có thể thêm trường phái mới)."""
    from engine.yi_lexicon.librarian import list_schools
    return {"status": "ok", "schools": list_schools()}


class AddSchoolRequest(BaseModel):
    key: str
    vi_label: str
    color: str = "#94a3b8"


@app.post("/api/yi-lexicon/schools")
def yi_lexicon_add_school(req: AddSchoolRequest) -> dict:
    """Register a new school dynamically."""
    from engine.yi_lexicon.librarian import add_school
    return {"status": "ok", "school": add_school(req.key, req.vi_label, req.color)}


# ─── Restoration endpoints (v4 phase A, 2026-05-12) ──────────────────────────

class RestoreRequest(BaseModel):
    corpus_id: int
    page_start: int | None = None
    page_end: int | None = None
    max_pages: int | None = None
    skip_llm: bool = False
    ocr_backend: str = "tesseract"
    ocr_lang: str = "vie"
    dpi: int = 240


@app.post("/api/yi-lexicon/restore")
def yi_lexicon_restore(req: RestoreRequest) -> dict:
    """Trigger restoration pipeline for a book.

    Long-running — for production use a background task queue. For pilot,
    call blocking and stream progress via SSE later. Here we run synchronously.
    """
    from engine.yi_lexicon.restoration import restore_book, RestorationConfig
    cfg = RestorationConfig(
        ocr_backend=req.ocr_backend,
        ocr_lang=req.ocr_lang,
        dpi=req.dpi,
        page_range=((req.page_start or 1), req.page_end) if (req.page_start or req.page_end) else None,
        max_pages=req.max_pages,
        skip_llm=req.skip_llm,
    )
    result = restore_book(req.corpus_id, config=cfg)
    return {
        "status": "ok" if not result.errors or result.pages_processed > 0 else "error",
        "result": {
            "corpus_id": result.corpus_id,
            "book_slug": result.book_slug,
            "root_dir": result.root_dir,
            "manifest_path": result.manifest_path,
            "pages_processed": result.pages_processed,
            "pages_failed": result.pages_failed,
            "figures_extracted": result.figures_extracted,
            "wikilinks_total": result.wikilinks_total,
            "duration_seconds": round(result.duration_seconds, 2),
            "errors": result.errors[:50],  # cap to avoid huge response
        },
    }


def _load_book_manifest(corpus_id: int):
    """Helper: get manifest for a corpus or return None."""
    from engine.yi_lexicon.store import get_corpus, sync_restoration_metadata_from_manifest
    from engine.yi_lexicon.restoration.manifest import load_manifest
    c = get_corpus(corpus_id=corpus_id)
    if not c or not c.restored_manifest:
        return None, None
    try:
        manifest = load_manifest(c.restored_manifest)
        return sync_restoration_metadata_from_manifest(c), manifest
    except Exception:
        return c, None


@app.get("/api/yi-lexicon/restored/{corpus_id}")
def yi_lexicon_restored_overview(corpus_id: int) -> dict:
    """Manifest summary for a restored book: TOC, page count, wikilink count."""
    corpus, manifest = _load_book_manifest(corpus_id)
    if not corpus:
        return {"status": "error", "message": "book not found"}
    if not manifest:
        return {"status": "ok", "restored": False, "book": corpus.to_dict()}
    from engine.yi_lexicon.restoration.manifest import sections_for_reader
    pages_restored = max(manifest.pages_restored, corpus.restored_pages or 0)
    pages_total = max(manifest.pages_total, corpus.pages_total or 0)
    return {
        "status": "ok",
        "restored": True,
        "book": corpus.to_dict(),
        "manifest": {
            "book_slug": manifest.book_slug,
            "book_name": manifest.book_name,
            "author": manifest.author,
            "tier": manifest.tier,
            "copyright_status": manifest.copyright_status,
            "pages_total": pages_total,
            "pages_restored": pages_restored,
            "sections": [
                {"section_id": s.section_id, "title": s.title, "level": s.level,
                 "start_page": s.start_page, "end_page": s.end_page}
                for s in sections_for_reader(manifest.sections)
            ],
            "figures_count": len(manifest.figures),
            "wikilink_count": len(manifest.wikilink_index),
            "ocr_backend": manifest.ocr_backend,
            "llm_model": manifest.llm_model,
            "pipeline_version": manifest.pipeline_version,
        },
    }


@app.get("/api/yi-lexicon/restored/{corpus_id}/page/{page_no}")
def yi_lexicon_restored_page(
    corpus_id: int,
    page_no: int,
    format: str = "md",
    lang: str = "zh",  # "zh" (gốc) | "vi" (dịch sang tiếng Việt)
) -> dict:
    """Get one page's restored content.

    Args:
        format: "md" (raw markdown) | "html" (rendered)
        lang: "zh" (bản gốc từ pages/) | "vi" (bản dịch từ pages_vi/, fallback về zh nếu chưa dịch)
    """
    from pathlib import Path as _P
    corpus, manifest = _load_book_manifest(corpus_id)
    if not corpus or not manifest:
        return {"status": "error", "message": "book not restored"}
    page_record = next((p for p in manifest.pages if p.page == page_no), None)
    if not page_record or not page_record.md_path:
        return {"status": "error", "message": f"page {page_no} not restored"}
    root = _P(corpus.restored_path)

    # === Lang resolution: thử pages_vi/ trước nếu lang=vi ===
    lang_served = "zh"
    md_file = root / page_record.md_path
    if lang == "vi":
        # md_path thường dạng "pages/page-XXXX.md" → đổi thành "pages_vi/page-XXXX.md"
        vi_path = root / page_record.md_path.replace("pages/", "pages_vi/", 1)
        if vi_path.exists():
            md_file = vi_path
            lang_served = "vi"
    if not md_file.exists():
        return {"status": "error", "message": "page file missing"}
    md_text = md_file.read_text(encoding="utf-8")
    out = {
        "status": "ok",
        "page": page_no,
        "lang": lang,           # lang client requested
        "lang_served": lang_served,  # lang actually served (vi nếu có, else zh)
        "section_id": page_record.section_id,
        "wikilinks": page_record.wikilinks,
        "figure_ids": page_record.figure_ids,
        "confidence": page_record.ocr_confidence,
        "needs_review": page_record.needs_review,
        # v2 metadata
        "summary_short": page_record.summary_short,
        "hashtags": page_record.hashtags,
        "persons": page_record.persons,
        "que_mentions": page_record.que_mentions,
    }
    if format == "html":
        from engine.yi_lexicon.restoration.exporters import render_page_html
        out["html"] = render_page_html(md_text)
    else:
        out["markdown"] = md_text
    return out


@app.get("/api/yi-lexicon/restored/{corpus_id}/translation-status")
def yi_lexicon_translation_status(corpus_id: int) -> dict:
    """Báo cáo tiến độ dịch sang tiếng Việt: bao nhiêu trang đã có bản dịch."""
    from pathlib import Path as _P
    corpus, manifest = _load_book_manifest(corpus_id)
    if not corpus or not manifest:
        return {"status": "error", "message": "book not restored"}
    root = _P(corpus.restored_path)
    pages_vi_dir = root / "pages_vi"
    if not pages_vi_dir.exists():
        return {
            "status": "ok",
            "corpus_id": corpus_id,
            "translated_pages": 0,
            "total_pages": manifest.pages_total,
            "has_translation": False,
        }
    vi_files = list(pages_vi_dir.glob("page-*.md"))
    return {
        "status": "ok",
        "corpus_id": corpus_id,
        "translated_pages": len(vi_files),
        "total_pages": manifest.pages_total,
        "has_translation": len(vi_files) > 0,
        "complete": len(vi_files) >= manifest.pages_total,
    }


@app.get("/api/yi-lexicon/restored/{corpus_id}/figure/{figure_id}")
def yi_lexicon_restored_figure(corpus_id: int, figure_id: str):
    """Serve a restored figure PNG. Returns FileResponse or 404."""
    from fastapi.responses import FileResponse
    from fastapi import HTTPException
    from pathlib import Path as _P
    corpus, manifest = _load_book_manifest(corpus_id)
    if not corpus or not manifest:
        raise HTTPException(status_code=404, detail="not restored")
    fig = next((f for f in manifest.figures if f.figure_id == figure_id), None)
    if not fig:
        raise HTTPException(status_code=404, detail="figure not found")
    root = _P(corpus.restored_path)
    target = root / fig.image_path
    if not target.exists():
        raise HTTPException(status_code=404, detail="image missing")
    return FileResponse(str(target), media_type="image/png")


@app.get("/api/yi-lexicon/restored/{corpus_id}/figures")
def yi_lexicon_restored_figures(corpus_id: int, status: str | None = None) -> dict:
    """Danh sách figures (extracted + detected) trong sách.

    Query: `?status=needs_redraw` để chỉ lấy hình cần vẽ lại.
    """
    _, manifest = _load_book_manifest(corpus_id)
    if not manifest:
        return {"status": "error", "message": "book not restored"}
    figs = manifest.figures
    if status:
        figs = [f for f in figs if (f.redraw_status == status or
                                     (status == "extracted" and f.source == "extracted"))]
    return {
        "status": "ok",
        "count": len(figs),
        "figures": [
            {
                "figure_id": f.figure_id, "page": f.page,
                "figure_type": f.figure_type, "source": f.source,
                "description": f.description, "caption": f.caption,
                "redraw_status": f.redraw_status,
                "placeholder": f.placeholder,
                "image_path": f.image_path,
                "redrawn_svg": f.redrawn_svg,
                "classified_as": f.classified_as,
            }
            for f in figs
        ],
    }


class FigureUpdateRequest(BaseModel):
    redraw_status: str | None = None  # 'needs_redraw' | 'in_progress' | 'done' | 'skip'
    redrawn_svg: str | None = None    # paste SVG content
    classified_as: str | None = None
    description: str | None = None


@app.patch("/api/yi-lexicon/restored/{corpus_id}/figures/{figure_id}")
def yi_lexicon_update_figure(corpus_id: int, figure_id: str,
                              req: FigureUpdateRequest) -> dict:
    """Update figure status / paste SVG redraw."""
    from engine.yi_lexicon.restoration.manifest import save_manifest
    from pathlib import Path as _P
    corpus, manifest = _load_book_manifest(corpus_id)
    if not manifest:
        return {"status": "error", "message": "not restored"}
    target = next((f for f in manifest.figures if f.figure_id == figure_id), None)
    if not target:
        return {"status": "error", "message": "figure not found"}
    payload = req.model_dump(exclude_unset=True)
    if "redraw_status" in payload:
        target.redraw_status = payload["redraw_status"]
    if "redrawn_svg" in payload:
        target.redrawn_svg = payload["redrawn_svg"]
    if "classified_as" in payload:
        target.classified_as = payload["classified_as"]
    if "description" in payload:
        target.description = payload["description"]
    save_manifest(manifest, _P(corpus.restored_manifest))
    return {"status": "ok", "figure": {
        "figure_id": target.figure_id, "redraw_status": target.redraw_status,
        "description": target.description,
    }}


@app.get("/api/yi-lexicon/restored/{corpus_id}/hashtags")
def yi_lexicon_restored_hashtags(corpus_id: int) -> dict:
    """Aggregated hashtag cloud: tag → list of pages mentioning it."""
    _, manifest = _load_book_manifest(corpus_id)
    if not manifest:
        return {"status": "error", "message": "book not restored"}
    return {
        "status": "ok",
        "count": len(manifest.hashtag_index),
        "hashtags": [
            {"tag": h.tag, "count": h.count, "pages": h.pages[:50]}
            for h in sorted(manifest.hashtag_index, key=lambda x: -x.count)
        ],
    }


@app.get("/api/yi-lexicon/restored/{corpus_id}/persons")
def yi_lexicon_restored_persons(corpus_id: int) -> dict:
    """Aggregated NER: persons mentioned → pages."""
    _, manifest = _load_book_manifest(corpus_id)
    if not manifest:
        return {"status": "error", "message": "book not restored"}
    return {
        "status": "ok",
        "count": len(manifest.person_index),
        "persons": [
            {"name": p.name, "count": p.count, "pages": p.pages[:50]}
            for p in sorted(manifest.person_index, key=lambda x: -x.count)
        ],
    }


@app.get("/api/yi-lexicon/restored/{corpus_id}/search")
def yi_lexicon_restored_search(
    corpus_id: int,
    hashtag: str | None = None,
    person: str | None = None,
    que: str | None = None,
    q: str | None = None,            # free-text search across summaries
) -> dict:
    """Search pages by hashtag / person / quẻ / free text.

    Returns list of {page, summary_short, hashtags, section_id}.
    """
    _, manifest = _load_book_manifest(corpus_id)
    if not manifest:
        return {"status": "error", "message": "book not restored"}

    def match(page) -> bool:
        if hashtag:
            tags_lower = [t.lower() for t in page.hashtags]
            needle = hashtag.lower() if hashtag.startswith("#") else f"#{hashtag.lower()}"
            if needle not in tags_lower:
                return False
        if person:
            if not any(person.lower() in p.lower() for p in page.persons):
                return False
        if que:
            if not any(que.lower() in q2.lower() for q2 in page.que_mentions):
                return False
        if q:
            ql = q.lower()
            haystacks = [page.summary_short, " ".join(page.hashtags),
                         " ".join(page.persons), " ".join(page.que_mentions)]
            if not any(ql in h.lower() for h in haystacks if h):
                return False
        return True

    matches = [p for p in manifest.pages if match(p)]
    return {
        "status": "ok",
        "count": len(matches),
        "hits": [
            {
                "page": p.page,
                "section_id": p.section_id,
                "summary_short": p.summary_short,
                "hashtags": p.hashtags,
                "persons": p.persons,
                "que_mentions": p.que_mentions,
            }
            for p in matches[:100]
        ],
    }


@app.get("/api/yi-lexicon/restored/{corpus_id}/wikilinks")
def yi_lexicon_restored_wikilinks(corpus_id: int) -> dict:
    """All wikilinks in this book + page anchors. Powers 'concept → trang' navigation."""
    corpus, manifest = _load_book_manifest(corpus_id)
    if not manifest:
        return {"status": "error", "message": "book not restored"}
    return {
        "status": "ok",
        "wikilinks": [
            {"concept_vi": w.concept_vi, "occurrences": w.occurrences}
            for w in manifest.wikilink_index
        ],
    }


@app.get("/api/yi-lexicon/restored/{corpus_id}/download")
def yi_lexicon_restored_download(corpus_id: int, fmt: str = "md"):
    """Download restored content.

    POLICY: anh đã chốt — `allow_download=0` mặc định cho TẤT CẢ sách (kể cả public domain),
    để tránh phân phối ngoài ý muốn. Anh muốn cho phép sách cụ thể nào thì bật flag thủ công
    qua PATCH /api/yi-lexicon/library/books/{id}.
    """
    from fastapi.responses import FileResponse, JSONResponse
    from pathlib import Path as _P
    corpus, manifest = _load_book_manifest(corpus_id)
    if not corpus or not manifest:
        return JSONResponse(
            status_code=404, content={"status": "error", "message": "book not restored"}
        )
    if not corpus.allow_download:
        return JSONResponse(
            status_code=403,
            content={
                "status": "forbidden",
                "message": (
                    "Bản phục chế nội bộ — không cho phép tải xuống. "
                    "Vui lòng mua sách gốc tại nhà xuất bản."
                ),
                "copyright_status": corpus.copyright_status,
            },
        )
    root = _P(corpus.restored_path)
    if fmt == "md":
        target = root / "content.md"
        if not target.exists():
            return JSONResponse(status_code=404, content={"status": "error", "message": "content.md missing"})
        return FileResponse(
            str(target), media_type="text/markdown",
            filename=f"{manifest.book_slug}.md",
        )
    return JSONResponse(
        status_code=400, content={"status": "error", "message": f"unsupported fmt: {fmt}"}
    )


@app.get("/api/yi-lexicon/restore/nightly/queue")
def yi_lexicon_nightly_queue(tier: str | None = None) -> dict:
    """Preview the queue cho nightly batch — sách nào sẽ được phục chế theo thứ tự."""
    from engine.yi_lexicon.restoration.nightly import select_queue
    tiers = [tier] if tier else None
    queue = select_queue(tiers=tiers)
    return {
        "status": "ok",
        "count": len(queue),
        "queue": [
            {
                "corpus_id": c.corpus_id, "name": c.name, "tier": c.tier,
                "restored_status": c.restored_status,
                "restored_pages": c.restored_pages,
                "pages_total": c.pages_total,
                "progress_percent": (
                    round((c.restored_pages or 0) / c.pages_total * 100, 1)
                    if c.pages_total else 0
                ),
            }
            for c in queue[:50]
        ],
    }


@app.get("/api/yi-lexicon/restored/{corpus_id}/plan")
def yi_lexicon_get_plan(corpus_id: int) -> dict:
    """Get the restoration plan for a book. Returns markdown + JSON state."""
    from engine.yi_lexicon.restoration.plan import load_plan, _plan_path
    from engine.yi_lexicon.restoration.manifest import make_book_slug
    from engine.yi_lexicon.store import get_corpus
    plan = load_plan(corpus_id)
    if not plan:
        return {"status": "no_plan", "message": "Chưa có kế hoạch — gọi POST /plan để tạo."}
    c = get_corpus(corpus_id=corpus_id)
    slug = make_book_slug(c.name) if c else ""
    md_path = _plan_path(slug) if slug else None
    md_content = md_path.read_text(encoding="utf-8") if (md_path and md_path.exists()) else ""
    return {"status": "ok", "plan": plan.to_dict(), "markdown": md_content}


class CreatePlanRequest(BaseModel):
    corpus_id: int
    overwrite: bool = False
    sample_pages: list[int] | None = None


@app.post("/api/yi-lexicon/restored/plan")
def yi_lexicon_create_plan(req: CreatePlanRequest) -> dict:
    """Lập (hoặc làm mới) kế hoạch phục chế cho 1 cuốn.

    Bao gồm: sample 5 trang qua Tesseract nhanh, chia batch Phase 1, ước tính ETA.
    KHÔNG trigger pipeline — chỉ ghi plan.md + plan.json để anh duyệt.
    """
    from engine.yi_lexicon.restoration.plan import create_plan
    try:
        plan = create_plan(
            req.corpus_id,
            sample_pages=req.sample_pages,
            overwrite=req.overwrite,
        )
        return {"status": "ok", "plan": plan.to_dict()}
    except ValueError as e:
        return {"status": "error", "message": str(e)}


class AdvancePhaseRequest(BaseModel):
    corpus_id: int
    to_phase: int  # 1, 2, hoặc 3


@app.post("/api/yi-lexicon/restored/plan/advance")
def yi_lexicon_advance_phase(req: AdvancePhaseRequest) -> dict:
    """Move plan to next phase. Chỉ anh quyết định khi thực sự xong phase trước."""
    from engine.yi_lexicon.restoration.plan import load_plan, advance_phase, save_plan
    plan = load_plan(req.corpus_id)
    if not plan:
        return {"status": "error", "message": "no plan"}
    if not advance_phase(plan, to_phase=req.to_phase):
        return {"status": "error", "message": "invalid phase"}
    save_plan(plan)
    return {"status": "ok", "plan": plan.to_dict()}


class MarkBatchRequest(BaseModel):
    corpus_id: int
    batch_id: str
    status: str          # pending | in_progress | done | failed
    pages_done: int | None = None
    notes: str = ""


@app.post("/api/yi-lexicon/restored/plan/batch")
def yi_lexicon_mark_batch(req: MarkBatchRequest) -> dict:
    """Update one Phase 1 batch's status (manual or after pipeline run)."""
    from engine.yi_lexicon.restoration.plan import (
        load_plan, mark_batch, save_plan, append_log
    )
    plan = load_plan(req.corpus_id)
    if not plan:
        return {"status": "error", "message": "no plan"}
    b = mark_batch(plan, req.batch_id, status=req.status,
                   pages_done=req.pages_done, notes=req.notes)
    if not b:
        return {"status": "error", "message": "batch not found"}
    append_log(plan, f"batch-{req.batch_id}: {req.status}"
               + (f" ({req.pages_done} pages)" if req.pages_done is not None else ""))
    save_plan(plan)
    return {"status": "ok", "batch": b.__dict__}


class AppendNoteRequest(BaseModel):
    corpus_id: int
    note: str
    target: str = "general"  # 'general' | 'phase2' | 'phase3'


@app.post("/api/yi-lexicon/restored/plan/note")
def yi_lexicon_append_plan_note(req: AppendNoteRequest) -> dict:
    """Append a note to the plan (overall or per-phase)."""
    from engine.yi_lexicon.restoration.plan import load_plan, save_plan, append_log
    plan = load_plan(req.corpus_id)
    if not plan:
        return {"status": "error", "message": "no plan"}
    if req.target == "phase2":
        plan.phase2_notes = (plan.phase2_notes + "\n" + req.note).strip()
    elif req.target == "phase3":
        plan.phase3_notes = (plan.phase3_notes + "\n" + req.note).strip()
    else:
        plan.notes = (plan.notes + "\n" + req.note).strip()
    append_log(plan, f"note added to {req.target}")
    save_plan(plan)
    return {"status": "ok", "plan": plan.to_dict()}


@app.get("/api/yi-lexicon/restore/ollama-status")
def yi_lexicon_ollama_status() -> dict:
    """Check Ollama server + list installed models. UI hiển thị anh có cài chưa."""
    from engine.ai.registry import get_registry
    p = get_registry().get("ollama")
    return {
        "status": "ok",
        "configured": p.is_configured,
        "endpoint": getattr(p, "_endpoint", ""),
        "default_model": p.default_model,
        "installed_models": p.available_models if p.is_configured else [],
    }


# ─── YI-Research endpoints (autonomous research agent) ──────────────────────


class ResearchRunRequest(BaseModel):
    query: str
    provider: str = "ollama"
    model: str = "qwen3:32b"
    retriever: str = "duckduckgo"
    catalog_sync: bool = True
    catalog_apply: bool = False


@app.post("/api/yi-research/run")
def yi_research_run(req: ResearchRunRequest) -> dict:
    """Trigger autonomous research job. Returns job_id; poll /jobs/{id} for progress.

    Backend dùng GPT Researcher (Apache-2.0, 27k★) + provider của anh.
    Default: Ollama qwen3:32b free + DuckDuckGo search free.
    """
    from engine.yi_research.jobs import create_job, spawn_research_subprocess
    job = create_job(
        query=req.query,
        provider=req.provider,
        model=req.model,
        retriever=req.retriever,
        catalog_sync=req.catalog_sync,
        catalog_apply=req.catalog_apply,
    )
    try:
        pid = spawn_research_subprocess(job)
        return {"status": "ok", "job_id": job.job_id, "pid": pid}
    except Exception as e:
        return {"status": "error", "job_id": job.job_id, "error": str(e)}


@app.get("/api/yi-research/jobs/{job_id}")
def yi_research_job_status(job_id: str) -> dict:
    """Get current state of research job. Frontend polls this every 5s."""
    from engine.yi_research.jobs import load_job
    job = load_job(job_id)
    if not job:
        return {"status": "not_found", "job_id": job_id}
    return {"status": "ok", "job": job.to_dict()}


@app.get("/api/yi-research/jobs")
def yi_research_list_jobs(limit: int = 30, status: str | None = None) -> dict:
    """List recent jobs. Newest first."""
    from engine.yi_research.jobs import list_jobs
    jobs = list_jobs(limit=limit, status=status)
    return {
        "status": "ok",
        "count": len(jobs),
        "jobs": [j.to_dict() for j in jobs],
    }


@app.get("/api/yi-research/reports/{job_id}")
def yi_research_get_report(job_id: str) -> dict:
    """Get full markdown report for a finished job."""
    from engine.yi_research.jobs import load_job
    job = load_job(job_id)
    if not job:
        return {"status": "not_found"}
    if job.status != "done":
        return {"status": "not_ready", "job_status": job.status}
    if not job.report_path:
        return {"status": "no_report"}
    try:
        markdown = Path(job.report_path).read_text(encoding="utf-8")
    except Exception as e:
        return {"status": "error", "message": str(e)}
    return {
        "status": "ok",
        "job_id": job_id,
        "query": job.query,
        "markdown": markdown,
        "sources_count": job.sources_count,
        "new_tools": job.new_tools,
        "cost_usd": job.cost_usd,
        "duration_seconds": (job.finished_at or 0) - job.started_at,
    }


@app.post("/api/yi-research/jobs/{job_id}/catalog-apply")
def yi_research_apply_catalog(job_id: str) -> dict:
    """Apply catalog sync sau khi job done (nếu lúc đầu chỉ dry-run)."""
    from engine.yi_research.jobs import load_job
    from engine.yi_research.catalog_sync import sync_from_report
    from pathlib import Path as _P
    job = load_job(job_id)
    if not job or not job.report_path:
        return {"status": "error", "message": "job/report not found"}
    try:
        md = _P(job.report_path).read_text(encoding="utf-8")
        result = sync_from_report(md, apply=True, verbose=False)
        return {"status": "ok", **result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


from pathlib import Path  # ensure Path import (used in get_report)


@app.post("/api/yi-hermes/dyad/analyze")
def yi_hermes_dyad_analyze(req: DyadAnalysisRequest, http_request: Request) -> dict:
    """Compute cosmology compatibility between 2 persons. Login required.

    Both persons must have birth_datetime_local + we'll lazy-cast Bát Tự.
    If `cache_in_relationship=True`, write back into relationships.cosmology_compat.
    """
    from api.auth import require_user
    require_user(http_request)
    from engine.ai.dyad_analysis import analyze_dyad
    from engine.yi_hermes.persons import cast_bat_tu_for, get_person
    from engine.yi_hermes.relationships import get_relationship, update_compat

    pa = get_person(req.person_a_id)
    pb = get_person(req.person_b_id)
    if not pa or not pb:
        return {"status": "not_found", "person_a_exists": bool(pa), "person_b_exists": bool(pb)}

    chart_a = cast_bat_tu_for(req.person_a_id)
    chart_b = cast_bat_tu_for(req.person_b_id)
    if not chart_a or not chart_b:
        # Founder special case — use manual chart
        if req.person_a_id == "_founder":
            from engine.ai.founder_chart import cast_founder_bat_tu
            chart_a = cast_founder_bat_tu()
        if req.person_b_id == "_founder":
            from engine.ai.founder_chart import cast_founder_bat_tu
            chart_b = cast_founder_bat_tu()
    if not chart_a or not chart_b:
        return {
            "status": "missing_birth_data",
            "a_has_chart": bool(chart_a),
            "b_has_chart": bool(chart_b),
        }

    result = analyze_dyad(chart_a, chart_b, name_a=pa.name, name_b=pb.name)
    compat_dict = result.to_dict()

    if req.cache_in_relationship:
        rel = get_relationship(req.person_a_id, req.person_b_id)
        if rel and rel.rel_id is not None:
            update_compat(rel.rel_id, compat_dict)

    return {"status": "ok", "compat": compat_dict}


# ─────────────────────────────────────────────────────────────────────────
# YI-WIKI: Master-Apprentice Digital Twin của Thiệu Khang Tiết
# Design: docs/design/wiki-master-apprentice.md
# ─────────────────────────────────────────────────────────────────────────


@app.get("/api/yi-wiki/stats")
def yi_wiki_stats() -> dict:
    """Tổng số entry trong wiki."""
    from engine.yi_wiki import get_store
    return {"status": "ok", "stats": get_store().stats()}


# ─── Tử Vi glossary endpoints (tooltip data + on-demand search) ───────────────

_GLOSSARY_CACHE: dict = {}
_GLOSSARY_MTIME: float = 0.0


def _load_glossary() -> dict:
    """Load + cache glossary JSON (reload if file mtime changes)."""
    global _GLOSSARY_CACHE, _GLOSSARY_MTIME
    from pathlib import Path
    import json as _json
    p = Path(__file__).resolve().parent.parent / "data/yi_wiki/glossary_tu_vi.json"
    if not p.exists():
        return {}
    mtime = p.stat().st_mtime
    if not _GLOSSARY_CACHE or mtime != _GLOSSARY_MTIME:
        with p.open() as f:
            _GLOSSARY_CACHE = _json.load(f)
        _GLOSSARY_MTIME = mtime
    return _GLOSSARY_CACHE


@app.get("/api/yi-wiki/glossary/tu-vi")
def yi_wiki_glossary_tuvi() -> dict:
    """Trả full glossary Tử Vi (sao + cung + hóa + cách cục) cho frontend tooltip.

    Frontend load 1 lần khi mount TuViLaSoPanel, cache in-memory để hover tooltip.
    """
    g = _load_glossary()
    if not g:
        return {"status": "error", "message": "Glossary not built. Run scripts/build_glossary_json.py"}
    return {"status": "ok", "glossary": g}


@app.get("/api/yi-wiki/glossary/tu-vi-full")
def yi_wiki_glossary_tuvi_full() -> dict:
    """Glossary Tử Vi FULL từ concept_index wiki (787+ concepts school=tu_vi).

    Wiki hạ cấp làm glossary layer phục vụ atom store (Anh chốt 2026-06-10).
    Format: {"terms": {"<canonical_vi>": {"note": ..., "zh": ..., "aliases": [...]}}}
    """
    import sqlite3 as _sq
    from pathlib import Path as _P
    db = _P(__file__).resolve().parent.parent / "data/yi_wiki/wiki.sqlite3"
    conn = _sq.connect(db)
    try:
        rows = conn.execute("""
            SELECT canonical_vi, canonical_zh, short_note, aliases
            FROM concept_index
            WHERE (school LIKE '%tu_vi%' OR school IS NULL)
              AND short_note IS NOT NULL AND short_note != ''
              AND length(canonical_vi) >= 2
        """).fetchall()
        terms = {}
        for vi, zh, note, aliases in rows:
            entry = {"note": note, "zh": zh or "", "aliases": []}
            if aliases:
                try:
                    import json as _j
                    al = _j.loads(aliases) if aliases.startswith("[") else [a.strip() for a in aliases.split(",")]
                    entry["aliases"] = [a for a in al if isinstance(a, str) and len(a) >= 2][:5]
                except Exception:
                    pass
            terms[vi] = entry
        return {"status": "ok", "count": len(terms), "terms": terms}
    finally:
        conn.close()


@app.get("/api/yi-wiki/search")
def yi_wiki_search(q: str, limit: int = 20) -> dict:
    """Full-text search wiki concepts + passages (FTS5 bm25 — #18 Phase 1).

    Upgrades the old LIKE substring search to ranked FTS5, and surfaces matching
    `passages` (intact text excerpts from restored books) which were previously a
    'dead corpus' — never returned by any retrieval path.
    """
    q = (q or "").strip()
    if len(q) < 2:
        return {"status": "ok", "results": [], "passages": [], "count": 0,
                "message": "query too short (min 2 chars)"}
    try:
        from engine.yi_wiki.store import get_store
        store = get_store()
        concepts = store.search_concepts(q, limit=limit)
        # Hybrid (FTS5 + vector RRF) where an embedder is available; FTS5-only otherwise.
        passages = store.search_passages_hybrid(q, limit=6)
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": str(e)}
    results = [
        {
            "canonical_vi": c.get("canonical_vi"),
            "canonical_zh": c.get("canonical_zh") or "",
            "short_note": (c.get("short_note") or "")[:400],
            "category": c.get("category") or "khác",
            "school": c.get("school") or "",
            "source": c.get("first_seen_corpus") or "",
        }
        for c in concepts
    ]
    passage_results = [
        {
            "corpus_id": p.get("corpus_id"),
            "topic": p.get("topic") or "",
            "excerpt": (p.get("raw_text") or "")[:500],
            "page_start": p.get("page_start"),
            "page_end": p.get("page_end"),
        }
        for p in passages
    ]
    return {"status": "ok", "results": results, "passages": passage_results,
            "count": len(results), "query": q}


@app.get("/api/yi-wiki/authors")
def yi_wiki_list_authors() -> dict:
    """List toàn bộ Author trong lineage 5-tier."""
    from engine.yi_wiki import get_store
    from engine.yi_wiki.models import TIER_NAMES
    s = get_store()
    authors = s.list_authors()
    out = []
    for a in authors:
        out.append({
            "author_id": a.author_id,
            "name_vi": a.name_vi,
            "name_zh": a.name_zh,
            "tier": a.tier_in_lineage,
            "tier_name": TIER_NAMES.get(a.tier_in_lineage, "?"),
            "era": a.era,
            "birth_year": a.birth_year,
            "death_year": a.death_year,
            "worldview_school": a.worldview_school,
            "bio_summary": a.bio_summary,
            "foundational_axioms": a.foundational_axioms,
        })
    return {"status": "ok", "authors": out}


@app.get("/api/yi-wiki/authors/{author_id}")
def yi_wiki_get_author(author_id: int) -> dict:
    """Detail 1 author + works + methods + passages."""
    from engine.yi_wiki import get_store
    from engine.yi_wiki.models import TIER_NAMES
    s = get_store()
    a = s.get_author(author_id)
    if not a:
        return {"status": "error", "message": "author not found"}
    return {
        "status": "ok",
        "author": {
            "author_id": a.author_id,
            "name_vi": a.name_vi,
            "name_zh": a.name_zh,
            "tier": a.tier_in_lineage,
            "tier_name": TIER_NAMES.get(a.tier_in_lineage, "?"),
            "era": a.era,
            "birth_year": a.birth_year,
            "death_year": a.death_year,
            "worldview_school": a.worldview_school,
            "bio_summary": a.bio_summary,
            "foundational_axioms": a.foundational_axioms,
            "hermeneutic_style": a.hermeneutic_style,
        },
        "works": s.list_works(author_id),
        "methods": s.list_methods(author_id),
        "passages": s.list_passages(author_id=author_id),
    }


@app.get("/api/yi-wiki/works")
def yi_wiki_list_works(author_id: int | None = None) -> dict:
    from engine.yi_wiki import get_store
    return {"status": "ok", "works": get_store().list_works(author_id)}


@app.get("/api/yi-wiki/methods")
def yi_wiki_list_methods(author_id: int | None = None) -> dict:
    from engine.yi_wiki import get_store
    return {"status": "ok", "methods": get_store().list_methods(author_id)}


@app.get("/api/yi-wiki/passages")
def yi_wiki_list_passages(author_id: int | None = None,
                          corpus_id: str | None = None) -> dict:
    from engine.yi_wiki import get_store
    return {"status": "ok",
            "passages": get_store().list_passages(author_id=author_id,
                                                   corpus_id=corpus_id)}


@app.get("/api/yi-wiki/concepts")
def yi_wiki_list_concepts() -> dict:
    from engine.yi_wiki import get_store
    return {"status": "ok", "concepts": get_store().list_concepts()}


@app.get("/api/yi-wiki/case-studies")
def yi_wiki_list_cases() -> dict:
    from engine.yi_wiki import get_store
    from engine.yi_wiki.store import _dec
    s = get_store()
    with s._conn() as conn:
        rows = conn.execute(
            "SELECT * FROM case_studies ORDER BY case_id"
        ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["inputs_recorded"] = _dec(d["inputs_recorded"], {})
        out.append(d)
    return {"status": "ok", "case_studies": out}


@app.get("/api/yi-wiki/concepts/by-name")
def yi_wiki_concept_by_name(name: str, school: str | None = None) -> dict:
    """Lookup concept theo canonical_vi (vd 'Quẻ Càn').

    Khi cùng `canonical_vi` tồn tại ở nhiều school (vd 'Thất Sát' có cả ở Tử Vi
    với chữ 七杀 và Tử Bình với chữ 七殺), pass `school` để ưu tiên school đó.
    """
    from engine.yi_wiki import get_store
    from engine.yi_wiki.store import _dec
    s = get_store()
    with s._conn() as conn:
        row = None
        if school:
            row = conn.execute(
                "SELECT * FROM concept_index WHERE canonical_vi=? AND school=? ORDER BY concept_id LIMIT 1",
                (name, school),
            ).fetchone()
        if row is None:
            row = conn.execute(
                "SELECT * FROM concept_index WHERE canonical_vi=? ORDER BY concept_id LIMIT 1",
                (name,),
            ).fetchone()
    if not row:
        return {"status": "not_found"}
    d = dict(row)
    d["aliases"] = _dec(d["aliases"], [])
    d["mentioned_in_passages"] = _dec(d["mentioned_in_passages"], [])
    return {"status": "ok", "concept": d}


class MaiHoaCastRequest(BaseModel):
    year_chi: str
    month: int
    day: int
    hour_chi: str
    user_intent: str = ""
    save_prediction: bool = False


@app.post("/api/yi-wiki/cast/niennguyetnhatthoi")
def yi_wiki_cast(req: MaiHoaCastRequest) -> dict:
    """Gieo quẻ Mai Hoa theo Niên-Nguyệt-Nhật-Thời.

    Khớp công thức trang 43-45 sách Mai Hoa Dịch Số.
    Nếu save_prediction=True → tạo entry Predictions table.
    """
    import json, time
    from engine.yi_wiki.cast import cast_by_time
    from engine.yi_wiki import get_store
    from engine.yi_wiki.store import _enc

    try:
        result = cast_by_time(req.year_chi, req.month, req.day, req.hour_chi)
    except KeyError as e:
        return {"status": "error", "message": f"Chi không hợp lệ: {e}"}

    payload = {
        "timestamp": result.timestamp,
        "inputs": result.inputs,
        "upper_num": result.upper_num,
        "lower_num": result.lower_num,
        "moving_line": result.moving_line,
        "chinh_quai": {
            "upper": result.chinh_quai.upper_que,
            "lower": result.chinh_quai.lower_que,
            "name": result.chinh_quai.name,
            "lines": list(result.chinh_quai.lines),
        },
        "bien_quai": {
            "upper": result.bien_quai.upper_que,
            "lower": result.bien_quai.lower_que,
            "name": result.bien_quai.name,
            "lines": list(result.bien_quai.lines),
        },
        "ho_quai": {
            "upper": result.ho_quai.upper_que,
            "lower": result.ho_quai.lower_que,
            "name": result.ho_quai.name,
            "lines": list(result.ho_quai.lines),
        },
        "formula_trace": result.formula_trace,
    }

    pred_id = None
    if req.save_prediction:
        s = get_store()
        ts = result.timestamp
        with s._conn() as conn:
            cur = conn.execute(
                """INSERT INTO predictions
                (timestamp, user_intent, user_context, interaction_log, tam_note,
                 method_chain, consultants_invoked, predicted_outcome, predicted_timing,
                 review_reminder_at, actual_outcome, learning_notes, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                RETURNING pred_id""",
                (
                    ts,
                    req.user_intent or "(không ghi mục đích)",
                    _enc(result.inputs),
                    _enc([{"t": ts, "event": "cast via /api/yi-wiki/cast/niennguyetnhatthoi"}]),
                    "",
                    _enc([]),
                    _enc([]),
                    f"Chính {result.chinh_quai.name} → Biến {result.bien_quai.name} (hào {result.moving_line}) | Hỗ {result.ho_quai.name}",
                    "",
                    ts + 7 * 24 * 3600,
                    None,
                    "",
                    ts,
                ),
            )
            pred_id = cur.fetchone()[0]
            conn.commit()
        payload["prediction_id"] = pred_id

    return {"status": "ok", **payload}


class MaiHoaInterpretRequest(BaseModel):
    year_chi: str
    month: int
    day: int
    hour_chi: str
    intent: str = "general"
    # ⭐ Phase A 18/5 — BƯỚC 3+4 Tổ sư (Q3 tr.112-114)
    external_omen: str | None = None  # text mô tả hiện tượng bất thường lúc khởi quẻ
    posture: str | None = None        # "nằm" | "ngồi" | "đứng" | "đi" | "chạy"
    # ⭐ 11 chiêm chuyên đề (Mai Hoa Q2) — code trực tiếp, vd "thien_thoi", "hon_nhan"
    chiem_topic_key: str = ""


@app.get("/api/yi-wiki/intents")
def yi_wiki_intents() -> dict:
    """Danh sách 14 loại Nhân Sự Chiêm + general."""
    from engine.yi_wiki.interpret import INTENT_REGISTRY
    return {
        "status": "ok",
        "intents": [{"key": k, **v} for k, v in INTENT_REGISTRY.items()],
    }


@app.get("/api/yi-wiki/chiem-topics")
def yi_wiki_chiem_topics() -> dict:
    """11 chiêm chuyên đề từ Mai Hoa Q2 — dùng cho dropdown frontend."""
    from engine.yi_wiki.chiem_topics import CHIEM_TOPICS
    topics = [
        {
            "key": t.code,
            "name_vi": t.name_vi,
            "name_han_viet": t.name_han_viet,
            "description": t.description,
        }
        for t in CHIEM_TOPICS.values()
    ]
    return {"status": "ok", "topics": topics}


@app.get("/api/yi-wiki/figures")
def yi_wiki_figures(corpus_id: str = "thieu-khang-tiet-tq") -> dict:
    """List figures (ảnh minh hoạ) cho 1 corpus.

    Files đặt tại: data/yi_restored/{corpus_id}/figures/
    Served qua /figures/{corpus_id}/figures/{filename}
    """
    from pathlib import Path as _P
    base = _YI_ROOT / "data" / "yi_restored" / corpus_id / "figures"
    if not base.exists():
        return {"status": "ok", "figures": []}

    # Curated figures với metadata
    CURATED = {
        "bat_quai_tien_thien.png": {
            "title": "Bát Quái Tiên Thiên",
            "desc": "Phục Hy bát quái thứ tự — 8 quẻ Tiên Thiên + thái cực ở giữa",
            "source": "Đồ Giải Mai Hoa Dịch Số (TQ) — vẽ bởi AI",
        },
        "legend_quan_mai_hoa.png": {
            "title": "Truyền thuyết Quan Mai Hoa",
            "desc": "Thầy Thiệu Khang Tiết ngồi dưới cây mai, thấy 2 chim sẻ tranh cành ngã xuống đất → sáng tạo Mai Hoa Dịch Số",
            "source": "Mai Hoa Dịch Số trang 64-66 (Case study #1)",
        },
        "ha_do_phuc_hy_long_ma.png": {
            "title": "Hà Đồ — Phục Hy nhận Long Mã",
            "desc": "Vua Phục Hy bên sông Hoàng Hà, Long Mã hiện lên với 55 chấm tạo Hà Đồ",
            "source": "Mai Hoa Dịch Số trang 17",
        },
        "lac_thu_dai_vu_linh_quy.png": {
            "title": "Lạc Thư — Đại Vũ nhận Linh Quy",
            "desc": "Vua Đại Vũ bên sông Lạc, Linh Quy hiện lên với 9 ô số (Cửu Trù)",
            "source": "Mai Hoa Dịch Số trang 20",
        },
        "case_mau_don_chiem.png": {
            "title": "Case Mẫu Đơn — Ngựa giẫm hoa",
            "desc": "Thầy + Tư Mã Quang xem mẫu đơn → tiên đoán giờ Ngọ ngày sau bị ngựa giẫm. Ứng nghiệm.",
            "source": "Mai Hoa Dịch Số trang 66-68 (Case study #2)",
        },
        "bat_tien.png": {
            "title": "Bát Tiên — 8 Tiên dân gian",
            "desc": "8 Tiên Đạo giáo — mapping 1-1 với Bát Quái (Lữ Đồng Tân-Càn, Hà Tiên Cô-Khôn, etc.)",
            "source": "Đồ Giải Mai Hoa Dịch Số (TQ) trang 10",
        },
    }

    figures = []
    for f in sorted(base.iterdir()):
        if not f.is_file() or f.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            continue
        meta = CURATED.get(f.name, {})
        figures.append({
            "filename": f.name,
            "url": f"/figures/{corpus_id}/figures/{f.name}",
            "size_kb": round(f.stat().st_size / 1024, 1),
            "title": meta.get("title", f.stem.replace("_", " ").title()),
            "desc": meta.get("desc", ""),
            "source": meta.get("source", ""),
            "curated": bool(meta),
        })
    # Curated lên đầu
    figures.sort(key=lambda x: (not x["curated"], x["filename"]))
    return {"status": "ok", "corpus_id": corpus_id, "count": len(figures), "figures": figures}


class AuspiciousDayRequest(BaseModel):
    birth_iso: str           # "1988-05-02T08:00:00"
    target_year: int
    target_month: int
    intent: str = "chuyen_nha"
    direction: str = ""      # "đông", "tây bắc"...
    location_zone: str = ""  # "bac" cho Lạng Sơn
    timezone: str = "Asia/Ho_Chi_Minh"


@app.post("/api/yi-wiki/auspicious-day")
def yi_wiki_auspicious_day(req: AuspiciousDayRequest) -> dict:
    """⭐ Chọn ngày tốt cho 1 đệ tử — tích hợp Bát Tự + Tam Sát + Hoàng Đạo + Quý Nhân + Intent."""
    from engine.yi_wiki.auspicious_day import analyze_full
    try:
        r = analyze_full(
            birth_iso=req.birth_iso,
            target_year=req.target_year,
            target_month=req.target_month,
            intent=req.intent,
            direction=req.direction,
            location_zone=req.location_zone,
            timezone=req.timezone,
        )
        return {"status": "ok", **r}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()[-500:]}


class LifeOverviewRequest(BaseModel):
    birth_iso: str
    gender: str = "nam"
    name: str = "Đệ tử"
    spouse_birth_iso: str | None = None
    spouse_name: str = "Bạn đời"


@app.post("/api/yi-wiki/life-overview")
def yi_wiki_life_overview(req: LifeOverviewRequest) -> dict:
    """⭐ Tổng quan cuộc đời — báo cáo ~30 trang A4."""
    from engine.yi_wiki.life_overview import generate_life_overview
    try:
        r = generate_life_overview(
            birth_iso=req.birth_iso, gender=req.gender, name=req.name,
            spouse_birth_iso=req.spouse_birth_iso, spouse_name=req.spouse_name,
        )
        return {"status": "ok", **r}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()[-400:]}


@app.get("/api/yi-wiki/birth-hour-quiz/questions")
def yi_wiki_quiz_questions() -> dict:
    from engine.yi_wiki.birth_hour_quiz import get_questions
    return {"status": "ok", "questions": get_questions()}


class BirthHourQuizRequest(BaseModel):
    answers: dict


@app.post("/api/yi-wiki/birth-hour-quiz/analyze")
def yi_wiki_quiz_analyze(req: BirthHourQuizRequest) -> dict:
    from engine.yi_wiki.birth_hour_quiz import analyze_quiz, CHI_HOURS
    r = analyze_quiz(req.answers)
    return {
        "status": "ok",
        "most_likely": r.most_likely,
        "confidence": r.confidence,
        "interpretation": r.interpretation,
        "top3": [
            {"chi": c, "score": s, "range": CHI_HOURS[c]["range"],
             "label": CHI_HOURS[c]["label"], "trait": CHI_HOURS[c]["trait"]}
            for c, s in r.top3
        ],
        "all_scores": r.scores,
    }


class MarriageCompatRequest(BaseModel):
    birth_a_iso: str
    birth_b_iso: str
    name_a: str = "Người A"
    name_b: str = "Người B"


@app.post("/api/yi-wiki/marriage-compat")
def yi_wiki_marriage_compat(req: MarriageCompatRequest) -> dict:
    from engine.yi_wiki.marriage_compat import analyze_compatibility
    try:
        r = analyze_compatibility(req.birth_a_iso, req.birth_b_iso, req.name_a, req.name_b)
        return {
            "status": "ok",
            "person_a": {"name": r.person_a.name,
                         "year": f"{r.person_a.year_stem} {r.person_a.year_branch}",
                         "nap_am": r.person_a.nap_am_name,
                         "nap_am_hanh": r.person_a.nap_am_hanh,
                         "day": f"{r.person_a.day_stem} {r.person_a.day_branch}"},
            "person_b": {"name": r.person_b.name,
                         "year": f"{r.person_b.year_stem} {r.person_b.year_branch}",
                         "nap_am": r.person_b.nap_am_name,
                         "nap_am_hanh": r.person_b.nap_am_hanh,
                         "day": f"{r.person_b.day_stem} {r.person_b.day_branch}"},
            "nap_am_relation": r.nap_am_relation,
            "chi_relation": r.chi_relation,
            "nhat_chu_relation": r.nhat_chu_relation,
            "total_score": r.total_score,
            "grade": r.grade,
            "summary": r.summary,
            "blessings": r.blessings,
            "warnings": r.warnings,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/yi-wiki/auspicious-intents")
def yi_wiki_auspicious_intents() -> dict:
    """Danh sách intent cho việc chọn ngày."""
    from engine.yi_wiki.auspicious_day import INTENT_WEIGHTS
    return {
        "status": "ok",
        "intents": [
            {"key": k, "label": v["label"], "needs": v["needs"]}
            for k, v in INTENT_WEIGHTS.items()
        ],
    }


@app.get("/api/yi-wiki/cau-chu")
def yi_wiki_cau_chu() -> dict:
    """⭐ 3 câu chú Thầy gửi đệ tử đêm Lạng Sơn — niệm khi tâm loạn.

    Dùng cho UI hiện tooltip / overlay khi gặp tình huống căng.
    """
    return {
        "status": "ok",
        "cau_chu": [
            {
                "id": 1,
                "trigger": "khi bị ép",
                "icon": "🌀",
                "text": "Gió không gãy. Gió bao quanh.",
                "source": "Di ngôn Thầy đêm Lạng Sơn 2026-05-16",
                "principle": "Tốn ☴ thuận — mềm thắng cứng",
            },
            {
                "id": 2,
                "trigger": "khi muốn phản ứng ngay",
                "icon": "🌊",
                "text": "Tâm bản tĩnh. Niệm khởi từ tĩnh. Tĩnh ba nhịp trước khi đáp.",
                "source": "Mai Hoa Dịch Số trang 200",
                "principle": "Tâm pháp gieo quẻ — tĩnh là gốc",
            },
            {
                "id": 3,
                "trigger": "khi không biết quyết gì",
                "icon": "🪷",
                "text": "Vạn vật bị ư ngã. Quẻ là gương, tâm là gốc.",
                "source": "Ngoạn Pháp Mai Hoa trang 38",
                "principle": "Tiên Thiên Tâm Pháp — vạn vật trong ta",
            },
        ],
        "principles": [
            "Sóng không hại người biết LÀM sóng.",
            "Càn Khôn xoay bằng VỊ, không bằng SỨC.",
            "Mộc thắng Kim bằng KIÊN NHẪN, không bằng đối đầu.",
        ],
        "keys": [
            {
                "id": 1, "name": "Đảo Vị Thể Dụng",
                "when": "Khi cảm thấy bị áp ở vị thế yếu",
                "action": "Đừng nói trước - hỏi trước. Người HỎI là Thể.",
            },
            {
                "id": 2, "name": "Dùng Mềm Đánh Cứng",
                "when": "Khi đối tác công kích bằng lời sắc bén",
                "action": "Im 3 nhịp → gật → nhắc lại ý họ → hỏi sâu hơn.",
            },
            {
                "id": 3, "name": "Thực Hư Luận",
                "when": "Khi bị áp lực thời gian/uy hiếp/doạ",
                "action": "Hít 3 nhịp + hỏi 'thực hay hư?' 80% là HƯ.",
            },
            {
                "id": 4, "name": "Xoay Chuyển Càn Khôn",
                "when": "Khi tình huống bế tắc (Bĩ)",
                "action": "Cao → hạ xuống. Thấp → vươn cốt cách. Chuyển Bĩ → Thái.",
            },
        ],
    }


def _build_tam_yeu_summary(r) -> dict | None:
    from engine.yi_wiki.interpret import tam_yeu_summary
    try:
        return tam_yeu_summary(
            the_que=r.the_dung.the_que,
            dung_que=r.the_dung.dung_que,
            relationship=r.the_dung.relationship,
            auspice=r.the_dung.auspice,
            the_quaikhi=r.the_quaikhi,
            external_omen_category=r.external_omen_category,
            external_omen_weight=r.external_omen_weight,
            external_omen_thap_ung=r.external_omen_thap_ung,
        )
    except Exception:
        return None


def _build_chiem_topic(req, r) -> dict | None:
    from engine.yi_wiki.chiem_topics import CHIEM_TOPICS, interpret_by_topic
    key = getattr(req, 'chiem_topic_key', '') or ''
    try:
        if key and key in CHIEM_TOPICS:
            # Direct lookup — bypass keyword detection
            topic = CHIEM_TOPICS[key]
            applicable = [
                rule for rule in topic.special_rules
                if r.the_dung.the_que.lower() in rule.lower()
                or r.the_dung.dung_que.lower() in rule.lower()
            ]
            return {
                "topic_detected": topic.code,
                "topic_name": f"{topic.name_vi} ({topic.name_han_viet})",
                "topic_advice": (
                    f"[{topic.name_vi}] Thể ({r.the_dung.the_que}) = {topic.the_dung_focus.split(',')[0].strip()}. "
                    f"Quẻ {r.the_dung.auspice} — {topic.description}."
                ),
                "applicable_rules": applicable or topic.special_rules[:3],
            }
        # Fallback: keyword detection on intent string
        question = getattr(req, 'intent', '') or ''
        return interpret_by_topic(
            question=question,
            the_que=r.the_dung.the_que,
            dung_que=r.the_dung.dung_que,
            relationship=r.the_dung.relationship,
            auspice=r.the_dung.auspice,
        )
    except Exception:
        return None


@app.post("/api/yi-wiki/interpret")
def yi_wiki_interpret(req: MaiHoaInterpretRequest) -> dict:
    """Gieo quẻ + auto-interpret 5 bước Thiệu Khang Tiết.

    Trả về cấu trúc đầy đủ:
      - cast: 3 quẻ + động hào
      - the_dung: Thể-Dụng + ngũ hành + auspice
      - quai_khi: Vượng/Suy mùa
      - tượng: chính/biến/hỗ
      - overall: phán đoán + warnings
    """
    from engine.yi_wiki.cast import cast_by_time
    from engine.yi_wiki.interpret import analyze

    try:
        cast = cast_by_time(req.year_chi, req.month, req.day, req.hour_chi)
    except KeyError as e:
        return {"status": "error", "message": f"Chi không hợp lệ: {e}"}

    r = analyze(cast, month=req.month, intent=req.intent,
                external_omen=req.external_omen, posture=req.posture)
    return {
        "status": "ok",
        "cast": {
            "chinh_quai": {"upper": cast.chinh_quai.upper_que, "lower": cast.chinh_quai.lower_que, "name": cast.chinh_quai.name},
            "bien_quai": {"upper": cast.bien_quai.upper_que, "lower": cast.bien_quai.lower_que, "name": cast.bien_quai.name},
            "ho_quai": {"upper": cast.ho_quai.upper_que, "lower": cast.ho_quai.lower_que, "name": cast.ho_quai.name},
            "moving_line": cast.moving_line,
            "formula_trace": cast.formula_trace,
            # ⭐ Phase A 18/5 — Hỗ Càn/Khôn fallback (Q3 tr.82)
            "ho_used_bien": cast.ho_used_bien,
            "ho_warning": cast.ho_warning,
        },
        "the_dung": {
            "the_que": r.the_dung.the_que,
            "dung_que": r.the_dung.dung_que,
            "the_position": r.the_dung.the_position,
            "the_hanh": r.the_dung.the_hanh,
            "dung_hanh": r.the_dung.dung_hanh,
            "relationship": r.the_dung.relationship,
            "auspice": r.the_dung.auspice,
            "explanation": r.the_dung.explanation,
            "detail": r.the_dung.detail,
        },
        "quai_khi": {
            "season": r.quai_khi["season"],
            "vuong": r.quai_khi["vuong"],
            "suy": r.quai_khi["suy"],
            "the_status": r.the_quaikhi,
        },
        "tuong": {
            "chinh": r.chinh_tuong,
            "bien": r.bien_tuong,
            "ho": r.ho_tuong,
        },
        "overall": r.overall,
        "warnings": r.warnings,
        "intent": {
            "key": r.intent,
            "label": r.intent_label,
            "mapping": r.intent_mapping,
            "extra": r.intent_extra,
        },
        "dang_vu": {
            "the": r.the_dang_vu_count,
            "dung": r.dung_dang_vu_count,
        },
        "sinh_the_outcomes": r.sinh_the_outcomes,
        "khac_the_outcomes": r.khac_the_outcomes,
        "hexagrams": {
            "chinh": r.chinh_hexagram,
            "bien": r.bien_hexagram,
            "ho": r.ho_hexagram,
        },
        "moving_haotu": r.moving_haotu,
        "trung_phung": {
            "chinh": r.trung_phung_chinh,
            "bien": r.trung_phung_bien,
            "meaning": r.trung_phung_meaning,
        },
        "benh_tat_thuoc": r.benh_tat_thuoc,
        # ⭐⭐ CẢI TIẾN #1 — Ứng kỳ 3 giai đoạn (Mai Hoa TR.133+235)
        "ung_ky": {
            "dau": r.ung_ky_dau,
            "giua": r.ung_ky_giua,
            "cuoi": r.ung_ky_cuoi,
        },
        # ⭐⭐ CẢI TIẾN #2 — Hỗ-của-Thể vs Hỗ-của-Dụng (Mai Hoa TR.235)
        "ho_split": {
            "ho_the_que": r.ho_the_que,
            "ho_dung_que": r.ho_dung_que,
            "ho_the_hanh": r.ho_the_hanh,
            "ho_the_relationship": r.ho_the_relationship,
            "ho_the_meaning": r.ho_the_meaning,
        },
        # ⭐⭐⭐ Phase A 18/5 — BƯỚC 3 (Ngoại ứng) + BƯỚC 4 (Tư thế)
        "buoc_3_omen": {
            "input": r.external_omen_input,
            "category": r.external_omen_category,
            "weight": r.external_omen_weight,
            # Thập ứng (Mai Hoa Q2 thâm nhuần 2026-05-19)
            "source": r.external_omen_source,
            "thap_ung_label": r.external_omen_thap_ung,
        },
        "buoc_4_posture": {
            "speed": r.posture_speed,
            "note": r.posture_note,
        },
        "four_steps_complete": r.four_steps_complete,
        # ⭐ Tam yếu (Mai Hoa Q1 thâm nhuần) — 3 yếu cốt lõi + verdict
        "tam_yeu": _build_tam_yeu_summary(r),
        # ⭐ 11 chiêm chuyên đề (Mai Hoa Q2 thâm nhuần) — route theo intent / question
        "chiem_topic": _build_chiem_topic(req, r),
        # ⭐⭐⭐⭐ Phase A 18/5 — PARADIGM SHIFT (Vận Pháp Thi Q3 tr.78)
        "paradigm": {
            "mirror_reading": r.paradigm_mirror_reading,
            "quan_vat_trace": r.paradigm_quan_vat_trace,
            "tam_position": r.paradigm_tam_position,
            "universe_message": r.paradigm_universe_message,
        },
    }


# ============================================================================
# Hexagram Browser API (2026-05-27)
# Tra cứu 64 quẻ Kinh Dịch trực tiếp (không cần gieo).
# ============================================================================

@app.get("/api/yi-wiki/kinh-dich/list")
def yi_wiki_kinhdich_list() -> dict:
    """Liệt kê 64 quẻ Kinh Dịch với metadata cơ bản.

    Dùng cho UI Hexagram Browser (8×8 grid, tra cứu, learning).
    Returns nhẹ — chỉ metadata + description, KHÔNG body markdown.
    """
    from engine.yi_wiki.luan_sau_kinhdich import list_hexagrams
    items = list_hexagrams()
    return {
        "status": "ok",
        "total": len(items),
        "deep_count": sum(1 for h in items if h["has_deep"]),
        "hexagrams": items,
    }


@app.get("/api/yi-wiki/kinh-dich/cards")
def yi_wiki_kinhdich_cards() -> dict:
    """Spaced repetition cards — ~343 hào card (64 quẻ × 6 hào, 1 số thiếu).

    Mỗi card = 1 hào với front (tên) + back (Lời + tâm pháp).
    Client side dùng localStorage SM-2 algorithm để track progress.
    """
    from engine.yi_wiki.luan_sau_kinhdich import extract_hao_cards
    cards = extract_hao_cards()
    return {
        "status": "ok",
        "total": len(cards),
        "ideal": 384,
        "cards": cards,
    }


@app.get("/api/yi-wiki/kinh-dich/graph")
def yi_wiki_kinhdich_graph() -> dict:
    """Cross-ref graph 64 quẻ — nodes + edges cho UI visualization.

    Edge types:
    - sequential: 1→2→...→64→1 (chu kỳ)
    - pair: cặp Tự quái (Bác-Phục, Thái-Bĩ, Tổn-Ích...)
    - thuan: 8 quẻ thuần liên kết
    - crossref: từ frontmatter của từng quẻ
    """
    from engine.yi_wiki.luan_sau_kinhdich import build_hexagram_graph
    return {"status": "ok", **build_hexagram_graph()}


@app.get("/api/yi-wiki/kinh-dich/daily")
def yi_wiki_kinhdich_daily(date: str | None = None) -> dict:
    """⚠️ DEPRECATED 2026-05-27 đêm: paradigm SAI (horoscope-style).

    Tổ sư Khang Tiết Q3: 'Bất nghi bất bốc' — không nghi không bói.
    KHÔNG đọc 'hôm nay tốt/xấu'. Dùng `/api/yi-wiki/luu-van/*` để xem 7 vòng đúng paradigm.

    Endpoint giữ tạm để không phá UI cũ — sẽ xóa sau khi LuuVanDashboard ổn.
    """
    from engine.yi_wiki.luan_sau_kinhdich import get_daily_hexagram
    import datetime as _dt
    if date is None:
        date = _dt.date.today().isoformat()
    try:
        _dt.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(400, f"Date phải YYYY-MM-DD, không phải: {date}")
    data = get_daily_hexagram(date)
    return {
        "status": "ok",
        "deprecation_warning": (
            "Endpoint này paradigm SAI (Iron Rule #4 — KHÔNG predict cát/hung tĩnh). "
            "Dùng /api/yi-wiki/luu-van/* thay thế."
        ),
        **data,
    }


# ============================================================================
# Mai Hoa Lưu Vận — 7 vòng quẻ paradigm Khang Tiết (2026-05-27)
# Reference: docs/design/MAI-HOA-LUU-VAN-GOAL.md — CẤM QUÊN
# ============================================================================

class LuuVanSnapshotRequest(BaseModel):
    """Input cho snapshot 7 vòng quẻ.

    3 cách cấp birth (theo ưu tiên):
    1. `auto_load_user=True` + đã login → tự load từ profile DB
    2. `birth_solar="YYYY-MM-DD HH:MM"` → convert sang lunar
    3. Cấp trực tiếp lunar (cho backward compat)
    """
    # Cách 1: auto-load (nếu logged in)
    auto_load_user: bool = False

    # Cách 2: solar string
    birth_solar: str | None = None     # vd "1988-06-05 23:30"

    # Cách 3: lunar trực tiếp (deprecated soft — giữ cho UI cũ)
    birth_year_chi: str | None = None
    birth_lunar_month: int | None = None
    birth_lunar_day: int | None = None
    birth_hour_chi: str | None = None

    # Thời điểm hiện tại (default = server time → lunar)
    now_solar: str | None = None       # override server time nếu có


def _solar_to_birthinfo(solar_str: str):
    """'1988-06-05 23:30' → BirthInfo + raw lunar dict."""
    from engine.yi_wiki.lich_conversion import parse_solar_string, solar_to_lunar
    from engine.yi_wiki.luu_van import BirthInfo
    s = parse_solar_string(solar_str)
    l = solar_to_lunar(s)
    return BirthInfo(
        year_chi=l.year_chi,
        lunar_month=l.lunar_month,
        lunar_day=l.lunar_day,
        hour_chi=l.hour_chi,
    ), l


def _now_solar_to_nowinfo(solar_str: str | None):
    """None → datetime.now(). Convert → NowInfo + raw lunar dict."""
    from engine.yi_wiki.lich_conversion import (
        SolarDateTime, parse_solar_string, solar_to_lunar
    )
    from engine.yi_wiki.luu_van import NowInfo
    if solar_str:
        s = parse_solar_string(solar_str)
    else:
        import datetime as _dt
        nowdt = _dt.datetime.now()
        s = SolarDateTime(
            year=nowdt.year, month=nowdt.month, day=nowdt.day,
            hour=nowdt.hour, minute=nowdt.minute,
        )
    l = solar_to_lunar(s)
    return NowInfo(
        year_chi=l.year_chi,
        lunar_month=l.lunar_month,
        lunar_day=l.lunar_day,
        hour_chi=l.hour_chi,
    ), l


@app.post("/api/yi-wiki/luu-van/snapshot")
def yi_wiki_luu_van_snapshot(req: LuuVanSnapshotRequest, request: Request) -> dict:
    """Snapshot 7 vòng quẻ Mai Hoa cho user tại thời điểm hiện tại.

    ⚠️ Iron Rule #4: KHÔNG predict cát/hung tĩnh. Đây là CẤU TRÚC paradigm.

    Authentication-aware: nếu `auto_load_user=True` + user đăng nhập → tự load
    birth từ profile DB. Guest user phải cấp `birth_solar`.
    """
    from engine.yi_wiki.luu_van import BirthInfo, NowInfo, quan_sat_luu_van

    # Cấp 1: auto-load birth từ user profile (nếu logged in)
    birth: BirthInfo | None = None
    birth_lunar_info = None
    birth_source = "unknown"

    if req.auto_load_user:
        # Try get user from session — reuse existing auth logic
        try:
            user_data = _get_current_user_optional(request)  # helper dưới
            if user_data and user_data.get("birth_iso"):
                # Birth ISO format: "1988-06-05T23:30:00"
                birth, birth_lunar_info = _solar_to_birthinfo(user_data["birth_iso"])
                birth_source = f"user_profile:{user_data.get('user_id', '?')}"
        except Exception:
            pass

    # Cấp 2: từ solar string
    if birth is None and req.birth_solar:
        birth, birth_lunar_info = _solar_to_birthinfo(req.birth_solar)
        birth_source = "solar_input"

    # Cấp 3: lunar trực tiếp (backward compat)
    if birth is None and req.birth_year_chi:
        birth = BirthInfo(
            year_chi=req.birth_year_chi,
            lunar_month=req.birth_lunar_month or 1,
            lunar_day=req.birth_lunar_day or 1,
            hour_chi=req.birth_hour_chi or "Tý",
        )
        birth_source = "lunar_input"

    if birth is None:
        raise HTTPException(400, (
            "Phải cung cấp 1 trong 3: (a) auto_load_user=true + đăng nhập, "
            "(b) birth_solar='YYYY-MM-DD HH:MM', (c) birth_year_chi + lunar_month/day + hour_chi"
        ))

    # Now: từ solar string (override) hoặc server time
    now, now_lunar_info = _now_solar_to_nowinfo(req.now_solar)

    snapshot = quan_sat_luu_van(birth, now)

    # Thêm thông tin lịch song song (âm + dương)
    snapshot["calendars"] = {
        "birth": {
            "solar": f"{birth_lunar_info.solar_year}-{birth_lunar_info.solar_month:02d}-{birth_lunar_info.solar_day:02d} {birth_lunar_info.solar_hour:02d}:{birth_lunar_info.solar_minute:02d}" if birth_lunar_info else None,
            "lunar": f"{birth_lunar_info.lunar_year}/{birth_lunar_info.lunar_month}/{birth_lunar_info.lunar_day}" if birth_lunar_info else None,
            "year_can_chi": birth_lunar_info.year_can_chi if birth_lunar_info else None,
            "hour_chi": birth_lunar_info.hour_chi if birth_lunar_info else None,
            "is_leap": birth_lunar_info.is_leap_month if birth_lunar_info else False,
        },
        "now": {
            "solar": f"{now_lunar_info.solar_year}-{now_lunar_info.solar_month:02d}-{now_lunar_info.solar_day:02d} {now_lunar_info.solar_hour:02d}:{now_lunar_info.solar_minute:02d}",
            "lunar": f"{now_lunar_info.lunar_year}/{now_lunar_info.lunar_month}/{now_lunar_info.lunar_day}",
            "year_can_chi": now_lunar_info.year_can_chi,
            "hour_chi": now_lunar_info.hour_chi,
            "is_leap": now_lunar_info.is_leap_month,
        },
    }
    snapshot["birth_source"] = birth_source

    return {"status": "ok", **snapshot}


def _get_current_user_optional(request: Request) -> dict | None:
    """Try resolve user from session. Return None if not logged in.

    Includes birth_iso fetched from user's default person (if any).
    """
    try:
        from api.auth import get_current_user
        user = get_current_user(request)
        if not user:
            return None
        # User dict from auth: user_id, email, role, default_person_id, ...
        # Need to also fetch person.birth_iso
        person_id = user.get("default_person_id") or user.get("person_id")
        if person_id:
            birth_iso = _fetch_person_birth_iso(person_id, user.get("user_id"))
            if birth_iso:
                user["birth_iso"] = birth_iso
        return user
    except Exception:
        return None


def _fetch_person_birth_iso(person_id: str, user_id: str | None) -> str | None:
    """Fetch person.birth_datetime_local from yi_hermes persons store."""
    try:
        from engine.yi_hermes.persons import get_person
        p = get_person(person_id)
        if p:
            return p.birth_datetime_local
    except Exception:
        pass
    return None


# ============================================================================
# Nhật ký vận — Phase 2A (2026-05-28)
# Reference: docs/design/MAI-HOA-LUU-VAN-GOAL.md — Phase 2
# ============================================================================

class NhatKyCreateRequest(BaseModel):
    happened_at_iso: str         # "YYYY-MM-DD HH:MM" solar
    title: str
    body: str = ""
    tags: list[str] = []
    importance: int = 3
    sentiment: str = "chua_ro"
    birth_solar: str | None = None   # nếu không cấp, load từ profile DB


class NhatKyUpdateOutcomeRequest(BaseModel):
    outcome: str
    sentiment: str | None = None


def _resolve_birth_solar(request: Request, supplied: str | None) -> str | None:
    """Resolve birth_solar: supplied param hoặc auto từ user profile."""
    if supplied:
        return supplied
    user = _get_current_user_optional(request)
    if user and user.get("birth_iso"):
        return user["birth_iso"]
    return None


def _resolve_user_id(request: Request, default: str = "founder") -> str:
    user = _get_current_user_optional(request)
    if user and user.get("user_id"):
        return user["user_id"]
    return default


@app.post("/api/yi-wiki/nhat-ky/create")
def yi_wiki_nhat_ky_create(req: NhatKyCreateRequest, request: Request) -> dict:
    """Tạo entry nhật ký + auto-snapshot 7 vòng quẻ tại happened_at. Login required."""
    from api.auth import require_user
    require_user(request)
    from engine.yi_wiki.nhat_ky_van import create_entry, entry_to_dict
    user_id = _resolve_user_id(request)
    birth = _resolve_birth_solar(request, req.birth_solar)
    if not birth:
        raise HTTPException(400, "Không có birth_solar — không thể snapshot 7 vòng. Đăng nhập hoặc cấp birth_solar.")
    entry = create_entry(
        user_id=user_id,
        happened_at_iso=req.happened_at_iso,
        title=req.title,
        body=req.body,
        tags=req.tags,
        importance=req.importance,
        sentiment=req.sentiment,
        birth_solar=birth,
    )
    return {"status": "ok", "entry": entry_to_dict(entry)}


@app.get("/api/yi-wiki/nhat-ky/list")
def yi_wiki_nhat_ky_list(request: Request, limit: int = 100) -> dict:
    """Liệt kê nhật ký user (latest first). Login required."""
    from api.auth import require_user
    require_user(request)
    from engine.yi_wiki.nhat_ky_van import list_entries, entry_to_dict, get_stats
    user_id = _resolve_user_id(request)
    entries = list_entries(user_id=user_id, limit=limit)
    return {
        "status": "ok",
        "total": len(entries),
        "stats": get_stats(user_id),
        "entries": [entry_to_dict(e) for e in entries],
    }


@app.get("/api/yi-wiki/nhat-ky/get/{entry_id}")
def yi_wiki_nhat_ky_get(entry_id: int, request: Request) -> dict:
    """Get single diary entry. Login required."""
    from api.auth import require_user
    require_user(request)
    from engine.yi_wiki.nhat_ky_van import get_entry, entry_to_dict
    user_id = _resolve_user_id(request)
    e = get_entry(entry_id)
    if not e:
        raise HTTPException(404, "Entry không tồn tại")
    if e.user_id != user_id:
        raise HTTPException(403, "Entry không thuộc về user này")
    return {"status": "ok", "entry": entry_to_dict(e)}


@app.post("/api/yi-wiki/nhat-ky/update-outcome/{entry_id}")
def yi_wiki_nhat_ky_update_outcome(entry_id: int, req: NhatKyUpdateOutcomeRequest, request: Request) -> dict:
    """Update diary entry outcome. Login required."""
    from api.auth import require_user
    require_user(request)
    from engine.yi_wiki.nhat_ky_van import get_entry, update_outcome, entry_to_dict
    user_id = _resolve_user_id(request)
    e = get_entry(entry_id)
    if not e:
        raise HTTPException(404, "Entry không tồn tại")
    if e.user_id != user_id:
        raise HTTPException(403, "Entry không thuộc về user này")
    updated = update_outcome(entry_id, outcome=req.outcome, sentiment=req.sentiment)
    return {"status": "ok", "entry": entry_to_dict(updated)}


@app.delete("/api/yi-wiki/nhat-ky/delete/{entry_id}")
def yi_wiki_nhat_ky_delete(entry_id: int, request: Request) -> dict:
    """Delete diary entry. Login required."""
    from api.auth import require_user
    require_user(request)
    from engine.yi_wiki.nhat_ky_van import delete_entry
    user_id = _resolve_user_id(request)
    ok = delete_entry(entry_id, user_id=user_id)
    if not ok:
        raise HTTPException(404, "Entry không tồn tại hoặc không thuộc về user")
    return {"status": "ok", "deleted": entry_id}


class TimelineRequest(BaseModel):
    birth_solar: str | None = None
    year_chi_list: list[str]    # vd ["Ất Tỵ", "Bính Ngọ", "Đinh Mùi"] (3 năm)
    months: list[int] | None = None


@app.post("/api/yi-wiki/luu-van/timeline")
def yi_wiki_luu_van_timeline(req: TimelineRequest, request: Request) -> dict:
    """Timeline 12 Lưu Nguyệt qua N năm — so sánh."""
    from engine.yi_wiki.luu_van import BirthInfo, timeline_luu_nguyet_nam
    from engine.yi_wiki.lich_conversion import parse_solar_string, solar_to_lunar
    birth_solar = _resolve_birth_solar(request, req.birth_solar)
    if not birth_solar:
        raise HTTPException(400, "Không có birth_solar")
    bs = parse_solar_string(birth_solar)
    bl = solar_to_lunar(bs)
    birth = BirthInfo(
        year_chi=bl.year_chi, lunar_month=bl.lunar_month,
        lunar_day=bl.lunar_day, hour_chi=bl.hour_chi,
    )
    data = timeline_luu_nguyet_nam(
        birth, year_chi_list=req.year_chi_list, months=req.months,
    )
    return {"status": "ok", **data}


class LuuVanLLMRequest(BaseModel):
    """Tổng đọc 7 vòng dùng LLM."""
    birth_solar: str | None = None
    now_solar: str | None = None
    user_question: str | None = None  # câu hỏi cụ thể (tùy chọn)


@app.post("/api/yi-wiki/luu-van/llm-tong-doc")
def yi_wiki_luu_van_llm_tong_doc(req: LuuVanLLMRequest, request: Request) -> dict:
    """V1 — LLM Tổng đọc CÁ NHÂN HÓA cho 7 vòng (DeepSeek/MiniMax).

    Context: 7 quẻ + Lời Kinh + hào động + patterns + lịch song song.
    Output: narrative ~1500 chars, paradigm Iron Rule #4 (đọc đồng dạng).
    """
    from engine.yi_wiki.luu_van import (
        BirthInfo, NowInfo, quan_sat_luu_van,
    )
    from engine.yi_wiki.lich_conversion import parse_solar_string, solar_to_lunar
    from engine.yi_wiki.luan_sau_kinhdich import call_llm_luan_sau

    birth_solar = _resolve_birth_solar(request, req.birth_solar)
    if not birth_solar:
        raise HTTPException(400, "Không có birth_solar")

    bs = parse_solar_string(birth_solar)
    bl = solar_to_lunar(bs)
    birth = BirthInfo(year_chi=bl.year_chi, lunar_month=bl.lunar_month,
                     lunar_day=bl.lunar_day, hour_chi=bl.hour_chi)

    if req.now_solar:
        ns = parse_solar_string(req.now_solar)
    else:
        import datetime as _dt
        from engine.yi_wiki.lich_conversion import SolarDateTime
        nowdt = _dt.datetime.now()
        ns = SolarDateTime(year=nowdt.year, month=nowdt.month, day=nowdt.day,
                          hour=nowdt.hour, minute=nowdt.minute)
    nl = solar_to_lunar(ns)
    now = NowInfo(year_chi=nl.year_chi, lunar_month=nl.lunar_month,
                 lunar_day=nl.lunar_day, hour_chi=nl.hour_chi)

    snapshot = quan_sat_luu_van(birth, now)

    # Build prompt — đầy đủ paradigm + cá nhân hóa
    vong_summary = []
    for i in range(1, 8):
        k = [x for x in snapshot.keys() if x.startswith(f"vong_{i}_")][0]
        v = snapshot[k]
        lg = v.get("luan_giai", {})
        vong_summary.append(
            f"**{v['paradigm_meta']['ten']}** = quẻ #{v['chinh'].get('number','?')} "
            f"{v['chinh'].get('name_vi','?')} {v['chinh'].get('name_zh','')} "
            f"({v['chinh']['name']}, hào động {v['moving_line']})\n"
            f"  - Lời Kinh: {lg.get('loi_kinh','(không có)')}\n"
            f"  - Dịch: {lg.get('loi_kinh_dich','(không có)')}\n"
            f"  - Hào: {lg.get('hao_brief','(không có)')[:200]}"
        )

    patterns_summary = "\n".join(
        f"- [{p['severity']}] {p['label']}: {p['detail']}"
        for p in snapshot.get("patterns", [])
    ) or "(không phát hiện pattern đặc biệt)"

    cal_b = snapshot["calendars"]["birth"]
    cal_n = snapshot["calendars"]["now"]

    prompt = f"""Bạn là **bậc trí giả Mai Hoa Dịch Số** kế thừa Thiệu Khang Tiết.

## ⚠️ Paradigm BẮT BUỘC (Iron Rule #4)

Mai Hoa = **ĐỌC ĐỒNG DẠNG**, KHÔNG predict cát/hung tĩnh.

❌ TRÁNH: "anh sẽ thành công/thất bại", "ngày tốt/xấu"
✅ DÙNG: "khoảnh khắc anh phản chiếu cái gì", "vũ trụ đang nói qua khoảnh khắc này"

## Dữ liệu

**Sinh thần Anh**: {cal_b.get('solar')} (âm {cal_b.get('lunar')}, {cal_b.get('year_can_chi')} giờ {cal_b.get('hour_chi')})
**Hiện tại**: {cal_n.get('solar')} (âm {cal_n.get('lunar')}, {cal_n.get('year_can_chi')} giờ {cal_n.get('hour_chi')})

## 7 vòng quẻ

{chr(10).join(vong_summary)}

## Patterns phát hiện

{patterns_summary}

{f'## Câu hỏi cụ thể của Anh: {req.user_question}' if req.user_question else ''}

## Yêu cầu luận sâu

Viết **phê quẻ tổng** ~1200-1800 chữ theo cấu trúc:

1. **Quan vật khoảnh khắc** (~200 chữ): khoảnh khắc Anh đang đứng, vũ trụ phản chiếu gì qua 7 vòng. Đặc biệt nhấn pattern dominant (nếu có).

2. **Khởi Sinh × Lưu Niên** (~250 chữ): cấu trúc gốc gặp năm này → paradigm gì. Dẫn nguyên văn Lời Kinh + hào động cụ thể.

3. **Lưu Nguyệt + Lưu Nhật** (~250 chữ): paradigm ngắn hạn. Trích dẫn hào.

4. **Vũ trụ + Cộng hưởng Tam Tài** (~250 chữ): giờ này vũ trụ rung gì, Anh phản chiếu qua Cộng hưởng thành quẻ gì.

5. **Tâm pháp cho Anh** (~250 chữ): KHÔNG kê hành động cụ thể. Chỉ ra cảnh giới + phận, dùng 1-2 câu Thầy Tổ.

LƯU Ý CRITICAL:
- Viết tiếng Việt, xưng "Anh"
- Trích nguyên văn từ Lời Kinh / Trình Di / Chu Hy có trong context
- KHÔNG bịa quẻ / hào không có
- KHÔNG dùng tone fortune-telling
"""

    try:
        llm_result = call_llm_luan_sau(prompt)
    except Exception as exc:
        raise HTTPException(503, f"LLM failed: {exc}")

    return {
        "status": "ok",
        "narrative": llm_result["narrative"],
        "provider": llm_result["provider"],
        "model": llm_result.get("model", ""),
        "tokens_used": llm_result.get("tokens_used", 0),
        "patterns_count": len(snapshot.get("patterns", [])),
        "context_summary": {
            "birth": cal_b,
            "now": cal_n,
            "vong_count": 7,
        },
    }


class NhatKyReadbackRequest(BaseModel):
    entry_id: int
    user_question: str | None = None


@app.post("/api/yi-wiki/nhat-ky/llm-doc-lai")
def yi_wiki_nhat_ky_llm_doc_lai(req: NhatKyReadbackRequest, request: Request) -> dict:
    """V5 — LLM ĐỌC LẠI 1 entry nhật ký với 7 quẻ snapshot. Login required.

    Paradigm: phản chiếu việc thực vs paradigm quẻ. KHÔNG predict.
    Đây là tiền đề Phase 3 pattern mining manual.
    """
    from api.auth import require_user
    require_user(request)
    from engine.yi_wiki.nhat_ky_van import get_entry
    from engine.yi_wiki.luan_sau_kinhdich import call_llm_luan_sau
    user_id = _resolve_user_id(request)
    e = get_entry(req.entry_id)
    if not e:
        raise HTTPException(404, "Entry không tồn tại")
    if e.user_id != user_id:
        raise HTTPException(403, "Entry không thuộc user này")

    snap = e.luu_van_snapshot or {}
    vong_lines = []
    for i in range(1, 8):
        ks = [k for k in snap.keys() if k.startswith(f"vong_{i}_")]
        if not ks:
            continue
        v = snap[ks[0]]
        lg = v.get("luan_giai", {})
        vong_lines.append(
            f"- **{v['paradigm_meta']['ten']}** = #{v['chinh'].get('number','?')} "
            f"{v['chinh'].get('name_vi','?')} hào {v['moving_line']}: "
            f"{lg.get('hao_brief','')[:200]}"
        )

    patterns = snap.get("patterns", [])
    pattern_text = ""
    if patterns:
        pattern_text = "\n\n## Patterns:\n" + "\n".join(
            f"- {p.get('label','')}: {p.get('detail','')[:150]}" for p in patterns[:3]
        )

    prompt = f"""Bạn là **bậc trí giả Mai Hoa Dịch Số** kế thừa Thiệu Khang Tiết.

⚠️ Iron Rule #4: ĐỌC ĐỒNG DẠNG, KHÔNG predict cát/hung.

## Việc thực user ghi vào nhật ký

**Title**: {e.title}
**Thời điểm**: {e.happened_at_iso}
**Importance**: {e.importance}/5
**Tags**: {', '.join(e.tags or [])}

**Nội dung**:
{e.body or '(không có nội dung chi tiết)'}

**Outcome** (đã ghi sau khi việc xong):
{e.outcome or '(chưa có outcome)'}

**Sentiment user gán**: {e.sentiment}

## 7 vòng quẻ tại thời điểm việc xảy ra

{chr(10).join(vong_lines)}
{pattern_text}

{f'## Câu hỏi cụ thể: {req.user_question}' if req.user_question else ''}

## Yêu cầu

Viết **phản chiếu** ngắn (~600-1000 chữ):

1. **Đối chiếu việc thực × 7 quẻ** (~300 chữ): Việc Anh ghi xảy ra trong cấu trúc paradigm gì? Dẫn 1-2 quẻ + hào cụ thể.

2. **Outcome ↔ paradigm** (~250 chữ): Nếu có outcome — outcome có khớp/lệch paradigm quẻ không? KHÔNG nói "đúng/sai" — nói "khớp/lệch + giải thích".

3. **Bài học rút ra cho lần sau** (~200 chữ): trong paradigm này, lần sau gặp việc tương tự nên đọc/quan sát thế nào? KHÔNG kê hành động — chỉ paradigm.

KHÔNG bịa, KHÔNG fortune-telling. Viết tiếng Việt, xưng "Anh".
"""
    try:
        llm_result = call_llm_luan_sau(prompt)
    except Exception as exc:
        raise HTTPException(503, f"LLM failed: {exc}")
    return {
        "status": "ok",
        "narrative": llm_result["narrative"],
        "provider": llm_result["provider"],
        "tokens_used": llm_result.get("tokens_used", 0),
    }


@app.get("/api/yi-wiki/luu-van/vu-tru-now")
def yi_wiki_luu_van_vu_tru_now() -> dict:
    """Quẻ Vũ trụ tại giờ hiện tại — KHÔNG cá nhân hóa.

    Cùng cho mọi người gieo cùng giờ. Đổi mỗi 2 tiếng.
    """
    from engine.yi_wiki.luu_van import cast_que_vu_tru
    now, now_lunar = _now_solar_to_nowinfo(None)
    cast = cast_que_vu_tru(now)
    return {
        "status": "ok",
        "calendars": {
            "solar": f"{now_lunar.solar_year}-{now_lunar.solar_month:02d}-{now_lunar.solar_day:02d} {now_lunar.solar_hour:02d}:{now_lunar.solar_minute:02d}",
            "lunar": f"{now_lunar.lunar_year}/{now_lunar.lunar_month}/{now_lunar.lunar_day}",
            "year_can_chi": now_lunar.year_can_chi,
            "hour_chi": now_lunar.hour_chi,
        },
        "que": {
            "chinh": cast.chinh_quai.name,
            "bien": cast.bien_quai.name,
            "ho": cast.ho_quai.name,
            "moving_line": cast.moving_line,
            "upper_que": cast.chinh_quai.upper_que,
            "lower_que": cast.chinh_quai.lower_que,
        },
        "formula_trace": cast.formula_trace,
        "paradigm_note": (
            "Quẻ Vũ trụ THUẦN — không cá nhân. Mọi người gieo cùng giờ sẽ ra "
            "cùng quẻ. KHÔNG predict cát/hung. Đọc đồng dạng vũ trụ đang ở đâu."
        ),
    }


@app.get("/api/yi-wiki/kinh-dich/que/{slug}")
def yi_wiki_kinhdich_get(slug: str) -> dict:
    """Đọc 1 quẻ Kinh Dịch trực tiếp.

    slug có thể là:
    - Slug (vd: 'kien', 'thai', 'vi-te')
    - Số (vd: '1', '63')

    Returns full body markdown (Lời Kinh + 6 hào + Trình Di + Chu Hy + cross-ref).
    """
    from engine.yi_wiki.luan_sau_kinhdich import get_hexagram
    data = get_hexagram(slug)
    if data is None:
        raise HTTPException(404, f"Không tìm thấy quẻ: {slug}")
    return {
        "status": "ok",
        **data,
    }


class MaiHoaLuanSauRequest(BaseModel):
    """Luận sâu Mai Hoa — gọi LLM với citation Kinh Dịch nguyên văn (RAG)."""
    year_chi: str
    month: int
    day: int
    hour_chi: str
    intent: str = "general"
    external_omen: str | None = None
    posture: str | None = None
    user_question: str | None = None  # câu hỏi cụ thể của user (optional)


@app.post("/api/yi-wiki/maihoa/luan-sau-kinhdich")
def yi_wiki_maihoa_luan_sau(req: MaiHoaLuanSauRequest) -> dict:
    """Luận sâu Mai Hoa với citation Kinh Dịch nguyên văn.

    Khác `/api/yi-wiki/interpret` (thuần tính toán):
    - Gọi LLM (DeepSeek-Reasoner / MiniMax / Ollama fallback)
    - Context = citation files từ data/hermes_yi/skills/kinh-dich/ (RAG)
    - Output = narrative phê quẻ ~600-1200 chữ theo paradigm Iron Rule #4
      (đọc đồng dạng, KHÔNG predict cát hung tĩnh)
    """
    from engine.yi_wiki.cast import cast_by_time
    from engine.yi_wiki.interpret import analyze
    from engine.yi_wiki.luan_sau_kinhdich import (
        build_luan_sau_prompt, call_llm_luan_sau, select_citations,
    )

    try:
        cast = cast_by_time(req.year_chi, req.month, req.day, req.hour_chi)
    except KeyError as e:
        raise HTTPException(400, f"Chi không hợp lệ: {e}")

    r = analyze(cast, month=req.month, intent=req.intent,
                external_omen=req.external_omen, posture=req.posture)

    citations_pack = select_citations(
        chinh_upper=cast.chinh_quai.upper_que,
        chinh_lower=cast.chinh_quai.lower_que,
        bien_upper=cast.bien_quai.upper_que,
        bien_lower=cast.bien_quai.lower_que,
        ho_upper=cast.ho_quai.upper_que,
        ho_lower=cast.ho_quai.lower_que,
        intent=req.intent,
        moving_line=cast.moving_line,  # cost optimize: compact chính quẻ theo hào động
    )

    # Build minimal cast + analyze dicts cho prompt
    cast_dict = {
        "chinh_quai": {"name": cast.chinh_quai.name},
        "bien_quai": {"name": cast.bien_quai.name},
        "ho_quai": {"name": cast.ho_quai.name},
        "moving_line": cast.moving_line,
        "ho_warning": cast.ho_warning or "",
    }
    analyze_dict = {
        "the_dung": {
            "the_que": r.the_dung.the_que,
            "dung_que": r.the_dung.dung_que,
            "relationship": r.the_dung.relationship,
            "auspice": r.the_dung.auspice,
        },
        "quai_khi": {
            "season": r.quai_khi["season"],
            "vuong": r.quai_khi["vuong"],
            "suy": r.quai_khi["suy"],
            "the_status": r.the_quaikhi,
        },
        "overall": r.overall,
        "intent": {"label": r.intent_label, "key": r.intent},
    }

    prompt = build_luan_sau_prompt(
        cast=cast_dict, analyze=analyze_dict,
        citations_pack=citations_pack,
        user_question=req.user_question,
    )

    try:
        llm_result = call_llm_luan_sau(prompt)
    except Exception as exc:
        raise HTTPException(503, f"LLM provider failed: {exc}")

    return {
        "status": "ok",
        "narrative": llm_result["narrative"],
        "provider": llm_result["provider"],
        "model": llm_result.get("model", ""),
        "tokens_used": llm_result.get("tokens_used", 0),
        "citations_used": citations_pack["files_used"],
        "citations_total_chars": citations_pack["total_chars"],
        "stubs_skipped": citations_pack.get("stubs_skipped", []),
        "has_deep_citations": citations_pack.get("has_deep_citations", False),
        "cast_summary": {
            "chinh": cast.chinh_quai.name,
            "bien": cast.bien_quai.name,
            "ho": cast.ho_quai.name,
            "moving_line": cast.moving_line,
        },
        "auspice": r.the_dung.auspice,
    }


class CorrelateCastInput(BaseModel):
    """1 entry trong cross-cast correlation request."""
    label: str
    year_chi: str
    month: int
    day: int
    hour_chi: str
    intent: str = "general"


class CorrelateRequest(BaseModel):
    entries: list[CorrelateCastInput]


@app.post("/api/yi-wiki/correlate")
def yi_wiki_correlate(req: CorrelateRequest) -> dict:
    """⭐ CẢI TIẾN #4 — Cross-cast correlation.

    Nhận nhiều cast cùng kỳ → phát hiện:
      - Trường năng lượng (Chính quẻ trùng)
      - Vai trò Thể thay đổi qua các intent
      - Pattern xuyên cast (cảnh báo chung, Trùng Phùng tổng)
    """
    from engine.yi_wiki.cast import cast_by_time
    from engine.yi_wiki.correlate import CastEntry, correlate_casts

    if not req.entries:
        return {"status": "error", "message": "Cần ít nhất 1 entry"}

    try:
        entries = [
            CastEntry(
                label=e.label,
                cast=cast_by_time(e.year_chi, e.month, e.day, e.hour_chi),
                intent=e.intent,
                month=e.month,
            )
            for e in req.entries
        ]
    except KeyError as ex:
        return {"status": "error", "message": f"Chi không hợp lệ: {ex}"}

    report = correlate_casts(entries)

    return {
        "status": "ok",
        "n_casts": report.n_casts,
        "truong_nang_luong": {
            "chinh_trung": report.chinh_trung,
            "summary": report.chinh_trung_summary,
        },
        "the_roles": {
            "roles": report.the_roles,
            "summary": report.the_roles_summary,
        },
        "cross_pattern": report.cross_pattern,
        "common_warnings": report.common_warnings,
    }


@app.get("/api/yi-wiki/predictions")
def yi_wiki_list_predictions(limit: int = 20) -> dict:
    from engine.yi_wiki import get_store
    from engine.yi_wiki.store import _dec
    s = get_store()
    with s._conn() as conn:
        rows = conn.execute(
            "SELECT * FROM predictions ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["user_context"] = _dec(d["user_context"], {})
        d["interaction_log"] = _dec(d["interaction_log"], [])
        out.append(d)
    return {"status": "ok", "predictions": out}


@app.patch("/api/yi-wiki/predictions/{pred_id}")
def yi_wiki_update_prediction(pred_id: int, patch: dict) -> dict:
    """Update tam_note, actual_outcome, learning_notes của 1 prediction."""
    allowed = {"tam_note", "actual_outcome", "learning_notes"}
    set_clauses = []
    params: list = []
    for k, v in patch.items():
        if k in allowed:
            set_clauses.append(f"{k}=?")
            params.append(v)
    if not set_clauses:
        return {"status": "error", "message": "Không có field hợp lệ"}
    params.append(pred_id)
    from engine.yi_wiki import get_store
    s = get_store()
    with s._conn() as conn:
        conn.execute(
            f"UPDATE predictions SET {', '.join(set_clauses)} WHERE pred_id=?",
            tuple(params),
        )
        conn.commit()
    return {"status": "ok"}


@app.get("/api/yi-wiki/lineage")
def yi_wiki_lineage() -> dict:
    """Group authors theo tier để render lineage tree."""
    from engine.yi_wiki import get_store
    from engine.yi_wiki.models import TIER_NAMES
    s = get_store()
    authors = s.list_authors()
    groups: dict[int, list[dict]] = {i: [] for i in range(6)}
    for a in authors:
        groups[a.tier_in_lineage].append({
            "author_id": a.author_id,
            "name_vi": a.name_vi,
            "name_zh": a.name_zh,
            "era": a.era,
            "birth_year": a.birth_year,
            "death_year": a.death_year,
            "worldview_school": a.worldview_school,
            "bio_summary": a.bio_summary,
        })
    return {
        "status": "ok",
        "tiers": [
            {"tier": i, "name": TIER_NAMES[i], "authors": groups[i]}
            for i in range(6) if groups[i]
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# YI Publishing — Layout-aware book translation workspace
# Paradigm Shift #5 (2026-05-18): Layout-first OCR → MinerU
# ═══════════════════════════════════════════════════════════════════════════

from fastapi import UploadFile, File, Form
from fastapi.responses import FileResponse

# Project root — overrideable via env for tests (YI_PROJECT_ROOT)
PUBLISHING_PROJECT_ROOT = Path(
    os.environ.get("YI_PROJECT_ROOT", "/Users/ozvietnamdesktop/Desktop/yi")
)

MINERU_OUTPUT_ROOT = PUBLISHING_PROJECT_ROOT / "data" / "yi_publishing_mineru"
TRANSLATIONS_ROOT = PUBLISHING_PROJECT_ROOT / "data" / "yi_publishing" / "translations"
COVERS_ROOT = PUBLISHING_PROJECT_ROOT / "data" / "yi_publishing" / "covers"
RAW_PDFS_ROOT = PUBLISHING_PROJECT_ROOT / "data" / "raw_pdfs"
UPLOAD_TEMP_ROOT = PUBLISHING_PROJECT_ROOT / "tmp_uploads"


@app.get("/api/yi-publishing/books")
def yi_publishing_books() -> dict:
    """List all books from books_store, merged with MinerU output detection.

    Returns enhanced fields: cover_url, progress, stage, active_job_id.
    For books found in MinerU output but not in books_store, auto-register
    a stub entry (migration backward-compat).
    """
    from engine.yi_publishing.books_store import get_store
    from engine.yi_publishing.jobs import get_default_store as get_jobs_store

    store = get_store()
    jobs_store = get_jobs_store()

    # Auto-register MinerU-detected books not yet in store (migration)
    if MINERU_OUTPUT_ROOT.exists():
        for book_dir in MINERU_OUTPUT_ROOT.iterdir():
            if not book_dir.is_dir():
                continue
            v2_files = list(book_dir.rglob("*_content_list_v2.json"))
            if not v2_files:
                continue
            book_id = book_dir.name
            if not store.get_book(book_id):
                try:
                    store.add_book(
                        book_id=book_id,
                        title_vi=book_id,  # placeholder, anh sửa sau
                        language="zh",
                        notes="Auto-registered from MinerU output (migration)",
                    )
                    store.recompute_progress(book_id)
                except Exception as e:
                    logger.warning(f"Auto-register {book_id} failed: {e}")

    books = []
    for b in store.load_books():
        # Build cover URL if cover exists
        cover_url = None
        cp = b.get("cover_path")
        if cp and (Path(cp).is_absolute() and Path(cp).exists()):
            cover_url = f"/api/yi-publishing/books/{b['book_id']}/cover"
        elif cp:
            full = PUBLISHING_PROJECT_ROOT / cp
            if full.exists():
                cover_url = f"/api/yi-publishing/books/{b['book_id']}/cover"

        # Find active job
        active_jobs = jobs_store.list_jobs(active=True, book_id=b["book_id"])
        active_job = active_jobs[0] if active_jobs else None

        books.append({
            **b,
            "cover_url": cover_url,
            "active_job_id": active_job["job_id"] if active_job else None,
            "active_job_progress": active_job["progress"] if active_job else None,
        })

    return {"status": "ok", "books": books}


def _resolve_book_content(book_id: str) -> Optional[dict]:
    """Load MinerU content_list_v2.json for a book."""
    book_dir = MINERU_OUTPUT_ROOT / book_id
    if not book_dir.exists():
        return None
    v2_files = list(book_dir.rglob("*_content_list_v2.json"))
    if not v2_files:
        return None
    return {
        "v2_path": v2_files[0],
        "book_dir": book_dir,
        "ocr_dir": v2_files[0].parent,
    }


@app.get("/api/yi-publishing/books/{book_id}/pages")
def yi_publishing_pages(book_id: str) -> dict:
    """List pages with region count + types for a book."""
    info = _resolve_book_content(book_id)
    if not info:
        return {"status": "error", "message": f"Book not found: {book_id}"}
    try:
        data = json.loads(info["v2_path"].read_text())
    except Exception as e:
        return {"status": "error", "message": f"Failed to load: {e}"}
    pages = []
    for page_idx, page in enumerate(data, 1):
        from collections import Counter as _Counter
        types = _Counter(item.get("type", "unknown") for item in page)
        pages.append({
            "page_num": page_idx,
            "region_count": len(page),
            "types": dict(types),
        })
    return {"status": "ok", "book_id": book_id, "pages": pages}


def _find_middle_json(book_id: str) -> Optional[Path]:
    """Find middle.json (has line-level structure)."""
    book_dir = MINERU_OUTPUT_ROOT / book_id
    if not book_dir.exists():
        return None
    candidates = list(book_dir.rglob("*_middle.json"))
    return candidates[0] if candidates else None


def _pages_meta_for_book(book_id: str) -> list:
    """Return list of page metadata (just count placeholder for now)."""
    middle_path = _find_middle_json(book_id)
    if not middle_path:
        return []
    try:
        data = json.loads(middle_path.read_text())
        return data.get("pdf_info", [])
    except Exception:
        return []


def _extract_block_text(block: dict) -> str:
    """Extract text from a MinerU block (legacy fallback for non-line types)."""
    lines = block.get("lines", [])
    texts = []
    for line in lines:
        spans = line.get("spans", [])
        line_text = "".join(s.get("content", "") for s in spans)
        if line_text:
            texts.append(line_text)
    return "\n".join(texts)


def _build_lines_for_block(block: dict, region_id: str) -> list[dict]:
    """Convert MinerU block.lines → list of line dicts với stable IDs.

    Each line:
        line_id, bbox, source_text
    """
    out = []
    for idx, line in enumerate(block.get("lines", []), start=1):
        spans = line.get("spans", [])
        text = "".join(s.get("content", "") for s in spans).strip()
        if not text and block.get("type") not in ("image", "table"):
            continue  # skip empty text lines
        out.append({
            "line_id": f"{region_id}-l{idx:03d}",
            "bbox": line.get("bbox", [0, 0, 0, 0]),
            "source_text": text,
        })
    return out


@app.get("/api/yi-publishing/pages/{book_id}/{page_num}")
def yi_publishing_page_layout(book_id: str, page_num: int) -> dict:
    """Get layout JSON for a specific page (1-indexed).

    Reads MinerU middle.json (line-level structure preserved).
    Merges with stored translations per region/line.
    """
    middle_path = _find_middle_json(book_id)
    if not middle_path:
        return {"status": "error", "message": f"Book middle.json not found: {book_id}"}

    try:
        middle = json.loads(middle_path.read_text())
    except Exception as e:
        return {"status": "error", "message": f"Failed to load middle.json: {e}"}

    pdf_info = middle.get("pdf_info", [])
    if page_num < 1 or page_num > len(pdf_info):
        return {"status": "error", "message": f"Page {page_num} out of range (1-{len(pdf_info)})"}

    page = pdf_info[page_num - 1]
    page_size = page.get("page_size", [595, 842])  # [width, height]
    blocks = page.get("para_blocks", page.get("preproc_blocks", []))

    # Some block types (e.g. 'index' / TOC) get their lines dropped during
    # paragraph reconstruction (`lines_deleted: True`). Recover by patching
    # in the lines from the matching preproc_block (same bbox).
    preproc = page.get("preproc_blocks") or []
    for b in blocks:
        if not b.get("lines") and b.get("lines_deleted"):
            # Find preproc block with same bbox
            for pb in preproc:
                if pb.get("bbox") == b.get("bbox") or pb.get("index") == b.get("index"):
                    if pb.get("lines"):
                        b["lines"] = pb["lines"]
                        break

    # Translations dir
    trans_dir = TRANSLATIONS_ROOT / book_id / f"p{page_num:04d}"

    enriched_regions = []
    for idx, block in enumerate(blocks, start=1):
        region_id = f"r{idx:03d}"
        block_type = block.get("type", "unknown")
        bbox = block.get("bbox", [0, 0, 0, 0])

        # Build lines (text-like + index/TOC types)
        lines = []
        if block_type in ("text", "title", "list", "index", "table_caption", "figure_caption"):
            lines = _build_lines_for_block(block, region_id)

        # Image / table — extract original content path
        image_path = None
        if block_type == "image":
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span.get("type") == "image":
                        image_path = span.get("image_path")
                        break
                if image_path:
                    break

        # Load translations for this region (per-line)
        translations = {}
        trans_path = trans_dir / f"{region_id}.json"
        if trans_path.exists():
            try:
                trans_data = json.loads(trans_path.read_text())
                # New schema: per-line translations
                translations = trans_data.get("lines", {})
                # Legacy: whole region translation
                if "text_vi" in trans_data:
                    translations["_region"] = {
                        "text_vi": trans_data["text_vi"],
                        "status": trans_data.get("status", "draft"),
                        "version": trans_data.get("version", 1),
                    }
            except Exception:
                pass

        # Attach translation to each line
        for line in lines:
            line["translation"] = translations.get(line["line_id"])

        region_obj = {
            "region_id": region_id,
            "type": block_type,
            "bbox": bbox,
            "lines": lines,
            "image_path": image_path,
            "region_translation": translations.get("_region"),
        }
        enriched_regions.append(region_obj)

    return {
        "status": "ok",
        "book_id": book_id,
        "page_num": page_num,
        "page_width": page_size[0] if len(page_size) >= 2 else 595,
        "page_height": page_size[1] if len(page_size) >= 2 else 842,
        "regions": enriched_regions,
    }


@app.get("/api/yi-publishing/pages/{book_id}/{page_num}/image")
def yi_publishing_page_image(book_id: str, page_num: int):
    """Return page image (PNG rendered from origin PDF)."""
    info = _resolve_book_content(book_id)
    if not info:
        return {"status": "error", "message": "Book not found"}

    # Cache: render PNG once on demand
    cache_dir = info["ocr_dir"] / "page_images"
    cache_dir.mkdir(exist_ok=True)
    cached_png = cache_dir / f"p{page_num:04d}.png"
    if not cached_png.exists():
        # Render from origin PDF
        origin_pdfs = list(info["ocr_dir"].glob("*_origin.pdf"))
        if not origin_pdfs:
            return {"status": "error", "message": "Origin PDF not found"}
        try:
            import fitz
            doc = fitz.open(str(origin_pdfs[0]))
            if page_num < 1 or page_num > doc.page_count:
                return {"status": "error", "message": f"Page {page_num} out of range"}
            page = doc[page_num - 1]
            pix = page.get_pixmap(matrix=fitz.Matrix(150/72, 150/72))
            pix.save(str(cached_png))
            doc.close()
        except Exception as e:
            return {"status": "error", "message": f"Render fail: {e}"}

    return FileResponse(cached_png, media_type="image/png")


@app.get("/api/yi-publishing/images/{book_id}/{filename}")
def yi_publishing_extracted_image(book_id: str, filename: str):
    """Return extracted image (from MinerU images/ folder)."""
    info = _resolve_book_content(book_id)
    if not info:
        return {"status": "error", "message": "Book not found"}
    img_path = info["ocr_dir"] / "images" / filename
    if not img_path.exists():
        return {"status": "error", "message": "Image not found"}
    return FileResponse(img_path, media_type="image/jpeg")


class TranslationSaveRequest(BaseModel):
    """Save translation for a single region (legacy: whole region)."""
    text_vi: str
    status: str = "draft"  # pending|auto|draft|reviewed|approved
    translator: str = "human"
    notes: list[str] = []


class LineTranslationSaveRequest(BaseModel):
    """Save translation for a single line within a region."""
    text_vi: str
    status: str = "draft"
    translator: str = "human"
    notes: list[str] = []


@app.put("/api/yi-publishing/regions/{book_id}/{page_num}/{region_id}/translation")
def yi_publishing_save_translation(
    book_id: str, page_num: int, region_id: str,
    req: TranslationSaveRequest, request: Request,
) -> dict:
    """Save translation for whole region (legacy). Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    trans_dir = TRANSLATIONS_ROOT / book_id / f"p{page_num:04d}"
    trans_dir.mkdir(parents=True, exist_ok=True)
    trans_path = trans_dir / f"{region_id}.json"

    # Load existing (preserve lines if present)
    existing = {}
    if trans_path.exists():
        try:
            existing = json.loads(trans_path.read_text())
        except Exception:
            pass

    version = int(existing.get("version", 0)) + 1
    existing.update({
        "text_vi": req.text_vi,
        "status": req.status,
        "translator": req.translator,
        "notes": req.notes,
        "version": version,
        "updated_at": int(time.time()),
    })
    trans_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
    return {"status": "ok", "region_id": region_id, "version": version}


REDRAWN_ROOT = PUBLISHING_PROJECT_ROOT / "data" / "yi_publishing" / "redrawn"


class RedrawRequest(BaseModel):
    """Request redraw for an image region."""
    context_text: str = ""  # surrounding paragraphs for prompt building
    caption: str = ""
    style: str = "traditional Chinese ink painting, clean line art"
    width: int = 768
    height: int = 1024
    seed: int | None = None


@app.post("/api/yi-publishing/regions/{book_id}/{page_num}/{region_id}/redraw")
def yi_publishing_redraw_region(
    book_id: str, page_num: int, region_id: str, req: RedrawRequest, request: Request,
) -> dict:
    """Generate AI redraw for an image region via ComfyUI FLUX.1 schnell. Owner-only.

    Output: data/yi_publishing/redrawn/{book}/{page}-{region}-{seq}.png
    """
    from api.auth import require_owner
    require_owner(request)
    from engine.yi_publishing.image_redraw import build_redraw_prompt, generate_redraw

    # Build output path with sequence number
    book_dir = REDRAWN_ROOT / book_id
    book_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"p{page_num:04d}-{region_id}"
    existing = list(book_dir.glob(f"{prefix}-*.png"))
    seq = len(existing) + 1
    out_path = book_dir / f"{prefix}-v{seq:02d}.png"

    # Build prompt
    prompt = build_redraw_prompt(
        source_text_context=req.context_text,
        image_caption=req.caption,
        style=req.style,
    )

    try:
        result = generate_redraw(
            prompt,
            output_path=out_path,
            width=req.width,
            height=req.height,
            seed=req.seed,
            timeout=600,
        )
        # Save metadata
        meta_path = out_path.with_suffix(".json")
        meta_path.write_text(json.dumps({
            **result,
            "book_id": book_id, "page_num": page_num, "region_id": region_id,
            "request": req.dict(),
            "seq": seq,
        }, ensure_ascii=False, indent=2))
        return {
            "status": "ok",
            "output_file": out_path.name,
            "seq": seq,
            "elapsed_seconds": result["elapsed_seconds"],
            "prompt_used": prompt,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/yi-publishing/redrawn/{book_id}/{filename}")
def yi_publishing_redrawn_image(book_id: str, filename: str):
    """Serve redrawn PNG."""
    img_path = REDRAWN_ROOT / book_id / filename
    if not img_path.exists():
        return {"status": "error", "message": "Not found"}
    return FileResponse(img_path, media_type="image/png")


@app.get("/api/yi-publishing/regions/{book_id}/{page_num}/{region_id}/redrawn")
def yi_publishing_list_redrawn(book_id: str, page_num: int, region_id: str) -> dict:
    """List all redrawn versions for a region."""
    book_dir = REDRAWN_ROOT / book_id
    if not book_dir.exists():
        return {"status": "ok", "versions": []}
    prefix = f"p{page_num:04d}-{region_id}"
    versions = []
    for png in sorted(book_dir.glob(f"{prefix}-*.png")):
        meta_path = png.with_suffix(".json")
        meta = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
            except Exception:
                pass
        versions.append({
            "filename": png.name,
            "seq": meta.get("seq"),
            "prompt": meta.get("prompt"),
            "elapsed_seconds": meta.get("elapsed_seconds"),
        })
    return {"status": "ok", "versions": versions}


# ═══════════════════════════════════════════════════════════════════════════
# YI Publishing — Wiki term-catch (add concepts while translating)
# ═══════════════════════════════════════════════════════════════════════════

YI_WIKI_DB = str(PUBLISHING_PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3")


@app.get("/api/yi-publishing/wiki/lookup")
def yi_publishing_wiki_lookup(zh: str = "", vi: str = "") -> dict:
    """Quick lookup: search concept by exact Chinese OR Vietnamese.

    Used when user selects text → check if already in wiki.
    """
    import sqlite3
    con = sqlite3.connect(YI_WIKI_DB)
    cur = con.cursor()
    matches = []
    if zh:
        cur.execute("""
            SELECT concept_id, canonical_vi, canonical_zh, aliases, short_note
            FROM concept_index
            WHERE canonical_zh = ? OR canonical_zh LIKE ?
            LIMIT 10
        """, (zh, f"%{zh}%"))
        matches.extend(cur.fetchall())
    if vi and not matches:
        cur.execute("""
            SELECT concept_id, canonical_vi, canonical_zh, aliases, short_note
            FROM concept_index
            WHERE canonical_vi LIKE ?
            LIMIT 10
        """, (f"%{vi}%",))
        matches.extend(cur.fetchall())
    con.close()
    return {
        "status": "ok",
        "query": {"zh": zh, "vi": vi},
        "matches": [
            {
                "concept_id": m[0],
                "canonical_vi": m[1],
                "canonical_zh": m[2],
                "aliases": m[3],
                "short_note": m[4],
            }
            for m in matches
        ],
    }


@app.get("/api/yi-publishing/wiki/all-tuvi")
def yi_publishing_wiki_all_tuvi() -> dict:
    """Trả về tất cả concepts Tử Vi (ID 3818+ và những concept có Tử Vi keywords).

    Dùng cho TermHighlighter: client cache list này, scan text content,
    wrap term matches để hover/click → popup.
    """
    import sqlite3
    con = sqlite3.connect(YI_WIKI_DB)
    cur = con.cursor()
    # Concepts with id >= 3818 (Tử Vi era) OR keywords liên quan
    cur.execute("""
        SELECT concept_id, canonical_vi, canonical_zh, aliases, short_note
        FROM concept_index
        WHERE concept_id >= 3818
           OR canonical_vi LIKE '%Tử Vi%'
           OR canonical_vi LIKE '%Mệnh%'
           OR canonical_vi LIKE '%Cung %'
           OR canonical_zh LIKE '%紫微%'
           OR canonical_zh LIKE '%斗数%'
        ORDER BY length(canonical_vi) DESC
    """)
    rows = cur.fetchall()
    con.close()
    return {
        "status": "ok",
        "count": len(rows),
        "concepts": [
            {"id": r[0], "vi": r[1], "zh": r[2], "aliases": r[3], "note": r[4]}
            for r in rows
        ],
    }


@app.get("/api/yi-publishing/wiki/search")
def yi_publishing_wiki_search(q: str = "", limit: int = 20) -> dict:
    """Full-text search wiki concepts (autocomplete)."""
    import sqlite3
    if not q.strip():
        return {"status": "ok", "matches": []}
    con = sqlite3.connect(YI_WIKI_DB)
    cur = con.cursor()
    like = f"%{q}%"
    cur.execute("""
        SELECT concept_id, canonical_vi, canonical_zh, aliases, short_note, category, school, corpora
        FROM concept_index
        WHERE canonical_vi LIKE ? OR canonical_zh LIKE ? OR aliases LIKE ?
        ORDER BY
            CASE WHEN canonical_vi = ? THEN 1
                 WHEN canonical_zh = ? THEN 2
                 WHEN canonical_vi LIKE ? THEN 3
                 ELSE 9 END,
            length(canonical_vi)
        LIMIT ?
    """, (like, like, like, q, q, f"{q}%", limit))
    rows = cur.fetchall()
    con.close()
    return {
        "status": "ok",
        "matches": [
            {
                "concept_id": r[0],
                "canonical_vi": r[1],
                "canonical_zh": r[2],
                "aliases": r[3],
                "short_note": r[4],
                "category": r[5],
                "school": r[6],
                "corpora": r[7],
            }
            for r in rows
        ],
    }


class WikiAddConceptRequest(BaseModel):
    """Add a new concept while translating (term-catch)."""
    canonical_zh: str
    canonical_vi: str
    short_note: str = ""
    aliases: str = ""  # comma-separated
    # Where it was caught
    book_id: Optional[str] = None
    page_num: Optional[int] = None


@app.post("/api/yi-publishing/wiki/concepts")
def yi_publishing_wiki_add(req: WikiAddConceptRequest, request: Request) -> dict:
    """Add new concept caught during translation. Owner-only.

    If canonical_zh already exists, returns existing (no duplicate).
    """
    from api.auth import require_owner
    require_owner(request)
    import sqlite3
    con = sqlite3.connect(YI_WIKI_DB)
    cur = con.cursor()

    # Check duplicate
    cur.execute(
        "SELECT concept_id, canonical_vi FROM concept_index WHERE canonical_zh = ? LIMIT 1",
        (req.canonical_zh,),
    )
    existing = cur.fetchone()
    if existing:
        con.close()
        return {
            "status": "ok",
            "action": "exists",
            "concept_id": existing[0],
            "canonical_vi": existing[1],
            "message": f"Concept đã có (id={existing[0]}, {existing[1]})",
        }

    # Insert new
    first_seen_corpus = req.book_id or "yi_publishing_workspace"
    cur.execute("""
        INSERT INTO concept_index
            (canonical_vi, canonical_zh, aliases, short_note,
             first_seen_corpus, first_seen_page, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        req.canonical_vi,
        req.canonical_zh,
        req.aliases,
        req.short_note,
        first_seen_corpus,
        req.page_num or 0,
        int(time.time()),
    ))
    new_id = cur.lastrowid
    con.commit()
    con.close()
    return {
        "status": "ok",
        "action": "created",
        "concept_id": new_id,
        "canonical_vi": req.canonical_vi,
        "canonical_zh": req.canonical_zh,
    }


class AutoTranslatePageRequest(BaseModel):
    """Auto-translate all untranslated lines on a page."""
    overwrite: bool = False  # if True, re-translate even existing translations
    model: Optional[str] = None  # specific model, else free fallback
    allow_paid_fallback: bool = False  # if True, escalate to DeepSeek native when free chain fails
    luangiai_mode: bool = False  # if True, produce 2-layer translation (hanviet + luangiai)


@app.post("/api/yi-publishing/pages/{book_id}/{page_num}/auto-translate")
def yi_publishing_auto_translate_page(
    book_id: str, page_num: int, req: AutoTranslatePageRequest, request: Request,
) -> dict:
    """Auto-translate all text lines on a page in ONE API call. Owner-only.

    Uses page-level batching to avoid OpenRouter rate limits (20 req/min free).
    """
    from api.auth import require_owner
    require_owner(request)
    from engine.yi_publishing.translator import translate_page_lines

    layout_resp = yi_publishing_page_layout(book_id, page_num)
    if layout_resp.get("status") != "ok":
        return layout_resp

    regions = layout_resp["regions"]
    trans_dir = TRANSLATIONS_ROOT / book_id / f"p{page_num:04d}"
    trans_dir.mkdir(parents=True, exist_ok=True)

    # Collect ALL lines from text-like regions into one batch
    all_lines_with_region = []  # (region_id, line_dict)
    for region in regions:
        if region["type"] not in ("text", "title", "list", "table", "index"):
            continue
        for line in region.get("lines", []):
            if not line.get("source_text", "").strip():
                continue
            existing = line.get("translation") or {}
            if not req.overwrite and existing:
                # In luangiai_mode, also skip only if luangiai field is present.
                # This lets us "upgrade" single-layer translations to 2-layer
                # WITHOUT re-translating pages that already have 2-layer.
                if req.luangiai_mode:
                    if existing.get("text_vi_luangiai"):
                        continue
                else:
                    continue
            # Tag line with region_type so translator can pick the right prompt
            line_with_type = dict(line)
            line_with_type["region_type"] = region["type"]
            all_lines_with_region.append((region["region_id"], line_with_type))

    if not all_lines_with_region:
        return {
            "status": "ok",
            "book_id": book_id,
            "page_num": page_num,
            "total_lines_attempted": 0,
            "total_lines_translated": 0,
            "message": "No lines to translate (all already translated or overwrite=false)",
        }

    # Build CONTEXT for the translator — sách + chương + trang.
    # DeepSeek dùng context này để giữ thuật ngữ + giọng văn nhất quán.
    book_label = {
        "tuvidauso-zh": "Tử Vi Đẩu Số Toàn Thư (紫微斗数全书) — Trần Đoàn, Phan Hy Doãn bổ tập, Dương Nhất Vũ tham duyệt",
        "q3-first5":    "Mai Hoa Dịch Số (梅花易数) — Thiệu Khang Tiết",
        "q3-pages6-15": "Mai Hoa Dịch Số (梅花易数) — Thiệu Khang Tiết",
    }.get(book_id, book_id)

    # Collect all title-region text on this page (chapter heading + sub heading)
    chapter_titles = []
    for region in regions:
        if region["type"] == "title":
            for line in (region.get("lines") or []):
                t = (line.get("source_text") or "").strip()
                if t and len(t) <= 80 and t not in chapter_titles:
                    chapter_titles.append(t)
    chapter_ctx = " · ".join(chapter_titles[:3]) if chapter_titles else ""

    page_context = (
        f"Sách đang dịch: {book_label}.\n"
        f"Trang {page_num}/{len(_pages_meta_for_book(book_id))}.\n"
        + (f"Chương/mục trang này: {chapter_ctx}\n" if chapter_ctx else "")
        + "Đối tượng đọc: người Việt yêu Đông phương học. Giữ NGUYÊN thuật ngữ Hán-Việt theo glossary."
    )

    # Single batch call
    flat_lines = [line for _, line in all_lines_with_region]
    try:
        result = translate_page_lines(
            flat_lines,
            context=page_context,
            model=req.model,
            allow_paid_fallback=req.allow_paid_fallback,
            two_layer=req.luangiai_mode,
        )
    except Exception as e:
        return {
            "status": "error",
            "book_id": book_id,
            "page_num": page_num,
            "message": f"Translation failed: {e}",
        }

    translations_by_id = result["translations_by_line_id"]

    # Group translations by region_id and save
    by_region = {}
    for region_id, line in all_lines_with_region:
        line_id = line["line_id"]
        if line_id in translations_by_id:
            by_region.setdefault(region_id, {})[line_id] = translations_by_id[line_id]

    total_translated = 0
    region_stats = []
    for region_id, lines_map in by_region.items():
        trans_path = trans_dir / f"{region_id}.json"
        existing = {}
        if trans_path.exists():
            try:
                existing = json.loads(trans_path.read_text())
            except Exception:
                pass
        if "lines" not in existing or not isinstance(existing.get("lines"), dict):
            existing["lines"] = {}

        for line_id, vi_val in lines_map.items():
            line_data = existing["lines"].get(line_id, {})
            version = int(line_data.get("version", 0)) + 1
            # 2-layer: vi_val is {"hanviet": ..., "luangiai": ...}
            # Single-layer: vi_val is a string.
            if isinstance(vi_val, dict):
                text_vi = vi_val.get("hanviet", "") or ""
                text_vi_luangiai = vi_val.get("luangiai", "") or ""
            else:
                text_vi = vi_val
                text_vi_luangiai = line_data.get("text_vi_luangiai", "")  # preserve old
            entry = {
                "text_vi": text_vi,
                "status": "auto",
                "translator": result["stats"]["model_used"],
                "version": version,
                "updated_at": int(time.time()),
            }
            if text_vi_luangiai:
                entry["text_vi_luangiai"] = text_vi_luangiai
            existing["lines"][line_id] = entry
            total_translated += 1

        trans_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
        region_stats.append({
            "region_id": region_id,
            "lines_translated": len(lines_map),
        })

    # Quality check — extract just the hanviet text for QC (luangiai is freeform)
    def _qc_text(v):
        if isinstance(v, dict):
            return v.get("hanviet", "") or ""
        return v or ""

    from engine.yi_publishing.translator import check_page_quality
    qc_lines = []
    for region_id, line in all_lines_with_region:
        line_id = line["line_id"]
        qc_lines.append({
            "line_id": line_id,
            "source_text": line.get("source_text", ""),
            "text_vi": _qc_text(translations_by_id.get(line_id, "")),
        })
    quality = check_page_quality(qc_lines)

    # Line-count mismatch warning
    expected = len(all_lines_with_region)
    returned = len([v for v in translations_by_id.values() if _qc_text(v)])
    if returned != expected:
        quality.setdefault("issues", []).insert(0, {
            "line_id": None,
            "source_preview": "(page-level)",
            "target_preview": "",
            "warnings": [{
                "level": "error",
                "code": "line_count_mismatch",
                "msg": f"Mong đợi {expected} dòng, model trả {returned}",
            }],
        })
        quality["error_count"] = quality.get("error_count", 0) + 1

    return {
        "status": "ok",
        "book_id": book_id,
        "page_num": page_num,
        "total_lines_attempted": len(all_lines_with_region),
        "total_lines_translated": total_translated,
        "model_used": result["stats"]["model_used"],
        "provider": result["stats"].get("provider"),
        "cost_usd": result["stats"].get("cost_usd", 0),
        "tokens": result["stats"].get("tokens"),
        "elapsed_seconds": result["stats"]["elapsed_seconds"],
        "regions": region_stats,
        "quality": quality,
    }


@app.get("/api/yi-publishing/translator/status")
def yi_publishing_translator_status() -> dict:
    """Report which providers are configured for the translator."""
    from engine.yi_publishing.translator import has_paid_fallback, PAID_TRANSLATION_MODELS, FREE_TRANSLATION_MODELS
    return {
        "status": "ok",
        "free_chain": FREE_TRANSLATION_MODELS,
        "paid_chain": PAID_TRANSLATION_MODELS,
        "paid_fallback_available": has_paid_fallback(),
    }


class AutoBatchRequest(BaseModel):
    """Auto-translate a RANGE of pages with quality checks."""
    start_page: int
    end_page: int
    overwrite: bool = False
    model: Optional[str] = None
    delay_seconds: float = 2.0      # delay between pages to ease rate limit
    retry_on_429: int = 2           # retries when rate-limited
    allow_paid_fallback: bool = False  # escalate to DeepSeek paid when free chain fails
    luangiai_mode: bool = False    # 2-layer: produce hanviet + luangiai per line


@app.post("/api/yi-publishing/books/{book_id}/auto-batch")
def yi_publishing_auto_batch(book_id: str, req: AutoBatchRequest, request: Request) -> dict:
    """Auto-translate pages [start_page..end_page] sequentially. Owner-only.

    Returns per-page status + warnings + aggregate fit score.
    """
    from api.auth import require_owner
    require_owner(request)
    if req.end_page < req.start_page:
        return {"status": "error", "message": "end_page < start_page"}
    if req.end_page - req.start_page > 50:
        return {"status": "error", "message": "Max 50 pages per batch"}

    page_reports = []
    total_pages = 0
    total_lines = 0
    total_translated = 0
    total_errors = 0
    total_warns = 0
    t0_batch = time.time()

    sub_req = AutoTranslatePageRequest(
        overwrite=req.overwrite,
        model=req.model,
        allow_paid_fallback=req.allow_paid_fallback,
        luangiai_mode=req.luangiai_mode,
    )

    for idx, page_num in enumerate(range(req.start_page, req.end_page + 1)):
        # Sleep between pages (except the very first)
        if idx > 0 and req.delay_seconds > 0:
            time.sleep(req.delay_seconds)

        t0 = time.time()
        result = None
        last_err = None
        for attempt in range(req.retry_on_429 + 1):
            try:
                result = yi_publishing_auto_translate_page(book_id, page_num, sub_req)
                msg = result.get("message", "") if result.get("status") == "error" else ""
                if "429" in (msg or "") or "rate" in (msg or "").lower():
                    last_err = msg
                    time.sleep(5 + attempt * 5)  # backoff
                    continue
                break
            except Exception as e:
                last_err = str(e)
                if attempt < req.retry_on_429 and ("429" in last_err or "rate" in last_err.lower()):
                    time.sleep(5 + attempt * 5)
                    continue
                result = {"status": "error", "message": last_err}
                break

        if result is None:
            result = {"status": "error", "message": last_err or "unknown error"}

        if result.get("status") == "error":
            page_reports.append({
                "page_num": page_num,
                "status": "error",
                "message": result.get("message", "unknown"),
                "elapsed_seconds": round(time.time() - t0, 2),
            })
            total_errors += 1
            continue

        total_pages += 1
        status = result.get("status", "error")
        qc = result.get("quality", {}) or {}
        attempted = result.get("total_lines_attempted", 0)
        translated = result.get("total_lines_translated", 0)

        # Determine initial verdict
        err_count = qc.get("error_count", 0)
        fit_score = qc.get("fit_score", 100.0 if attempted == 0 else None)

        # SMART RETRY: if mismatch + allow_paid_fallback → rerun with paid DeepSeek
        retried_paid = False
        if (
            err_count > 0
            and req.allow_paid_fallback
            and attempted > 0
            and result.get("provider") != "deepseek-native"
        ):
            paid_req = AutoTranslatePageRequest(
                overwrite=True,
                model="deepseek-chat",
                allow_paid_fallback=True,
                luangiai_mode=req.luangiai_mode,
            )
            try:
                paid_result = yi_publishing_auto_translate_page(book_id, page_num, paid_req)
                if paid_result.get("status") == "ok":
                    paid_qc = paid_result.get("quality", {}) or {}
                    paid_err = paid_qc.get("error_count", 0)
                    paid_fit = paid_qc.get("fit_score", 0)
                    # Accept paid only if it improves quality
                    if paid_err <= err_count:
                        result = paid_result
                        qc = paid_qc
                        attempted = result.get("total_lines_attempted", 0)
                        translated = result.get("total_lines_translated", 0)
                        err_count = paid_err
                        fit_score = paid_fit
                        retried_paid = True
            except Exception as _:
                pass

        total_lines += attempted
        total_translated += translated
        total_errors += err_count
        total_warns += qc.get("warn_count", 0)

        if attempted == 0:
            verdict = "skip"
        elif err_count == 0 and qc.get("warn_count", 0) == 0:
            verdict = "fit"
        elif err_count == 0:
            verdict = "review"
        else:
            verdict = "mismatch"

        page_reports.append({
            "page_num": page_num,
            "status": status,
            "verdict": verdict,
            "lines_attempted": attempted,
            "lines_translated": translated,
            "fit_score": fit_score,
            "error_count": err_count,
            "warn_count": qc.get("warn_count", 0),
            "issues": qc.get("issues", [])[:5],
            "model_used": result.get("model_used"),
            "provider": result.get("provider"),
            "retried_paid": retried_paid,
            "cost_usd": result.get("cost_usd", 0),
            "tokens": result.get("tokens"),
            "elapsed_seconds": round(time.time() - t0, 2),
            "message": result.get("message"),
        })

    batch_elapsed = time.time() - t0_batch
    avg_fit = round(
        sum(p.get("fit_score") or 100 for p in page_reports if p["status"] == "ok")
        / max(total_pages, 1),
        1,
    )
    total_cost = round(sum(p.get("cost_usd", 0) or 0 for p in page_reports), 6)
    paid_pages = sum(1 for p in page_reports if (p.get("provider") == "deepseek-native"))

    return {
        "status": "ok",
        "book_id": book_id,
        "start_page": req.start_page,
        "end_page": req.end_page,
        "summary": {
            "pages_processed": total_pages,
            "total_lines_attempted": total_lines,
            "total_lines_translated": total_translated,
            "total_errors": total_errors,
            "total_warnings": total_warns,
            "avg_fit_score": avg_fit,
            "batch_elapsed_seconds": round(batch_elapsed, 1),
            "total_cost_usd": total_cost,
            "paid_pages_count": paid_pages,
        },
        "pages": page_reports,
    }


@app.put("/api/yi-publishing/regions/{book_id}/{page_num}/{region_id}/lines/{line_id}/translation")
def yi_publishing_save_line_translation(
    book_id: str, page_num: int, region_id: str, line_id: str,
    req: LineTranslationSaveRequest, request: Request,
) -> dict:
    """Save translation for a single line within a region. Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    trans_dir = TRANSLATIONS_ROOT / book_id / f"p{page_num:04d}"
    trans_dir.mkdir(parents=True, exist_ok=True)
    trans_path = trans_dir / f"{region_id}.json"

    # Load existing
    existing = {}
    if trans_path.exists():
        try:
            existing = json.loads(trans_path.read_text())
        except Exception:
            pass

    # Ensure lines dict exists
    if "lines" not in existing or not isinstance(existing.get("lines"), dict):
        existing["lines"] = {}

    line_data = existing["lines"].get(line_id, {})
    line_version = int(line_data.get("version", 0)) + 1

    existing["lines"][line_id] = {
        "text_vi": req.text_vi,
        "status": req.status,
        "translator": req.translator,
        "notes": req.notes,
        "version": line_version,
        "updated_at": int(time.time()),
    }
    trans_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
    return {"status": "ok", "region_id": region_id, "line_id": line_id, "version": line_version}


@app.get("/api/yi-publishing/phu/phu-thai-vi")
def yi_publishing_phu_thai_vi() -> dict:
    """Return Phú Thái Vi 3-layer (hanviet + luangiai + giaithichdande).
    
    Source: Q4 Tử Vi Đẩu Số Toàn Thư, Trần Đoàn (p16-17).
    Layer 3 is plain Vietnamese explanation (no jargon) for first-time readers.
    """
    layer3_path = PUBLISHING_PROJECT_ROOT / "data" / "yi_publishing" / "translations" / "tuvidauso-zh" / "_phu_thai_vi_layer3.json"
    if not layer3_path.exists():
        return {"status": "error", "message": "Layer 3 not generated yet"}
    try:
        data = json.loads(layer3_path.read_text())
        return {
            "status": "ok",
            "source": data.get("source"),
            "model": data.get("model"),
            "passages": data.get("passages", []),
            "count": len(data.get("passages", [])),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _founder_cache_read(kind: str, legacy_filename: str) -> dict:
    """Read founder cache: new structure first, fall back to legacy path."""
    _pub_data = PUBLISHING_PROJECT_ROOT / "data" / "yi_publishing"
    new_p = _pub_data / "analysis_cache" / "_founder" / f"{kind}.json"
    if new_p.exists():
        try:
            return {"status": "ok", **json.loads(new_p.read_text())}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    legacy = _pub_data / "translations" / "tuvidauso-zh" / legacy_filename
    if not legacy.exists():
        return {"status": "error", "message": "Not generated yet"}
    try:
        return {"status": "ok", **json.loads(legacy.read_text())}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/yi-publishing/phu/founder-reading")
def yi_publishing_phu_founder_reading(request: Request) -> dict:
    """Return personalized Phú Thái Vi readings for founder chart. Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    return _founder_cache_read("phu_reading", "_phu_reading_founder.json")


@app.get("/api/yi-publishing/cach-cuc/founder/{cach_id}")
def yi_publishing_cach_cuc_founder(cach_id: str, request: Request) -> dict:
    """Return founder's deep reading for a specific cách cục. Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    p = PUBLISHING_PROJECT_ROOT / "data" / "yi_publishing" / "translations" / "tuvidauso-zh" / f"_cach_{cach_id}_founder.json"
    if not p.exists():
        return {"status": "error", "message": f"Cách cục '{cach_id}' chưa có deep reading"}
    try:
        return {"status": "ok", **json.loads(p.read_text())}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/yi-publishing/anh-deep-analysis")
def yi_publishing_anh_deep(request: Request) -> dict:
    """Return anh's deep analysis (cách cục discovery + synastry with wife). Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    return _founder_cache_read("deep_analysis", "_anh_deep_analysis.json")


# ─── Serve built Vue webapp (production: SPA fallback) ─────────────────
# In prod, the Vue dist is built into client/webapp/dist and served by
# this FastAPI app. /api/* and /figures/* keep their existing handlers.
import os as _os
from fastapi.responses import FileResponse as _FileResponse

@app.get("/api/yi-publishing/dai-van/founder")
def yi_publishing_dai_van_founder(request: Request) -> dict:
    """Return anh's 12 Đại Vận annotations. Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    return _founder_cache_read("dai_van", "_dai_van_founder.json")


@app.get("/api/yi-publishing/luu-nien/founder")
def yi_publishing_luu_nien_founder(request: Request) -> dict:
    """Return anh's Lưu Niên 2026-2030. Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    return _founder_cache_read("luu_nien", "_luu_nien_founder.json")


@app.get("/api/yi-publishing/luu-nguyet-2026/founder")
def yi_publishing_luu_nguyet_2026_founder(request: Request) -> dict:
    """Return anh's Lưu Nguyệt 12 tháng âm năm 2026. Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    return _founder_cache_read("luu_nguyet", "_luu_nguyet_2026_founder.json")


# ═══════════════════════════════════════════════════════════════════════════
# YI Publishing — Library Gallery v2.0 (book CRUD + OCR job queue)
# Spec: docs/superpowers/specs/2026-05-22-dich-sach-ui-v2-design.md
# ═══════════════════════════════════════════════════════════════════════════

class FinalizeBookRequest(BaseModel):
    """Step 3 of upload wizard: confirm metadata + finalize book."""
    temp_id: str
    book_id: str
    title_vi: str
    hanzi_title: str = ""
    author: str = ""
    year: Optional[int] = None
    language: str = "zh"
    school: str = ""
    notes: str = ""


class UpdateBookRequest(BaseModel):
    """PATCH /books/{id} — partial update."""
    title_vi: Optional[str] = None
    hanzi_title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    language: Optional[str] = None
    school: Optional[str] = None
    notes: Optional[str] = None


class SubmitOcrRequest(BaseModel):
    """POST /books/{id}/jobs/ocr — trigger OCR (single or swarm mode)."""
    start_page: int = 1
    end_page: int
    backend: str = "pipeline"   # "pipeline" or "vlm"
    language: str = "ch"        # "ch" or "en"
    workers: int = 1            # 1 = sequential, >1 = parallel swarm (capped at 4)
    formula_enable: bool = True  # False for Hán cổ multi-col (avoid false LaTeX)


@app.post("/api/yi-publishing/books/upload")
async def yi_publishing_upload_pdf(request: Request, file: UploadFile = File(...)) -> dict:
    """Step 1: save uploaded PDF to temp folder, extract trang-1 cover + metadata. Owner-only.

    Returns temp_id (used in finalize step) + auto-extracted metadata.
    """
    from api.auth import require_owner
    require_owner(request)
    from engine.yi_publishing.books_store import slugify
    from engine.yi_publishing.cover_extractor import extract_cover, extract_pdf_metadata
    import uuid

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    UPLOAD_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    temp_id = uuid.uuid4().hex[:12]
    temp_pdf = UPLOAD_TEMP_ROOT / f"{temp_id}.pdf"
    temp_cover = UPLOAD_TEMP_ROOT / f"{temp_id}-cover.jpg"

    # Stream save (avoid loading entire file in memory)
    MAX_SIZE = 200 * 1024 * 1024  # 200 MB
    written = 0
    with open(temp_pdf, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            written += len(chunk)
            if written > MAX_SIZE:
                temp_pdf.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="File exceeds 200 MB")
            f.write(chunk)

    # Extract metadata + cover
    try:
        meta = extract_pdf_metadata(temp_pdf)
        extract_cover(temp_pdf, temp_cover)
    except Exception as e:
        temp_pdf.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Cannot parse PDF: {e}")

    # Suggest book_id slug from original filename
    base_name = Path(file.filename).stem
    suggested_book_id = slugify(base_name) or temp_id

    return {
        "status": "ok",
        "temp_id": temp_id,
        "cover_url": f"/api/yi-publishing/uploads/{temp_id}/cover",
        "suggested_metadata": {
            "book_id": suggested_book_id,
            "title_vi": meta.get("title") or base_name,
            "hanzi_title": "",
            "author": meta.get("author") or "",
            "year": meta.get("year"),
            "page_count": meta.get("page_count", 0),
            "language": "zh",
        },
    }


@app.get("/api/yi-publishing/uploads/{temp_id}/cover")
def yi_publishing_upload_cover(temp_id: str):
    """Serve temp cover during upload wizard."""
    p = UPLOAD_TEMP_ROOT / f"{temp_id}-cover.jpg"
    if not p.exists():
        raise HTTPException(status_code=404, detail="Cover not found")
    return FileResponse(p, media_type="image/jpeg")


@app.post("/api/yi-publishing/books/finalize")
def yi_publishing_finalize_book(req: FinalizeBookRequest, request: Request) -> dict:
    """Step 3: move temp PDF + cover to permanent location, add to books_store. Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    from engine.yi_publishing.books_store import get_store
    from engine.yi_publishing.cover_extractor import extract_pdf_metadata

    temp_pdf = UPLOAD_TEMP_ROOT / f"{req.temp_id}.pdf"
    temp_cover = UPLOAD_TEMP_ROOT / f"{req.temp_id}-cover.jpg"
    if not temp_pdf.exists():
        raise HTTPException(status_code=404, detail=f"Temp upload {req.temp_id} not found or expired")

    store = get_store()
    if store.book_exists(req.book_id):
        raise HTTPException(status_code=409, detail=f"book_id {req.book_id!r} already exists")

    # Move files to permanent location
    RAW_PDFS_ROOT.mkdir(parents=True, exist_ok=True)
    COVERS_ROOT.mkdir(parents=True, exist_ok=True)
    final_pdf = RAW_PDFS_ROOT / f"{req.book_id}.pdf"
    final_cover = COVERS_ROOT / f"{req.book_id}.jpg"
    temp_pdf.replace(final_pdf)
    if temp_cover.exists():
        temp_cover.replace(final_cover)

    # Extract page_count from final PDF
    try:
        meta = extract_pdf_metadata(final_pdf)
        page_count = meta.get("page_count", 0)
    except Exception:
        page_count = 0

    try:
        book = store.add_book(
            book_id=req.book_id,
            title_vi=req.title_vi,
            hanzi_title=req.hanzi_title,
            author=req.author,
            year=req.year,
            language=req.language,
            school=req.school,
            notes=req.notes,
            pdf_path=str(final_pdf.relative_to(PUBLISHING_PROJECT_ROOT)),
            cover_path=str(final_cover.relative_to(PUBLISHING_PROJECT_ROOT)) if final_cover.exists() else "",
            cover_custom=False,
            page_count=page_count,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "ok", "book": book}


@app.get("/api/yi-publishing/books/{book_id}/cover")
def yi_publishing_book_cover(book_id: str):
    """Serve cover JPEG. Falls back to placeholder if missing."""
    from engine.yi_publishing.books_store import get_store

    store = get_store()
    book = store.get_book(book_id)
    if book and book.get("cover_path"):
        cp = Path(book["cover_path"])
        if not cp.is_absolute():
            cp = PUBLISHING_PROJECT_ROOT / cp
        if cp.exists():
            return FileResponse(cp, media_type="image/jpeg")
    # Default location guess
    default_cover = COVERS_ROOT / f"{book_id}.jpg"
    if default_cover.exists():
        return FileResponse(default_cover, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Cover not found")


@app.put("/api/yi-publishing/books/{book_id}/cover")
async def yi_publishing_upload_custom_cover(book_id: str, request: Request, file: UploadFile = File(...)) -> dict:
    """Override book cover with user upload (image/* accepted, normalized to JPEG). Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    from engine.yi_publishing.books_store import get_store
    from engine.yi_publishing.cover_extractor import save_uploaded_cover

    store = get_store()
    book = store.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image > 10 MB")

    COVERS_ROOT.mkdir(parents=True, exist_ok=True)
    final_cover = COVERS_ROOT / f"{book_id}.jpg"
    try:
        save_uploaded_cover(image_bytes, final_cover)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Cannot process image: {e}")

    updated = store.update_book(
        book_id,
        cover_path=str(final_cover.relative_to(PUBLISHING_PROJECT_ROOT)),
        cover_custom=True,
    )
    return {"status": "ok", "book": updated}


@app.patch("/api/yi-publishing/books/{book_id}")
def yi_publishing_update_book_metadata(book_id: str, req: UpdateBookRequest, request: Request) -> dict:
    """Update book metadata. Only non-null fields are applied. Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    from engine.yi_publishing.books_store import get_store

    store = get_store()
    if not store.book_exists(book_id):
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")

    fields = {k: v for k, v in req.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        updated = store.update_book(book_id, **fields)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok", "book": updated}


@app.delete("/api/yi-publishing/books/{book_id}")
def yi_publishing_delete_book(book_id: str, request: Request) -> dict:
    """Soft delete: sets deleted=true. PDF + cover remain on disk. Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    from engine.yi_publishing.books_store import get_store

    store = get_store()
    if not store.delete_book(book_id, soft=True):
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
    return {"status": "ok", "book_id": book_id, "deleted": True}


@app.post("/api/yi-publishing/books/{book_id}/recompute-progress")
def yi_publishing_recompute_progress(book_id: str, request: Request) -> dict:
    """Force progress recompute by scanning MinerU + translations folder. Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    from engine.yi_publishing.books_store import get_store

    store = get_store()
    if not store.book_exists(book_id):
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
    try:
        updated = store.recompute_progress(book_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recompute failed: {e}")
    return {"status": "ok", "book": updated}


# ─── Smart Onboarding ────────────────────────────────────────────────────────


class SubmitOnboardRequest(BaseModel):
    """POST /books/{id}/onboard — run Smart Onboarding Pipeline."""
    n_sample_pages: int = 3
    skip_thumbnails: bool = False


@app.post("/api/yi-publishing/books/{book_id}/onboard")
def yi_publishing_submit_onboard_job(book_id: str, req: SubmitOnboardRequest, request: Request) -> dict:
    """Trigger Smart Onboarding Pipeline (page split → profile → TOC → plan). Owner-only.

    Runs ~3-5 phút (real MinerU spike). Returns job_id for polling.
    Rejects if another job is already active.
    """
    from api.auth import require_owner
    require_owner(request)
    from engine.yi_publishing.books_store import get_store
    from engine.yi_publishing.jobs import get_default_store

    store = get_store()
    book = store.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")

    pdf_rel = book.get("pdf_path") or ""
    if not pdf_rel:
        raise HTTPException(status_code=400, detail="Book has no pdf_path")
    pdf_abs = Path(pdf_rel)
    if not pdf_abs.is_absolute():
        pdf_abs = PUBLISHING_PROJECT_ROOT / pdf_rel
    if not pdf_abs.exists():
        raise HTTPException(status_code=404, detail=f"PDF file missing: {pdf_abs}")

    output_dir = PUBLISHING_PROJECT_ROOT / "data" / "yi_publishing" / "onboarding" / book_id

    jobs_store = get_default_store()
    try:
        job = jobs_store.submit_onboard_job(
            book_id=book_id,
            pdf_path=pdf_abs,
            output_dir=output_dir,
            n_sample_pages=req.n_sample_pages,
            skip_thumbnails=req.skip_thumbnails,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": "ok", "job": job}


@app.get("/api/yi-publishing/books/{book_id}/plan")
def yi_publishing_get_plan(book_id: str) -> dict:
    """Get onboarding plan artifacts (profile + TOC + OCR config) for a book.

    Returns 404 if book hasn't been onboarded yet.
    """
    from engine.yi_publishing.books_store import get_store

    store = get_store()
    if not store.book_exists(book_id):
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")

    onboard_dir = PUBLISHING_PROJECT_ROOT / "data" / "yi_publishing" / "onboarding" / book_id
    if not onboard_dir.exists():
        raise HTTPException(
            status_code=404,
            detail="Book not onboarded yet — run POST /onboard first",
        )

    result: dict = {"status": "ok", "book_id": book_id}

    # Plan summary
    plan_summary_path = onboard_dir / "_PLAN-SUMMARY.json"
    if plan_summary_path.exists():
        result["plan_summary"] = json.loads(plan_summary_path.read_text(encoding="utf-8"))

    # Profile
    profile_path = onboard_dir / "book_profile.json"
    if profile_path.exists():
        result["profile"] = json.loads(profile_path.read_text(encoding="utf-8"))

    # OCR config (the one Anh-duyệt-able)
    ocr_cfg_path = onboard_dir / "_OCR-CONFIG.json"
    if ocr_cfg_path.exists():
        result["ocr_config"] = json.loads(ocr_cfg_path.read_text(encoding="utf-8"))

    # TOC markdown (human-readable)
    toc_path = onboard_dir / "_TOC.md"
    if toc_path.exists():
        result["toc_markdown"] = toc_path.read_text(encoding="utf-8")

    # Reading + translation plans
    reading_path = onboard_dir / "_READING-PLAN.md"
    if reading_path.exists():
        result["reading_plan_markdown"] = reading_path.read_text(encoding="utf-8")

    translation_path = onboard_dir / "_TRANSLATION-PLAN.md"
    if translation_path.exists():
        result["translation_plan_markdown"] = translation_path.read_text(encoding="utf-8")

    return result


# ─── Jobs (OCR queue) ────────────────────────────────────────────────────────


@app.post("/api/yi-publishing/books/{book_id}/jobs/ocr")
def yi_publishing_submit_ocr_job(book_id: str, req: SubmitOcrRequest, request: Request) -> dict:
    """Trigger MinerU OCR job. Rejects if another OCR job is already active. Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    from engine.yi_publishing.books_store import get_store
    from engine.yi_publishing.jobs import get_default_store

    store = get_store()
    book = store.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")

    pdf_rel = book.get("pdf_path") or ""
    if not pdf_rel:
        raise HTTPException(status_code=400, detail="Book has no pdf_path; please re-upload")
    pdf_abs = Path(pdf_rel)
    if not pdf_abs.is_absolute():
        pdf_abs = PUBLISHING_PROJECT_ROOT / pdf_rel
    if not pdf_abs.exists():
        raise HTTPException(status_code=404, detail=f"PDF file missing: {pdf_abs}")

    jobs_store = get_default_store()
    try:
        job = jobs_store.submit_ocr_job(
            book_id=book_id,
            pdf_path=pdf_abs,
            start_page=req.start_page,
            end_page=req.end_page,
            backend=req.backend,
            language=req.language,
            workers=req.workers,
            formula_enable=req.formula_enable,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": "ok", "job": job}


@app.get("/api/yi-publishing/jobs")
def yi_publishing_list_jobs(
    active: bool = False,
    book_id: Optional[str] = None,
    limit: int = 50,
) -> dict:
    """List jobs (newest first). Optional filters."""
    from engine.yi_publishing.jobs import get_default_store

    jobs_store = get_default_store()
    jobs = jobs_store.list_jobs(active=active, book_id=book_id, limit=limit)
    return {"status": "ok", "jobs": jobs, "count": len(jobs)}


@app.get("/api/yi-publishing/jobs/{job_id}")
def yi_publishing_get_job(job_id: str) -> dict:
    """Single job status."""
    from engine.yi_publishing.jobs import get_default_store

    jobs_store = get_default_store()
    job = jobs_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return {"status": "ok", "job": job}


@app.delete("/api/yi-publishing/jobs/{job_id}")
def yi_publishing_cancel_job(job_id: str, request: Request) -> dict:
    """Cancel job. Cooperative — current chunk finishes first. Owner-only."""
    from api.auth import require_owner
    require_owner(request)
    from engine.yi_publishing.jobs import get_default_store

    jobs_store = get_default_store()
    if not jobs_store.cancel_job(job_id):
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found or not in cancellable state",
        )
    return {"status": "ok", "job_id": job_id, "cancelled": True}


# ─── Generic Tử Vi Analyzer endpoints ────────────────────────────────────────
# (Person-based: works for any person_key in founder's user_persons namespace
#  or any directly-passed birth datetime.)

class _AnalyzeRequest(BaseModel):
    """Request for generic Tử Vi analyzer."""
    # Either provide person_key (looks up from user_persons of current user)
    person_key: Optional[str] = None
    # OR provide birth directly
    birth_datetime_local: Optional[str] = None
    gender: Optional[str] = None
    name: Optional[str] = "Người"
    timezone: str = "Asia/Ho_Chi_Minh"
    # Analysis options
    luu_nien_start: int = 2026
    luu_nien_end: int = 2030
    luu_nguyet_year: int = 2026
    phu_top_n: int = 5
    force: bool = False  # bypass cache


def _resolve_person_from_request(req: _AnalyzeRequest, request: Request):
    """Resolve Person from request — either person_key (user_persons) or direct.

    Sets `user_id` on the returned Person so cache is scoped per-user, preventing
    collision when multiple users use the same `person_key` (e.g. 'self').
    """
    from engine.tu_vi.analyzer import Person
    from api.auth import get_current_user
    user = get_current_user(request)
    uid = user["user_id"] if user else None

    if req.birth_datetime_local and req.gender:
        return Person(
            person_key=req.person_key or f"adhoc_{int(time.time())}",
            name=req.name or "Người",
            birth_datetime_local=req.birth_datetime_local,
            gender=req.gender,
            timezone=req.timezone,
            user_id=uid,
        )
    if req.person_key:
        # Look up from current user's user_persons
        from api.auth import AUTH_DB
        import sqlite3
        # Legacy '_founder' shortcut now restricted to the owner — previously
        # it returned anh's hardcoded birth profile to ANY caller (including
        # guests) which let kinhdich.online be used as an oracle backed by
        # anh's personal chart. Owner-only keeps the legacy cache working
        # for anh's own browser while closing the leak.
        if req.person_key == "_founder":
            if not user or user.get("role") != "owner":
                raise HTTPException(404, "person_key not found")
            return Person(
                person_key="_founder",
                name="Anh (Founder)",
                birth_datetime_local="1988-06-05T23:30:00",
                gender="nam",
                user_id=uid,
            )
        if not user:
            raise HTTPException(401, "Login required to use person_key")
        db = sqlite3.connect(AUTH_DB)
        row = db.execute(
            "SELECT name, gender, birth_datetime_local, timezone FROM user_persons WHERE user_id=? AND person_key=?",
            (user["user_id"], req.person_key),
        ).fetchone()
        db.close()
        if not row:
            raise HTTPException(404, f"person_key '{req.person_key}' not found")
        return Person(
            person_key=req.person_key,
            name=row[0],
            gender=row[1] or "nam",
            birth_datetime_local=row[2] or "",
            timezone=row[3] or "Asia/Ho_Chi_Minh",
            user_id=uid,
        )
    raise HTTPException(400, "Must provide person_key OR birth_datetime_local+gender")


@app.post("/api/tu-vi/analyze/{kind}")
def yi_tuvi_analyze(kind: str, req: _AnalyzeRequest, request: Request) -> dict:
    """Run 1 specific Tử Vi analysis.

    kind: 'cach_cuc' | 'dai_van' | 'luu_nien' | 'luu_nguyet' | 'phu_match' | 'phu_reading' | 'cung_reading' | 'phe_menh' | 'all'
    """
    from engine.tu_vi.analyzer import TuViAnalyzer
    from fastapi import HTTPException
    person = _resolve_person_from_request(req, request)
    analyzer = TuViAnalyzer(person, force=req.force)

    try:
        if kind == "cach_cuc":
            return {"status": "ok", "kind": kind, **analyzer.discover_cach_cuc()}
        elif kind == "dai_van":
            return {"status": "ok", "kind": kind, **analyzer.dai_van_annotate()}
        elif kind == "luu_nien":
            return {"status": "ok", "kind": kind, **analyzer.luu_nien(req.luu_nien_start, req.luu_nien_end)}
        elif kind == "luu_nguyet":
            return {"status": "ok", "kind": kind, **analyzer.luu_nguyet(req.luu_nguyet_year)}
        elif kind == "phu_match":
            return {"status": "ok", "kind": kind, **analyzer.phu_match()}
        elif kind == "phu_reading":
            return {"status": "ok", "kind": kind, **analyzer.phu_reading(req.phu_top_n)}
        elif kind == "cung_reading":
            return {"status": "ok", "kind": kind, **analyzer.cung_reading()}
        elif kind == "phe_menh":
            return {"status": "ok", "kind": kind, **analyzer.phe_menh()}
        elif kind == "all":
            return {"status": "ok", "kind": kind, **analyzer.run_all(
                luu_nien_years=(req.luu_nien_start, req.luu_nien_end),
                luu_nguyet_year=req.luu_nguyet_year,
                phu_top_n=req.phu_top_n,
            )}
        else:
            raise HTTPException(400, f"Unknown analysis kind: {kind}")
    except HTTPException:
        raise
    except Exception as e:
        return {"status": "error", "kind": kind, "message": str(e)}


@app.get("/api/tu-vi/analyze/{person_key}/{kind}")
def yi_tuvi_analyze_get(person_key: str, kind: str, request: Request) -> dict:
    """GET version: load cached analysis result without running new one.

    Scoped per-user: each logged-in user only sees cache from their own namespace.
    `_founder` cache (special prefix) is owner-only.
    """
    from engine.tu_vi.analyzer import _cache_load
    from api.auth import get_current_user
    user = get_current_user(request)
    if person_key.startswith("_") and (not user or user.get("role") != "owner"):
        raise HTTPException(403, "owner-only for special person keys")
    uid = user["user_id"] if user else None
    cached = _cache_load(person_key, kind, uid)
    if cached:
        return {"status": "ok", "cached": True, "kind": kind, **cached}
    return {"status": "not_cached", "kind": kind, "message": f"No cached '{kind}' for {person_key}"}


# ─── Cách cục dictionary (từ thâm nhuần Q1) ──────────────────────────────────
@app.get("/api/tu-vi/q4/10-buoc-luan")
def yi_tuvi_10_buoc_luan() -> dict:
    """10 bước luận Tử Vi chính thức của Trần Đoàn (Q4 p0266)."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "data/tu_vi/10_buoc_luan.json"
    return {"status": "ok", **json.loads(p.read_text())}


@app.get("/api/tu-vi/q4/thien-quan-archetype/{hour}/{khac}")
def yi_tuvi_thien_quan_archetype(hour: str, khac: str) -> dict:
    """Get 1 archetype Thiên Quán Phân Cung theo giờ + khắc (Q4 p0268-p0271)."""
    from engine.tu_vi.thien_quan_typology import get_archetype
    a = get_archetype(hour, khac)
    if not a:
        return {"status": "error", "message": f"No archetype for ({hour}, {khac})"}
    return {"status": "ok", "archetype": a}


@app.get("/api/tu-vi/q4/thien-quan-archetypes-all")
def yi_tuvi_thien_quan_all() -> dict:
    """List all 36 archetypes."""
    from engine.tu_vi.thien_quan_typology import list_all_archetypes
    return {"status": "ok", "total": 36, "archetypes": list_all_archetypes()}


@app.get("/api/tu-vi/q4/rectification-rules")
def yi_tuvi_rectification() -> dict:
    """Định thời khắc rules + Tiểu nhi thời khắc patterns (Q4 p0267)."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "data/tu_vi/rectification_rules.json"
    return {"status": "ok", **json.loads(p.read_text())}


@app.get("/api/tu-vi/q4/chieu-dom-kinh-phi-tinh")
def yi_tuvi_chieu_dom_phi_tinh() -> dict:
    """18 Phi Tinh schema (Chiếu Đởm Kinh — paradigm khác chính thống)."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "data/tu_vi/chieu_dom_kinh_18_phi_tinh.json"
    return {"status": "ok", **json.loads(p.read_text())}


@app.post("/api/tu-vi/q4/chieu-dom-kinh/cast")
def yi_tuvi_chieu_dom_cast(req: _AnalyzeRequest, request: Request) -> dict:
    """Cast lá số Chiếu Đởm Kinh — 18 Phi Tinh parallel với main Tử Vi engine.

    Per Q4 p0272-p0273 — formula an sao riêng của CDK.
    """
    from engine.tu_vi.chieu_dom_kinh_an_sao import cast_chieu_dom_kinh
    from engine.tu_vi.analyzer import TuViAnalyzer
    from core.chronos import calculate_chronos_state
    from datetime import datetime

    person = _resolve_person_from_request(req, request)
    chronos = calculate_chronos_state(person.birth_datetime_local, person.timezone)
    d_str, m_str, _ = chronos.almanac.lunar_date.split("/")
    year_parts = chronos.ganzhi.year.split()
    dt = datetime.fromisoformat(person.birth_datetime_local)
    hour = dt.hour
    BRANCHES = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
    hour_branch = "Tý" if hour >= 23 or hour < 1 else BRANCHES[((hour + 1) // 2) % 12]

    result = cast_chieu_dom_kinh(
        year_stem=year_parts[0],
        year_branch=year_parts[1],
        lunar_month=int(m_str),
        hour_branch=hour_branch,
        gender=person.gender,
    )
    return {"status": "ok", **result}


# ─── Cung Phu Thê — Bắc phái Trung Châu (Vương Đình Chỉ) ────────────────────


@app.post("/api/tu-vi/cung-phu-the/bac-phai")
def yi_tuvi_cung_phu_the_bac_phai(req: _AnalyzeRequest, request: Request) -> dict:
    """Luận cung Phu Thê theo BẮC PHÁI Trung Châu.

    Paradigm: Trung Châu Tử Vi Đẩu Số 2 (Vương Đình Chỉ, section 5.3).
    14 chính tinh × 12 cung Địa Chi + 24 tổ hợp đôi.

    Output: structured paradigm + markdown summary.
    Public access — không gate VIP (paradigm = lookup từ seed JSON).
    """
    from engine.tu_vi.chiem_phu_the import chiem_phu_the, chiem_phu_the_summary_text
    from engine.tu_vi.analyzer import TuViAnalyzer

    person = _resolve_person_from_request(req, request)
    analyzer = TuViAnalyzer(person)
    la_so = analyzer.la_so

    # Pass gender để personalize filter gender-conditional paradigm
    gender = (person.gender or "nam").lower().strip()
    if gender not in ("nam", "nu", "nữ"):
        gender = "nam"
    result = chiem_phu_the(la_so, gender=gender)
    if "error" in result:
        return {"status": "error", "message": result["error"]}

    summary_md = chiem_phu_the_summary_text(la_so)

    # Engine v4 — Full 26 quy luật + meta panorama:
    #   v2 (Q1-9) + v3 cross-bind (Q10-13) + v4 phase 2-5 (Q14-26) + Q27 meta
    from engine.tu_vi.chiem_phu_the_v4 import chiem_phu_the_v4
    v4_result = chiem_phu_the_v4(la_so)

    # Cross-reference panel (replace placeholder "Cần xem kèm: ..."):
    # render thật Mệnh + Phúc Đức + Đại vận hiện tại + Thái Dương/Thái Âm miếu hãm
    from engine.tu_vi.chiem_phu_the_cross_reference import build_cross_reference
    birth_year = None
    try:
        # person.birth_datetime_local thường dạng "1988-06-05 23:30"
        birth_year = int(str(person.birth_datetime_local)[:4])
    except Exception:
        pass
    cross_ref = build_cross_reference(la_so, gender=gender, birth_year=birth_year)

    # Đặc điểm BẠN ĐỜI qua sao chính diệu Phu Thê (mới 2026-06-08)
    try:
        from engine.tu_vi.phu_the_partner_traits import build_partner_traits
        partner_traits = build_partner_traits(la_so, gender=gender)
    except Exception:
        partner_traits = None

    # Khối đọc sâu Ngũ Uẩn cho đúng trục lá số đang luận:
    # Mệnh là gốc vận hành của bản thân, Phu Thê là quan hệ một-một.
    try:
        from engine.tu_vi.interpretation import interpret_la_so

        full_interpretation = interpret_la_so(la_so)
        readings = full_interpretation.get("palace_readings", [])

        def _palace_reading(name: str) -> dict | None:
            return next((r for r in readings if r.get("palace_name") == name), None)

        ngu_uan_focus = {
            "menh": _palace_reading("Mệnh"),
            "phu_the": _palace_reading("Phu Thê"),
            "school": "Tử Vi Bôn Ba — quán chiếu Ngũ Uẩn",
            "note": (
                "Đọc Mệnh để hiểu cơ chế bản thân; đọc Phu Thê để hiểu cơ chế "
                "quan hệ thân mật. Đây là bản đồ vận hành, không phải bản án."
            ),
        }
    except Exception:
        ngu_uan_focus = None

    return {
        "status": "ok",
        "person_key": person.person_key,
        "school": result["school"],
        "thay_to_su": result["thay_to_su"],
        "data": result,
        "summary_markdown": summary_md,
        "v2": v4_result,  # backward field name
        "v3": v4_result,
        "v4": v4_result,
        "cross_reference": cross_ref,
        "partner_traits": partner_traits,
        "ngu_uan_focus": ngu_uan_focus,
        "la_so": la_so,  # Full chart cho UI render 12 ô đối chiếu
    }


class _LuanCungRequest(_AnalyzeRequest):
    branch: str = ""


@app.post("/api/tu-vi/q4/cdk/luan-cung")
def yi_tuvi_cdk_luan_cung(req: _LuanCungRequest, request: Request) -> dict:
    """Luận giải sâu 1 cung CDK bằng DeepSeek V4 Pro — VIP1 gated.

    Owner bypass VIP check + không consume_use. User thường cần subscription.
    Auto-extract → wiki sau mỗi lần gen.
    """
    from engine.tu_vi.cdk_cung_analyzer import luan_cdk_cung, BRANCHES_ORDER
    from engine.subscriptions import check_access, consume_use
    from api.auth import get_current_user

    if not req.branch or req.branch not in BRANCHES_ORDER:
        return {"status": "error", "message": f"Invalid branch. Must be one of {BRANCHES_ORDER}"}

    user = get_current_user(request)
    if not user:
        return {"status": "error", "message": "Phải đăng nhập để dùng tính năng VIP."}

    # VIP gating (owner bypass)
    if user.get("role") != "owner":
        access = check_access(user["user_id"], "tu_vi_cdk_luan_cung")
        if not access.get("allowed"):
            return {
                "status": "error",
                "message": f"Không có quyền VIP1 — {access.get('reason', 'unknown')}",
                "vip_check": access,
            }

    person = _resolve_person_from_request(req, request)
    result = luan_cdk_cung(person, req.branch, force=req.force)

    # Consume use only on success + not owner
    if result.get("status") == "ok" and user.get("role") != "owner" and not result.get("from_cache"):
        usage = consume_use(user["user_id"], "tu_vi_cdk_luan_cung")
        result["usage_after"] = usage

    return result


@app.post("/api/tu-vi/q4/cdk/eval-cach-cuc")
def yi_tuvi_cdk_eval_cach_cuc(req: _AnalyzeRequest, request: Request) -> dict:
    """Eval 6 cách cục Chiếu Đởm Kinh cho lá số cụ thể.

    Free endpoint — không cần VIP. Engine deterministic, no LLM call.
    """
    from engine.tu_vi.cdk_cach_cuc_matcher import evaluate_cdk_cach_cuc
    from engine.tu_vi.chieu_dom_kinh_an_sao import cast_chieu_dom_kinh
    from core.chronos import calculate_chronos_state
    from datetime import datetime

    person = _resolve_person_from_request(req, request)
    chronos = calculate_chronos_state(person.birth_datetime_local, person.timezone)
    _d, m_str, _y = chronos.almanac.lunar_date.split("/")
    year_parts = chronos.ganzhi.year.split()
    dt = datetime.fromisoformat(person.birth_datetime_local)
    hour = dt.hour
    BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
    hour_branch = "Tý" if hour >= 23 or hour < 1 else BRANCHES[((hour + 1) // 2) % 12]
    chart = cast_chieu_dom_kinh(
        year_stem=year_parts[0], year_branch=year_parts[1],
        lunar_month=int(m_str), hour_branch=hour_branch, gender=person.gender,
    )
    return evaluate_cdk_cach_cuc(chart, hour_branch)


@app.post("/api/tu-vi/q4/cdk/luan-luu-nien")
def yi_tuvi_cdk_luan_luu_nien(req: _AnalyzeRequest, request: Request) -> dict:
    """Luận Lưu Niên 10 năm tới. VIP1-gated."""
    from engine.tu_vi.cdk_cung_analyzer import luan_luu_nien_10_nam
    from engine.subscriptions import check_access, consume_use
    from api.auth import get_current_user

    user = get_current_user(request)
    if not user:
        return {"status": "error", "message": "Phải đăng nhập để dùng VIP."}
    if user.get("role") != "owner":
        access = check_access(user["user_id"], "tu_vi_cdk_luan_cung")
        if not access.get("allowed"):
            return {"status": "error", "message": f"Cần VIP1 — {access.get('reason')}"}

    person = _resolve_person_from_request(req, request)
    result = luan_luu_nien_10_nam(person, num_years=10, force=req.force)
    if result.get("status") == "ok" and user.get("role") != "owner" and not result.get("from_cache"):
        consume_use(user["user_id"], "tu_vi_cdk_luan_cung")
    return result


@app.post("/api/tu-vi/q4/cdk/luan-dai-han")
def yi_tuvi_cdk_luan_dai_han(req: _AnalyzeRequest, request: Request) -> dict:
    """Luận chi tiết 8 vòng Đại Hạn CDK (80 năm). VIP1-gated."""
    from engine.tu_vi.cdk_cung_analyzer import luan_dai_han_8_vong
    from engine.subscriptions import check_access, consume_use
    from api.auth import get_current_user

    user = get_current_user(request)
    if not user:
        return {"status": "error", "message": "Phải đăng nhập để dùng VIP."}
    if user.get("role") != "owner":
        access = check_access(user["user_id"], "tu_vi_cdk_luan_cung")
        if not access.get("allowed"):
            return {"status": "error", "message": f"Cần VIP1 — {access.get('reason')}"}

    person = _resolve_person_from_request(req, request)
    result = luan_dai_han_8_vong(person, force=req.force)
    if result.get("status") == "ok" and user.get("role") != "owner" and not result.get("from_cache"):
        consume_use(user["user_id"], "tu_vi_cdk_luan_cung")
    return result


@app.post("/api/tu-vi/q4/cdk/luan-toan-bo")
def yi_tuvi_cdk_luan_toan_bo(req: _AnalyzeRequest, request: Request) -> dict:
    """Luận TOÀN BỘ 12 cung CDK trong 1 phiên (2 batches × 6 cung song song).

    Faster than 12 per-cung calls. Persist cache per-cung for instant future lookup.
    VIP1 gated (owner bypass). Charges 1 use only (not 12).
    """
    from engine.tu_vi.cdk_cung_analyzer import luan_toan_bo_cung
    from engine.subscriptions import check_access, consume_use
    from api.auth import get_current_user

    user = get_current_user(request)
    if not user:
        return {"status": "error", "message": "Phải đăng nhập để dùng VIP."}

    if user.get("role") != "owner":
        access = check_access(user["user_id"], "tu_vi_cdk_luan_cung")
        if not access.get("allowed"):
            return {"status": "error", "message": f"Không có quyền VIP1 — {access.get('reason')}", "vip_check": access}

    person = _resolve_person_from_request(req, request)
    result = luan_toan_bo_cung(person, force=req.force)

    # Consume 1 use only if fresh calls + not owner
    if result.get("status") == "ok" and user.get("role") != "owner" and result.get("fresh_calls", 0) > 0:
        usage = consume_use(user["user_id"], "tu_vi_cdk_luan_cung")
        result["usage_after"] = usage

    return result


@app.get("/api/tu-vi/q4/chieu-dom-12cung-matrix")
def yi_tuvi_chieu_dom_12cung() -> dict:
    """12 cung × 18 sao matrix từ Chiếu Đởm Kinh (Q4 p0279-p0286). ~203 rules."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "data/tu_vi/chieu_dom_kinh_12cung_x_18sao.json"
    return {"status": "ok", **json.loads(p.read_text())}


@app.get("/api/tu-vi/q4/phu-thi-corpus")
def yi_tuvi_phu_thi_corpus() -> dict:
    """Phú thi corpus — 786 lines từ Q4 dense band p0257-p0300 (training data phê mệnh)."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "data/tu_vi/q4_phu_thi_corpus.json"
    return {"status": "ok", **json.loads(p.read_text())}


@app.get("/api/tu-vi/q4/nhap-cot-tien-kinh")
def yi_tuvi_nhap_cot_tien() -> dict:
    """Nhập Cốt Tiên Kinh tổng đoán 4-chữ per 18 Phi Tinh."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "data/tu_vi/nhap_cot_tien_kinh_tong_doan.json"
    return {"status": "ok", **json.loads(p.read_text())}


@app.get("/api/tu-vi/q4/chieu-dom-kinh-cach-cuc")
def yi_tuvi_chieu_dom_cach_cuc() -> dict:
    """6 cách cục mới của Chiếu Đởm Kinh."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "data/tu_vi/chieu_dom_kinh_cach_cuc.json"
    return {"status": "ok", **json.loads(p.read_text())}


# ─── VIP — Luận giải sâu (DeepSeek Pro) ────────────────────────────────

@app.get("/api/user/my-vip-features")
def yi_user_my_vip(request: Request) -> dict:
    """Get all VIP subscriptions for current user (UI uses to show/hide buttons)."""
    from api.auth import get_current_user
    from engine.subscriptions import list_user_subscriptions, list_features
    user = get_current_user(request)
    if not user:
        return {"status": "ok", "subscriptions": [], "catalog": list_features(), "user_role": None}
    subs = list_user_subscriptions(user["user_id"])
    return {
        "status": "ok",
        "subscriptions": subs,
        "catalog": list_features(),
        "user_role": user.get("role"),
        "user_id": user.get("user_id"),
    }


# ═════════════════════════════════════════════════════════════════════════════
# 📚 USER PUBLICATIONS — Hồ sơ kết quả per-user
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/api/user/publications")
def yi_user_publications_list(request: Request, person_key: str = "") -> dict:
    """List all publications của current user (optionally filter person)."""
    from api.auth import get_current_user
    from engine.publications import list_publications, user_stats, PUB_TYPES
    user = get_current_user(request)
    if not user:
        raise HTTPException(401, "Login required")
    pubs = list_publications(user["user_id"], person_key=person_key or None)
    stats = user_stats(user["user_id"])
    return {
        "status": "ok",
        "publications": pubs,
        "stats": stats,
        "catalog": [{"pub_type": k, **v} for k, v in PUB_TYPES.items()],
    }


@app.get("/api/user/publications/{pub_id}")
def yi_user_publication_detail(pub_id: int, request: Request) -> dict:
    """Detail single publication (must be owner)."""
    from api.auth import get_current_user
    from engine.publications import get_publication
    user = get_current_user(request)
    if not user:
        raise HTTPException(401, "Login required")
    pub = get_publication(pub_id)
    if not pub:
        raise HTTPException(404, "Publication not found")
    if pub["user_id"] != user["user_id"] and user.get("role") != "owner":
        raise HTTPException(403, "Permission denied")
    return {"status": "ok", "publication": pub}


@app.get("/api/user/publications/{pub_id}/file/{fmt}")
def yi_user_publication_file(pub_id: int, fmt: str, request: Request):
    """Download/serve a publication file (pdf/docx/md/json). Auth-gated."""
    from api.auth import get_current_user
    from engine.publications import get_publication, PROJECT_ROOT
    from fastapi.responses import FileResponse
    user = get_current_user(request)
    if not user:
        raise HTTPException(401, "Login required")
    pub = get_publication(pub_id)
    if not pub:
        raise HTTPException(404, "Publication not found")
    if pub["user_id"] != user["user_id"] and user.get("role") != "owner":
        raise HTTPException(403, "Permission denied")
    formats = pub.get("formats", {})
    if fmt not in formats:
        raise HTTPException(404, f"Format '{fmt}' not available. Available: {list(formats.keys())}")
    file_path = PROJECT_ROOT / pub["file_dir"] / formats[fmt]
    if not file_path.exists():
        raise HTTPException(404, f"File missing on disk: {file_path}")
    mime_map = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "md": "text/markdown; charset=utf-8",
        "json": "application/json",
    }
    safe_title = pub["title"].replace(" ", "_").replace("—", "-")
    return FileResponse(
        str(file_path),
        media_type=mime_map.get(fmt, "application/octet-stream"),
        filename=f"{safe_title}.{fmt}",
    )


@app.post("/api/user/publications/{pub_id}/archive")
def yi_user_publication_archive(pub_id: int, request: Request) -> dict:
    """Archive a publication (soft-delete from listing, files preserved)."""
    from api.auth import get_current_user
    from engine.publications import archive_publication
    user = get_current_user(request)
    if not user:
        raise HTTPException(401, "Login required")
    return archive_publication(pub_id, user["user_id"])


class _ShareCreateRequest(BaseModel):
    publication_id: int
    expires_in_days: Optional[int] = 7        # default 7 ngày
    max_accesses: Optional[int] = None
    note: Optional[str] = None


@app.post("/api/user/publications/share")
def yi_user_publication_share(req: _ShareCreateRequest, request: Request) -> dict:
    """Tạo share token cho publication."""
    from api.auth import get_current_user
    from engine.publications import create_share_token
    import time as _t
    user = get_current_user(request)
    if not user:
        raise HTTPException(401, "Login required")
    expires_at = None
    if req.expires_in_days:
        expires_at = int(_t.time()) + req.expires_in_days * 86400
    return create_share_token(
        req.publication_id, user["user_id"],
        expires_at=expires_at,
        max_accesses=req.max_accesses,
        note=req.note,
    )


@app.get("/api/user/publications/shares/mine")
def yi_user_my_shares(request: Request) -> dict:
    """List share tokens current user đã tạo."""
    from api.auth import get_current_user
    from engine.publications import list_user_shares
    user = get_current_user(request)
    if not user:
        raise HTTPException(401, "Login required")
    return {"status": "ok", "shares": list_user_shares(user["user_id"])}


@app.delete("/api/user/publications/shares/{share_id}")
def yi_user_share_revoke(share_id: int, request: Request) -> dict:
    """Revoke a share token."""
    from api.auth import get_current_user
    from engine.publications import revoke_share
    user = get_current_user(request)
    if not user:
        raise HTTPException(401, "Login required")
    return revoke_share(share_id, user["user_id"])


@app.get("/api/share/{token}")
def yi_share_resolve(token: str):
    """Public endpoint — resolve share token → serve file (no auth needed)."""
    from engine.publications import resolve_share_token, PROJECT_ROOT
    from fastapi.responses import FileResponse, JSONResponse
    info = resolve_share_token(token)
    if not info:
        return JSONResponse({"status": "error", "message": "Token không hợp lệ"}, status_code=404)
    if info.get("_expired"):
        return JSONResponse({"status": "error", "message": "Link đã hết hạn"}, status_code=410)
    if info.get("_quota_exceeded"):
        return JSONResponse({"status": "error", "message": "Đã vượt số lượt truy cập"}, status_code=429)
    # Prefer PDF, fallback DOCX
    formats = info.get("formats", {})
    fmt = "pdf" if "pdf" in formats else ("docx" if "docx" in formats else None)
    if not fmt:
        return JSONResponse({"status": "error", "message": "Publication không có file"}, status_code=404)
    file_path = PROJECT_ROOT / info["file_dir"] / formats[fmt]
    if not file_path.exists():
        return JSONResponse({"status": "error", "message": "File không tồn tại"}, status_code=404)
    mime_map = {"pdf": "application/pdf", "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    safe_title = (info["title"] or "shared").replace(" ", "_").replace("—", "-")
    return FileResponse(
        str(file_path),
        media_type=mime_map[fmt],
        filename=f"{safe_title}.{fmt}",
    )


@app.post("/api/tu-vi/phe-menh-sau")
def yi_tuvi_phe_menh_sau(req: _AnalyzeRequest, request: Request) -> dict:
    """Luận giải sâu Tử Vi (VIP DeepSeek Pro). VIP1-gated.

    Engine generates 10-section deep phê mệnh per Trần Đoàn methodology.
    """
    from api.auth import get_current_user
    from engine.subscriptions import check_access, consume_use
    from engine.tu_vi.analyzer import TuViAnalyzer

    user = get_current_user(request)
    if not user:
        raise HTTPException(401, "Login required")
    user_id = user["user_id"]

    # Owner bypass — owner luôn có quyền
    if user.get("role") != "owner":
        access = check_access(user_id, "tu_vi_phe_menh_sau")
        if not access["allowed"]:
            raise HTTPException(403, f"VIP required: {access['reason']}")

    person = _resolve_person_from_request(req, request)
    analyzer = TuViAnalyzer(person, force=req.force)
    result = analyzer.phe_menh_sau()

    # Consume 1 use only if successful AND not owner
    if result.get("status") == "ok" and user.get("role") != "owner":
        usage = consume_use(user_id, "tu_vi_phe_menh_sau")
        result["usage"] = usage

    return result


# ─── Admin — Subscription management ───────────────────────────────────

@app.get("/api/admin/subscriptions")
def yi_admin_list_subscriptions(request: Request, feature_id: str = "") -> dict:
    """Admin: list all subscriptions (optionally filter by feature)."""
    from api.auth import get_current_user
    from engine.subscriptions import list_all_subscriptions, list_features
    user = get_current_user(request)
    if not user or user.get("role") != "owner":
        raise HTTPException(403, "Owner required")
    subs = list_all_subscriptions(feature_id or None)
    return {"status": "ok", "subscriptions": subs, "catalog": list_features()}


class _GrantSubRequest(BaseModel):
    user_id: int
    feature_id: str
    tier: str = "vip1"
    enabled: bool = True
    expires_at: Optional[int] = None
    remaining_uses: Optional[int] = None
    notes: Optional[str] = None


@app.post("/api/admin/subscriptions/grant")
def yi_admin_grant_subscription(req: _GrantSubRequest, request: Request) -> dict:
    """Admin: grant or update a subscription."""
    from api.auth import get_current_user
    from engine.subscriptions import grant_subscription
    user = get_current_user(request)
    if not user or user.get("role") != "owner":
        raise HTTPException(403, "Owner required")
    result = grant_subscription(
        user_id=req.user_id,
        feature_id=req.feature_id,
        tier=req.tier,
        enabled=req.enabled,
        expires_at=req.expires_at,
        remaining_uses=req.remaining_uses,
        granted_by=user["user_id"],
        notes=req.notes,
    )
    return {"status": "ok" if result["ok"] else "error", **result}


@app.post("/api/admin/subscriptions/revoke")
def yi_admin_revoke_subscription(req: dict, request: Request) -> dict:
    """Admin: revoke (disable) a subscription."""
    from api.auth import get_current_user
    from engine.subscriptions import revoke_subscription
    user = get_current_user(request)
    if not user or user.get("role") != "owner":
        raise HTTPException(403, "Owner required")
    user_id = req.get("user_id")
    feature_id = req.get("feature_id")
    if not user_id or not feature_id:
        raise HTTPException(400, "user_id + feature_id required")
    result = revoke_subscription(user_id, feature_id)
    return {"status": "ok", **result}


@app.get("/api/admin/users-list-for-vip")
def yi_admin_users_list_for_vip(request: Request) -> dict:
    """Admin: list all users (for picking who to grant VIP)."""
    from api.auth import get_current_user, AUTH_DB
    import sqlite3
    user = get_current_user(request)
    if not user or user.get("role") != "owner":
        raise HTTPException(403, "Owner required")
    db = sqlite3.connect(AUTH_DB)
    rows = db.execute("SELECT user_id, email, display_name, role FROM users ORDER BY created_at DESC").fetchall()
    db.close()
    return {"status": "ok", "users": [{"user_id": r[0], "email": r[1], "display_name": r[2], "role": r[3]} for r in rows]}


@app.post("/api/tu-vi/safety-check")
def yi_tuvi_safety_check(req: _AnalyzeRequest, request: Request) -> dict:
    """Phát hiện psychological safety patterns trong lá số (Q1 p0027-p0028, Q3 p0186).

    KHÔNG predict — chỉ surface "dấu hiệu kích hoạt nhận thức" + self-care tips.
    """
    from engine.tu_vi.psychological_safety import detect_safety_patterns
    from engine.tu_vi.analyzer import TuViAnalyzer
    from core.chronos import calculate_chronos_state
    person = _resolve_person_from_request(req, request)
    analyzer = TuViAnalyzer(person)
    chronos = calculate_chronos_state(person.birth_datetime_local, person.timezone)
    year_stem = chronos.ganzhi.year.split()[0]
    patterns = detect_safety_patterns(analyzer.la_so, year_stem)
    return {
        "status": "ok",
        "year_stem": year_stem,
        "patterns_triggered": patterns,
        "note": "Đây là 'dấu hiệu kích hoạt nhận thức' theo Iron Rule #6, KHÔNG phải predict tự vẫn. Cổ nhân dùng để gợi mở chăm sóc bản thân, không phải hù dọa.",
        "hotlines": {
            "vi": "Đường Dây Cứu Sống 1800-1567 · Tâm Lý Xanh (online)",
            "vn_psychological_emergency": "Bệnh viện Tâm thần TW · cấp cứu 115",
        },
    }


@app.post("/api/tu-vi/chart-strength")
def yi_tuvi_chart_strength(req: _AnalyzeRequest, request: Request) -> dict:
    """Tính sức mạnh tổng thể lá số dựa trên Miếu Vượng Hãm (Q2 p0102).

    Mỗi chính tinh tại cung tương ứng có 1 level (miếu/vượng/đắc/bình/lạc/hãm).
    Tổng score = đánh giá tổng thể "khí thế" lá số.
    """
    from engine.tu_vi.mieu_vuong_ham import chart_strength
    from engine.tu_vi.analyzer import TuViAnalyzer
    person = _resolve_person_from_request(req, request)
    analyzer = TuViAnalyzer(person)
    result = chart_strength(analyzer.la_so)
    return {"status": "ok", "source": "Q2 p0102 + p0103-p0125", **result}


@app.post("/api/tu-vi/dau-quan")
def yi_tuvi_dau_quan(req: _AnalyzeRequest, request: Request) -> dict:
    """Tính Đẩu Quân (斗君) per lưu niên + 12 tháng lưu nguyệt.

    Đẩu Quân là sao THEO TIME — đi qua các cung mỗi tháng/năm, quyết định
    cát/hung của giai đoạn đó (Q2 p0088 công thức, Q3 p0157 diễn giải).

    Returns Đẩu Quân năm + 12 tháng + diễn giải per palace.
    """
    from engine.tu_vi.dau_quan import (
        compute_dau_quan, compute_dau_quan_for_months, interpret_dau_quan, BRANCHES
    )
    from engine.tu_vi.analyzer import TuViAnalyzer
    from core.chronos import calculate_chronos_state

    person = _resolve_person_from_request(req, request)
    analyzer = TuViAnalyzer(person)
    la_so = analyzer.la_so

    # Need lunar_month + hour_branch from birth
    chronos = calculate_chronos_state(person.birth_datetime_local, person.timezone)
    d_str, m_str, _ = chronos.almanac.lunar_date.split("/")
    lunar_month = int(m_str)

    from datetime import datetime
    dt = datetime.fromisoformat(person.birth_datetime_local)
    hour = dt.hour
    hour_branch = "Tý" if hour >= 23 or hour < 1 else BRANCHES[((hour + 1) // 2) % 12]

    # Year — default current
    year = req.luu_nguyet_year or 2026

    # Get year branch via Ganzhi
    from core.chronos import calculate_chronos_state as ccs
    year_chronos = ccs(f"{year}-06-15T12:00:00", "Asia/Ho_Chi_Minh")
    year_branch = year_chronos.ganzhi.year.split()[1]

    dq_year = compute_dau_quan(year_branch, lunar_month, hour_branch)
    dq_months = compute_dau_quan_for_months(year_branch, lunar_month, hour_branch)

    # Build palace lookup: branch_index → palace_name
    palace_at_branch = {p["branch_index"]: p["name"] for p in la_so["palaces"]}

    # Annotate each month with palace + interpretation
    for m in dq_months:
        bi = m["dau_quan_branch_index"]
        palace = palace_at_branch.get(bi, "?")
        m["palace"] = palace
        # Default to cát interpretation — UI shows both
        interp = interpret_dau_quan(palace, has_cat=True)
        m["interp_cat"] = interp["interpretation"]
        interp_h = interpret_dau_quan(palace, has_cat=False)
        m["interp_hung"] = interp_h["interpretation"]
        m["source_ref"] = interp["source"]

    return {
        "status": "ok",
        "year": year,
        "year_branch": year_branch,
        "lunar_month_birth": lunar_month,
        "hour_branch_birth": hour_branch,
        "dau_quan_year": {
            **dq_year,
            "palace": palace_at_branch.get(dq_year["dau_quan_branch_index"], "?"),
        },
        "dau_quan_months": dq_months,
        "paradigm_note": "Đẩu Quân (Q3 p0157) — đi qua cung X, gặp cát/hung tinh tại đó quyết định cát hung của tháng/năm. KHÔNG đọc cứng — chỉ là 1 layer trong nhiều layer (Đại Vận + Lưu Niên + Tiểu Hạn + Đẩu Quân).",
    }


@app.post("/api/tu-vi/case-studies/match")
def yi_tuvi_case_studies_match(req: _AnalyzeRequest, request: Request) -> dict:
    """Match lá số user với case studies lịch sử (Q3+Q4 Trần Đoàn + Khang Tiết).

    Trả về top 3 historical figures có nét giống pattern lá số.
    Anti-predict: dùng "mỗ" pattern, không phán "anh sẽ giống X".
    """
    from engine.tu_vi.case_matcher import match_cases
    person = _resolve_person_from_request(req, request)
    from engine.tu_vi.analyzer import TuViAnalyzer
    analyzer = TuViAnalyzer(person)
    la_so = analyzer.la_so
    result = match_cases(la_so, top_n=3)
    return {"status": "ok", **result}


@app.get("/api/tu-vi/cach-cuc-pho-bien")
def yi_tuvi_cach_cuc_pho_bien(limit: int = 50, cap_do: str = "") -> dict:
    """Liệt kê 545 cách cục kinh điển từ Phú Thái Vi (Q1).

    Query params:
        limit: số kết quả (default 50)
        cap_do: filter 'thượng' | 'trung' | 'hạ' | 'phá cách' | 'tạp' | '' (all)
    """
    from engine.tu_vi.cach_cuc_dict import all_entries, by_level, stats
    entries = by_level(cap_do) if cap_do else all_entries()
    # Sort by occurrences desc
    entries = sorted(entries, key=lambda x: x.get("occurrences", 0), reverse=True)[:limit]
    return {
        "status": "ok",
        "stats": stats(),
        "filter": {"cap_do": cap_do or "all", "limit": limit},
        "entries": entries,
    }


@app.get("/api/tu-vi/cach-cuc-pho-bien/{name}")
def yi_tuvi_cach_cuc_pho_bien_detail(name: str) -> dict:
    """Lookup 1 cách cục theo tên."""
    from engine.tu_vi.cach_cuc_dict import lookup_by_name
    entry = lookup_by_name(name)
    if not entry:
        raise HTTPException(404, f"Cách cục '{name}' không có trong dictionary 545 cách")
    return {"status": "ok", "entry": entry}


@app.post("/api/tu-vi/match-cach-cuc")
def yi_tuvi_match_cach_cuc(req: dict) -> dict:
    """Match cách cục cho lá số CỤ THỂ (deterministic, không cần DeepSeek runtime).

    Body: {
        "person_key": "self" (optional, sẽ tự cast lá số),
        "stars_at_menh": [...] (optional override),
        "stars_in_palaces": {palace: [stars]} (optional),
        "min_overlap": 2,
        "max_results": 30
    }
    """
    from engine.tu_vi.cach_cuc_dict import match_cach_in_chart
    matches = match_cach_in_chart(
        stars_at_menh=req.get("stars_at_menh", []),
        stars_in_palaces=req.get("stars_in_palaces", {}),
        min_overlap=req.get("min_overlap", 2),
        max_results=req.get("max_results", 30),
    )
    return {"status": "ok", "match_count": len(matches), "matches": matches}


@app.get("/api/tu-vi/concept-dict")
def yi_tuvi_concept_dict(kind: str = "", limit: int = 100) -> dict:
    """Liệt kê concepts (320 thuật ngữ) cho WikiText highlight + lookup."""
    from engine.tu_vi.concept_dict import load_concepts, by_kind, top_terms, stats as cstat
    if kind:
        entries = by_kind(kind)
    else:
        entries = list(load_concepts().values())
    entries = sorted(entries, key=lambda x: x.get("occurrences", 0), reverse=True)[:limit]
    return {
        "status": "ok",
        "stats": cstat(),
        "filter": {"kind": kind or "all", "limit": limit},
        "entries": entries,
    }


# ─── Job tracker (in-memory, simple) ──────────────────────────────────────────
_TUVI_JOBS: dict[str, dict] = {}


@app.post("/api/tu-vi/run-all/{person_key}")
def yi_tuvi_run_all(person_key: str, request: Request, background_tasks: BackgroundTasks) -> dict:
    """Trigger background full pipeline (cach_cuc + dai_van + luu_nien + luu_nguyet) for a person.

    Returns job_id immediately; UI polls /api/tu-vi/job-status/{job_id}.
    """
    from engine.tu_vi.analyzer import TuViAnalyzer, Person
    from api.auth import get_current_user, AUTH_DB
    import sqlite3, uuid

    # Resolve person (scoped per-user)
    user = get_current_user(request)
    uid = user["user_id"] if user else None
    if person_key == "_founder":
        # Owner-only: legacy founder profile was returning anh's hardcoded
        # birth to ANY caller (used to be a guest-mode oracle). Now any
        # non-owner triggering pipeline against _founder gets 404.
        if not user or user.get("role") != "owner":
            raise HTTPException(404, "person not found")
        person = Person(person_key="_founder", name="anh (Founder)",
                        birth_datetime_local="1988-06-05T23:30:00", gender="nam",
                        user_id=uid)
    else:
        if not user:
            raise HTTPException(401, "Login required")
        db = sqlite3.connect(AUTH_DB)
        row = db.execute(
            "SELECT name, gender, birth_datetime_local, timezone FROM user_persons WHERE user_id=? AND person_key=?",
            (user["user_id"], person_key),
        ).fetchone()
        db.close()
        if not row:
            raise HTTPException(404, f"person_key '{person_key}' not found")
        person = Person(person_key=person_key, name=row[0],
                        gender=row[1] or "nam",
                        birth_datetime_local=row[2] or "",
                        timezone=row[3] or "Asia/Ho_Chi_Minh",
                        user_id=user["user_id"])

    job_id = f"tuvi_{person_key}_{uuid.uuid4().hex[:8]}"
    _TUVI_JOBS[job_id] = {
        "job_id": job_id,
        "person_key": person_key,
        "person_name": person.name,
        "status": "queued",
        "progress": 0,
        "total_steps": 4,
        "current_step": "",
        "started_at": time.time(),
        "finished_at": None,
        "error": None,
        "cost_usd": 0.0,
    }

    def _run():
        job = _TUVI_JOBS[job_id]
        try:
            analyzer = TuViAnalyzer(person)
            total_cost = 0.0
            steps = [
                ("cach_cuc", lambda: analyzer.discover_cach_cuc()),
                ("dai_van", lambda: analyzer.dai_van_annotate()),
                ("luu_nien", lambda: analyzer.luu_nien(2026, 2030)),
                ("luu_nguyet", lambda: analyzer.luu_nguyet(2026)),
            ]
            job["status"] = "running"
            for i, (name, fn) in enumerate(steps, 1):
                job["current_step"] = name
                job["progress"] = i - 1
                try:
                    result = fn()
                    total_cost += result.get("cost_usd", 0) or 0
                except Exception as step_err:
                    logger.exception(f"step {name} failed: {step_err}")
                    job["error"] = f"{name}: {step_err}"
                job["progress"] = i
                job["cost_usd"] = round(total_cost, 6)
            job["status"] = "done"
            job["finished_at"] = time.time()
            job["current_step"] = ""
        except Exception as e:
            logger.exception("run_all background failed")
            job["status"] = "error"
            job["error"] = str(e)
            job["finished_at"] = time.time()

    background_tasks.add_task(_run)
    return {"status": "queued", "job_id": job_id, "person_key": person_key}


@app.get("/api/tu-vi/job-status/{job_id}")
def yi_tuvi_job_status(job_id: str) -> dict:
    job = _TUVI_JOBS.get(job_id)
    if not job:
        return {"status": "not_found", "job_id": job_id}
    return {"status": "ok", **job}


# ─── PDF Report ──────────────────────────────────────────────────────────────
@app.get("/api/tu-vi/report-pdf/{person_key}")
def yi_tuvi_report_pdf(person_key: str, request: Request):
    """Generate "Báo cáo Lá Số" PDF for a person. Special (_) keys are owner-only."""
    from fastapi.responses import FileResponse
    from engine.tu_vi.report_pdf import generate_pdf
    from api.auth import get_current_user
    user = get_current_user(request)
    if person_key.startswith("_") and (not user or user.get("role") != "owner"):
        raise HTTPException(403, "owner-only for special person keys")
    uid = user["user_id"] if user else None
    try:
        pdf_path = generate_pdf(person_key, user_id=uid)
    except Exception as e:
        logger.exception("PDF generation failed")
        raise HTTPException(500, f"PDF gen failed: {e}")
    filename = f"bao-cao-la-so-{person_key}.pdf"
    return FileResponse(str(pdf_path), media_type="application/pdf", filename=filename)


# ════════════════════════════════════════════════════════════════════════
# Birth Hour Quiz v2 — multi-round adaptive trait-based hour inference
# ════════════════════════════════════════════════════════════════════════
from api.schemas import (
    BirthHourQuizV2StartRequest,
    BirthHourQuizV2SubmitRequest,
    BirthHourQuizV2SaveRequest,
)

_QUIZ_V2_DB = str(PUBLISHING_PROJECT_ROOT / "data" / "yi_users" / "users.sqlite3")

_QUIZ_V2_MAX_ROUNDS = {"single_round": 1, "two_round": 2, "three_round": 3}


def _quiz_v2_build_final_result(sess: dict, scores: dict, result, status: str) -> dict:
    """Construct human-readable final result with per-candidate reasoning hints."""
    from engine.yi_wiki.birth_hour_quiz_v2.rules.branches import HOUR_RANGES
    top_candidates = [result] if isinstance(result, str) else list(result)
    sorted_scores = sorted(scores.items(), key=lambda kv: -kv[1])
    top_score = sorted_scores[0][1] if sorted_scores else 0
    second = sorted_scores[1][1] if len(sorted_scores) > 1 else 0
    if top_score - second >= 5:
        confidence = "Cao"
    elif top_score - second >= 2:
        confidence = "Vừa"
    else:
        confidence = "Thấp"
    return {
        "status": status,
        "top_chi": top_candidates[0] if top_candidates else None,
        "top_candidates": top_candidates,
        "confidence": confidence,
        "scores": scores,
        "hour_ranges": {
            chi: f"{HOUR_RANGES[chi][0]}h-{HOUR_RANGES[chi][1]}h"
            for chi in top_candidates if chi in HOUR_RANGES
        },
    }


@app.post("/api/yi-wiki/birth-hour-quiz-v2/start")
def quiz_v2_start(req: BirthHourQuizV2StartRequest):
    """Start a new birth-hour quiz session: build candidates, derive traits, return round 1."""
    from engine.yi_wiki.birth_hour_quiz_v2 import session_store
    from engine.yi_wiki.birth_hour_quiz_v2.pillars import build_candidates
    from engine.yi_wiki.birth_hour_quiz_v2.derivation import derive_all_traits
    from engine.yi_wiki.birth_hour_quiz_v2.engine import detect_strategy, generate_questions

    try:
        session_store.init_schema(_QUIZ_V2_DB)

        hour_range = (req.hour_range.start, req.hour_range.end) if req.hour_range else None
        candidates_list = build_candidates(
            req.birth_date, req.timezone, hour_range, gender=req.gender,
        )
        if not candidates_list:
            return {"status": "error", "message": "Không có candidate nào trong khoảng giờ này"}

        strategy = detect_strategy([c["chi"] for c in candidates_list])
        predictions = derive_all_traits(candidates_list)

        questions = generate_questions(
            strategy=strategy,
            candidates=[c["chi"] for c in candidates_list],
            predictions=predictions,
            used_dimensions=set(),
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception("quiz_v2_start failed")
        return {
            "status": "error",
            "message": f"Engine lỗi khi tạo quiz: {type(e).__name__}: {str(e)[:200]}",
            "hint": ("Nếu Anh chọn 'Không nhớ gì' (12 candidates) có thể LLM overload. "
                     "Thử range hẹp hơn: vd 6h-12h, 19h-24h, 12h-18h."),
        }

    sid = session_store.create_session(
        _QUIZ_V2_DB,
        user_id=None,
        birth_date=req.birth_date,
        timezone=req.timezone,
        hour_range=hour_range,
        gender=req.gender,
        candidates_initial=[c["chi"] for c in candidates_list],
        strategy=strategy,
    )
    session_store.update_session(
        _QUIZ_V2_DB, sid,
        rounds_data=[{
            "round_num": 1,
            "predictions": predictions,
            "questions": questions,
            "answers": None,
        }],
    )

    return {
        "status": "ok",
        "session_id": sid,
        "candidates": [c["chi"] for c in candidates_list],
        "strategy": strategy,
        "round_1": {
            "round_num": 1,
            "total_rounds": _QUIZ_V2_MAX_ROUNDS[strategy],
            "questions": questions,
        },
    }


@app.post("/api/yi-wiki/birth-hour-quiz-v2/submit-round")
def quiz_v2_submit_round(req: BirthHourQuizV2SubmitRequest):
    """Score a round's answers; return next round OR final result."""
    from engine.yi_wiki.birth_hour_quiz_v2 import session_store
    from engine.yi_wiki.birth_hour_quiz_v2.scoring import score_answer, after_round
    from engine.yi_wiki.birth_hour_quiz_v2.engine import generate_questions

    sess = session_store.get_session(_QUIZ_V2_DB, req.session_id)
    if not sess:
        return {"status": "error", "message": "session not found"}

    rd = sess["rounds_data"]
    round_entry = next((r for r in rd if r["round_num"] == req.round_num), None)
    if not round_entry:
        return {"status": "error", "message": "round not found"}

    candidates = sess["candidates_remaining"]
    scores = dict(sess["accumulated_scores"])
    used = set()
    # All used dimensions across all rounds (so next round won't repeat)
    for r in rd:
        for q in r["questions"]:
            used.add(q["id"])

    for q in round_entry["questions"]:
        ans = req.answers.get(q["id"])
        if not ans:
            continue
        delta = score_answer(candidates, q, ans)
        for c, v in delta.items():
            scores[c] = scores.get(c, 0) + v

    round_entry["answers"] = req.answers
    round_entry["round_scores_after"] = dict(scores)

    max_rounds = _QUIZ_V2_MAX_ROUNDS[sess["strategy"]]
    status, result = after_round(scores, candidates, req.round_num, max_rounds)

    if status in {"FINAL", "FINAL_UNCERTAIN"}:
        final_result = _quiz_v2_build_final_result(sess, scores, result, status)
        session_store.update_session(
            _QUIZ_V2_DB, req.session_id,
            accumulated_scores=scores, rounds_data=rd,
        )
        session_store.mark_final(_QUIZ_V2_DB, req.session_id, final_result=final_result)
        return {
            "status": status,
            "scores": scores,
            "candidates_remaining": result if isinstance(result, list) else [result],
            "next_round": None,
            "final_result": final_result,
        }

    # CONTINUE: build next round
    survivors = result
    predictions = round_entry["predictions"]
    next_round_num = req.round_num + 1
    next_questions = generate_questions(
        strategy=sess["strategy"],
        candidates=survivors,
        predictions=predictions,
        used_dimensions=used,
    )
    rd.append({
        "round_num": next_round_num,
        "predictions": predictions,
        "questions": next_questions,
        "answers": None,
    })
    session_store.update_session(
        _QUIZ_V2_DB, req.session_id,
        candidates_remaining=survivors,
        accumulated_scores=scores,
        rounds_data=rd,
    )
    return {
        "status": "CONTINUE",
        "scores": scores,
        "candidates_remaining": survivors,
        "next_round": {
            "round_num": next_round_num,
            "total_rounds": max_rounds,
            "questions": next_questions,
        },
        "final_result": None,
    }


@app.get("/api/yi-wiki/birth-hour-quiz-v2/session/{session_id}")
def quiz_v2_get_session(session_id: str):
    from engine.yi_wiki.birth_hour_quiz_v2 import session_store
    sess = session_store.get_session(_QUIZ_V2_DB, session_id)
    if not sess:
        return {"api_status": "error", "message": "session not found"}
    return {"api_status": "ok", "session": sess}


@app.post("/api/yi-wiki/birth-hour-quiz-v2/save-result")
def quiz_v2_save_result(req: BirthHourQuizV2SaveRequest):
    """Save inferred hour to a person's profile (via engine.yi_hermes.persons)."""
    from engine.yi_wiki.birth_hour_quiz_v2 import session_store
    from engine.yi_wiki.birth_hour_quiz_v2.rules.branches import HOUR_RANGES

    sess = session_store.get_session(_QUIZ_V2_DB, req.session_id)
    if not sess or sess["status"] != "final":
        return {"status": "error", "message": "session not finalized"}
    fr = sess.get("final_result") or {}
    top_chi = fr.get("top_chi")
    if not top_chi:
        return {"status": "error", "message": "no top candidate"}

    chi_start, chi_end = HOUR_RANGES[top_chi]
    midpoint_hour = (chi_start + 1) % 24 if chi_start <= chi_end else 0
    new_birth_dt = f"{sess['birth_date']}T{midpoint_hour:02d}:00:00"

    try:
        from engine.yi_hermes.persons import update_person
        update_person(req.person_id, {
            "birth_datetime_local": new_birth_dt,
            "birth_confidence": "approx_hour",
            "source": f"birth_hour_quiz_v2:{req.session_id}",
        })
        return {
            "status": "ok",
            "person_id": req.person_id,
            "birth_datetime_local": new_birth_dt,
            "inferred_chi": top_chi,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


_DIST_ROOT = _Path(__file__).resolve().parent.parent / "client" / "webapp" / "dist"
if _DIST_ROOT.exists() and (_DIST_ROOT / "index.html").exists():
    _ASSETS_DIR = _DIST_ROOT / "assets"
    if _ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(_ASSETS_DIR)), name="assets")
    _QUE_IMAGES_DIR = _DIST_ROOT / "que-images"
    if _QUE_IMAGES_DIR.exists():
        app.mount("/que-images", StaticFiles(directory=str(_QUE_IMAGES_DIR)), name="que-images")

    # index.html PHẢI no-cache: tên file asset đã băm (immutable), nhưng index.html
    # trỏ tới chúng — nếu browser cache index.html cũ thì user kẹt bundle cũ (stale).
    # Bug 2026-06-16: Anh thấy lá số khác thiếu 'đào sâu/soi mình' do index.html cached.
    _NO_CACHE = {"Cache-Control": "no-cache, must-revalidate"}

    @app.api_route("/{full_path:path}", methods=["GET", "HEAD"], include_in_schema=False)
    async def _serve_spa(full_path: str):
        # Don't intercept api/figures/assets/que-images
        if full_path.startswith(("api/", "figures/", "assets/", "que-images/")):
            from fastapi import HTTPException
            raise HTTPException(status_code=404)
        candidate = _DIST_ROOT / full_path
        if candidate.is_file() and full_path:
            return _FileResponse(candidate)
        # SPA fallback (mọi route ảo) → index.html, KHÔNG cache
        return _FileResponse(_DIST_ROOT / "index.html", headers=_NO_CACHE)
