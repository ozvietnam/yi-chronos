from __future__ import annotations

from hashlib import sha256
from uuid import uuid4

from pydantic import BaseModel

from core.chronos import calculate_chronos_state
from core.config import ALGORITHM_VERSION


ELEMENTS = ("mộc", "hỏa", "thổ", "kim", "thủy")


class BirthProfile(BaseModel):
    birth_datetime_local: str
    timezone: str
    location_ref: str | None = None
    birth_precision: str = "exact"
    gender_optional: str | None = None


def profile_hash(profile: BirthProfile) -> str:
    raw = "|".join(
        [
            profile.birth_datetime_local,
            profile.timezone,
            profile.location_ref or "",
            profile.birth_precision,
            profile.gender_optional or "",
        ]
    )
    return sha256(raw.encode("utf-8")).hexdigest()


def five_element_bias(profile: BirthProfile) -> dict[str, float]:
    """Real Bát Tự ngũ hành distribution (normalized 0..1), NOT a SHA256 hash (#26).

    Casts the Tứ Trụ and uses the verified weighted element count (tàng can included),
    so the value displayed under the 'ngũ hành' label is authentic — and so the
    downstream sync_score (resonance.py reads thủy/hỏa) reflects the real chart.
    """
    from engine.bat_tu.cast import cast_bat_tu

    g = (profile.gender_optional or "").strip().lower()
    gender = "nữ" if g in ("nữ", "nu", "female", "f", "woman", "w") else "nam"
    try:
        chart = cast_bat_tu(
            birth_datetime_local=profile.birth_datetime_local,
            timezone=profile.timezone,
            gender=gender,
        )
        counts = chart["ngu_hanh"]["counts"]  # {mộc, hỏa, thổ, kim, thủy: float}
    except Exception:
        # Degrade gracefully to an even distribution rather than fabricating bias.
        counts = {el: 1.0 for el in ELEMENTS}
    total = sum(counts.get(el, 0.0) for el in ELEMENTS) or 1.0
    return {el: round(counts.get(el, 0.0) / total, 3) for el in ELEMENTS}


def build_personal_vector(profile: BirthProfile) -> dict[str, object]:
    state = calculate_chronos_state(profile.birth_datetime_local, profile.timezone)
    return {
        "five_element_bias": five_element_bias(profile),
        "pillar_summary": state.ganzhi.model_dump(),
        "birth_profile_hash": profile_hash(profile),
        "algorithm_version": ALGORITHM_VERSION,
    }


def generate_milestone_prompts(profile: BirthProfile) -> list[dict[str, object]]:
    state = calculate_chronos_state(profile.birth_datetime_local, profile.timezone)
    birth_year = int(profile.birth_datetime_local[:4])
    domains = ("sức khỏe", "công việc", "quan hệ")
    labels = {
        "sức khỏe": "sức khỏe / áp lực thân thể",
        "công việc": "công việc / hướng đi",
        "quan hệ": "quan hệ / gia đình",
    }
    prompts = []
    for index, age in enumerate((21, 27, 33)):
        start = birth_year + age
        strength = round(0.58 + ((state.cycle_60_idx + index * 7) % 20) / 100, 2)
        domain = domains[index]
        prompts.append(
            {
                "prompt_id": f"p_{uuid4().hex[:12]}",
                "window_start": f"{start}-01-01",
                "window_end": f"{start + 1}-12-31",
                "domain": domain,
                "signal_strength": strength,
                "prompt_text": (
                    f"Khung {start}-{start + 1} có tín hiệu biến động về {labels[domain]}. "
                    "Bạn có nhớ điều gì đáng kể không?"
                ),
            }
        )
    return prompts
