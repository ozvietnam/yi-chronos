"""Task profiles cho KMDG analyze_for_task() — task-oriented luận bàn.

Source: Đàm Liên Chương I phần IV-V (pages 36-50) — mỗi cách cục có gắn
với danh sách việc cụ thể. Em đọc kỹ + tổng hợp 15 việc cổ điển.

Paradigm: KMDG cổ điển = TASK-ORIENTED. User hỏi "Tôi muốn làm X, có thuận không?"
KHÔNG phải "Bàn này tốt/xấu chung". Iron Rule #4/#6 vẫn giữ — đây là QUAN-SÁT
đồng dạng cho VIỆC, không predict cát hung tuyệt đối.
"""

# 15 tasks cổ điển KMDG + 'Quan-sát chung' default
TASK_PROFILES = {
    "Kết hôn": {
        "label": "Kết hôn / Cưới gả",
        "favored_mon": ["休", "生"],     # Hưu, Sinh
        "favored_tinh": ["輔", "禽", "心"],  # Phụ, Cầm, Tâm
        "favored_than": ["合"],           # Lục Hợp
        "favored_cach_cuc": ["Trùng Trá", "Hưu Trá", "Tam Cơ Thăng Điện", "Nhân Độn", "Tam Trá"],
        "avoid_mon": ["傷", "杜", "死"],
        "avoid_tinh": ["蓬", "芮"],
        "avoid_than": ["蛇", "雀"],
        "avoid_cach_cuc": ["Hình Cách", "Phục Can Cách", "Bạch Hổ Xương Cuồng"],
        "note": "Đàm Liên: Hôn nhân hợp Hưu môn (sum họp) + Sinh môn (sinh sôi) + Lục Hợp (môi giới). Tránh Thương môn (thị phi) + Bồng/Nhuế (hung tinh).",
    },
    "Khởi nghiệp": {
        "label": "Khởi nghiệp / Kinh doanh / Cầu tài",
        "favored_mon": ["開", "生"],
        "favored_tinh": ["輔", "心", "禽"],
        "favored_than": ["符", "天"],     # Trực Phù, Cửu Thiên
        "favored_cach_cuc": ["Thanh Long Hồi Thủ", "Phi Điểu Trật Huyệt", "Thiên Độn", "Trùng Trá"],
        "avoid_mon": ["死", "驚"],
        "avoid_tinh": ["蓬", "芮"],
        "avoid_cach_cuc": ["Hình Cách", "Phục Ngâm (Tinh/Môn)", "Thanh Long Đào Tẩu"],
        "note": "Khởi nghiệp cần Khai môn (mở đầu) + Sinh môn (sinh sôi). Trị Phù dẫn dắt. Tránh Tử/Kinh (kết thúc/giật mình).",
    },
    "Đi xa": {
        "label": "Đi xa / Xuất hành",
        "favored_mon": ["開", "生", "休"],
        "favored_tinh": ["輔"],
        "favored_than": ["天"],          # Cửu Thiên
        "favored_cach_cuc": ["Thanh Long Hồi Thủ", "Tam Cơ Thăng Điện"],
        "avoid_mon": ["傷", "驚"],
        "avoid_cach_cuc": ["Lục Nghi Kích Hình", "Hình Cách"],
        "note": "Đi xa cần Khai (mở đường) + Cửu Thiên (vươn cao). Tránh Thương (tai nạn đường) + Lục Nghi Kích Hình (đại kỵ).",
    },
    "Thăng quan": {
        "label": "Thăng quan / Cầu quan",
        "favored_mon": ["開", "景"],
        "favored_tinh": ["輔", "英"],
        "favored_than": ["天"],
        "favored_cach_cuc": ["Đại Giả", "Tam Cơ Thăng Điện", "Thiên Độn"],
        "avoid_mon": ["死"],
        "avoid_cach_cuc": ["Phục Ngâm (Tinh/Môn)"],
        "note": "Đại Giả 'gặp quý nhân dâng kế'. Cảnh môn (truyền tin) + Thiên Anh (sáng danh) + Cửu Thiên.",
    },
    "Học tập": {
        "label": "Học tập / Thi cử",
        "favored_mon": ["開", "休", "景"],
        "favored_tinh": ["輔", "心"],
        "favored_than": ["合"],
        "favored_cach_cuc": ["Thiên Độn", "Tam Cơ Thăng Điện"],
        "avoid_mon": ["傷", "杜"],
        "note": "Thiên Phụ = học hành, văn thư. Cảnh môn (sáng tỏ) + Lục Hợp (giảng học bạn bè).",
    },
    "Chữa bệnh": {
        "label": "Chữa bệnh / Uống thuốc",
        "favored_mon": ["休"],
        "favored_tinh": ["心"],
        "favored_than": ["合"],
        "favored_cach_cuc": ["Hưu Trá"],
        "avoid_mon": ["死"],
        "avoid_tinh": ["蓬", "芮"],
        "note": "Hưu Trá ĐẶC THÙ = 'hợp uống thuốc, trị bệnh'. Thiên Tâm = y dược. Tránh Tử môn + Nhuế (bệnh tinh).",
    },
    "Gặp quý nhân": {
        "label": "Gặp quý nhân / Xin giúp đỡ",
        "favored_mon": ["開", "生"],
        "favored_tinh": ["輔"],
        "favored_than": ["合", "天"],
        "favored_cach_cuc": ["Đại Giả", "Trùng Trá", "Tam Cơ Thăng Điện"],
        "avoid_than": ["蛇", "雀"],
        "note": "Đại Giả/Trùng Trá đều có 'gặp người quyền quý'. Cửu Thiên + Lục Hợp = hòa hợp giao tế.",
    },
    "Mai phục": {
        "label": "Mai phục / Xuất binh",
        "favored_mon": ["杜", "休", "生"],   # Đỗ môn = đóng kín
        "favored_than": ["陰", "地"],        # Thái Âm, Cửu Địa
        "favored_cach_cuc": ["Quỷ Độn", "Phong Độn", "Vân Độn", "Long Độn", "Hổ Độn", "Trùng Trá"],
        "avoid_cach_cuc": ["Phục Ngâm (Tinh/Môn)"],
        "note": "Đỗ môn (đóng kín bảo mật) + Thái Âm/Cửu Địa (kín đáo). 5 độn quân sự đều phù hợp.",
    },
    "Ẩn náu": {
        "label": "Ẩn náu / Lánh nạn",
        "favored_mon": ["杜", "休"],
        "favored_than": ["陰", "地"],
        "favored_cach_cuc": ["Địa Giả"],
        "avoid_than": ["天", "符"],   # Quá vươn cao, không phù hợp ẩn
        "note": "Địa Giả = 'ẩn mình lánh nạn, thăm dò, điều tra'. Thái Âm/Cửu Địa kín đáo.",
    },
    "Mai táng": {
        "label": "Mai táng / Tang lễ",
        "favored_mon": ["死"],          # ĐẶC THÙ: Tử môn TỐT cho tang lễ
        "favored_cach_cuc": ["Vật Giả", "Quy Giả"],
        "avoid_cach_cuc": ["Thiên Độn", "Địa Độn", "Quỷ Độn", "Phong Độn", "Vân Độn", "Long Độn", "Hổ Độn"],  # Cửu Độn kỵ an táng
        "note": "Tử môn ĐẶC THÙ TỐT cho tang lễ (ngoại lệ paradigm). Vật Giả/Quy Giả phù hợp. CỬU ĐỘN kỵ an táng.",
    },
    "Tu sửa mộ": {
        "label": "Tu sửa mộ",
        "favored_cach_cuc": ["Quy Giả"],
        "favored_tinh": ["輔", "心"],
        "favored_mon": ["休", "生"],
        "note": "Quy Giả = 'hợp sửa mộ, đi săn'. Thiên Phụ cát.",
    },
    "Săn bắn": {
        "label": "Săn bắn",
        "favored_cach_cuc": ["Long Độn", "Quy Giả"],
        "favored_mon": ["傷"],          # paradox: Thương = bắt tội phạm + săn
        "note": "Long Độn = 'săn bắn, thủy chiến'. Thương môn PARADOX: hại với hành nhân thường, lợi cho thợ săn.",
    },
    "Cầu mưa": {
        "label": "Cầu mưa / Thời tiết",
        "favored_cach_cuc": ["Long Độn", "Vân Độn"],
        "note": "Long Độn + Vân Độn ĐẶC THÙ cho cầu mưa.",
    },
    "Tìm đồ mất": {
        "label": "Tìm đồ mất / Truy đuổi",
        "favored_mon": ["驚"],          # Kinh môn paradox: tốt cho truy đuổi
        "favored_cach_cuc": ["Nhân Giả"],
        "note": "Kinh môn PARADOX: 'dễ tìm đồ đã mất, truy đuổi tội phạm'.",
    },
    "Bắt tội phạm": {
        "label": "Bắt tội phạm / Điều tra",
        "favored_mon": ["傷", "驚"],
        "favored_cach_cuc": ["Nhân Giả", "Địa Giả"],
        "note": "Nhân Giả = 'bắt bớ, tù đày'. Thương + Kinh môn PARADOX dùng được.",
    },
    "Quan-sát chung": {
        "label": "Quan-sát chung (không task cụ thể)",
        "note": "Không task. Em hiển thị paradigm chung + cách cục dominant. Iron Rule #4: đọc đồng dạng, không predict.",
    },
}


def analyze_for_task(state: dict, task_name: str) -> dict:
    """Phân tích bàn KMDG theo task cụ thể.

    Args:
        state: ky_mon_state output từ cast()
        task_name: tên task trong TASK_PROFILES (tiếng Việt key)

    Returns:
        {
            "task": tên task,
            "task_label": label friendly,
            "note": Đàm Liên note + paradigm,
            "huong_tot": [{cung, direction, score, reasons[]}, ...] (top 3),
            "huong_tranh": [{cung, direction, score, reasons[]}, ...] (top 2 negative),
            "cach_cuc_relevant": [{...cach_cuc, task_match: 'favored'|'avoid'}],
        }
    """
    profile = TASK_PROFILES.get(task_name, TASK_PROFILES["Quan-sát chung"])

    result = {
        "task": task_name,
        "task_label": profile.get("label", task_name),
        "note": profile.get("note", ""),
        "huong_tot": [],
        "huong_tranh": [],
        "cach_cuc_relevant": [],
    }

    # Quan-sát chung: skip detailed scoring
    if task_name == "Quan-sát chung":
        return result

    # Build lookups by cung
    thien_by_cung = {c["cung_vn"]: c for c in state.get("thien_ban", [])}
    dia_by_cung = {c["cung_vn"]: c for c in state.get("dia_ban", [])}
    mon_by_cung = {c["cung_vn"]: c for c in state.get("mon", [])}
    tinh_by_cung = {c["cung_vn"]: c for c in state.get("tinh", [])}
    than_by_cung = {c["cung_vn"]: c for c in state.get("than", [])}

    cung_list = ["Khảm", "Cấn", "Chấn", "Tốn", "Ly", "Khôn", "Đoài", "Càn"]  # skip Trung
    cung_scores = []

    favored_mon = set(profile.get("favored_mon", []))
    avoid_mon = set(profile.get("avoid_mon", []))
    favored_tinh = set(profile.get("favored_tinh", []))
    avoid_tinh = set(profile.get("avoid_tinh", []))
    favored_than = set(profile.get("favored_than", []))
    avoid_than = set(profile.get("avoid_than", []))

    for cung in cung_list:
        thien = thien_by_cung.get(cung, {})
        dia = dia_by_cung.get(cung, {})
        mon = mon_by_cung.get(cung, {})
        tinh = tinh_by_cung.get(cung, {})
        than = than_by_cung.get(cung, {})

        score = 0
        reasons = []

        mon_zh = mon.get("mon_zh", "")
        tinh_zh = tinh.get("tinh_zh", "")
        than_zh = than.get("than_zh", "")

        if mon_zh in favored_mon:
            score += 3
            reasons.append(f"{mon.get('mon_vn', '?')} môn — cát cho việc này")
        if mon_zh in avoid_mon:
            score -= 3
            reasons.append(f"{mon.get('mon_vn', '?')} môn — TRÁNH cho việc này")

        if tinh_zh in favored_tinh:
            score += 2
            reasons.append(f"{tinh.get('tinh_vn', '?')} — sao phù hợp")
        if tinh_zh in avoid_tinh:
            score -= 2
            reasons.append(f"{tinh.get('tinh_vn', '?')} — sao bất lợi")

        if than_zh in favored_than:
            score += 2
            reasons.append(f"{than.get('than_vn', '?')} — thần hỗ trợ")
        if than_zh in avoid_than:
            score -= 2
            reasons.append(f"{than.get('than_vn', '?')} — thần ngại")

        if score != 0:
            cung_scores.append({
                "cung": cung,
                "cung_zh": thien.get("cung_zh", ""),
                "direction": thien.get("direction", ""),
                "score": score,
                "reasons": reasons,
                "mon": mon.get("mon_vn", ""),
                "tinh": tinh.get("tinh_vn", ""),
                "than": than.get("than_vn", ""),
            })

    # Sort by score: positive descending for huong_tot, negative ascending for huong_tranh
    positive = sorted([c for c in cung_scores if c["score"] > 0], key=lambda x: -x["score"])
    negative = sorted([c for c in cung_scores if c["score"] < 0], key=lambda x: x["score"])

    result["huong_tot"] = positive[:3]
    result["huong_tranh"] = negative[:2]

    # Check matching cách cục
    favored_cc = set(profile.get("favored_cach_cuc", []))
    avoid_cc = set(profile.get("avoid_cach_cuc", []))

    for cc in state.get("cach_cuc_detected", []):
        if cc.get("name") in favored_cc:
            result["cach_cuc_relevant"].append({**cc, "task_match": "favored"})
        elif cc.get("name") in avoid_cc:
            result["cach_cuc_relevant"].append({**cc, "task_match": "avoid"})

    return result


def list_tasks() -> list[dict]:
    """Return list of tasks for UI dropdown."""
    return [
        {"key": k, "label": v.get("label", k)}
        for k, v in TASK_PROFILES.items()
    ]
