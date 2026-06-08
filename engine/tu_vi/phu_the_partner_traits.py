"""Đặc điểm BẠN ĐỜI (vợ/chồng) qua sao chính diệu cung Phu Thê.

Kết tinh từ 32 vòng thâm nhuần Trung Châu Tử Vi Đẩu Số Q2 — Vương Đình Chỉ.
Section §5.3 (Cung Phu Thê) + §4.x (60 tinh hệ tại Phu Thê).

Output: build_partner_traits(la_so, gender) → list[dict]
  Mỗi item: {
    "tinh_he": "Tử-Tham",
    "category": "tính_cách" | "ngoại_hình" | "sự_nghiệp" | "quan_hệ",
    "trait": str,
    "warning": Optional[str],
    "source": "Trung Châu Q2 §5.3.1 p569",
  }

Paradigm gender-aware: nam mệnh xem vợ; nữ mệnh xem chồng.
"""
from __future__ import annotations
from typing import Any

from .chiem_phu_the import _find_palace, _stars_at_branch_idx


# ════════════════════════════════════════════════════════════════
# REGISTRY — đặc điểm bạn đời qua sao chính diệu Phu Thê
# Format: key = (sao1, sao2 or None, branch_idx or None or "X")
# value = list of trait dicts
# ════════════════════════════════════════════════════════════════

# Branch index: 0=Tý, 1=Sửu, 2=Dần, 3=Mão, 4=Thìn, 5=Tỵ,
#               6=Ngọ, 7=Mùi, 8=Thân, 9=Dậu, 10=Tuất, 11=Hợi

# ─── TỬ VI tại Phu Thê ────────────────────────────────────────
TU_VI_TRAITS = {
    # Tử Vi độc tọa Tý/Ngọ
    "Tử Vi_X_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời có khí chất 'Đế tinh' — địa vị cao, tự tin, tính ĐỘC ĐOÁN",
            "source": "Trung Châu Q2 §5.3.1 p568",
        },
        {
            "category": "quan_hệ",
            "trait": "CÓ KHUYNH HƯỚNG CHI PHỐI mệnh tạo — về tinh thần hoặc tiền bạc",
            "warning": "Nếu kết cấu 'tại dã cô quân' hoặc 'vô đạo' → bạn đời tính BẠO NGƯỢC",
            "source": "Trung Châu Q2 §5.3.1 p568",
        },
        {
            "category": "sự_nghiệp",
            "trait": "Nam mệnh: VỢ NÊN CÓ SỰ NGHIỆP RIÊNG. Nếu ở nhà nhiều → 'không chế chồng' (tài lãnh đạo phát huy vào quan hệ gia đình)",
            "gender": "nam",
            "source": "Trung Châu Q2 p571",
        },
        {
            "category": "tuổi_tác",
            "trait": "Nữ mệnh 'tại dã cô quân/vô đạo' → cần KẾT HÔN MUỘN sau 30 tuổi, kết hôn sớm dễ trắc trở",
            "gender": "nữ",
            "source": "Trung Châu Q2 p572",
        },
    ],
    # Tử-Phá Sửu/Mùi
    "Tử Vi+Phá Quân_1_7": [
        {
            "category": "quan_hệ",
            "trait": "Trước hôn nhân CÓ SÓNG GIÓ, TRẮC TRỞ; nếu vốn không ổn định → dễ LY DỊ",
            "warning": "Gặp 'sao lẻ' phụ-tá → thường có NGƯỜI THỨ BA xen vào",
            "source": "Trung Châu Q2 §5.3.1 p569",
        },
        {
            "category": "sự_nghiệp",
            "trait": "Vợ chồng cùng sáng lập sự nghiệp tay trắng làm nên (nếu 'bách quan triều củng')",
            "source": "Trung Châu Q2 p571",
        },
    ],
    # Tử-Phủ Dần/Thân
    "Tử Vi+Thiên Phủ_2_8": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời ổn định, có chí tiến thủ",
            "source": "Trung Châu Q2 §5.3.1 p569",
        },
        {
            "category": "tuổi_tác",
            "trait": "Có Thiên Thọ đồng độ — nam nên lấy vợ NHỎ TUỔI, nữ nên lấy chồng LỚN TUỔI",
            "source": "Trung Châu Q2 p569",
        },
        {
            "category": "quan_hệ",
            "trait": "Lộc Tồn đồng → bạn đời ÍCH KỶ, có khuynh hướng chi phối",
            "warning": "Không có cát phụ tá → dễ sinh ngoại tình tại lưu niên Liêm/Tướng/Đồng/Cơ Phu Thê",
            "source": "Trung Châu Q2 p569-570",
        },
    ],
    # Tử-Tham Mão/Dậu
    "Tử Vi+Tham Lang_3_9": [
        {
            "category": "tính_cách",
            "trait": "Tinh hệ THUẦN DỤC VỌNG. Phân biệt 2 loại: VẬT CHẤT (chí tiến thủ) vs DỤC TÌNH (dễ ngoại tình)",
            "source": "Trung Châu Q2 §5.3.1 p569",
        },
        {
            "category": "sự_nghiệp",
            "trait": "Có cát tinh → vợ chồng cùng sáng nghiệp, NHƯNG VỢ/CHỒNG LÀ NHÂN VẬT CHÍNH (chủ sở hữu / đứng tên pháp lý)",
            "source": "Trung Châu Q2 p569",
        },
        {
            "category": "tinh_thần",
            "trait": "Bạn đời có khuynh hướng THẦN BÍ TÔN GIÁO (Tham Lang sinh hoạt tinh thần)",
            "source": "Trung Châu Q2 p531",
        },
        {
            "category": "quan_hệ",
            "warning": "Liêm Trinh Hóa Kỵ hội → bạn đời THÔNG MINH NHƯNG DỄ THẤT CHÍ, ưa cảm giác kích thích",
            "trait": "Liêm Trinh Hóa Lộc hội → bạn đời KHÔNG LO LẮNG CHO GIA ĐÌNH (chỉ lo công việc)",
            "source": "Trung Châu Q2 p569",
        },
    ],
    # Tử-Tướng Thìn/Tuất
    "Tử Vi+Thiên Tướng_4_10": [
        {
            "category": "tuổi_tác",
            "trait": "Nam nên lấy vợ NHỎ TUỔI hơn (có thể đến 12 tuổi); nữ nên lấy chồng LỚN TUỔI 8-12 tuổi",
            "warning": "Nếu 'vô tình' → vợ chồng cần CHÊNH LỆCH TUỔI TÁC nhiều mới khỏi sinh ly",
            "source": "Trung Châu Q2 §5.3.1 p570",
        },
        {
            "category": "lịch_sử",
            "trait": "Nên lấy NGƯỜI ĐÃ TỪNG KẾT HÔN (tái hôn / li dị / góa) — gặp 'sao lẻ' phụ-tá càng đúng",
            "source": "Trung Châu Q2 p570",
        },
        {
            "category": "sức_khỏe",
            "warning": "'Vô tình' + sát tinh xung khởi → đề phòng BẠN ĐỜI ĐỘT NHIÊN BỆNH",
            "source": "Trung Châu Q2 p570",
        },
    ],
    # Tử-Thất Tỵ/Hợi
    "Tử Vi+Thất Sát_5_11": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời LỘNG QUYỀN, mạnh mẽ",
            "source": "Trung Châu Q2 §5.3.1 p571",
        },
        {
            "category": "sự_nghiệp",
            "trait": "Phụ-tá cát → bạn đời có SỰ NGHIỆP LỚN — nhưng vợ chồng GẶP NHAU ÍT, XA NHAU NHIỀU (hoặc ở chung nhưng quan hệ xa cách)",
            "source": "Trung Châu Q2 p571",
        },
        {
            "category": "tài_chính",
            "trait": "Hỏa-Linh Tham hội → bạn đời ĐỘT NHIÊN PHÁT ĐẠT",
            "warning": "Đào hoa hội → bạn đời ĐỘT NHIÊN THAY LÒNG ĐỔI DẠ",
            "source": "Trung Châu Q2 p571",
        },
        {
            "category": "tuổi_tác",
            "trait": "Nên KẾT HÔN MUỘN",
            "source": "Trung Châu Q2 p571",
        },
    ],
}

# ─── THIÊN CƠ tại Phu Thê ─────────────────────────────────────
THIEN_CO_TRAITS = {
    "Thiên Cơ_X_single": [
        {
            "category": "quan_hệ",
            "trait": "Về cơ bản BẤT LỢI — vợ chồng bằng mặt mà không bằng lòng",
            "warning": "Cơ Hóa Kỵ / Cự Hóa Kỵ → tính cách KHÔNG HỢP, dễ thay lòng đổi dạ",
            "source": "Trung Châu Q2 §5.3.2 p572",
        },
        {
            "category": "tuổi_tác",
            "trait": "Vợ chồng nên CHÊNH LỆCH TUỔI TÁC, kết hôn muộn",
            "source": "Trung Châu Q2 p572",
        },
    ],
    "Thiên Cơ+Thái Âm_2_8": [
        {
            "category": "ngoại_hình",
            "trait": "Nam mệnh: VỢ XINH ĐẸP, giỏi nội trợ",
            "gender": "nam",
            "source": "Trung Châu Q2 §5.3.2 p573",
        },
        {
            "category": "tính_cách",
            "trait": "Nữ mệnh: cần ĐỀ PHÒNG dễ bị người khác giới để ý",
            "gender": "nữ",
            "source": "Trung Châu Q2 p573",
        },
        {
            "category": "tâm_lý",
            "warning": "Đồng Hóa Kỵ + Không-Kiếp/Hư/Hao → bạn đời TÂM CHÍ BẠC NHƯỢC, quá mẫn cảm → dễ sóng gió hôn nhân",
            "source": "Trung Châu Q2 p573",
        },
    ],
    "Thiên Cơ+Cự Môn_3_9": [
        {
            "category": "quan_hệ",
            "trait": "Cần sao Lộc mới sống đến bạc đầu. Sau kết hôn liền có sóng gió, trải qua mới sống ấm",
            "warning": "Cơ Hóa Kỵ → DỄ YÊU NGƯỜI ĐÃ CÓ GIA ĐÌNH",
            "source": "Trung Châu Q2 §5.3.2 p573",
        },
        {
            "category": "lịch_sử",
            "warning": "Cự Hóa Kỵ → có NỖI KHỔ ĐAU THẦM KÍN về tình cảm. Gặp sát → 2 LẦN KẾT HÔN",
            "source": "Trung Châu Q2 p574",
        },
    ],
    "Thiên Cơ+Thiên Lương_4_10": [
        {
            "category": "tuổi_tác",
            "trait": "KẾT HÔN MUỘN, hoặc trước hôn nhân có sóng gió trong tình yêu",
            "source": "Trung Châu Q2 §5.3.2 p574",
        },
        {
            "category": "lịch_sử",
            "trait": "Trước hôn nhân CÓ MỘT LẦN LÌA BIỆT, gặp lại nhau mới sống đến bạc đầu",
            "source": "Trung Châu Q2 p574",
        },
    ],
}

# ─── THÁI DƯƠNG tại Phu Thê ──────────────────────────────────
THAI_DUONG_TRAITS = {
    "Thái Dương_0_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời có tính SOI BÓI BỚI MÓC (đặc biệt khi gặp Hỏa-Linh)",
            "source": "Trung Châu Q2 §5.3.3 p575",
        },
        {
            "category": "quan_hệ",
            "warning": "Thái Dương Hóa Kỵ Tý + Địa Không/Kiếp → NỮ mệnh SỚM LÀM QUẢ PHỤ; nam SAU 30 tuổi dễ thay lòng",
            "gender_specific": True,
            "source": "Trung Châu Q2 p575-576",
        },
    ],
    "Thái Dương_6_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời GIỎI GIANG, CÓ TRÁCH NHIỆM",
            "source": "Trung Châu Q2 §5.3.3 p576",
        },
        {
            "category": "lịch_sử",
            "trait": "Sát tinh đồng → ngày đêm BÔN BA, BẬN RỘN BÊN NGOÀI, ít hưởng vui gia đình",
            "source": "Trung Châu Q2 p576",
        },
        {
            "category": "sự_nghiệp",
            "trait": "Nam mệnh thời cổ → nhờ GIA ĐÌNH VỢ mà được quý; thời hiện đại → vợ có sự nghiệp tốt",
            "gender": "nam",
            "source": "Trung Châu Q2 p576",
        },
    ],
    "Thái Dương+Thái Âm_1_7": [
        {
            "category": "quan_hệ",
            "trait": "Nam mệnh cát + sinh đêm → VỢ HIẾP ĐÁP CHỒNG (đặc biệt cung Sửu)",
            "warning": "Sát-kỵ-hình → VÌ VỢ PHÁ GIA (cung Sửu, sinh đêm nặng nhất)",
            "gender": "nam",
            "source": "Trung Châu Q2 §5.3.3 p576",
        },
        {
            "category": "tài_chính",
            "trait": "Âm Hóa Lộc → ĐƯỢC NHÀ VỢ TRỢ LỰC, vợ giỏi nội trợ",
            "gender": "nam",
            "source": "Trung Châu Q2 p577",
        },
        {
            "category": "tính_cách",
            "warning": "Nữ + Thái Dương Hóa Kỵ → CHỒNG NHIỀU NẠN TAI BỆNH TẬT, có sát → hình khắc / sinh ly",
            "gender": "nữ",
            "source": "Trung Châu Q2 p577",
        },
    ],
    "Thái Dương+Cự Môn_2_8": [
        {
            "category": "nguồn_gốc",
            "trait": "Hóa Lộc/Quyền → KẾT HÔN VỚI NGƯỜI NGOẠI QUỐC (hoặc người ở phương xa)",
            "source": "Trung Châu Q2 p577",
        },
        {
            "category": "lịch_sử",
            "trait": "Cát hóa + Phúc Đức không cát → nữ rời quê hương lấy chồng theo chồng; nam Ở RỂ",
            "source": "Trung Châu Q2 p577",
        },
    ],
    "Thái Dương+Thiên Lương_3_9": [
        {
            "category": "tuổi_tác",
            "trait": "Vợ chồng tuổi tác CHÊNH LỆCH; có Thiên Thọ chênh càng nhiều. Vợ có thể LỚN HƠN CHỒNG",
            "source": "Trung Châu Q2 §5.3.3 p577",
        },
        {
            "category": "lịch_sử",
            "trait": "Sóng gió trắc trở trước hôn nhân, hoặc BẠN CŨ GẶP LẠI NHAU rồi lấy nhau",
            "source": "Trung Châu Q2 p578",
        },
    ],
    # Thái Dương Thìn — "Nhật Nguyệt toàn bích" (nếu Âm tại Tuất)
    "Thái Dương_4_single": [
        {
            "category": "tính_cách",
            "trait": "Thái Dương Thìn = mặt trời SẮP MỌC — bạn đời CÓ Ý CHÍ vươn lên, hướng ngoại, dương khí đầy. Cách 'Nhật Nguyệt toàn bích' (Âm Tuất đối) = thượng cách, phú quý nếu có cát hóa",
            "source": "Trung Châu Q2 §5.1.3 p512-513",
        },
        {
            "category": "quan_hệ",
            "warning": "Rất kỵ Đà La / Hỏa Tinh đồng / Kình + Linh đồng → vợ chồng KHÔNG sống đến bạc đầu",
            "source": "Trung Châu Q2 p513",
        },
        {
            "category": "lịch_sử",
            "trait": "Hóa Lộc + đại hạn 'Tử Vi-Phá Quân' → thường thành thân KHÔNG có nghi lễ chính thức",
            "source": "Trung Châu Q2 p578",
        },
    ],
    # ⭐ Thái Dương Tuất — "Nhật Nguyệt thất huy" (LẠC HÃM) — paradigm cốt
    "Thái Dương_10_single": [
        {
            "category": "tính_cách",
            "trait": "Thái Dương Tuất = mặt trời ĐÃ LẶN — bạn đời 'Nhật Nguyệt thất huy' (mất sáng) khi Âm tại Thìn. Cuộc đời BIẾN THIÊN BẤT ĐỊNH (sách Trung Châu Q2 §5.1.3 p512)",
            "source": "Trung Châu Q2 §5.1.3 p512-513",
        },
        {
            "category": "lịch_sử",
            "trait": "Bạn đời cuộc đời nhiều THĂNG TRẦM, biến động — phải tự lập, có thể trải qua nhiều thay đổi nghề nghiệp / địa lý",
            "source": "Trung Châu Q2 p512",
        },
        {
            "category": "quan_hệ",
            "warning": "Thái Dương Tuất + Cự Hóa Kỵ → bất lợi nặng. Hóa Lộc KHÔNG chủ kết hôn người ngoại quốc; nhưng nữ mệnh → được người ngoại quốc theo đuổi",
            "source": "Trung Châu Q2 p578",
        },
        {
            "category": "tinh_thần",
            "trait": "Mặc dù lạc hãm, bạn đời vẫn giữ KHÍ DƯƠNG (tự tin, hướng tới mục tiêu) — chỉ ánh sáng không rực rỡ ra ngoài",
            "source": "Trung Châu Q2 §5.1.3",
        },
        {
            "category": "sự_nghiệp",
            "warning": "Nhật Nguyệt thất huy → sự nghiệp bạn đời gặp NHIỀU GIAI ĐOẠN; có lúc sáng có lúc tối. Cần Văn Xương/Khúc + Lộc để bù",
            "source": "Trung Châu Q2 p513",
        },
        {
            "category": "tuổi_tác",
            "trait": "Vợ chồng nên CHÊNH LỆCH TUỔI để bù paradigm lạc hãm",
            "source": "Trung Châu Q2",
        },
    ],
}

# ─── VŨ KHÚC tại Phu Thê ─────────────────────────────────────
VU_KHUC_TRAITS = {
    "Vũ Khúc+Thiên Phủ_0_6": [
        {
            "category": "sự_nghiệp",
            "trait": "Vũ Hóa Lộc + nam → VỢ CÓ NĂNG LỰC LÀM VIỆC GIỎI HƠN CHỒNG",
            "gender": "nam",
            "source": "Trung Châu Q2 §5.3.4 p580",
        },
        {
            "category": "quan_hệ",
            "warning": "Thất Sát đối + Lộc Tồn đồng → tình hình 'VỢ ĐOẠT QUYỀN CHỒNG' càng nghiêm trọng. Nam có Hỏa-Linh Mệnh → Ở RỂ",
            "gender": "nam",
            "source": "Trung Châu Q2 p580",
        },
        {
            "category": "tính_cách",
            "warning": "Vũ Hóa Kỵ + nữ → HÔN NHÂN GIỮA CHỪNG ĐỨT ĐOẠN (chồng mắc bệnh hoặc thay lòng)",
            "gender": "nữ",
            "source": "Trung Châu Q2 p580",
        },
        {
            "category": "lịch_sử",
            "warning": "Sao lẻ phụ-tá → MẠNG TÁI HÔN. Đào hoa hội → sau kết hôn vẫn bị người đã có gia đình theo đuổi (nữ nặng hơn)",
            "source": "Trung Châu Q2 p580",
        },
    ],
    "Vũ Khúc+Tham Lang_1_7": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời KEO KIỆT, BỦN XỈN, xem nặng tiền bạc, kiểm soát tiền bạc của mệnh tạo",
            "warning": "Lộc Tồn/Hóa Lộc hội → KHÔNG đúng — chồng giàu sung túc / vợ tự kinh doanh",
            "source": "Trung Châu Q2 §5.3.4 p580",
        },
        {
            "category": "quan_hệ",
            "warning": "Hỏa-Linh đồng → tình cảm vợ chồng TRƯỚC NỒNG ẤM SAU NGUỘI LẠNH. Đào hoa tụ → trước+sau hôn nhân đều rắc rối tình cảm",
            "source": "Trung Châu Q2 p580",
        },
        {
            "category": "lịch_sử",
            "warning": "Hóa Kỵ → vì bạn đời mà PHÁ TÀI. Khoa văn/đào hoa → THAY LÒNG ĐỔI DẠ. Không-Kiếp → KHÔNG có LẠC THÚ KHUÊ PHÒNG / TÁI HÔN",
            "source": "Trung Châu Q2 p580",
        },
    ],
}


# ════════════════════════════════════════════════════════════════
# BUILDER
# ════════════════════════════════════════════════════════════════

# ─── THIÊN ĐỒNG tại Phu Thê (Q2 §5.3.5) ────────────────────────
THIEN_DONG_TRAITS = {
    "Thiên Đồng_X_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời TÌNH CẢM, dễ thân mật. Tính ôn hòa, có khuynh hướng ỦY MỊ nếu Phu Thê có sát tinh",
            "source": "Trung Châu Q2 §5.3.5",
        },
        {
            "category": "quan_hệ",
            "trait": "Đồng Hóa Lộc + Văn Xương/Khúc → bạn đời 'khoát đạt' (thông minh, có tài)",
            "warning": "Đồng Hóa Kỵ + Hỏa-Linh → 'đoản chí' (việc sắp thành lại hỏng, tâm trạng mất ổn định)",
            "source": "Trung Châu Q2 §5.1.5",
        },
    ],
    "Thiên Đồng+Thái Âm_0_6": [
        {
            "category": "ngoại_hình",
            "trait": "Nam: VỢ XINH ĐẸP, dịu dàng, tình cảm sâu",
            "gender": "nam",
            "source": "Trung Châu Q2 §5.3.5",
        },
        {
            "category": "lịch_sử",
            "warning": "Đào hoa hội → trước+sau hôn nhân đều có tình huống rắc rối tình cảm",
            "source": "Trung Châu Q2",
        },
    ],
    "Thiên Đồng+Cự Môn_1_7": [
        {
            "category": "tâm_lý",
            "warning": "Đồng-Cự hội Cự Hóa Kỵ → bạn đời có NỖI ĐAU KHỔ THẦM KÍN nội tâm không thể chia sẻ",
            "source": "Trung Châu Q2 §5.1.10 p534",
        },
    ],
    "Thiên Đồng+Thiên Lương_4_10": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời ÔN HÒA, có khí nho nhã. Đồng = phúc + Lương = ấm = phối hợp dịu dàng",
            "source": "Trung Châu Q2 §5.3.5",
        },
    ],
}

# ─── LIÊM TRINH tại Phu Thê ────────────────────────────────────
LIEM_TRINH_TRAITS = {
    "Liêm Trinh_X_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời ĐÀO HOA + LÝ TRÍ. Đặc biệt nặng về tình cảm tinh thần (ghi lòng tạc dạ)",
            "source": "Trung Châu Q2 §5.1.6 p521",
        },
        {
            "category": "quan_hệ",
            "warning": "Liêm Trinh Hóa Kỵ tại Phu Thê → CỰC KỲ BẤT LỢI (tình cảm tổn thương, có thể liên quan máu)",
            "source": "Trung Châu Q2 §5.1.6 p521",
        },
    ],
    "Liêm Trinh+Thiên Tướng_0_6": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời khí HÒA HOÃN, thông minh mẫn tiệp, có tính phục vụ",
            "source": "Trung Châu Q2 p522",
        },
        {
            "category": "sự_nghiệp",
            "trait": "Liêm Hóa Lộc / Phá Hóa Lộc đối → bạn đời phú quý nhưng VỊ TRÍ PHỤ TÁ / phó",
            "source": "Trung Châu Q2 p522",
        },
        {
            "category": "tâm_lý",
            "warning": "Hỏa-Linh đồng → bạn đời gặp TRẮC TRỞ NGHIÊM TRỌNG, có khuynh hướng tự sát",
            "source": "Trung Châu Q2 p522",
        },
    ],
    "Liêm Trinh+Phá Quân_3_9": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời mạnh mẽ, khí khái — nhưng cuộc đời nhiều biến động",
            "source": "Trung Châu Q2 §5.1.6 p524",
        },
        {
            "category": "lịch_sử",
            "warning": "Hỏa-Linh đồng → bạn đời SUY SỤP NHANH; sát nặng + Thiên Hình → có thể phẫu thuật",
            "source": "Trung Châu Q2 p524",
        },
    ],
    "Liêm Trinh+Thiên Phủ_4_10": [
        {
            "category": "tính_cách",
            "trait": "Khí HÒA HOÃN, ổn định",
            "source": "Trung Châu Q2 p524",
        },
        {
            "category": "lịch_sử",
            "warning": "Kết hôn sớm bất lợi — dễ 'ngó đứt mà tơ chưa lìa' (cảm xúc kéo dài) / hữu danh vô thực",
            "source": "Trung Châu Q2 p524",
        },
    ],
    "Liêm Trinh+Thất Sát_1_7": [
        {
            "category": "tính_cách",
            "trait": "Cấu hình MÙI (chỉ Mùi mới thành cách 'Hùng Tú Kiển Nguyên') → bạn đời trải qua gian khổ thành đại nghiệp",
            "source": "Trung Châu Q2 p358",
        },
        {
            "category": "quan_hệ",
            "warning": "Liêm Hóa Kỵ + sát-hình → chủ về 'chết ở xứ người'; có khuynh hướng tự sát nếu Hỏa-Linh + Vũ/Văn Hóa Kỵ",
            "source": "Trung Châu Q2 §5.1.6 p523",
        },
    ],
    "Liêm Trinh+Tham Lang_5_11": [
        {
            "category": "tính_cách",
            "trait": "Khí chất cao thượng, phong lưu nho nhã — nếu phụ-tá đầy đủ → làm chính giới/quân đội",
            "source": "Trung Châu Q2 §5.1.6 p525",
        },
        {
            "category": "lịch_sử",
            "warning": "Hỏa-Linh đồng → BẠO PHÁT BẠO BẠI cực kỳ nghiêm trọng. Đào hoa → 'ngó đứt mà tơ chưa lìa'",
            "source": "Trung Châu Q2 p525",
        },
    ],
}

# ─── THIÊN PHỦ tại Phu Thê ─────────────────────────────────────
THIEN_PHU_TRAITS = {
    "Thiên Phủ_X_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời CẨN THẬN, có nguyên tắc. Phân biệt 'TƯỜNG HÒA' (thông minh + có thành tích vô tình) vs 'QUYỀN BIẾN' (nhiều thay đổi, không được gì)",
            "source": "Trung Châu Q2 §4.6.3 p465",
        },
        {
            "category": "tài_chính",
            "trait": "Thiên Phủ = kho tiền — bạn đời GIỎI GIỮ TIỀN, chưa chắc giỏi kiếm. Cần xem Phủ là 'kho đầy ắp' / 'kho lộ' / 'kho trống'",
            "source": "Trung Châu Q2 §5.1.7 p525",
        },
        {
            "category": "quan_hệ",
            "warning": "'Kho lộ' / 'kho trống' → bạn đời TÂM CHÍ BẠC NHƯỢC, ích kỷ, lo nghĩ vô vị",
            "source": "Trung Châu Q2 p526",
        },
    ],
}

# ─── THÁI ÂM tại Phu Thê ────────────────────────────────────────
THAI_AM_TRAITS = {
    "Thái Âm_X_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời HƯỚNG NỘI, tình cảm phong phú. Miếu vượng = đẹp; lạc hãm = ẩn ức",
            "source": "Trung Châu Q2 §5.1.8 p528",
        },
        {
            "category": "tài_chính",
            "trait": "Thái Âm = sao tiền tài (kế hoạch). Bạn đời giỏi quản lý tài chính",
            "source": "Trung Châu Q2 §5.1.8",
        },
        {
            "category": "tâm_lý",
            "warning": "Đà-Linh-Kỵ-Âm Sát-Không-Kiếp-Hình tụ → có thể TỰ KỶ, mặc cảm",
            "source": "Trung Châu Q2 p529",
        },
        {
            "category": "ngoại_hình",
            "trait": "Nữ mệnh: chồng tinh tế, có nét nữ tính (Âm chỉ chồng khi nữ)",
            "gender": "nữ",
            "source": "Trung Châu Q2 §5.1.8",
        },
    ],
}

# ─── THAM LANG tại Phu Thê ─────────────────────────────────────
THAM_LANG_TRAITS = {
    "Tham Lang_X_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời VẬT DỤC + SẮC DỤC. Phân biệt qua Hóa Lộc (vật chất) vs đào hoa (sắc tình)",
            "source": "Trung Châu Q2 §5.1.9 p531",
        },
        {
            "category": "tinh_thần",
            "trait": "Thích sự vật THẦN BÍ TÔN GIÁO, có thể tu luyện / sắc thái tâm linh",
            "source": "Trung Châu Q2 p531",
        },
        {
            "category": "quan_hệ",
            "warning": "Cách 'Phiếm Thủy Đào Hoa' (Tý + Kình) / 'Phong Lưu Thái Trượng' (Dần + Đà) → bạn đời VÌ SẮC THẤT BẠI",
            "source": "Trung Châu Q2 p532",
        },
        {
            "category": "tài_chính",
            "trait": "Hỏa-Linh đồng → cách 'Hỏa Tham/Linh Tham' = bạn đời PHÁT ĐỘT NGỘT (kiếm được tiền bất ngờ)",
            "source": "Trung Châu Q2 p531",
        },
    ],
}

# ─── CỰ MÔN tại Phu Thê ────────────────────────────────────────
CU_MON_TRAITS = {
    "Cự Môn_X_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời CHỦ VỀ MIỆNG LƯỠI — giỏi nói, ăn nói có tài. Cự Môn = 'ám tinh' che ánh sáng → có thể có nét u tối, kín đáo",
            "source": "Trung Châu Q2 §5.1.10 p533",
        },
        {
            "category": "sự_nghiệp",
            "trait": "Hợp với nghề DÙNG TÀI ĂN NÓI: giáo viên, luật sư, kinh doanh, ngoại giao, MC",
            "source": "Trung Châu Q2 p813",
        },
        {
            "category": "quan_hệ",
            "warning": "Cự Hóa Kỵ → bạn đời mang nhiều THỊ PHI, oán trách. Có thể tính cách KÍN, GIẤU CHUYỆN",
            "source": "Trung Châu Q2 §5.1.10",
        },
        {
            "category": "lịch_sử",
            "trait": "Hóa Lộc + người ngoại quốc → KẾT HÔN với người ở phương xa / nước ngoài",
            "source": "Trung Châu Q2 p812",
        },
    ],
}

# ─── THIÊN TƯỚNG tại Phu Thê ───────────────────────────────────
THIEN_TUONG_TRAITS = {
    "Thiên Tướng_X_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời CÔNG MINH, trợ giúp tha nhân. 'Gặp thiện thì thiện, gặp ác thì ác' — thấm theo môi trường, không có bản chất cố định",
            "source": "Trung Châu Q2 §5.1.11 p536",
        },
        {
            "category": "quan_hệ",
            "trait": "Cần CÁT TINH HỖ TRỢ vì Tướng kỵ cô độc. 'Tài ấm giáp ấn' → bạn đời được phúc; 'Hình kỵ giáp ấn' → bị áp lực",
            "source": "Trung Châu Q2 p536",
        },
        {
            "category": "sự_nghiệp",
            "trait": "Bạn đời thường ở VỊ TRÍ PHÓ / cố vấn / thư ký — danh nghĩa không bằng thực tế",
            "source": "Trung Châu Q2 §5.9.11",
        },
    ],
}

# ─── THIÊN LƯƠNG tại Phu Thê ───────────────────────────────────
THIEN_LUONG_TRAITS = {
    "Thiên Lương_X_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời TRƯỞNG THƯỢNG, có khí nguyên tắc kỷ luật. 'Ấm tinh' che chở TINH THẦN, không vật chất",
            "source": "Trung Châu Q2 §5.1.12 p539",
        },
        {
            "category": "tuổi_tác",
            "trait": "Bạn đời nên NHỎ HƠN mệnh tạo 5-10 tuổi để cân bằng",
            "source": "Trung Châu Q2 §5.1.12",
        },
        {
            "category": "quan_hệ",
            "warning": "Lương Hóa Lộc → mang thị phi; Lương Hóa Quyền → khuynh hướng LỘNG QUYỀN",
            "source": "Trung Châu Q2 p540",
        },
        {
            "category": "lịch_sử",
            "trait": "Phải gặp NẠN TRƯỚC rồi mới hóa giải (tiêu tai giải ách) — bạn đời trải qua khó khăn",
            "source": "Trung Châu Q2 p539",
        },
    ],
}

# ─── THẤT SÁT tại Phu Thê ──────────────────────────────────────
THAT_SAT_TRAITS = {
    "Thất Sát_X_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời BẠO LIỆT, mạnh mẽ — có thời kỳ gian khổ trong đời. Khí cương cường",
            "source": "Trung Châu Q2 §5.1.13 p543",
        },
        {
            "category": "tuổi_tác",
            "trait": "Vợ chồng thường gặp SÓNG GIÓ — KẾT HÔN MUỘN tốt hơn",
            "source": "Trung Châu Q2 §5.1.13",
        },
        {
            "category": "sức_khỏe",
            "warning": "Kình-Linh + Thiên Hình + Âm Sát-Hư-Đại Hao → có thể PHẠM PHÁP HÌNH SỰ",
            "source": "Trung Châu Q2 p544",
        },
    ],
}

# ─── PHÁ QUÂN tại Phu Thê ──────────────────────────────────────
PHA_QUAN_TRAITS = {
    "Phá Quân_X_single": [
        {
            "category": "tính_cách",
            "trait": "Bạn đời ƯA THAY ĐỔI, năng động — cuộc đời nhiều biến động",
            "source": "Trung Châu Q2 §5.1.14",
        },
        {
            "category": "lịch_sử",
            "warning": "Phu Thê dễ TÁI HÔN — cần Hóa Lộc/Quyền hỗ trợ. Phá Quân ở Hợi/Tý/Sửu + Văn Khúc → 'tàn tật rời xa quê hương' (cách cổ)",
            "source": "Trung Châu Q2 §5.1.14 p547",
        },
        {
            "category": "sự_nghiệp",
            "trait": "Có sao Lộc → tiêu trừ khuyết điểm hao tổn, tăng sáng tạo",
            "source": "Trung Châu Q2 p547",
        },
    ],
}


ALL_REGISTRIES = [
    TU_VI_TRAITS,
    THIEN_CO_TRAITS,
    THAI_DUONG_TRAITS,
    VU_KHUC_TRAITS,
    THIEN_DONG_TRAITS,
    LIEM_TRINH_TRAITS,
    THIEN_PHU_TRAITS,
    THAI_AM_TRAITS,
    THAM_LANG_TRAITS,
    CU_MON_TRAITS,
    THIEN_TUONG_TRAITS,
    THIEN_LUONG_TRAITS,
    THAT_SAT_TRAITS,
    PHA_QUAN_TRAITS,
]


def _stars_at_named_palace(la_so: dict, palace_name: str) -> dict[str, list[str]]:
    pal = _find_palace(la_so, palace_name)
    if not pal:
        return {"chinh_tinh": []}
    return _stars_at_branch_idx(la_so, pal["branch_index"])


def _palace_branch_idx(la_so: dict, palace_name: str) -> int | None:
    pal = _find_palace(la_so, palace_name)
    return pal["branch_index"] if pal else None


def _gender_norm(gender: str) -> str:
    g = (gender or "nam").lower().strip()
    return "nữ" if g in ("nu", "nữ") else "nam"


def _match_traits_key(key: str, chinh_tinh: list[str], branch_idx: int | None) -> bool:
    """Match key format:
    - "Sao1_idx_single" — sao đơn tại branch idx (X = any)
    - "Sao1+Sao2_idx1_idx2" — sao đôi tại idx1 OR idx2
    - "Sao1+Sao2_idx_idx" — same idx
    """
    parts = key.split("_")
    if "single" in parts:
        # "Sao_idx_single"
        star = parts[0]
        idx_str = parts[1] if len(parts) >= 3 else "X"
        if not any(star in s for s in chinh_tinh):
            return False
        if idx_str == "X":
            return True
        try:
            return branch_idx == int(idx_str)
        except ValueError:
            return False
    # Sao đôi
    star_part = parts[0]  # "Sao1+Sao2"
    if "+" not in star_part:
        return False
    s1, s2 = star_part.split("+", 1)
    if not (any(s1 in c for c in chinh_tinh) and any(s2 in c for c in chinh_tinh)):
        return False
    # Match branch
    idx_strs = parts[1:]
    if not idx_strs:
        return True
    try:
        valid_idxs = {int(x) for x in idx_strs}
    except ValueError:
        return True
    return branch_idx in valid_idxs


def build_partner_traits(la_so: dict, gender: str = "nam") -> dict[str, Any]:
    """Build paradigm "Đặc điểm Bạn Đời" từ sao chính diệu cung Phu Thê.

    Returns:
        {
            "role": "vợ" or "chồng",
            "phu_the_branch": "Mão",
            "phu_the_chinh_tinh": ["Tử Vi", "Tham Lang"],
            "phu_the_phu_tinh": [...],
            "tinh_he": "Tử-Tham",
            "traits": [
                {"category": "tính_cách", "trait": "...", "source": "...", "warning": "..."},
                ...
            ],
            "matched_keys": ["Tử Vi+Tham Lang_3_9", ...],
        }
    """
    gender_n = _gender_norm(gender)
    role = "vợ" if gender_n == "nam" else "chồng"

    pt_stars = _stars_at_named_palace(la_so, "Phu Thê")
    chinh_tinh = pt_stars.get("chinh_tinh", [])
    phu_tinh = pt_stars.get("phu_tinh", [])
    branch_idx = _palace_branch_idx(la_so, "Phu Thê")

    # Tinh hệ label
    tinh_he = "+".join(chinh_tinh) if chinh_tinh else "Vô chính diệu"

    traits = []
    matched_keys = []
    for registry in ALL_REGISTRIES:
        for key, trait_list in registry.items():
            if _match_traits_key(key, chinh_tinh, branch_idx):
                matched_keys.append(key)
                for trait in trait_list:
                    # Filter by gender if specified
                    trait_gender = trait.get("gender")
                    if trait_gender and trait_gender != gender_n:
                        continue
                    # Append a flat copy
                    item = {
                        "category": trait.get("category", "khác"),
                        "trait": trait.get("trait", ""),
                        "source": trait.get("source", "Trung Châu Q2"),
                    }
                    if trait.get("warning"):
                        item["warning"] = trait["warning"]
                    traits.append(item)

    # Branches Vietnamese
    BRANCH_NAMES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
                    "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
    branch_name = BRANCH_NAMES[branch_idx] if branch_idx is not None and 0 <= branch_idx < 12 else "?"

    return {
        "role": role,
        "gender_input": gender_n,
        "phu_the_branch": branch_name,
        "phu_the_branch_idx": branch_idx,
        "phu_the_chinh_tinh": chinh_tinh,
        "phu_the_phu_tinh": phu_tinh,
        "tinh_he": tinh_he,
        "traits": traits,
        "matched_keys": matched_keys,
        "summary": (
            f"{len(traits)} đặc điểm {role} (cấu hình {tinh_he} tại cung {branch_name})"
            if traits
            else f"Chưa có paradigm khớp cho cấu hình {tinh_he} tại {branch_name}"
        ),
        "note": (
            f"Đặc điểm bạn đời ({role} của mệnh tạo) trích từ Trung Châu Tử Vi Đẩu Số Q2 "
            f"(Vương Đình Chỉ) — §5.3 Cung Phu Thê. Paradigm 'đọc đồng dạng' không predict cứng."
        ),
    }
