"""Founder's Bát Tự chart — now delegated to the native engine.

HISTORY: this module used to hardcode the founder's pillars (FOUNDER_PILLARS_RAW)
because `core.chronos` had broken can-chi math (wrong day-cycle epoch + solar-month
month boundary + no 早子時). That engine bug is now FIXED via sxtwl (2026-06-03):
`calculate_chronos_state` computes can-chi astronomically (立春 year boundary, 節
month boundary, continuous day cycle, 早子時 day-roll per Thiệu Vĩ Hoa).

So the manual override is retired — `cast_founder_bat_tu()` delegates to the native
`cast_bat_tu()`, which now produces the CORRECT chart:

    Mậu Thìn / Mậu Ngọ / Nhâm Thìn / Canh Tý  →  Day Master Nhâm (Dương Thủy)

(The old hardcode said Ất Hợi / Day Master Ất, which was itself wrong — it trusted
the buggy engine baseline. Verified against sxtwl + the world anchor 2000-01-01 =
Mậu Ngọ.)

See `data/yi_hermes/founder_profile.md` for the full chart + verification.
"""

from __future__ import annotations

from engine.bat_tu.cast import cast_bat_tu

FOUNDER_BIRTH = {
    "birth_datetime_local": "1988-06-05T23:30:00",
    "timezone": "Asia/Ho_Chi_Minh",
    "gender": "nam",
    "day_pillar_convention": "早子時 (early Tý)",
}


def cast_founder_bat_tu() -> dict:
    """Compose the founder's full Bát Tự chart via the native engine.

    Returns the standard `cast_bat_tu()` shape (tu_tru, ngu_hanh, dung_than,
    cach_cuc, than_sat, dai_van, …). The engine now applies the 早子時 convention
    by default, matching the founder's birth (23:30 → Nhâm Thìn day pillar).
    """
    return cast_bat_tu(
        birth_datetime_local=FOUNDER_BIRTH["birth_datetime_local"],
        timezone=FOUNDER_BIRTH["timezone"],
        gender=FOUNDER_BIRTH["gender"],
    )


def build_founder_pillars() -> dict[str, dict]:
    """Return the 4 pillars dict (same shape as engine.bat_tu.tu_tru)."""
    return cast_founder_bat_tu()["tu_tru"]["pillars"]
