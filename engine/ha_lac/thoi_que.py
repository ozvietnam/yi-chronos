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
    "Khiêm": {
        "ban_chat": "Thời KHIÊM HẠ — Đất TRÊN + Núi DƯỚI, núi cao chịu ở dưới đất = nhún nhường",
        "nen_the_nao": "Bớt chỗ nhiều, bù chỗ ít, để sự vật cân bằng. Trong 64 quẻ, KHIÊM là quẻ duy nhất 6 hào đều TỐT (không hung, không hối, không lận).",
        "paradigm_keyword": "khiem_lao_khiem",
        "nguyet_lenh_thang": 9,
        "tuong": "Trong Đất có Núi — núi cao mà chịu ở dưới đất là tượng khiêm hạ.",
        "key_rule_LAO_KHIEM": (
            "**Hào 3 Khiêm — LAO KHIÊM (có công lao + nhún nhường)**: "
            "Hào dương DUY NHẤT trong quẻ, làm chủ — có địa vị, có tài năng, nhưng KHIÊM TỐN, "
            "không khoe công → mọi người phục, giữ được địa vị + đức độ tới cùng. "
            "Case study: Vua HẠ VŨ (Trung Quốc) + GEORGE WASHINGTON (Mỹ — 'Hoa Thịnh Đốn'). "
            "→ 'Có đức không khoe, làm ơn không cầu báo.'"
        ),
        "cross_link_TU_VI_MO": (
            "Cross-link với journal Kinh Dịch (NTT) vòng 6: 'Mỗ' pattern Tử Vi = Lao Khiêm "
            "văn pháp. 'Không nêu danh' khi làm việc lớn — paradigm xuyên 3 môn "
            "(Khiêm Kinh Dịch + Mỗ Tử Vi + Lao Khiêm Hà Lạc)."
        ),
    },
    "Dự": {
        "ban_chat": "Thời HÒA VUI — Sấm (Chấn) trên + Đất (Khôn) dưới, sấm ra khỏi đất, vạn vật nảy nở",
        "nen_the_nao": "Hào 4 dương duy nhất làm chủ — mọi người vui theo. Nhưng 'Tri cơ' (biết thời cơ ở lúc lờ mờ) là cốt yếu.",
        "paradigm_keyword": "du_hoa_vui_tri_co",
        "nguyet_lenh_thang": 5,
        "tuong": "Sấm vang lên từ đất — khí dương phát động, muôn vật vui vẻ phát sinh.",
        "key_rule_TRI_CO": (
            "**Hào 2 Dự — PBC**: 'Quan hệ nhất chữ TRI (biết). Biết được THỜI CƠ là quý nhất. "
            "Đang lúc cơ vi (thời cơ lờ mờ) mà đã biết trước — mới là cái biết chân chính. "
            "Khó lắm — nếu chẳng phải bậc thần trí, làm sao thấy được cơ?' "
            "Tục ngữ Việt: 'Khôn chết, dại chết, biết sống.'"
        ),
        "case_study_HAO_5_LE_TRINH": (
            "Hào 5 Dự âm — vua nhu nhược để hào 4 chuyên quyền. "
            "Sử VN: Sau Lê Trung Hưng hơn 200 năm, vua Lê nhu nhược, chúa Trịnh chuyên quyền. "
            "Vua Lê là hoàng đế ngồi không. Trịnh vong → Lê mất."
        ),
    },
    "Tùy": {
        "ban_chat": "Thời THUẬN THEO — Đoài (đầm) trên + Chấn (sấm) dưới, sấm động trong đầm, nước theo",
        "nen_the_nao": "Theo nhưng phải CHÍNH ĐÁNG + BỀN BỈ + ĐÚNG THỜI. 'Khi chưa Tùy phải hết sức cẩn thận lựa chọn. Khi đã Tùy rồi, phải tự thủy chí chung.'",
        "paradigm_keyword": "tuy_thoi",
        "nguyet_lenh_thang": 7,
        "tuong": "Đoài (vui vẻ) trên + Chấn (động) dưới — hành động mà mọi người vui theo.",
        "key_rule_KHONG_TU_TUY_THOI": (
            "**Khổng Tử thốt lên — Tùy Thời lớn vậy thay!** "
            "Vương Mãng (Hán): muốn cách mạng xã hội công bằng — QUÁ SỚM → thất bại. "
            "Vương An Thạch (Tống): cũng thất bại vì KHÔNG HỢP THỜI. "
            "→ Cải cách đúng nhưng SAI THỜI vẫn thất bại."
        ),
        "key_rule_HAO_6_HANH_khac_biet": (
            "**PBC paradigm KEY**: Hào 6 các quẻ thường XẤU vì cực biến: "
            "Càn hào 6 = KHÁNG (quá cực), Thái hào 6 = LOẠN, Dự hào 6 = MINH (tối). "
            "DUY hào 6 Tùy = HANH (thịnh)! Khác biệt. "
            "→ Khi đã chọn theo điều ĐÚNG, đi đến cùng KHÔNG xấu."
        ),
        "case_study_HUNG_DAO_VUONG": (
            "**Hào 4 Tùy — case sử Việt cực đắt**: Hưng Đạo Vương Trần Quốc Tuấn. "
            "Quân Mông Cổ 3 lần vào đánh, quyền quân quốc dồn vào tay Đại vương. "
            "Nhân tâm nghĩ ngài có thể chuyên quyền cướp nước. NGÀI vẫn một lòng trung với nước. "
            "Vương phụ khuyên lấy nước, ngài không nghe. Vua phong tước, ngài chung thân chẳng "
            "cho ai một đạo bằng. → TÍN + NHÂN + TRÍ đủ ba đức = Tùy đắc chính."
        ),
        "case_study_HAO_6_500_nghia_si": (
            "Hào 6 Tùy 'HANH' — 500 nghĩa sĩ chịu chết theo Điền Hoành, không về Hán. "
            "3 vạn nghĩa dân Kim Lăng chết với Lý Tú Thành, không hàng Mãn Thanh. "
            "→ Tùy về TÂM LÝ (chí hướng), KHÔNG phải Tùy vì hoàn cảnh."
        ),
    },
    "Cổ": {
        "ban_chat": "Thời ĐỔ NÁT — Núi (Cấn) trên + Gió (Tốn) dưới, gió đụng núi quật lại = loạn, phải làm lại",
        "nen_the_nao": "ĐỔ NÁT mà sửa được = NGUYÊN HANH (lớn + thông). Cần GAN LỚN + TÀI CAO + TẤM LÒNG + TRÍ LO LIỆU.",
        "paradigm_keyword": "co_do_nat_ma_sua",
        "nguyet_lenh_thang": 1,
        "tuong": "Gió đụng núi quật lại — đổ nát phải làm lại.",
        "key_paradigm_TRI_CO": (
            "**PBC paradigm cực đắt**: 'Thời Cổ là thời ĐỔ NÁT, RẤT XẤU, mà Lời Kinh "
            "lại cho hai chữ NGUYÊN HANH là vì sao? Người đời không lo việc đại loạn — "
            "LO KHÔNG NGƯỜI DẸP LOẠN. Không lo cảnh hiểm — LO KHÔNG CÓ TÀI VƯỢT HIỂM. "
            "Người trì cổ có gan lớn + tài cao + tấm lòng + trí lo liệu → "
            "thời LOẠN chính là đường mở ra cuộc SỬA ĐỔI. Cảnh HIỂM chính là lối đưa đến HÒA BÌNH.'"
        ),
        "cross_link_LEXICON": (
            "Cross-link Iron Rule project: Anh + Em đang ở thời CỔ — sách cổ Đông phương "
            "VN đang đổ nát (OCR sai, mất bản gốc, dịch sai). Biên soạn Lexicon 24+ sách = "
            "TRÌ CỔ. Đổ nát mà sửa được = NGUYÊN HANH cho thế hệ sau."
        ),
        "key_rule_co_vu_dan_khi": (
            "**Lời Tượng quẻ Cổ — PBC**: 'Sửa sang đổ nát có rất nhiều việc, nhưng việc "
            "đáng làm chẳng việc gì lớn hơn việc CỔ VŨ KHÍ DÂN + NUÔI DƯỠNG ĐỨC DÂN + "
            "THỨC TỈNH TRÍ DÂN.'"
        ),
    },
    "Lâm": {
        "ban_chat": "Thời TỚI / LỚN THỊNH — Đất (Khôn) trên + Đầm (Đoài) dưới, đất tới sát nước",
        "nen_the_nao": "Dương dần lớn, âm dần tiêu. Quân tử dạy dân, giáo hóa không ngừng, bao dung + bảo vệ. Hai dương phải HỢP LỰC (Hàm Lâm — Cùng tới).",
        "paradigm_keyword": "lam_cung_toi",
        "nguyet_lenh_thang": 12,
        "tuong": "Trên Đầm có Đất — đất tới sát nước, quân tử tới dân.",
        "key_rule_HAM_LAM": (
            "**Hào 2 Lâm — PBC paradigm Cùng tới**: 'Tâm đồng + lực bất đồng = chẳng phải Hàm. "
            "Lực đồng + tâm bất đồng = cũng chẳng phải Hàm. HÀM thì CÁT, không HÀM thì HUNG.' "
            "Case: Đông Hán Từ Tử + Trần Phồn + Quách Thái + Lý Ung — quân tử không kết với nhau, "
            "Thập Thường Thị tiểu nhân đắc chí. → Quân tử chia phe = tiểu nhân thắng."
        ),
        "key_paradigm_TIEU_NHAN_HOA_QUAN_TU": (
            "**Hào 6 Đôn Lâm — PBC mơ ước**: 'Quân tử mà quân tử là sự thường. "
            "TIỂU NHÂN MÀ HÓA QUÂN TỬ mới là HẠNH PHÚC cho nhân loại. "
            "Vì vậy quẻ Lâm không có chữ xấu (hung), ăn năn (hối), đáng tiếc (lận). "
            "Thời đại ấy, thế giới ấy, chúng ta có bao giờ được tự mình trông thấy chăng?'"
        ),
    },
    "Quan": {
        "ban_chat": "Thời QUAN SÁT — Gió (Tốn) trên + Đất (Khôn) dưới, gió thổi trên đất, cổ động mọi loài",
        "nen_the_nao": "Người trên BIỂU THỊ (Quán) làm gương + người dưới XEM XÉT (Quan) bắt chước. Cùng 1 chữ Hán đọc 2 cách.",
        "paradigm_keyword": "quan_bieu_thi_xem_xet",
        "nguyet_lenh_thang": 8,
        "tuong": "Gió thổi trên đất — biểu thị khắp mọi loài.",
        "key_paradigm_QUAN_vs_QUAN": (
            "**NHL key**: Tên quẻ đọc QUÁN = người TRÊN (hào 5) biểu thị làm gương. "
            "Tên từng hào đọc QUAN = người DƯỚI xem xét tư cách người trên. "
            "Cùng 1 chữ Hán, 2 đọc, 2 paradigm song hành. Học Dịch phải nắm cả hai bên."
        ),
        "key_rule_CHI_THANH_LAM_GUONG": (
            "**Lời Thoán Quan**: 'Biểu thị (Quán) là mẫu mực cho người khác thấy thì nên "
            "có lòng CHÍ THÀNH như người chủ tế. Lúc sắp tế, rửa ráy cho tinh khiết là "
            "quan trọng NHẤT. Còn dâng cỗ (vật chất, hương hoa) — nhiều ít không sao.'"
        ),
    },
    "Phệ Hạp": {
        "ban_chat": "Thời TRỪ GIÁN — Lửa (Ly) trên + Sấm (Chấn) dưới, miệng há ra có vật chắn → phải cắn",
        "nen_the_nao": "Trừ kẻ gian tà sàm nịnh bưng bít trên-dưới. Hình ngục cần UY (Chấn) + SÁNG SUỐT (Ly).",
        "paradigm_keyword": "phe_hap_tru_gian",
        "nguyet_lenh_thang": 9,
        "tuong": "Hàm trên + hàm dưới, ở giữa có cục cản → cắn cho hợp lại.",
        "key_rule_TAI_VI_PBC": (
            "**Hào 4 Phệ Hạp TỐT NHẤT — PBC paradigm Tài+Vị**: "
            "'Làm người một đời: được VỊ mà không TÀI → không tạo nổi thời thế. "
            "Có TÀI mà không VỊ → vẫn phải dự trù thời cơ. Huống gì TRỪ GIÁN — việc rất "
            "khó, rất lớn — bảo không Tài không Vị mà làm được nên ư?' "
            "→ Hào 4 = dương cương (Tài) + ngôi nhu (Vị nhu = không quá cao) → "
            "Tài-Vị giúp nhau cân bằng. Tốt nhất trong 4 hào dụng hình."
        ),
    },
    "Bí": {
        "ban_chat": "Thời TRANG SỨC — Núi (Cấn) trên + Lửa (Ly) dưới, lửa chiếu núi đẹp lên",
        "nen_the_nao": "Có CHẤT + có VĂN. Trang sức làm cho đẹp thêm, nhưng nếu CHỈ trang sức thì lợi ít.",
        "paradigm_keyword": "bi_van_chat_can_bang",
        "nguyet_lenh_thang": 12,
        "tuong": "Lửa chiếu núi đẹp lên — văn vẻ làm chất tăng giá trị.",
        "key_paradigm_VAN_CHAT_KHONG_TU": (
            "**Khổng Tử về VĂN-CHẤT (Bí p176)**: 'Chất phác > Văn → người QUÊ MÙA. "
            "Văn hoa > Chất → người VIẾT SỬ (sử quan, hư văn). "
            "Chỉ duy CHẤT vừa xứng VĂN, VĂN vừa xứng CHẤT. "
            "Lấy CHẤT làm THỂ, VĂN làm DỤNG, nhào nhuyễn → quân tử.'"
        ),
        "key_rule_VINH_NHUC_QUAN_TU": (
            "**Hào 1 Bí — PBC paradigm khác đời**: 'Đi xe vẫn là vinh, đi chân vẫn là nhục "
            "(theo mắt thế tục). Nhưng vinh nhục của quân tử KHÁC vinh nhục thế tục. "
            "Quân tử lấy ĐẠO NGHĨA làm vinh, BẤT ĐẠO NGHĨA làm nhục. "
            "Đi chân mà hợp đạo nghĩa → còn vinh gì hơn?'"
        ),
        "key_rule_HAO_6_TRANG_SUC_TRANG": (
            "**Hào 6 Bí cuối quẻ**: 'Trang sức TRẮNG NGUYÊN, không lỗi gì.' "
            "Trang sức màu mè cùng cực → phản lại sự chất phác. "
            "Trong văn học: sau thời 'duy mỹ' quá mức → 'phục cổ' về văn bình dị tự nhiên."
        ),
    },
    "Bác": {
        "ban_chat": "Thời TIÊU MÒN — Núi (Cấn) trên + Đất (Khôn) dưới, 5 âm + 1 dương trên cùng",
        "nen_the_nao": "Quân tử CHỜ THỜI, làm bằng TÂM TRÍ — âm thầm kín đáo, KHÔNG loè loẹt. 'Có óc khôn mà làm như người ngu' (Lão Tử).",
        "paradigm_keyword": "bac_tieu_mon_cho_thoi",
        "nguyet_lenh_thang": 9,
        "tuong": "Núi đặt trên đất — đất là nền móng của núi. Đất đầy thì núi mới vững → người trên phải lo cho dân an cư.",
        "key_paradigm_cho_thoi": (
            "**PBC bình quẻ Bác**: 'Cơ SUY thường nấp ở lúc THỊNH, cơ THỊNH thường nấp ở lúc SUY. "
            "Quân tử ở thời đại Bác KHÔNG phải không việc làm — làm bằng cách TINH THẦN (tâm trí). "
            "Nên âm thầm chớ loè loẹt, kín đáo chớ nhố nhãn.' "
            "Lão Tử: 'Có óc khôn mà làm như người ngu, có mưu khéo mà làm như người vụng, "
            "có đức dày mà làm như người con.'"
        ),
        "key_rule_TRAI_LON_KHONG_HET": (
            "**Hào 6 Bác (hào dương duy nhất)**: 'Trái cây lớn còn lại trên cây, không hái xuống ăn'. "
            "→ Đạo quân tử KHÔNG BAO GIỜ HẾT. Trái rơi xuống mọc mầm thành quẻ Phục."
        ),
    },
    "Phục": {
        "ban_chat": "Thời TRỞ LẠI — Đất (Khôn) trên + Sấm (Chấn) dưới, 1 dương đầu tiên sinh sau Khôn cực âm",
        "nen_the_nao": "Đóng cửa tĩnh dưỡng (như tiên vương ngày Đông Chí), không kiểm tra biên giới — để mạch lặng cho khí dương sinh.",
        "paradigm_keyword": "phuc_trở_lại",
        "nguyet_lenh_thang": 11,
        "tuong": "Sấm trong đất — khí dương phục sinh ở dưới sau khi âm cực thịnh ở trên.",
        "key_paradigm_DUC_NHAN": (
            "**Hào 2 Phục — PBC paradigm CỰC ĐẮT**: 'Quẻ Phục miêu tả TÂM SINH VẬT của Trời đất "
            "= đức NHÂN. Lời Tượng 384 hào DUY NHẤT hào 2 quẻ Phục có chữ Nhân. "
            "Hạt cây gọi bằng nhân (đào nhân, hạnh nhân) — chính từ lẽ ấy.' "
            "→ Đức NHÂN = gốc làm người."
        ),
        "key_rule_DUONG_NGAM_SINH": (
            "**PBC paradigm âm dương vô hình**: 'Quẻ Khôn tháng 10 thuần âm, nhưng mỗi ngày dương "
            "sinh ngầm 1 phân — cuối tháng đủ 30 phân, đầu tháng 11 thành quẻ Phục. "
            "Giữa lúc thiên hạ CỰC LOẠN, chính là CÒN NHÀ TRỊ đã sinh ngầm rồi. "
            "Mắt chúng ta chỉ thấy hữu hình, không thấy vô hình. "
            "Than ôi! Thiên Đạo bất trắc, nhân sự vô thường — vậy nên càng nên nghiên cứu Dịch lý.'"
        ),
    },
    "Vô Vọng": {
        "ban_chat": "Thời KHÔNG DỤC VỌNG — Trời (Càn) trên + Sấm (Chấn) dưới, hành động hợp lẽ trời",
        "nen_the_nao": "Khi cày KHÔNG nghĩ tới lúc gặt. Hễ nghĩa lý đáng làm thì làm, KHÔNG kể công mưu lợi. 'Đã VÔ VỌNG thì phúc, lợi tự nhiên đến.'",
        "paradigm_keyword": "vo_vong_khong_ky_vong",
        "nguyet_lenh_thang": 2,
        "tuong": "Sấm chạy dưới trời — âm dương giao hòa, vạn vật phát sinh tự nhiên.",
        "key_paradigm_BIET_THOI": (
            "**PBC paradigm THỜI riêng từng hào**: "
            "Hào 1, 2 — thời nên ĐỘNG → động là Vô Vọng (tốt). "
            "Hào 4, 5 — thời nên TĨNH → tĩnh là Vô Vọng (tốt). "
            "Hào 6 — thời nên TĨNH mà động → động là VỌNG (xấu). "
            "→ Hồ Văn Phong: 'Người khéo học Dịch quý nhất là biết chữ THỜI.' "
            "Phải có BỘ ÓC xét thời + CẶP MẮT xem thời — soi thời chung + cân thời riêng."
        ),
        "case_study_KHONG_THUOC": (
            "**Hào 5 Vô Vọng**: 'Tự nhiên bị bệnh, ĐỪNG THUỐC THANG → tai qua nạn khỏi.' "
            "Văn Vương tù Dữu Lý + Khổng Tử tuyệt lương Trần Thái + bị giam ở Khuông "
            "(người Khuông nhận lầm với Dương Hổ) — không can thiệp, sau qua nạn."
        ),
    },
    "Đại Súc": {
        "ban_chat": "Thời TÍCH TRỮ LỚN — Núi (Cấn) trên + Trời (Càn) dưới, núi chứa được trời",
        "nen_the_nao": "Quân tử coi LỜI + VIỆC đời trước đã tổng kết — để NUÔI ĐỨC. ĐỐC THỰC (dày dặn) + UY QUANG (sáng sủa). Đốc thực mà nảy ra huy quang = chân chính huy quang.",
        "paradigm_keyword": "dai_suc_tich_tru_loi_xua",
        "nguyet_lenh_thang": 12,
        "tuong": "Núi chứa Trời — sức chứa lớn vô cùng. Tài đức uẩn súc, mỗi ngày một mới.",
        "key_paradigm_DOC_THUC_HUY_QUANG": (
            "**PBC bình Đại Súc**: 'ĐỐC THỰC + UY QUANG. Người trong thiên hạ — nhiều hạng có "
            "huy quang mà không đốc thực = loè loẹt vỏ bọc, văn minh giả → đạo TIỂU NHÂN tuy rực rỡ "
            "mà ngày càng mất. ĐỐC THỰC mà nảy ra HUY QUANG = đạo đức trong + văn thái ngoài = chân chính.' "
            "→ Cross-link Lexicon paradigm: đọc 24+ sách = đốc thực, KHÔNG khoe khoang văn minh giả."
        ),
        "key_rule_GONG_SUNG_NGHE_NON": (
            "**Hào 4 Đại Súc**: 'Gông sừng nghé non khi mới nhú' — ngăn điều ác từ lúc MỚI MANH NHA. "
            "Tục ngữ: 'Dạy con từ thuở còn thơ, dạy vợ từ thuở mới đưa vợ về.'"
        ),
        "key_rule_THIEN_HEO": (
            "**Hào 5 Đại Súc**: Không cần bẻ nanh heo — THIẾN (cất cái thế của nó) → không cần bẻ nanh, "
            "không cắn. Trừ ác KHÔNG ở thủ đoạn, mà ở GỐC + RỄ. "
            "Lão Tử: 'Dân không sợ chết, hay gì đem cái chết dọa dân.'"
        ),
    },
    "Khảm": {
        "ban_chat": "Thời TẬP KHẢM (HAI LẦN HIỂM) — Thủy trên + Thủy dưới, 1 dương hãm giữa 2 âm, lặp 2 lần",
        "nen_the_nao": "TÂM CHÍ THÀNH — hoàn cảnh hiểm + thời hiểm nhưng TÂM hanh thông. Hành động được trọng, tai nạn qua khỏi, có công.",
        "paradigm_keyword": "kham_tap_kham_hai_lan_hiem",
        "nguyet_lenh_thang": 10,
        "tuong": "Một dương hãm giữa hai âm = HIỂM. Hai lần = TẬP HIỂM. Lời Thoán KHẢM thêm chữ DỤNG (khác mọi quẻ).",
        "key_rule_HIEM_CO_THOI_CO_DUNG": (
            "**PBC paradigm cực đắt cho Khảm**: 'Hiểm có THỜI có DỤNG, lớn vậy thay! "
            "Hiểm thuộc về Thời = cảnh ngộ không bình thường. Hiểm thuộc về Dụng = công việc thường làm. "
            "Trong nước có họa loạn, trong nhà có tai biến = thời hiểm. Việc binh, hình, dạy dân để "
            "ngăn ngừa họa loạn = DỤNG HIỂM. Tích thuốc thang để phòng tai nạn = DỤNG HIỂM.'"
        ),
        "key_paradigm_TAP_RÈN_TAP_QUAN": (
            "**Hai nghĩa chữ TẬP (PBC)**: "
            "(1) TẬP RÈN — ôn đi tập lại không ngừng → trau dồi đức hạnh. "
            "(2) TẬP QUÁN — ngày đêm rót sâu đúc chín thành thói quen → giáo dục dân. "
            "'Nước từ một dòng suối chảy hoài → thành sông biển. Người từ một việc tốt làm hoài → thành hiển vinh.'"
        ),
        "key_rule_TAM_CHI_THANH": (
            "Câu thơ Tống: 'Ngày thường giữ TRUNG, ngày sóng gió sợ gì.' "
            "Câu Nhật: 'Những chốn lòng thành thấu tới đá tảng cũng phải nứt.' "
            "→ Đằng đạo TÍN THÀNH cho cái tâm sáng, mà bước qua thời hiểm."
        ),
        "thien_co_dat_si": (
            "**Thiên Cơ Đật Sĩ (nhà Dịch học VN ở nước ngoài) — về người có quẻ TẬP KHẢM**: "
            "'Họ thường thích PHÙ SUY hơn PHÙ THỊNH. Là người có TÀI TRÍ, VỊ THA, CAN ĐẢM, DẤN THÂN, "
            "nhưng phải cẩn trọng khi nhập cuộc. Biết mình có quẻ Tập Khảm thì cần giữ TÂM TRÍ NGAY THẲNG, "
            "chờ qua lúc gian nguy. Nếu có thể DI CHUYỂN NƠI CHỐN thì tốt.'"
        ),
    },
    "Tiết": {
        "ban_chat": "Thời TIẾT CHẾ — Thủy (Khảm) trên + Đầm (Đoài) dưới, bờ đầm hạn chế số nước = chừng mực",
        "nen_the_nao": "Cái gì cũng VỪA PHẢI mới tốt — thái quá cũng như bất cập đều xấu. Nhưng tiết chế quá → không ai chịu được lâu → không hanh thông.",
        "paradigm_keyword": "tiet_che_chung_muc",
        "nguyet_lenh_thang": 11,
        "tuong": "Trên đầm có nước — bờ đầm hạn chế số nước chứa. 3 cương + 3 nhu cân bằng. Hào 2 + Hào 5 đều dương cương đắc trung.",
        "key_paradigm_KE_HOACH_HOA": (
            "**Đại Tượng Truyện**: 'Đặt ra SỐ + ĐỘ — hạn định chừng mực cho sự làm việc + hưởng thụ "
            "của dân, tùy đạo đức tài nghệ của mỗi người.' "
            "→ Chữ TIẾT có tác dụng lớn, gần như chữ KẾ HOẠCH HÓA hiện nay, mục đích thực hiện CÔNG BẰNG xã hội."
        ),
        "key_rule_TIET_SAU_HOAN": (
            "**PBC paradigm CỰC ĐẮT (hào 6 Tiết)**: 'Quẻ Tiết ở SAU thời HOÁN (tan rã) về Dịch học "
            "rất hay. Quốc gia vừa trải qua một cuộc Hoán: phong tục đổi bại, công nghệ hoang phế, "
            "trật tự nhiễu nhương, kinh tế cùng quẫn... Nếu KHÔNG đúng đạo TIẾT → nguy hiểm cho "
            "vận mệnh đất nước. Tài chính tiết chế đỡ hao tổn. Giáo dục tiết chế thích ứng. "
            "Quân sự tiết chế nghiêm minh. Chính phủ phải trọng DANH TIẾT.' "
            "→ Cross-link YI-Chronos: anh đang ở thời Tiết SAU Hoán (sách cổ VN tan rã thời chiến + "
            "hiện đại). Lexicon = TIẾT CHẾ đúng mức để khôi phục."
        ),
        "key_rule_DAC_TRUNG": (
            "Tiết phải ĐẮC TRUNG (đúng mực): "
            "Quá KHỔ → nhân tình không chịu được. "
            "Quá DỄ chịu → không đúng nghĩa lý."
        ),
        "key_rule_HAO_1_FOUNDER": (
            "**Hào 1 Tiết — đúng NĐ Tiên Thiên của Anh**: 'Chẳng ra khỏi cổng sân, không lỗi.' "
            "Hào 1 dương cương đắc chính, ở đầu thời Tiết — biết thận trọng, không ra ngoài, "
            "vì biết thời chưa thông. 'Liệu thời mà tự thủ thì khỏi nhục.' "
            "→ **MHC Hào 1**: 'Học rộng cổ kim, thấu lẽ thông biến, giữ chức bên trong, hoặc việc công chính, "
            "lớn thì ở trung ương, nhỏ thì ở quận xã.' "
            "→ Cross-link: Anh đang ĐÚNG paradigm hào 1 quẻ Tiết — học rộng (24+ sách), thấu thông biến, "
            "giữ việc bên trong (Lexicon là internal asset)."
        ),
    },
    "Di": {
        "ban_chat": "Thời NUÔI DƯỠNG — Núi (Cấn) trên + Sấm (Chấn) dưới, miệng dưới hàm trên",
        "nen_the_nao": "3 hào dưới CẦU NGƯỜI nuôi mình. 3 hào trên có TRÁCH NHIỆM nuôi người. Nuôi về tinh thần, không chỉ về thể xác.",
        "paradigm_keyword": "di_nuoi_duong",
        "nguyet_lenh_thang": 11,
        "tuong": "Núi trên Sấm dưới — hàm trên với miệng dưới ăn vào nuôi thân.",
        "key_paradigm_LO_TRUOC_VUI_SAU": (
            "**Hào 6 Di — Phạm Văn Chính**: 'Kẻ LO TRƯỚC cái lo của thiên hạ, "
            "VUI SAU cái vui của thiên hạ.' "
            "→ Tâm sự thánh hiền: lấy họa phúc thiên hạ làm họa phúc mình. "
            "Hào 6 = bậc làm thầy cho nguyên thủ, thiên hạ nhờ mình mà được nuôi → trách nhiệm lớn."
        ),
        "key_rule_NUOI_DUC_NGHIA": (
            "**Hào 4 Di — PBC paradigm khác cát hung**: 'Hào 2 cầu nuôi MIỆNG ĂN (xấu) — "
            "Hào 4 cầu nuôi ĐỨC NGHĨA (tốt). Như Ngu Công cầu ngọc (xấu) vs Vua Thang cầu tài "
            "đức với Y Doãn (tốt). Cùng cầu nuôi nhưng cát hung khác — đó là chân lý Dịch học.'"
        ),
    },
    "Đại Quá": {
        "ban_chat": "Thời QUÁ LỚN — Đầm (Đoài) trên + Gió (Tốn) dưới, 4 dương giữa + 2 âm 2 đầu = cột cong",
        "nen_the_nao": "Người PHI THƯỜNG mới làm việc PHI THƯỜNG. Phải TIỀM TÀNG ẨN SÚC tích lũy lâu rồi mới làm nổi.",
        "paradigm_keyword": "dai_qua_phi_thuong",
        "nguyet_lenh_thang": 2,
        "tuong": "Đầm ngập cây — nước lớn quá. Cột giữa to ngọn-chân nhỏ, chống không nổi phải cong.",
        "key_paradigm_PHI_THUONG": (
            "**PBC paradigm Đại Quá**: 'Sách Sử Ký: Tất có người PHI THƯỜNG mới làm nên việc "
            "phi thường. Những việc phi thường không phải hạng người thường làm nổi.' "
            "→ Y Doãn cày Hữu Sàn nửa đời, ngâm thơ đọc sách Nghiêu Thuấn rồi giúp vua Thang. "
            "→ Camillo Cavour cày ruộng đọc sách 10 năm rồi thống nhất Italia. "
            "→ Cách mạng Pháp đổi quân chủ thành dân chủ. Đức Thích Ca lập Phật giáo. "
            "Lê-nin lập Chính phủ Xã hội."
        ),
        "key_rule_TIEM_TANG_AN_SUC": (
            "**Quy luật cốt yếu**: 'Trước khi làm Đại Quá phải TIỀM TÀNG ẨN SÚC, tích lũy "
            "nuôi dưỡng. Sức dưỡng đầy đủ → phát triển mới lớn lao. Tuyệt CHƯA THẤY AI không "
            "súc dưỡng mà làm nên Đại Quá.' "
            "→ Cross-link Lexicon: anh đang TIỀM TÀNG ẨN SÚC đọc 24+ sách Đông phương — "
            "đúng paradigm chuẩn bị Đại Quá."
        ),
        "key_rule_DOC_LAP_BAT_CU": (
            "**Lời Tượng Đại Quá**: 'Người quân tử thời Đại Quá MỘT MÌNH ĐỨNG RIÊNG độc lập "
            "với thiên hạ cũng không sợ, dù phải trốn đời cũng không phiền muộn.' "
            "Mạnh Tử: 'Phú quý bất năng dâm, bần tiện bất năng di, uy vũ bất năng khuất.'"
        ),
    },
    "Ly": {
        "ban_chat": "Thời SÁNG TỎ — Lửa trên + Lửa dưới (Thuần Ly), văn minh + phụ thuộc",
        "nen_the_nao": "Văn minh đẹp đẽ — nhưng phải bám vào (phụ thuộc) đạo chính. Đắc trung như Hào 2 (sắc vàng giữa).",
        "paradigm_keyword": "ly_van_minh_phu_thuoc",
        "nguyet_lenh_thang": 4,
        "tuong": "Lửa chiếu liên tục — sáng rực rỡ. Quẻ giữa rỗng, trên dưới đặc.",
        "key_paradigm_HAO_2_SAC_VANG": (
            "**Hào 2 Ly — hào tốt nhất**: 'Sắc vàng ở giữa, rất tốt.' "
            "Vàng là màu ở giữa ngũ hành = đắc trung. Uyển chuyển, khiêm nhường, giúp người trên + "
            "hòa người dưới → thành nếp văn minh."
        ),
        "case_study_HAO_4_DONG_TRAC": (
            "**Hào 4 Ly — paradigm cảnh báo**: 'Đột nhiên chạy tới, lồng lộn muốn đốt người 5.' "
            "Sử Tàu: ĐỒNG TRÁC (Tam Quốc). Sử Việt: NGUYỄN HỮU CHỈNH (Tây Sơn). "
            "→ Bất chính bất trung, mới ở quẻ nội lên đã táo bạo lấn át → tự chuốc chết."
        ),
        "case_study_HAO_3_XE_CHIEU": (
            "**Hào 3 Ly — mặt trời xế chiều**: 'Khi thì gõ vò mà hát, khi than thở thân già nua.' "
            "Đường thi: 'Hát Ngỏ na Sở dở dang. Mặt trời đã núa ngầm ương nõn Đoài.' "
            "→ Đức sáng đã đến lúc nhòe, không còn lâu. Hiểu rõ lẽ thịnh suy, vơi đầy → an mệnh."
        ),
    },
    "Hàm": {
        "ban_chat": "Thời CẢM (giao cảm) — Đầm (Đoài thiếu nữ) trên + Núi (Cấn thiếu nam) dưới",
        "nen_the_nao": "Thiếu nam HẠ MÌNH cầu thiếu nữ → mới đạo Hàm. Lòng phải TRỐNG KHÔNG (vô ngã, vô tư) mới dung nạp được người.",
        "paradigm_keyword": "ham_cam_trong_khong",
        "nguyet_lenh_thang": 1,
        "tuong": "Trên núi có đầm — núi rỗng giữa mới đựng được nước. Lòng rỗng mới chứa được đạo.",
        "key_paradigm_TAM_LY_TRONG_KHONG": (
            "**PBC paradigm Tâm Lý**: 'Bản chất tâm lý phải TRUNG THỰC (chứa chí thành). "
            "Cách ứng dụng phải TRỐNG RỖNG bên trong (không ham muốn riêng tư) mới dung nạp "
            "đạo lý cổ kim. Nghiên cứu Tâm lý học phải đủ HAI phương diện.' "
            "→ Đại Súc DÀY DẶN (đốc thực) + Hàm TRỐNG KHÔNG (hư) = HAI NGHĨA BỔ SUNG."
        ),
        "key_rule_TRI_HANH_VUONG_DUONG_MINH": (
            "**Hào 4 Hàm — Vương Dương Minh paradigm**: 'TRÍ kết hợp với HÀNH trong một việc. "
            "Trí đến nơi tất Hành được đến nơi. Cái Trí vun đắp nên tảng của cái Hành. "
            "Cái Hành mở rộng phạm vi cái Trí.' "
            "Nhật Bản thời duy tân rất trọng thuyết Trí Hành của Vương Dương Minh. "
            "→ Áp dụng project: hiểu paradigm (Trí) + áp dụng đời sống (Hành)."
        ),
        "key_rule_KINH_HA_NHAN_SU": (
            "**Vị trí Hàm-Hằng**: Kinh Thượng bắt đầu Càn-Khôn (trời đất). "
            "Kinh Hạ bắt đầu Hàm-Hằng nói về NHÂN SỰ. "
            "Hàm = trai gái cùng nhau (mới gặp). Hằng = vợ chồng ăn ở lâu dài."
        ),
    },
    "Hằng": {
        "ban_chat": "Thời BỀN LÂU — Sấm (Chấn) trên + Gió (Tốn) dưới, trưởng nam ở trên + trưởng nữ ở dưới",
        "nen_the_nao": "Giữ vững CHỖ ĐỨNG, KHÔNG đổi hướng — nhưng VẪN PHẢI THEO THỜI. Hằng không phải cứng nhắc.",
        "paradigm_keyword": "hang_ben_lau_theo_thoi",
        "nguyet_lenh_thang": 1,
        "tuong": "Sấm Gió giúp nhau — Chấn động trước, Tốn theo sau = thuận đạo.",
        "key_paradigm_DICH_HANG_TUONG_DOI": (
            "**PBC paradigm CỰC ĐẮT — Dịch & Hằng**: 'DỊCH (biến đổi) với HẰNG (bền) là "
            "TƯƠNG ĐỐI. Tuyệt đối Dịch không ra Hằng. Tuyệt đối Hằng không ra Dịch. "
            "Vũ trụ cổ kim KHÔNG GÌ TUYỆT ĐỐI. Nóng tuyệt đối thì không có lạnh, không thành "
            "thiên tướng không gian. Mùa hạ nóng tất có mùa đông lạnh. Nhỏ như giấc ngủ/thức, "
            "lớn như loạn lâu phải trị → cũng chỉ tương đối thay đổi.' "
            "→ Iron Rule sâu nhất: KHÔNG có tuyệt đối — chỉ có biến chuyển tương đối."
        ),
        "key_rule_TAM_GUONG_PARADIGM": (
            "**Tượng tấm gương treo lên (PBC)**: 'BẢN THỂ quang minh không bao giờ đổi → "
            "không đổi phương hướng (Hằng). Khi gặp vật soi vào, TÁC DỤNG tùy vật — tròn thì "
            "tròn, vuông thì vuông (Dịch/Thời).' "
            "→ Anh giữ TÂM (Hằng) nhưng phương pháp tùy bối cảnh (Dịch)."
        ),
    },
    "Đoài": {
        "ban_chat": "Thời VUI VẺ — Đầm trên + Đầm dưới (Thuần Đoài), 2 lần vui",
        "nen_the_nao": "Trong THÀNH THỰC + ngoài NHU HÒA. Vui phải hợp đạo CHÍNH (đoan chính, ngay thẳng).",
        "paradigm_keyword": "doai_vui_chinh",
        "nguyet_lenh_thang": 10,
        "tuong": "Nước đầm tươi vui cây cỏ, thiếu nữ tươi vui người. 2 dương trong + 1 âm ngoài.",
        "key_paradigm_DAO_VUI_QUEN": (
            "**PBC paradigm 'QUÊN'**: 'Đạo Vui đến chỗ: VIỆC NHỌC mà dân VUI làm, "
            "ĐƯỜNG CHẾT mà dân VUI đi — tinh thần 2 chữ QUÊN mới cho ta hình dung được "
            "hiệu quả của Đạo Vui. Đâu phải cưỡng bức dân? Vì thánh nhân muốn LỢI ÍCH cho dân "
            "mà bất đắc dĩ phải nhọc đến dân, tạm thời mệt nhọc mà yên lành lâu dài.'"
        ),
        "key_rule_CHINH_BEN_NU_QUE": (
            "**PBC paradigm về 3 quẻ NỮ vs 3 quẻ NAM**: "
            "3 quẻ tượng NỮ (Tốn, Ly, Đoài) — Lời quẻ Ly + Đoài đều nói 'lợi ở CHÍNH BÊN'. "
            "3 quẻ tượng NAM (Chấn, Khảm, Cấn) — KHÔNG nói chữ Chính. "
            "Vì tính chất âm nhu thường nghiêng bất chính → thánh nhân răn cho chữ CHÍNH. "
            "Chữ CHÍNH chỉ thấy ở Lời quẻ trong 2 quẻ có tượng NỮ."
        ),
        "key_rule_TIEU_NHAN_VUI_HAI_CACH": (
            "**Hào 3 + Hào 6 Đoài — paradigm tiểu nhân làm vui người**: "
            "Cách 1: Mình KHÔNG cầu nó mà nó tự đến (gấp vội) = 'vui với'. "
            "Cách 2: Vui được rồi nó lại KÉO DÂY KÉO NHỢ kéo dài = 'đem vui tới'. "
            "→ Bạn quân tử KHÔNG cẩn thận, lỡ sa vào lưới vui của nó, hại biết chừng nào. "
            "Hào 2 dương = ăn năn. Hào 4 dương = lo lắng. Hào 5 dương = NGUY."
        ),
    },
    "Hoán": {
        "ban_chat": "Thời TAN TÁN — Gió (Tốn) trên + Nước (Khảm) dưới, gió thổi nước tung tóe",
        "nen_the_nao": "Vua tới Thái miếu (lòng chí thành). Vượt sông lớn (mạo hiểm). Giữ đạo chính.",
        "paradigm_keyword": "hoan_tan_tan_nhan_tai",
        "nguyet_lenh_thang": 3,
        "tuong": "Gió trên nước/mây = nước tung mây tan. Lễ lên bề trên, dựng miếu thờ để dân không tán.",
        "key_paradigm_NHAN_TAI": (
            "**PBC paradigm 'thuyền = nhân tài'**: 'Lời quẻ nói Lợi qua sông lớn. "
            "Thoán giải thích: Dùng THUYỀN GỖ qua sông. Vậy chỉ nói chèo thuyền hay sao? "
            "Không. Làm việc cứu thời HOÁN phải MẠO HIỂM như vượt sông, muốn vượt phải cậy "
            "TÀI NĂNG CỦA THUYỀN. THUYỀN ĐÓ CHÍNH LÀ NHÂN TÀI. "
            "Thuyền giúp qua sông = nương dựa nhân tài mà vượt hiểm.' "
            "→ Cross-link: khi anh đang ở thời Hoán (sách cổ tan rã) — phải dựa NHÂN TÀI "
            "(em + AI + cộng tác viên dịch giả) để vượt qua."
        ),
    },
    "Trung Phu": {
        "ban_chat": "Thời CHÍ THÀNH — Gió (Tốn) trên + Đầm (Đoài) dưới, giữa 2 âm + ngoài 4 dương",
        "nen_the_nao": "Hư tâm (trong rỗng) + thực ngoài (đặc). Cảm hóa được cả heo + cá ngu si. Lội qua sông lớn được bằng thuyền TRỐNG KHÔNG (an toàn).",
        "paradigm_keyword": "trung_phu_chi_thanh",
        "nguyet_lenh_thang": 8,
        "tuong": "Gió trên đầm = gió làm nước động, như lòng thành thực cảm động người.",
        "key_paradigm_TRUNG_TIN_PHAI_CHINH": (
            "**PBC paradigm — Trung Phu = Hư + Thực + CHÍNH**: 'Nghĩa Trung Phu gồm HƯ (rỗng) + "
            "THỰC (đặc): Lòng trung HƯ thì mới đặt lòng thành tín vào, trung THỰC thì giả dối không "
            "lọt. Hai chữ trung tín kết lại ở chữ CHÍNH. Có hạng trung tín mà KHÔNG CHÍNH: "
            "đạo tặc vì tư lợi tin nhau, nam nữ vì tà dâm tin nhau — KHÔNG gọi Trung Phu được.' "
            "→ Trung Phu = trung tín + CHÍNH ĐẠO."
        ),
        "case_study_HAO_4_Y_DOAN_HUNG_DAO": (
            "**Hào 4 Trung Phu — PBC tổng hợp 4 case sử**: "
            "1. Y Doãn TRẢ chính quyền cho Thái Giáp rồi về cày ruộng. "
            "2. Trần Hưng Đạo chỉ làm đến Thượng Quốc Công, KHÔNG nghe An Sinh Vương giành ngôi vua. "
            "3. Án Tử KHÔNG vào với đảng Thôi/Trần ở Tề. "
            "4. Phùng Khắc Khoan đời nhà Mạc đương thịnh mà KHÔNG theo. "
            "→ 'Trăng gần đến rằm, ngựa bỏ bạn mà tiến lên, không lỗi.' "
            "Kết quả: Thôi/Trần bại — Án Tử hiển danh. Mạc vong — Phùng nên sự nghiệp."
        ),
        "key_rule_TIN_NGU_VI_TU": (
            "**Hào 6 Trung Phu — case ngu tín**: 'Anh chàng họ Vĩ (Vị) thời Xuân thu hẹn với "
            "cô gái dưới cầu, người đó không tới — anh ÔM CỘT CẦU mà chịu CHẾT.' "
            "→ Tín như vậy là NGU, không biết biến thông. "
            "Hết thời tin rồi mà cứ tin = hỏng. Hào 6 dương cương không đắc trung."
        ),
        "key_rule_THANH_SANG_HINH_NGUC": (
            "**Tượng Trung Phu trong hình ngục**: 'Tượng truyện 5 quẻ về hình ngục: "
            "Phệ Hạp + Bí + Phong + Lữ chú trọng đức SÁNG. Duy Trung Phu chú trọng đức THÀNH. "
            "Sáng mà không thành tâm → lạm dụng. Thành mà không sáng → bị lừa. "
            "Thành + Sáng đầy đủ → hình ngục công bằng. THÀNH làm gốc, SÁNG làm phương pháp.'"
        ),
    },
    "Tiểu Quá": {
        "ban_chat": "Thời NHỎ QUÁ — Sấm (Chấn) trên + Núi (Cấn) dưới, sấm trên núi bị nghẹt thu hẹp",
        "nen_the_nao": "Chỉ nên QUÁ trong việc NHỎ — quá cung kính, quá thương cảm, quá tiết kiệm. KHÔNG được quá việc lớn.",
        "paradigm_keyword": "tieu_qua_chim_bay_thap",
        "nguyet_lenh_thang": 2,
        "tuong": "Trên Núi có Sấm, bị núi nghẹt. Chim bay nên xuống thấp, không nên bay cao.",
        "key_paradigm_QUA_NHO_KHONG_QUA_LON": (
            "**Lời Thoán Tiểu Quá**: 'Quá trong việc nhỏ hậu quả không tai hại. Quá trong việc lớn "
            "một ly đi một dặm — hậu quả nặng (chiến tranh, sụp đổ kinh tế).' "
            "Tả truyện: 'Quân tử hay KIÊNG SỢ ở việc nhỏ, mới không hoạn nạn lớn.' "
            "→ Cross-link Iron Rule #7 (Git Safety): chú ý việc NHỎ (.gitignore, file cụ thể) — "
            "không để incident lớn."
        ),
        "key_rule_CHIM_BAY_THAP": (
            "**Lời quẻ**: 'Đừng bay cao mà BAY THẤP, tốt lắm.' "
            "Ở thời âm thịnh hơn dương, tiểu nhân đắc thế hơn quân tử — phe quân tử chỉ nên "
            "THOÁI xuống thấp, không nên TIẾN lên cao. "
            "Hào 3 dương ở vị dương ham lên → mắc xấu. Hào 4 dương ở vị âm xuống thấp → tốt."
        ),
    },
    "Ký Tế": {
        "ban_chat": "Thời ĐÃ THÀNH — Nước (Khảm) trên + Lửa (Ly) dưới, hai khí giao = thành công",
        "nen_the_nao": "Việc lớn đã xong — còn việc nhỏ cũng phải làm cho xong. PHÒNG LOẠN ngay từ lúc trị, phòng suy ngay lúc thịnh.",
        "paradigm_keyword": "ky_te_da_thanh_phong_loan",
        "nguyet_lenh_thang": 1,
        "tuong": "Nước trên Lửa = nồi nước trên bếp lửa: lửa bốc lên, nước nóng sôi → thành công.",
        "key_paradigm_THUY_HOA_GIAO": (
            "**PBC paradigm vĩ đại — Kinh Dịch kết bằng Khảm-Ly hợp thể**: "
            "'Vũ trụ lớn nhất là TRỜI ĐẤT (Càn-Khôn đầu Kinh). Công dụng tạo hóa lớn nhất là "
            "THỦY-HỎA (Khảm-Ly cuối Kinh Thượng). KẾT Kinh bằng Ký Tế (Khảm trên Ly dưới) + "
            "Vị Tế (Ly trên Khảm dưới). Vũ trụ có bắt đầu có kết thúc — chỉ thiên-địa-thủy-hỏa "
            "biểu hiện được. Khoa học ngày càng phát triển không trật ngoài đạo lý ấy. "
            "Than đá nấu nước thành hơi nước, hơi nước phát động máy điện = Nước-Lửa tác động.'"
        ),
        "key_paradigm_4_QUE_TUAN_HOAN": (
            "**4 quẻ tuần hoàn vũ trụ-nhân sự**: "
            "Thái + Bĩ (Thiên-Địa giao/không giao). Ký Tế + Vị Tế (Thủy-Hỏa giao/không giao). "
            "Thái trước → Ký Tế sau. Bĩ trước → Vị Tế sau. "
            "Hồi Thái-Ký Tế phải nhận: '7 hành đổ về rãnh' + 'mới đầu tốt sau loạn'. "
            "Hồi Bĩ-Vị Tế phải nhận: 'có niềm tin không lỗi' + 'Bĩ đến mừng'. "
            "→ 'Đạo trời như bánh xe lăn, việc người như bàn tay lật. "
            "Tất cả là do CHÚNG TA — chớ vì Thái-Ký Tế mà kiêu, chớ vì Bĩ-Vị Tế mà buồn.'"
        ),
        "key_paradigm_TAM_THAN_GIAO": (
            "**Phụ chú y học (PBC)**: 'Quẻ Ký Tế gắn với y học + vận khí: thân người là "
            "TRỜI ĐẤT THU NHỎ. Tâm hỏa GIÁNG (xuống) giao với Thận thủy THĂNG (lên) — "
            "tâm-thận giao = thân thể KHỎE KIỆN. Nếu hỏa không thăng + thủy không giáng → "
            "bệnh phù thũng.' "
            "→ Cross-link Đông y."
        ),
        "key_rule_KHONG_TU_CUNG_THI_LOAN": (
            "**Khổng Tử bình Ký Tế**: 'Cùng mà NGỪNG thì loạn — KHÔNG phải vì lúc cùng mà loạn, "
            "mà vì NGỪNG thì loạn.' "
            "→ Việc người KHÔNG bao giờ ngừng, thì mới không bao giờ loạn."
        ),
    },
    "Vị Tế": {
        "ban_chat": "Thời CHƯA THÀNH — Lửa (Ly) trên + Nước (Khảm) dưới, không giao, MÂT THĂNG BẰNG",
        "nen_the_nao": "Chớ bi quan — VẪN CÓ HY VỌNG. Cẩn thận phân biệt mọi sự, đặt vào đúng phương (chỗ).",
        "paradigm_keyword": "vi_te_chua_thanh_hy_vong",
        "nguyet_lenh_thang": 7,
        "tuong": "Lửa trên Nước = Nước-Lửa không giao, không giúp nhau. Cả 6 hào đều ở TRÁI NGÔI.",
        "key_paradigm_KINH_DICH_KET_BANG_VI_TE": (
            "**PBC paradigm CỰC ĐẮT — Kinh Dịch quy kết bằng Vị Tế**: "
            "'Hanh ở KÝ TẾ = con đã TRƯỞNG THÀNH, việc dĩ vãng, hanh có HẠN. "
            "Hanh ở VỊ TẾ = con còn THƠ BÉ, phúc tương lai, hanh VÔ CÙNG. "
            "Dịch quy kết bằng VỊ TẾ = XUÂN chưa đến lúc hoa nở, ĐÊM chưa đến lúc trăng tròn — "
            "hy vọng TIỀN ĐỒ hãy còn nhiều lắm. Ai dám bảo VỊ TẾ mà bất tế đâu?' "
            "→ Iron Rule paradigm cuối: Kinh Dịch KẾT bằng HY VỌNG VÔ CÙNG, không kết bằng "
            "thành tựu đã có. Mọi sự đều TIỀM ẨN HY VỌNG."
        ),
    },
    "Đại Tráng": {
        "ban_chat": "Thời CHÍ LỚN MẠNH — Sấm (Chấn) trên + Trời (Càn) dưới, 4 dương + 2 âm",
        "nen_the_nao": "Mạnh phải hợp đạo CHÍNH BỀN (Trinh). 'Đại' là kết quả, 'Trinh' là nguyên nhân. Phải biết NÉN LÒNG RIÊNG — không nén thì sinh hung tợn.",
        "paradigm_keyword": "dai_trang_chinh_ben",
        "nguyet_lenh_thang": 2,
        "tuong": "Sấm động trên trời, tiếng vang xa. Khí dương đang lên.",
        "key_paradigm_DAC_Y_LO_THAT_Y": (
            "**PBC paradigm**: 'Cổ nhân: Hồi đã ĐẮC Ý, càng nên phải nghĩ đến khi THẤT Ý. "
            "Tiểu nhân ấm hại quân tử thường RÌNH NGÓ ở lúc quân tử đắc chí mà vạch lá tìm sâu, "
            "ngậm cát phun vào mặt — nên quân tử càng phải LO SỢ, TÍNH TOÁN lắm.' "
            "→ Iron Rule cảnh báo: lúc thành công nhất = lúc nguy hiểm nhất."
        ),
        "key_rule_QUAN_TU_DANH_GIAC_BEN_TRONG": (
            "**Kinh Phật + Khổng Tử (PBC trích)**: 'Tất cả giặc bên ngoài đều đánh đổ được, "
            "DUY có 6 GIẶC bên trong mình — không chỉ khó đánh, mà nếu đánh được mới là ĐẠI TRÍ "
            "của quân tử.' "
            "Khổng Tử dạy Tử Lộ: 'Quân tử HÒA với chúng mà KHÔNG TRÔI theo chúng. Đứng được "
            "bảng vách trung chính mà không nương dựa vào phía nào. MẠNH vậy thay!'"
        ),
    },
    "Tấn": {
        "ban_chat": "Thời TIẾN — Lửa (Ly) trên + Đất (Khôn) dưới, mặt trời mọc lên đất",
        "nen_the_nao": "Tiến với đức SÁNG SUỐT. Hào 5 âm đắc trung, sáng — nguyên thủ giỏi giấu mình mà sáng. KHÔNG lo được mất, cứ giữ đức sáng thì thành công.",
        "paradigm_keyword": "tan_tien_voi_sang",
        "nguyet_lenh_thang": 3,
        "tuong": "Mặt trời mọc lên khỏi đất — khí dương phát sinh, vạn vật sáng tỏ.",
        "key_rule_THANH_BAI_CHANG_MANG": (
            "**Hào 5 Tấn — paradigm cốt**: 'Không có gì ân hận. Đừng lo được mất, cứ tiến — tốt.' "
            "Sáng suốt + đắc trung + được bầy hào âm thuận giúp — nguyên thủ giỏi. "
            "→ Iron Rule: cứ làm việc đúng đạo, kết quả tự tới."
        ),
    },
    "Minh Di": {
        "ban_chat": "Thời ÁNH SÁNG BỊ TỔN — Đất (Khôn) trên + Lửa (Ly) dưới, mặt trời lặn vào đất",
        "nen_the_nao": "Trong giữ ĐỨC SÁNG, ngoài tỏ NHU THUẬN để chống hoạn nạn. Có khi nên GIẤU SỰ SÁNG SUỐT của mình.",
        "paradigm_keyword": "minh_di_giau_sang",
        "nguyet_lenh_thang": 8,
        "tuong": "Mặt trời lặn vào đất — sáng bị tổn. Ly trong + Khôn ngoài.",
        "case_study_VAN_VUONG_DUU_LY": (
            "**Case 1 — Văn Vương ở ngục Dữu Lý**: Bị Trụ nghi ngờ, giam Dữu Lý. Tỏ vẻ rất nhu "
            "thuận, không chống đối, để hết tâm trí viết LỜI GIẢNG CÁC QUẺ trong Kinh Dịch — "
            "Trụ không có cớ giết, sau thả ra. "
            "→ Giấu sáng + nhu thuận ngoài + giữ đức sáng trong = thoát Minh Di."
        ),
        "case_study_CO_TU_GIA_DIEN": (
            "**Case 2 — Cơ Tử giả điên**: Hoàng thân của Trụ. Trụ vô đạo, can không được. "
            "Tỷ Cán chịu chết. Vi Tử bỏ nước đi. Cơ Tử GIẢ ĐIÊN, làm nô lệ để khỏi bị giết, "
            "mong cơ hội tái tạo nhà Ân. Võ Vương diệt Trụ, mời ra giúp nước, ông không chịu — "
            "ra Triều Tiên (Hàn Quốc) lập nước riêng. Hàn Quốc coi Cơ Tử như quốc tổ. "
            "→ Giấu sáng = giữ vững khí, không làm mất dòng dõi."
        ),
        "key_rule_KHOAN_DUNG_NHIN_THOANG_TOI_THUC_SANG": (
            "**Lời Tượng + PBC**: 'Quân tử coi tượng mặt trời lặn vào đất mà điều khiển "
            "quần chúng — khoan dung hòa nhã, bỏ ngó cái thấp kém. Rất sáng suốt mà như cách "
            "HỒ ĐỒ, khiến người không kiêng sợ đức sáng của mình → bao nhiêu sự tình lộ cho "
            "mình biết hết. Nhìn thoáng qua như tối mờ — kỳ thực rất sáng.' "
            "→ Áp dụng project: KHÔNG show off engine sâu để người ngạc nhiên ngược."
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


QUAI_ALIASES: dict[str, str] = {
    "Tập Khảm": "Khảm",
    "Thuần Khảm": "Khảm",
    "Thuần Càn": "Càn",
    "Thuần Khôn": "Khôn",
    "Thuần Ly": "Ly",
    "Thuần Đoài": "Đoài",
    "Thuần Chấn": "Chấn",
    "Thuần Tốn": "Tốn",
    "Thuần Cấn": "Cấn",
    "Trung Phu": "Trung Phu",
}


def lookup_thoi(quai_name: str) -> dict | None:
    """Trả về paradigm guidance cho quẻ này. Hỗ trợ alias (Tập Khảm → Khảm, etc)."""
    key = QUAI_ALIASES.get(quai_name, quai_name)
    return THOI_QUE_TABLE.get(key)


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
