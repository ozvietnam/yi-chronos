"""Natal universe data — bầu trời THẬT (skyfield) + địa bàn Tử Vi KÝ HIỆU.

Gộp dữ liệu cho viz "lá số trên nền vũ trụ":
  - sky: vị trí hoàng đạo THẬT của 10 thiên thể lúc sinh (engine.sky / DE440s) + Asc.
  - dia_ban: 12 cung địa chi (neo TIẾT KHÍ = vị trí thật của Mặt Trời) + cung Mệnh.

Tôn trọng giả tướng (Iron #4/#6): nền THẬT + lớp KÝ HIỆU suy TỪ nền, KHÔNG rắc
"sao Tử Vi" lên bầu trời thật. Cầu nối hai lớp = vị trí thật của Mặt Trời.
"""
from __future__ import annotations

from datetime import datetime, timezone

from engine.sky import calculate_sky_chart
from engine.tu_vi import an_sao
from engine.tu_vi.chinh_tinh import get_chinh_tinh_by_name
from engine.yi_wiki.lich_conversion import SolarDateTime, solar_to_lunar

# Tý=0 .. Hợi=11
CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# Tâm 中氣 (độ hoàng đạo) cho từng chi — neo địa bàn vào vị trí THẬT của Mặt Trời.
CHI_LON_CENTER = {
    "Mão": 0.0, "Thìn": 30.0, "Tỵ": 60.0, "Ngọ": 90.0, "Mùi": 120.0, "Thân": 150.0,
    "Dậu": 180.0, "Tuất": 210.0, "Hợi": 240.0, "Tý": 270.0, "Sửu": 300.0, "Dần": 330.0,
}

CHI_HANH = {
    "Tý": "thuy", "Hợi": "thuy", "Dần": "moc", "Mão": "moc", "Tỵ": "hoa", "Ngọ": "hoa",
    "Thân": "kim", "Dậu": "kim", "Thìn": "tho", "Tuất": "tho", "Sửu": "tho", "Mùi": "tho",
}


def _star_ngu_hanh(name: str) -> str:
    """Ngũ hành của một chính tinh (data/tu_vi/chinh_tinh.json). Thuộc tính TÍNH ĐƯỢC
    — nền của sinh-khắc (functor đồng dạng giữa hành-sao và hành-cung)."""
    try:
        return get_chinh_tinh_by_name(name).ngu_hanh
    except Exception:
        return ""


def _star_do_sang(name: str, chi: str) -> str:
    """Độ sáng theo VỊ TRÍ (miếu-vượng-hãm rút gọn): 'đắc' nếu ở đắc-địa, 'hãm' nếu
    lạc-địa, 'bình' còn lại. Thuộc tính TÍNH ĐƯỢC (Đằng Sơn: kiểm nghiệm đắc/hãm địa) —
    cùng một sao mạnh hay yếu là HÀM của cung nó đậu."""
    try:
        s = get_chinh_tinh_by_name(name)
        if chi in s.dac_dia:
            return "đắc"
        if chi in s.lac_dia:
            return "hãm"
    except Exception:
        pass
    return "bình"


def build_natal(
    birth_local: datetime, lat: float, lon: float, target_year: int | None = None
) -> dict:
    """Gộp bầu trời thật + địa bàn ký hiệu cho một thời điểm sinh.

    - birth_local: datetime CÓ tzinfo (giờ địa phương nơi sinh).
    - lat/lon: toạ độ nơi sinh (độ) — để tính Ascendant + giờ thật.
    - target_year: nếu có → kèm tầng LƯU NIÊN (lá số "thở" theo năm): lưu Tứ Hóa +
      cung Thái Tuế năm đó. Mỗi năm Can khác → Tứ Hóa bắn vào sao khác = "mệnh là
      động từ" hiện hình. Tính được SÂN KHẤU năm đó, KHÔNG tính kết cục (Iron #4/#6/#8).
    """
    if birth_local.tzinfo is None:
        raise ValueError("birth_local phải có tzinfo (giờ địa phương nơi sinh)")

    utc = birth_local.astimezone(timezone.utc)
    chart = calculate_sky_chart(dt_utc=utc, lat=lat, lon=lon)
    lun = solar_to_lunar(SolarDateTime(
        birth_local.year, birth_local.month, birth_local.day,
        birth_local.hour, birth_local.minute,
    ))
    # An sao TẤT ĐỊNH — chuỗi hàm thuần của thời điểm sinh (engine canonical):
    # giờ → cung Mệnh → Cục → vị trí Tử Vi → 14 chính tinh (phép dịch cố định).
    hour_index = an_sao.hour_index_from_branch(lun.hour_chi)
    menh_idx = an_sao.cung_menh_index(lun.lunar_month, hour_index)
    menh = CHI[menh_idx]
    year_stem = lun.year_can_chi.split()[0]
    cuc = an_sao.cuc_so(year_stem, menh)
    tu_vi_idx = an_sao.tu_vi_position(cuc, lun.lunar_day)
    stars_by_cung: dict[int, list[str]] = {}
    for star_name, cung_idx in an_sao.place_14_chinh_tinh(tu_vi_idx).items():
        stars_by_cung.setdefault(cung_idx, []).append(star_name)
    # Tứ Hóa — hàm tất định của CAN năm (Đằng Sơn tr.165): sao nào hóa Lộc/Quyền/Khoa/Kỵ.
    tu_hoa = an_sao.tu_hoa_assignments(year_stem)
    hoa_of_star = {star: hoa for hoa, star in tu_hoa.items()}

    bodies = [{
        "name": b.name,
        "ecliptic_longitude": b.ecliptic_longitude,
        "ecliptic_latitude": b.ecliptic_latitude,
        "sign": b.sign,
        "sign_degree": b.sign_degree,
        "is_retrograde": b.is_retrograde,
    } for b in chart.bodies]
    sun = next((b for b in bodies if b["name"] == "sun"), None)

    cung = [{
        "chi": chi,
        "lon_center": CHI_LON_CENTER[chi],
        "hanh": CHI_HANH[chi],
        "is_menh": chi == menh,
        "chinh_tinh": [
            {
                "name": n,
                "ngu_hanh": _star_ngu_hanh(n),
                "hoa": hoa_of_star.get(n),
                "do_sang": _star_do_sang(n, chi),
            }
            for n in stars_by_cung.get(i, [])
        ],
    } for i, chi in enumerate(CHI)]

    # Tầng LƯU NIÊN — lá số "thở" theo năm (lưu Tứ Hóa + Thái Tuế). Hàm thuần của Can năm.
    luu_nien = None
    if target_year is not None:
        ly = solar_to_lunar(SolarDateTime(target_year, 6, 15, 12, 0))
        luu_nien = {
            "year": target_year,
            "can_chi": ly.year_can_chi,
            "thai_tue_chi": ly.year_chi,
            "tu_hoa": an_sao.tu_hoa_assignments(ly.year_can_chi.split()[0]),
        }

    return {
        "luu_nien": luu_nien,
        "birth": {
            "local": birth_local.isoformat(),
            "utc": utc.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "lat": lat, "lon": lon,
        },
        "sky": {
            "bodies": bodies,
            "sun_longitude": sun["ecliptic_longitude"] if sun else None,
            "ascendant": chart.ascendant.to_dict() if chart.ascendant else None,
            "ephemeris_source": chart.ephemeris_source,
        },
        "dia_ban": {
            "menh_chi": menh,
            "cuc": cuc,
            "tu_vi_chi": CHI[tu_vi_idx],
            "tu_hoa": tu_hoa,
            "lunar_month": lun.lunar_month,
            "lunar_day": lun.lunar_day,
            "hour_chi": lun.hour_chi,
            "year_can_chi": lun.year_can_chi,
            "cung": cung,
        },
    }
