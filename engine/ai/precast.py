"""Auto-precast helper: route sage_tag → engine cast function.

This module is responsible for taking a birth payload + optional event
timestamp and producing per-sage `precast_data` dicts ready to embed in
kanban task bodies. Sages MUST NOT recompute — they consume this JSON.

Birth-based sages: tu_vi, bat_tu, ha_lac
Event-based sages: mai_hoa, luc_hao, lien_hoa
Hybrid:            western (currently birth-only via collectors.jpl_horizons)
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)


def _safe_cast(fn, **kwargs) -> dict | None:
    """Wrap an engine cast with broad exception → log + return None.

    Sages tolerate missing precast (they annotate engine_gap), so a partial
    failure in one cast must not break the whole consultation.
    """
    try:
        return fn(**kwargs)
    except Exception as e:  # noqa: BLE001
        log.warning("precast %s failed: %s", fn.__qualname__, e)
        return {"_precast_error": str(e), "_engine": fn.__qualname__}


# ─── Birth-based sages ───────────────────────────────────────────────────────


def _precast_bat_tu(birth: dict) -> dict | None:
    from engine.bat_tu.cast import cast_bat_tu

    return _safe_cast(
        cast_bat_tu,
        birth_datetime_local=birth["birth_datetime_local"],
        timezone=birth.get("timezone", "Asia/Ho_Chi_Minh"),
        gender=birth.get("gender", "nam"),
    )


def _precast_ha_lac(birth: dict) -> dict | None:
    from engine.ha_lac.cast import cast_ha_lac

    return _safe_cast(
        cast_ha_lac,
        birth_datetime_local=birth["birth_datetime_local"],
        timezone=birth.get("timezone", "Asia/Ho_Chi_Minh"),
        gender=birth.get("gender", "nam"),
    )


def _precast_tu_vi(birth: dict) -> dict | None:
    """Tử Vi requires lunar date + hour_branch. If birth payload only has
    Gregorian datetime, convert first.
    """
    # Direct lunar mode if provided
    if all(k in birth for k in ("lunar_month", "lunar_day", "hour_branch", "year_stem", "year_branch")):
        from engine.tu_vi.an_sao import cast_la_so

        return _safe_cast(
            cast_la_so,
            lunar_month=birth["lunar_month"],
            lunar_day=birth["lunar_day"],
            hour_branch=birth["hour_branch"],
            year_stem=birth["year_stem"],
            year_branch=birth["year_branch"],
            gender=birth.get("gender", "nam"),
        )

    # Convert Gregorian → lunar via core.chronos
    if "birth_datetime_local" in birth:
        try:
            from core.chronos import calculate_chronos_state
            from engine.tu_vi.an_sao import cast_la_so

            cs = calculate_chronos_state(
                birth["birth_datetime_local"],
                birth.get("timezone", "Asia/Ho_Chi_Minh"),
            )
            # ganzhi entries are space-joined "Stem Branch" strings (e.g. "Ất Sửu")
            year_parts = cs.ganzhi.year.split()
            hour_parts = cs.ganzhi.hour.split()
            # lunar_date is "DD/MM/YYYY"
            ld = cs.almanac.lunar_date.split("/")
            return _safe_cast(
                cast_la_so,
                lunar_month=int(ld[1]),
                lunar_day=int(ld[0]),
                hour_branch=hour_parts[1],
                year_stem=year_parts[0],
                year_branch=year_parts[1],
                gender=birth.get("gender", "nam"),
            )
        except Exception as e:  # noqa: BLE001
            log.warning("tu_vi auto-convert failed: %s", e)
            return {"_precast_error": str(e), "_engine": "cast_la_so (auto-convert)"}

    return None


# ─── Event-based sages ───────────────────────────────────────────────────────


def _precast_lien_hoa(event: dict) -> dict | None:
    """Liên Hoa needs 2 numbers (tâm-ý) — caller supplies via event payload."""
    if "n1" in event and "n2" in event:
        try:
            from engine.lien_hoa.cast import cast_lien_hoa

            return _safe_cast(cast_lien_hoa, n1=event["n1"], n2=event["n2"])
        except Exception as e:  # noqa: BLE001
            return {"_precast_error": str(e), "_engine": "cast_lien_hoa"}
    return None


def _precast_luc_hao(event: dict) -> dict | None:
    """Lục Hào needs 6 hexagram lines from coin toss — caller supplies."""
    if "lines" in event and len(event["lines"]) == 6:
        try:
            from engine.luc_hao.cast import cast_luc_hao

            return _safe_cast(
                cast_luc_hao,
                lines=event["lines"],
                event_datetime_local=event.get("event_datetime_local"),
            )
        except Exception as e:  # noqa: BLE001
            return {"_precast_error": str(e), "_engine": "cast_luc_hao"}
    return None


def _precast_mai_hoa(event: dict) -> dict | None:
    """Mai Hoa: NNTT from event timestamp; engine entrypoint may vary."""
    try:
        from engine.mai_hoa.cast import cast_mai_hoa  # type: ignore[import-not-found]

        return _safe_cast(
            cast_mai_hoa,
            event_datetime_local=event.get("event_datetime_local"),
        )
    except ImportError:
        # Mai Hoa engine not yet packaged with cast.py — leave to sage's engine_gap.
        return None


def _precast_western(birth: dict) -> dict | None:
    """Western astrology — currently we only have planet positions via
    collectors.jpl_horizons. A full natal chart engine is a known engine_gap.
    """
    try:
        from collectors.jpl_horizons import get_planet_positions

        if "birth_datetime_local" not in birth:
            return None
        return _safe_cast(
            get_planet_positions,
            datetime_local=birth["birth_datetime_local"],
            timezone=birth.get("timezone", "Asia/Ho_Chi_Minh"),
        )
    except Exception as e:  # noqa: BLE001
        return {"_precast_error": str(e), "_engine": "get_planet_positions"}


# ─── Public router ───────────────────────────────────────────────────────────


_BIRTH_SAGES = {"bat_tu", "ha_lac", "tu_vi", "western"}
_EVENT_SAGES = {"mai_hoa", "luc_hao", "lien_hoa"}


def precast_for_sages(
    sages: list[str],
    *,
    birth: dict | None = None,
    event: dict | None = None,
) -> dict[str, dict]:
    """Build precast_data dict for the given sage tags.

    Args:
        sages: list of sage tags (e.g. ["bat_tu", "tu_vi", "mai_hoa"]).
        birth: birth payload — keys: birth_datetime_local, timezone, gender,
            optionally lunar_* + year_stem + year_branch.
        event: event payload — keys depend on school (lien_hoa: n1/n2,
            luc_hao: lines, mai_hoa: event_datetime_local).

    Returns dict: {sage_tag: precast_output_or_error_envelope}.
    Sages whose precast returns None are omitted (sage will see no
    precast_data and annotate engine_gap).
    """
    out: dict[str, dict] = {}
    for tag in sages:
        result: dict | None = None
        if tag in _BIRTH_SAGES:
            if birth:
                if tag == "bat_tu":
                    result = _precast_bat_tu(birth)
                elif tag == "ha_lac":
                    result = _precast_ha_lac(birth)
                elif tag == "tu_vi":
                    result = _precast_tu_vi(birth)
                elif tag == "western":
                    result = _precast_western(birth)
        elif tag in _EVENT_SAGES:
            if event is not None:
                if tag == "lien_hoa":
                    result = _precast_lien_hoa(event)
                elif tag == "luc_hao":
                    result = _precast_luc_hao(event)
                elif tag == "mai_hoa":
                    result = _precast_mai_hoa(event)
        if result is not None:
            out[tag] = result
    return out


def required_inputs(sage_tag: str) -> dict[str, Any]:
    """Describe what payload a sage tag needs — useful for UI hints."""
    if sage_tag == "bat_tu":
        return {"birth": ["birth_datetime_local", "timezone?", "gender?"]}
    if sage_tag == "ha_lac":
        return {"birth": ["birth_datetime_local", "timezone?", "gender?"]}
    if sage_tag == "tu_vi":
        return {
            "birth": [
                "birth_datetime_local OR (lunar_month + lunar_day + hour_branch + year_stem + year_branch)",
                "gender?",
            ]
        }
    if sage_tag == "western":
        return {"birth": ["birth_datetime_local", "timezone?"]}
    if sage_tag == "lien_hoa":
        return {"event": ["n1", "n2"]}
    if sage_tag == "luc_hao":
        return {"event": ["lines (6 ints)", "event_datetime_local?"]}
    if sage_tag == "mai_hoa":
        return {"event": ["event_datetime_local?"]}
    return {}
