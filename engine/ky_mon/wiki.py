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

    # ─── 8 môn (verbatim Đàm Liên Chương I phần IV pages 38-40) ───
    # Mỗi môn có: bản chất, việc thuận lợi, ngoại lệ paradox, sinh khắc cung
    "mon": {
        "Hưu": {
            "zh": "休門", "ngu_hanh": "Thủy", "than": "Thủy thần",
            "cat_hung": "cát",
            "tinh_chat": "Cát môn — mọi việc đều HOÀN CHỈNH",
            "viec_thuan": "Sum họp, kinh doanh, kết hôn, gặp giàu sang phú quý",
            "viec_tranh": "",
            "ngoai_le": "Cung Ly số 9 → Thủy xung khắc Hỏa → không may",
            "desc": "Đàm Liên: 'Hưu môn là cát môn, mọi việc đều hoàn chỉnh, dễ dàng sum họp, kinh doanh, kết hôn, gặp giàu sang phú quý.'",
        },
        "Sinh": {
            "zh": "生門", "ngu_hanh": "Thổ", "than": "Thổ thần",
            "cat_hung": "đại cát",
            "tinh_chat": "Cát môn — sinh sôi nảy nở",
            "viec_thuan": "Xây dựng, kết hôn, TÌM VIỆC, gặp giàu sang phú quý",
            "viec_tranh": "",
            "ngoai_le": "Cung Khảm số 1 → Thổ xung khắc Thủy → không may",
            "desc": "Đàm Liên: 'Sinh môn là cát môn còn lại, dễ dàng xây dựng, kết hôn gặp nhiều may mắn, dễ tìm việc và gặp giàu sang phú quý.'",
        },
        "Thương": {
            "zh": "傷門", "ngu_hanh": "Mộc", "than": "Mộc thần",
            "cat_hung": "đại hung",
            "tinh_chat": "HUNG MÔN XẤU NHẤT (trong 5 hung môn)",
            "viec_thuan": "PARADOX — Đòi nợ, bắt tội phạm trốn thoát (đạt kết quả CAO)",
            "viec_tranh": "Đi ra ngoài: mắc bệnh, tai nạn thương vong, thị phi",
            "ngoai_le": "Cung Khôn 2 / Cấn 8 (Thổ) → Mộc khắc Thổ → CÀNG XẤU",
            "desc": "Đàm Liên: 'Thương môn chính là hung môn XẤU NHẤT. Khi đi ra ngoài dễ gặp xấu như mắc bệnh, tai nạn thương vong, thị phi. NHƯNG nếu đòi nợ thì lại đạt được kết quả cao, dễ dàng bắt được tội phạm đã trốn thoát.'",
        },
        "Đỗ": {
            "zh": "杜門", "ngu_hanh": "Mộc", "than": "Mộc thần",
            "cat_hung": "trung bình",
            "tinh_chat": "Hung môn nhưng MỨC ĐỘ XẤU ÍT HƠN Thương môn + Tử môn",
            "viec_thuan": "Xuất hành, GẶP QUÝ NHÂN phù trợ, TRÁNH ĐƯỢC TANG TÓC",
            "viec_tranh": "(u ám, chậm trễ)",
            "ngoai_le": "Cung Khôn 2 / Cấn 8 → CÀNG XẤU",
            "desc": "Đàm Liên: 'Đỗ môn tuy cũng là một hung môn nhưng mức độ xấu của nó ÍT HƠN HẲN so với Thương môn, ít xấu hơn Tử môn một chút. Cũng có thể xuất hành, gặp quý nhân phù trợ, dễ dàng tránh được tang tóc. Đỗ môn mang ý nghĩa của sự U ÁM, CHẬM TRỄ.'",
        },
        "Cảnh": {
            "zh": "景門", "ngu_hanh": "Hỏa", "than": "Hỏa thần",
            "cat_hung": "trung bình",
            "tinh_chat": "BÌNH MÔN (bình thường) — phấn chấn ngắn hạn",
            "viec_thuan": "Tham gia THI ĐẤU TRÒ CHƠI → dễ chiến thắng",
            "viec_tranh": "",
            "ngoai_le": "Cung Càn 6 / Đoài 7 → tương đối xấu",
            "desc": "Đàm Liên: 'Cảnh môn được gọi là BÌNH MÔN (bình thường). Cảnh môn làm người ta phấn chấn nhưng thời gian kéo dài không lâu. Nếu tham gia thi đấu trò chơi thì dễ dàng chiến thắng.'",
        },
        "Tử": {
            "zh": "死門", "ngu_hanh": "Thổ", "than": "Thổ thần",
            "cat_hung": "đại hung",
            "tinh_chat": "Môn HUNG HIỂM CAO",
            "viec_thuan": "(chỉ phù hợp tang lễ — ngoại lệ paradigm)",
            "viec_tranh": "Xuất hành, xây dựng, tìm việc → thiệt hại NGƯỜI + CỦA, dễ bị HÀNH HÌNH, gặp TANG TÓC",
            "ngoai_le": "Cung Khảm số 1 → XẤU NHẤT",
            "desc": "Đàm Liên: 'Tử môn là một trong những môn có mức độ hung hiểm cao. Ở Tử môn người ta kiêng không xuất hành, xây dựng hay đi tìm việc, nếu không sẽ thiệt hại về người và của, dễ dàng bị hành hình, gặp tang tóc.'",
        },
        "Kinh": {
            "zh": "驚門", "ngu_hanh": "Kim", "than": "Kim thần",
            "cat_hung": "hung",
            "tinh_chat": "Hung môn — KINH HOÀNG KINH KHỦNG",
            "viec_thuan": "PARADOX — Dễ TÌM ĐỒ ĐÃ MẤT, TRUY ĐUỔI TỘI PHẠM",
            "viec_tranh": "Xuất hành / đi xa: khó khăn nguy hiểm trên đường, đến đích nhưng mục đích KHÔNG thực hiện được",
            "ngoai_le": "Cung Tốn 4 / Chấn 3 → mức độ hung hiểm RẤT CAO",
            "desc": "Đàm Liên: 'Kinh môn không nên xuất hành. Tuy nhiên dễ dàng tìm được đồ đã mất, truy đuổi tội phạm. Chữ kinh = kinh hoàng, kinh khủng — mọi việc đều xảy ra KÌ LẠ BẤT NGỜ.'",
        },
        "Khai": {
            "zh": "開門", "ngu_hanh": "Kim", "than": "Kim thần",
            "cat_hung": "đại cát",
            "tinh_chat": "Cát môn — TỨ THÔNG BÁT ĐẠT (may mắn mọi đường)",
            "viec_thuan": "Mọi việc thông suốt KHÔNG có trở ngại, đi xa, gặp giàu sang phú quý",
            "viec_tranh": "",
            "ngoai_le": "Cung Chấn 3 / Tốn 4 (Mộc) → 'KIM KHẮC' (môn bị cung khắc) → KHÔNG MAY",
            "desc": "Đàm Liên: 'Khai môn là cát môn. Khai môn có nghĩa là TỨ THÔNG BÁT ĐẠT (may mắn mọi đường), mọi việc được thông suốt không có trở ngại. Nếu ở vào cung Chấn, cung Tốn thì lại là KIM KHẮC, không hề may mắn chút nào.'",
        },
    },

    # Concept "MÔN BÁCH" / "MÔN BỨC" — sinh khắc Môn ↔ Cung (Đàm Liên page 38, 51)
    "mon_bach_concept": {
        "name_vn": "Môn bách / Môn bức (門剝 / 門剝)",
        "definition": "Khi Cung KHẮC Môn → môn bị suy giảm cát khí (gọi 'môn bách'). Khi Môn KHẮC Cung → môn không thuận (gọi 'môn bức'). Đây là RULE CỐT để fine-tune cat_hung gốc của môn.",
        "vd_cat_thanh_xau": "Cát môn (Khai/Sinh/Hưu) khắc cung HOẶC cung khắc cát môn → VIỆC TỐT cũng thành xấu",
        "vd_hung_thanh_dai_hung": "Hung môn (Thương/Tử/Kinh) khắc cung HOẶC cung khắc hung môn → ĐẶC BIỆT TAI HUNG",
        "principle": "Đàm Liên: cat_hung thực tế = cat_hung gốc môn × sinh-khắc cung × mùa khí",
    },

    # Hoà / Nghĩa — Đàm Liên page 48
    "hoa_nghia_rule": {
        "Hoà 和": "Môn SINH cung → Hoà (môn hỗ trợ cung)",
        "Nghĩa 義": "Cung SINH Môn → Nghĩa (cung hỗ trợ môn — TỐT HƠN Hoà)",
        "rule": "Gặp Hoà / Nghĩa + cát môn → việc gì cũng tốt. Gặp Bách / Bức + hung môn → đại tai.",
    },

    # ─── 9 tinh (verbatim Đàm Liên Chương I phần IV pages 41-43) ───
    # Em đã BIAS lần trước. Rewrite STRICT theo Đàm Liên. Source ghi rõ.
    "tinh": {
        "Thiên Bồng": {
            "zh": "天蓬", "ngu_hanh": "Thủy", "cat_hung": "đại hung",
            "tinh_chat": "Thủy tặc — đầu hung tinh",
            "viec_thuan": "PARADOX — nếu gặp Sinh môn + Bính Kỳ/Đinh Kỳ → có thể làm việc lớn (chỉ MÙA XUÂN/HÈ áp dụng)",
            "viec_tranh": "KẾT HÔN, XÂY DỰNG, DI DỜI — không nên",
            "mua_hop": "Xuân/Hạ may; Thu/Đông xấu",
            "desc": "Đàm Liên: 'Thiên Bồng là thủy tặc. Nếu vào mùa xuân hay mùa hạ thì may mắn nhưng nếu vào mùa thu hay mùa đông thì xấu. Là thời gian để TU TẠO LẠI MỒ MẢ. Nếu gặp Sinh môn + Bính/Đinh Kỳ thì có thể làm việc lớn, mùa xuân hè áp dụng được, không thể mùa thu đông.'",
        },
        "Thiên Nhậm": {
            "zh": "天任", "ngu_hanh": "Thổ", "cat_hung": "cát",
            "tinh_chat": "Sao MAY MẮN (tiểu cát)",
            "viec_thuan": "Tế lễ CẦU DANH, kết hôn, xây mồ mả, làm kinh doanh — mọi việc đều thuận lợi",
            "viec_tranh": "",
            "mua_hop": "(không nhấn rõ)",
            "desc": "Đàm Liên: 'Thiên Nhậm là một sao may mắn, tế lễ CẦU DANH hay KẾT HÔN đều được, xây mồ mả hay làm kinh doanh đều gặp may mắn. Đây là thời gian may mắn, cầu danh, kết hôn, di dời kinh doanh... mọi việc đều thuận lợi.'",
        },
        "Thiên Xung": {
            "zh": "天沖", "ngu_hanh": "Mộc", "cat_hung": "cát",
            "tinh_chat": "Lôi tê / thiên đế / võ sĩ (tiểu cát)",
            "viec_thuan": "XUẤT QUÂN",
            "viec_tranh": "Kết hôn, xây dựng, di dời, kinh doanh, tu mộ — đều GẶP TAI HỌA",
            "desc": "Đàm Liên: 'Thiên Xung — Kết hôn xây dựng cơ nghiệp, xuất hành di dời đều GẶP TAI HỌA, tu sửa mồ mả cũng không gặp may. Thiên Xung được coi là lôi tê, thiên đế, võ sĩ, DỄ DÀNG XUẤT QUÂN nhưng KHÔNG NÊN kết hôn, xây dựng, di dời hay làm kinh doanh.'",
        },
        "Thiên Phụ": {
            "zh": "天輔", "ngu_hanh": "Mộc", "cat_hung": "đại cát",
            "tinh_chat": "Vì vạn vật, vì dân chúng (đại cát)",
            "viec_thuan": "Xuất hành, TU SỬA MỒ MẢ, THĂNG QUAN, di dời, kết hôn, mời khách — VẠN SỰ CÁT TƯỜNG",
            "viec_tranh": "",
            "desc": "Đàm Liên: 'Thiên Phụ — rất dễ xuất hành, tu sửa mồ mả, RẤT DỄ THĂNG QUAN TIẾN CHỨC, mọi việc đều cát tường. Thiên Phụ là VÌ VẠN VẬT, VÌ DÂN CHÚNG, dễ xuất hành, xây dựng, di dời, kết hôn, mời khách.'",
        },
        "Thiên Cầm": {
            "zh": "天禽", "ngu_hanh": "Thổ", "cat_hung": "đại cát",
            "tinh_chat": "Trung tâm, đi cùng Trực Phù (đại cát)",
            "viec_thuan": "Đi xa, làm ăn buôn bán mang lại NHIỀU LỢI LỘC, gặp quý nhân phù trợ, tu sửa mồ mả, GIÀU SANG PHÚ QUÝ",
            "desc": "Đàm Liên: 'Thiên Cầm rất dễ đi xa, làm ăn buôn bán mang lại nhiều lợi lộc, có thể gặp quý nhân phù trợ, nên tu sửa mồ mả. Thời gian này rất dễ xuất hành, kinh doanh, xây dựng và gặp giàu sang phú quý.'",
        },
        "Thiên Tâm": {
            "zh": "天心", "ngu_hanh": "Kim", "cat_hung": "đại cát",
            "tinh_chat": "Tiên nhân cho thuốc quý (đại cát)",
            "viec_thuan": "VẠN SỰ MAY MẮN — chữa bệnh NHANH CHÓNG, luyện tập sức khỏe, kinh doanh, di dời, xây mồ mả",
            "mua_hop": "Đông/Thu may; Xuân/Hạ xấu",
            "desc": "Đàm Liên: 'Thiên Tâm gặp được TIÊN NHÂN CHO THUỐC QUÝ, làm ăn buôn bán mang về nhiều lợi lộc. Nếu chữa bệnh vào thời gian này sẽ NHANH CHÓNG CHỮA ĐƯỢC BỆNH TẬT. VẠN SỰ ĐỀU MAY MẮN, CÁT TƯỜNG.'",
        },
        "Thiên Trụ": {
            "zh": "天柱", "ngu_hanh": "Kim", "cat_hung": "hung",
            "tinh_chat": "TẤT CẢ MỌI VIỆC ĐỀU KHÔNG THUẬN LỢI (tiểu hung)",
            "viec_thuan": "(không có việc nào thuận)",
            "viec_tranh": "Xuất hành, kinh doanh, tìm việc — LẬP TỨC GẶP XẤU nếu làm",
            "desc": "Đàm Liên: 'Thiên Trụ KHÔNG NÊN xuất hành hay làm kinh doanh. Làm kinh doanh đều không thuận lợi, nếu làm LẬP TỨC GẶP XẤU. Bởi thế không nên xuất hành, đi tìm việc, TẤT CẢ MỌI VIỆC ĐỀU KHÔNG THUẬN LỢI.' (Em ĐÃ BIAS lần trước với 'phòng thủ giữ thành' — Đàm Liên KHÔNG nói thế.)",
        },
        "Thiên Anh": {
            "zh": "天英", "ngu_hanh": "Hỏa", "cat_hung": "hung",
            "tinh_chat": "SAO XẤU — mọi việc đều không may (tiểu hung)",
            "viec_thuan": "(không có)",
            "viec_tranh": "Kết hôn, đi xa, di dời, CẦU DANH, CẦU TÀI — đều KHÔNG có kết quả",
            "desc": "Đàm Liên: 'Thiên Anh — KHÔNG nên kết hôn, đi xa hay di dời. Cầu danh, cầu tài đều không có kết quả gì. Đây là SAO XẤU nên mọi việc đều KHÔNG MAY MẮN.' (Em đã BIAS với 'văn thư danh tiếng' — Đàm Liên dứt khoát phản đối Thiên Anh cho cầu danh.)",
        },
        "Thiên Nhuế": {
            "zh": "天芮", "ngu_hanh": "Thổ", "cat_hung": "đại hung",
            "tinh_chat": "Sao Thổ — bệnh tinh đầu",
            "viec_thuan": "Dễ KẾT GIAO BẠN BÈ, THẦY CÔ (paradox)",
            "viec_tranh": "Xuất hành (mọi việc thất bại), xây dựng (tai họa), KẾT HÔN, di dời, tố tụng — DÙ ĐẮC KÌ ĐẮC MÔN cũng khó may",
            "mua_hop": "Đông/Thu may; Hạ/Xuân xấu",
            "desc": "Đàm Liên: 'Thiên Nhuế — không nên xuất hành, nếu xuất hành thì mọi việc thất bại. Vào thời gian này dễ dàng kết giao bạn bè, thầy cô NHƯNG không nên kết hôn, di dời, tố tụng xây dựng, MẶC DÙ ĐẮC KÌ ĐẮC MÔN nhưng cùng khó mà gặp may mắn.'",
        },
    },

    # Note Đàm Liên về Cửu tinh
    "cuu_tinh_note_dam_lien": {
        "warning": "Đàm Liên thẳng thắn: 'Các sách bói toán có những cách nói KHÔNG ĐỒNG NHẤT với nhau về ý nghĩa lành dữ của 9 sao, cũng như xuất hiện nhiều mâu thuẫn.' (page 42)",
        "stance": "Engine YI-Chronos TRUNG THÀNH với Đàm Liên (source canonical đã chọn). Tradition khác có thể có version khác cho Thiên Anh / Thiên Trụ.",
    },

    # ─── 8 thần (verbatim Đàm Liên Chương I phần IV pages 43-44) ───
    # KMDG tone GỐC LÀ BINH-GIA (mưu sĩ chiến tranh — Trương Lương, Gia Cát, Lưu Bá Ôn).
    # Em đã neuter-hoá lần trước. Rewrite restore tone military.
    "than": {
        "Trị Phù": {
            "zh": "值符", "alias": "Thần Thiên Ất 天乙", "cat_hung": "đại cát",
            "tinh_chat": "Thần ĐẦU TIÊN trong Bát thần",
            "rule": "Đi đến BẤT KÌ NƠI NÀO mọi điều xấu đều XOÁ TAN HẾT",
            "viec_thuan": "Có việc GẤP nên xuất phát từ đây",
            "co_ngu": "'Có việc gấp thì nên xuất phát từ thần ấm áp' (Yên Ba Chước Du Ca)",
            "desc": "Đàm Liên: 'Trực Phù là thần Thiên Ất, là thân đầu tiên trong các vị thần, đi đến BẤT KÌ NƠI NÀO mọi điều xấu đều XOÁ TAN HẾT. Có VIỆC GẤP nên xuất phát từ đây.'",
        },
        "Đằng Xà": {
            "zh": "螣蛇", "cat_hung": "hung",
            "tinh_chat": "Rắn bay — thần biến hoá kì quặc",
            "rule": "Chuyện KINH KHỦNG kì quặc, tinh thần HOẢNG HỐT, hay GẶP ÁC MỘNG",
            "desc": "Đàm Liên: 'Đằng Xà — gặp phải những chuyện KINH KHỦNG kì quặc. Nếu chỗ nào xuất hiện Đằng Xà thì người sẽ cảm thấy TINH THẦN HOẢNG HỐT, hay GẶP ÁC MỘNG.'",
        },
        "Thái Âm": {
            "zh": "太陰", "cat_hung": "cát",
            "tinh_chat": "Thần PHÙ HỘ — tính ÂM",
            "rule": "Có thể ĐÓNG CỬA THÀNH cho quân lính NGHỈ NGƠI, tránh được nguy hiểm",
            "tone_binh_gia": "true",
            "desc": "Đàm Liên: 'Thái Âm được coi là THẦN PHÙ HỘ, tính âm. Nếu thấy xuất hiện Thái Âm thì có thể ĐÓNG CỬA THÀNH cho quân lính NGHỈ NGƠI, tránh được nguy hiểm.'",
        },
        "Lục Hợp": {
            "zh": "六合", "cat_hung": "cát",
            "tinh_chat": "Thần BẢO VỆ — tính ÔN HOÀ",
            "rule": "Giới thiệu người MÔI GIỚI hôn nhân, thương mại; kết hôn, kết giao bạn bè",
            "desc": "Đàm Liên: 'Lục Hợp là thần BẢO VỆ, tính ÔN HOÀ. Có thể giới thiệu người MÔI GIỚI hôn nhân, thương mại. Nếu là phương Lục Hợp thì có thể kết hôn, kết giao bạn bè.'",
        },
        "Câu Trần": {
            "zh": "勾陳", "alias": "Bạch Hổ", "cat_hung": "hung",
            "tinh_chat": "Thần XẤU",
            "rule": "Phải ĐỀ PHÒNG KẺ ĐỊCH ĐÁNH BẤT NGỜ",
            "tone_binh_gia": "true",
            "desc": "Đàm Liên: 'Câu Trần (Bạch Hổ) là thần XẤU. Nếu có Câu Trần thì phải ĐỀ PHÒNG KẺ ĐỊCH ĐÁNH BẤT NGỜ.'",
        },
        "Chu Tước": {
            "zh": "朱雀", "cat_hung": "hung",
            "tinh_chat": "Thần CƯỚP BÓC",
            "rule": "Hay bị TRỘM, ÂM MƯU LÀM HẠI, chuyện MẤT MÁT; đề phòng MẬT THÁM",
            "tone_binh_gia": "true",
            "desc": "Đàm Liên: 'Chu Tước là THẦN CƯỚP BÓC, hay bị TRỘM, ÂM MƯU LÀM HẠI, hay gặp chuyện MẤT MÁT. Xuất hiện Chu Tước thì phải đề phòng MẬT THÁM.'",
        },
        "Cửu Địa": {
            "zh": "九地", "cat_hung": "cát",
            "tinh_chat": "MẸ CỦA VẠN VẬT — thần KIÊN CỐ, tính TĨNH",
            "rule": "Có thể PHÒNG THỦ BINH TƯỚNG",
            "tone_binh_gia": "true",
            "desc": "Đàm Liên: 'Cửu Địa là MẸ của vạn vật, được coi là thần KIÊN CỐ, tính TĨNH. Nếu là phương Cửu Địa thì có thể PHÒNG THỦ BINH TƯỚNG.'",
        },
        "Cửu Thiên": {
            "zh": "九天", "cat_hung": "đại cát",
            "tinh_chat": "CHA CỦA VẠN VẬT — thần HÙNG DŨNG, tính ĐỘNG",
            "rule": "Phương Cửu Thiên: nên SẮP XẾP BINH LÍNH để chuẩn bị CHIẾN ĐẤU",
            "tone_binh_gia": "true",
            "desc": "Đàm Liên: 'Cửu Thiên là CHA của vạn vật, được coi là thần HÙNG DŨNG, tính ĐỘNG. Nếu phương xuất hiện Cửu Thiên thì nên SẮP XẾP BINH LÍNH để chuẩn bị CHIẾN ĐẤU.'",
        },
    },

    # Note Đàm Liên về tone KMDG
    "tone_binh_gia_note": {
        "warning": "KMDG GỐC LÀ MÔN BINH GIA (mưu sĩ chiến tranh — Trương Lương, Gia Cát Lượng, Lưu Bá Ôn đều là quân sư). Đàm Liên dùng nhiều ẩn dụ quân sự (đóng cửa thành, phòng thủ binh tướng, sắp binh chiến đấu, kẻ địch đánh bất ngờ, mật thám, cướp bóc).",
        "implication": "User vào KMDG đừng chỉ nghĩ 'kết hôn, kinh doanh'. Paradigm gốc là TÁC CHIẾN: vì sao Thái Âm = đóng cửa thành, Cửu Địa = phòng thủ binh, Cửu Thiên = xuất binh — đó là context tasks 'Mai phục / Ẩn náu / Bắt tội phạm' đặc thù binh-gia.",
        "modern_translation": "Áp dụng modern: 'kẻ địch' = competitor / kẻ phản; 'đóng cửa thành' = consolidate position; 'xuất binh' = launch / pivot lớn; 'mật thám' = data leak / info security.",
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

    # ─── Bố cục KMDG: 4320 → 1080 → 72 → 18 (Đàm Liên Chương II pages 51-53) ───
    "bo_cuc_numbers": {
        "overview": "KMDG có nhiều cấp số bố cục. Mỗi cấp giảm theo trùng lặp.",
        "4320": "Theoretical: 360 ngày × 12 giờ/ngày = 4320 giờ → 4320 bố cục (Thiên Bàn + Môn Bàn biến theo giờ)",
        "1080": "Practical: 4320 ÷ 4 (trùng lặp 4 lần/năm) = 1080 bố cục thực dụng",
        "72": "Canon: 24 tiết khí × 3 nguyên (Thượng/Trung/Hạ) = 72 bố cục",
        "18_dia_ban": "Địa Bàn cố định: 72 ÷ 4 = 18 cục (9 Dương Độn + 9 Âm Độn). Trích Yên Ba Chước Du Ca: 'Chế ra thời gian 1800 giờ, Thái Công chia 72, đến Hán Trương Tử Phòng tiết giảm còn 18 cục'",
        "implication": "Khi cast, kinqimen library xử lý đủ 4320 case. UI hiển thị 1 cục (1 bố cục cụ thể của thời điểm). Wiki + UI tooltip cho user hiểu 18 cục gốc.",
    },

    # ─── Tiết vs Trung Khí (Đàm Liên Chương II page 55) ───
    "tiet_vs_trung_khi": {
        "overview": "Người ta thường nói '24 tiết khí' nhưng thực ra là 12 TIẾT + 12 KHÍ (trung khí).",
        "tiet": "Nửa tháng ĐẦU mỗi tháng âm lịch. VD Lập Xuân (tháng giêng), Kinh Chập (tháng hai), Thanh Minh (tháng ba)...",
        "trung_khi": "Nửa tháng SAU mỗi tháng. VD Vũ Thủy (tháng giêng), Xuân Phân (tháng hai), Cốc Vũ (tháng ba)...",
        "12_tiet": ["Lập Xuân", "Kinh Chập", "Thanh Minh", "Lập Hạ", "Mang Chủng", "Tiểu Thử", "Lập Thu", "Bạch Lộ", "Hàn Lộ", "Lập Đông", "Đại Tuyết", "Tiểu Hàn"],
        "12_trung_khi": ["Vũ Thủy", "Xuân Phân", "Cốc Vũ", "Tiểu Mãn", "Hạ Chí", "Đại Thử", "Xử Thử", "Thu Phân", "Sương Giáng", "Tiểu Tuyết", "Đông Chí", "Đại Hàn"],
    },

    # ─── Phù Đầu rule (Đàm Liên pages 58-59) ───
    "phu_dau_rule": {
        "overview": "Mỗi đơn Nguyên = 5 ngày, khởi từ Phù Đầu (ngày Giáp hoặc Kỷ). Pattern chi xác định Nguyên nào.",
        "thuong_nguyen": "Phù Đầu = Giáp/Kỷ + chi Tứ Trọng (Tý Ngọ Mão Dậu) — chi giữa mùa",
        "trung_nguyen": "Phù Đầu = Giáp/Kỷ + chi Tứ Mạnh (Dần Thân Tỵ Hợi) — chi đầu mùa",
        "ha_nguyen": "Phù Đầu = Giáp/Kỷ + chi Tứ Quý (Thìn Tuất Sửu Mùi) — chi cuối mùa",
        "vd_thoi_gia": "Đông Chí cung 1 Khảm → Thượng Nguyên = Dương Độn 1 cục. Hạ Chí cung 9 Ly → Âm Độn 9 cục. Lập Xuân cung 2 Khôn → Âm Độn 2 cục.",
    },

    # ─── Trí Nhuận (Đàm Liên pages 59-60) — explain method 'zhirun' trong kinqimen ───
    "tri_nhuan_chabu": {
        "overview": "Khi Phù Đầu cách tiết khí > 9 ngày → cần 'Trí Nhuận' để chỉnh. Đây là 2 methods chính trong kinqimen.",
        "chabu_拆補": {
            "name_vn": "Chabu — Tách bổ",
            "rule": "Mặc định. Mỗi 5 ngày 1 nguyên, không insert ngày bổ sung. Phù hợp khi Phù Đầu cách tiết khí < 9 ngày.",
            "library_value": "method='chabu' trong kinqimen (default)",
        },
        "zhirun_置閏": {
            "name_vn": "Zhirun — Trí Nhuận (Đặt nhuận)",
            "rule": "Khi Phù Đầu cách tiết khí > 9 ngày, insert 15 ngày trùng lặp (lặp Thượng/Trung/Hạ Nguyên). Siêu Thần → Tiếp Khí.",
            "library_value": "method='zhirun' trong kinqimen",
        },
        "implication": "User chọn 'Zhirun 置閏' trong dropdown UI khi muốn theo phương pháp lịch nhuận (cận đại hơn). Mặc định 'Chabu' cho đơn giản.",
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
