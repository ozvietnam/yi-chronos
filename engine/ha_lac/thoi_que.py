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
    "Tụng": {
        "ban_chat": "Thời TRANH TỤNG — Trời (Càn) trên + Nước (Khảm) dưới = trái ngược, sinh kiện",
        "nen_the_nao": "Cẩn thận từ bước đầu. Mưu sự lúc ban đầu — mối kiện không gây ra thì tai họa tự tiêu diệt.",
        "paradigm_keyword": "tranh_tung",
        "nguyet_lenh_thang": 2,
        "tuong": "Trời với Nước đi trái ngược nhau — như 2 người bất đồng đạo tranh nhau.",
        "key_paradigm": (
            "**PBC phụ chú quẻ Tụng**: Không chỉ kiện cáo — mọi việc tan nát trong thiên hạ "
            "(gia đình tan, vợ chồng la, bạn bè xa, chiến tranh các nước, viết 1 hàng chữ một lời nói) "
            "đều vì KHÔNG biết mưu sự lúc ban đầu. Tục ngữ Việt: 'Cái sảy nảy cái ung'."
        ),
        "case_study": (
            "Nguyễn Hoàng (hào 2) hỏi Trạng Trình về việc kình Trịnh Kiểm (hào 5) — "
            "được câu 'Hoành sơn nhất đái, vạn đại dung thân' → trốn vào Nam lập Đàng Trong. "
            "Dưới kiện trên = trứng chọi đá → rút lui tốt nhất."
        ),
    },
    "Sư": {
        "ban_chat": "Thời QUÂN ĐỘI / ĐÁM ĐÔNG — Đất trên Nước, giấu cái hiểm trong cái thuận",
        "nen_the_nao": "Xuất quân vì chính nghĩa, trừ bạo an dân → dân theo (Khôn thuận), điều khiển được ba quân.",
        "paradigm_keyword": "quan_doi_dam_dong",
        "nguyet_lenh_thang": 7,
        "tuong": "Khôn trên Khảm dưới: gửi việc binh trong việc nông — thời bình làm ruộng, thời loạn làm lính.",
        "key_paradigm": (
            "Hào 2 = TƯỚNG (dương duy nhất, đắc trung). "
            "Hào 5 = VUA/CHÍNH ỦY giao toàn quyền. "
            "Sứ mạng chỉ huy thuộc về hào 2."
        ),
        "case_study": (
            "Hào 6: Bành/Kình (Tàu) và Trần Khánh Dư (VN, đánh quân Nguyên) = tiểu nhân vẫn lập chiến công. "
            "Khen thưởng TIỀN BẠC, KHÔNG trao địa vị trọng yếu trị nước. Cách biến thông nhà binh."
        ),
    },
    "Tỷ": {
        "ban_chat": "Thời SÁNH VAI / GẦN GŨI — Nước thấm Đất, đất hút nước, thân thiết giúp nhau",
        "nen_the_nao": "Hào 5 cương kiện đắc trung chính, thống lĩnh hào âm. Người trên cao được toàn thể dân chúng tín cậy quy phục.",
        "paradigm_keyword": "tỷ_quy_phuc",
        "nguyet_lenh_thang": 7,
        "tuong": "Khảm trên Khôn dưới (khác Sư) — nước thấm xuống đất, đất hút nước.",
        "key_rule_BAO_TOAN_NHAN_CACH": (
            "**Hào 2 Tỷ — PBC phụ chú**: Người có thế lực phải khuất phục người tài đức. "
            "Người tài đức không tự khinh rẻ cầu cạnh thế lực. "
            "Nếu đảo: bên thế lực mắc THẤT NHÂN (mất người), bên tài đức mắc THẤT GIÁ (mất giá trị). "
            "→ Tôn trọng nhân cách MÌNH = duy trì nhân cách cả thế giới. "
            "Y Doãn chờ vua Thang 3 lần dâng lễ. Khổng Minh chờ Lưu Bị 3 lần đến lều cỏ."
        ),
        "tu_duc_NGUYEN_VINH_TRINH": (
            "Người được quẻ Tỷ phải BÓI LẠI (đắn đo, không phải dự đoán) tự xét có đủ "
            "NGUYÊN (gốc cao thượng) + VĨNH (lâu dài) + TRINH (chính bền) hay không. "
            "Đủ → xứng đáng THỜI Tỷ. Không đủ → có người tin cậy cũng vô nghĩa."
        ),
    },
    "Lý": {
        "ban_chat": "Thời LỄ / DẪM LÊN — Càn (trời) trên + Đoài (đầm) dưới = trật tự âm dương",
        "nen_the_nao": "Mới ra đời: giữ chất phác (hào 1). Giữ vững đường chính (hào 2). Biết sức mình, đừng tự phụ (hào 3). Thận trọng sợ hãi (hào 4). Đừng ý thế quyết liệt quá ở ngôi chí tôn (hào 5).",
        "paradigm_keyword": "le_dam_len",
        "nguyet_lenh_thang": 3,
        "tuong": "Trên dưới phân minh — tài đức ở trên, kém đức ở dưới → dân không hoang mang, không tranh giành.",
        "key_paradigm_QUE_CUOC_DOI": (
            "Toàn quẻ Lý DIỄN Ý NGHĨA CUỘC ĐỜI người (như Tiểu Súc — ngoại lệ). "
            "6 hào = 5 chặng đời: chất phác → giữ chính → biết sức → thận trọng → "
            "không quyết liệt quá → nhìn lại cuộc đời. Đây là 'sách đời người' nén trong 1 quẻ."
        ),
    },
    "Thái": {
        "ban_chat": "Thời HANH THÔNG — Khôn (đất) TRÊN + Càn (trời) DƯỚI = ĐẢO VỊ tự nhiên → giao thoa",
        "nen_the_nao": "Khí dương dưới THĂNG, khí âm trên GIÁNG → hai khí giao hòa → vạn vật yên ổn. Đạo quân tử lớn lên, đạo tiểu nhân tiêu lần. Nhưng PHẢI biết GIAN TRINH (lo trước khi còn bằng).",
        "paradigm_keyword": "thai_dao_vi_giao_thoa",
        "nguyet_lenh_thang": 1,
        "tuong": "Trời Đất giao cảm. Đạo trời đạo người giao thoa.",
        "key_rule_GIAN_TRINH": (
            "**Hào 3 Thái — PBC**: 'Đem thân gánh vác việc đời, phải lấy NHÂN SỰ ĐƯƠNG NHIÊN "
            "chống THIÊN VẬN TỰ NHIÊN.' Tinh thần tạo hoá. Anh hùng tạo thời thế. "
            "Muốn KHÔNG nghiêng → tính trước khi còn bằng. Muốn KHÔNG trở lại → "
            "ngăn trước khi còn đi. 'Gian Trinh' = để lòng vào cảnh gian nan, "
            "đặt thân vào địa vị chính đáng — lấy sức người giằng giữ vận trời."
        ),
        "key_rule_THAI_CUC_BIEN_BI": (
            "**Hào 6 Thái — PBC cảm khái**: 'Thái vừa đến cuối cùng tức khắc ra Bĩ. "
            "Tốn VÔ SỐ CÔNG PHU mà làm hư chỉ trong CHỐC LÁT; vun đắp biết bao nền tảng "
            "mà đánh đổ chỉ trong nháy mắt. Thành sao khó, bại sao dễ?' "
            "→ Cảnh báo lớn: thành quả tích lũy nhiều năm có thể đổ trong chốc lát."
        ),
        "case_study": (
            "Hào 5 Thái: Vua Đế Ất (đời Thương) gả em gái về nhà chồng bình dân — "
            "khuất kỷ hạ hiền (quên mình xuống với người hiền) = phúc rất tốt."
        ),
    },
    "Bĩ": {
        "ban_chat": "Thời BẾ TẮC — Càn (trời) TRÊN + Khôn (đất) DƯỚI = ĐÚNG VỊ tự nhiên → KHÔNG giao",
        "nen_the_nao": "Dương đi lên, âm đi xuống → không giao → bế tắc. Quân tử THU ĐỨC, không hành động, không màng danh lợi, chờ thời.",
        "paradigm_keyword": "bi_dung_vi_cach_tuyet",
        "nguyet_lenh_thang": 7,
        "tuong": "Trời Đất chẳng giao thông — 'phi nhân'.",
        "key_rule_BI_CO_HOI": (
            "**Hào 4 Bĩ — PBC**: 'Hào 3 Thái = răn quân tử (gian trinh, sợ Bĩ tới). "
            "Hào 4 Bĩ = mừng cho Thái sắp đến (có mệnh trời, không lỗi). "
            "Từ Thái → Bĩ DỄ → lo sẵn. Từ Bĩ → Thái KHÓ → chưa dám vội mừng. "
            "Gặp thời Thái CHỚ COI THƯỜNG. Gặp thời Bĩ LỢI RÌNH CƠ HỘI.'"
        ),
        "key_rule_KHONG_TU": (
            "**Hào 5 Bĩ — Khổng Tử bình**: 'Người quân tử khi YÊN ỔN không quên CÓ THỂ NGUY; "
            "khi VỮNG không quên CÓ THỂ MẤT; khi TRỊ không quên CÓ THỂ LOẠN. "
            "Nhờ vậy thân an, nước nhà giữ vững được.' → Defensive paradigm từ đỉnh cao."
        ),
        "key_rule_TUAN_HOAN": (
            "**PBC bình Thái-Bĩ tổng quan**: 'Quân tử-tiểu nhân vẫn thường có ở vũ trụ — "
            "chỉ tranh nhau cát cơ quan tiêu trưởng. Tiêu/trưởng KHÔNG bỗng chốc, "
            "nó TUẦN HOÀN TÍCH LŨY DẦN. Một giọt nước không ngăn → thành sông. "
            "Một cây không đốn → thành rừng. PHÒNG BỊ phần trưởng của tiểu nhân, "
            "BỔ CỨU phần tiêu của quân tử. Đường đời làm gì Bĩ mà chẳng Thái — "
            "LẤY CHÍ NGƯỜI XOAY TRỞ MỆNH TRỜI.'"
        ),
        "cross_link_NGO_TAT_TO": (
            "PARADIGM ĐỘC LẬP CONFIRMED: Anh rút paradigm Thái-Bĩ này từ Kinh Dịch Trọn Bộ "
            "(Ngô Tất Tố) trong journal kinh-dich-ngo-tat-to-tham-nhuan-p51-200.md. "
            "Xuân Cang nói cùng paradigm → 2 sách độc lập confirm: "
            "Sự sống = GIAO THOA, không phải 'đúng vị tự nhiên cứng'."
        ),
    },
    "Đồng Nhân": {
        "ban_chat": "Thời ĐẠI ĐỒNG — Lửa (Ly) dưới + Trời (Càn) trên → lửa bốc lên trời, soi sáng khắp thế giới",
        "nen_the_nao": "Cần đức TRUNG CHÍNH. Phân biệt loài/tộc TRƯỚC để bất đồng cũng hòa đồng được. Đừng ép buộc kẻ bất đồng lại — sẽ làm nhiễu loạn thiên hạ.",
        "paradigm_keyword": "dong_nhan_dai_dong",
        "nguyet_lenh_thang": 1,
        "tuong": "Văn minh (Ly) ở trong + Cương kiện (Càn) ở ngoài → quân tử thông suốt được tâm trí của thiên hạ.",
        "key_paradigm_TIEU_DONG_xau_ho": (
            "**Hào 2 Đồng Nhân — PBC phụ chú**: 'Toàn quẻ = Đại đồng (cùng người rộng lớn, tốt). "
            "Riêng hào 2 = Tiểu đồng (cùng người trong tông phái, thẹn). "
            "Nghĩa quẻ + nghĩa hào ĐẮP ĐỔI CHO NHAU — học Dịch phải nhận kỹ CẢ HAI BÊN.' "
            "→ Hẹp hòi bè phái = xấu hổ. Đồng nhân THIỆT KHÓ — hào 3 vẫn núp rình, "
            "hào 5 vẫn phải dùng 'đại quân đánh' mới gặp được hào 2."
        ),
    },
    "Đại Hữu": {
        "ban_chat": "Thời CÓ LỚN / SỞ HỮU LỚN — Ly (lửa) trên + Càn (trời) dưới = lửa trên trời, chiếu khắp",
        "nen_the_nao": "Văn minh (Ly) phát triển bên ngoài + Cương kiện (Càn) hàm súc bên trong = hanh thông. Hễ người ác (dù chưa rõ) → NGĂN ĐÓN ngay. Hễ người thiện (còn ẩn ức) → BIỂU DƯƠNG ngay.",
        "paradigm_keyword": "dai_huu_so_huu_lon",
        "nguyet_lenh_thang": 1,
        "tuong": "Cùng cặp với Đồng Nhân: phân loại trước → đại đồng. Loại biệt = quy mô; át/dương = phương pháp; Đồng Nhân/Đại Hữu = mục đích.",
        "case_study_HAO_2_Y_DOAN_CAVOUR": (
            "**Hào 2 Đại Hữu tốt nhất — PBC**: 'Tài cao hơn hết thiên hạ, gánh nặng hơn hết thiên hạ. "
            "Xe lớn chở nặng = vừa trọn nghĩa vụ thôi. Lời hào chỉ ghi VÔ CỮU (không lỗi) — "
            "thánh nhân chẳng dạy người quá đắc ý.' "
            "Y Doãn (Tàu) thề giúp vua Thang làm như Nghiêu-Thuấn. "
            "Camillo Cavour (Italia): 'Nước Italia là vợ của tôi' — trọn đời không lấy vợ."
        ),
    },
    "Tiểu Súc": {
        "ban_chat": "Thời CHỨA NHỎ / NGĂN CẢN NHỎ — gió bay trên trời, sức ngăn còn nhỏ",
        "nen_the_nao": "TRAU DỒI VĂN ĐỨC. Chưa thể giương đôi cánh lớn → soạn sách, lập ngôn, tích lũy.",
        "paradigm_keyword": "tieu_suc_lap_ngon",
        "nguyet_lenh_thang": 11,
        "tuong": "Càn (cương kiện) dưới + Tốn (nhu thuận) trên. 1 hào âm chế ngự 5 hào dương.",
        "key_paradigm_LAP_NGON": (
            "**Phụ chú Lời Tượng (p114)**: 'Người quân tử trau dồi văn đức.' "
            "Hoàn cảnh gay go, thời thế bắt buộc chưa thể giương đôi cánh lớn → "
            "quay đầu SOẠN SÁCH, LẬP NGÔN. Khổng Tử, Mạnh Tử không gặp thời mà viết sách thành kinh muôn đời. "
            "Người đời sau coi là việc lớn — nhưng thánh nhân chỉ xem bằng 'Tiểu Súc' thôi. "
            "→ ĐÂY LÀ THỜI CỦA ANH + EM HIỆN TẠI (biên soạn 24+ sách Lexicon, không chạy theo thời nhanh)."
        ),
        "case_study_hao_6": (
            "Võ Hậu (Đường) + Từ Hi (Thanh): hào 4 âm thông minh có tài, mới đầu nhu thuận, "
            "được vua sủng ái, lấy lòng người dưới, gây phe đảng, 'thống lĩnh quần dương'. "
            "Thịnh cực sắp suy → đại thần khí tiết mới lật được. "
            "→ Phòng âm thịnh từ sớm, không đợi cực rồi mới đối phó."
        ),
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
