"""Deep readings cho KMDG — per-element micro-readings + combinations.

Tách khỏi wiki.py để keep wiki.py modular. Chứa:
- MON_DEEP: 8 môn × tâm pháp / combo / người dùng / cấm kỵ
- TINH_DEEP: 9 tinh × tâm pháp / combo / mùa / khí
- THAN_DEEP: 8 thần × tâm pháp / ứng xử / chiến thuật
- CACH_CUC_DEEP: 10+ cách cục KEY với chi tiết áp dụng
- COMBO_LUAN_GIAI: 30+ combo Môn × Tinh × Thần tiêu biểu
- interpret_cell_deep(cell): luận sâu 1 cell trong bàn (cung + môn + tinh + thần)

Source: Đàm Liên Chương I phần IV-V + paradigm Iron Rule #4 đọc đồng dạng.
"""

from typing import Optional


# ─── 8 MÔN — micro-readings sâu ───
MON_DEEP = {
    "Khai": {
        "tam_phap_ung_xu": (
            "Khi gặp Khai môn: ĐI THẲNG, không quanh co. 'Tứ thông bát đạt' = "
            "tự nhiên thông suốt, anh KHÔNG cần force. Nếu anh thấy còn cản trở "
            "→ đó không phải Khai môn thực, có thể bị 'môn bách' (cung khắc môn)."
        ),
        "combo_voi_than": {
            "Trị Phù": "Khai + Trị Phù = ĐẠI CÁT KÉP — vua mở đường, đi đến đâu xấu xoá đến đó",
            "Cửu Thiên": "Khai + Cửu Thiên = vươn cao + mở rộng, tốt cho expansion lớn",
            "Cửu Địa": "Khai + Cửu Địa = mở để ẩn náu/lập căn cứ — tốt cho thiết lập lâu dài",
            "Lục Hợp": "Khai + Lục Hợp = mở giao tế, môi giới, partnership",
            "Thái Âm": "Khai + Thái Âm = mở việc kín đáo, không phô trương",
            "Câu Trần": "Khai + Câu Trần = mở nhưng cẩn thận kẻ đánh bất ngờ",
            "Chu Tước": "Khai + Chu Tước = mở dễ bị trộm tin tức, đề phòng mật thám",
            "Đằng Xà": "Khai + Đằng Xà = mở nhưng có ảo, dễ bị lừa kì quặc",
        },
        "nguoi_co_quy_dung": "CEO, founder, lãnh đạo expansion. Người mở rộng kinh doanh.",
        "cam_ky": "TANG LỄ. Không khai mở vào việc tang.",
        "cau_chu_co_dien": "「開門宜行 — 開門應期不遲疑」 (Khai môn nên đi, ứng kỳ không do dự)",
        "ngu_hanh_chi_tiet": (
            "Khai môn = Kim thần. Cát ở cung Khôn 2 + Cấn 8 (Thổ sinh Kim = Nghĩa). "
            "Hung ở cung Chấn 3 + Tốn 4 (Mộc bị Kim khắc = Kim khắc cung = Bức). "
            "Trung tính ở cung Khảm 1 (Kim sinh Thủy = Hoà — môn xuất khí cho cung)."
        ),
    },
    "Hưu": {
        "tam_phap_ung_xu": (
            "Khi gặp Hưu môn: SUM HỌP, không tranh đấu. 'Hưu' = nghỉ ngơi NHƯNG "
            "không phải bất động — là 'nghỉ để hợp'. Tốt cho meeting, đàm phán, "
            "hôn nhân, kinh doanh quan hệ."
        ),
        "combo_voi_than": {
            "Lục Hợp": "Hưu + Lục Hợp = HÔN NHÂN cát kép. Cũng tốt môi giới thương mại.",
            "Trị Phù": "Hưu + Trị Phù = sum họp với người trên, gặp quý nhân",
            "Thái Âm": "Hưu + Thái Âm = nghỉ ngơi kín, dưỡng sức, healing",
            "Cửu Thiên": "Hưu + Cửu Thiên = nghỉ để chuẩn bị bứt phá",
            "Cửu Địa": "Hưu + Cửu Địa = nghỉ ẩn náu, restore foundation",
            "Đằng Xà": "Hưu + Đằng Xà = nghỉ nhưng ác mộng, cẩn thận lừa giấc",
            "Chu Tước": "Hưu + Chu Tước = sum họp dễ bị tin xấu, thị phi",
            "Câu Trần": "Hưu + Câu Trần = sum họp dây dưa, khó dứt",
        },
        "nguoi_co_quy_dung": "Nhà ngoại giao, người làm marriage broker, family advisor, HR.",
        "cam_ky": "KHỞI BINH. Không Hưu khi cần phải tấn công nhanh.",
        "cau_chu_co_dien": "「休門宜求和 — 不宜爭戰」 (Hưu môn nên cầu hòa, không nên tranh)",
        "ngu_hanh_chi_tiet": (
            "Hưu môn = Thủy thần. Cát ở cung Chấn 3 + Tốn 4 (Thủy sinh Mộc = Hoà). "
            "Hung ở cung Ly 9 (Thủy bị Hỏa khắc = Hung, Đàm Liên page 39). "
            "Cát ở Khảm 1 (đồng Thủy = Vượng)."
        ),
    },
    "Sinh": {
        "tam_phap_ung_xu": (
            "Khi gặp Sinh môn: KHỞI ĐẦU, gieo hạt. 'Sinh' = sinh sôi. Tốt cho "
            "việc cần TĂNG TRƯỞNG: trồng cây, mở shop, kết hôn (con cái), "
            "tuyển nhân viên, KHỞI NGHIỆP."
        ),
        "combo_voi_than": {
            "Cửu Thiên": "Sinh + Cửu Thiên = KHỞI NGHIỆP đại cát — gieo to gặt to",
            "Trị Phù": "Sinh + Trị Phù = khởi sự có quý nhân bảo trợ",
            "Lục Hợp": "Sinh + Lục Hợp = khởi việc hợp tác, joint venture",
            "Cửu Địa": "Sinh + Cửu Địa = khởi ngầm, build foundation lâu dài",
            "Thái Âm": "Sinh + Thái Âm = khởi việc kín, không công bố",
            "Câu Trần": "Sinh + Câu Trần = khởi sự bị ràng buộc, contract dây dưa",
            "Chu Tước": "Sinh + Chu Tước = khởi sự lộ tin trước thời điểm",
            "Đằng Xà": "Sinh + Đằng Xà = khởi sự dễ ảo, giấc mộng không thực",
        },
        "nguoi_co_quy_dung": "Khởi nghiệp, người làm nông, sản xuất, builder, người muốn có con.",
        "cam_ky": "TANG LỄ. Sinh đối ngược với Tử.",
        "cau_chu_co_dien": "「生門大利 — 求財有得」 (Sinh môn đại lợi, cầu tài có được)",
        "ngu_hanh_chi_tiet": (
            "Sinh môn = Thổ thần. Cát ở cung Ly 9 (Hỏa sinh Thổ = Nghĩa). "
            "Hung ở cung Khảm 1 (Thủy bị Thổ khắc — môn khắc cung, Đàm Liên page 39). "
            "Hoà ở cung Càn 6 + Đoài 7 (Thổ sinh Kim)."
        ),
    },
    "Thương": {
        "tam_phap_ung_xu": (
            "Khi gặp Thương môn: DỪNG xuất hành. NHƯNG paradox — TỐT cho đối kháng "
            "trực diện: đòi nợ, kiện tụng, bắt tội phạm, debate. 'Thương' = tổn "
            "thương — anh là người gây tổn thương (đối kháng), không bị tổn thương "
            "(thụ động)."
        ),
        "combo_voi_than": {
            "Cửu Thiên": "Thương + Cửu Thiên = chiến đấu chính nghĩa, danh tiếng qua xung đột",
            "Câu Trần": "Thương + Câu Trần = HUNG kép — kiện tụng dây dưa, hình thương",
            "Chu Tước": "Thương + Chu Tước = tổn thương bị thị phi, miệng tiếng xấu",
            "Trị Phù": "Thương + Trị Phù = vua trừng phạt, hình pháp chính nghĩa",
            "Lục Hợp": "Thương + Lục Hợp = hòa giải sau xung đột, mediation",
            "Cửu Địa": "Thương + Cửu Địa = tổn thương ngầm, không phô",
            "Thái Âm": "Thương + Thái Âm = tổn thương kín, ẩn ức",
            "Đằng Xà": "Thương + Đằng Xà = tổn thương kì lạ, ác mộng thật",
        },
        "nguoi_co_quy_dung": "Cảnh sát, luật sư, người đòi nợ, judge, debt collector, debater.",
        "cam_ky": "ĐI XA, KẾT HÔN, XÂY DỰNG mới.",
        "cau_chu_co_dien": "「傷門宜捕逃 — 不宜遠行」 (Thương môn nên bắt người bỏ trốn, không nên đi xa)",
        "ngu_hanh_chi_tiet": (
            "Thương môn = Mộc thần. Đại hung ở cung Khôn 2 + Cấn 8 (Mộc khắc Thổ "
            "= Bức, Đàm Liên page 39). Cát ở Ly 9 (Mộc sinh Hỏa = Hoà). "
            "Vượng ở Chấn 3 + Tốn 4 (đồng Mộc)."
        ),
    },
    "Đỗ": {
        "tam_phap_ung_xu": (
            "Khi gặp Đỗ môn: ĐÓNG KÍN, bảo mật. 'Đỗ' = chặn. Tốt cho ẩn náu, "
            "thiền, học sâu, bảo vệ thông tin, ẩn quân tướng. Đàm Liên: 'gặp "
            "quý nhân phù trợ' khi Đỗ."
        ),
        "combo_voi_than": {
            "Cửu Địa": "Đỗ + Cửu Địa = ẨN NÁU đại cát (cách cục Địa Giả)",
            "Thái Âm": "Đỗ + Thái Âm = bảo mật kép, mưu sau lưng",
            "Trị Phù": "Đỗ + Trị Phù = đóng cửa thành chờ thời",
            "Cửu Thiên": "Đỗ + Cửu Thiên = ẩn để chuẩn bị bứt phá",
            "Lục Hợp": "Đỗ + Lục Hợp = giao tế kín, bí mật",
            "Câu Trần": "Đỗ + Câu Trần = bị bao vây, khó thoát",
            "Chu Tước": "Đỗ + Chu Tước = tin xấu lan kín, đề phòng leak",
            "Đằng Xà": "Đỗ + Đằng Xà = ẩn kín nhưng ác mộng",
        },
        "nguoi_co_quy_dung": "Spy, advisor mưu kế, security expert, monk, người nghiên cứu kín.",
        "cam_ky": "PHÔ TRƯƠNG, công bố lớn.",
        "cau_chu_co_dien": "「杜門宜隱跡 — 不宜公開」 (Đỗ môn nên ẩn dấu vết, không nên công khai)",
        "ngu_hanh_chi_tiet": (
            "Đỗ môn = Mộc thần. Đại hung ở Khôn 2 + Cấn 8 (Mộc khắc Thổ). "
            "Cát ở Ly 9 (Mộc sinh Hỏa). Vượng ở Chấn + Tốn."
        ),
    },
    "Cảnh": {
        "tam_phap_ung_xu": (
            "Khi gặp Cảnh môn: PHÔ TRƯƠNG ngắn hạn. 'Cảnh' = sáng, view. Tốt cho "
            "thi đấu trò chơi, presentation, biểu diễn ngắn. Đàm Liên gọi 'bình "
            "môn' — không cát không hung mạnh, phấn chấn nhưng không bền."
        ),
        "combo_voi_than": {
            "Cửu Thiên": "Cảnh + Cửu Thiên = ĐẠI GIẢ — dâng kế sách, gặp quý nhân, kết giao ước",
            "Lục Hợp": "Cảnh + Lục Hợp = ký kết hợp đồng, signing ceremony",
            "Trị Phù": "Cảnh + Trị Phù = phát lệnh chính thức, ban hành",
            "Thái Âm": "Cảnh + Thái Âm = phô diễn kín, private show",
            "Cửu Địa": "Cảnh + Cửu Địa = phô nhưng có sức bền nhẹ",
            "Câu Trần": "Cảnh + Câu Trần = phô bị kiện tụng ràng buộc",
            "Chu Tước": "Cảnh + Chu Tước = phô bị thị phi, miệng tiếng",
            "Đằng Xà": "Cảnh + Đằng Xà = phô diễn ảo, false show",
        },
        "nguoi_co_quy_dung": "Athletes, performers, public speakers, contestant, marketing.",
        "cam_ky": "CỐ THỦ LÂU DÀI (Cảnh không bền).",
        "cau_chu_co_dien": "「景門宜競技 — 短期勝利」 (Cảnh môn nên thi đấu, thắng ngắn hạn)",
        "ngu_hanh_chi_tiet": (
            "Cảnh môn = Hỏa thần. Tương đối xấu ở Càn 6 + Đoài 7 (Hỏa khắc Kim "
            "= Bức, Đàm Liên page 39). Cát ở Khôn 2 + Cấn 8 (Hỏa sinh Thổ = Nghĩa)."
        ),
    },
    "Tử": {
        "tam_phap_ung_xu": (
            "Khi gặp Tử môn: KẾT THÚC, không khởi mới. 'Tử' = chết, ending. ĐẠI "
            "HUNG cho mọi việc khởi NHƯNG TỐT cho tang lễ + tu mộ. Đây là môn "
            "DUY NHẤT có usage ngược paradigm: hung-cho-sống = cát-cho-chết."
        ),
        "combo_voi_than": {
            "Cửu Địa": "Tử + Cửu Địa = QUY GIẢ — sửa mộ, đi săn cát",
            "Thái Âm": "Tử + Thái Âm = an táng kín, lễ tang riêng tư",
            "Trị Phù": "Tử + Trị Phù = vua chủ tang lễ, lễ chính thức",
            "Lục Hợp": "Tử + Lục Hợp = họp gia đình tang lễ, đoàn tụ điếu",
            "Cửu Thiên": "Tử + Cửu Thiên = tang lễ vĩ nhân, state funeral",
            "Câu Trần": "Tử + Câu Trần = tử kiện tụng, di chúc tranh chấp",
            "Chu Tước": "Tử + Chu Tước = tử bị thị phi, scandal",
            "Đằng Xà": "Tử + Đằng Xà = tử kì lạ, không yên giấc",
        },
        "nguoi_co_quy_dung": "Tang lễ services, mortician, di chúc lawyer, archeologist (đào quá khứ).",
        "cam_ky": "KHỞI SỰ MỚI tuyệt đối. Xuất hành cho việc lớn.",
        "cau_chu_co_dien": "「死門宜葬埋 — 不宜出行」 (Tử môn nên an táng, không nên xuất hành)",
        "ngu_hanh_chi_tiet": (
            "Tử môn = Thổ thần. Xấu nhất ở Khảm 1 (Thổ khắc Thủy, Đàm Liên page 39). "
            "Cát ở Càn 6 + Đoài 7 (Thổ sinh Kim = Nghĩa). Vượng ở Khôn 2 + Cấn 8."
        ),
    },
    "Kinh": {
        "tam_phap_ung_xu": (
            "Khi gặp Kinh môn: GIẬT MÌNH, cẩn thận. 'Kinh' = kinh hoàng. Hung cho "
            "xuất hành NHƯNG paradox — TỐT cho TRUY ĐUỔI: tìm đồ mất, bắt tội "
            "phạm, lần dấu vết. Đàm Liên: 'mọi việc xảy ra kì lạ bất ngờ'."
        ),
        "combo_voi_than": {
            "Cửu Thiên": "Kinh + Cửu Thiên = NHÂN GIẢ — bắt bớ, tù đày",
            "Câu Trần": "Kinh + Câu Trần = kinh sợ + bị bao vây, đại hung",
            "Chu Tước": "Kinh + Chu Tước = tin xấu giật mình, scandal đột",
            "Trị Phù": "Kinh + Trị Phù = vua giật mình, cứu cấp khẩn",
            "Lục Hợp": "Kinh + Lục Hợp = giật mình giải hòa, đột nhập kín",
            "Thái Âm": "Kinh + Thái Âm = kinh sợ ẩn trong, paranoid",
            "Cửu Địa": "Kinh + Cửu Địa = kinh nhưng ẩn được, escape",
            "Đằng Xà": "Kinh + Đằng Xà = ác mộng thực sự, hoảng loạn",
        },
        "nguoi_co_quy_dung": "Detective, tracker, lost-and-found, emergency responder, alarm.",
        "cam_ky": "ĐI XA, làm việc ở xa.",
        "cau_chu_co_dien": "「驚門宜捕亡 — 出行不利」 (Kinh môn nên truy đuổi người trốn, xuất hành bất lợi)",
        "ngu_hanh_chi_tiet": (
            "Kinh môn = Kim thần. Hung cao ở Chấn 3 + Tốn 4 (Mộc khắc Kim = Bức, "
            "Đàm Liên page 40). Cát ở Khôn 2 + Cấn 8 (Thổ sinh Kim = Nghĩa). "
            "Vượng ở Càn 6 + Đoài 7."
        ),
    },
}


# ─── 9 TINH — micro-readings sâu ───
TINH_DEEP = {
    "Thiên Bồng": {
        "tam_phap": (
            "Sao THỦY TẶC. Khi gặp Thiên Bồng: cảnh giác trộm cướp, dâm dục, "
            "mưu kế đen. NHƯNG paradox — Sinh môn + Bính Kỳ/Đinh Kỳ + mùa Xuân/Hè "
            "= có thể làm việc lớn. Cấu trúc 'thủy đen có thể uống nếu lọc kỹ'."
        ),
        "combo_voi_mon": {
            "Sinh": "Thiên Bồng + Sinh môn = paradox ngoại lệ (cần Bính/Đinh Kỳ + mùa hè)",
            "Tử": "Thiên Bồng + Tử = ĐẠI HUNG kép, thủy tặc tới ngày chết",
            "Khai": "Thiên Bồng + Khai = mở đường nhưng có trộm, đề phòng",
            "Hưu": "Thiên Bồng + Hưu = nghỉ kín, thủy tặc không tới",
            "Cảnh": "Thiên Bồng + Cảnh = phô trương dễ bị trộm",
            "Đỗ": "Thiên Bồng + Đỗ = đóng kín đề phòng trộm — tốt",
            "Kinh": "Thiên Bồng + Kinh = kinh sợ trộm, paranoid",
            "Thương": "Thiên Bồng + Thương = bị trộm + tổn thương, đại hung",
        },
        "tinh_chuyen_mon": (
            "Sao cốt: đầu Bắc Đẩu (Thủy). Đại hung tinh số 1 trong Cửu Tinh. Tuy "
            "nhiên trong Huyền Không Phi Tinh, Nhất Bạch (= Bồng) lại là cát tinh "
            "trong vận 1. Phụ thuộc context."
        ),
        "mua_chi_tiet": "Xuân (Mộc) + Hạ (Hỏa) → may (Thủy nuôi Mộc, sinh Hỏa); Thu (Kim) + Đông (Thủy) → xấu (Kim sinh Thủy quá vượng, đông đồng Thủy)",
    },
    "Thiên Nhậm": {
        "tam_phap": (
            "Sao MAY MẮN tiểu cát. Khi gặp Thiên Nhậm: bảo trì + đảm nhận. Tốt cho "
            "việc lâu dài, tích lũy, kết hôn, cầu danh, xây mồ mả. 'Nhậm' = "
            "đảm nhiệm = stable + reliable."
        ),
        "combo_voi_mon": {
            "Sinh": "Thiên Nhậm + Sinh = khởi đầu bền vững, đại cát kép",
            "Hưu": "Thiên Nhậm + Hưu = sum họp gia đình, hôn nhân chắc chắn",
            "Khai": "Thiên Nhậm + Khai = mở việc lâu dài, infrastructure",
            "Cảnh": "Thiên Nhậm + Cảnh = phô diễn có sức bền",
            "Thương": "Thiên Nhậm + Thương = chịu tổn thương nhưng đảm nhiệm",
            "Đỗ": "Thiên Nhậm + Đỗ = đóng kín để bảo trì",
            "Tử": "Thiên Nhậm + Tử = bảo trì tang lễ, lo việc tang dài hạn",
            "Kinh": "Thiên Nhậm + Kinh = kinh sợ nhưng đảm nhiệm, hold ground",
        },
        "tinh_chuyen_mon": "Sao Thổ. Đại diện cho LÂU DÀI + ĐẢM NHẬN. Trong Huyền Không = Bát Bạch (cát).",
        "mua_chi_tiet": "Phù hợp mọi mùa (Thổ ổn).",
    },
    "Thiên Xung": {
        "tam_phap": (
            "Sao VÕ SĨ tiểu cát. 'Xung' = kích phạt, lôi tê. Tốt cho người võ, "
            "XUẤT QUÂN, tranh đấu chính nghĩa. KHÔNG NÊN kết hôn, xây dựng, "
            "kinh doanh (Đàm Liên page 42: 'đều gặp tai họa')."
        ),
        "combo_voi_mon": {
            "Thương": "Thiên Xung + Thương = chiến đấu trực diện, võ sĩ tham chiến",
            "Kinh": "Thiên Xung + Kinh = tấn công đột ngột",
            "Khai": "Thiên Xung + Khai = mở đường bằng vũ lực",
            "Sinh": "Thiên Xung + Sinh = khởi sự bằng đấu tranh (startup chiến)",
            "Hưu": "Thiên Xung + Hưu = nghỉ giữa trận, recovery",
            "Đỗ": "Thiên Xung + Đỗ = võ sĩ ẩn náu, ninja",
            "Cảnh": "Thiên Xung + Cảnh = thi đấu thể thao, võ thi",
            "Tử": "Thiên Xung + Tử = chết trong chiến, hung",
        },
        "tinh_chuyen_mon": "Sao Mộc. Đại diện cho XUNG ĐỘT chính nghĩa.",
        "mua_chi_tiet": "Xuân (đồng Mộc) → vượng; Thu (Kim khắc Mộc) → suy",
    },
    "Thiên Phụ": {
        "tam_phap": (
            "Sao ĐẠI CÁT — vì vạn vật, vì dân chúng. Tốt cho xuất hành, tu sửa "
            "mồ mả, RẤT DỄ THĂNG QUAN TIẾN CHỨC, di dời, kết hôn, mời khách. "
            "Đàm Liên: 'vạn sự cát tường'."
        ),
        "combo_voi_mon": {
            "Khai": "Thiên Phụ + Khai = ĐẠI CÁT KÉP — xuất hành, expand toàn diện",
            "Sinh": "Thiên Phụ + Sinh = khởi nghiệp có quý nhân phù trợ",
            "Hưu": "Thiên Phụ + Hưu = sum họp + phù trợ = hôn nhân đại cát",
            "Cảnh": "Thiên Phụ + Cảnh = phô diễn + công nhận, awards",
            "Tử": "Thiên Phụ + Tử = tu mộ + phù trợ tổ tiên",
            "Thương": "Thiên Phụ + Thương = phù trợ qua tranh đấu",
            "Đỗ": "Thiên Phụ + Đỗ = phù trợ ẩn, mentor kín",
            "Kinh": "Thiên Phụ + Kinh = phù trợ trong khủng hoảng",
        },
        "tinh_chuyen_mon": "Sao Mộc đại cát. Trong Huyền Không = Tứ Lục (cát).",
        "mua_chi_tiet": "Xuân + Đông tốt; Thu (Kim khắc) suy nhẹ",
    },
    "Thiên Cầm": {
        "tam_phap": (
            "Sao ĐẠI CÁT — trung tâm. Đi cùng Trị Phù (luôn ở Trung cung khi bàn "
            "ổn). Tốt cho ĐI XA, làm ăn buôn bán, gặp quý nhân, tu sửa mồ mả. "
            "Đàm Liên: 'mang về nhiều lợi lộc'."
        ),
        "combo_voi_mon": {
            "Khai": "Thiên Cầm + Khai = đi xa mở rộng, expansion cát",
            "Sinh": "Thiên Cầm + Sinh = khởi sự trung tâm, headquarter",
            "Hưu": "Thiên Cầm + Hưu = sum họp trung tâm, family core",
            "Cảnh": "Thiên Cầm + Cảnh = phô diễn trung tâm, conference",
            "Thương": "Thiên Cầm + Thương = trung tâm bị tổn thương, hung",
            "Đỗ": "Thiên Cầm + Đỗ = trung tâm đóng kín",
            "Tử": "Thiên Cầm + Tử = trung tâm chết, hung lớn",
            "Kinh": "Thiên Cầm + Kinh = trung tâm giật mình, panic core",
        },
        "tinh_chuyen_mon": "Sao Thổ trung cung. Vô-vi mạnh — không di chuyển. Trong Huyền Không = Ngũ Hoàng.",
        "mua_chi_tiet": "Mọi mùa ổn (trung cung)",
    },
    "Thiên Tâm": {
        "tam_phap": (
            "Sao ĐẠI CÁT — Y DƯỢC. Đàm Liên: 'gặp được tiên nhân cho thuốc quý'. "
            "Tốt cho CHỮA BỆNH NHANH CHÓNG, sức khỏe, nghiên cứu sâu. VẠN SỰ "
            "MAY MẮN. 'Tâm' = tim, trung tâm tinh thần."
        ),
        "combo_voi_mon": {
            "Hưu": "Thiên Tâm + Hưu = HƯU TRÁ — uống thuốc trị bệnh",
            "Sinh": "Thiên Tâm + Sinh = khởi sự y dược, mở phòng khám",
            "Khai": "Thiên Tâm + Khai = mở đường y dược, expand healing",
            "Đỗ": "Thiên Tâm + Đỗ = y dược kín, alternative medicine",
            "Cảnh": "Thiên Tâm + Cảnh = phô y dược, hospital launch",
            "Thương": "Thiên Tâm + Thương = chữa qua phẫu thuật, đau để khỏi",
            "Tử": "Thiên Tâm + Tử = y dược cuối đời, palliative care",
            "Kinh": "Thiên Tâm + Kinh = cấp cứu y khoa, ER",
        },
        "tinh_chuyen_mon": "Sao Kim. Y dược + tim mạch. Trong Huyền Không = Lục Bạch (cát).",
        "mua_chi_tiet": "Đông/Thu (đồng Kim hoặc Thủy sinh Kim) may; Xuân/Hạ (Mộc khắc Kim, Hỏa thiêu Kim) xấu",
    },
    "Thiên Trụ": {
        "tam_phap": (
            "Sao TIỂU HUNG. Đàm Liên dứt khoát: 'KHÔNG nên xuất hành hay làm "
            "kinh doanh. Làm kinh doanh LẬP TỨC GẶP XẤU. TẤT CẢ MỌI VIỆC ĐỀU "
            "KHÔNG THUẬN LỢI.' 'Trụ' = cột, cố thủ — nhưng cố thủ trong tình "
            "huống không lợi."
        ),
        "combo_voi_mon": {
            "Đỗ": "Thiên Trụ + Đỗ = cố thủ kín, defensive position",
            "Hưu": "Thiên Trụ + Hưu = nghỉ tại chỗ, không động",
            "Khai": "Thiên Trụ + Khai = mở nhưng bị cản, frustration",
            "Sinh": "Thiên Trụ + Sinh = khởi sự bị stuck",
            "Cảnh": "Thiên Trụ + Cảnh = phô trương bị nghẽn",
            "Thương": "Thiên Trụ + Thương = bị thương + cố thủ → hung",
            "Tử": "Thiên Trụ + Tử = chết tại cột, cố thủ đến chết",
            "Kinh": "Thiên Trụ + Kinh = kinh sợ + cố thủ = paralysis",
        },
        "tinh_chuyen_mon": "Sao Kim hung. Trong Huyền Không = Thất Xích (hung trong vận sai).",
        "mua_chi_tiet": "Mọi mùa đều suy nhẹ (sao hung)",
    },
    "Thiên Anh": {
        "tam_phap": (
            "Sao TIỂU HUNG. Đàm Liên: 'KHÔNG nên kết hôn, đi xa, di dời. Cầu danh, "
            "cầu tài đều KHÔNG có kết quả. Đây là SAO XẤU.' 'Anh' = rực rỡ — "
            "nhưng rực rỡ giả, hư danh, dễ bị hỏa thiêu."
        ),
        "combo_voi_mon": {
            "Cảnh": "Thiên Anh + Cảnh = phô trương rực rỡ giả tạo",
            "Khai": "Thiên Anh + Khai = mở đường nhưng hư danh",
            "Sinh": "Thiên Anh + Sinh = khởi sự với danh hư",
            "Hưu": "Thiên Anh + Hưu = nghỉ + hư danh, kiệt sức",
            "Tử": "Thiên Anh + Tử = ĐẠI HUNG — danh tan + chết, scandal đến chết",
            "Đỗ": "Thiên Anh + Đỗ = ẩn nhưng vẫn lộ, không kín được",
            "Thương": "Thiên Anh + Thương = danh tiếng qua tổn thương, controversial",
            "Kinh": "Thiên Anh + Kinh = scandal kinh hoàng",
        },
        "tinh_chuyen_mon": "Sao Hỏa hung. Trong Huyền Không = Cửu Tử (tốt vận 9, xấu khác vận).",
        "mua_chi_tiet": "Hạ (đồng Hỏa) vượng nhưng vượng hung; Thu/Đông suy",
    },
    "Thiên Nhuế": {
        "tam_phap": (
            "Sao ĐẠI HUNG — BỆNH TINH. Đàm Liên: 'không nên xuất hành, nếu xuất "
            "hành thì mọi việc đều thất bại'. PARADOX: 'dễ kết giao bạn bè, thầy "
            "cô NHƯNG không nên kết hôn, di dời, tố tụng xây dựng. DÙ ĐẮC KÌ ĐẮC "
            "MÔN cũng khó may.'"
        ),
        "combo_voi_mon": {
            "Đỗ": "Thiên Nhuế + Đỗ = ẩn bệnh, không thể chữa",
            "Hưu": "Thiên Nhuế + Hưu = nghỉ vì bệnh, sick leave",
            "Tử": "Thiên Nhuế + Tử = chết vì bệnh, tang bệnh",
            "Khai": "Thiên Nhuế + Khai = mở nhưng bệnh tật, expansion đau",
            "Sinh": "Thiên Nhuế + Sinh = sinh con bệnh tật",
            "Cảnh": "Thiên Nhuế + Cảnh = phô bệnh, hospital visit",
            "Thương": "Thiên Nhuế + Thương = bệnh + tai nạn, multi-hurt",
            "Kinh": "Thiên Nhuế + Kinh = cấp cứu bệnh, ER critical",
        },
        "tinh_chuyen_mon": "Sao Thổ hung — bệnh tinh đầu. Trong Huyền Không = Nhị Hắc (sao bệnh).",
        "mua_chi_tiet": "Đông/Thu may (Thủy/Kim sinh Thổ); Hạ/Xuân xấu (Hỏa sinh Thổ vượng, Mộc khắc Thổ)",
    },
}


# ─── 8 THẦN — micro-readings sâu ───
THAN_DEEP = {
    "Trị Phù": {
        "tam_phap_ung_xu": (
            "Khi gặp Trị Phù: KÍCH HOẠT vận khí. Trị Phù là chủ tể — đi đến đâu "
            "xấu xoá đến đó. 'Có việc gấp xuất phát từ đây' = TRỤC CỨU CẤP. "
            "Hành động: face hướng Trị Phù khi gặp khủng hoảng."
        ),
        "chien_thuat": "Cứu cấp, vua trừng phạt, kích hoạt authority",
        "cam_ky": "Không có (Trị Phù toàn cát)",
        "modern_application": (
            "Modern: 'Trị Phù' = guardian angel pattern. Khi gặp critical incident, "
            "ngồi face hướng Trị Phù → tâm tĩnh, decision rõ. Trong company: Trị "
            "Phù = founder/CEO authority — chính sách 'có việc gấp report thẳng "
            "lên'."
        ),
    },
    "Đằng Xà": {
        "tam_phap_ung_xu": (
            "Khi gặp Đằng Xà: ĐỀ PHÒNG kì quặc, ác mộng, lừa. 'Đằng Xà' = rắn "
            "bay — biến hoá vô lường. Hành động: đừng tin lời ngọt + giấc mộng + "
            "promise quá đẹp."
        ),
        "chien_thuat": "Phòng tin đồn, lừa đảo, ảo tưởng",
        "cam_ky": "Tin lời người lạ quá nhanh, decision mơ hồ",
        "modern_application": (
            "Modern: 'Đằng Xà' = scam pattern. Đề phòng phishing, fake promises, "
            "rumors. Trong startup: không trust lời 'investor sẽ rót' đến khi có "
            "term sheet ký. Bám fact, không bám lời."
        ),
    },
    "Thái Âm": {
        "tam_phap_ung_xu": (
            "Khi gặp Thái Âm: ẨN, kín đáo, phù hộ. 'Thái Âm' = mặt trăng + bảo "
            "vệ kín. Đàm Liên: 'đóng cửa thành cho quân lính nghỉ ngơi'. Hành "
            "động: KHÔNG phô trương, mưu sau lưng, dưỡng sức."
        ),
        "chien_thuat": "Ẩn náu, mưu kín, dưỡng quân, plan B",
        "cam_ky": "Phô diễn, công khai sớm",
        "modern_application": (
            "Modern: 'Thái Âm' = stealth mode pattern. Founder phase 'building "
            "in stealth' — không announce trước khi product chín. Strategic "
            "patience. Cũng phù hợp meditation/healing."
        ),
    },
    "Lục Hợp": {
        "tam_phap_ung_xu": (
            "Khi gặp Lục Hợp: HÒA HỢP, môi giới. 'Lục Hợp' = thần bảo vệ ôn hòa. "
            "Đàm Liên: 'giới thiệu người môi giới hôn nhân, thương mại, kết hôn, "
            "kết giao bạn bè'. Hành động: kết nối, network, mediation."
        ),
        "chien_thuat": "Mediation, hôn nhân, joint venture, partnership",
        "cam_ky": "Xung đột trực diện, debate hard",
        "modern_application": (
            "Modern: 'Lục Hợp' = networking pattern. Hướng có Lục Hợp = nơi tốt "
            "để gặp gỡ business partner, kết hôn, ký hợp đồng. Founder: hướng "
            "Lục Hợp = chỗ meet investor / co-founder."
        ),
    },
    "Câu Trần": {
        "tam_phap_ung_xu": (
            "Khi gặp Câu Trần: ĐỀ PHÒNG đánh bất ngờ. 'Câu Trần' = Bạch Hổ — "
            "thần xấu. Đàm Liên: 'đề phòng kẻ địch đánh bất ngờ'. Hành động: "
            "tăng strategic alert, không relax."
        ),
        "chien_thuat": "Defense, recon, threat assessment",
        "cam_ky": "Lơ là cảnh giác, trust blindly",
        "modern_application": (
            "Modern: 'Câu Trần' = competitive threat pattern. Hướng Câu Trần = "
            "nơi competitor có thể đánh bất ngờ. Founder: scan competitive "
            "landscape monthly. Security audit thường xuyên."
        ),
    },
    "Chu Tước": {
        "tam_phap_ung_xu": (
            "Khi gặp Chu Tước: ĐỀ PHÒNG TRỘM TIN. 'Chu Tước' = thần cướp bóc, "
            "âm mưu hại. Đàm Liên: 'đề phòng mật thám, trộm, mất mát'. Hành "
            "động: bảo mật info, không tin người mới."
        ),
        "chien_thuat": "Infosec, data protection, NDA, encrypted comm",
        "cam_ky": "Lộ secrets, public bragging",
        "modern_application": (
            "Modern: 'Chu Tước' = data breach + IP theft pattern. Hướng Chu "
            "Tước = nơi data có thể leak. Founder: NDA cho mọi conversations "
            "với potential partners. Encryption mọi sensitive comm."
        ),
    },
    "Cửu Địa": {
        "tam_phap_ung_xu": (
            "Khi gặp Cửu Địa: ẨN NÁU, build foundation. 'Cửu Địa' = mẹ vạn vật, "
            "kiên cố, tính tĩnh. Đàm Liên: 'phòng thủ binh tướng'. Hành động: "
            "consolidate, secure base, deep work."
        ),
        "chien_thuat": "Foundation building, defensive consolidation, deep work",
        "cam_ky": "Expansion mạo hiểm, surface-level work",
        "modern_application": (
            "Modern: 'Cửu Địa' = moat-building pattern. Hướng Cửu Địa = nơi "
            "build defensible advantage (IP, brand, network). Founder phase "
            "'9 nữ' (deep work) thay vì 'launching'."
        ),
    },
    "Cửu Thiên": {
        "tam_phap_ung_xu": (
            "Khi gặp Cửu Thiên: VƯƠN CAO, tiến quân. 'Cửu Thiên' = cha vạn vật, "
            "hùng dũng, tính động. Đàm Liên: 'sắp xếp binh lính chiến đấu'. "
            "Hành động: bứt phá, đi xa, launch lớn."
        ),
        "chien_thuat": "Expansion, launch, scaling, conquest",
        "cam_ky": "Cố thủ, retreat, ẩn náu",
        "modern_application": (
            "Modern: 'Cửu Thiên' = growth + launch pattern. Hướng Cửu Thiên = "
            "nơi expand. Founder phase 'rocket ship' — series A/B, "
            "international expansion, M&A."
        ),
    },
}


# ─── 30+ COMBO LUẬN GIẢI — Môn × Tinh × Thần ───
# Triple combinations đặc biệt (rare patterns) từ Đàm Liên + tradition
COMBO_LUAN_GIAI = {
    # ════════ TRIPLE CÁT ════════
    "Khai_TrieuPhu_CuuThien": {
        "name": "Khai môn + Thiên Phụ + Cửu Thiên",
        "loai": "đại cát kép",
        "luan": "MỞ ĐƯỜNG + PHÙ TRỢ + VƯƠN CAO. Tổ hợp cát nhất KMDG cho expansion. "
                "Trong KMDG quân sự = 'thần tướng đại tiến'. Modern: founder launch "
                "globally với mentor support + team strong.",
        "khi_dung": "Launch lớn, IPO, international expansion, conquest",
    },
    "Sinh_ThienTam_LucHop": {
        "name": "Sinh môn + Thiên Tâm + Lục Hợp",
        "loai": "đại cát",
        "luan": "KHỞI ĐẦU + Y DƯỢC + HÒA HỢP. Hưu Trá variant — 'uống thuốc trị "
                "bệnh' (Đàm Liên page 45). Tốt cho lập practice y học, health "
                "service. Modern: telemedicine startup.",
        "khi_dung": "Khởi nghiệp y tế, health/wellness business, chữa bệnh",
    },
    "Hưu_ThienNham_LucHop": {
        "name": "Hưu môn + Thiên Nhậm + Lục Hợp",
        "loai": "đại cát",
        "luan": "SUM HỌP + LÂU DÀI + HÒA HỢP. Cấu trúc HÔN NHÂN đại cát. Hôn nhân "
                "có cả 3: sum họp (Hưu) + bền vững (Nhậm) + môi giới hòa hợp (Lục Hợp).",
        "khi_dung": "Kết hôn, anniversary, family gathering quan trọng",
    },
    "Khai_ThienCam_TriPhu": {
        "name": "Khai môn + Thiên Cầm + Trị Phù",
        "loai": "đại cát kép",
        "luan": "MỞ ĐƯỜNG + TRUNG TÂM + CHỦ TỂ. 'Thanh Long Hồi Thủ' tương tự — "
                "trăm sự bình an. Trị Phù tại Trung cung là cấu trúc mạnh nhất.",
        "khi_dung": "Sáng lập headquarter, opening ceremony lớn",
    },
    "Canh_ThienPhu_CuuThien": {
        "name": "Cảnh môn + Thiên Phụ + Cửu Thiên",
        "loai": "đại cát",
        "luan": "PHÔ TRƯƠNG + PHÙ TRỢ + VƯƠN CAO. 'Đại Giả' canonical — "
                "'gặp quý nhân, dâng kế sách, phát lệnh, kết giao ước'. Tốt cho "
                "presentation, signing, public speaking lớn.",
        "khi_dung": "Pitch investor, keynote, ký hợp đồng quan trọng",
    },
    "Do_ThienNham_CuuDia": {
        "name": "Đỗ môn + Thiên Nhậm + Cửu Địa",
        "loai": "cát",
        "luan": "ĐÓNG KÍN + LÂU DÀI + ẨN NÁU. 'Địa Giả' canonical — 'ẩn mình "
                "lánh nạn, thăm dò, điều tra'. Tốt cho R&D phase, stealth mode "
                "startup, deep research.",
        "khi_dung": "Startup stealth, deep research, intelligence gathering",
    },
    "Khai_Bính_Ất": {
        "name": "Khai môn + Thiên Bàn Bính + Địa Bàn Ất",
        "loai": "đại cát hiếm",
        "luan": "Khai + 2 Tam Kỳ kề nhau (Bính trên Thiên + Ất dưới Địa). Cấu "
                "trúc 'ÁNH SÁNG ĐÔI mở cửa'. Cực hiếm gặp. Tốt cho khoảnh khắc "
                "anh muốn TỎA SÁNG ĐẶC THÙ.",
        "khi_dung": "Personal branding launch, ra mắt cá nhân, public reveal",
    },

    # ════════ TRIPLE HUNG ════════
    "Tu_ThienAnh_DangXa": {
        "name": "Tử môn + Thiên Anh + Đằng Xà",
        "loai": "đại hung kép",
        "luan": "CHẾT + HƯ DANH + ẢO TƯỞNG. Tổ hợp HUNG nhất KMDG cho lập "
                "nghiệp. 'Danh tan + chết + lừa'. Modern: scam project, dự án "
                "ảo, false hope. Tuyệt đối tránh khởi sự.",
        "khi_dung": "(TUYỆT ĐỐI TRÁNH lập nghiệp / kết hôn / di dời)",
    },
    "Thuong_ThienBong_CauTran": {
        "name": "Thương môn + Thiên Bồng + Câu Trần",
        "loai": "đại hung",
        "luan": "TỔN THƯƠNG + THỦY TẶC + ĐÁNH BẤT NGỜ. Cấu trúc 'bị cướp + bị "
                "đánh + dây dưa kiện'. Modern: ransomware attack + lawsuit. "
                "Tuyệt đối phòng thủ, không mở rộng.",
        "khi_dung": "(TUYỆT ĐỐI phòng thủ, không expansion)",
    },
    "Kinh_ThienNhue_ChuTuoc": {
        "name": "Kinh môn + Thiên Nhuế + Chu Tước",
        "loai": "đại hung",
        "luan": "GIẬT MÌNH + BỆNH + CƯỚP TIN. Cấu trúc 'bệnh đột + scandal + "
                "data leak'. Modern: medical emergency + PR crisis + breach. "
                "Triple threat — ưu tiên Trị Phù cứu cấp.",
        "khi_dung": "(emergency mode — gọi support khẩn cấp)",
    },
    "Tu_ThienBong_DangXa": {
        "name": "Tử môn + Thiên Bồng + Đằng Xà",
        "loai": "đại hung",
        "luan": "CHẾT + THỦY TẶC + ẢO. Cấu trúc rất hung — chết do bị lừa + "
                "trộm. Đặc biệt nguy hiểm cho đầu tư, partnership với người mới.",
        "khi_dung": "(TUYỆT ĐỐI không invest / partner mới)",
    },

    # ════════ PARADOX (cát-hung mix) ════════
    "Sinh_ThienBong": {
        "name": "Sinh môn + Thiên Bồng (paradox)",
        "loai": "paradox conditional",
        "luan": "Sinh đại cát + Bồng đại hung — conflict. Đàm Liên: 'nếu gặp "
                "Sinh môn + Bính Kỳ/Đinh Kỳ + mùa Xuân/Hè → có thể làm việc lớn'. "
                "Cấu trúc 'cửa sinh có thủy tặc — cần partner sáng'.",
        "khi_dung": "Khởi sự CÓ partner sáng (Bính/Đinh) + mùa hè",
    },
    "Khai_KimKhac": {
        "name": "Khai môn ở cung Chấn/Tốn (Kim khắc)",
        "loai": "paradox suy",
        "luan": "Khai môn (Kim) ở cung Chấn/Tốn (Mộc) → Mộc khắc Kim → 'kim "
                "khắc' (môn bách). Đàm Liên: 'không hề may mắn chút nào'. "
                "Khai môn ngon cũng bị suy.",
        "khi_dung": "(tránh khởi sự lớn ở Đông/Đông Nam khi có Khai+Mộc)",
    },
    "ThienAnh_TheoCung": {
        "name": "Thiên Anh ở cung Hỏa (Ly) vs Kim (Càn/Đoài)",
        "loai": "conditional",
        "luan": "Thiên Anh Hỏa. Ở cung Ly (Hỏa) = đồng vượng → hư danh phình "
                "to. Ở cung Càn/Đoài (Kim) = Hỏa khắc Kim → tự tổn thương. "
                "Bất kể vị trí, Thiên Anh đều hung.",
        "khi_dung": "(tránh cầu danh ở mọi vị trí có Thiên Anh)",
    },
}


def interpret_cell_deep(
    cung_vn: str,
    mon_vn: Optional[str] = None,
    tinh_vn: Optional[str] = None,
    than_vn: Optional[str] = None,
    thien_can: Optional[str] = None,
    dia_can: Optional[str] = None,
) -> dict:
    """Luận sâu 1 cell trong bàn KMDG — môn + tinh + thần kết hợp.

    Args:
        cung_vn: Tên cung Việt (Khảm, Cấn, Chấn, ...)
        mon_vn: Tên môn Việt (Khai, Sinh, ...)
        tinh_vn: Tên tinh Việt (Thiên Phụ, Thiên Bồng, ...)
        than_vn: Tên thần Việt (Trị Phù, Đằng Xà, ...)
        thien_can: Thiên can Hán (戊, 己, ...) — optional
        dia_can: Địa can Hán — optional

    Returns:
        {
            "cung": cung_vn,
            "elements": [...],
            "mon_deep": {tam_phap, combo_with_than, cau_chu, ...},
            "tinh_deep": {tam_phap, combo_with_mon, mua, ...},
            "than_deep": {tam_phap, chien_thuat, modern, ...},
            "triple_combo": [...] (matching COMBO_LUAN_GIAI patterns),
            "overall_assessment": "...",
        }
    """
    result = {
        "cung": cung_vn,
        "elements": [],
        "mon_deep": None,
        "tinh_deep": None,
        "than_deep": None,
        "triple_combo": [],
        "overall_assessment": "",
    }

    if mon_vn and mon_vn in MON_DEEP:
        mon_d = MON_DEEP[mon_vn].copy()
        # Combo với thần cùng cell
        if than_vn and than_vn in mon_d.get("combo_voi_than", {}):
            mon_d["combo_with_current_than"] = {
                "than": than_vn,
                "luan": mon_d["combo_voi_than"][than_vn],
            }
        result["mon_deep"] = mon_d
        result["elements"].append(("Môn", mon_vn))

    if tinh_vn and tinh_vn in TINH_DEEP:
        tinh_d = TINH_DEEP[tinh_vn].copy()
        if mon_vn and mon_vn in tinh_d.get("combo_voi_mon", {}):
            tinh_d["combo_with_current_mon"] = {
                "mon": mon_vn,
                "luan": tinh_d["combo_voi_mon"][mon_vn],
            }
        result["tinh_deep"] = tinh_d
        result["elements"].append(("Tinh", tinh_vn))

    if than_vn and than_vn in THAN_DEEP:
        result["than_deep"] = THAN_DEEP[than_vn].copy()
        result["elements"].append(("Thần", than_vn))

    # Check triple combo matches
    if mon_vn and tinh_vn and than_vn:
        for combo_id, combo in COMBO_LUAN_GIAI.items():
            name = combo["name"]
            # Heuristic match: combo name contains all 3 element names
            if (mon_vn in name and tinh_vn.replace("Thiên ", "") in name
                and than_vn in name):
                result["triple_combo"].append({"id": combo_id, **combo})

    # Build overall assessment
    parts = []
    if result["mon_deep"]:
        parts.append(f"Môn {mon_vn}: {result['mon_deep'].get('tam_phap_ung_xu', '')[:80]}")
    if result["tinh_deep"]:
        parts.append(f"Tinh {tinh_vn}: {result['tinh_deep'].get('tam_phap', '')[:80]}")
    if result["than_deep"]:
        parts.append(f"Thần {than_vn}: {result['than_deep'].get('tam_phap_ung_xu', '')[:80]}")
    if result["triple_combo"]:
        parts.append(f"⚡ TRIPLE COMBO detected: {result['triple_combo'][0]['name']}")
    result["overall_assessment"] = " | ".join(parts)

    return result


def list_combo_patterns() -> list[dict]:
    """List tất cả combo patterns cho UI browse."""
    return [{"id": k, **v} for k, v in COMBO_LUAN_GIAI.items()]
