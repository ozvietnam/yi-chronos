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
