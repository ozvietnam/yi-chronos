"""Marriage Compatibility — Hai người có hợp nhau trong hôn nhân không?

Phân tích 4 lớp:
  1. NẠP ÂM 60 GIÁP TÝ (Hành mệnh) — 2 mệnh sinh/khắc/hợp nhau?
  2. NĂM CHI — Xung/Hại/Hình/Lục Hợp/Tam Hợp
  3. NHẬT CHỦ — Bát Tự day master tương khắc/sinh
  4. NGŨ HÀNH TỔNG THỂ — Mộc-Mộc / Mộc-Hoả... 5 quan hệ Thể-Dụng

Mỗi lớp đóng góp score, tổng hợp → đánh giá.
"""
from __future__ import annotations

from dataclasses import dataclass, field


# Nạp âm 60 Giáp Tý — bảng ngắn (10 mệnh)
NAP_AM = {
    # (Can, Chi) → tên nạp âm + hành
    ("Giáp","Tý"): ("Hải Trung Kim", "Kim"),  ("Ất","Sửu"): ("Hải Trung Kim", "Kim"),
    ("Bính","Dần"): ("Lư Trung Hoả", "Hoả"),  ("Đinh","Mão"): ("Lư Trung Hoả", "Hoả"),
    ("Mậu","Thìn"): ("Đại Lâm Mộc", "Mộc"),    ("Kỷ","Tỵ"): ("Đại Lâm Mộc", "Mộc"),
    ("Canh","Ngọ"): ("Lộ Bàng Thổ", "Thổ"),   ("Tân","Mùi"): ("Lộ Bàng Thổ", "Thổ"),
    ("Nhâm","Thân"): ("Kiếm Phong Kim", "Kim"), ("Quý","Dậu"): ("Kiếm Phong Kim", "Kim"),
    ("Giáp","Tuất"): ("Sơn Đầu Hoả", "Hoả"),  ("Ất","Hợi"): ("Sơn Đầu Hoả", "Hoả"),
    ("Bính","Tý"): ("Giản Hạ Thuỷ", "Thuỷ"),  ("Đinh","Sửu"): ("Giản Hạ Thuỷ", "Thuỷ"),
    ("Mậu","Dần"): ("Thành Đầu Thổ", "Thổ"),   ("Kỷ","Mão"): ("Thành Đầu Thổ", "Thổ"),
    ("Canh","Thìn"): ("Bạch Lạp Kim", "Kim"),  ("Tân","Tỵ"): ("Bạch Lạp Kim", "Kim"),
    ("Nhâm","Ngọ"): ("Dương Liễu Mộc", "Mộc"), ("Quý","Mùi"): ("Dương Liễu Mộc", "Mộc"),
    ("Giáp","Thân"): ("Tuyền Trung Thuỷ", "Thuỷ"), ("Ất","Dậu"): ("Tuyền Trung Thuỷ", "Thuỷ"),
    ("Bính","Tuất"): ("Ốc Thượng Thổ", "Thổ"),  ("Đinh","Hợi"): ("Ốc Thượng Thổ", "Thổ"),
    ("Mậu","Tý"): ("Tích Lịch Hoả", "Hoả"),   ("Kỷ","Sửu"): ("Tích Lịch Hoả", "Hoả"),
    ("Canh","Dần"): ("Tùng Bách Mộc", "Mộc"),  ("Tân","Mão"): ("Tùng Bách Mộc", "Mộc"),
    ("Nhâm","Thìn"): ("Trường Lưu Thuỷ", "Thuỷ"), ("Quý","Tỵ"): ("Trường Lưu Thuỷ", "Thuỷ"),
    ("Giáp","Ngọ"): ("Sa Trung Kim", "Kim"),  ("Ất","Mùi"): ("Sa Trung Kim", "Kim"),
    ("Bính","Thân"): ("Sơn Hạ Hoả", "Hoả"),   ("Đinh","Dậu"): ("Sơn Hạ Hoả", "Hoả"),
    ("Mậu","Tuất"): ("Bình Địa Mộc", "Mộc"),  ("Kỷ","Hợi"): ("Bình Địa Mộc", "Mộc"),
    ("Canh","Tý"): ("Bích Thượng Thổ", "Thổ"), ("Tân","Sửu"): ("Bích Thượng Thổ", "Thổ"),
    ("Nhâm","Dần"): ("Kim Bạch Kim", "Kim"),  ("Quý","Mão"): ("Kim Bạch Kim", "Kim"),
    ("Giáp","Thìn"): ("Phú Đăng Hoả", "Hoả"), ("Ất","Tỵ"): ("Phú Đăng Hoả", "Hoả"),
    ("Bính","Ngọ"): ("Thiên Hà Thuỷ", "Thuỷ"), ("Đinh","Mùi"): ("Thiên Hà Thuỷ", "Thuỷ"),
    ("Mậu","Thân"): ("Đại Dịch Thổ", "Thổ"),   ("Kỷ","Dậu"): ("Đại Dịch Thổ", "Thổ"),
    ("Canh","Tuất"): ("Thoa Xuyến Kim", "Kim"), ("Tân","Hợi"): ("Thoa Xuyến Kim", "Kim"),
    ("Nhâm","Tý"): ("Tang Đố Mộc", "Mộc"),    ("Quý","Sửu"): ("Tang Đố Mộc", "Mộc"),
    ("Giáp","Dần"): ("Đại Khê Thuỷ", "Thuỷ"), ("Ất","Mão"): ("Đại Khê Thuỷ", "Thuỷ"),
    ("Bính","Thìn"): ("Sa Trung Thổ", "Thổ"),  ("Đinh","Tỵ"): ("Sa Trung Thổ", "Thổ"),
    ("Mậu","Ngọ"): ("Thiên Thượng Hoả", "Hoả"), ("Kỷ","Mùi"): ("Thiên Thượng Hoả", "Hoả"),
    ("Canh","Thân"): ("Thạch Lựu Mộc", "Mộc"), ("Tân","Dậu"): ("Thạch Lựu Mộc", "Mộc"),
    ("Nhâm","Tuất"): ("Đại Hải Thuỷ", "Thuỷ"), ("Quý","Hợi"): ("Đại Hải Thuỷ", "Thuỷ"),
}

SINH = {"Kim": "Thuỷ", "Thuỷ": "Mộc", "Mộc": "Hoả", "Hoả": "Thổ", "Thổ": "Kim"}
KHAC = {"Kim": "Mộc", "Mộc": "Thổ", "Thổ": "Thuỷ", "Thuỷ": "Hoả", "Hoả": "Kim"}

XUNG = {"Tý":"Ngọ","Ngọ":"Tý","Sửu":"Mùi","Mùi":"Sửu","Dần":"Thân","Thân":"Dần",
        "Mão":"Dậu","Dậu":"Mão","Thìn":"Tuất","Tuất":"Thìn","Tỵ":"Hợi","Hợi":"Tỵ"}
LUC_HOP = {"Tý":"Sửu","Sửu":"Tý","Dần":"Hợi","Hợi":"Dần","Mão":"Tuất","Tuất":"Mão",
           "Thìn":"Dậu","Dậu":"Thìn","Tỵ":"Thân","Thân":"Tỵ","Ngọ":"Mùi","Mùi":"Ngọ"}
TAM_HOP = {
    frozenset(["Thân","Tý","Thìn"]): "Thuỷ",
    frozenset(["Tỵ","Dậu","Sửu"]): "Kim",
    frozenset(["Dần","Ngọ","Tuất"]): "Hoả",
    frozenset(["Hợi","Mão","Mùi"]): "Mộc",
}
HAI = {"Tý":"Mùi","Mùi":"Tý","Sửu":"Ngọ","Ngọ":"Sửu","Dần":"Tỵ","Tỵ":"Dần",
       "Mão":"Thìn","Thìn":"Mão","Thân":"Hợi","Hợi":"Thân","Dậu":"Tuất","Tuất":"Dậu"}

STEM_HANH = {"Giáp":"Mộc","Ất":"Mộc","Bính":"Hoả","Đinh":"Hoả",
             "Mậu":"Thổ","Kỷ":"Thổ","Canh":"Kim","Tân":"Kim",
             "Nhâm":"Thuỷ","Quý":"Thuỷ"}

CON_GIAP = {"Tý":"Chuột","Sửu":"Trâu","Dần":"Hổ","Mão":"Mèo","Thìn":"Rồng","Tỵ":"Rắn",
            "Ngọ":"Ngựa","Mùi":"Dê","Thân":"Khỉ","Dậu":"Gà","Tuất":"Chó","Hợi":"Lợn"}


@dataclass
class PersonInfo:
    name: str
    year_stem: str
    year_branch: str
    nap_am_name: str
    nap_am_hanh: str
    day_stem: str
    day_branch: str


@dataclass
class CompatResult:
    person_a: PersonInfo
    person_b: PersonInfo
    nap_am_relation: dict
    chi_relation: dict
    nhat_chu_relation: dict
    total_score: int
    grade: str
    summary: str
    warnings: list[str] = field(default_factory=list)
    blessings: list[str] = field(default_factory=list)


def _ngu_hanh_relation(h1: str, h2: str) -> tuple[str, str]:
    """Return (relation_type, description)."""
    if h1 == h2:
        return "tỉ_hoà", f"Tỉ hoà ({h1}-{h1}) — bình thuận"
    if SINH.get(h2) == h1:
        return "sinh_thuận", f"{h2} sinh {h1} — đối phương nuôi"
    if SINH.get(h1) == h2:
        return "sinh_nghịch", f"{h1} sinh {h2} — anh cho đi sức"
    if KHAC.get(h1) == h2:
        return "khắc_xuôi", f"{h1} khắc {h2} — anh thắng"
    if KHAC.get(h2) == h1:
        return "khắc_nghịch", f"{h2} khắc {h1} — anh bị áp"
    return "unknown", ""


def _parse_person(birth_iso: str, name: str = "") -> PersonInfo:
    from core.chronos import calculate_chronos_state
    state = calculate_chronos_state(birth_iso, "Asia/Ho_Chi_Minh")
    ys, yb = state.ganzhi.year.split()
    ds, db = state.ganzhi.day.split()
    nap_am_name, nap_am_hanh = NAP_AM.get((ys, yb), ("Unknown", "?"))
    return PersonInfo(
        name=name or "Người",
        year_stem=ys, year_branch=yb,
        nap_am_name=nap_am_name, nap_am_hanh=nap_am_hanh,
        day_stem=ds, day_branch=db,
    )


def analyze_compatibility(
    birth_a_iso: str, birth_b_iso: str,
    name_a: str = "A", name_b: str = "B",
) -> CompatResult:
    """Phân tích hợp tuổi hôn nhân."""
    pa = _parse_person(birth_a_iso, name_a)
    pb = _parse_person(birth_b_iso, name_b)

    total = 0
    warnings = []
    blessings = []

    # ─── LỚP 1: NẠP ÂM ───────────────────────────────────
    na_rel_type, na_desc = _ngu_hanh_relation(pa.nap_am_hanh, pb.nap_am_hanh)
    na_score = {"tỉ_hoà": 5, "sinh_thuận": 8, "sinh_nghịch": 4,
                "khắc_xuôi": -3, "khắc_nghịch": -3, "unknown": 0}[na_rel_type]
    total += na_score
    nap_am_relation = {
        "person_a_napam": f"{pa.nap_am_name} ({pa.nap_am_hanh})",
        "person_b_napam": f"{pb.nap_am_name} ({pb.nap_am_hanh})",
        "relation_type": na_rel_type,
        "description": na_desc,
        "score": na_score,
    }
    if na_rel_type in ("sinh_thuận",):
        blessings.append(f"⭐ Nạp âm: {pb.nap_am_hanh} sinh {pa.nap_am_hanh} — hai mệnh nuôi nhau")
    elif na_rel_type in ("khắc_xuôi", "khắc_nghịch"):
        warnings.append(f"⚠️ Nạp âm khắc ({pa.nap_am_hanh}-{pb.nap_am_hanh}) — cần hoá giải")

    # ─── LỚP 2: NĂM CHI ─────────────────────────────────
    chi_a, chi_b = pa.year_branch, pb.year_branch
    chi_score = 0
    chi_notes = []

    if XUNG.get(chi_a) == chi_b:
        chi_score -= 15
        chi_notes.append(f"⛔ LỤC XUNG ({chi_a}-{chi_b}) — kỵ rất mạnh")
        warnings.append(f"⛔ Tuổi {CON_GIAP[chi_a]}-{CON_GIAP[chi_b]} XUNG — kết hôn cần đề phòng xung đột lớn")
    elif LUC_HOP.get(chi_a) == chi_b:
        chi_score += 12
        chi_notes.append(f"⭐ LỤC HỢP ({chi_a}-{chi_b}) — cực hợp")
        blessings.append(f"⭐ Lục Hợp {CON_GIAP[chi_a]}-{CON_GIAP[chi_b]} — bậc nhất trong hôn nhân")
    elif any(chi_a in c and chi_b in c for c in TAM_HOP if chi_a != chi_b):
        for combo, hanh in TAM_HOP.items():
            if chi_a in combo and chi_b in combo:
                chi_score += 9
                chi_notes.append(f"⭐ TAM HỢP {hanh} ({chi_a}-{chi_b})")
                blessings.append(f"⭐ Tam Hợp {hanh} — hai tuổi cùng nhóm khí")
                break
    elif HAI.get(chi_a) == chi_b:
        chi_score -= 8
        chi_notes.append(f"⚠️ TƯƠNG HẠI ({chi_a}-{chi_b})")
        warnings.append(f"⚠️ Tương Hại {CON_GIAP[chi_a]}-{CON_GIAP[chi_b]} — có khoảng cách ngầm")
    elif chi_a == chi_b:
        chi_score += 2
        chi_notes.append(f"Cùng tuổi {CON_GIAP[chi_a]} — bình")
    else:
        chi_score += 1
        chi_notes.append(f"Năm chi {chi_a}-{chi_b} không xung không hợp")

    total += chi_score
    chi_relation = {
        "year_a": chi_a, "year_b": chi_b,
        "con_giap_a": CON_GIAP.get(chi_a, "?"),
        "con_giap_b": CON_GIAP.get(chi_b, "?"),
        "score": chi_score,
        "notes": chi_notes,
    }

    # ─── LỚP 3: NHẬT CHỦ ────────────────────────────────
    ha = STEM_HANH[pa.day_stem]
    hb = STEM_HANH[pb.day_stem]
    nc_rel_type, nc_desc = _ngu_hanh_relation(ha, hb)
    nc_score = {"tỉ_hoà": 3, "sinh_thuận": 6, "sinh_nghịch": 3,
                "khắc_xuôi": -2, "khắc_nghịch": -2, "unknown": 0}[nc_rel_type]
    total += nc_score
    nhat_chu_relation = {
        "person_a_day": f"{pa.day_stem} ({ha})",
        "person_b_day": f"{pb.day_stem} ({hb})",
        "relation_type": nc_rel_type,
        "description": nc_desc,
        "score": nc_score,
    }
    if nc_rel_type == "sinh_thuận":
        blessings.append(f"Nhật chủ: {pb.day_stem} sinh {pa.day_stem} — đối phương nuôi tâm anh")

    # ─── GRADE — đọc cấu hình KHÍ, KHÔNG phán "nên/không nên cưới" (Iron Rule #4/#6) ──
    # NOTE: đây là engine "xem tuổi" dân gian (nông). UI chính dùng engine sâu
    # bat_tu/compatibility (dụng thần + spouse-check). Giữ endpoint này nhưng diễn
    # ngôn đồng-dạng, không verdict cứng doạ đôi trẻ.
    if total >= 18:
        grade = "Khí tương hợp mạnh — nhiều dòng nâng đỡ nhau"
    elif total >= 12:
        grade = "Khí tương hợp rõ — nền tảng thuận"
    elif total >= 6:
        grade = "Có dòng tương hợp — ít chỗ nghịch khí"
    elif total >= 0:
        grade = "Khí cân bằng — cần hai bên cùng vun bồi"
    elif total >= -10:
        grade = "Khí có nhiều chỗ nghịch — mời quan-sát để hiểu & dung hòa"
    else:
        grade = "Khí xung nhiều — quan-sát kỹ điểm nghịch mà dung hòa (KHÔNG phải điềm cấm cưới)"

    summary = (
        f"Tổng điểm {total:+}. "
        f"Nạp âm: {na_desc}. "
        f"Năm chi: {' / '.join(chi_notes[:1]) if chi_notes else 'không xung'}. "
        f"Nhật chủ: {nc_desc}."
    )

    return CompatResult(
        person_a=pa, person_b=pb,
        nap_am_relation=nap_am_relation,
        chi_relation=chi_relation,
        nhat_chu_relation=nhat_chu_relation,
        total_score=total, grade=grade, summary=summary,
        warnings=warnings, blessings=blessings,
    )


if __name__ == "__main__":
    # Test: bạn anh 1988 Mậu Thìn + giả lập 1990 Canh Ngọ
    r = analyze_compatibility(
        "1988-05-02T08:00:00", "1990-06-15T14:00:00",
        "Anh", "Vợ"
    )
    print(f"=== HỢP TUỔI ===")
    print(f"A: {r.person_a.name} — {r.person_a.year_stem} {r.person_a.year_branch} "
          f"({r.person_a.nap_am_name})")
    print(f"B: {r.person_b.name} — {r.person_b.year_stem} {r.person_b.year_branch} "
          f"({r.person_b.nap_am_name})")
    print()
    print(f"Total: {r.total_score:+}")
    print(f"Grade: {r.grade}")
    print(f"Summary: {r.summary}")
    print()
    print("Blessings:")
    for b in r.blessings: print(f"  {b}")
    print("Warnings:")
    for w in r.warnings: print(f"  {w}")
