"""Trung Châu Tử Vi Đẩu Số — paradigm kết tinh từ 32 vòng thâm nhuần Q2 (2026-06-08).

Sau khi đọc xuyên 900 trang Q2 (Vương Đình Chỉ), em chốt 3 IRON RULE
+ 14 paradigm chính tinh × cung trọng yếu vào module này.

Output: build_trung_chau_context(la_so, gender) → str
  Trả về 1 block context để inject vào prompt LLM phê mệnh sâu.
  KHÔNG dump toàn bộ 34 rules — chỉ paradigm CHIẾU CỐT cho lá số cụ thể.

Iron Rules (paradigm CỐT Trung Châu):
  1. DI CUNG HOÁN VỊ — không cố định cung, sao di chuyển + xem phản ứng
  2. XU CÁT TỊ HUNG — hành động hậu thiên TÁC ĐỘNG vận trình (không predict)
  3. HƯ TÂM LÃNH HỘI — không trình bày hết, tự suy ra
"""
from __future__ import annotations
from typing import Any

from .chiem_phu_the import _find_palace, _stars_at_branch_idx


# ════════════════════════════════════════════════════════════════
# IRON RULES CỐT TRUNG CHÂU (luôn inject)
# ════════════════════════════════════════════════════════════════

IRON_RULES_HEADER = """━━━ 🔑 BÍ TRUYỀN TRUNG CHÂU (Vương Đình Chỉ Q2 — paradigm CỐT) ━━━

**3 Iron Rule khi luận giải lá số** (KHÔNG được vi phạm):

1. **DI CUNG HOÁN VỊ** (Q2 p501) — KHÔNG cố định cung Mệnh nguyên cục.
   - Khi đến Đại Vận / Lưu Niên → cung Mệnh anh DI CHUYỂN
   - Phải MANG TÍNH CHẤT sao đã di chuyển + xem PHẢN ỨNG giữa nguyên cục và vận hạn
   - Cách luận đoán SAI: chỉ xem tam phương tứ chính cung Mệnh đại vận → MÁY MÓC
   - Cách ĐÚNG: 12 cung nguyên cục → di chuyển → phản ứng → 3-tier (Mệnh + Đại Vận + Lưu Niên)

2. **XU CÁT TỊ HUNG** (Q2 p461) — HÀNH ĐỘNG HẬU THIÊN TÁC ĐỘNG VÀO VẬN TRÌNH.
   - Mệnh = nguyên cục paradigm (TÍNH CHẤT, không phải định mệnh cứng)
   - Hành động đúng đắn HẬU THIÊN có thể XOAY CHUYỂN cát-hung
   - Tuyệt đối KHÔNG predict tuyệt đối ("anh sẽ giàu", "anh sẽ nghèo")
   - PHẢI dùng: "khoảnh khắc này phản chiếu cấu trúc gì", "tâm anh đang ở vị trí nào"

3. **HƯ TÂM LÃNH HỘI** (Q2 p502) — không thể trình bày hết tổ hợp sao.
   - Tổ sư bảo: lấy "hư tâm" mà LÃNH HỘI, dựa vào nguyên tắc mà SUY RA
   - Đẩu số = đọc đồng dạng, không phải predict tool
   - Khớp Iron Rule #6 project: Tử Vi = quan-sao-trace-tính
"""


# ════════════════════════════════════════════════════════════════
# PARADIGM CỐT cho 14 CHÍNH TINH × CUNG TRỌNG YẾU
# (extract từ §4 60 tinh hệ + §5 cung viên luận)
# ════════════════════════════════════════════════════════════════

# Format: (key_check, paradigm_text)
# key_check: function(la_so) → bool — paradigm có ứng cho lá số không
# paradigm_text: string CỐT từ sách Trung Châu Q2 — inject nếu ứng

CHINH_TINH_TAI_MENH = {
    # Thiên Tướng Mệnh — §4.4.3 + §5.1.11
    "Thiên Tướng_5": """**MỆNH THIÊN TƯỚNG TỴ** (Q2 p347 + p536):
- Thiên Tướng Tỵ/Hợi = ỔN NHẤT 12 cung — kiên nhẫn + sức khai sáng
- Trong 14 chính diệu, CHỈ Thiên Tướng XEM TRỌNG VIỆC GIÁP CUNG
- "GẶP THIỆN THÌ THIỆN, GẶP ÁC THÌ ÁC" — thấm theo môi trường, không có bản chất cố định
- Nếu có "Tài ấm giáp ấn" (Cự Lộc giáp) → cát; "Hình kỵ giáp ấn" (Cự Kỵ giáp) → xấu nhất
- Phải XEM KÈM cung Phụ Mẫu (cấp trên phù trợ) — Thiên Tướng CẦN người phù trợ""",

    "Thiên Tướng_11": """**MỆNH THIÊN TƯỚNG HỢI** (Q2 p347 + p538):
- Đối Vũ-Phá Tỵ — nếu Vũ Hóa Kỵ → Kình-Đà giáp = ĐẠI BẤT LỢI (việc sắp thành lại hỏng)
- Cần sao Lộc đối chiếu mới cát; không thì BẤT ỔN, TIÊU CỰC
- Nữ mệnh nên lấy chồng lớn tuổi""",

    # Tử-Tham Mệnh Mão/Dậu — §4.4.1
    "Tử Vi_2_Tham Lang": """**MỆNH TỬ-THAM MÃO/DẬU** (Q2 p336-341):
- THUẦN DỤC VỌNG — Vũ-Phá tam hợp + Liêm-Thất Phúc Đức
- Phân biệt VẬT CHẤT (Tham Hóa Lộc) vs DỤC TÌNH (Thiên Diêu/Hàm Trì hội)
- TÍNH CHỦ ĐỘNG MẠNH — vì mục đích có thể KHÔNG TỪ THỦ ĐOẠN""",

    # Liêm-Phá Mệnh Mão/Dậu — §5.1.6
    "Liêm Trinh_2_Phá Quân": """**MỆNH LIÊM-PHÁ MÃO/DẬU** (Q2 p459):
- Thích hợp làm CÔNG CHỨC — lấy khai sáng làm chức trách
- Phân biệt "VIỆC CÔNG" (Liêm Hóa Lộc) vs "TƯ LỢI" (Liêm Hóa Kỵ)""",

    # Tử-Phá Mệnh Sửu/Mùi
    "Tử Vi_1_Phá Quân": """**MỆNH TỬ-PHÁ SỬU/MÙI** (Q2):
- Sức khai sáng mạnh từ chỗ KHÔNG CÓ GÌ
- Vợ chồng cùng sáng lập sự nghiệp, có thể tay trắng làm nên""",

    # Cự Môn Mệnh — §5.1.10
    "Cự Môn_0": """**MỆNH CỰ MÔN TÝ** (Q2 p534):
- "Thạch trung ẩn ngọc" — Hóa Lộc = phú, Hóa Quyền = quý
- KHÔNG nên ngồi vị trí tối cao""",
    "Cự Môn_6": """**MỆNH CỰ MÔN NGỌ** (Q2 p534):
- "Thạch trung ẩn ngọc" — Hóa Lộc = phú, Hóa Quyền = quý
- KHÔNG nên ngồi vị trí tối cao""",

    # Tử Vi độc tọa
    "Tử Vi_0": """**MỆNH TỬ VI TÝ** (Q2 §5.1.1):
- Đối Tham Lang → "Phiếm Thủy Đào Hoa" nếu có Kình Dương đối
- Cần "bách quan triều củng" để thành cách; thiếu → "tại dã cô quân" (cô độc) hoặc "vô đạo" (bạo ngược)
- Ưa cung hạn Phủ + Tướng tọa thủ""",
    "Tử Vi_6": """**MỆNH TỬ VI NGỌ** (Q2 §5.1.1):
- Tốt hơn Tý — không bị "Phiếm Thủy Đào Hoa"
- Cần "bách quan triều củng" để thành cách Đế Tinh
- Ưa cung hạn Phủ + Tướng""",

    # Thiên Cơ Mệnh — §5.1.2
    "Thiên Cơ_0": """**MỆNH THIÊN CƠ TÝ** (Q2 §5.1.2):
- Ưa Hóa Quyền (vững vàng) hơn Hóa Lộc (trôi nổi bất định)
- "Cơ Nguyệt Đồng Lương" cách — dùng miệng kiếm tiền
- Kỵ Hỏa-Linh đồng độ → rời xa cha mẹ từ bé""",
    "Thiên Cơ_6": """**MỆNH THIÊN CƠ NGỌ** (Q2 §5.1.2):
- Tương tự Tý — Ưa Hóa Quyền hơn Hóa Lộc
- "Cơ Nguyệt Đồng Lương" cách""",

    # Thái Dương Mệnh — §5.1.3
    "Thái Dương_X_Cự Môn": """**MỆNH THÁI DƯƠNG-CỰ MÔN** (Q2 §5.1.3 + p482):
- Tam phương đều vô chính diệu → BỊ CÔ LẬP / cổ nhân định "người ngoại quốc"
- Phân biệt "ĐƯỢC TRỢ GIÚP" (Lộc Quyền Khoa) vs "BỊ CÔ LẬP" (sao lẻ, Hóa Kỵ)
- Sinh ngày tốt hơn sinh đêm; nhập miếu tốt hơn lạc hãm""",

    # Vũ Khúc Mệnh — §5.1.4
    "Vũ Khúc_X_Thiên Phủ": """**MỆNH VŨ-PHỦ** (Q2 §5.1.4):
- Sống thọ; Vũ-Phủ Ngọ tốt hơn Tý
- Hợp với giới làm ăn kinh doanh, ngân hàng, tài chính
- Sao Lộc + Khôi-Việt → đắc ý""",
    "Vũ Khúc_X_Tham Lang": """**MỆNH VŨ-THAM** (Q2 §5.1.4 + p476):
- Phân biệt "DỤC VỌNG" (ai cũng có, không hại) vs "THAM VỌNG" (tổn nhân lợi kỷ)
- Hỏa-Linh đồng → cách "Hỏa Tham" / "Linh Tham" phát đột ngột
- Sao Lộc + Khôi-Việt → quý""",
    "Vũ Khúc_X_Thất Sát": """**MỆNH VŨ-THẤT** (Q2 §5.1.4):
- Tính cương mãnh — võ nghiệp
- Phải có sao Lộc mới chủ giàu""",

    # Thiên Đồng Mệnh
    "Thiên Đồng_X": """**MỆNH THIÊN ĐỒNG** (Q2 §5.1.5):
- Sao "phúc" — chủ về hưởng thụ, an nhàn
- Cần Hóa Lộc + Văn Xương/Khúc → "khoát đạt" (thông minh, có tài)
- Hỏa-Linh đồng → "đoản chí" (việc sắp thành lại hỏng)""",

    # Liêm Trinh Mệnh — §5.1.6
    "Liêm Trinh_X_Thiên Tướng": """**MỆNH LIÊM-TƯỚNG TÝ/NGỌ** (Q2 p522):
- Khí hòa hoãn — thông minh mẫn tiệp, có tính phục vụ
- Cần "Tài ấm giáp ấn" → phú quý nhưng vẫn ở vị trí PHỤ TÁ
- Kỵ Hỏa-Linh đồng → trắc trở nghiêm trọng, có khuynh hướng tự sát""",
    "Liêm Trinh_X_Thiên Phủ": """**MỆNH LIÊM-PHỦ THÌN/TUẤT** (Q2):
- Liêm Trinh + Thiên Phủ Thìn/Tuất là quý cách
- Tài ấm + Bách quan triều củng → đại phú đại quý""",
    "Liêm Trinh_X_Thất Sát": """**MỆNH LIÊM-THẤT SỬU/MÙI** (Q2 p358):
- "Hùng Tú Kiển Nguyên Cách" — chỉ ở MÙI mới thành (Mùi tốt hơn Sửu)
- Phân biệt PHẤN CHẤN vs CƯƠNG BẠO
- Phấn chấn: gặp Xương-Khúc + Lộc, không sát → trải qua gian khổ thành đại nghiệp""",

    # Thiên Phủ Mệnh — §5.1.7
    "Thiên Phủ_X": """**MỆNH THIÊN PHỦ** (Q2 §5.1.7):
- Sao "kho tiền" — giỏi giữ tiền, chưa chắc giỏi kiếm
- Ưa sao Lộc + Triều Củng — không ưa "kho lộ", "kho trống"
- "Phùng Phủ khán Tướng" — phải xem cả Thiên Tướng""",

    # Thái Âm Mệnh — §5.1.8
    "Thái Âm_X": """**MỆNH THÁI ÂM** (Q2 §5.1.8):
- Sao tiền tài (kế hoạch) — văn; khác Vũ Khúc (hành động) võ
- Nhập miếu tốt, lạc hãm xấu; sinh đêm tốt hơn sinh ngày
- Ưa Hóa Lộc + Văn Xương/Khúc → thông minh + tiền tài""",

    # Tham Lang Mệnh — §5.1.9
    "Tham Lang_X": """**MỆNH THAM LANG** (Q2 §5.1.9):
- Sao vật dục + sắc dục — ưa Hỏa-Linh đồng (cách "Hỏa Tham" phát đột ngột)
- Sinh hoạt tinh thần: thích THẦN BÍ TÔN GIÁO
- Cách "Phiếm Thủy Đào Hoa" (Tý + Kình) / "Phong Lưu Thái Trượng" (Dần + Đà) = vì sắc thất bại""",

    # Thiên Lương Mệnh — §5.1.12
    "Thiên Lương_X": """**MỆNH THIÊN LƯƠNG** (Q2 p539):
- "Ấm tinh" — che chở TINH THẦN, KHÔNG vật chất
- Phải GẶP NẠN trước rồi mới hóa giải (tiêu tai giải ách)
- Ưa Hóa Khoa, KHÔNG ưa Hóa Lộc (mang thị phi) / Hóa Quyền (lộng quyền)""",

    # Thất Sát Mệnh — §5.1.13
    "Thất Sát_X": """**MỆNH THẤT SÁT** (Q2 p543):
- "Hai cung gặp nó định phải trải qua GIAN KHỔ" — Mệnh/Thân có Sát = đời người ắt có thời kỳ gian khổ
- Kỵ Cự Môn / Thiên Cơ cung hạn
- Đối Thiên Phủ → công vs thủ, cân bằng quan trọng""",

    # Phá Quân Mệnh — §5.1.14
    "Phá Quân_X": """**MỆNH PHÁ QUÂN** (Q2 §5.1.14):
- Cần sao Lộc → tiêu trừ khuyết điểm hao tổn, phá tán; tăng sáng tạo
- Ở Thủy Vực (Hợi/Tý/Sửu) + Văn Khúc → tàn tật rời quê hương
- Sát-cát lẫn lộn + Xương-Khúc → "hàn sĩ có tài không gặp thời" """,
}


CHINH_TINH_TAI_PHU_THE = {
    "Tử Vi_2_Tham Lang": """**PHU THÊ TỬ-THAM** (Q2 p569):
- "Thuần dục vọng" — phân biệt vật chất / dục tình
- Tử-Tham + CÁT TINH ≠ "đào hoa phạm chủ" → vợ chồng cùng sáng nghiệp,
  NHƯNG VỢ LÀ NHÂN VẬT CHÍNH (chủ sở hữu / đứng tên pháp lý)
- Nam mệnh Tử Vi đồng Phu Thê → VỢ NÊN CÓ SỰ NGHIỆP RIÊNG;
  nếu vợ ở nhà nhiều → "KHÔNG CHẾ CHỒNG" (Q2 p571)""",

    "Thiên Cơ_X": """**PHU THÊ THIÊN CƠ** (Q2 p573):
- VỀ CƠ BẢN BẤT LỢI — trừ phi đối/đồng Thái Âm + cát tinh mới sống đến bạc đầu
- Cơ Hóa Kỵ + Cự Môn Hóa Kỵ → vợ chồng dễ thay lòng đổi dạ
- Vợ chồng nên CHÊNH LỆCH TUỔI TÁC""",

    "Thái Dương_X": """**PHU THÊ THÁI DƯƠNG** (Q2 p579):
- KỴ Hóa Kỵ — chủ về SINH LY TỬ BIỆT với nguyên phối
- Hợp với người ngoại quốc / phương xa""",
}


CHINH_TINH_TAI_PHUC_DUC = {
    "Liêm Trinh_7_Thất Sát": """**PHÚC ĐỨC LIÊM-THẤT MÙI** (Q2 p358 + p858):
- "Hùng Tú Kiển Nguyên" — phân biệt PHẤN CHẤN vs CƯƠNG BẠO
- Liêm-Thất thuộc nhóm "HAY LO TOAN, NGHĨ NGỢI" (khác Liêm-Phủ/Tướng/Tham "tự thỏa mãn")
- "Tư tưởng TIÊU CỰC — việc gì cũng SUY NGHĨ TỪ MẶT XẤU" (p858)
- Cứu paradigm: KHOA VĂN đồng độ → quân bình; nếu không có XƯƠNG-KHÚC →
  TU DƯỠNG HỌC THUẬT là đường cứu

- Biểu hiện cương bạo: "ĐOẠT SỨC KIẾM TIỀN, không thiết một thứ gì khác, ít hưởng thụ"
- Layer ẩn: thỉnh thoảng "ẨN TU, không màng danh lợi" (do Thất Sát + Không-Kiếp đối)""",

    "Tử Vi_X": """**PHÚC ĐỨC TỬ VI** (Q2 p847):
- Phúc hậu hoặc cực kỳ ĐỘC ĐOÁN (phân biệt qua "bách quan triều củng" vs "tại dã cô quân")
- Lòng yêu ghét nặng""",

    "Thiên Cơ_X": """**PHÚC ĐỨC THIÊN CƠ** (Q2 p850):
- LO NGHĨ NHIỀU, hứng thú nhiều thứ, tư tưởng không tập trung
- Việc sắp thành lại hỏng""",
}


CHINH_TINH_TAI_THIEN_DI = {
    "Vũ Khúc_11_Phá Quân": """**THIÊN DI VŨ-PHÁ HỢI** (Q2 p370 + p736):
- Phân biệt "GIỎI THÍCH ỨNG" vs "NGOAN CỐ"
- Có Lộc Tồn (anh ở Mệnh đối) → có hỗ trợ, không thì BẤT ỔN, TIÊU CỰC
- Vũ-Phá rất NGẠI Hỏa-Linh đồng độ → bị TÌNH THẾ BỨC ÉP thành ngoan cố
- Có Không-Kiếp đồng → đi xa OK, KHÔNG NÊN ĐỊNH CƯ LÂU DÀI (kẹt tha hương)
- CẢNH BÁO: "Lộc Mã giao trì + sát kỵ ám xung = ra ngoài kiếm tiền CHUỐC HUNG HỌA" (p731)""",

    "Vũ Khúc_5_Phá Quân": """**THIÊN DI VŨ-PHÁ TỴ** — đối Tướng Hợi:
- Tương tự Vũ-Phá Hợi, paradigm chính""",
}


CHINH_TINH_TAI_SU_NGHIEP = {
    "Cự Môn_X": """**SỰ NGHIỆP CỰ MÔN** (Q2 p813):
- TÍNH CHẤT CƠ BẢN: "DÙNG TÀI ĂN NÓI ĐỂ KIẾM TIỀN"
- Nghề tốt: luật sư, ngoại giao, chính khách, GIÁO SƯ, NHÀ THUẬT SỐ, bán hàng
- Mở rộng "miệng lưỡi" → ẨM THỰC, y khoa (răng hàm mặt, tiêu hóa)
- Ưa Hóa Lộc / Lộc Tồn → thanh danh từ "miệng"
- KHÔNG nên chủ động phô trương — bị bài xích, chèn ép
- KHÔNG nên ngồi ghế thứ nhất ở công ty lớn""",

    "Thiên Tướng_X": """**SỰ NGHIỆP THIÊN TƯỚNG** (Q2 §5.9.11):
- Thường ở VỊ TRÍ PHÓ — danh nghĩa không bằng thực tế
- Nên có sao Lộc / cát hóa → kinh tế tài chính""",
}


CHINH_TINH_TAI_PHU_MAU = {
    "Thiên Lương_X": """**PHỤ MẪU THIÊN LƯƠNG** (Q2 p539):
- THIÊN LƯƠNG = "ẤM TINH" — che chở thuộc TINH THẦN, KHÔNG VẬT CHẤT
- Phải GẶP NẠN TRƯỚC RỒI MỚI HÓA GIẢI (tiêu tai giải ách)
- Cha mẹ trợ tinh thần, không trợ vật chất → con tự lập kinh tế""",
}


# ════════════════════════════════════════════════════════════════
# BUILDER
# ════════════════════════════════════════════════════════════════

def _stars_at_named_palace(la_so: dict, palace_name: str) -> dict[str, list[str]]:
    pal = _find_palace(la_so, palace_name)
    if not pal:
        return {"chinh_tinh": []}
    return _stars_at_branch_idx(la_so, pal["branch_index"])


def _palace_branch_idx(la_so: dict, palace_name: str) -> int | None:
    pal = _find_palace(la_so, palace_name)
    return pal["branch_index"] if pal else None


def _match_chinh_tinh_paradigm(la_so: dict, palace_name: str, registry: dict) -> list[str]:
    """Tìm paradigm khớp cho cung này trong registry."""
    stars = _stars_at_named_palace(la_so, palace_name)
    chinh_tinh = stars.get("chinh_tinh", [])
    branch_idx = _palace_branch_idx(la_so, palace_name)

    matched = []
    for key, paradigm in registry.items():
        # Format key: "Tinh_idx" hoặc "Tinh1_idx_Tinh2" hoặc "Tinh_X" (X = any branch)
        parts = key.split("_")
        if len(parts) == 2:
            # "Tinh_idx" or "Tinh_X"
            star, idx_str = parts
            if idx_str == "X":
                # Match any branch
                if any(star in s for s in chinh_tinh):
                    matched.append(paradigm)
            else:
                try:
                    expected_idx = int(idx_str)
                except ValueError:
                    continue
                if branch_idx == expected_idx and any(star in s for s in chinh_tinh):
                    matched.append(paradigm)
        elif len(parts) == 3:
            # "Tinh1_idx_Tinh2" — dual star at specific branch
            star1, idx_str, star2 = parts
            try:
                expected_idx = int(idx_str)
            except ValueError:
                continue
            if (branch_idx == expected_idx
                    and any(star1 in s for s in chinh_tinh)
                    and any(star2 in s for s in chinh_tinh)):
                matched.append(paradigm)
    return matched


def build_trung_chau_context(la_so: dict, gender: str = "nam") -> str:
    """Build paradigm CỐT context for LLM phê mệnh sâu.

    Returns a multi-line string with:
    - 3 Iron Rules Trung Châu (luôn inject)
    - Paradigm khớp cho 6 cung trọng yếu: Mệnh, Phu Thê, Phúc Đức,
      Thiên Di, Sự Nghiệp, Phụ Mẫu
    """
    parts = [IRON_RULES_HEADER]

    # 6 cung × registry
    palace_registries = [
        ("Mệnh", CHINH_TINH_TAI_MENH),
        ("Phu Thê", CHINH_TINH_TAI_PHU_THE),
        ("Phúc Đức", CHINH_TINH_TAI_PHUC_DUC),
        ("Thiên Di", CHINH_TINH_TAI_THIEN_DI),
        ("Sự Nghiệp", CHINH_TINH_TAI_SU_NGHIEP),
        ("Phụ Mẫu", CHINH_TINH_TAI_PHU_MAU),
    ]

    paradigm_block = []
    for palace_name, registry in palace_registries:
        matched = _match_chinh_tinh_paradigm(la_so, palace_name, registry)
        for paradigm in matched:
            paradigm_block.append(paradigm)

    if paradigm_block:
        parts.append("\n━━━ 📜 PARADIGM TRUNG CHÂU Q2 KHỚP LÁ SỐ NÀY ━━━")
        parts.extend(paradigm_block)

    parts.append("\n━━━ 🎯 LƯU Ý KHI LUẬN GIẢI ━━━")
    parts.append(
        "- Áp dụng 3 Iron Rule TRUNG CHÂU vào tất cả 10 sections\n"
        "- Đặc biệt section 6 ĐẠI VẬN, section 7 LƯU NIÊN, section 10 KẾT TÂM AN:\n"
        "  PHẢI dùng nguyên tắc DI CUNG HOÁN VỊ — không chỉ xem cung Mệnh đại vận\n"
        "- Trích quote Hán-Việt từ Vương Đình Chỉ Q2 khi phù hợp + DỊCH SANG VIỆT NGAY SAU\n"
        "- KHÔNG predict tuyệt đối — dùng paradigm phản chiếu"
    )

    return "\n".join(parts)
