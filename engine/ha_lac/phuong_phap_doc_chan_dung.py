"""Phương Pháp Đọc Chân Dung Hà Lạc — Method extract từ Phần Ba Xuân Cang.

Paradigm Anh (2026-06-02): "Engine ra được cách cục, chứ chưa luận giải sâu được."

Module này extract PHƯƠNG PHÁP cụ thể Xuân Cang dùng để đọc lá số:
1. Tản Đà (Sơn Thủy Mông) — p420-451
2. Tô Hoài — p465-482
3. Nguyên Ngọc — p483-494
4. Trần Đăng Khoa — p495-519
5. Nguyễn Thị Thu Huệ — p520-531
6. Nguyễn Hiến Lê (Bác + Thái Quy Muội) — p532-541
7. Đoàn Thị Lam Luyến (Lôi Thiên Đại Tráng) — p533-541

PHƯƠNG PHÁP 7 BƯỚC để LLM có thể luận giải tường minh:
"""

from __future__ import annotations


# 7 bước Xuân Cang dùng để đọc chân dung Hà Lạc
PHUONG_PHAP_7_BUOC: list[dict] = [
    {
        "step": 1,
        "title": "Cấu trúc Hà Lạc 4 thành phần",
        "desc": (
            "Lấy 4 thành phần CỐT: Tiên Thiên (THỂ) + Hậu Thiên (DỤNG) + Hỗ Tiên + Hỗ Hậu. "
            "Tiên Thiên = mệnh trời TỔNG (chi phối cả đời). Hậu Thiên = vận hành thực tế "
            "(tiền vận → hậu vận). Hỗ = mặt động bên trong."
        ),
        "vi_du": (
            "Tản Đà: Sơn Thủy Mông (TT, mệnh giáo hóa). "
            "Nguyễn Hiến Lê: Bác + Thái Quy Muội (TT + HT). "
            "Đoàn Thị Lam Luyến: Lôi Thiên Đại Tráng (TT + chi phối cả đời nữ thơ chứa sấm trời)."
        ),
    },
    {
        "step": 2,
        "title": "Hóa Công + Thiên Nguyên Khí + Địa Nguyên Khí",
        "desc": (
            "Check 3 ưu tiên Trời Đất: Hóa Công (mùa sinh), TNK (Can năm sinh), ĐNK (Chi năm sinh). "
            "Có cả 3 = Phú Quý song toàn. Có TNK → SANG TRỌNG (hiển đạt). Có ĐNK → GIÀU CÓ."
        ),
        "vi_du": (
            "Tản Đà: Có Hóa Công + có Địa Nguyên Khí. "
            "Founder: Có TNK Khảm (Can Mậu → Khảm có trong cấu trúc) — chủ về SANG TRỌNG."
        ),
    },
    {
        "step": 3,
        "title": "Cross-link tên người + tượng quẻ + nghề nghiệp",
        "desc": (
            "Đây là bước Xuân Cang gọi 'reo lên: thế là chúng ta đã tìm ra đúng ngày giờ sinh!'. "
            "Cross-link tên người, tên đất, nghề nghiệp với tượng quẻ. "
            "Nếu khớp → chứng minh quẻ đúng. Nếu không → kiểm tra lại giờ sinh."
        ),
        "vi_du": (
            "**Tản Đà = Sơn Thủy Mông**: Tản = núi Tản (Sơn), Đà = sông Đà (Thủy), "
            "Mông = sứ mạng giáo hóa → Tản Đà viết Lên Sáu/Lên Tám/Đài Gương Kí/Quốc Sử Huấn Mông "
            "dạy trẻ em. **NGẪU NHIÊN KHÔNG THỂ TÌNH CỜ.**"
        ),
    },
    {
        "step": 4,
        "title": "Quan Mệnh × Quẻ — cross-table Mạng × Bát Quái",
        "desc": (
            "Lấy nạp âm (Mộc/Kim/Thủy/Hỏa/Thổ) cross với 8 trigram quẻ chính. "
            "Đã có sẵn trong engine `menh_hop_cach.py` MANG_VS_TRIGRAM (5×8 table)."
        ),
        "vi_du": (
            "**Đoàn Thị Lam Luyến mệnh Mộc tùng bách + quẻ Càn (Lôi Thiên Đại Tráng)**: "
            "'Mệnh Mộc gặp Càn → mơ mộng hão huyền, ít thực tế.' → Giải thích vì sao thơ ĐTLL "
            "'thất vọng chán chường vì không tìm được tình yêu lý tưởng' (qua *Chồng Chị Chồng Em* "
            "+ *Châm Khói*)."
        ),
    },
    {
        "step": 5,
        "title": "Đếm quẻ LẶP LẠI nhiều lần trong đời",
        "desc": (
            "Trong 12 đại vận × 6 hào = 72 quẻ năm cuộc đời, nếu 1 quẻ lặp lại ≥3 lần → "
            "đó là ĐẶC TÍNH NỔI BẬT của chủ thể. Không phải ngẫu nhiên."
        ),
        "vi_du": (
            "**Tản Đà có**:\n"
            "- 4 quẻ CÁCH (cách tân, cách mạng) → thơ Tản Đà CÁCH TÂN khỏi niêm luật, mở Thơ Mới\n"
            "- 3 quẻ BÍ (trang sức) → chú trọng HÌNH THỨC văn chương (vần điệu, âm thanh, tượng hình)\n"
            "- 2 quẻ DI (nuôi dưỡng) → văn hóa ẨM THỰC (sáng tạo món ăn, viết về cách ăn)"
        ),
    },
    {
        "step": 6,
        "title": "Hào chủ mệnh suốt đời = paradigm hành xử cốt",
        "desc": (
            "Mỗi đại vận có 1 hào nguyên đường chi phối. Hào chủ mệnh CỦA TIỀN VẬN xuyên suốt "
            "1/2 đời đầu. Hào chủ mệnh CỦA HẬU VẬN xuyên suốt 1/2 đời sau. "
            "Phải match với cách hành xử thực tế người."
        ),
        "vi_du": (
            "**NHL hào 4 quẻ Quán**: 'Luôn gần các nguyên thủ' → NHL viết về Khổng Tử, Mạnh Tử, "
            "Trang Tử, Tô Đông Pha, Hàn Phi Tử — toàn là các 'nguyên thủ'.\n"
            "**Tản Đà hào 2 quẻ Mông**: 'Bậc hiền tài lớn, đại lượng, bao dung' — Tản Đà là tài "
            "năng giao thời 2 thế kỷ, cách tân thơ ca dân tộc."
        ),
    },
    {
        "step": 7,
        "title": "Sự kiện CỤ THỂ từng năm match với quẻ năm",
        "desc": (
            "Đây là bước CHỨNG MINH quẻ đúng — không thể có quẻ năm nào sai mà sự kiện đúng. "
            "Lấy 1 sự kiện đời (xuất bản, biến cố, thi đỗ, hôn nhân, mất...) → tra quẻ năm tương "
            "ứng → cross-link với lời quẻ."
        ),
        "vi_du": (
            "**Tản Đà**:\n"
            "- 1909 (thi rớt) ↔ quẻ CÁCH hào 3 'tiến hiểu thì hung'\n"
            "- 1914 (đỗ đạt) ↔ quẻ KÝ TẾ 'đã sang sông'\n"
            "- 1920 (viết Thề Non Nước) ↔ quẻ BÍ (trang sức văn chương)\n"
            "- 1932 (rời An Nam tạp chí, lên đường mây) ↔ quẻ TIỆM hào 6 'chim hồng bay lên mây'\n"
            "- 1939 ngày mất ↔ quẻ TIỂU SÚC hào 3 'xe rời nhất trục'\n"
            "**NHL 1973**: từ chối giải Ngô Đình Diệm 1 triệu = 25 lượng vàng "
            "↔ Tổn hào 6 'cuối thời Tổn, không Tổn nữa.'\n"
            "**NHL 1979**: viết 'Kinh Dịch — Đạo của người quân tử' với tâm vô tư "
            "↔ quẻ HÀM 'lấy tấm lòng hư không thu phục người.'"
        ),
    },
]


# 3 mẹo Xuân Cang dùng — khi không biết giờ sinh
MEO_TIM_GIO_SINH: list[str] = [
    "1. Cross-check 12 quẻ × 12 giờ trong ngày Can Chi đã biết. Chọn quẻ ỨNG NGHIỆM NHẤT với đời.",
    "2. Cross-link tên người + nghề nghiệp với tượng quẻ. Khớp = quẻ đúng.",
    "3. Sự kiện đời cụ thể (thi đỗ/rớt, xuất bản, biến cố) phải match với quẻ năm tương ứng.",
]


# 4 paradigm xuyên suốt cho LLM luận giải
PARADIGM_CHO_LLM_LUAN_GIAI: dict[str, str] = {
    "khong_predict_tinh": (
        "**KHÔNG predict cát/hung tĩnh**. Quẻ phản chiếu cấu trúc khoảnh khắc sinh — "
        "không phải vận mệnh cứng. Người sống thế nào, paradigm có thể chuyển."
    ),
    "cross_link_doi_thuc": (
        "**Cross-link đời thực**: Lấy 3-5 sự kiện cụ thể từ đời người (xuất bản, biến cố, "
        "thi đỗ, hôn nhân, mất, di chuyển nơi chốn) → tra quẻ năm → match với lời quẻ → "
        "chứng minh quẻ đúng."
    ),
    "tinh_cach_tu_que_chinh": (
        "**Tính cách từ quẻ chính + nạp âm**: cross-table Mạng × Bát Quái (đã có engine). "
        "Hào chủ mệnh suốt đời = paradigm hành xử cốt."
    ),
    "que_lap_lai_dac_tinh_noi_bat": (
        "**Quẻ lặp lại nhiều ≥3 lần = đặc tính nổi bật**. Vd Tản Đà có 4 Cách, 3 Bí, 2 Di "
        "→ tướng văn cách tân, trang sức, ẩm thực. Đếm trên 72 quẻ năm."
    ),
}


# Case studies thật từ Phần Ba — dataset cho LLM
CASE_STUDIES_PHAN_BA: list[dict] = [
    {
        "ten": "Tản Đà (Nguyễn Khắc Hiếu)",
        "sinh": "1889-05-19 giờ Tý (Kỷ Sửu, Kỷ Tỵ, Ất Mùi, Bính Tý)",
        "tien_thien": "Sơn Thủy Mông",
        "hao_chu_menh": 2,
        "phuong_phap_match": (
            "Cross-link tên: Tản = Sơn (núi Tản), Đà = Thủy (sông Đà). "
            "Sứ mạng: 'Bậc hiền tài lớn, đại lượng, bao dung' → viết Lên Sáu/Lên Tám/Đài Gương Kí "
            "dạy trẻ em (mệnh GIÁO HÓA quẻ Mông)."
        ),
        "que_dac_biet": "4 quẻ Cách (cách tân thơ) + 3 quẻ Bí (trang sức văn) + 2 quẻ Di (ẩm thực)",
        "su_kien_match": [
            "1909: thi rớt o-ral ↔ Cách hào 3 'tiến hiểu thì hung'",
            "1920: viết Thề Non Nước ↔ Bí hào 2 (trang sức bộ râu = trang sức văn chương)",
            "1932: rời An Nam tạp chí lên đường mây ↔ Tiệm hào 6 'chim hồng bay tầng mây'",
            "1939-04-20: mất ↔ Tiểu Súc hào 3 'xe rời nhất trục'",
        ],
        "source": "Xuân Cang p.420-451 (chân dung mẫu, đầu Phần Ba)",
    },
    {
        "ten": "Nguyễn Hiến Lê",
        "sinh": "1912-01-08 giờ Dậu (Tân Hợi)",
        "tien_thien": "Bác",
        "hau_thien": "Thái → Quy Muội",
        "hao_chu_menh": 4,
        "que_chu_menh_la": "Quán hào 4",
        "phuong_phap_match": (
            "Hào 4 quẻ Quán = 'gần các nguyên thủ' → NHL viết về Khổng Tử, Mạnh Tử, Trang Tử, "
            "Tô Đông Pha, Hàn Phi Tử — đều là 'nguyên thủ' tư tưởng."
        ),
        "su_kien_match": [
            "1973: từ chối giải Ngô Đình Diệm 1 triệu = 25 lượng vàng ↔ Tổn hào 6 'cuối thời Tổn, không Tổn nữa'",
            "1979: viết 'Kinh Dịch - Đạo của người quân tử' ↔ Hàm 'hư tâm thu phục người'",
            "1968+: bộ sách tâm đắc về 'người quân tử' ↔ paradigm Bác (hào 6 = đạo quân tử không bao giờ hết)",
        ],
        "source": "Xuân Cang p.532-541",
        "paradigm_can_them_vao_engine": (
            "NHL chủ trương: 'Bỏ phần BÓI TOÁN huyền bí, nhất là phần TƯỚNG SỐ.' "
            "→ Cross-link với Iron Rule #4+6 'không predict tĩnh' — NHL paradigm DỊCH = "
            "ĐẠO của NGƯỜI QUÂN TỬ, không phải tool tướng số."
        ),
    },
    {
        "ten": "Tô Hoài",
        "sinh": "1920-09-27 giờ Dậu (Canh Thân, Ất Dậu, Mậu Tý, Tân Dậu), Mệnh Mộc thạch lựu",
        "tien_thien": "Đại Quá",
        "hau_thien": "Tiểu Súc",
        "ho_quai": "Khuê",
        "hoa_cong": "Đoài ở Tiên Thiên + Hậu Thiên",
        "phuong_phap_match": (
            "Tô Hoài mệnh ĐẠI QUÁ + có Hóa Công → làm việc phi thường: 150+ đầu sách, đi khắp thế giới. "
            "Cấu trúc Phong (gió) + Thiên (trời) + Đoài (đầm hồ) → 'làn gió bay trên trời cao'. "
            "Khi tập trung paradigm Đoài (đầm hồ) → viết về quê đầm hồ Tây (Hà Nội): Dế Mèn, "
            "Giảng Thề, Quê Nhà, Cát Bụi, Chuyện Cũ → kiệt tác."
        ),
        "paradigm_nhan_xet": (
            "**Tiếc**: Có Đại Quá + Hóa Công thì có thể làm phi thường, nhưng nếu Tô Hoài tập trung "
            "150 đầu sách vào QUÊ ĐẦM HỒ (paradigm chính của cấu trúc), bạn đọc nước nhà còn nhờ "
            "nhiều hơn — Đại Quá có ưu tiên năng lượng nhưng vẫn nên đi đúng paradigm tượng quẻ."
        ),
        "source": "Xuân Cang p.465",
    },
    {
        "ten": "Nguyên Ngọc",
        "sinh": "1932-09-05 giờ Mão (Nhâm Thân, tháng Bảy)",
        "tien_thien": "Địa Phong Thăng",
        "ho_tien": "Lôi Trạch Quy Muội",
        "hau_thien": "Thủy Địa Tỷ",
        "ho_hau": "Sơn Địa Bác",
        "hao_chu_menh_tt": 3,
        "hao_chu_menh_ht": 6,
        "dia_nguyen_khi": "Khôn (3 quẻ Khôn trong cấu trúc — rất giàu ĐNK)",
        "phuong_phap_match": (
            "Cấu trúc 4 quẻ: Địa + Phong + Thủy + Sơn — toàn ĐẤT + CÂY + NƯỚC. "
            "→ Toàn bộ tác phẩm Nguyên Ngọc: 'Đất Nước Đứng Lên', 'Đất Quảng', 'Mạch nước ngầm', "
            "'Rừng xanh', 'Mùa hoa thuốc phiện cuối cùng' — đều ĐẤT và NƯỚC. Không đi đâu ra "
            "khỏi paradigm tượng quẻ. **Nguyên Ngọc → tự nhận ngỡ ngàng khi nhận ra.**"
        ),
        "paradigm_cay_mam_len_loi": (
            "**Hào 3 quẻ Thăng (chủ mệnh tiền vận)**: 'Tiến lên DỄ NHƯ vào ấp không người.' "
            "Tượng quẻ: cây mầm LEN LỎI lên qua sỏi đá, vượt trở ngại, hướng về ánh nắng. "
            "→ Nguyên Ngọc là người: nhạy cảm với CÁI MỚI, ủng hộ cái mới hết lòng, giàu MƠ MỘNG + "
            "TƯỞNG TƯỢNG + NIỀM TIN tâm linh (tin trong lòng, không lễ lạt). "
            "Đường đời: học giỏi, vào bộ đội Tây Nguyên 1945, gặp quý nhân, sớm vào nghề làm báo."
        ),
        "paradigm_quy_muoi_cuc_doan": (
            "**Hỗ Tiên Quy Muội** → Bạn bè dùng chữ CỰC ĐOAN để chỉ Nguyên Ngọc. "
            "1987 làm Tổng Biên Tập báo Văn Nghệ — quẻ Tỷ → để xuất hàng loạt quan điểm đổi mới + "
            "quá đà ('văn chương phải đạo', 'lời ai điếu cho văn chương minh họa'). "
            "Cuối cùng chỉ làm được việc nhỏ, chưa đúng tham vọng lớn — paradigm Quy Muội."
        ),
        "source": "Xuân Cang p.466-482",
    },
    {
        "ten": "Trần Đăng Khoa",
        "sinh": "ngày tháng năm — cấu trúc giống NHL chỉ khác Hóa Công",
        "tien_thien": "Phong Địa Quán",
        "hau_thien": "Địa Thiên Thái",
        "ho_quai": "Lôi Trạch Quy Muội + Sơn Địa Bác",
        "hoa_cong": "Chấn ở Hỗ Hậu Thiên (NHL không có)",
        "phuong_phap_match": (
            "Cấu trúc Trần Đăng Khoa GIỐNG HỆT Nguyễn Hiến Lê (cả 4 quẻ + 2 hào nguyên đường)! "
            "Chỉ khác: TĐK có Hóa Công Chấn (sấm) trong Hỗ Hậu Thiên — NHL không có. "
            "Hóa Công Chấn → TĐK là THẦN ĐỒNG (Tử Quán trong Tứ Trụ — nổi danh rất sớm)."
        ),
        "paradigm_nhin_tu_troi_xuong": (
            "**Hậu vận Thái** → cả Trần Đăng Khoa và NHL đều có tố chất TRỜI chiếm lĩnh tâm trí. "
            "→ Cái nhìn TỪ TRỜI XUỐNG — bao quát, rộng rãi, phóng khoáng, công bằng, độ lượng. "
            "TĐK: thơ + phê bình văn chương (Chân Dung và Đối Thoại). "
            "NHL: tổng kết sách Khổng-Mạnh-Trang-Tử-Hàn Phi từ cái nhìn cao."
        ),
        "case_di_chech_hanh_lang": (
            "**Đi chệch hành lang ngắn**: TĐK có ý định trở thành nhà thơ HẢI QUÂN — nhưng "
            "TĐK không có duyên VÙNG TRỜI NƯỚC trong cấu trúc. Sau đó về đúng paradigm = "
            "nhà thơ của ĐẤT TRỜI + GIÓ CÂY + ĐẦM HỒ + SẤM CHỚP."
        ),
        "source": "Xuân Cang p.495-519",
    },
    {
        "ten": "Nguyễn Thị Thu Huệ",
        "sinh": "1966-08-12 sau 3am giờ Dần (Bính Ngọ, Bính Thân, Quý Mão)",
        "tien_thien": "Thiên Địa Bĩ",
        "ho_tien": "Phong Sơn Tiệm (?)",
        "hau_thien": "Địa Lôi Phục",
        "thien_nguyen_khi": "Càn ở Hỗ Tiên Thiên",
        "phuong_phap_match": (
            "Tiền Thiên BĨ → Thu Huệ tự bạch: 'ĐẶC BIỆT SỢ NHỮNG NGƯỜI LỪA LỌC.' "
            "→ Thu Huệ là BẠN của những THÂN PHẬN BĨ — người khốn khó, bế tắc, trôi dạt, cô đơn, "
            "nhiều người được xếp 'tiểu nhân'. Truyện ngắn 'Ký ức': anh họa sĩ vì tôn trọng "
            "tiết trinh người con gái mà làm cô không biết hạnh phúc dâng hiến — paradigm Bĩ."
        ),
        "paradigm_troi_dat": (
            "**Tượng Thiên + Địa chi phối** → cảm xúc văn chương Thu Huệ về TRỜI ĐẤT: "
            "trăng, hoa sữa, cát biển (không phải sóng — cát là tượng ĐẤT, không phải nước). "
            "Hào 6 Bĩ: 'chí lớn cương quyết, có tài sắp đặt hơn người' → Thu Huệ làm PHIM từ "
            "văn học (đòi hỏi cái nhìn bao quát, tỉnh táo, từ trên xuống)."
        ),
        "source": "Xuân Cang p.520-531",
    },
    {
        "ten": "Đoàn Thị Lam Luyến",
        "sinh": "1951-07-18 (Tân Mão, mệnh Mộc tùng bách)",
        "tien_thien": "Lôi Thiên Đại Tráng",
        "ho_tien": "Địa Thiên Thái → Quải",
        "hau_thien": "Phong Lôi Ích",
        "ho_hau": "Sơn Địa Bác",
        "phuong_phap_match": (
            "Mệnh Mộc + quẻ Càn (Lôi Thiên Đại Tráng): 'Mộc gặp Càn → mơ mộng hão huyền, ít thực tế.' "
            "→ Giải thích thơ ĐTLL: 'thất vọng chán chường vì không tìm được tình yêu lý tưởng.'"
        ),
        "thien_nhien_trong_tho": (
            "ĐTLL có Lôi (sấm) + Thiên (trời) + Trạch (đầm) + Phong (gió) trong cấu trúc → "
            "rất nhạy cảm với SẤM CHỚP, GIÔNG GIÓ, MƯA. ÍT cảm xúc với ĐẤT (mầm cây, hoa). "
            "Khớp với 2 tập thơ 'Chồng Chị Chồng Em' + 'Châm Khói'."
        ),
        "source": "Xuân Cang p.533-541",
    },
]


def get_phuong_phap_summary() -> str:
    """Trả về tóm tắt phương pháp 7 bước."""
    lines = ["# Phương Pháp Đọc Chân Dung Hà Lạc — Xuân Cang Phần Ba\n"]
    for step in PHUONG_PHAP_7_BUOC:
        lines.append(f"## Bước {step['step']}: {step['title']}")
        lines.append(step["desc"])
        lines.append(f"\n_Ví dụ_: {step['vi_du']}\n")
    lines.append("\n## 3 mẹo tìm giờ sinh khi không biết\n")
    for m in MEO_TIM_GIO_SINH:
        lines.append(f"- {m}")
    return "\n".join(lines)


def get_case_study(ten: str) -> dict | None:
    """Lookup case study by name (substring match)."""
    for c in CASE_STUDIES_PHAN_BA:
        if ten.lower() in c["ten"].lower():
            return c
    return None


def get_paradigm_for_llm() -> dict[str, str]:
    """Paradigm constraints cho LLM khi luận giải sâu."""
    return PARADIGM_CHO_LLM_LUAN_GIAI
