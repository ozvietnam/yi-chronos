"""THỜI Quẻ — Xác định THỜI mà cấu trúc Hà Lạc đặt anh vào.

Paradigm Xuân Cang p.65 (vòng 4):
> "Cổ bộ Kinh Dịch, quy lại chỉ một chữ Thời. 64 quẻ Dịch là 64 Thời."

THỜI ở đây là THỜI CỦA BẢN THỂ, không phải thời sự khách quan.
Cấu trúc Hà Lạc (quẻ Tiên Thiên = THỜI TỔNG, quẻ Hậu Thiên = THỜI ỨNG DỤNG)
cho biết anh thuộc THỜI nào trong trời đất.

Mỗi THỜI cho 1 paradigm guidance:
- nên CƯƠNG hay NHU?
- nên TIẾN hay THOÁI?
- nên ĐỘNG hay NHẪN?
- nên TẤN CÔNG hay NHƯỜNG NHỊN?

⚠️ Iron Rule #4+6: KHÔNG predict cát/hung tĩnh.
THỜI = đọc đồng dạng cấu trúc khoảnh khắc sinh.

Reference: Xuân Cang p.65, Nguyễn Hiến Lê "Kinh Dịch — Đạo của người quân tử".
"""

from __future__ import annotations


# 64 THỜI — paradigm guidance per quẻ.
# Schema: {quẻ_name: {bản_chất, nên_thế_nào, paradigm_keyword, source_lines}}
# Bắt đầu với các quẻ đã đọc (vòng 4-5) + framework cho 59 quẻ còn lại.
THOI_QUE_TABLE: dict[str, dict] = {
    "Càn": {
        "ban_chat": "Thời TỰ CƯỜNG, không ngừng nghỉ — như rồng lên cuồn cuộn",
        "nen_the_nao": "Tự rèn nội lực không ngừng. Việc bản thân, việc nhà, việc lớn đều như vậy.",
        "paradigm_keyword": "tự_cường",
        "nguyet_lenh_thang": 4,
        "tu_duc": ["Nguyên", "Hành", "Lợi", "Trinh"],
        "yeu_dieu_canh_bao": (
            "Hào 6 Càn = 'Kháng long hữu hối' — rồng bay quá cao có điều phải hối. "
            "Tự cường nhưng phải biết khiêm. Hào 1 = Tiềm long: chưa thể dùng tài."
        ),
    },
    "Khôn": {
        "ban_chat": "Thời NHU THUẬN, bao dung — như đất dày bao bọc",
        "nen_the_nao": "KHÔNG khởi xướng (việc khởi xướng để Càn). Chờ người khác khởi rồi thuận theo + góp công.",
        "paradigm_keyword": "nhu_thuan",
        "nguyet_lenh_thang": 10,
        "tu_duc": ["Nguyên", "Hành", "Lợi", "Trinh (chính + bền + thuận)"],
        "phuong_huong": "Tây Nam được bạn, Đông Bắc mất bạn",
        "yeu_dieu_canh_bao": (
            "Hào 6 Khôn = 'Long chiến ngoài nội, máu chảy đen vàng' — "
            "Âm cực thịnh tất xung đột với Dương, cả 2 đều bại. "
            "Hào 5 = 'Hoàng thường nguyên cát' (xiêm vàng cực tốt) — vẻ đẹp tiềm ẩn + khiêm nhường."
        ),
        "case_study": (
            "Nam Khoái bói được hào 5 Khôn cho là rất tốt — sau thất bại. "
            "Tử Phục Huệ Bá: 'Bói đúng chưa đủ — phải có TRUNG + CHÍNH + đúng đạo lý.' "
            "→ Lý số Hà Lạc cần vận dụng LINH HOẠT."
        ),
    },
    "Truân": {
        "ban_chat": "Thời GIAN TRUÂN — khó khăn nhưng có cơ hội (vạn vật mới sinh, hỗn mang)",
        "nen_the_nao": "Cần tài + chí + bạn hiền tài. Quẻ Ngoại Khảm (hiểm) trên quẻ Nội Chấn (động) — hành động trong hiểm, phải mạo hiểm có chí.",
        "paradigm_keyword": "gian_truan_co_co",
        "nguyet_lenh_thang": 6,
        "tu_duc": ["Nguyên", "Hành", "Lợi", "Trinh"],
        "tuong": "Trên trời có Mây + Sấm — chưa có Mưa. Cơ trời đang vận động.",
        "yeu_dieu_canh_bao": "Thời Truân cần người giỏi tổ chức + sắp xếp. Người quân tử ý thức sứ mệnh đó.",
        "case_study": (
            "Quang Trung bắt Nguyễn Hoàng Đức người Gia Long, "
            "mời lên ngủ chung giường — đó là tượng hào 1 Truân (dùng dằng nhưng có chí)."
        ),
    },
    "Mông": {
        "ban_chat": "Thời MÔNG MUỘI — non yếu, cần được hướng dẫn (như trẻ thơ + suối mới chảy)",
        "nen_the_nao": "Trò cầu thầy, KHÔNG phải thầy cầu trò. Hỏi 1 lần thì bảo. 2-3 lần là nhàm, KHÔNG bảo.",
        "paradigm_keyword": "mong_muoi_can_day",
        "nguyet_lenh_thang": 8,
        "tu_duc": ["Hành", "Lợi", "Trinh"],
        "tuong": "Trên Cấn (núi), dưới Khảm (nước sâu) — tối tăm. Dưới chân núi có suối nhỏ.",
        "key_rule_THOIDAU": (
            "**Trình Di về quẻ Mông**: Hỏi = bói. Mới bói thì thành tâm. "
            "Bói 2-3 lần là phiền nhiễu, không thành tâm, là nhảm nhí khinh nhờn — "
            "KHÔNG nên bảo nữa. Cả người hỏi người bảo đều phiền nhảm. "
            "→ ĐÂY LÀ GỐC TRỰC TIẾP CỦA IRON RULE #4 ('bất nghi bất bốc, "
            "một việc bói một lần') — Khang Tiết KẾ THỪA, không phát minh."
        ),
    },
    "Nhu": {
        "ban_chat": "Thời CHỜ ĐỢI — kiên cứng cần tiến nhưng gặp Khảm hiểm, phải đợi",
        "nen_the_nao": "Ăn uống vui vẻ, dưỡng thân, tỉnh thản chờ. Sắp đặt sẵn sàng trước, chứa trữ đầy đủ.",
        "paradigm_keyword": "cho_doi",
        "nguyet_lenh_thang": 8,
        "tuong": "Mây bao kín bầu trời — thế nào cũng mưa. Cứ chờ.",
        "tu_duc": ["3 nghĩa: Cần thiết / Chờ đợi / Do dự (không dùng nghĩa do dự)"],
        "key_paradigm": (
            "**PBC paradigm chữ TRUNG hào 2 Nhu**: "
            "Nhiệt tâm mà không quá nóng / Trầm tĩnh mà không quá nguội / "
            "Cẩn thận mà không hồ nghi / Thung dung mà không chậm trễ. "
            "Thời chưa đến, ai đẩy mấy cũng không đi; thời đến rồi, ai kéo lại vẫn cố tới."
        ),
        "yeu_dieu_canh_bao": "Hào 3 Nhu = 'Đợi ở chỗ bùn — tự vời giặc đến'. Sát Khảm rồi, phải kính cẩn thận trọng.",
    },
}


# 5 cặp đối lập THỜI (giúp đọc đồng dạng nhanh)
THOI_DOI_LAP: list[tuple[str, str]] = [
    ("Càn", "Khôn"),       # Tự cường ↔ Nhu thuận
    ("Truân", "Giải"),     # Gian truân ↔ Giải thoát
    ("Mông", "Cách"),      # Mông muội ↔ Cách mạng
    ("Nhu", "Tụng"),       # Chờ đợi ↔ Tranh tụng
    ("Thái", "Bĩ"),        # Hanh thông ↔ Bế tắc
]


def lookup_thoi(quai_name: str) -> dict | None:
    """Trả về paradigm guidance cho quẻ này."""
    return THOI_QUE_TABLE.get(quai_name)


def describe_thoi_cau_truc(tien_thien_name: str, hau_thien_name: str) -> dict:
    """Mô tả THỜI TỔNG (Tiên Thiên) + THỜI ỨNG DỤNG (Hậu Thiên) cho cấu trúc Hà Lạc.

    Args:
        tien_thien_name: tên quẻ Tiên Thiên (vd "Tiết")
        hau_thien_name: tên quẻ Hậu Thiên (vd "Tập Khảm")

    Returns: dict với 2 keys (tien_thien_thoi, hau_thien_thoi).
    """
    tt = lookup_thoi(tien_thien_name)
    ht = lookup_thoi(hau_thien_name)
    return {
        "tien_thien_thoi": {
            "que": tien_thien_name,
            "data": tt,
            "narrative": (
                f"**THỜI TỔNG (Tiên Thiên = THỂ)**: {tt['ban_chat']}" if tt
                else f"**THỜI TỔNG (Tiên Thiên = THỂ)**: quẻ {tien_thien_name} — TODO wiki citation"
            ),
        },
        "hau_thien_thoi": {
            "que": hau_thien_name,
            "data": ht,
            "narrative": (
                f"**THỜI ỨNG DỤNG (Hậu Thiên = DỤNG)**: {ht['ban_chat']}" if ht
                else f"**THỜI ỨNG DỤNG (Hậu Thiên = DỤNG)**: quẻ {hau_thien_name} — TODO wiki citation"
            ),
        },
        "paradigm_guard": (
            "⚠️ THỜI = đọc đồng dạng cấu trúc khoảnh khắc sinh, KHÔNG predict tĩnh đời người. "
            "Iron Rule #4+6 — anh sống thế nào, THỜI có thể chuyển."
        ),
        "source": "Xuân Cang p.65 — '64 quẻ Dịch là 64 Thời, 384 hào là 384 hoàn cảnh'",
    }
