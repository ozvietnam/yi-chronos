# -*- coding: utf-8 -*-
"""Bảng DERIVE thuần-Việt — NEO từ _vocab_canon.json (dinh_nghia_canon).

NGUYÊN TẮC NEO (chống drift):
  - net_canon = list các NÉT (dimension) TÁCH ra từ dinh_nghia_canon. KHÔNG thêm nét lạ.
  - thuan_viet = câu đời thường GIỮ ĐỦ mọi nét trong net_canon (không rơi, không bịa),
    người không biết tử vi vẫn hiểu, KHÔNG có tên sao / chữ Hán trong câu.
  - Mỗi term GẮN nguồn (lấy từ canon_nguon của canon). can_review=True khi thiếu nguồn.

Key = han_viet (đúng như trong _vocab_canon.json terms[].han_viet).
Value = {"net_canon": [...], "thuan_viet": "..."}.

Term nào KHÔNG có trong bảng này → builder set can_review=True (chờ Anh duyệt bản thuần-Việt),
nhưng vẫn copy net_canon thô (tách theo dấu phẩy) để không mất dữ liệu.
"""

# Mỗi entry: net_canon GIỮ ĐÚNG số nét của canon. thuan_viet ráp đủ các nét đó.
MAP = {
    # ===== 14 CHÍNH TINH =====
    "Tử Vi": {
        "net_canon": ["đế vương/đứng đầu", "quyền lực tối cao", "dung mạo trọng hậu/dáng vẻ đường bệ"],
        "thuan_viet": "Mẫu người sinh ra để đứng đầu, nắm quyền cao nhất, lại có dáng vẻ đường bệ khiến người khác nể trọng.",
    },
    "Thiên Cơ": {
        "net_canon": ["trí tuệ", "nhanh nhẹn/linh hoạt", "thiện tâm/lòng tốt"],
        "thuan_viet": "Người đầu óc sáng, phản ứng nhanh nhạy linh hoạt, và bụng dạ tử tế hay thương người.",
    },
    "Thái Dương": {
        "net_canon": ["mặt trời/toả sáng", "quyền lực", "danh vọng", "sáng suốt/minh bạch"],
        "thuan_viet": "Người như mặt trời toả sáng cho mọi người, có sức ảnh hưởng và uy quyền, được nhiều người biết tiếng, sống minh bạch và nhìn việc thấu suốt.",
    },
    "Vũ Khúc": {
        "net_canon": ["thuộc võ/làm ăn cứng cỏi", "cương cường/cứng cỏi", "quyết đoán/dứt khoát"],
        "thuan_viet": "Người cứng cỏi, làm việc thực tế bằng nội lực bản thân, tính tình mạnh mẽ và quyết định việc gì là làm dứt khoát.",
    },
    "Thiên Đồng": {
        "net_canon": ["phúc đức/có phúc", "an nhàn/thư thái", "đầy đặn/phúc hậu bên ngoài"],
        "thuan_viet": "Người có phúc, sống thong dong an nhàn không bon chen, vẻ ngoài đầy đặn phúc hậu.",
    },
    "Liêm Trinh": {
        "net_canon": ["tham vọng/khát khao lớn", "sắc đẹp/duyên hút người", "mày rộng miệng tươi/nét mặt cởi mở"],
        "thuan_viet": "Người nhiều khát khao và tham vọng lớn, lại có nét cuốn hút duyên dáng, gương mặt mày rộng miệng tươi trông cởi mở dễ gần.",
    },
    "Thiên Phủ": {
        "net_canon": ["tôn quý/được trọng vọng", "thể chất thuần hoà/tính ôn hoà", "cát tinh ổn định/vững vàng lành"],
        "thuan_viet": "Người được nể trọng, tính tình ôn hoà điềm đạm, và là chỗ dựa vững vàng đem lại sự yên ổn lành mạnh cho xung quanh.",
    },
    "Thái Âm": {
        "net_canon": ["mặt trăng/dịu mát", "tài lộc/tiền của", "dịu dàng", "văn chương/yêu cái đẹp chữ nghĩa"],
        "thuan_viet": "Người dịu dàng mát mẻ như ánh trăng, khéo lo tiền của tích góp, tính nết nhẹ nhàng và yêu thích chữ nghĩa văn chương.",
    },
    "Tham Lang": {
        "net_canon": ["sắc đẹp/sức hút", "tham vọng/ham muốn nhiều", "đào hoa/đa tình", "phong lưu/ham vui hưởng thụ"],
        "thuan_viet": "Người có sức hút, ham muốn nhiều thứ và khát khao lớn, đào hoa được người khác phái để ý, lại thích ăn chơi hưởng thụ vui vẻ.",
    },
    "Cự Môn": {
        "net_canon": ["thị phi/dễ vướng điều tiếng", "khẩu thiệt/chuyện lời ăn tiếng nói"],
        "thuan_viet": "Người dễ vướng vào điều tiếng và những chuyện rắc rối quanh lời ăn tiếng nói, miệng lưỡi.",
    },
    "Thiên Tướng": {
        "net_canon": ["ấn tín/giữ chữ tín, đáng tin cậy", "quyền hành/có vị thế điều hành", "bảo vệ/che chở người khác"],
        "thuan_viet": "Người đáng tin cậy được giao việc và con dấu, có vị thế đứng ra cầm trịch điều hành, và luôn che chở bảo vệ cho người bên cạnh.",
    },
    "Thiên Lương": {
        "net_canon": ["phúc đức/có phúc", "tuổi thọ/sống lâu", "nhân từ/hiền lành thương người"],
        "thuan_viet": "Người có phúc dày, được sống lâu khoẻ mạnh, tính tình hiền hậu nhân từ hay che chở giúp đỡ kẻ khác.",
    },
    # THẬP THẦN Bát Tự 七殺 (KHÔNG phải SAO Tử Vi cùng tên) — neo concept_index
    # tu_binh_ba_tu: khắc Nhật chủ cùng âm dương; nữ mệnh = chồng/áp lực.
    "Thất Sát": {
        "net_canon": ["khắc Nhật chủ, cùng âm dương/sức ép mạnh đè lên bản thân", "quyền lực dữ dội, áp lực", "tướng quân/đối thủ mạnh", "tích cực: quân đội, công an, kinh doanh mạo hiểm, lãnh đạo", "tiêu cực: tai hoạ, kiện tụng, kẻ thù", "cần được kiềm chế (Thực Thần chế) hoặc chuyển hoá (Ấn hoá) thì thành quý hiển", "với nữ là sao người chồng/sức ép phối ngẫu (tầng product)"],
        "thuan_viet": "Loại sức ép mạnh dữ dằn đè thẳng lên bản thân, như uy của một viên tướng hay một đối thủ ngang ngửa: hợp với binh nghiệp, công an, làm ăn mạo hiểm và vai trò chỉ huy; nhưng buông lỏng thì hoá tai hoạ, kiện tụng, sinh kẻ thù. Phải biết ghìm lại hoặc chuyển hoá nó thì mới thành người quý hiển. Với người nữ, đây cũng là hình ảnh người chồng và áp lực từ bạn đời.",
    },
    "Phá Quân": {
        "net_canon": ["hung/dữ", "phá hoại/đập bỏ cái cũ", "thay đổi/xáo trộn", "đổ vỡ/tan rã"],
        "thuan_viet": "Mang khí dữ thích đập bỏ cái cũ làm lại, đời nhiều thay đổi xáo trộn, dễ gặp cảnh đổ vỡ tan rã.",
    },
    # ===== ĐÀO HOA / SÁT / PHỤ TINH =====
    "Thiên Diêu": {
        "net_canon": ["dâm dục/nặng chuyện ái tình", "phong lưu/ham vui đa tình", "tâm tính âm độc/bụng dạ ngầm hiểm", "đa nghi/hay ngờ vực"],
        "thuan_viet": "Người nặng về ái tình và ham vui đa tình, bụng dạ có phần ngầm hiểm khó lường, lại hay ngờ vực người khác.",
    },
    "Thiên Dao": {
        "net_canon": ["dâm dục/nặng chuyện ái tình", "phong lưu/ham vui đa tình", "tâm tính âm độc/bụng dạ ngầm hiểm", "đa nghi/hay ngờ vực"],
        "thuan_viet": "Người nặng về ái tình và ham vui đa tình, bụng dạ có phần ngầm hiểm khó lường, lại hay ngờ vực người khác.",
    },
    "Hàm Trì": {
        "net_canon": ["sát tinh/khí xấu", "thuộc Thuỷ", "dâm loạn/lối sống buông thả", "yêu kiều/duyên dáng mê hoặc", "nghiêng nước nghiêng thành/đẹp mê đắm"],
        "thuan_viet": "Mang khí không lành thuộc nước, dễ dẫn tới lối sống tình cảm buông thả, nhưng vẻ ngoài yêu kiều duyên dáng đẹp tới mức mê hoặc lòng người.",
    },
    "Mộc Dục": {
        "net_canon": ["tắm gội/thanh tẩy", "giai đoạn non trẻ", "cần chăm sóc/còn yếu cần nâng đỡ"],
        "thuan_viet": "Như lúc vừa tắm gội gột rửa để khởi đầu, đang ở giai đoạn còn non trẻ nên cần được chăm sóc nâng đỡ.",
    },
    "Đại Hao": {
        "net_canon": ["hung tinh/khí xấu", "tai hoạ hao tổn/mất mát do tai ương", "chết chóc hoặc mất mát lớn"],
        "thuan_viet": "Mang khí xấu báo hiệu tai ương hao tổn, dễ kéo theo mất mát lớn hoặc chuyện đau buồn tang tóc.",
    },
    "Hồng Loan": {
        "net_canon": ["thuộc Thuỷ", "đào hoa/duyên tình", "hôn nhân/chuyện cưới hỏi"],
        "thuan_viet": "Mang khí nước, báo hiệu duyên tình tới và chuyện cưới hỏi hôn nhân.",
    },
    "Thiên Hỉ": {
        "net_canon": ["hỉ sự/chuyện vui mừng", "đối cung với Hồng Loan/cặp đôi với sao duyên tình"],
        "thuan_viet": "Báo hiệu chuyện vui mừng (cưới hỏi, sinh nở), thường đi thành cặp với điềm duyên tình ở phía đối diện.",
    },
    "Thiên Hỷ": {
        "net_canon": ["hỉ sự/chuyện vui mừng", "đối cung với Hồng Loan/cặp đôi với sao duyên tình"],
        "thuan_viet": "Báo hiệu chuyện vui mừng (cưới hỏi, sinh nở), thường đi thành cặp với điềm duyên tình ở phía đối diện.",
    },
    "Xương Khúc": {
        "net_canon": ["gồm hai phần văn học chữ nghĩa và tài hoa nghệ thuật", "chủ văn học/giỏi chữ nghĩa"],
        "thuan_viet": "Cặp dấu hiệu của người giỏi chữ nghĩa, có khiếu văn học và tài hoa.",
    },
    "Đào Hoa": {
        "net_canon": ["tình duyên/duyên với người khác phái", "dâm dật/say mê chuyện tình cảm"],
        "thuan_viet": "Dấu hiệu của duyên tình đậm với người khác phái, dễ say mê và đắm trong chuyện tình cảm.",
    },
    # ===== TỨ HOÁ =====
    "Hóa Lộc": {
        "net_canon": ["tài lộc/tiền của", "may mắn", "phú quý/giàu sang"],
        "thuan_viet": "Dấu hiệu tiền của tới, gặp may, và đời sống dư dả sung túc.",
    },
    "Hóa Quyền": {
        "net_canon": ["quyền lực", "địa vị/chức phận"],
        "thuan_viet": "Dấu hiệu nắm được quyền hành và có địa vị, chức phận trong tay.",
    },
    "Hóa Khoa": {
        "net_canon": ["danh tiếng/tiếng thơm", "học hành/thi cử đỗ đạt"],
        "thuan_viet": "Dấu hiệu có tiếng thơm và đường học hành thi cử thuận lợi đỗ đạt.",
    },
    "Hóa Kỵ": {
        "net_canon": ["tai ương", "khó khăn/trắc trở", "ảnh hưởng xấu tới mệnh/làm hỏng việc"],
        "thuan_viet": "Dấu hiệu vướng tai ương, gặp khó khăn trắc trở, làm cho việc đang tốt bị hỏng đi.",
    },
    # ===== LỤC SÁT + KHÔNG KIẾP =====
    "Kình Dương": {
        "net_canon": ["hung/khí xấu", "hình phạt/dao kéo thương tích", "chướng ngại/cản trở", "đụng độ/va chạm tranh chấp"],
        "thuan_viet": "Mang khí xấu cứng, dễ dính thương tích dao kéo hoặc kiện cáo, hay gặp cản trở và va chạm tranh chấp với người.",
    },
    "Đà La": {
        "net_canon": ["hung/khí xấu", "tù tội/vướng vòng lao lý", "gian trá/dối trá dây dưa"],
        "thuan_viet": "Mang khí xấu âm ỉ, dễ vướng chuyện lao lý kéo dài, và liên quan tới gian dối lằng nhằng dây dưa.",
    },
    "Hỏa Tinh": {
        "net_canon": ["thuộc Hoả", "nóng nảy/dễ bốc", "hung bạo/dữ dằn"],
        "thuan_viet": "Mang khí lửa, tính nóng nảy dễ bốc, khi nổi lên thì dữ dằn mạnh bạo.",
    },
    "Linh Tinh": {
        "net_canon": ["thuộc Hoả", "nóng nảy/dễ bốc", "tai nạn", "xung đột/va chạm"],
        "thuan_viet": "Mang khí lửa ngầm, tính nóng dễ bùng, dễ gặp tai nạn bất ngờ và va chạm xung đột.",
    },
    "Địa Không": {
        "net_canon": ["hư vô/trống rỗng mất mát", "thất bại", "kỵ hợp với Kiếp/gặp sao phá tán càng xấu"],
        "thuan_viet": "Báo hiệu sự trống rỗng mất mát và dễ thất bại; càng nặng khi đi cùng sao phá tán kia.",
    },
    "Địa Kiếp": {
        "net_canon": ["hung/khí xấu", "tai hoạ", "mất mát", "kiếp nạn/tai ách lớn"],
        "thuan_viet": "Mang khí xấu báo tai hoạ, dễ mất mát của cải và gặp tai ách lớn trong đời.",
    },
    "Thiên Không": {
        "net_canon": ["hư không/trống rỗng", "phá tài/hao của", "kỵ gặp ở mệnh thân/đóng tại bản thân thì xấu"],
        "thuan_viet": "Báo hiệu sự trống rỗng và hao hụt tiền của; đóng ngay vào bản thân thì càng bất lợi.",
    },
    "Hỏa Linh": {
        "net_canon": ["gồm hai sao đều thuộc Hoả", "đều là sát tinh/đều mang khí xấu"],
        "thuan_viet": "Cặp khí lửa, cả hai đều là dấu hiệu xấu nóng gấp dễ sinh biến.",
    },
    "Không Kiếp": {
        "net_canon": ["gồm hai sao đều thuộc Hoả", "đều là sát tinh", "chủ phá tán/làm hao tan của cải"],
        "thuan_viet": "Cặp khí xấu, cùng nhau làm hao tán mất mát của cải.",
    },
    # ===== PHỤ TINH CÁT / QUÝ NHÂN =====
    "Thiên Mã": {
        "net_canon": ["di động/hay di chuyển", "xa xôi/đi xa", "xuất ngoại/ra nước ngoài"],
        "thuan_viet": "Dấu hiệu của người hay di chuyển, đi lại xa xôi, dễ ra nước ngoài hoặc làm ăn xa nhà.",
    },
    "Văn Xương": {
        "net_canon": ["văn học/giỏi chữ nghĩa", "khoa cử/thi cử", "thông minh"],
        "thuan_viet": "Người giỏi chữ nghĩa, thuận đường thi cử, đầu óc thông minh sáng láng.",
    },
    "Văn Khúc": {
        "net_canon": ["văn chương/giỏi viết lách", "nghệ thuật", "tài năng/có khiếu"],
        "thuan_viet": "Người có khiếu văn chương viết lách, giỏi nghệ thuật và nhiều tài lẻ.",
    },
    "Tả Phù": {
        "net_canon": ["hỗ trợ/giúp sức", "phụ tá/người phò bên cạnh", "cùng người đứng đầu tạo nên quyền lực"],
        "thuan_viet": "Người trợ giúp đắc lực đứng bên cạnh phò tá, góp sức cùng người chủ tạo nên thế lực.",
    },
    "Tả Phụ": {
        "net_canon": ["hỗ trợ/giúp sức", "phụ tá/người phò bên cạnh", "cùng người đứng đầu tạo nên quyền lực"],
        "thuan_viet": "Người trợ giúp đắc lực đứng bên cạnh phò tá, góp sức cùng người chủ tạo nên thế lực.",
    },
    "Hữu Bật": {
        "net_canon": ["phò tá/giúp sức", "giống Tả Phụ/vai trợ thủ", "kết hợp với người đứng đầu"],
        "thuan_viet": "Người trợ thủ đắc lực, sát cánh giúp sức cho người chủ giống như một cánh tay phải.",
    },
    "Thiên Khôi": {
        "net_canon": ["quý nhân/người tốt nâng đỡ", "giúp đỡ", "được tôn trọng/có uy"],
        "thuan_viet": "Dấu hiệu có quý nhân là người trên ra tay giúp đỡ, và bản thân được người ta nể trọng.",
    },
    "Thiên Việt": {
        "net_canon": ["quý nhân/người tốt nâng đỡ", "tương tự Thiên Khôi/cùng loại quý nhân"],
        "thuan_viet": "Dấu hiệu có quý nhân nâng đỡ, cùng một loại với điềm gặp người tốt giúp sức.",
    },
    "Khôi Việt": {
        "net_canon": ["gồm hai sao quý nhân", "quý hiển/được trọng vọng cao", "tài lộc/tiền của"],
        "thuan_viet": "Cặp dấu hiệu quý nhân, đem lại sự trọng vọng cao và cả tiền của.",
    },
    "Thiên Hình": {
        "net_canon": ["hình phạt/dính chuyện trừng phạt", "pháp luật/liên quan luật lệ", "nghiêm khắc/cứng rắn kỷ luật"],
        "thuan_viet": "Dấu hiệu liên quan tới luật lệ và sự trừng phạt, con người nghiêm khắc cứng rắn giữ kỷ luật.",
    },
    "Thiên Khốc": {
        "net_canon": ["thuộc Kim", "tang trở/việc buồn ma chay trắc trở", "buồn thương/khóc lóc đau xót"],
        "thuan_viet": "Mang khí kim, báo hiệu chuyện buồn tang tóc trắc trở, và nỗi buồn thương đau xót.",
    },
    "Thiên Hư": {
        "net_canon": ["sao ác/khí xấu", "cùng Thiên Khốc gây hoạ cho mệnh chủ/đi đôi với sao buồn làm hại bản thân"],
        "thuan_viet": "Mang khí xấu, đi đôi với điềm buồn thương để gây hoạ rắc rối cho chính bản thân người đó.",
    },
    "Âm Sát": {
        "net_canon": ["âm thầm/ngấm ngầm", "tai hoạ ngầm/rắc rối ẩn không thấy trước"],
        "thuan_viet": "Dấu hiệu tai hoạ ngấm ngầm, rắc rối ẩn nấp khó thấy trước nên hay bị bất ngờ.",
    },
    "Tam Thai": {
        "net_canon": ["sao phụ/vai phụ trợ", "mô phạm", "mẫu mực/đàng hoàng nề nếp"],
        "thuan_viet": "Dấu hiệu phụ trợ cho thấy con người mô phạm, sống mẫu mực nề nếp đàng hoàng.",
    },
    "Bát Tọa": {
        "net_canon": ["quý tử/con cái quý", "quyền bính/có quyền vị"],
        "thuan_viet": "Dấu hiệu có con cái quý hiển và bản thân nắm được quyền vị.",
    },
    "Lộc Tồn": {
        "net_canon": ["lộc/của cải tới", "của cải", "bền vững/giữ được lâu dài"],
        "thuan_viet": "Dấu hiệu của cải tiền bạc tới và giữ được bền vững lâu dài.",
    },
    "Tiểu Hao": {
        "net_canon": ["thuộc nhóm sao theo năm tuổi", "hao tiền/tốn kém vặt"],
        "thuan_viet": "Dấu hiệu hao tiền tốn kém lặt vặt theo năm.",
    },
    "Bách Quan Triều Củng": {
        "net_canon": ["người đứng đầu được nhiều sao tốt vây quanh", "cách quý/thế cục cao sang"],
        "thuan_viet": "Cảnh người chủ được nhiều người giỏi và điềm tốt vây quanh phò trợ, là thế cục cao sang đáng quý.",
    },
    # ===== THẬP THẦN (Bát Tự) =====
    "Chính Quan": {
        "net_canon": ["khắc Nhật chủ, khác âm dương/lực ràng buộc chính danh", "chức tước chính thống", "kỷ luật", "chồng (với nữ)", "tích cực: chức vụ chính danh, danh tiếng tốt", "tiêu cực: gò bó, áp lực kỷ luật", "sợ Thương Quan đả phá", "sợ Thất Sát hỗn tạp"],
        "thuan_viet": "Sức ép chính đáng giữ người vào khuôn phép: hợp với chức vụ danh chính ngôn thuận, danh tiếng tốt và nền nếp kỷ luật; với nữ đại diện người chồng. Mặt trái là cảm giác gò bó áp lực. Dễ bị hỏng khi gặp tài năng phá cách lấn át, hoặc khi lẫn lộn với loại quyền lực dữ.",
    },
    "Thiên Quan": {
        "net_canon": ["khắc Nhật chủ, cùng âm dương/quyền lực dữ dội", "áp lực mạnh", "tướng quân/đối thủ mạnh", "tích cực: quân đội, công an, kinh doanh mạo hiểm, lãnh đạo", "tiêu cực: tai hoạ, kiện tụng, kẻ thù", "cần được kiềm chế (chế) hoặc chuyển hoá (hoá) thì thành quý hiển"],
        "thuan_viet": "Quyền lực dữ dằn và áp lực mạnh, như sức của một viên tướng hay một đối thủ ngang ngửa: hợp với binh nghiệp, công an, làm ăn mạo hiểm và vai trò chỉ huy; nhưng nếu buông lỏng thì hoá tai hoạ, kiện tụng, sinh kẻ thù. Phải biết kiềm chế hoặc chuyển hoá nó thì mới thành người quý hiển.",
    },
    "Quan Sát": {
        "net_canon": ["gộp Chính Quan + Thất Sát/cùng nhóm áp lực bên ngoài", "khắc Nhật chủ", "với nữ đại diện chồng/phối ngẫu", "Chính Quan = ràng buộc chính đáng, danh phận", "Thất Sát = áp lực mạnh, uy quyền"],
        "thuan_viet": "Gộp chung hai loại sức ép từ bên ngoài đè lên bản thân: một bên là ràng buộc danh chính ngôn thuận có danh phận, một bên là áp lực mạnh đầy uy quyền; với người nữ đây chính là hình ảnh người chồng, người bạn đời.",
    },
    "Thương Quan": {
        "net_canon": ["Nhật chủ sinh ra, khác âm dương/sức biểu đạt tuôn ra vượt khuôn", "tài năng vượt khuôn khổ", "phá cách/nổi loạn", "tích cực: nghệ sĩ độc đáo, khởi nghiệp đột phá, tài ăn nói", "tiêu cực: ngạo mạn, vô lễ, khắc chồng (với nữ)", "cần được khuôn lại (phối Ấn) thì tài năng có khuôn"],
        "thuan_viet": "Năng lực tuôn ra mạnh vượt mọi khuôn phép: làm nên nghệ sĩ độc đáo, người khởi nghiệp đột phá, tài ăn nói hơn người; nhưng buông thả thì hoá kiêu ngạo, vô lễ, và với nữ thì lấn át khắc chế người chồng. Cần có cái khuôn ghìm lại thì tài năng mới thành nề nếp.",
    },
    "Thực Thần": {
        "net_canon": ["Nhật chủ sinh ra, cùng âm dương/sức sáng tạo nuôi dưỡng êm", "tài năng sáng tạo", "hưởng thụ", "nuôi dưỡng", "tích cực: nghệ thuật, ẩm thực, giáo dục, sinh con, phúc lộc", "tiêu cực: lười nhác, ham hưởng thụ", "kỵ bị Thiên Ấn cướp mất nguồn lộc"],
        "thuan_viet": "Sức sáng tạo êm đềm biết nuôi dưỡng và tận hưởng: hợp với nghệ thuật, ẩm thực, dạy học, chuyện con cái và phúc lộc dồi dào; mặt trái là dễ lười và ham hưởng thụ. Sợ nhất bị loại khí lệch cướp mất nguồn nuôi sống này.",
    },
    "食伤": {
        "net_canon": ["gộp Thực Thần + Thương Quan/do Nhật chủ sinh ra", "tài năng", "biểu đạt", "sáng tạo", "nữ mệnh khắc sao chồng"],
        "thuan_viet": "Gộp chung phần năng lực do bản thân toả ra ngoài: tài năng, khả năng biểu đạt và óc sáng tạo; với người nữ, phần khí này có thể lấn át sao người chồng.",
    },
    "Thực Thương": {
        "net_canon": ["gộp Thực Thần + Thương Quan/do Nhật chủ sinh ra", "sáng tạo", "biểu đạt", "nữ mệnh khắc sao chồng"],
        "thuan_viet": "Gộp chung phần năng lực do bản thân toả ra ngoài: óc sáng tạo và khả năng biểu đạt; với người nữ, phần khí này có thể lấn át sao người chồng.",
    },
    "Chính Tài": {
        "net_canon": ["Nhật chủ khắc, khác âm dương/của cải mình làm chủ chính đáng", "tài chính ổn định", "lương cứng", "vợ chính (với nam)", "tích cực: cần kiệm, tích luỹ, gia đình ổn", "tiêu cực: cứng nhắc, sợ rủi ro", "khi bản thân vượng + tài vượng thì đại phú"],
        "thuan_viet": "Của cải chính đáng do mình làm chủ một cách đều đặn: tiền lương ổn định, biết cần kiệm tích cóp, gia đình êm ấm; với nam đại diện người vợ chính thức. Mặt trái là cứng nhắc, ngại rủi ro. Khi bản thân đủ mạnh mà phần của cải này cũng mạnh thì giàu lớn.",
    },
    "Thiên Tài": {
        "net_canon": ["Nhật chủ khắc, cùng âm dương/của cải linh động", "tài lộc bất ngờ", "đào hoa", "đầu cơ", "tích cực: kinh doanh đa lĩnh vực, môi giới, có sức hút", "tiêu cực: phá tài bất ngờ, đào hoa loạn"],
        "thuan_viet": "Của cải tới bất ngờ và linh động: hợp làm ăn nhiều ngành, môi giới, người có sức hút, dễ trúng món lớn; nhưng cũng dễ mất của đột ngột và đào hoa rối ren ngoài luồng.",
    },
    # Cụm gộp 财 = Chính Tài + Thiên Tài (COMPOSE) — KHÔNG phải "tiền bạc + danh lợi"
    # (drift Hoàng Cực). Thập thần Nhật chủ KHẮC; nam mệnh = vợ.
    "财": {
        "net_canon": ["gộp Chính Tài + Thiên Tài/nhóm Nhật chủ khắc", "của cải mình làm chủ (chính: ổn định; thiên: bất ngờ, linh động)", "với nam đại diện người vợ/phối ngẫu (tầng product)"],
        "thuan_viet": "Gộp chung phần của cải mà bản thân làm chủ: một bên là tiền bạc ổn định chính đáng, một bên là tài lộc tới bất ngờ linh động; với người nam, phần khí này còn là hình ảnh người vợ, người bạn đời.",
    },
    "Chính Ấn": {
        "net_canon": ["sinh Nhật chủ, khác âm dương/nguồn nuôi dưỡng che chở chính thống", "mẹ ruột", "học vấn chính quy", "ấn tín bảo hộ/giấy tờ chứng nhận bảo vệ", "tích cực: trí tuệ, danh tiếng học thuật, nhân từ, từ thiện", "tiêu cực: ỷ lại, lười suy nghĩ độc lập", "kỵ bị của cải làm hỏng (Tài đoạt Ấn)"],
        "thuan_viet": "Nguồn nuôi dưỡng và che chở chính thống: hình ảnh mẹ ruột, sự học hành bài bản, giấy tờ chứng nhận bảo vệ mình; đem lại trí tuệ, tiếng thơm học thuật, lòng nhân hậu hay làm việc thiện. Mặt trái là dễ ỷ lại, lười tự suy nghĩ. Sợ bị ham tiền của làm hỏng mất chỗ dựa này.",
    },
    # THẬP THẦN Bát Tự 偏印 (KHÔNG phải SAO Tử Vi "ấn tín") — sinh Nhật chủ cùng
    # âm dương; tục danh Kiêu Thần, dễ đoạt Thực Thần.
    "Thiên Ấn": {
        "net_canon": ["sinh Nhật chủ, cùng âm dương/nguồn nuôi dưỡng lệch, không chính thống", "quý nhân ngầm", "mẹ kế", "trí tuệ phi truyền thống", "tích cực: thiền, tôn giáo, nghiên cứu lập dị, công nghệ", "tiêu cực: Kiêu Thần đoạt Thực Thần → mất phúc"],
        "thuan_viet": "Nguồn nuôi dưỡng và che chở theo lối lệch, không chính thống: hình ảnh quý nhân giúp ngầm, người mẹ kế, đầu óc khác người; hợp với thiền, tôn giáo, nghiên cứu lập dị và công nghệ. Mặt trái là nó hay cướp mất nguồn phúc lộc êm đềm của bản thân.",
    },
    # Cụm gộp 印 = Chính Ấn + Thiên Ấn (COMPOSE) — KHÔNG phải "chữ ký/tâm ấn" (drift
    # Mai Hoa). Thập thần SINH Nhật chủ: che chở, học vấn, nương tựa; Ấn chế Thương Quan.
    "Ấn Tinh": {
        "net_canon": ["gộp Chính Ấn + Thiên Ấn/nhóm sinh Nhật chủ", "che chở, nương tựa", "học vấn", "Ấn chế Thương Quan (bảo vệ sao chồng ở nữ mệnh)"],
        "thuan_viet": "Gộp chung nguồn nuôi dưỡng và chỗ dựa cho bản thân: sự che chở, học hành và nơi nương tựa; loại khí này còn ghìm bớt phần tài năng phá cách (Thương Quan), nên với người nữ nó gián tiếp bảo vệ sao người chồng.",
    },
    "ấn tinh": {
        "net_canon": ["gộp Chính Ấn + Thiên Ấn/nhóm sinh Nhật chủ", "che chở, nương tựa", "học vấn", "Ấn chế Thương Quan (bảo vệ sao chồng ở nữ mệnh)"],
        "thuan_viet": "Gộp chung nguồn nuôi dưỡng và chỗ dựa cho bản thân: sự che chở, học hành và nơi nương tựa; loại khí này còn ghìm bớt phần tài năng phá cách (Thương Quan), nên với người nữ nó gián tiếp bảo vệ sao người chồng.",
    },
    "Tỷ Kiên": {
        "net_canon": ["cùng hành + cùng âm dương với Nhật chủ/người ngang vai giống mình", "anh em ngang vai", "đồng nghiệp", "cạnh tranh trực diện", "tích cực: hỗ trợ, độc lập, ý chí", "tiêu cực: cứng đầu, tranh chấp, hao của"],
        "thuan_viet": "Hình ảnh người ngang vai giống hệt mình — anh em, bạn đồng nghiệp, đối thủ cạnh tranh ngang ngửa: đem lại sự hỗ trợ, tính độc lập và ý chí; mặt trái là cứng đầu, hay tranh chấp và tốn kém của cải vì chia sẻ.",
    },
    "Kiếp Tài": {
        "net_canon": ["cùng hành + khác âm dương với Nhật chủ/người giống mình nhưng giành phần", "người cướp của/đối thủ ngầm", "tích cực: dũng mãnh, hành động nhanh", "tiêu cực: hao tổn tài lộc, dễ bị lừa, bị cướp đoạt vô hình", "ở Trụ Tháng thành cách đặc biệt (Dương Nhận)"],
        "thuan_viet": "Hình ảnh người giống mình nhưng tới giành phần — đối thủ ngầm hay kẻ chực cướp của: cho mình sự gan dạ và ra tay nhanh, nhưng cũng làm hao của, dễ bị lừa và mất mát một cách vô hình. Nếu nằm ở trụ tháng thì thành một thế cục riêng đặc biệt.",
    },
    "Tỷ Kiếp": {
        "net_canon": ["gộp Tỷ Kiên + Kiếp Tài/cùng loại với Nhật chủ", "anh em, bằng hữu, cạnh tranh", "ở nam mệnh khắc của cải nên là kẻ khắc vợ"],
        "thuan_viet": "Gộp chung những người ngang vai giống mình — anh em, bạn bè, đối thủ cạnh tranh; với nam, nhóm này tranh mất phần của cải nên cũng là dấu hiệu khắc vợ.",
    },
    "Chính Quan Thất Sát": {
        "net_canon": ["gộp Chính Quan + Thất Sát/nhóm áp lực bên ngoài", "khắc Nhật chủ", "nữ mệnh là sao phối ngẫu (chồng)"],
        "thuan_viet": "Gộp chung hai loại sức ép từ bên ngoài đè lên bản thân; với người nữ, đây là hình ảnh người bạn đời, người chồng.",
    },
    "官杀": {
        "net_canon": ["gộp Chính Quan + Thất Sát/nhóm áp lực bên ngoài", "khắc Nhật chủ", "nữ mệnh = sao chồng"],
        "thuan_viet": "Gộp chung hai loại sức ép từ bên ngoài đè lên bản thân; với người nữ, đây là hình ảnh người chồng.",
    },
    # ===== LÝ THUYẾT TỬ BÌNH (neo concept_index tu_binh_ba_tu) =====
    "Nhật chủ": {
        "net_canon": ["Thiên Can của Trụ Ngày", "đại biểu cho BẢN THÂN người được xem", "mọi phân tích thập thần/dụng thần/cách cục đều quy chiếu về nó"],
        "thuan_viet": "Là chữ đứng ở cột ngày sinh, dùng làm đại diện cho chính bản thân người được xem; mọi thứ khác trong lá số đều được đọc trong tương quan với nó.",
    },
    "dụng thần": {
        "net_canon": ["hành cốt yếu cứu mệnh/'thuốc' cho lá số", "bản thân vượng → cần khí làm hao tiết (sinh ra, của cải, sức ép)", "bản thân nhược → cần khí hỗ trợ (nuôi dưỡng, người cùng loại)", "chặng vận đi vào dụng thần → vận tốt; đi vào khí kỵ → vận xấu", "có thêm tầng cân bằng nóng-lạnh (điều hậu)"],
        "thuan_viet": "Là yếu tố cốt lõi giữ cân bằng cho lá số, ví như vị thuốc chữa bệnh: nếu bản thân quá mạnh thì cần thứ làm bớt đi, nếu bản thân quá yếu thì cần thứ nâng đỡ thêm. Chặng đời nào gặp được yếu tố này thì hanh thông, gặp thứ ngược lại thì trắc trở; ngoài ra còn xét thêm việc cân bằng nóng-lạnh của lá số.",
    },
    "ngũ hành sinh": {
        "net_canon": ["quy luật ngũ hành: Mộc→Hỏa→Thổ→Kim→Thủy→Mộc (vòng tuần hoàn)", "sinh = nuôi dưỡng, tiếp khí"],
        "thuan_viet": "Quy luật năm hành nuôi nhau theo vòng: Mộc nuôi Hỏa, Hỏa nuôi Thổ, Thổ nuôi Kim, Kim nuôi Thủy, Thủy lại nuôi Mộc; 'sinh' ở đây nghĩa là tiếp sức, nuôi dưỡng cho nhau.",
    },
    "ngũ hành khắc": {
        "net_canon": ["quy luật ngũ hành: Mộc khắc Thổ, Thổ khắc Thủy, Thủy khắc Hỏa, Hỏa khắc Kim, Kim khắc Mộc (cách ngôi)", "khắc = chế ngự, kìm hãm"],
        "thuan_viet": "Quy luật năm hành kìm nhau theo lối cách quãng: Mộc kìm Thổ, Thổ kìm Thủy, Thủy kìm Hỏa, Hỏa kìm Kim, Kim kìm Mộc; 'khắc' ở đây nghĩa là chế ngự, kìm hãm bớt nhau.",
    },
    # ===== LÝ THUYẾT / TRẠNG THÁI SAO (quy ước an-sao Tử Vi) =====
    "đại vận": {
        "net_canon": ["giai đoạn khoảng 10 năm", "mỗi đại vận lần lượt quản một cung", "đọc cát-hung động theo thời/xem tốt xấu thay đổi theo từng chặng"],
        "thuan_viet": "Một chặng đời khoảng mười năm; mỗi chặng lần lượt cai quản một mảng cuộc sống, nên phải xem cái tốt cái xấu chuyển động theo từng chặng chứ không cố định.",
    },
    "lưu niên": {
        "net_canon": ["năm cụ thể đang xét", "chồng lên đại vận để định thời sự việc"],
        "thuan_viet": "Năm cụ thể đang được xem; đặt chồng lên chặng mười năm để định xem việc rơi vào lúc nào.",
    },
    "tiểu hạn": {
        "net_canon": ["vận trong một năm", "an theo tuổi", "một tầng định thời song song lưu niên"],
        "thuan_viet": "Vận của riêng một năm, tính theo tuổi; là một cách định thời đi song song với năm đang xét.",
    },
    "lưu nguyệt": {
        "net_canon": ["tháng cụ thể đang xét", "tầng định thời nhỏ hơn năm"],
        "thuan_viet": "Việc xem riêng cho một tháng cụ thể, là mức chia thời gian nhỏ hơn cả năm.",
    },
    "hãm": {
        "net_canon": ["sao đóng tại cung vị xấu", "suy yếu", "mang lại điều không may"],
        "thuan_viet": "Dấu hiệu rơi vào vị trí bất lợi nên yếu sức và kéo theo điều không may.",
    },
    "thất hãm": {
        "net_canon": ["sao lạc cung xấu", "mất thế", "sinh ra hung hoạ"],
        "thuan_viet": "Dấu hiệu lạc vào chỗ xấu, mất chỗ đứng đẹp, nên dễ sinh chuyện rủi ro.",
    },
    "lạc hãm": {
        "net_canon": ["trạng thái xấu của sao", "khó phát huy tác dụng"],
        "thuan_viet": "Trạng thái rơi vào chỗ bất lợi nên khó phát huy được mặt mạnh của mình.",
    },
    "miếu": {
        "net_canon": ["sao đắc địa/ở đúng chỗ đẹp", "phát huy tối đa năng lượng"],
        "thuan_viet": "Trạng thái ở đúng chỗ đẹp nhất nên phát huy được hết sức mạnh.",
    },
    "vượng": {
        "net_canon": ["thịnh vượng", "sức mạnh đạt đỉnh"],
        "thuan_viet": "Trạng thái đang thịnh, sức mạnh lên tới đỉnh cao.",
    },
    "nhập miếu": {
        "net_canon": ["sao đắc địa/vào đúng chỗ đẹp", "mạnh mẽ", "mang lại may mắn và quý hiển"],
        "thuan_viet": "Trạng thái vào đúng chỗ đẹp nhất, sức mạnh dồi dào, đem lại may mắn và sự sang quý.",
    },
    "đắc địa": {
        "net_canon": ["sao đóng tại cung tốt", "hưởng phúc", "bình hoà/yên ổn"],
        "thuan_viet": "Trạng thái ở vào chỗ tốt nên được hưởng phúc, yên ổn bình hoà.",
    },
    "vượng địa": {
        "net_canon": ["cung vị tốt", "có vượng khí/khí thịnh", "thuận lợi"],
        "thuan_viet": "Chỗ đứng tốt, khí lực dồi dào nên mọi việc thuận lợi.",
    },
    "trung tính": {
        "net_canon": ["không thiên tốt cũng không thiên xấu", "phải xét bối cảnh các sao hội tụ"],
        "thuan_viet": "Sắc thái không ngả hẳn về tốt hay xấu, phải nhìn cả bối cảnh xung quanh mới định được.",
    },
    "đắc": {
        "net_canon": ["sao đóng ở vị trí thuận", "phát huy được lực"],
        "thuan_viet": "Trạng thái ở vào chỗ thuận nên phát huy được sức của mình.",
    },
    "tường hòa": {
        "net_canon": ["khí ôn hoà", "an ổn", "trạng thái lành"],
        "thuan_viet": "Trạng thái khí êm ả, an ổn và lành.",
    },
    "chính tinh": {
        "net_canon": ["14 sao chính", "trục mô tả cốt lõi của một cung"],
        "thuan_viet": "Nhóm mười bốn dấu hiệu chính yếu, là cái trục cốt lõi để mô tả một mảng cuộc sống.",
    },
    "chính diệu": {
        "net_canon": ["cách gọi khác của chính tinh", "14 sao chính"],
        "thuan_viet": "Tên gọi khác của nhóm mười bốn dấu hiệu chính yếu cốt lõi.",
    },
    "phụ tinh": {
        "net_canon": ["sao phụ trợ", "tăng hoặc giảm lực của sao chính"],
        "thuan_viet": "Những dấu hiệu phụ đi kèm, làm mạnh thêm hoặc yếu bớt sức của dấu hiệu chính.",
    },
    "tạp diệu": {
        "net_canon": ["sao lẻ/tạp", "đọc theo cụm, không phán độc lập"],
        "thuan_viet": "Những dấu hiệu lẻ tẻ phụ thêm, phải đọc gộp theo cụm chứ không kết luận riêng từng cái.",
    },
    "không diệu": {
        "net_canon": ["gồm hai sao trống/hao", "chủ trống trải, hao tổn", "cũng kìm bớt đào hoa"],
        "thuan_viet": "Cặp dấu hiệu của sự trống trải và hao tổn, nhưng cũng có mặt kìm bớt được chuyện tình cảm lăng nhăng.",
    },
    "lưu Kình": {
        "net_canon": ["sao cứng sắc theo năm/khí xấu cương xuất hiện trong năm đang xét"],
        "thuan_viet": "Dấu hiệu khí xấu cứng sắc rơi đúng vào năm đang xét.",
    },
    "lưu Đà": {
        "net_canon": ["sao xấu dây dưa theo năm/khí xấu lằng nhằng xuất hiện trong năm đang xét"],
        "thuan_viet": "Dấu hiệu khí xấu lằng nhằng dây dưa rơi đúng vào năm đang xét.",
    },
    "lưu Lộc": {
        "net_canon": ["lộc khí theo năm/của cải may mắn rơi vào năm đang xét"],
        "thuan_viet": "Dấu hiệu lộc khí, của cải may mắn rơi đúng vào năm đang xét.",
    },
    "Kình-Đà giáp": {
        "net_canon": ["hai sao xấu kẹp hai bên một cung", "kết cấu ép", "làm xấu lực sao bị kẹp"],
        "thuan_viet": "Cảnh hai khí xấu kẹp chặt hai bên một mảng cuộc sống, tạo thế bị ép khiến mảng đó yếu đi.",
    },
    "Kình Đà giáp": {
        "net_canon": ["hai sao xấu kẹp hai bên một cung", "kết cấu ép"],
        "thuan_viet": "Cảnh hai khí xấu kẹp chặt hai bên một mảng cuộc sống, tạo thế bị ép.",
    },
    "cương khắc": {
        "net_canon": ["khí quá cứng dẫn tới xung khắc người thân", "cần xét mức độ, không kết án"],
        "thuan_viet": "Khí quá cứng dễ va chạm khắc khẩu với người thân; nhưng phải cân nhắc nặng nhẹ chứ không vội kết tội.",
    },
    "cô khắc": {
        "net_canon": ["khuynh hướng cô độc/khó gần", "do khí cương liệt mạnh cứng"],
        "thuan_viet": "Khuynh hướng sống một mình, khó gần, sinh ra từ tính khí quá mạnh cứng.",
    },
    "cương liệt": {
        "net_canon": ["tính cứng mạnh", "quyết liệt"],
        "thuan_viet": "Tính khí cứng cỏi mạnh mẽ, làm gì cũng quyết liệt.",
    },
    "sát cương": {
        "net_canon": ["sát tinh mang khí cứng/khí xấu cứng rắn", "chủ hình thương, tranh chấp"],
        "thuan_viet": "Khí xấu loại cứng rắn, hay đem tới thương tích và tranh chấp va chạm.",
    },
    "sát hỏa": {
        "net_canon": ["sát tinh thuộc hoả/khí xấu loại lửa", "chủ nóng gấp, biến cố nhanh"],
        "thuan_viet": "Khí xấu loại lửa, làm việc nóng vội và biến cố ập tới rất nhanh.",
    },
    "sát âm": {
        "net_canon": ["sát tinh trầm/âm/khí xấu loại ngầm", "chủ dây dưa, uất kết ngầm"],
        "thuan_viet": "Khí xấu loại âm ỉ, kéo dài dây dưa và dồn nén uất ức bên trong.",
    },
    "gặp sát": {
        "net_canon": ["hội hoặc đồng cung với sát tinh/đụng phải khí xấu", "tăng sắc thái xung khắc", "cần giữ gìn"],
        "thuan_viet": "Tình huống đụng phải khí xấu, làm tăng phần va chạm xung khắc nên cần giữ gìn thận trọng.",
    },
    "hội sát": {
        "net_canon": ["sát tinh chiếu tới từ tam phương tứ chính/khí xấu chiếu sang", "như gặp sát"],
        "thuan_viet": "Tình huống khí xấu từ các góc chiếu sang một mảng, tác động tương tự như khi đụng phải khí xấu.",
    },
    "sát-kỵ": {
        "net_canon": ["sát tinh cộng khí làm hỏng việc (Hoá Kỵ)", "cụm tín hiệu cần lưu tâm nhất", "không phải bản án"],
        "thuan_viet": "Khí xấu cộng thêm điềm làm hỏng việc — đây là cụm dấu hiệu cần để mắt nhất, nhưng vẫn chỉ là dấu hiệu chứ không phải bản án.",
    },
    "sát kỵ": {
        "net_canon": ["sát tinh cộng khí làm hỏng việc (Hoá Kỵ)", "cụm cần lưu tâm"],
        "thuan_viet": "Khí xấu cộng thêm điềm làm hỏng việc — cụm dấu hiệu cần để mắt tới.",
    },
    "thượng cách": {
        "net_canon": ["cách cục cao", "hội tụ nhiều điềm tốt", "hợp khuôn mẫu kinh điển"],
        "thuan_viet": "Thế cục bậc cao, tụ nhiều điềm tốt và khớp với khuôn mẫu đẹp của sách xưa.",
    },
    "trung cách": {
        "net_canon": ["cách cục mức trung", "không cao cũng không thấp"],
        "thuan_viet": "Thế cục mức trung bình, không nổi trội mà cũng không kém.",
    },
    "thuộc hạ cách": {
        "net_canon": ["cách cục mức thấp theo phú cổ", "đọc lại theo bối cảnh, không kết án"],
        "thuan_viet": "Thế cục bị sách xưa xếp vào mức thấp, nhưng phải đọc lại theo hoàn cảnh thực chứ không vội kết tội.",
    },
    "hạ cách": {
        "net_canon": ["cách cục thấp", "thiếu điềm tốt hoặc kết hợp xấu"],
        "thuan_viet": "Thế cục bậc thấp, do thiếu điềm tốt hoặc các yếu tố ghép lại thành xấu.",
    },
    "đồng cung": {
        "net_canon": ["hai hay nhiều sao cùng nằm trong một cung/cùng một ô"],
        "thuan_viet": "Tình huống hai dấu hiệu trở lên cùng nằm chung trong một ô.",
    },
    "đồng độ": {
        "net_canon": ["hai sao cùng một cung/cùng một ô", "như đồng cung"],
        "thuan_viet": "Tình huống hai dấu hiệu cùng nằm chung một ô, giống như ở chung cung.",
    },
    "đồng triền": {
        "net_canon": ["hai sao cùng vận hành/đóng một cung/đi chung một ô"],
        "thuan_viet": "Tình huống hai dấu hiệu cùng vận hành và đóng chung trong một ô.",
    },
    "hội chiếu": {
        "net_canon": ["sao chiếu tới một cung từ tam phương tứ chính/từ các góc chiếu sang"],
        "thuan_viet": "Tình huống một dấu hiệu từ các góc xa chiếu ảnh hưởng sang một ô.",
    },
    "tam phương": {
        "net_canon": ["ba cung: Thiên Di, Quan Lộc, Tài Bạch/ba mảng đi xa, sự nghiệp, tiền của"],
        "thuan_viet": "Ba mảng cuộc sống liên quan đến nhau: việc đi lại bên ngoài, công danh sự nghiệp và tiền của.",
    },
    "tứ chính": {
        "net_canon": ["bốn chính cung: Mệnh, Thân, Tài, Quan/bản thân, thân, tiền của, sự nghiệp"],
        "thuan_viet": "Bốn mảng trụ cột: con người gốc, tấm thân, tiền của và sự nghiệp.",
    },
    "giáp cung": {
        "net_canon": ["hai cung kề hai bên kẹp cung giữa", "ảnh hưởng tới cung bị kẹp"],
        "thuan_viet": "Cảnh hai ô hai bên kẹp lấy ô ở giữa, tác động lên ô bị kẹp đó.",
    },
    "hóa Lộc": {
        "net_canon": ["tài lộc/tiền của", "may mắn", "phú quý/giàu sang"],
        "thuan_viet": "Dấu hiệu tiền của tới, gặp may, và đời sống dư dả sung túc.",
    },
    "hóa Quyền": {
        "net_canon": ["quyền lực", "địa vị/chức phận"],
        "thuan_viet": "Dấu hiệu nắm được quyền hành và có địa vị, chức phận trong tay.",
    },
    "hóa Khoa": {
        "net_canon": ["danh tiếng/tiếng thơm", "học hành/thi cử đỗ đạt"],
        "thuan_viet": "Dấu hiệu có tiếng thơm và đường học hành thi cử thuận lợi đỗ đạt.",
    },
    "hóa Kỵ": {
        "net_canon": ["tai ương", "khó khăn/trắc trở", "ảnh hưởng xấu tới mệnh/làm hỏng việc"],
        "thuan_viet": "Dấu hiệu vướng tai ương, gặp khó khăn trắc trở, làm cho việc đang tốt bị hỏng đi.",
    },
    "tứ hóa": {
        "net_canon": ["gồm bốn biến hoá: lộc (của cải), quyền, khoa (danh tiếng học hành), kỵ (làm hỏng việc)"],
        "thuan_viet": "Bốn kiểu biến hoá: hoá ra của cải, hoá ra quyền hành, hoá ra danh tiếng học hành, và hoá ra điều làm hỏng việc.",
    },
    "Tứ Hóa": {
        "net_canon": ["gồm bốn biến hoá: lộc (của cải), quyền, khoa (danh tiếng học hành), kỵ (làm hỏng việc)"],
        "thuan_viet": "Bốn kiểu biến hoá: hoá ra của cải, hoá ra quyền hành, hoá ra danh tiếng học hành, và hoá ra điều làm hỏng việc.",
    },
    "Tuần": {
        "net_canon": ["một trục 'không'", "làm yếu hoặc đình hoãn lực sao trong cung nó án ngữ"],
        "thuan_viet": "Một trục mang khí 'trống', làm cho mọi dấu hiệu trong ô nó chắn lại bị yếu đi hoặc bị hoãn lại.",
    },
    "Triệt": {
        "net_canon": ["một trục 'chặn'", "làm sao trong cung bị cắt hoặc đảo lực", "tựa rào chắn"],
        "thuan_viet": "Một trục mang khí 'chặn' như tấm rào, làm cho dấu hiệu trong ô bị cắt đứt hoặc bị đảo ngược tác dụng.",
    },
    "Tuần Triệt": {
        "net_canon": ["gồm trục 'trống' và trục 'chặn'", "đều làm gián đoạn hoặc biến chất lực sao án ngữ"],
        "thuan_viet": "Hai trục — một 'trống' một 'chặn' — đều làm cho dấu hiệu trong ô bị gián đoạn hoặc biến đổi khác đi.",
    },
    "cung Phu Thê": {
        "net_canon": ["ô vợ/chồng trong mười hai mảng", "mô tả người bạn đời và quan hệ hôn nhân"],
        "thuan_viet": "Ô nói về người vợ hoặc chồng, mô tả người bạn đời và đời sống hôn nhân.",
    },
    "cung Mệnh": {
        "net_canon": ["ô gốc của lá số", "trục chính mô tả bản thân"],
        "thuan_viet": "Ô gốc của lá số, là trục chính nói về chính con người mình.",
    },
    "cung Phúc": {
        "net_canon": ["ô phúc đức", "đời sống tinh thần, hưởng thụ, tâm tính"],
        "thuan_viet": "Ô nói về đời sống bên trong: tinh thần, sự hưởng thụ và tâm tính.",
    },
    "cung Tài": {
        "net_canon": ["ô tiền của", "cách kiếm và giữ tiền"],
        "thuan_viet": "Ô nói về tiền của, về cách mình kiếm tiền và giữ tiền.",
    },
    "cung Quan": {
        "net_canon": ["ô quan lộc/sự nghiệp", "công danh, sự nghiệp"],
        "thuan_viet": "Ô nói về công danh và sự nghiệp.",
    },
    "nhật chủ": {
        "net_canon": ["thiên can của ngày sinh", "dùng để phối hợp với các sao/làm gốc đối chiếu"],
        "thuan_viet": "Cái gốc đại diện cho chính bản thân (lấy từ ngày sinh), dùng làm mốc để đối chiếu với mọi yếu tố khác.",
    },
    "thân chủ": {
        "net_canon": ["sao chủ của cung Thân", "thay đổi theo cung an Thân/tuỳ chỗ đặt mà khác"],
        "thuan_viet": "Dấu hiệu cầm chịch cho phần hậu vận của tấm thân, thay đổi tuỳ theo chỗ nó được đặt.",
    },
    "mệnh chủ": {
        "net_canon": ["sao chủ của cung Mệnh", "thay đổi theo cung an Mệnh/tuỳ chỗ đặt mà khác"],
        "thuan_viet": "Dấu hiệu cầm chịch cho phần gốc con người, thay đổi tuỳ theo chỗ nó được đặt.",
    },
    "thân vượng": {
        "net_canon": ["bản thân mạnh", "đủ lực gánh được của cải và áp lực (Tài/Quan)"],
        "thuan_viet": "Trạng thái bản thân đủ mạnh, gánh nổi cả của cải lẫn áp lực trách nhiệm đè lên.",
    },
    "thân nhược": {
        "net_canon": ["bản thân yếu", "cần được nguồn nuôi dưỡng và người ngang vai trợ lực (Ấn/Tỷ)"],
        "thuan_viet": "Trạng thái bản thân còn yếu, cần được nuôi dưỡng và có người ngang vai trợ sức.",
    },
    "Quan nhược": {
        "net_canon": ["sao chồng (nữ mệnh) yếu lực", "cần được sinh trợ/nâng đỡ"],
        "thuan_viet": "Dấu hiệu phần người chồng (với nữ) còn yếu, cần được nuôi dưỡng nâng đỡ thêm.",
    },
    "Quan vượng": {
        "net_canon": ["sao chồng mạnh lực"],
        "thuan_viet": "Dấu hiệu phần người chồng mạnh, đầy đủ sức.",
    },
    "Tài thông quan": {
        "net_canon": ["của cải làm cầu nối từ tài năng tới người chồng (Thương → Tài → Quan)", "hoá giải việc tài năng lấn át người chồng"],
        "thuan_viet": "Phần của cải đứng làm cầu nối, chuyển năng lực cá nhân thành sự bồi đắp cho người chồng, nhờ đó tài năng không còn lấn át bạn đời.",
    },
    "Ấn chế": {
        "net_canon": ["nguồn che chở (Ấn) ghìm bớt sức biểu đạt lấn át (Thương Quan)", "bảo vệ sao chồng"],
        "thuan_viet": "Chỗ dựa che chở đứng ra ghìm bớt năng lực ngang ngạnh, nhờ đó giữ gìn được cho người chồng.",
    },
    "chế hóa": {
        "net_canon": ["chế = khắc khi vượng/ghìm trực tiếp khi khí mạnh", "hoá = sinh chuyển thành khí khác qua trung gian/chuyển hoá qua khâu trung gian"],
        "thuan_viet": "Hai cách xử lý khí mạnh: 'ghìm' là chặn thẳng khi nó đang vượng, còn 'chuyển' là mượn một khâu trung gian để biến nó thành khí khác thay vì đối đầu trực diện.",
    },
    "thông quan": {
        "net_canon": ["một yếu tố làm cầu nối", "hoá giải hai bên đang khắc nhau"],
        "thuan_viet": "Một yếu tố đứng giữa làm cầu nối, gỡ thế hai bên đang xung khắc nhau.",
    },
    "杀破狼": {
        "net_canon": ["gồm ba dấu hiệu xông pha, phá bỏ, khát khao", "trục biến động, khai phá"],
        "thuan_viet": "Bộ ba dấu hiệu của sự xông pha, đập bỏ cái cũ và khát khao lớn — tạo nên một trục đời đầy biến động và khai phá.",
    },
    "Sát Phá Lang": {
        "net_canon": ["gồm ba dấu hiệu xông pha, phá bỏ, khát khao", "bộ ba chủ biến động, khai phá, thay cũ đổi mới"],
        "thuan_viet": "Bộ ba dấu hiệu của sự xông pha, đập bỏ và khát khao lớn — chủ về biến động, khai phá và thay cũ đổi mới.",
    },
    "cô quân": {
        "net_canon": ["người đứng đầu thiếu người phò tá", "vị chủ đứng một mình, dễ cô"],
        "thuan_viet": "Cảnh người chủ thiếu trợ thủ bên cạnh, phải đứng đơn độc một mình nên dễ rơi vào cô quạnh.",
    },
    "bách quan triều củng": {
        "net_canon": ["người đứng đầu được nhiều điềm tốt vây quanh trợ giúp", "cách quý hiển"],
        "thuan_viet": "Cảnh người chủ được nhiều người giỏi và điềm tốt vây quanh phò trợ, là thế cục cao sang đáng quý.",
    },
    "刑忌夹印": {
        "net_canon": ["khí hình phạt + khí làm hỏng việc kẹp lấy người đáng tin/giữ ấn", "kết cấu ép khiến dễ mất chí, nhu nhược", "cần giữ chính kiến"],
        "thuan_viet": "Cảnh khí trừng phạt và khí làm hỏng việc kẹp chặt người vốn đáng tin cậy, tạo thế bị ép khiến họ dễ nản chí mềm yếu — nên phải giữ vững lập trường.",
    },
    "财荫夹印": {
        "net_canon": ["khí của cải + khí che chở kẹp lấy người đáng tin/giữ ấn", "kết cấu nâng đỡ", "nhưng nếu không thuận cũng làm người đó dựa dẫm"],
        "thuan_viet": "Cảnh khí của cải và khí che chở kẹp lấy người đáng tin cậy, tạo thế nâng đỡ; song nếu lệch đi thì cũng dễ khiến người đó sinh tính dựa dẫm.",
    },
    "羊陀夹忌": {
        "net_canon": ["hai khí xấu cứng và dây dưa kẹp lấy một ô có khí làm hỏng việc", "kết cấu rất xấu", "năm/vận đó cần giữ gìn"],
        "thuan_viet": "Cảnh hai khí xấu — một cứng sắc một dây dưa — kẹp chặt một ô vốn đã có điềm hỏng việc; thế này rất xấu nên chặng đời hay năm đó cần hết sức giữ gìn.",
    },
    "羊陀夹武曲": {
        "net_canon": ["hai khí xấu cứng và dây dưa kẹp lấy người cứng cỏi thực tế (Vũ Khúc)", "nhất là khi người đó mang khí hỏng việc", "cương khắc nặng", "rất kỵ với hôn nhân"],
        "thuan_viet": "Cảnh hai khí xấu kẹp chặt người cứng cỏi thực tế, nhất là khi người đó lại mang điềm hỏng việc; khí va chạm rất nặng, đặc biệt bất lợi cho chuyện hôn nhân.",
    },
    "桃花犯主": {
        "net_canon": ["khí tình ái (Tham Lang) nằm chung với người đứng đầu (Tử Vi)", "sắc thái tình dục đậm", "cần khí kỷ luật hoặc khí trống để thành thanh bạch"],
        "thuan_viet": "Cảnh khí tình ái nằm chung với người chủ, làm màu sắc tình dục đậm lên; cần có khí kỷ luật hoặc khí 'trống' kiềm lại thì mới giữ được sự trong sạch.",
    },
    "泛水桃花": {
        "net_canon": ["khí tình ái ở vị trí nước gặp khí cứng sắc", "cách đào hoa nặng", "sức hút mạnh cần định hướng"],
        "thuan_viet": "Một thế tình duyên rất đậm khi khí ái tình ở vị trí nước gặp thêm khí cứng sắc; sức hút mạnh nên cần được định hướng đúng đắn.",
    },
    "风流采杖": {
        "net_canon": ["khí tình ái gặp khí xấu dây dưa hoặc khí kỷ luật và cứng sắc", "cách đào hoa", "phong lưu đa tình"],
        "thuan_viet": "Một thế tình duyên đậm khi khí ái tình gặp khí xấu dây dưa hoặc khí cứng kỷ luật, sinh ra người phong lưu đa tình.",
    },
    "红杏出墙": {
        "net_canon": ["cụm khí đào hoa tụ ở ô vợ chồng hoặc ô phúc cộng hôn nhân không như ý", "cổ nói dễ sinh tình ngoài hôn nhân", "đọc là dấu hiệu cần chăm sóc quan hệ, không phán định"],
        "thuan_viet": "Cảnh nhiều khí tình ái tụ vào ô vợ chồng hoặc ô đời sống tinh thần kèm theo hôn nhân không như ý; sách xưa nói dễ sinh tình cảm ngoài luồng, nhưng nên hiểu đây là lời nhắc cần chăm sóc lại quan hệ chứ không phải lời kết tội.",
    },
    "石中隐玉": {
        "net_canon": ["khí điều tiếng/lời nói ở vị trí Tý hoặc Ngọ", "như ngọc giấu trong đá", "tính cách kín đáo", "tài năng tiềm ẩn", "không phô trương"],
        "thuan_viet": "Cảnh người mang khí lời nói đặt ở vị trí đẹp, như viên ngọc giấu trong đá: tính kín đáo, tài năng ẩn bên trong và không thích phô trương.",
    },
    # ===== CAN CHI =====
    "Tý": {
        "net_canon": ["địa chi thứ 1", "thuỷ dương — con chuột", "giờ 23:00-01:00", "tàng can: Quý", "giữa mùa đông (tháng 11 âm lịch)", "phương Bắc"],
        "thuan_viet": "Mốc đầu trong mười hai con giáp, là con chuột mang khí nước dương; ứng với khung giờ khuya 23 giờ tới 1 giờ, ẩn chứa khí Quý bên trong, thuộc giữa mùa đông tháng Mười Một âm lịch và chỉ phương Bắc.",
    },
    "Sửu": {
        "net_canon": ["địa chi thứ 2", "thổ âm — con trâu", "giờ 01:00-03:00", "tàng can: Kỷ, Quý, Tân", "tháng 12 âm lịch", "phương Đông Bắc"],
        "thuan_viet": "Mốc thứ hai trong mười hai con giáp, là con trâu mang khí đất âm; ứng với khung giờ 1 tới 3 giờ sáng, ẩn chứa các khí Kỷ, Quý, Tân, thuộc tháng Chạp và chỉ phương Đông Bắc.",
    },
    "Dần": {
        "net_canon": ["địa chi thứ 3", "mộc dương — con hổ", "giờ 03:00-05:00", "tàng can: Giáp, Bính, Mậu", "tháng Giêng âm lịch", "phương Đông Bắc", "khởi đầu Lập Xuân"],
        "thuan_viet": "Mốc thứ ba trong mười hai con giáp, là con hổ mang khí cây dương; ứng với khung giờ 3 tới 5 giờ sáng, ẩn chứa các khí Giáp, Bính, Mậu, thuộc tháng Giêng, chỉ phương Đông Bắc và là lúc mở đầu mùa xuân.",
    },
    "Mão": {
        "net_canon": ["địa chi thứ 4", "mộc âm — con mèo (VN) / con thỏ (TQ)", "giờ 05:00-07:00", "tàng can: Ất", "tháng 2 âm lịch", "phương Đông"],
        "thuan_viet": "Mốc thứ tư trong mười hai con giáp, là con mèo (ở ta) hay con thỏ (bên Tàu) mang khí cây âm; ứng với khung giờ 5 tới 7 giờ sáng, ẩn chứa khí Ất, thuộc tháng Hai và chỉ phương Đông.",
    },
    "Thìn": {
        "net_canon": ["địa chi thứ 5", "thổ dương — con rồng", "giờ 07:00-09:00", "tàng can: Mậu, Ất, Quý", "tháng 3 âm lịch", "phương Đông Nam"],
        "thuan_viet": "Mốc thứ năm trong mười hai con giáp, là con rồng mang khí đất dương; ứng với khung giờ 7 tới 9 giờ sáng, ẩn chứa các khí Mậu, Ất, Quý, thuộc tháng Ba và chỉ phương Đông Nam.",
    },
    "Tỵ": {
        "net_canon": ["địa chi thứ 6", "hỏa âm — con rắn", "giờ 09:00-11:00", "tàng can: Bính, Mậu, Canh", "tháng 4 âm lịch", "phương Đông Nam"],
        "thuan_viet": "Mốc thứ sáu trong mười hai con giáp, là con rắn mang khí lửa âm; ứng với khung giờ 9 tới 11 giờ trưa, ẩn chứa các khí Bính, Mậu, Canh, thuộc tháng Tư và chỉ phương Đông Nam.",
    },
    "Ngọ": {
        "net_canon": ["địa chi thứ 7", "nghĩa 'gặp gỡ'", "vạn vật đã qua thời cực thịnh", "lúc Âm Dương giao hoà"],
        "thuan_viet": "Mốc thứ bảy trong mười hai con giáp, mang nghĩa 'gặp gỡ', chỉ lúc muôn vật đã qua thời thịnh nhất, là khoảnh khắc hai khí âm và dương giao hoà với nhau.",
    },
    "Mùi": {
        "net_canon": ["địa chi thứ 8", "thổ âm — con dê", "giờ 13:00-15:00", "tàng can: Kỷ, Đinh, Ất", "tháng 6 âm lịch", "phương Tây Nam"],
        "thuan_viet": "Mốc thứ tám trong mười hai con giáp, là con dê mang khí đất âm; ứng với khung giờ 1 tới 3 giờ chiều, ẩn chứa các khí Kỷ, Đinh, Ất, thuộc tháng Sáu và chỉ phương Tây Nam.",
    },
    "Thân": {
        "net_canon": ["địa chi thứ 9", "kim dương — con khỉ", "giờ 15:00-17:00", "tàng can: Canh, Nhâm, Mậu", "tháng 7 âm lịch", "phương Tây Nam"],
        "thuan_viet": "Mốc thứ chín trong mười hai con giáp, là con khỉ mang khí kim dương; ứng với khung giờ 3 tới 5 giờ chiều, ẩn chứa các khí Canh, Nhâm, Mậu, thuộc tháng Bảy và chỉ phương Tây Nam.",
    },
    "Dậu": {
        "net_canon": ["địa chi thứ 10", "kim âm — con gà", "giờ 17:00-19:00", "tàng can: Tân", "tháng 8 âm lịch", "phương Tây"],
        "thuan_viet": "Mốc thứ mười trong mười hai con giáp, là con gà mang khí kim âm; ứng với khung giờ 5 tới 7 giờ tối, ẩn chứa khí Tân, thuộc tháng Tám và chỉ phương Tây.",
    },
    "Tuất": {
        "net_canon": ["địa chi thứ 11", "thổ dương — con chó", "giờ 19:00-21:00", "tàng can: Mậu, Tân, Đinh", "tháng 9 âm lịch", "phương Tây Bắc"],
        "thuan_viet": "Mốc thứ mười một trong mười hai con giáp, là con chó mang khí đất dương; ứng với khung giờ 7 tới 9 giờ tối, ẩn chứa các khí Mậu, Tân, Đinh, thuộc tháng Chín và chỉ phương Tây Bắc.",
    },
    "Hợi": {
        "net_canon": ["địa chi thứ 12", "nghĩa 'hạt nhân'", "vạn vật thu tàng", "ở dạng hạt giống ẩn dưới lòng đất"],
        "thuan_viet": "Mốc cuối trong mười hai con giáp, mang nghĩa 'hạt nhân', chỉ lúc muôn vật thu mình cất giữ lại, như hạt giống nằm ẩn dưới lòng đất chờ thời.",
    },
    "Giáp": {
        "net_canon": ["thiên can thứ 1", "mộc dương — đại thụ (cây lớn), thẳng, vươn cao", "tính nhân hậu, thẳng thắn, không khuất phục"],
        "thuan_viet": "Mốc trời thứ nhất, mang khí cây lớn vươn thẳng lên cao; tính người nhân hậu, thẳng thắn và không chịu khuất phục.",
    },
    "Ất": {
        "net_canon": ["thiên can thứ 2", "mộc âm — cây cỏ mềm, hoa lá", "tính uyển chuyển, dẻo dai, biết tuỳ hoàn cảnh"],
        "thuan_viet": "Mốc trời thứ hai, mang khí cây cỏ mềm hoa lá; tính người uyển chuyển dẻo dai, biết uốn mình tuỳ theo hoàn cảnh.",
    },
    "Bính": {
        "net_canon": ["thiên can thứ 3", "hỏa dương — mặt trời, lửa lớn", "tính nóng nhanh, sáng tỏ, hào hùng, công khai"],
        "thuan_viet": "Mốc trời thứ ba, mang khí mặt trời lửa lớn; tính người nóng và nhanh, sáng sủa rõ ràng, hào sảng và sống công khai không giấu giếm.",
    },
    "Đinh": {
        "net_canon": ["thiên can thứ 4", "cây cỏ lớn lên tráng kiện", "như con người đến tuổi trưởng thành"],
        "thuan_viet": "Mốc trời thứ tư, như cây cỏ đã vươn lên cứng cáp, ví như con người đã tới tuổi trưởng thành chững chạc.",
    },
    "Mậu": {
        "net_canon": ["thiên can thứ 5", "thổ dương — núi lớn, đất khô cao", "tính trung hậu, vững vàng, độ lượng"],
        "thuan_viet": "Mốc trời thứ năm, mang khí núi lớn đất khô cao; tính người trung hậu, vững vàng và rộng lượng.",
    },
    "Kỷ": {
        "net_canon": ["thiên can thứ 6", "thổ âm — đất ruộng ẩm, đất mềm", "tính tỉ mỉ, kiên trì, nuôi dưỡng"],
        "thuan_viet": "Mốc trời thứ sáu, mang khí đất ruộng ẩm mềm; tính người tỉ mỉ, bền bỉ kiên trì và biết nuôi dưỡng vun đắp.",
    },
    "Canh": {
        "net_canon": ["thiên can thứ 7", "nghĩa 'thay đổi'", "thời gian luân chuyển", "thu hoạch xong chờ xuân sang"],
        "thuan_viet": "Mốc trời thứ bảy, mang nghĩa 'thay đổi', chỉ thời khắc đang luân chuyển, như mùa màng đã gặt xong và đang chờ xuân mới tới.",
    },
    "Tân": {
        "net_canon": ["thiên can thứ 8", "nghĩa 'mới mẻ'", "vạn vật nghiêm trang đổi thay", "kết trái tươi mới"],
        "thuan_viet": "Mốc trời thứ tám, mang nghĩa 'mới mẻ', chỉ lúc muôn vật trang nghiêm chuyển mình đổi thay và kết thành trái tươi mới.",
    },
    "Nhâm": {
        "net_canon": ["thiên can thứ 9", "thủy dương — biển lớn, sông lớn", "tính rộng lượng, lưu động, trí tuệ rộng"],
        "thuan_viet": "Mốc trời thứ chín, mang khí biển lớn sông lớn; tính người rộng lượng, linh hoạt lưu chuyển và đầu óc bao quát rộng.",
    },
    "Quý": {
        "net_canon": ["thiên can thứ 10 (cuối cùng)", "nghĩa 'đo lường'", "vạn vật ẩn tàng dưới lòng đất"],
        "thuan_viet": "Mốc trời thứ mười cũng là mốc cuối, mang nghĩa 'đo lường'; ứng với lúc muôn vật thu mình ẩn náu dưới lòng đất.",
    },
    # ===== CÔ THẦN / QUẢ TÚ =====
    "Cô Thần": {
        "net_canon": ["sao cô độc với nam giới", "khó kết hôn hoặc hôn nhân xa cách"],
        "thuan_viet": "Dấu hiệu cô độc nghiêng về phía đàn ông: khó lấy vợ, hoặc dù có vợ thì vợ chồng cũng dễ xa cách.",
    },
    "Quả Tú": {
        "net_canon": ["sao cô độc với nữ giới", "khó có chồng hoặc sống một mình"],
        "thuan_viet": "Dấu hiệu cô độc nghiêng về phía đàn bà: khó lấy chồng, hoặc dễ phải sống lẻ bóng một mình.",
    },
}
