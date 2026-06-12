"""Domain 5: Tật ách / bệnh sử — derive từ sao an theo giờ trên lá số Tử Vi.

Phương pháp (video 091 kênh Tử Vi Bôn Ba, Anh duyệt 2026-06-12): khi giờ sinh
giáp ranh, lập lá số Tử Vi cho TỪNG giờ ứng viên rồi đối chiếu bệnh sử thực tế.
Cơ sở phân biệt: nhóm sao an theo GIỜ (Hỏa Tinh, Linh Tinh, Địa Không, Địa Kiếp)
và chính vị trí cung Mệnh/Thân/Tật Ách đều xoay theo giờ sinh — nên bệnh sử
(nóng trong, căng thẳng thần kinh, sẹo/bệnh vặt) là tín hiệu khách quan, dễ nhớ,
phân biệt mạnh giữa hai lá giáp ranh.

Lưu ý paradigm: trait chỉ dùng để ĐỐI CHIẾU lá số (xác định giờ sinh), KHÔNG
phải chẩn đoán y khoa, không phán bệnh.
"""
from __future__ import annotations


def _safe_cast_la_so(candidate: dict) -> dict | None:
    """Cast lá số Tử Vi cho 1 giờ ứng viên. None nếu thiếu dữ liệu."""
    lunar = candidate.get("lunar") or {}
    pillars = candidate.get("pillars") or {}
    year = pillars.get("year") or {}
    if not (lunar.get("month") and lunar.get("day") and year.get("stem")
            and year.get("branch") and candidate.get("chi")):
        return None
    from engine.tu_vi.an_sao import cast_la_so
    try:
        la_so = cast_la_so(
            lunar_month=int(lunar["month"]),
            lunar_day=int(lunar["day"]),
            hour_branch=candidate["chi"],
            year_stem=year["stem"],
            year_branch=year["branch"],
            gender=candidate.get("gender") or "nam",
        )
    except (ValueError, KeyError):
        return None
    return la_so  # cast_la_so trả dict (LaSoTuVi.to_dict() + sao_q2)


def _palace_index(la_so: dict, name: str) -> int | None:
    for p in la_so.get("palaces") or []:
        if p.get("name") == name:
            return p.get("branch_index")
    return None


def derive_tat_ach_traits(candidate: dict) -> dict[str, str]:
    """3 traits tật ách/bệnh sử cho 1 giờ ứng viên.

    Returns (value "unknown" nếu không cast được lá số):
      - health_hoa_linh:      'nong_trong'      | 'binh_thuong'
      - health_khong_kiep:    'cang_than_kinh'  | 'binh_thuong'
      - health_sat_tinh_than: 'nhieu_dau_vet'   | 'it_dau_vet'
    """
    unknown = {
        "health_hoa_linh": "unknown",
        "health_khong_kiep": "unknown",
        "health_sat_tinh_than": "unknown",
    }
    la_so = _safe_cast_la_so(candidate)
    if not la_so:
        return unknown

    sat = la_so.get("sat_tinh") or {}
    menh = la_so.get("menh_index")
    than = la_so.get("than_index")
    tat_ach = _palace_index(la_so, "Tật Ách")
    if menh is None or tat_ach is None:
        return unknown

    hoa, linh = sat.get("Hỏa Tinh"), sat.get("Linh Tinh")
    khong, kiep = sat.get("Địa Không"), sat.get("Địa Kiếp")
    core = {menh, tat_ach}
    body = {menh, than, tat_ach}

    hoa_linh_hit = any(x in core for x in (hoa, linh) if x is not None)
    khong_kiep_hit = any(x in core for x in (khong, kiep) if x is not None)
    n_body = sum(1 for x in (hoa, linh, khong, kiep) if x is not None and x in body)

    return {
        "health_hoa_linh": "nong_trong" if hoa_linh_hit else "binh_thuong",
        "health_khong_kiep": "cang_than_kinh" if khong_kiep_hit else "binh_thuong",
        "health_sat_tinh_than": "nhieu_dau_vet" if n_body >= 2 else "it_dau_vet",
    }
