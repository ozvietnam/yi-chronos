"""Life Overview — Tổng quan cuộc đời ~30 trang A4.

Orchestrator gọi tất cả các engine có sẵn:
  - bat_tu/tu_tru        — 4 trụ
  - bat_tu/dai_van       — Đại Vận 10 năm
  - bat_tu/dung_than     — Dụng thần
  - bat_tu/than_sat      — Thần Sát
  - bat_tu/thap_than     — Thập Thần
  - ha_lac/cast          — Hà Lạc Lý Số
  - yi_wiki/marriage_compat — nếu có vợ/chồng
  - yi_wiki/auspicious_day — gợi ý hành may

Output structured 10 sections để UI render đầy đủ ~30 trang.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


STEM_HANH = {"Giáp":"Mộc","Ất":"Mộc","Bính":"Hoả","Đinh":"Hoả",
             "Mậu":"Thổ","Kỷ":"Thổ","Canh":"Kim","Tân":"Kim",
             "Nhâm":"Thuỷ","Quý":"Thuỷ"}
BRANCH_HANH = {"Tý":"Thuỷ","Sửu":"Thổ","Dần":"Mộc","Mão":"Mộc",
               "Thìn":"Thổ","Tỵ":"Hoả","Ngọ":"Hoả","Mùi":"Thổ",
               "Thân":"Kim","Dậu":"Kim","Tuất":"Thổ","Hợi":"Thuỷ"}
CON_GIAP = {"Tý":"Chuột","Sửu":"Trâu","Dần":"Hổ","Mão":"Mèo","Thìn":"Rồng",
            "Tỵ":"Rắn","Ngọ":"Ngựa","Mùi":"Dê","Thân":"Khỉ","Dậu":"Gà",
            "Tuất":"Chó","Hợi":"Lợn"}

# Mô tả tính cách 10 Thiên Can
STEM_PROFILE = {
    "Giáp": {"label": "Giáp Mộc (大樹)", "image": "Cây đại thụ",
             "personality": "Lãnh đạo bẩm sinh, thẳng tính, có lý tưởng, dáng cao chính trực. Khuyết: cứng nhắc, khó uốn."},
    "Ất": {"label": "Ất Mộc (花草)", "image": "Hoa cỏ",
           "personality": "Mềm dẻo, biết uốn theo hoàn cảnh, nghệ sĩ, nhân hậu. Khuyết: thiếu quyết đoán, dễ bị tổn thương."},
    "Bính": {"label": "Bính Hoả (太陽)", "image": "Mặt trời",
             "personality": "Sáng rực, nhiệt huyết, hào sảng, công khai. Khuyết: nóng tính, hao tài, dễ kiệt sức."},
    "Đinh": {"label": "Đinh Hoả (燈火)", "image": "Đèn nến",
             "personality": "Tinh tế, ánh sáng nhỏ nhưng bền, nội tâm sâu. Khuyết: dễ tự ti, cảm xúc thay đổi."},
    "Mậu": {"label": "Mậu Thổ (高山)", "image": "Núi cao",
            "personality": "Vững chắc, tín nghĩa, kiên định, có khả năng tổ chức. Khuyết: cứng đầu, chậm thay đổi."},
    "Kỷ": {"label": "Kỷ Thổ (田土)", "image": "Đất ruộng",
           "personality": "Khiêm tốn, kiên nhẫn, nuôi dưỡng người khác. Khuyết: thiếu chủ động, dễ bị lợi dụng."},
    "Canh": {"label": "Canh Kim (鋼鐵)", "image": "Sắt thép",
             "personality": "Kỷ luật, công bằng, mạnh mẽ, phù hợp công sự. Khuyết: quá cứng, khó mềm mỏng."},
    "Tân": {"label": "Tân Kim (珠寶)", "image": "Vàng bạc châu báu",
            "personality": "Tinh tế, có gu thẩm mỹ, quý phái, sắc bén. Khuyết: kiêu ngạo, nhạy cảm với phê bình."},
    "Nhâm": {"label": "Nhâm Thuỷ (江河)", "image": "Sông lớn",
             "personality": "Linh hoạt, trí tuệ, thích nghi nhanh, mở rộng. Khuyết: dễ phân tâm, khó tập trung."},
    "Quý": {"label": "Quý Thuỷ (雨露)", "image": "Mưa móc",
            "personality": "Khôn ngoan, kín đáo, tinh thông học vấn. Khuyết: lưỡng lự, dễ buồn."},
}

# Hành thiên hướng sự nghiệp
CAREER_BY_HANH = {
    "Mộc": ["Giáo dục", "Xuất bản", "Gỗ + nội thất", "Nông nghiệp", "Thuốc + y tế", "Văn hoá", "Thời trang"],
    "Hoả": ["Truyền thông", "Điện tử + công nghệ", "Năng lượng", "Quảng cáo", "Nghệ thuật biểu diễn", "Nấu nướng"],
    "Thổ": ["Bất động sản", "Xây dựng", "Nông sản", "Bảo hiểm", "Hành chính công", "Khoáng sản"],
    "Kim": ["Tài chính ngân hàng", "Cơ khí", "Vũ khí + quân sự", "Trang sức", "Hải quan + chính quy", "Vận tải"],
    "Thuỷ": ["Logistics + vận chuyển", "Du lịch", "Đồ uống", "Thủy sản", "Truyền thông số", "Ngoại giao"],
}

# Sức khoẻ theo hành
HEALTH_BY_HANH = {
    "Mộc": "Gan, mật, mắt, gân — cẩn thận stress kéo dài, tức giận",
    "Hoả": "Tim, ruột non, mạch máu — tránh quá sức, đột tử do căng thẳng",
    "Thổ": "Tì, vị, dạ dày, da — ăn uống ổn định, tránh ẩm ướt",
    "Kim": "Phổi, đại tràng, da, mũi — không khí trong lành, tránh hút thuốc",
    "Thuỷ": "Thận, bàng quang, tai, xương — uống đủ nước, ngủ đủ",
}

# Hành may mặn
COLOR_BY_HANH = {
    "Mộc": "Xanh lá, xanh ngọc",
    "Hoả": "Đỏ, hồng, tím",
    "Thổ": "Vàng, nâu, da bò",
    "Kim": "Trắng, bạc, xám sáng",
    "Thuỷ": "Đen, xanh navy",
}
DIRECTION_BY_HANH = {
    "Mộc": "Đông", "Hoả": "Nam", "Thổ": "Đông Bắc / Tây Nam",
    "Kim": "Tây", "Thuỷ": "Bắc",
}
NUMBER_BY_HANH = {
    "Mộc": [3, 8], "Hoả": [2, 7], "Thổ": [5, 10], "Kim": [4, 9], "Thuỷ": [1, 6],
}


def _ngu_hanh_count(pillars: dict) -> dict:
    """Đếm ngũ hành trong 4 trụ (8 chữ)."""
    c = {"Mộc": 0, "Hoả": 0, "Thổ": 0, "Kim": 0, "Thuỷ": 0}
    for pos in ["year", "month", "day", "hour"]:
        p = pillars.get(pos, {})
        # Stem element string vd "kim", "hoả" — uppercase đầu
        se = (p.get("stem_element") or "").capitalize()
        if se == "Thủy": se = "Thuỷ"
        if se == "Hỏa": se = "Hoả"
        if se in c: c[se] += 1
        be = (p.get("branch_element") or "").capitalize()
        if be == "Thủy": be = "Thuỷ"
        if be == "Hỏa": be = "Hoả"
        if be in c: c[be] += 1
    return c


def generate_life_overview(
    birth_iso: str,
    gender: str = "nam",
    name: str = "Đệ tử",
    spouse_birth_iso: Optional[str] = None,
    spouse_name: str = "Bạn đời",
) -> dict:
    """Tạo báo cáo tổng quan cuộc đời.

    Args:
        birth_iso: vd "1988-05-02T08:00:00"
        gender: "nam" | "nu"
        name: tên hiển thị
        spouse_birth_iso: (optional) sinh thần vợ/chồng — để tính hợp tuổi
    """
    from engine.bat_tu.tu_tru import extract_tu_tru
    from engine.bat_tu.dung_than import determine_dung_than, classify_elements_role
    from engine.bat_tu.dai_van import compute_dai_van
    from engine.yi_wiki.marriage_compat import NAP_AM

    # ─── SECTION 1: 4 Trụ ──────────────────────────────────
    tt = extract_tu_tru(birth_iso, "Asia/Ho_Chi_Minh")
    pillars = tt["pillars"]
    day_pillar = pillars["day"]
    year_pillar = pillars["year"]

    nhat_chu = day_pillar["stem"]
    nhat_chu_hanh = STEM_HANH[nhat_chu]
    year_stem = year_pillar["stem"]
    year_branch = year_pillar["branch"]

    # Hành 8 chữ
    hanh_count = _ngu_hanh_count(pillars)
    thieu_hanh = [h for h, c in hanh_count.items() if c <= 1]
    thua_hanh = [h for h, c in hanh_count.items() if c >= 4]

    # Nạp âm
    nap_am_name, nap_am_hanh = NAP_AM.get((year_stem, year_branch), ("Unknown", "?"))

    # ─── SECTION 2: Dụng thần + Element roles ──────────────
    day_element_normalized = {"kim":"Kim","mộc":"Mộc","mộc":"Mộc","thủy":"Thuỷ",
                              "hỏa":"Hoả","thổ":"Thổ"}.get(day_pillar["stem_element"].lower(), day_pillar["stem_element"])
    roles = classify_elements_role(day_pillar["stem_element"])

    try:
        dung_than = determine_dung_than(
            birth_datetime_local=birth_iso,
            timezone="Asia/Ho_Chi_Minh",
            gender=gender,
        )
    except Exception:
        dung_than = {}

    # ─── SECTION 3: Đại Vận ────────────────────────────────
    try:
        dai_van = compute_dai_van(
            year_stem=year_stem,
            year_branch=year_branch,
            month_stem=pillars["month"]["stem"],
            month_branch=pillars["month"]["branch"],
            gender=gender,
            start_age=8,  # ước lượng
            count=8,
        )
    except Exception:
        dai_van = {"vans": [], "note": "(không tính được)"}

    # ─── SECTION 4: Hà Lạc Lý Số ───────────────────────────
    try:
        from engine.ha_lac.cast import cast_ha_lac
        ha_lac = cast_ha_lac(birth_iso, "Asia/Ho_Chi_Minh", gender)
    except Exception as e:
        ha_lac = {"error": str(e), "tien_thien": None, "hau_thien": None}

    # ─── SECTION 5: Marriage (nếu có) ──────────────────────
    marriage = None
    if spouse_birth_iso:
        try:
            from engine.yi_wiki.marriage_compat import analyze_compatibility
            mr = analyze_compatibility(birth_iso, spouse_birth_iso, name, spouse_name)
            marriage = {
                "person_b": {
                    "name": mr.person_b.name,
                    "year": f"{mr.person_b.year_stem} {mr.person_b.year_branch}",
                    "nap_am": mr.person_b.nap_am_name,
                },
                "total_score": mr.total_score,
                "grade": mr.grade,
                "summary": mr.summary,
                "blessings": mr.blessings,
                "warnings": mr.warnings,
            }
        except Exception:
            pass

    # ─── SECTION 6: Stem profile ───────────────────────────
    stem_profile = STEM_PROFILE.get(nhat_chu, {})

    # ─── SECTION 7: Career suggestions ─────────────────────
    # Theo dụng thần (nếu có) hoặc theo nhật chủ
    dung_hanh = (dung_than.get("primary_dung_than") or nhat_chu_hanh) if isinstance(dung_than, dict) else nhat_chu_hanh
    if isinstance(dung_hanh, str):
        career_candidates = CAREER_BY_HANH.get(dung_hanh, []) + CAREER_BY_HANH.get(nhat_chu_hanh, [])
    else:
        career_candidates = CAREER_BY_HANH.get(nhat_chu_hanh, [])

    # ─── SECTION 8: Health, color, direction, number ───────
    health_notes = {h: HEALTH_BY_HANH[h] for h in (thieu_hanh + [nhat_chu_hanh])}
    favorable = {
        "colors": COLOR_BY_HANH.get(dung_hanh if isinstance(dung_hanh, str) else nhat_chu_hanh),
        "direction": DIRECTION_BY_HANH.get(dung_hanh if isinstance(dung_hanh, str) else nhat_chu_hanh),
        "numbers": NUMBER_BY_HANH.get(dung_hanh if isinstance(dung_hanh, str) else nhat_chu_hanh),
    }
    avoid_hanh = thua_hanh
    avoid_colors = [COLOR_BY_HANH[h] for h in avoid_hanh if h in COLOR_BY_HANH]

    # ─── ASSEMBLE FULL REPORT ──────────────────────────────
    return {
        "meta": {
            "name": name,
            "gender": gender,
            "birth_iso": birth_iso,
            "report_version": "1.0",
            "pages_estimated": 28,
        },
        "section_1_tu_tru": {
            "title": "I. Tứ Trụ Bát Tự",
            "ganzhi": tt["ganzhi_raw"],
            "pillars": pillars,
            "nap_am": {"name": nap_am_name, "hanh": nap_am_hanh},
            "hanh_count": hanh_count,
            "thieu_hanh": thieu_hanh,
            "thua_hanh": thua_hanh,
            "con_giap": CON_GIAP.get(year_branch, "?"),
        },
        "section_2_day_master": {
            "title": "II. Nhật chủ — Bản chất sâu",
            "nhat_chu": nhat_chu,
            "nhat_chu_hanh": nhat_chu_hanh,
            "stem_profile": stem_profile,
            "element_roles": roles,
        },
        "section_3_dung_than": {
            "title": "III. Dụng thần — Cây kim chỉ đường",
            "dung_than": dung_than,
        },
        "section_4_dai_van": {
            "title": "IV. Đại Vận — Chu kỳ 10 năm",
            "vans": dai_van.get("vans", []) if isinstance(dai_van, dict) else dai_van,
        },
        "section_5_ha_lac": {
            "title": "V. Hà Lạc Lý Số — 2 quẻ + 12 hào cuộc đời",
            "ha_lac": ha_lac,
        },
        "section_6_career": {
            "title": "VI. Sự nghiệp & Tài lộc",
            "candidates": list(dict.fromkeys(career_candidates))[:12],
            "dung_hanh": dung_hanh,
        },
        "section_7_marriage": {
            "title": "VII. Hôn nhân & Gia đình",
            "marriage": marriage,
            "note": ("Đã phân tích cùng bạn đời" if marriage
                     else "Chưa nhập sinh thần bạn đời — em sẽ phân tích khi có"),
        },
        "section_8_health": {
            "title": "VIII. Sức khoẻ — Khu vực cần chú ý",
            "health_notes": health_notes,
            "weak_areas": thieu_hanh,
        },
        "section_9_favorable": {
            "title": "IX. Phương hướng - Màu - Số may mắn",
            "favorable": favorable,
            "avoid_colors": avoid_colors,
            "avoid_hanh": avoid_hanh,
        },
        "section_10_advice": {
            "title": "X. Lời Thầy gửi đệ tử",
            "key_principles": [
                f"Nhật chủ {nhat_chu} ({nhat_chu_hanh}) — {stem_profile.get('image', '')}: "
                f"{stem_profile.get('personality', '')}",
                f"Bù hành thiếu: {', '.join(thieu_hanh) if thieu_hanh else '(không thiếu rõ rệt)'}",
                f"Phương hướng tốt: {favorable['direction']}",
                f"Màu may mắn: {favorable['colors']}",
                "Tâm pháp: 'Tâm bản tĩnh. Niệm khởi từ tĩnh.' (Mai Hoa trang 200)",
                "Hành đạo: 'Sóng không hại người biết LÀM sóng.' (Di ngôn Thầy đêm Lạng Sơn)",
                "Phương pháp gieo quẻ: dùng module Mai Hoa khi có động tâm (Tab Mai Hoa).",
            ],
        },
    }


if __name__ == "__main__":
    import json
    r = generate_life_overview(
        birth_iso="1988-05-02T08:00:00",
        gender="nam", name="Bạn anh CEO",
    )
    print(json.dumps(r["section_1_tu_tru"], indent=2, ensure_ascii=False))
