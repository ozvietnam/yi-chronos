from __future__ import annotations

import json
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

NOAA_KP_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
CACHE_PATH = Path("data/cache/noaa_kp.json")


def _read_cache() -> dict[str, object] | None:
    if not CACHE_PATH.exists():
        return None
    return json.loads(CACHE_PATH.read_text())


def _write_cache(payload: dict[str, object]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(payload, indent=2))


def get_current_kp(timeout: float = 2.5) -> dict[str, object]:
    try:
        with urlopen(NOAA_KP_URL, timeout=timeout) as response:
            rows = json.loads(response.read().decode("utf-8"))
        latest = rows[-1]
        payload = {
            "kp_index": float(latest[1]),
            "observed_at": latest[0],
            "source": "NOAA_SWPC",
            "stale": False,
            "fetched_at": int(time.time()),
        }
        _write_cache(payload)
        return payload
    except (OSError, URLError, ValueError, IndexError, KeyError):
        cached = _read_cache()
        if cached:
            cached["stale"] = True
            return cached
        return {
            "kp_index": 2.0,
            "observed_at": None,
            "source": "NOAA_SWPC_FALLBACK",
            "stale": True,
            "fetched_at": int(time.time()),
        }

