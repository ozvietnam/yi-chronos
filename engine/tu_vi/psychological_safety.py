"""Tử Vi — Psychological safety rules.

Q3 p0186, Q1 p0027-p0028 chỉ rõ một số combo có **dark warning** (tự vẫn,
chết đuối, tự thắt cổ). Engine phát hiện pattern → KHÔNG hù dọa, mà:
1. Lưu ý nhẹ nhàng về health tinh thần
2. Gợi ý self-care + bạn bè + chuyên gia
3. KHÔNG predict, dùng "mỗ" pattern (gợi mở)

3 patterns chính rút từ thâm nhuần:

Pattern 1 — Văn Xương Văn Khúc + năm sinh + Đại Hạn Thìn/Tuất (Q3 p0186)
  "Xương Khúc kỷ tân nhâm sinh nhân, hạn phùng Thìn Tuất lự đầu hà."

Pattern 2 — Cự Môn tại Tý + hung tinh (Q1 p0027)
  "Cự Môn cung Tý, tất chủ đầu hà nị thủy."

Pattern 3 — Phá Quân + Nhật Nguyệt + hạn (Q1 p0028)
  "Phá Quân dữ nhật nguyệt dĩ tế hành... hạn phùng chí thử, tai bất khả nhương"

Iron Rule #6 — chỉ là **dấu hiệu kích hoạt nhận thức**, KHÔNG fortune-telling.
"""
from __future__ import annotations

BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


SAFETY_PATTERNS = [
    {
        "id": "dinh_tu_sinh_q4",
        "title": "Định tử sinh quyết (Q4 Chiếu Đởm Kinh) — Thiên Khốc + Thiên Hư đồng vị Thân/Mệnh",
        "source": "Q4 p0274 r009",
        "source_quote_hv": "Nhược Thiên Khốc chính lâm thân mệnh, cánh dữ Thiên Hư đồng vị, hỉ tinh hựu thả vô lực, kỳ nhân sinh hạ bất xuất tam ngũ nhật nhi tử.",
        "source_quote_zh": "若天哭正临身命，更与天虚同位，喜星又且无力，其人生下不出三五日而死。",
        "paradigm_alert": "⚠️ ĐÂY LÀ QUY TẮC PREDICT TỬ VONG TRONG CỔ KINH — ENGINE KHÔNG SURFACE RAW",
        "trigger": {
            "stars_required": ["Thiên Khốc", "Thiên Hư"],
            "stars_anywhere": False,
            "same_palace": True,
            "palace_any": ["Mệnh", "Thân"],
        },
        "raw_concern": "Cổ kinh ghi nhận pattern này — KHÔNG dùng để predict, mà để gợi mở chăm sóc thân thể đặc biệt",
        "gentle_message": "Lá số có cấu trúc Thiên Khốc + Thiên Hư đặc thù theo cổ kinh Q4. Đây KHÔNG phải predict — chỉ là 'dấu hiệu nhận thức' để chăm sóc thân thể + tâm trạng. Bạn vẫn đang sống và khỏe — đó là minh chứng paradigm cứng nhắc cổ KHÔNG đúng. Iron Rule #6: 'mỗ' pattern — không phán cứng.",
        "self_care_tips": [
            "Lưu ý sức khỏe định kỳ — khám tổng quát hàng năm",
            "Quản lý stress + tâm trạng — đặc biệt giai đoạn Đại Vận khó",
            "Duy trì kết nối xã hội — không cô lập",
            "Nếu có ý nghĩ tự hại — Đường Dây Cứu Sống 1800-1567",
        ],
        "ceo_directive_2026_05_20": "CEO duyệt tích hợp để test — nếu user có pattern này KHÔNG vào tình trạng nguy, thì paradigm cổ SAI, có thể loại pattern khỏi engine.",
    },
    {
        "id": "xuong_khuc_thin_tuat",
        "title": "Văn Xương Văn Khúc + năm Kỷ/Tân/Nhâm + Đại Hạn Thìn/Tuất",
        "source": "Q3 p0186",
        "key_phrase_hv": "Xương Khúc kỷ tân nhâm sinh nhân, hạn phùng Thìn Tuất lự đầu hà",
        "key_phrase_zh": "昌曲己辛壬生人 限逢辰戌 虑投河",
        "trigger": {
            "stars_required": ["Văn Xương", "Văn Khúc"],
            "stars_anywhere": True,
            "year_stems_any": ["Kỷ", "Tân", "Nhâm"],
            "dai_van_branch_any": ["Thìn", "Tuất"],
        },
        "raw_concern": "lự đầu hà (sợ nhảy sông tự vẫn)",
        "gentle_message": "Trong Đại Vận Thìn hoặc Tuất, lá số có khả năng nhạy cảm với áp lực tinh thần. Cổ nhân lưu ý nên giữ kết nối bạn bè + người thân + chuyên gia tâm lý nếu cần.",
        "self_care_tips": [
            "Duy trì kết nối xã hội — không cô độc dài hạn",
            "Quan tâm chất lượng giấc ngủ",
            "Nếu có ý nghĩ tự hại — liên hệ Tâm Lý Xanh, Đường Dây Cứu Sống 1800-1567",
            "Nói chuyện với 1 người tin cậy trước khi quyết định lớn",
        ],
    },
    {
        "id": "cu_mon_ty_hung",
        "title": "Cự Môn tại Tý + sát tinh hung",
        "source": "Q1 p0027",
        "key_phrase_hv": "Cự Môn cung Tý, tất chủ đầu hà nị thủy",
        "key_phrase_zh": "巨门子宫 必主投河溺水",
        "trigger": {
            "star_at_palace": {"star": "Cự Môn", "branch": "Tý"},
            "additional_required_any": ["Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Hóa Kỵ"],
        },
        "raw_concern": "đầu hà nị thủy (nhảy sông chết đuối)",
        "gentle_message": "Cự Môn tại Tý kết hợp với sát tinh — cổ nhân coi là cấu trúc nhạy cảm. Trong các Đại Vận đi qua cung này, lưu ý chăm sóc nội tâm.",
        "self_care_tips": [
            "Cẩn thận với hoạt động dưới nước trong DV qua Tý",
            "Tránh quyết định lớn khi tâm trạng đang căng",
            "Chia sẻ áp lực với người tin cậy",
        ],
    },
    {
        "id": "pha_quan_nhat_nguyet",
        "title": "Phá Quân + Nhật Nguyệt + Đại Hạn về cung này",
        "source": "Q1 p0028",
        "key_phrase_hv": "Phá Quân dữ nhật nguyệt dĩ tế hành, hạn phùng chí thử, tai bất khả nhương",
        "key_phrase_zh": "破军与日月以济行 限逢至此 灾不可禳",
        "trigger": {
            "stars_required": ["Phá Quân", "Thái Dương", "Thái Âm"],
            "stars_anywhere": True,
            "additional_condition": "Đại Hạn về cung có Phá Quân + Nhật + Nguyệt",
        },
        "raw_concern": "tai bất khả nhương (tai họa khó tránh khi hạn tới — thị lực + tinh thần)",
        "gentle_message": "Phá Quân + Nhật + Nguyệt gặp nhau trong Đại Vận — cổ nhân nói cần thận trọng đặc biệt về thị giác + áp lực tinh thần.",
        "self_care_tips": [
            "Khám mắt định kỳ trong DV đi qua cung này",
            "Đề phòng burnout — giữ work-life balance",
            "Tránh lái xe đêm khuya quá nhiều",
        ],
    },
]


def detect_safety_patterns(la_so: dict, year_stem: str = "") -> list[dict]:
    """Detect dark warning patterns trong lá số.

    Args:
        la_so: chart dict từ engine.tu_vi.an_sao
        year_stem: thiên can năm sinh (vd "Mậu" cho 1988)

    Returns:
        List of triggered patterns (có thể empty). Mỗi pattern có:
        - id, title, source, raw_concern, gentle_message, self_care_tips
        - which_dai_van: list các Đại Vận có thể kích hoạt
    """
    triggered: list[dict] = []
    chinh = la_so.get("chinh_tinh", {})
    phu = la_so.get("phu_tinh", {})
    sat = la_so.get("sat_tinh", {})
    tu_hoa = la_so.get("tu_hoa", {})
    all_stars = {**chinh, **phu, **sat}
    dai_van = la_so.get("dai_van", [])

    for pattern in SAFETY_PATTERNS:
        trigger = pattern["trigger"]
        matched = True
        which_dai_van: list[str] = []

        # Stars required (anywhere on chart)
        if "stars_required" in trigger:
            for s in trigger["stars_required"]:
                if s not in all_stars:
                    matched = False
                    break
            if not matched:
                continue

        # Year stem
        if "year_stems_any" in trigger:
            if year_stem not in trigger["year_stems_any"]:
                matched = False
                continue

        # Đại Vận branch
        if "dai_van_branch_any" in trigger and matched:
            for cycle in dai_van:
                # cycle may have 'branch_index' or branch name
                bi = cycle.get("branch_index", -1)
                if bi >= 0:
                    br = BRANCHES[bi]
                    if br in trigger["dai_van_branch_any"]:
                        which_dai_van.append(
                            f"DV {cycle.get('cycle_index', '?')} tại {br} (tuổi {cycle.get('start_age', '?')}-{cycle.get('end_age', '?')})"
                        )
            if not which_dai_van:
                matched = False

        # Same palace + palace_any (Định tử sinh quyết Q4)
        if trigger.get("same_palace") and "stars_required" in trigger:
            stars_req = trigger["stars_required"]
            indices = [all_stars.get(s, -1) for s in stars_req]
            if -1 in indices or len(set(indices)) != 1:
                matched = False
                continue
            palace_any = trigger.get("palace_any", [])
            if palace_any:
                # Need same palace + that palace must be Mệnh or Thân
                # Find palace at this branch_idx
                star_branch_idx = indices[0]
                palaces = la_so.get("palaces", [])
                palace_at_star = next((p["name"] for p in palaces if p["branch_index"] == star_branch_idx), None)
                if palace_at_star not in palace_any:
                    matched = False
                    continue

        # Star at specific palace
        if "star_at_palace" in trigger:
            sp = trigger["star_at_palace"]
            star_idx = all_stars.get(sp["star"], -1)
            target_idx = BRANCHES.index(sp["branch"])
            if star_idx != target_idx:
                matched = False
                continue
            # Check additional sát required at same palace
            if "additional_required_any" in trigger and matched:
                any_match = False
                for add_s in trigger["additional_required_any"]:
                    if all_stars.get(add_s) == target_idx:
                        any_match = True
                        break
                    # Check tu_hoa
                    for hoa, hoa_star in tu_hoa.items():
                        if hoa == "Kỵ" and hoa_star == sp["star"]:
                            any_match = True
                            break
                if not any_match:
                    matched = False

        if matched:
            triggered.append({
                **pattern,
                "which_dai_van": which_dai_van,
            })

    return triggered


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/Users/ozvietnamdesktop/Desktop/yi")
    from engine.tu_vi.an_sao import cast_la_so
    from core.chronos import calculate_chronos_state

    chronos = calculate_chronos_state("1988-06-05T23:30:00", "Asia/Ho_Chi_Minh")
    d_str, m_str, _ = chronos.almanac.lunar_date.split("/")
    year_parts = chronos.ganzhi.year.split()
    la_so = cast_la_so(
        lunar_month=int(m_str), lunar_day=int(d_str), hour_branch="Tý",
        year_stem=year_parts[0], year_branch=year_parts[1], gender="nam",
    )
    triggered = detect_safety_patterns(la_so, year_parts[0])
    print(f"=== Founder safety check (year stem: {year_parts[0]}) ===")
    if not triggered:
        print("Không có pattern nào kích hoạt — lá số an toàn về phương diện này.")
    else:
        for p in triggered:
            print(f"\n⚠️ {p['title']} (source: {p['source']})")
            print(f"   Concern: {p['raw_concern']}")
            print(f"   Gentle: {p['gentle_message']}")
            if p.get("which_dai_van"):
                print(f"   Khi nào: {p['which_dai_van']}")
