from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LunarDate:
    day: int
    month: int
    year: int
    is_leap: bool = False


def _jd_from_date(day: int, month: int, year: int) -> int:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jd = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    if jd < 2299161:
        jd = day + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083
    return jd


def _jd_to_date(jd: int) -> tuple[int, int, int]:
    if jd > 2299160:
        a = jd + 32044
        b = (4 * a + 3) // 146097
        c = a - (b * 146097) // 4
    else:
        b = 0
        c = jd + 32082
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = b * 100 + d - 4800 + m // 10
    return day, month, year


def _new_moon(k: int) -> float:
    from math import sin, pi

    t = k / 1236.85
    t2 = t * t
    t3 = t2 * t
    dr = pi / 180
    jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * t2 - 0.000000155 * t3
    jd1 += 0.00033 * sin((166.56 + 132.87 * t - 0.009173 * t2) * dr)
    m = 359.2242 + 29.10535608 * k - 0.0000333 * t2 - 0.00000347 * t3
    mpr = 306.0253 + 385.81691806 * k + 0.0107306 * t2 + 0.00001236 * t3
    f = 21.2964 + 390.67050646 * k - 0.0016528 * t2 - 0.00000239 * t3
    c1 = (0.1734 - 0.000393 * t) * sin(m * dr) + 0.0021 * sin(2 * dr * m)
    c1 -= 0.4068 * sin(mpr * dr) + 0.0161 * sin(dr * 2 * mpr)
    c1 -= 0.0004 * sin(dr * 3 * mpr)
    c1 += 0.0104 * sin(dr * 2 * f) - 0.0051 * sin(dr * (m + mpr))
    c1 -= 0.0074 * sin(dr * (m - mpr)) + 0.0004 * sin(dr * (2 * f + m))
    c1 -= 0.0004 * sin(dr * (2 * f - m)) - 0.0006 * sin(dr * (2 * f + mpr))
    c1 += 0.0010 * sin(dr * (2 * f - mpr)) + 0.0005 * sin(dr * (2 * mpr + m))
    if t < -11:
        deltat = 0.001 + 0.000839 * t + 0.0002261 * t2 - 0.00000845 * t3 - 0.000000081 * t * t3
    else:
        deltat = -0.000278 + 0.000265 * t + 0.000262 * t2
    return jd1 + c1 - deltat


def _sun_longitude(jdn: float) -> float:
    from math import sin, pi

    t = (jdn - 2451545.0) / 36525
    t2 = t * t
    dr = pi / 180
    m = 357.52910 + 35999.05030 * t - 0.0001559 * t2 - 0.00000048 * t * t2
    l0 = 280.46645 + 36000.76983 * t + 0.0003032 * t2
    dl = (1.914600 - 0.004817 * t - 0.000014 * t2) * sin(dr * m)
    dl += (0.019993 - 0.000101 * t) * sin(dr * 2 * m) + 0.000290 * sin(dr * 3 * m)
    l = l0 + dl
    l *= dr
    l -= pi * 2 * int(l / (pi * 2))
    return l


def _get_new_moon_day(k: int, time_zone: float) -> int:
    return int(_new_moon(k) + 0.5 + time_zone / 24)


def _get_sun_longitude(day_number: int, time_zone: float) -> int:
    from math import pi

    return int(_sun_longitude(day_number - 0.5 - time_zone / 24) / pi * 6)


def _get_lunar_month11(year: int, time_zone: float) -> int:
    off = _jd_from_date(31, 12, year) - 2415021
    k = int(off / 29.530588853)
    nm = _get_new_moon_day(k, time_zone)
    sun_long = _get_sun_longitude(nm, time_zone)
    if sun_long >= 9:
        nm = _get_new_moon_day(k - 1, time_zone)
    return nm


def _get_leap_month_offset(a11: int, time_zone: float) -> int:
    k = int((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    last = 0
    i = 1
    arc = _get_sun_longitude(_get_new_moon_day(k + i, time_zone), time_zone)
    while arc != last and i < 14:
        last = arc
        i += 1
        arc = _get_sun_longitude(_get_new_moon_day(k + i, time_zone), time_zone)
    return i - 1


# ─── Public API now delegates to sxtwl (project-wide single calendar — #15) ──────
# The Hồ Ngọc Đức (VN, UTC+7) algorithm above is kept for reference, but to end the
# VN/CN mixing the founder chose to standardize the whole project on sxtwl (CN
# astronomical lunar — same system Tử Vi / Mai Hoa / can-chi pillars use). `time_zone`
# is kept for signature compatibility but ignored.

def solar_to_lunar(day: int, month: int, year: int, time_zone: float = 7.0) -> LunarDate:
    import sxtwl

    d = sxtwl.fromSolar(year, month, day)
    return LunarDate(
        day=d.getLunarDay(),
        month=d.getLunarMonth(),
        year=d.getLunarYear(),
        is_leap=bool(d.isLunarLeap()),
    )


def lunar_to_solar(day: int, month: int, year: int, is_leap: bool = False, time_zone: float = 7.0) -> tuple[int, int, int]:
    import sxtwl

    d = sxtwl.fromLunar(year, month, day, bool(is_leap))
    return (d.getSolarDay(), d.getSolarMonth(), d.getSolarYear())
