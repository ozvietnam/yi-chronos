"""Hoàng Tuấn paradigm — Lý Thuyết Tượng Số + Phép Tính Số Hà Lạc.

Source: HOÀNG TUẤN (Đại tá, Giáo sư, Giám đốc BV 19-8 Bộ Công an).
Sách "Lý Thuyết Tượng Số" 375 trang, "Kinh Dịch và Hệ Nhị Phân" 842 trang.

Đây là góc nhìn KHOA HỌC HIỆN ĐẠI về Hà Lạc — bổ sung trực tiếp cho engine
Xuân Cang (paradigm cổ điển) đã có.

Bổ sung 3 đóng góp lớn:
1. Paradigm "PHÂN LOẠI NHÂN HỌC CỔ" — answer cho user "tại sao hàng triệu người cùng lá số?"
2. KHỔNG MINH 7 CÁCH PHỐI HỢP đánh giá tính cách — tiêu chí dùng người
3. CỤM TỪ BIỂU TƯỢNG + tục ngữ VN — dataset cho LLM render luận giải hấp dẫn

Phương pháp 14 bước lấy lá số Hà Lạc của Hoàng Tuấn — chi tiết hơn Xuân Cang.
"""

from __future__ import annotations


# ── 1. Paradigm "PHÂN LOẠI NHÂN HỌC CỔ" ──────────────────────────────────────
PHAN_LOAI_NHAN_HOC_PARADIGM: dict[str, str] = {
    "ban_chat": (
        "Hà Lạc + Tử Vi là MÔN PHÂN LOẠI NHÂN HỌC CỔ. 64 quẻ × 6 hào = 384 (Hà Lạc) "
        "hoặc 525,948 lá số Tử Vi = tiêu chí phân loại CHI TIẾT người theo Hệ Tọa Độ "
        "Không-Thời Gian (giờ-ngày-tháng-năm sinh)."
    ),
    "answer_cho_user": (
        "User thường hỏi: 'Hàng triệu người cùng lá số — số phận giống hệt nhau ư? Không thể!'"
        "\n\n"
        "Answer Hoàng Tuấn: 'Cùng giới đàn ông/đàn bà cũng có hàng tỷ người — nhưng PHÂN LOẠI "
        "giới tính ĐÚNG. Cùng tuổi sơ sinh/nhi đồng/thanh niên/già — cũng đúng phân loại. "
        "Hà Lạc + Tử Vi là phân loại CHI TIẾT hơn (hàng chục vạn loại) → xác suất giống nhau "
        "ở người cùng loại RẤT LỚN, nhưng KHÔNG giống nhau hoàn toàn từng chi tiết."
    ),
    "cross_link_iron_rule_4_6": (
        "Khớp đúng Iron Rule #4+6 của project: 'Đọc đồng dạng, KHÔNG predict tĩnh.' "
        "Hoàng Tuấn nói: 'Số Hà Lạc CHỈ cho HƯỚNG và NÉT LỚN — chi tiết phải do chính người đó.' "
        "→ Hai nguồn độc lập xác nhận paradigm."
    ),
    "phuong_phap_doi_xung_voi_khoa_hoc_hien_dai": (
        "Khoa học hiện đại = chia cắt vấn đề → nghiên cứu chi tiết + thực nghiệm chứng minh. "
        "Hà Lạc/Tử Vi = TỔNG HỢP (nhân tướng + cơ thể + tâm lý + xã hội) → trực giác + kinh nghiệm. "
        "Hai phương pháp TƯƠNG PHẢN nhưng BẤT KHẢ TƯƠNG VÔ (như âm-dương Dịch cổ) — "
        "BỔ SUNG cho nhau, không cái nào đúng hẳn cũng không cái nào sai hoàn toàn."
    ),
}


# ── 2. KHỔNG MINH 7 cách PHỐI HỢP đánh giá người ────────────────────────────
# Source: Khổng Minh (Gia Cát Lượng) — Hoàng Tuấn trích trong sách Lý Thuyết Tượng Số
KHONG_MINH_7_CACH: list[dict] = [
    {
        "stt": 1,
        "cach": "Đem điều PHẢI, lẽ TRÁI hỏi họ",
        "muc_dich": "Tìm hiểu CHÍ HƯỚNG",
        "vi_du_hien_dai": "Đưa case study mơ hồ về đạo đức (kiểu trolley problem) → xem họ ưu tiên giá trị nào",
    },
    {
        "stt": 2,
        "cach": "Đem LÝ LUẬN dồn họ vào THẾ BÍ",
        "muc_dich": "Biết phản ứng ĐÚNG-SAI",
        "vi_du_hien_dai": "Stress test phỏng vấn → người này phản ứng có lý không, hay cứng đầu chối",
    },
    {
        "stt": 3,
        "cach": "Lấy MƯU TRÍ thử họ",
        "muc_dich": "Biết KIẾN THỨC",
        "vi_du_hien_dai": "Đưa vấn đề phức tạp (system design, debug edge case) → xem họ có biết chiều sâu",
    },
    {
        "stt": 4,
        "cach": "Cho họ biết những KHÓ KHĂN",
        "muc_dich": "Để xét ĐỨC DŨNG",
        "vi_du_hien_dai": "Mô tả trade-off, scenario khó → xem họ có gan ra quyết định, không đùn đẩy",
    },
    {
        "stt": 5,
        "cach": "Đưa họ vào LỢI LỘC",
        "muc_dich": "Biết mức LIÊM CHÍNH",
        "vi_du_hien_dai": "Đặt offer hấp dẫn nhưng có conflict of interest → xem họ có dao động không",
    },
    {
        "stt": 6,
        "cach": "HẸN CÔNG VIỆC với họ",
        "muc_dich": "Đo lường CHỮ TÍN",
        "vi_du_hien_dai": "Giao deadline có thể trễ → xem họ có giữ lời, có báo trước nếu trễ",
    },
    {
        "stt": 7,
        "cach": "Cho họ uống RƯỢU SAY",
        "muc_dich": "Dò TÂM TÍNH",
        "vi_du_hien_dai": "Casual hangout không công việc → xem tính cách thật bộc lộ khi tỉnh táo giảm",
    },
]


KHONG_MINH_PARADIGM_TAM_TUONG: str = (
    "Khổng Minh coi trọng cái **TÂM TƯỚNG** hơn là **NGOẠI TƯỚNG**. "
    "Trông hình tướng bên ngoài khó chính xác — nhiều khi TRÁI NGƯỢC, sai lầm. "
    "(Ông trích: 'Kẻ trông hiền lành nhu thuận mà vô đạo. Kẻ bề ngoài cung kính mà trong lòng "
    "trí tuệ vô lễ. Kẻ trông hùng dũng nhưng lại nhát gan. Kẻ có vẻ tận tụy nhưng lại bất trung...'). "
    "→ Cross-link Iron Rule project: KHÔNG đánh giá người qua bề ngoài (commit message đẹp, "
    "code phức tạp...) — đánh giá qua KẾT QUẢ + 7 cách phối hợp Khổng Minh."
)


# ── 3. CỤM TỪ BIỂU TƯỢNG + tục ngữ — dataset cho LLM render ──────────────────
CUM_TU_BIEU_TUONG: list[dict] = [
    {
        "han_viet": "Bàn thuyên tại liễu",
        "nghia": "Con én sầu bị rét đậu trên cành liễu",
        "ung_dung": "Số phận khốn khổ tuyệt vọng, không nơi nương tựa vững chắc",
    },
    {
        "han_viet": "Vân đầu vọng nguyệt",
        "nghia": "Chờ trăng ra khỏi đám mây",
        "ung_dung": "Mơ tưởng hão huyền, có chút hy vọng nhưng chẳng biết bao giờ vận may đến",
    },
    {
        "han_viet": "Y cẩm kỵ ngưu",
        "nghia": "Áo gấm cưỡi trâu",
        "ung_dung": "Giả dối vụng về, muốn che mắt người (có áo gấm thì phải cưỡi ngựa, không ai cưỡi trâu)",
    },
    {
        "han_viet": "Ngọc thụ lâm phong",
        "nghia": "Cây ngọc gặp gió",
        "ung_dung": "Người đàn bà quyền quý gặp nạn",
    },
]


TUC_NGU_VIET_LUAN_GIAI: list[dict] = [
    {
        "tuc_ngu": "Đo gốm bài đêm",
        "nghia": "Nghèo khổ giả dối",
    },
    {
        "tuc_ngu": "Tối biết ma ăn cỗ",
        "nghia": "Việc làm mờ ám trong bóng tối",
    },
    {
        "tuc_ngu": "Thằng còng làm cho thằng ngay ăn",
        "nghia": "Bất công xã hội — người làm khổ không được hưởng",
    },
    {
        "tuc_ngu": "Lắm sãi không ai đóng cửa chùa",
        "nghia": "Đông người mà không ai chịu trách nhiệm",
    },
    {
        "tuc_ngu": "Đời cha ăn mặn đời con khát nước",
        "nghia": "Hậu quả lâu dài — nghiệp đời trước ảnh hưởng đời sau",
    },
    {
        "tuc_ngu": "Cái sảy nảy cái ung",
        "nghia": "Họa nhỏ thành họa lớn — phòng từ gốc (paradigm quẻ Tụng PBC)",
    },
]


# ── 4. Phương pháp 14 BƯỚC lấy lá số Hà Lạc (Hoàng Tuấn) ────────────────────
PHUONG_PHAP_14_BUOC_HOANG_TUAN: list[dict] = [
    {"buoc": 1, "noi_dung": "Chuyển năm-tháng-ngày-giờ DƯƠNG → 8 chữ CAN CHI âm lịch"},
    {"buoc": 2, "noi_dung": "Ghi số Can Chi hoạt hóa: Thiên Can theo số cung Lạc Thư, Địa Chi theo số sinh-thành Hà Đồ"},
    {"buoc": 3, "noi_dung": "Xem quẻ NGUYỆT LỆNH của tháng sinh → đắc quái hay không đắc quái"},
    {"buoc": 4, "noi_dung": "Tìm tổng số ÂM + ÂM DƯƠNG → so với quẻ Nguyệt Lệnh hợp/không hợp"},
    {"buoc": 5, "noi_dung": "Thông qua tổng số ÂM DƯƠNG → tìm quẻ GỐC (Tiên Thiên / Bản Mệnh) + quẻ HỖ TRỢ"},
    {"buoc": 6, "noi_dung": "Đánh giá đại cương Quẻ + Hào"},
    {"buoc": 7, "noi_dung": "Xác định HÀO NGUYÊN ĐƯỜNG của quẻ Tiên Thiên theo giờ sinh"},
    {"buoc": 8, "noi_dung": "Tìm quẻ BIẾN / HẬU THIÊN: hoán vị Thượng-Hạ Tiên Thiên + biến hào Nguyên Đường"},
    {"buoc": 9, "noi_dung": "Xác định QUẺ THỂ + QUẺ DỤNG. Đánh giá suy-vượng theo Hành + tương sinh-khắc"},
    {"buoc": 10, "noi_dung": "Tìm NIÊN MỆNH năm sinh (60 năm Giáp Tý) → so với Hành quẻ Tiên Thiên tương sinh/khắc"},
    {"buoc": 11, "noi_dung": "Tìm HÓA CÔNG + Thiên Nguyên Khí + Địa Nguyên Khí cả 2 quẻ Tiên+Hậu"},
    {"buoc": 12, "noi_dung": "Xác định ĐẠI VẬN từ Hào Nguyên Đường: 6 năm/hào Âm, 9 năm/hào Dương"},
    {"buoc": 13, "noi_dung": "Xác định TIỂU VẬN / NIÊN VẬN trong mỗi Đại Vận → quẻ từng năm"},
    {"buoc": 14, "noi_dung": "Lời giải quẻ + kết luận chung"},
]


def get_khong_minh_7_cach_summary() -> str:
    """Render Khổng Minh 7 cách dùng cho luận giải."""
    lines = ["## 🎓 KHỔNG MINH 7 cách phối hợp đánh giá người\n"]
    for c in KHONG_MINH_7_CACH:
        lines.append(f"**{c['stt']}. {c['cach']}** → {c['muc_dich']}")
        lines.append(f"   _Hiện đại_: {c['vi_du_hien_dai']}\n")
    lines.append("\n" + KHONG_MINH_PARADIGM_TAM_TUONG)
    return "\n".join(lines)


def get_cum_tu_bieu_tuong_dataset() -> dict:
    """Dataset cụm từ + tục ngữ cho LLM render luận giải hấp dẫn."""
    return {
        "han_viet": CUM_TU_BIEU_TUONG,
        "tuc_ngu_viet": TUC_NGU_VIET_LUAN_GIAI,
    }


def get_phan_loai_nhan_hoc_answer() -> str:
    """Trả lời user khi hỏi 'tại sao hàng triệu người cùng lá số?'."""
    return PHAN_LOAI_NHAN_HOC_PARADIGM["answer_cho_user"]


# ── 5. SỐ MÙA CỤ THỂ Hoàng Tuấn — bổ sung TC6 Mệnh Hợp Cách ─────────────────
# Source: Hoàng Tuấn p33-34. Thuận mùa theo các tháng cụ thể.
SO_MUA_HOANG_TUAN: dict[str, dict] = {
    "xuan_phan": {
        "thang_am": "Dần (1), Mão (2), Thìn (3)",
        "duong_thuan": (25, 35),
        "am_thuan": (30, 34),
        "ngay_diem": "Xuân Phân ~21-22/3 dương — ngày đêm bằng nhau",
    },
    "ha_chi": {
        "thang_am": "Tỵ (4), Ngọ (5), Mùi (6)",
        "duong_thuan": (35, 55),
        "am_thuan": (27, 30),
        "ngay_diem": "Hạ Chí ~21-22/6 dương — ngày dài nhất Bắc bán cầu",
    },
    "thu_phan": {
        "thang_am": "Thân (7), Dậu (8), Tuất (9)",
        "duong_thuan": (25, 29),
        "am_thuan": (30, 40),
        "ngay_diem": "Thu Phân ~23-24/9 dương — ngày đêm bằng nhau",
    },
    "dong_chi": {
        "thang_am": "Hợi (10), Tý (11), Sửu (12)",
        "duong_thuan": (22, 25),
        "am_thuan": (30, 60),
        "ngay_diem": "Đông Chí ~22-23/12 dương — đêm dài nhất Bắc bán cầu",
    },
}


# ── 6. PARADIGM "VĨ NHÂN NGHỊCH SỐ" — Hoàng Tuấn cảnh báo ───────────────────
PARADIGM_VI_NHAN_NGHICH_SO: dict[str, str] = {
    "main": (
        "Thời xưa quan niệm SỐ TRUNG HÒA là tốt nhất — người cân bằng tinh thần thể chất, "
        "hòa nhã, dễ mến, không hết lòng giúp ai. NHƯNG nhiều VĨ NHÂN trong văn học nghệ thuật + "
        "khoa học tự nhiên + chính trị xã hội KHÔNG bình thường về tâm lý."
    ),
    "vi_du": (
        "Hemingway (nhà văn Mỹ), Van Gogh (họa sĩ), Beethoven (nhạc), Lobachevsky (toán học), "
        "Stalin, Mao Trạch Đông... — đều là NGHỊCH SỐ mà lỗi lạc."
    ),
    "ket_luan": (
        "**NGHỊCH SỐ chưa chắc xấu. HỢP SỐ chưa chắc tốt.** Phải kết hợp nhiều yếu tố. "
        "→ Cross-link Iron Rule #4+6: KHÔNG predict tĩnh dựa trên 1 yếu tố."
    ),
    "ap_dung_founder": (
        "Lá số anh: Dương 26 (gần Số Cơ Bản 25) + Âm 40 (vượt 30 = 10 đơn vị) — "
        "NGHỊCH mùa Hạ (sinh 5/6 → giữa Xuân Phân-Hạ Chí). Nhưng Dương 26 chỉ hơn 25 chút, "
        "Âm 40 cũng KHÔNG quá xa 30 → 'TRUNG HÒA NGHIÊNG VỀ TỐT'. "
        "Engine TC6 hiện trả 'nghịch mùa' (hơi cứng) — phải mềm hóa: 'TRUNG HÒA dù nghịch nhẹ'."
    ),
}


# ── 7. "ĐỨC NĂNG THẮNG SỐ" — câu cốt yếu nhất Hoàng Tuấn ────────────────────
DUC_NANG_THANG_SO: str = (
    "**Đức năng thắng số** — câu cổ nhân, Hoàng Tuấn trích p37:\n\n"
    "'Số Hà Lạc chỉ là môn XÁC SUẤT CỔ, dùng để dự báo những KHẢ NĂNG có thể xảy ra. "
    "Nó KHÔNG THỂ trả lời những sự việc cụ thể của từng người trong tương lai. "
    "Điều đó PHẢI DO CHÍNH ĐƯƠNG SỰ căn cứ vào những khả năng đã được dự báo "
    "ĐỂ TỰ TRẢ LỜI.'\n\n"
    "Cốt: Số CHỈ HƯỚNG. ĐỨC + TÀI + Ý CHÍ + THỜI CƠ làm thay đổi số. "
    "→ Iron Rule #4+6 paradigm CỰC ĐẮT (xác nhận nguồn thứ 4 sau Khang Tiết, Trình Di, PBC)."
)


# ── 8. SỐ CƠ BẢN 25/30 — paradigm "trả nợ Tạo Hóa" ──────────────────────────
SO_CO_BAN_PARADIGM: str = (
    "**Số CƠ BẢN của Tạo Hóa** = Dương 25 (1+3+5+7+9) + Âm 30 (2+4+6+8+10) = 55 (tổng 10 số Hà Đồ).\n\n"
    "Người sinh ra mang số CỦA TẠO HÓA. Khi tính quẻ Hà Lạc — phải trừ 25/30 (như TRẢ NỢ Tạo Hóa) "
    "→ số còn lại là 'Số Gốc của mình'.\n\n"
    "**Exception**: nếu Dương ≤ 25 hoặc Âm ≤ 30 → KHÔNG trừ (Tạo Hóa chưa ban đủ thì không phải trả).\n\n"
    "→ Đây là quy tắc số học cốt yếu Xuân Cang + Hoàng Tuấn ĐỒNG nói. Engine `number_pools.py` "
    "của em đã wire đúng."
)


def get_so_mua_detail() -> dict:
    """Số mùa cụ thể Hoàng Tuấn — bổ sung TC6 Mệnh Hợp Cách."""
    return SO_MUA_HOANG_TUAN


def get_vi_nhan_nghich_so_summary() -> str:
    """Paradigm 'vĩ nhân nghịch số' — answer khi user lo Mệnh Hợp Cách thấp."""
    return "\n\n".join(f"**{k}**: {v}" for k, v in PARADIGM_VI_NHAN_NGHICH_SO.items())
