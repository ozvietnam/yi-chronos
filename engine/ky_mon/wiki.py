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

    # ─── 9 tinh ───
    "tinh": {
        "Thiên Bồng": {"zh": "天蓬", "ngu_hanh": "Thủy", "cat_hung": "đại hung",
                       "desc": "Đầu hung tinh — Bắc Đẩu thứ nhất. Chủ trộm cướp, dâm dục, mưu kế đen."},
        "Thiên Nhậm": {"zh": "天任", "ngu_hanh": "Thổ", "cat_hung": "cát",
                       "desc": "Bảo trì, đảm nhận. Cát cho việc lâu dài, tích lũy."},
        "Thiên Xung": {"zh": "天沖", "ngu_hanh": "Mộc", "cat_hung": "trung bình",
                       "desc": "Kích phạt, xung đột. Tốt cho người võ, tranh đấu chính nghĩa."},
        "Thiên Phụ": {"zh": "天輔", "ngu_hanh": "Mộc", "cat_hung": "đại cát",
                      "desc": "Phù trợ. Đại cát cho học hành, văn thư, du lịch."},
        "Thiên Cầm": {"zh": "天禽", "ngu_hanh": "Thổ", "cat_hung": "cát",
                      "desc": "Trung tâm, ổn định (luôn ở Trung cung). Đi cùng Trị Phù."},
        "Thiên Tâm": {"zh": "天心", "ngu_hanh": "Kim", "cat_hung": "cát",
                      "desc": "Y dược, lành bệnh. Cát cho sức khỏe, nghiên cứu sâu."},
        "Thiên Trụ": {"zh": "天柱", "ngu_hanh": "Kim", "cat_hung": "trung bình",
                      "desc": "Phòng thủ, cố thủ. Cát cho giữ thành, bất lợi cho công thành."},
        "Thiên Anh": {"zh": "天英", "ngu_hanh": "Hỏa", "cat_hung": "trung bình",
                      "desc": "Chiếu rọi, văn thư, danh tiếng. Hư danh, dễ bị hỏa thiêu."},
        "Thiên Nhuế": {"zh": "天芮", "ngu_hanh": "Thổ", "cat_hung": "đại hung",
                       "desc": "Đầu bệnh tinh. Chủ bệnh tật, tang sự. Tránh đi xa, mua bán quan trọng."},
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

    # ─── Tổ sư ───
    "to_su": {
        "name": "Lưu Bá Ôn",
        "name_zh": "劉伯溫",
        "birth": "1311-07-01",
        "death": "1375-05-16",
        "title": "Tư Mã Hư Tịnh — Cố vấn Minh Thái Tổ Chu Nguyên Chương",
        "work": "Bá Ôn Bí Truyền Kỳ Môn Độn Giáp (truyền thuyết)",
        "lineage": "Cửu Thiên Huyền Nữ → Hoàng Đế → Phong Hậu → Khương Tử Nha → Trương Lương → Gia Cát Lượng → Lưu Bá Ôn",
        "paradigm": "Hệ thống KMDG cận đại stable + procedural. Phù hợp Author-Worldview-First.",
    },
}


def get_concept(category: str, name: str) -> dict | None:
    """Tra cứu 1 khái niệm cụ thể."""
    return WIKI.get(category, {}).get(name)


def list_categories() -> list[str]:
    """List các category trong wiki."""
    return list(WIKI.keys())
