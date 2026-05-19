from __future__ import annotations

import json
import math
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

PLANETS = [
    {"id": "199", "name_vi": "Sao Thủy", "fallback_au": 0.39, "period_days": 88},
    {"id": "299", "name_vi": "Sao Kim", "fallback_au": 0.72, "period_days": 225},
    {"id": "399", "name_vi": "Trái Đất", "fallback_au": 1.0, "period_days": 365},
    {"id": "499", "name_vi": "Sao Hỏa", "fallback_au": 1.52, "period_days": 687},
    {"id": "599", "name_vi": "Sao Mộc", "fallback_au": 5.2, "period_days": 4333},
    {"id": "699", "name_vi": "Sao Thổ", "fallback_au": 9.58, "period_days": 10759},
    {"id": "799", "name_vi": "Sao Thiên Vương", "fallback_au": 19.2, "period_days": 30687},
    {"id": "899", "name_vi": "Sao Hải Vương", "fallback_au": 30.05, "period_days": 60190},
]

CACHE_PATH = Path("data/cache/jpl_planets.json")
HORIZONS_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"


def _query_planet(planet_id: str, timestamp: datetime) -> dict[str, float | str]:
    start = timestamp.strftime("'%Y-%b-%d %H:%M'")
    stop = (timestamp + timedelta(days=1)).strftime("'%Y-%b-%d %H:%M'")
    params = {
        "format": "json",
        "COMMAND": planet_id,
        "OBJ_DATA": "NO",
        "MAKE_EPHEM": "YES",
        "EPHEM_TYPE": "VECTORS",
        "CENTER": "500@10",
        "START_TIME": start,
        "STOP_TIME": stop,
        "STEP_SIZE": "'1 d'",
        "REF_PLANE": "ECLIPTIC",
        "REF_SYSTEM": "J2000",
        "OUT_UNITS": "AU-D",
        "VEC_TABLE": "2",
        "CSV_FORMAT": "YES",
        "VEC_LABELS": "YES",
    }
    with urlopen(f"{HORIZONS_URL}?{urlencode(params)}", timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if "error" in payload:
        raise RuntimeError(str(payload["error"]))
    result = payload["result"]
    rows = result.split("$$SOE", 1)[1].split("$$EOE", 1)[0].strip().splitlines()
    columns = [part.strip() for part in rows[0].split(",")]
    x, y, z = (float(columns[index]) for index in (2, 3, 4))
    vx, vy, vz = (float(columns[index]) for index in (5, 6, 7))
    distance = math.sqrt(x * x + y * y + z * z)
    longitude = (math.degrees(math.atan2(y, x)) + 360) % 360
    latitude = math.degrees(math.atan2(z, math.sqrt(x * x + y * y)))
    return {
        "x_au": x,
        "y_au": y,
        "z_au": z,
        "vx_au_per_day": vx,
        "vy_au_per_day": vy,
        "vz_au_per_day": vz,
        "distance_au": distance,
        "ecliptic_longitude_deg": longitude,
        "ecliptic_latitude_deg": latitude,
    }


def _fallback_positions(timestamp: datetime) -> dict[str, object]:
    days = timestamp.timestamp() / 86400
    planets = []
    for index, spec in enumerate(PLANETS):
        angle = (days / spec["period_days"] + index * 0.137) * math.tau
        distance = spec["fallback_au"]
        planets.append(
            {
                **spec,
                "x_au": math.cos(angle) * distance,
                "y_au": math.sin(angle) * distance,
                "z_au": math.sin(angle * 0.37) * distance * 0.03,
                "vx_au_per_day": 0,
                "vy_au_per_day": 0,
                "vz_au_per_day": 0,
                "distance_au": distance,
                "ecliptic_longitude_deg": (math.degrees(angle) + 360) % 360,
                "ecliptic_latitude_deg": math.sin(angle * 0.37) * 1.7,
            }
        )
    return {
        "timestamp_utc": timestamp.replace(second=0, microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": "LOCAL_FALLBACK",
        "reference_frame": "heliocentric ecliptic J2000 approximation",
        "stale": True,
        "planets": planets,
    }


def get_planet_positions(timestamp: datetime | None = None) -> dict[str, object]:
    timestamp = (timestamp or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(second=0, microsecond=0)
    try:
      planets = []
      for spec in PLANETS:
          vector = _query_planet(spec["id"], timestamp)
          planets.append({**spec, **vector})
      result = {
          "timestamp_utc": timestamp.isoformat().replace("+00:00", "Z"),
          "source": "NASA/JPL Horizons",
          "reference_frame": "heliocentric ecliptic J2000, geometric vectors, AU-D",
          "stale": False,
          "planets": planets,
      }
      CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
      CACHE_PATH.write_text(json.dumps({**result, "cached_at": int(time.time())}, ensure_ascii=False, indent=2))
      return result
    except Exception:
      if CACHE_PATH.exists():
          cached = json.loads(CACHE_PATH.read_text())
          cached["stale"] = True
          return cached
      return _fallback_positions(timestamp)
