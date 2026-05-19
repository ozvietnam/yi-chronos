"""Vietnamese question templates for 19 trait dimensions."""
from __future__ import annotations

TRAIT_TEMPLATES = {
    # ── Domain 1: NGOẠI HÌNH ────────────────────────────────────────────
    "body_height": {
        "question_vi": "Chiều cao của Anh so với người Việt cùng giới?",
        "domain": "ngoại hình",
        "value_labels": {
            "cao":        "Cao hơn trung bình",
            "trung_binh": "Trung bình",
            "thap":       "Thấp hơn trung bình",
        },
    },
    "body_build": {
        "question_vi": "Vóc dáng / khung xương của Anh?",
        "domain": "ngoại hình",
        "value_labels": {
            "gay_thon":   "Gầy thon, nhẹ cân",
            "trung_binh": "Cân đối trung bình",
            "day_dan":    "Đầy đặn, mềm mại",
            "dam_chac":   "Đậm chắc, vai rộng",
        },
    },
    "face_shape": {
        "question_vi": "Khuôn mặt của Anh có dạng nào gần nhất?",
        "domain": "ngoại hình",
        "value_labels": {
            "dai":   "Dài, gọn",
            "vuong": "Vuông, góc cạnh",
            "tron":  "Tròn, đầy đặn",
            "nhon":  "Sắc, hẹp về phía dưới",
            "oval":  "Oval cân đối",
        },
    },
    "skin_tone": {
        "question_vi": "Tông da tự nhiên của Anh?",
        "domain": "ngoại hình",
        "value_labels": {
            "trang":    "Trắng / sáng",
            "hong_hao": "Hồng hào, ấm",
            "vua":      "Trung bình, vàng nhẹ",
            "sam":      "Sậm, ngăm",
        },
    },
    "hair_quality": {
        "question_vi": "Tóc tự nhiên (chưa qua làm tóc) của Anh?",
        "domain": "ngoại hình",
        "value_labels": {
            "day_muot":   "Dày, mượt, mềm",
            "mong":       "Mỏng, thưa",
            "xoan":       "Xoăn / gợn",
            "thang_cung": "Thẳng, cứng",
        },
    },
    "eye_features": {
        "question_vi": "Mắt của Anh có đặc điểm gì?",
        "domain": "ngoại hình",
        "value_labels": {
            "sang_to":  "To, sáng, có thần",
            "sau_hep":  "Sâu, hẹp",
            "hien_min": "Mịn, hiền",
            "sac_net":  "Sắc, nét, ánh nhìn cương",
        },
    },
    "physiognomy_marks": {
        "question_vi": "Đỉnh đầu Anh có bao nhiêu xoáy tóc?",
        "domain": "ngoại hình",
        "value_labels": {
            "1_xoay":        "1 xoáy duy nhất",
            "2_xoay":        "2 xoáy",
            "vung_dac_biet": "Không rõ xoáy / có dấu hiệu khác (sẹo, đốm)",
        },
    },
    # ── Domain 2: TÍNH CÁCH ─────────────────────────────────────────────
    "decision_style": {
        "question_vi": "Khi gặp vấn đề lớn, Anh thường?",
        "domain": "tính cách",
        "value_labels": {
            "impulsive":    "Lao vào giải quyết ngay, không suy nghĩ nhiều",
            "analytical":   "Phân tích kỹ trước, lập kế hoạch",
            "consultative": "Tham khảo người khác, không quyết một mình",
            "patient":      "Lùi một bước, chờ thời cơ",
        },
    },
    "leadership_orientation": {
        "question_vi": "Trong nhóm / công việc, Anh thường ở vai trò?",
        "domain": "tính cách",
        "value_labels": {
            "dominant":      "Lãnh đạo, ra quyết định chính",
            "collaborative": "Cộng tác bình đẳng, xây dựng đồng thuận",
            "supportive":    "Hỗ trợ, giúp đỡ người dẫn dắt",
            "independent":   "Làm việc một mình, không thích team",
        },
    },
    "introvert_extrovert": {
        "question_vi": "Sau cuộc gặp đông người, Anh thấy?",
        "domain": "tính cách",
        "value_labels": {
            "mostly_extro": "Tràn năng lượng, muốn gặp thêm",
            "mid":          "Vừa phải — đôi khi vui, đôi khi mệt",
            "mostly_intro": "Mệt, cần thời gian một mình hồi phục",
        },
    },
    "emotional_pattern": {
        "question_vi": "Cảm xúc của Anh thường như thế nào?",
        "domain": "tính cách",
        "value_labels": {
            "cool":       "Bình tĩnh, ít thay đổi",
            "passionate": "Nồng nhiệt, dễ bùng cháy với điều thích",
            "volatile":   "Thay đổi nhanh — vui buồn lên xuống",
            "steady":     "Ổn định, đều đều, lâu dài",
        },
    },
    "communication_style": {
        "question_vi": "Cách Anh giao tiếp với người khác?",
        "domain": "tính cách",
        "value_labels": {
            "direct":     "Thẳng, nói ra ngay điều mình nghĩ",
            "nuanced":    "Tinh tế, chọn lời, đọc context",
            "quiet":      "Ít nói, lắng nghe nhiều hơn",
            "expressive": "Biểu cảm, kể chuyện sinh động",
        },
    },
    # ── Domain 3: ENERGY PATTERNS ───────────────────────────────────────
    "wake_natural_time": {
        "question_vi": "Khi không có lịch hẹn, Anh tự nhiên thức dậy lúc?",
        "domain": "năng lượng",
        "value_labels": {
            "truoc_5h": "Trước 5h sáng",
            "5_7h":     "5-7h",
            "7_9h":     "7-9h",
            "9_11h":    "9-11h",
            "muon":     "Sau 11h",
        },
    },
    "energy_peak_period": {
        "question_vi": "Anh thấy mình tỉnh táo / năng lượng cao nhất khi nào?",
        "domain": "năng lượng",
        "value_labels": {
            "sang":  "Sáng (5-11h)",
            "trua":  "Trưa (11-13h)",
            "chieu": "Chiều (13-17h)",
            "toi":   "Tối (17-21h)",
            "dem":   "Đêm khuya (sau 21h)",
        },
    },
    "sleep_pattern": {
        "question_vi": "Anh thường đi ngủ lúc?",
        "domain": "năng lượng",
        "value_labels": {
            "truoc_22h": "Trước 22h",
            "22_23h":    "22-23h",
            "23_1h":     "23h-1h sáng",
            "sau_1h":    "Sau 1h sáng",
        },
    },
    # ── Domain 4: LIFE EVENTS ───────────────────────────────────────────
    "career_direction": {
        "question_vi": "Anh hướng nghề nghiệp nào?",
        "domain": "sự nghiệp",
        "value_labels": {
            "corporate":       "Công ty lớn, vai trò ổn định",
            "creative":        "Sáng tạo, nghệ thuật, viết, thiết kế",
            "entrepreneurial": "Khởi nghiệp, làm riêng",
            "professional":    "Chuyên môn sâu (bác sĩ, kỹ sư, luật sư)",
            "craftsman":       "Tay nghề, thủ công, kỹ thuật cụ thể",
        },
    },
    "sibling_position_likely": {
        "question_vi": "Anh là con thứ mấy trong nhà?",
        "domain": "gia đình",
        "value_labels": {
            "ca":       "Con cả",
            "giua":     "Con giữa",
            "ut":       "Con út",
            "duy_nhat": "Con duy nhất",
        },
    },
    "marriage_timing_rough": {
        "question_vi": "Anh kết hôn (hoặc dự đoán kết hôn) ở độ tuổi?",
        "domain": "hôn nhân",
        "value_labels": {
            "som_25":  "Trước 25",
            "25_30":   "25-30",
            "30_35":   "30-35",
            "muon_35": "Sau 35",
        },
    },
    "health_pattern_general": {
        "question_vi": "Sức khoẻ tổng thể của Anh?",
        "domain": "sức khoẻ",
        "value_labels": {
            "strong":     "Rất khoẻ, hiếm ốm",
            "on":         "Ổn định, thỉnh thoảng cảm thường",
            "nhay":       "Nhạy cảm — dễ mệt khi căng thẳng",
            "yeu_vung_x": "Có vùng yếu cụ thể (tiêu hoá / hô hấp / xương khớp)",
        },
    },
}
