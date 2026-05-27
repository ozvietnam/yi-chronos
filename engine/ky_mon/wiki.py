"""Concept dictionary cho Kỳ Môn Độn Giáp — UI tooltip + reference.

Theo paradigm Master-Apprentice với tổ sư Lưu Bá Ôn (1311-1375).
Mô tả ngắn (1-2 câu/concept), không nhồi knowledge. Anh thâm nhuần sách
"Bá Ôn Bí Truyền KMDG" sau sẽ enrich qua skill folder hermes_yi/skills/ky-mon/.

Paradigm: 9 cung × 8 môn × 9 tinh × 8 thần là BẢN ĐỒ năng lượng thời-không,
KHÔNG phải fortune dictionary. Mỗi yếu tố = một loại "tính" — đối ứng tâm cảnh người hỏi.
"""

WIKI = {
    # ─── 8 cung Hậu Thiên + Trung cung ───
    # Mỗi cung KMDG = 1 Quẻ Thuần trong Kinh Dịch (gốc paradigm Bát Quái Hậu Thiên).
    # paradigm: trace ngược cung KMDG → Quẻ Thuần → đọc tính theo Trình Di + Chu Hy.
    "cung": {
        "Khảm": {
            "zh": "坎", "direction": "Bắc", "ngu_hanh": "Thủy",
            "desc": "Cung Khảm — nước chảy xuống, hiểm trong êm. Tính: ẩn náu, suy tư, dòng chảy ngầm.",
            "que_id": 29, "que_name": "Tập Khảm 習坎",
            "loi_kinh": "Tập Khảm, hữu phu, duy tâm hanh, hành hữu thượng.",
            "loi_kinh_vn": "Hiểm chồng hiểm, có chân thật, riêng tâm hanh, đi có thưởng.",
            "tam_phap_cot": "Trong hiểm chồng hiểm, chỉ TÂM thật mới hanh — bên ngoài vẫn hiểm. 'Thường đức hành, tập giáo sự' — vượt hiểm bằng tích lũy đều như nước chảy, không đột phá.",
            "insight_for_kmdg": "Cung Khảm có Thiên Bồng/Thiên Nhuế = hiểm chồng hiểm (Tập Khảm). Có Thiên Tâm = nước chảy chưa đầy nhưng sắp bình. Có Tử môn ở Khảm = 'hệ dụng huy mặc' (trói gai 3 năm hung).",
            "kinh_dich_que": "01-kien | 02-khon | 29-kham (chính)",
        },
        "Cấn": {
            "zh": "艮", "direction": "Đông Bắc", "ngu_hanh": "Thổ",
            "desc": "Cung Cấn — núi đứng yên. Tính: dừng đúng lúc, biết giới hạn, thiền định.",
            "que_id": 52, "que_name": "Cấn 艮 (thuần)",
            "loi_kinh": "Cấn kỳ bối, bất hoạch kỳ thân. Hành kỳ đình, bất kiến kỳ nhân. Vô cữu.",
            "loi_kinh_vn": "Đậu ở lưng, không thấy thân. Đi ở sân, không thấy người. Không lỗi.",
            "tam_phap_cot": "'Thì chỉ tắc chỉ, thì hành tắc hành' — biết THỜI dừng hay đi. 'Tư bất xuất kỳ vị' — nghĩ không vượt vị mình.",
            "insight_for_kmdg": "Cung Cấn có Khai môn = 'cấn kỳ chỉ lợi vĩnh trinh' (dừng từ ngón chân, đại cát). Có Tử môn = 'cấn kỳ hạn liệt kỳ nhân' (dừng sai chỗ, gãy đôi). Đôn cấn (Thượng Cửu) = dừng dày dặn = cát tuyệt.",
            "kinh_dich_que": "52-can-hexagram",
        },
        "Chấn": {
            "zh": "震", "direction": "Đông", "ngu_hanh": "Mộc",
            "desc": "Cung Chấn — sấm động. Tính: khởi động, đột phá, thanh xuân.",
            "que_id": 51, "que_name": "Chấn 震 (thuần)",
            "loi_kinh": "Chấn, hanh. Chấn lai hư hư, tiếu ngôn yết yết. Chấn kinh bách lý, bất tang chủy sưởng.",
            "loi_kinh_vn": "Chấn hanh. Sấm đến run, sau cười nói. Giật mình trăm dặm, không rời thìa rượu tế.",
            "tam_phap_cot": "'Khủng trí phúc' — sợ đúng đem phúc đến. 'Bất tang chủy sưởng' — trong nguy biến tột, chủ tế vẫn giữ thìa rượu (giữ paradigm).",
            "insight_for_kmdg": "Cung Chấn có Hưu môn = sấm đến nghỉ, biết sợ → cát. Có Tử môn = sấm bị bùn ngập (Cửu Tứ 'chấn toại nê') = không lên được. Sấm vu lân (Thượng Lục) — thấy người khác bị sấm thì tự tu = cảnh báo cát.",
            "kinh_dich_que": "51-chan",
        },
        "Tốn": {
            "zh": "巽", "direction": "Đông Nam", "ngu_hanh": "Mộc",
            "desc": "Cung Tốn — gió luồn. Tính: thuận theo, len lỏi, lan tỏa.",
            "que_id": 57, "que_name": "Tốn 巽 (thuần)",
            "loi_kinh": "Tốn, tiểu hanh, lợi hữu du vãng, lợi kiến đại nhân.",
            "loi_kinh_vn": "Tốn: hanh nhỏ, lợi có thừa đi, lợi thấy đại nhân.",
            "tam_phap_cot": "'Trùng tốn dĩ thân mệnh' — gió lặp 2 lần, lệnh phải lặp nhiều lần dân mới ngấm. CẦN ĐẠI NHÂN dẫn dắt — mềm một mình không đủ.",
            "insight_for_kmdg": "Cung Tốn có Sinh môn = gió thổi sinh sôi (đại cát). Có Thiên Phụ (Mộc) = phù trợ đại cát. Có Tử môn = 'tang kỳ tư phủ' (Thượng Cửu — nhún mất khí cụ, dù chính cũng hung). 'Tần tốn lận' (Cửu Tam) = nhún liên tục = giả.",
            "kinh_dich_que": "57-ton-hexagram",
        },
        "Ly": {
            "zh": "離", "direction": "Nam", "ngu_hanh": "Hỏa",
            "desc": "Cung Ly — lửa sáng, phụ thuộc vào chất đốt. Tính: chiếu rọi, văn minh, danh tiếng.",
            "que_id": 30, "que_name": "Ly 離 (thuần)",
            "loi_kinh": "Ly, lợi trinh, hanh. Súc tẫn ngưu cát.",
            "loi_kinh_vn": "Ly: lợi chính, hanh. Nuôi bò cái thì tốt.",
            "tam_phap_cot": "'Hoàng ly nguyên cát' (Lục Nhị) — TRUNG (vàng) > CỰC (đỏ). Sáng vừa phải bền hơn sáng chói. 'Kế minh chiếu tứ phương' — sáng phải truyền tiếp.",
            "insight_for_kmdg": "Cung Ly có Cảnh môn = sáng tỏ truyền tin (cát trung bình). Có Thiên Anh (Hỏa, sáng) = Ly thuần. Có Tử môn = 'đột như kỳ lai' (Cửu Tứ, sáng đột bất chính bị diệt). Trên ngôi vua mềm + sợ + chảy nước mắt → giữ được (Lục Ngũ).",
            "kinh_dich_que": "30-ly-hexagram",
        },
        "Khôn": {
            "zh": "坤", "direction": "Tây Nam", "ngu_hanh": "Thổ",
            "desc": "Cung Khôn — đất rộng nhận hết. Tính: chứa đựng, mẹ, nuôi dưỡng.",
            "que_id": 2, "que_name": "Khôn 坤 (thuần)",
            "loi_kinh": "Khôn nguyên hanh, lợi tẫn mã chi trinh. Quân tử hữu du vãng. Tiên mê, hậu đắc, chủ lợi.",
            "loi_kinh_vn": "Khôn đầu cả, hanh thông. Lợi về trinh của ngựa cái. Trước mê, sau được.",
            "tam_phap_cot": "'Lý sương kiên băng chí' (Sơ Lục) — xéo sương biết váng rắn tới. Quan sát dấu hiệu sớm. 4 đức nhưng trinh là MỀM THUẬN (≠ Càn cứng). 'Trực phương đại bất tập' (Lục Nhị) — đất tự nhiên 3 đức.",
            "insight_for_kmdg": "Cung Khôn có Sinh môn = đất nuôi (đại cát). Có Trị Phù = đại cát kép. Có Tử môn = đất chôn = táng (đại hung). Quan sát 'sương' (yếu tố nhỏ trong bàn) để dự đoán 'băng rắn' (xu hướng lớn).",
            "kinh_dich_que": "02-khon",
        },
        "Đoài": {
            "zh": "兌", "direction": "Tây", "ngu_hanh": "Kim",
            "desc": "Cung Đoài — đầm vui. Tính: vui vẻ, giao đãi, thiếu nữ.",
            "que_id": 58, "que_name": "Đoài 兌 (thuần)",
            "loi_kinh": "Đoài, hanh, lợi trinh.",
            "loi_kinh_vn": "Đoài: hanh thông, lợi về chính.",
            "tam_phap_cot": "'Cương trung nhu ngoại' — cứng giữa (chính) mềm ngoài (hòa). 'Duyệt dĩ tiên dân, dân vong kỳ lao' — vui dẫn trước, dân quên nhọc. 'Lệ trạch bằng hữu giảng tập' — 2 đầm tiếp = bạn bè học hỏi.",
            "insight_for_kmdg": "Cung Đoài có Khai môn = vui đúng mở ra (đại cát). Có Cảnh môn (Hỏa) = Hỏa khắc Kim = vui bị thiêu (cảnh báo). 'Lai duyệt hung' (Lục Tam) = cố mời vui = nịnh = hung. 'Hòa duyệt cát' (Sơ Cửu) = vui tự nhiên.",
            "kinh_dich_que": "58-doai",
        },
        "Càn": {
            "zh": "乾", "direction": "Tây Bắc", "ngu_hanh": "Kim",
            "desc": "Cung Càn — trời cương kiện. Tính: chủ động, lãnh đạo, cha.",
            "que_id": 1, "que_name": "Càn 乾 (thuần)",
            "loi_kinh": "Càn, nguyên hanh lợi trinh.",
            "loi_kinh_vn": "Càn: đầu cả, hanh thông, lợi tốt, chính bền.",
            "tam_phap_cot": "4 đức nguyên-hanh-lợi-trinh ĐẦY ĐỦ (chỉ Càn + Khôn có). 6 hào = 6 cảnh giới đời quân tử (tiềm long → kháng long). 'Dụng Cửu: kiến quần long vô thủ, cát' — không tự cứng đầu.",
            "insight_for_kmdg": "Cung Càn có Khai môn = trời mở (đại cát). Có Trị Phù = vua + chủ (cát kép). Có Tử môn = 'kháng long hữu hối' (rồng quá cực = ăn năn). Lực Dương cương — chỉ chính bền + biết thời mới giữ được.",
            "kinh_dich_que": "01-kien",
        },
        "Trung": {
            "zh": "中", "direction": "Trung tâm", "ngu_hanh": "Thổ",
            "desc": "Trung cung — không có môn (lấy Khôn thay), là trục xoay. Tính: chính giữa, gốc.",
            "que_id": None, "que_name": "Không có quẻ thuần riêng (gộp Khôn)",
            "loi_kinh": "",
            "loi_kinh_vn": "Trung cung trong Lạc Thư là điểm 5 (ngũ) — Thổ tại trung — không có quẻ thuần Bát Quái riêng. KMDG truyền thống GỘP Trung vào Khôn (cùng Thổ).",
            "tam_phap_cot": "Trung là TRỤC. Trị Phù + Thiên Cầm luôn ở Trung khi bàn ổn định. Không có môn ở Trung vì 8 môn đại diện 8 hướng — Trung không có hướng.",
            "insight_for_kmdg": "Cung Trung chứa Thiên Cầm (luôn ở đây) — sao Thổ trung tâm, không di chuyển. Trị Phù khi 'ký phục' (đã hồi) cũng về Trung. Trung cung mạnh = bàn ổn. Trung yếu = bàn loạn.",
            "kinh_dich_que": "(gộp 02-khon — cùng Thổ)",
        },
    },

    # ─── 8 môn ───
    "mon": {
        "Hưu": {"zh": "休門", "ngu_hanh": "Thủy", "cat_hung": "cát",
                "desc": "Nghỉ ngơi, dừng việc, ẩn náu. Tốt cho dưỡng sinh, gặp người trên."},
        "Sinh": {"zh": "生門", "ngu_hanh": "Thổ", "cat_hung": "đại cát",
                 "desc": "Khởi sự, sinh sôi, gặt hái. Tốt cho khởi nghiệp, cầu tài, hôn nhân."},
        "Thương": {"zh": "傷門", "ngu_hanh": "Mộc", "cat_hung": "hung",
                   "desc": "Bị tổn thương, va chạm, săn bắt. Đừng đi đường xa, dễ tai nạn. Tốt cho thợ săn, võ tướng."},
        "Đỗ": {"zh": "杜門", "ngu_hanh": "Mộc", "cat_hung": "trung bình",
               "desc": "Đóng kín, ẩn náu, bảo mật. Tốt cho học hành, thiền tĩnh, giấu mình."},
        "Cảnh": {"zh": "景門", "ngu_hanh": "Hỏa", "cat_hung": "trung bình",
                 "desc": "Sáng tỏ, truyền tin, văn thư. Tốt cho thi cử, ký kết, biểu diễn."},
        "Tử": {"zh": "死門", "ngu_hanh": "Thổ", "cat_hung": "đại hung",
               "desc": "Chết, kết thúc, an táng. Đại hung cho khởi sự, tốt cho việc tang."},
        "Kinh": {"zh": "驚門", "ngu_hanh": "Kim", "cat_hung": "hung",
                 "desc": "Giật mình, kinh hãi, kiện tụng. Đừng tranh cãi, cẩn thận tin xấu."},
        "Khai": {"zh": "開門", "ngu_hanh": "Kim", "cat_hung": "đại cát",
                 "desc": "Mở đầu, công khai, hành sự lớn. Tốt cho mọi việc trừ tang lễ."},
    },

    # ─── 9 tinh (cat_hung CORRECTED per Đàm Liên Chương I phần IV) ───
    "tinh": {
        "Thiên Bồng": {"zh": "天蓬", "ngu_hanh": "Thủy", "cat_hung": "đại hung",
                       "desc": "Đầu hung tinh — Bắc Đẩu thứ nhất. Chủ trộm cướp, dâm dục, mưu kế đen. Hợp xuân/hè, khắc thu/đông."},
        "Thiên Nhậm": {"zh": "天任", "ngu_hanh": "Thổ", "cat_hung": "cát",
                       "desc": "Tiểu cát. Bảo trì, đảm nhận. Cát cho việc lâu dài, tích lũy."},
        "Thiên Xung": {"zh": "天沖", "ngu_hanh": "Mộc", "cat_hung": "cát",
                       "desc": "Tiểu cát. Kích phạt, xung đột. Tốt cho người võ, tranh đấu chính nghĩa."},
        "Thiên Phụ": {"zh": "天輔", "ngu_hanh": "Mộc", "cat_hung": "đại cát",
                      "desc": "Đại cát. Phù trợ. Đại cát cho học hành, văn thư, du lịch."},
        "Thiên Cầm": {"zh": "天禽", "ngu_hanh": "Thổ", "cat_hung": "đại cát",
                      "desc": "Đại cát. Trung tâm, ổn định (luôn ở Trung cung). Đi cùng Trị Phù."},
        "Thiên Tâm": {"zh": "天心", "ngu_hanh": "Kim", "cat_hung": "đại cát",
                      "desc": "Đại cát. Y dược, lành bệnh. Cát cho sức khỏe, nghiên cứu sâu."},
        "Thiên Trụ": {"zh": "天柱", "ngu_hanh": "Kim", "cat_hung": "hung",
                      "desc": "Tiểu hung. Phòng thủ, cố thủ. Cát cho giữ thành, bất lợi cho công thành."},
        "Thiên Anh": {"zh": "天英", "ngu_hanh": "Hỏa", "cat_hung": "hung",
                      "desc": "Tiểu hung. Chiếu rọi, văn thư, danh tiếng. Hư danh, dễ bị hỏa thiêu."},
        "Thiên Nhuế": {"zh": "天芮", "ngu_hanh": "Thổ", "cat_hung": "đại hung",
                       "desc": "Đầu bệnh tinh. Chủ bệnh tật, tang sự. Tránh đi xa, mua bán quan trọng. Hợp đông/thu, khắc xuân/hè."},
    },

    # ─── 8 thần ───
    "than": {
        "Trị Phù": {"zh": "值符", "cat_hung": "đại cát",
                    "desc": "Đứng đầu Bát thần — chủ tể vận khí cuộc bàn. Đi đến đâu cát đến đó."},
        "Đằng Xà": {"zh": "螣蛇", "cat_hung": "hung",
                    "desc": "Ảo, biến hoá, mộng mị. Chủ tin đồn, mâu thuẫn nhỏ, lừa đảo."},
        "Thái Âm": {"zh": "太陰", "cat_hung": "cát",
                    "desc": "Kín đáo, mưu sau lưng. Cát cho việc bí mật, không cát cho công khai."},
        "Lục Hợp": {"zh": "六合", "cat_hung": "cát",
                    "desc": "Hòa hợp, kết giao, hôn nhân. Cát cho thương lượng, môi giới."},
        "Câu Trần": {"zh": "勾陳", "cat_hung": "hung",
                     "desc": "Hình thương, kiện tụng, ràng buộc. Chủ việc dây dưa khó dứt."},
        "Chu Tước": {"zh": "朱雀", "cat_hung": "hung",
                     "desc": "Truyền tin (thường tin xấu), thị phi, lời gièm. Cẩn thận khẩu thiệt."},
        "Cửu Địa": {"zh": "九地", "cat_hung": "cát",
                    "desc": "Ẩn náu, mai phục, nuôi dưỡng. Cát cho việc lâu dài, tránh xung đột."},
        "Cửu Thiên": {"zh": "九天", "cat_hung": "đại cát",
                      "desc": "Vươn cao, tiến quân, lập danh. Cát cho hành động mạnh, đi xa."},
    },

    # ─── Cấu trúc cuộc bàn ───
    "structure": {
        "Tam Kỳ": {"zh": "三奇",
                   "desc": "Ất 乙, Bính 丙, Đinh 丁 — 3 thiên can sáng, cát tinh. Ất=Nhật kỳ, Bính=Nguyệt kỳ, Đinh=Tinh kỳ."},
        "Lục Nghi": {"zh": "六儀",
                     "desc": "Mậu 戊, Kỷ 己, Canh 庚, Tân 辛, Nhâm 壬, Quý 癸 — 6 nghi ẩn 6 Giáp tuần thủ."},
        "Dương Cục": {"zh": "陽遁", "range": "Đông Chí → Hạ Chí",
                      "desc": "9 cục từ Đông Chí — số khí dương tăng. Cục số xếp theo tiết khí."},
        "Âm Cục": {"zh": "陰遁", "range": "Hạ Chí → Đông Chí",
                   "desc": "9 cục từ Hạ Chí — số khí âm tăng. Cục số xếp ngược chiều Dương Cục."},
        "Thượng/Trung/Hạ Nguyên": {"zh": "三元",
                                    "desc": "Mỗi tiết khí 15 ngày chia 3 nguyên × 5 ngày. Quyết định cục số cụ thể."},
        "Trị Phù — Trị Sử": {"zh": "值符值使",
                              "desc": "Trị Phù = ngôi sao chủ. Trị Sử = ngôi môn chủ. 2 điểm trục để luận toàn bàn."},
        "Thiên bàn — Địa bàn": {"zh": "天盤地盤",
                                "desc": "Địa bàn = vị trí cố định của Lục Nghi Tam Kỳ. Thiên bàn = vị trí xoay theo Trị Phù."},
        "Tuần thủ — Tuần không": {"zh": "旬首旬空",
                                   "desc": "Tuần thủ = Giáp khởi tuần. Tuần không = 2 chi không thuộc tuần đó (yếu khí)."},
    },

    # ─── Tổ sư (lineage cổ) ───
    "to_su": {
        "name": "Lưu Bá Ôn",
        "name_zh": "劉伯溫",
        "birth": "1311-07-01",
        "death": "1375-05-16",
        "title": "Tư Mã Hư Tịnh — Cố vấn Minh Thái Tổ Chu Nguyên Chương",
        "work": "Bá Ôn Bí Truyền Kỳ Môn Độn Giáp (truyền thuyết)",
        "lineage": "Cửu Thiên Huyền Nữ → Hoàng Đế → Phong Hậu → Khương Tử Nha → Trương Lương → Gia Cát Lượng → Lưu Bá Ôn",
        "lineage_note": "Lineage này là TRUYỀN THUYẾT cổ. Theo Đàm Liên (sách reference), Sử ký Tư Mã Thiên + Khổng Tử + tác phẩm trước Tần KHÔNG nhắc KMDG. Hậu Hán Thư của Phạm Hoa mới nhắc người am thông KMDG (Đông Hán, TK 2-3 SCN). Thực tế lịch sử: KMDG xuất hiện Đông Hán, không cổ hơn.",
        "paradigm": "Hệ thống KMDG cận đại stable + procedural. Phù hợp Author-Worldview-First.",
    },

    # ─── 5 Cổ thư KMDG canon (theo Đàm Liên Chương I) ───
    "co_thu_canon": {
        "Độn giáp diễn nghĩa": {"he": "Chuyển bàn", "note": "Thu nhập Tứ Khố Toàn Thư"},
        "Kỳ môn tống tông": {"he": "Chuyển bàn", "note": "Kỳ Môn Thống Tông — phổ biến nhất dân gian"},
        "Kỳ môn ngũ long quy": {"he": "Chuyển bàn", "note": ""},
        "Kỳ môn bí cực toàn thư": {"he": "Chuyển bàn", "note": ""},
        "Kỳ môn pháp khiếu": {"he": "Phi bàn", "note": "DUY NHẤT Phi bàn — sách Đàm Liên trình bày"},
    },

    # ─── 2 hệ KMDG ───
    "he_kmdg": {
        "Chuyển bàn 轉盤": {
            "desc": "Bàn xoay — Trị Phù + Trị Sử di chuyển theo cục số + nguyên. 4/5 cổ thư canon thuộc hệ này.",
            "popularity": "Phổ biến trong dân gian, ứng dụng nhiều",
            "difficulty": "Khó tìm sách viết nghiêm túc",
        },
        "Phi bàn 飛盤": {
            "desc": "Bàn bay — 9 cung + 9 tinh + 8 môn 'bay' theo quy luật bố cục riêng. 1/5 cổ thư canon (Pháp Khiếu).",
            "popularity": "Ít phổ biến hơn nhưng hệ thống hơn",
            "difficulty": "Đàm Liên trình bày chi tiết chương 4, 5, 6",
        },
    },

    # ─── Tam Kỳ Lục Nghi chi tiết (Đàm Liên Chương I) ───
    "tam_ky_luc_nghi": {
        "overview": "9 thiên can trong KMDG = Tam Kỳ + Lục Nghi (ẨN Giáp). Mỗi Lục Nghi đứng đầu 1 tuần Giáp.",
        "tam_ky": {
            "Nhật kỳ 日奇": {"can": "Ất 乙", "thien_the": "Mặt trời", "ngu_hanh": "Mộc"},
            "Nguyệt kỳ 月奇": {"can": "Bính 丙", "thien_the": "Mặt trăng", "ngu_hanh": "Hỏa"},
            "Tinh kỳ 星奇": {"can": "Đinh 丁", "thien_the": "Sao", "ngu_hanh": "Hỏa"},
        },
        "luc_nghi": {
            "Mậu nghi (戊)": "Giáp Tý tuần 甲子 — Giáp Tý ẩn dưới Mậu",
            "Kỷ nghi (己)": "Giáp Tuất tuần 甲戌 — Giáp Tuất ẩn dưới Kỷ",
            "Canh nghi (庚)": "Giáp Thân tuần 甲申 — Giáp Thân ẩn dưới Canh",
            "Tân nghi (辛)": "Giáp Ngọ tuần 甲午 — Giáp Ngọ ẩn dưới Tân",
            "Nhâm nghi (壬)": "Giáp Thìn tuần 甲辰 — Giáp Thìn ẩn dưới Nhâm",
            "Quý nghi (癸)": "Giáp Dần tuần 甲寅 — Giáp Dần ẩn dưới Quý",
        },
        "insight": "Giáp ẨN không xuất hiện trực tiếp trong bàn — chỉ thể hiện qua Lục Nghi. Đây là gốc tên 'Độn Giáp' (giấu Giáp).",
    },

    # ─── Cửu tinh: 2 hệ tên gọi song song ───
    "cuu_tinh_two_naming": {
        "overview": "9 sao KMDG có 2 cách gọi: theo TÊN (Thiên Bồng/Nhậm/...) và theo SỐ+MÀU (Nhất bạch/Nhị hắc/...). Cùng 1 sao.",
        "mapping": {
            "1 - Nhất bạch 一白 (trắng)": "Thiên Bồng 天蓬 — Thủy, đầu hung tinh",
            "2 - Nhị hắc 二黑 (đen)": "Thiên Nhuế 天芮 — Thổ, bệnh tinh",
            "3 - Tam bích 三碧 (lục)": "Thiên Xung 天沖 — Mộc, kích phạt",
            "4 - Tứ lục 四綠 (xanh)": "Thiên Phụ 天輔 — Mộc, phù trợ đại cát",
            "5 - Ngũ hoàng 五黃 (vàng)": "Thiên Cầm 天禽 — Thổ, trung cung",
            "6 - Lục bạch 六白 (trắng)": "Thiên Tâm 天心 — Kim, y dược",
            "7 - Thất xích 七赤 (đỏ)": "Thiên Trụ 天柱 — Kim, phòng thủ",
            "8 - Bát bạch 八白 (trắng)": "Thiên Nhậm 天任 — Thổ, bảo trì",
            "9 - Cửu tử 九紫 (tím)": "Thiên Anh 天英 — Hỏa, sáng",
        },
        "cross_school": "Hệ SỐ+MÀU dùng trong Huyền Không Phi Tinh phong thủy. KMDG dùng cả 2 hệ tùy context.",
    },

    # ─── Phương pháp an cục KMDG ───
    "phuong_phap_an_cuc": {
        "overview": "KMDG có 4 hệ thời gian (per Đàm Liên): niên gia / nguyệt gia / nhật gia / thời gia. Mỗi hệ có cách xác định Nguyên + cục số khác nhau.",
        "ky_mon_thoi_gia": "60 đơn vị (60 giờ) = 1 nguyên. Phổ biến nhất, library kinqimen support full.",
        "ky_mon_nguyet_gia": {
            "desc": "60 tháng (5 năm) = 1 nguyên",
            "rule_thuong_nguyen": "Niên can Giáp/Kỷ + niên chi Tứ Mạnh (Dần Thân Tỵ Hợi) → năm Giáp Tý Thượng Nguyên → cung Khảm số 1",
            "rule_trung_nguyen": "Niên chi Tứ Trọng (Tý Ngọ Mão Dậu) → năm Giáp Tý Trung Nguyên → cung Đoài số 7",
            "rule_ha_nguyen": "Niên chi Tứ Quý (Thìn Tuất Sửu Mùi) → năm Giáp Tý Hạ Nguyên → cung Tốn số 4. ALL âm độn.",
        },
        "duong_am_don": {
            "Dương độn 陽遁": "Đông Chí → Hạ Chí (6 tháng). 9 thiên can xếp THUẬN chiều (cung 1→9).",
            "Âm độn 陰遁": "Hạ Chí → Đông Chí (6 tháng). 9 thiên can xếp NGƯỢC chiều (cung 9→1).",
        },
    },

    # ─── Cấu trúc 4 tầng Âm Dương Bàn (Đàm Liên Chương I phần IV) ───
    "am_duong_ban_4_tang": {
        "overview": "Âm Dương Bàn hoàn chỉnh = 4 tầng đồng tâm. Chuyển bàn = 4 đường tròn xoay được. Phi bàn = 4 đường tròn cố định cùng mặt phẳng.",
        "tang_1_dia_ban": {
            "name": "Địa Bàn 地盤",
            "size": "Lớn nhất (đáy)",
            "movement": "CỐ ĐỊNH, không di chuyển",
            "content": "8 cung Bát Quái cố định + cơ sở chuẩn xác để bài bàn",
        },
        "tang_2_mon_ban": {
            "name": "Môn Bàn 門盤",
            "size": "Lớn thứ 2",
            "movement": "Chuyển bàn: tầng xoay được. Phi bàn: 8 môn biến đổi theo giờ",
            "content": "8 môn (Hưu Sinh Thương Đỗ Cảnh Tử Kinh Khai)",
        },
        "tang_3_thien_ban": {
            "name": "Thiên Bàn 天盤",
            "size": "Lớn thứ 3",
            "movement": "Chuyển động theo Trực Phù + Trực Sử",
            "content": "9 cung + Lục Nghi Tam Kỳ + 9 sao (Thiên Bồng/Nhậm/...)",
        },
        "tang_4_than_ban": {
            "name": "Thần Bàn 神盤",
            "size": "Nhỏ nhất (đỉnh)",
            "movement": "Phi bàn: chỉ 1 đường tròn (do Thiên Bàn lộ rõ)",
            "content": "8 thần thứ tự: Trực Phù → Đằng Xà → Thái Âm → Lục Hợp → Câu Trần → Chu Tước (Huyền Vũ) → Cửu Địa → Cửu Thiên",
        },
        "trung_cung_trick": "Trung cung số 5 GỬI vào cung Khôn số 2 (vì 3 tầng dưới che lấp Trung cung — không thể nhìn thấy trực tiếp).",
    },

    # ─── Quy tắc "Theo 3 tránh 5" (Đàm Liên Chương I phần IV) ───
    "theo_3_tranh_5": {
        "proverb": "Theo 3 tránh 5 (cho 8 môn)",
        "cat_mon": ["Khai môn", "Hưu môn", "Sinh môn"],
        "hung_mon": ["Thương môn", "Đỗ môn", "Cảnh môn", "Tử môn", "Kinh môn"],
        "rule": "Chọn 3 môn cát → hành động. Tránh 5 môn hung → đợi thời cơ khác.",
        "nuance": {
            "khai_mon": "Tứ thông bát đạt — thông suốt mọi việc. Nhưng nếu nằm cung Chấn/Tốn (Mộc) → 'kim khắc' (môn Kim bị Mộc khắc) → không may",
            "canh_mon": "Còn gọi 'bình môn' — bình thường, kéo dài không lâu. Tốt cho thi đấu, ký kết.",
            "tu_mon": "Đại hung — chỉ tốt cho việc tang lễ. Tránh khởi sự lớn.",
        },
    },

    # ─── Phân cấp Cửu tinh chính xác (Đàm Liên Chương I phần IV pages 39-40) ───
    "cuu_tinh_phan_cap": {
        "overview": "9 sao chia 2 nhóm × 2 mức độ. 5 cát + 4 hung. Em đã CORRECTED constants per Đàm Liên (commit batch 2).",
        "cat_tinh": {
            "dai_cat (3 sao)": ["Thiên Phụ 天輔", "Thiên Cầm 天禽", "Thiên Tâm 天心"],
            "tieu_cat (2 sao)": ["Thiên Xung 天沖", "Thiên Nhậm 天任"],
        },
        "hung_tinh": {
            "dai_hung (2 sao)": ["Thiên Bồng 天蓬", "Thiên Nhuế 天芮"],
            "tieu_hung (2 sao)": ["Thiên Trụ 天柱", "Thiên Anh 天英"],
        },
    },

    # ─── Sinh khắc Môn ↔ Cung (rule luận) ───
    "sinh_khac_mon_cung": {
        "overview": "Mỗi môn có ngũ hành riêng. Khi đặt vào cung (cũng có ngũ hành), check sinh khắc Môn↔Cung để xác định cát/hung TĂNG/GIẢM.",
        "vd_khai_mon": "Khai môn = Kim. Nếu đặt cung Chấn (3, Mộc) hoặc Tốn (4, Mộc) → Mộc khắc Kim → 'kim khắc' = Khai môn bị suy giảm cát khí.",
        "vd_thuong_mon": "Thương môn = Mộc. Nếu đặt cung Khôn (2, Thổ) hoặc Cấn (8, Thổ) → Mộc khắc Thổ → tăng độ hung.",
        "principle": "Tổng cát/hung của 1 cung = (cat_hung gốc của môn/tinh/thần) × (sinh/khắc/đồng/khoảng cung) × (mùa hợp/khắc)",
    },

    # ─── Mùa hợp/khắc cho Cửu tinh (Đàm Liên page 40+) ───
    "mua_hop_khac_tinh": {
        "Thiên Bồng (Thủy)": "Hợp xuân/hè (Mộc/Hỏa cần Thủy), khắc thu/đông (Kim/Thủy dư)",
        "Thiên Nhuế (Thổ)": "Hợp đông/thu (Thủy/Kim cần Thổ), khắc hè/xuân (Hỏa/Mộc)",
        "principle": "Đàm Liên gắn từng tinh với mùa hợp — thêm 1 chiều luận ngoài cung+môn+thần",
    },

    # ─── Sách reference em đọc trong YI-CHRONOS ───
    "source_book": {
        "title": "Kỳ Môn Độn Giáp",
        "subtitle": "Tìm hiểu văn hóa phương Đông",
        "author": "Đàm Liên",
        "publisher": "Nhà xuất bản Thời Đại",
        "pages": 367,
        "language": "Việt văn (biên soạn từ cổ thư Trung Hoa)",
        "year": "~2010 (PDF scan 2011)",
        "restoration_status": "Sample OCR 20 pages (cover + lời nói đầu + Chương I)",
        "restoration_path": "data/yi_restored/ky-mon-don-giap-dam-lien/",
        "key_quote_1": "KMĐG là sự kết hợp dung hoà sâu sắc giữa đa tư duy, cái lập thể và sự vận động, giữa thời gian, không gian và những con số.",
        "key_quote_2": "Các phương vị trong KMĐG không phải là tuyệt đối mà chỉ là tương đối.",
        "key_quote_3": "Muốn cho việc nghiên cứu KMDG phát triển lành mạnh, cần xoá bỏ những suy nghĩ coi KMDG là hoang đường, mê tín, lừa gạt.",
        "paradigm_alignment": "Đàm Liên BÁC BỎ 3 yếu tố mê tín: thần thoại hoá nguồn gốc + duy tâm về 'động ứng' + pháp thuật niệm chú. Trùng khớp Iron Rule #4/#6 của YI-CHRONOS (đọc đồng dạng, không predict).",
    },
}


def get_concept(category: str, name: str) -> dict | None:
    """Tra cứu 1 khái niệm cụ thể."""
    return WIKI.get(category, {}).get(name)


def list_categories() -> list[str]:
    """List các category trong wiki."""
    return list(WIKI.keys())
