from __future__ import annotations

from datetime import datetime
from math import cos, pi, sin

from pydantic import BaseModel

from core.chronos import ChronosState
from core.config import ALGORITHM_VERSION


class TemporalFeatures(BaseModel):
    vector: list[float]
    names: list[str]
    algorithm_version: str = ALGORITHM_VERSION


def _cycle_pair(position: float) -> tuple[float, float]:
    angle = 2 * pi * position
    return round(sin(angle), 6), round(cos(angle), 6)


def encode_temporal_features(state: ChronosState) -> TemporalFeatures:
    local_dt = datetime.fromisoformat(state.local_datetime)
    day_of_year = local_dt.timetuple().tm_yday
    hour_fraction = (local_dt.hour * 3600 + local_dt.minute * 60 + local_dt.second) / 86400
    year_fraction = day_of_year / 366
    month_fraction = (local_dt.day - 1) / 31
    cycle_fraction = state.cycle_60_idx / 60
    solar_fraction = state.solar_term.solar_longitude / 360
    moon_fraction = state.moon_phase.phase_norm

    names = [
        "hour_sin",
        "hour_cos",
        "year_sin",
        "year_cos",
        "month_sin",
        "month_cos",
        "cycle_60_sin",
        "cycle_60_cos",
        "solar_sin",
        "solar_cos",
        "moon_sin",
        "moon_cos",
    ]
    vector = [
        *_cycle_pair(hour_fraction),
        *_cycle_pair(year_fraction),
        *_cycle_pair(month_fraction),
        *_cycle_pair(cycle_fraction),
        *_cycle_pair(solar_fraction),
        *_cycle_pair(moon_fraction),
    ]
    return TemporalFeatures(vector=list(vector), names=names)

